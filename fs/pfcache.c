/*
 * Copyright (C) 2011 Parallels(C)
 * All rights reserved.
 * Cleancache interface to persistent file cache
 */

#include <linux/module.h>
#include <linux/fs.h>
#include <linux/kernel.h>
#include <linux/exportfs.h>
#include <linux/mm.h>
#include <linux/cleancache.h>
#include <linux/list_bl.h>
#include <linux/rcupdate.h>
#include <linux/rculist_bl.h>
#include <linux/bit_spinlock.h>
#include <linux/mount.h>
#include <linux/dcache.h>
#include <linux/namei.h>
#include <linux/bitops.h>
#include <linux/xattr.h>
#include <linux/pagemap.h>
#include <linux/sysfs.h>
#include <linux/vmalloc.h>
#include <linux/sysctl.h>

/*
 * Persistent file cache is an implementation of shared-cleancache for
 * read mostly files.
 * Idea: many sb may lookup in  shared persistent cache
 * Preconditions:
 * 1) Each inode has persisnent HASH summ of file content embeded inside inode
 * 2) Filesystem is responsible for maintaining this HASH to stay uptodate
 * 3) encode_fn/decode_fn should construct fhandle according inode's HASH
 */
#define NR_SYNCREAD_PAGES 16
#define HASH_TBL_ORDER	4
#define PFC_KEY_SIZE	20
#define PFC_PATH_MAX	(40 + 1 + 1)
static struct hlist_bl_head *pfc_hashtable __read_mostly;
static __cacheline_aligned_in_smp DEFINE_SPINLOCK(list_lock);
static LIST_HEAD(sb_list);

static unsigned int pfc_hash_bits, pfc_hash_mask __read_mostly;
struct path pfc_cache_path;
enum{
	PFC_FL_CONNECTED,
	PFC_FL_ACTIVE,
};

struct fs_node
{
	struct list_head list;
	struct super_block *sb;
	char *uuid;
	u32 pool_id;
};
/* Back reference */
struct back_ref {
	u32 ino;
	u32 generation;
	u32 pool_id;
};

struct pfc_node {
	struct hlist_bl_node hash_list;
	struct hlist_bl_node lru_list;
	struct rcu_head rcu;
	unsigned long flags;
	struct back_ref recent_user;
	u8 key[PFC_KEY_SIZE];
	atomic_t cnt;
	struct file * file;
};

static inline u8* key2csum(struct cleancache_filekey *key)
{
	return ((struct fid *) &key->u.fh)->i32_csum.check_sum;
}

static inline unsigned int __hashfn(u8 *csum)
{
	return ((unsigned int*)csum)[0] & pfc_hash_mask;
}

static inline unsigned int hashfn(struct cleancache_filekey *key)
{
	return __hashfn(key2csum(key));
}

static inline void spin_lock_bucket(struct hlist_bl_head *bl)
{
	bit_spin_lock(0, (unsigned long *)bl);
}

static inline void spin_unlock_bucket(struct hlist_bl_head *bl)
{
	__bit_spin_unlock(0, (unsigned long *)bl);
}

unsigned __read_mostly mtime_update_interval = 24 * 60 * 60; /* one day */

static void pfc_touch_file(struct file *file)
{
	struct timespec now = current_fs_time(file->f_mapping->host->i_sb);
	/*
	 * Is the previous mtime value older than a update interval?
	 * If yes, update file times:
	 */
	if ((long)(now.tv_sec - file->f_mapping->host->i_mtime.tv_sec) >=
	    mtime_update_interval) {
		file_update_time(file);
	}
}

static struct pfc_node* search_node(struct cleancache_filekey *fkey,
				    int update_time)
{
	struct pfc_node *pnode;
	struct hlist_bl_node *h;
	struct hlist_bl_head *head = pfc_hashtable + hashfn(fkey);
	u8 *csum = key2csum(fkey);

	hlist_bl_for_each_entry_rcu(pnode, h, head, hash_list) {
		if (memcmp(pnode->key, csum, sizeof(pnode->key)))
			continue;
		if (atomic_inc_not_zero(&pnode->cnt)) {
			if (pnode->file && update_time)
				pfc_touch_file(pnode->file);
			return pnode;
		}
	}
	return NULL;
}

static void drop_pnode_rcu(struct rcu_head *head)
{
	struct pfc_node *node;
	node = container_of(head, struct pfc_node, rcu);
	kfree(node);
}

/* Special case: Release negative node, caller must hold bucket lock. */
static int __pfc_release_pnode_noblock(struct pfc_node *node)
{
	struct hlist_bl_head *head;
	if (node->file)
		return 0;

	head = pfc_hashtable + __hashfn(node->key);
	hlist_bl_del_init_rcu(&node->hash_list);
	/* XXX remove from LRU lists */
	call_rcu(&node->rcu, drop_pnode_rcu);
	return 1;
}

static void pfc_release_pnode(struct pfc_node *node)
{
	struct hlist_bl_head *head = pfc_hashtable + __hashfn(node->key);
	spin_lock_bucket(head);
	hlist_bl_del_init_rcu(&node->hash_list);
	spin_unlock_bucket(head);
	/* XXX remove from LRU lists */
	if (node->file) {
		atomic_inc(&node->file->f_mapping->host->i_writecount);
		filp_close(node->file, NULL);
	}
	call_rcu(&node->rcu, drop_pnode_rcu);
}

static int put_pnode(struct pfc_node *node)
{
	if (atomic_dec_and_test(&node->cnt)) {
		pfc_release_pnode(node);
		return 1;
	}
	return 0;
}

static char* cache_path(struct pfc_node* node)
{
	int size;
	char *path, *p;
	u8 *key = node->key;
	path = kzalloc(PFC_PATH_MAX, GFP_KERNEL);
	if (!path)
		return NULL;
	/* Git like packing hex0/hex{1-19} */
	p = pack_hex_byte(path, *key++);
	*p++ = '/';
	size = PFC_KEY_SIZE - 1;
	while (size--)
		p = pack_hex_byte(p, *key++);
	p ="\0";
	return path;
}

/* Lookup and open cache file */
static int open_cache_file(struct pfc_node *node)
{
        const struct cred *old_cred;
        struct cred *override_cred;
	struct nameidata nd;
	char *path;
	int link_count, err = 0;

	path = cache_path(node);
	if (!path)
		return -ENOMEM;

        override_cred = prepare_creds();
        if (!override_cred) {
		err = -ENOMEM;
                goto out_free;
        }
        /* CAP_DAC_OVERRIDE for lookup */
        cap_raise(override_cred->cap_effective, CAP_DAC_OVERRIDE);
	old_cred = override_creds(override_cred);
	/* Lookup the file starting from the template area. */
	nd.flags = LOOKUP_STRICT;
	nd.path = pfc_cache_path;
	path_get(&nd.path);
	nd.depth = 0;

	link_count = current->link_count;
	current->link_count = 0;
	err = path_walk(path, &nd);
	current->link_count = link_count;
	if (err)
		goto out;

	path_get(&nd.path);
	node->file = dentry_open(nd.path.dentry,nd.path.mnt,
			   O_RDONLY | O_LARGEFILE, current_cred());
	if (IS_ERR(node->file)) {
		err = PTR_ERR(node->file);
		node->file = NULL;
		goto out_put_path;
	}
	pfc_touch_file(node->file);
	err = deny_write_access(node->file);
	if (!err)
		goto out;

	filp_close(node->file, NULL);
out_put_path:
	path_put(&nd.path);
out:
        revert_creds(old_cred);
        put_cred(override_cred);
out_free:
	kfree(path);
	return err;
}

struct pfc_node* insert_node(struct cleancache_filekey *fkey)
{
	struct pfc_node* node, *tmp;
	struct hlist_bl_head *head = pfc_hashtable + hashfn(fkey);

	tmp = kzalloc(sizeof(*node), GFP_KERNEL);
	if (!tmp)
		return NULL;

	memcpy(tmp->key, key2csum(fkey), sizeof(tmp->key));
	INIT_HLIST_BL_NODE(&tmp->hash_list);
	atomic_set(&tmp->cnt, 2); /* Speculative ref + our reference */
	/* Even if open failed we still want insert disconnected key */
	open_cache_file(tmp);
	/* Repeat search under lock */
	spin_lock_bucket(head);
	node = search_node(fkey, 0);
	if (node)
		goto out;
	node = tmp;
	tmp = NULL;
	hlist_bl_add_head_rcu(&node->hash_list, head);
out:
	spin_unlock_bucket(head);
	kfree(tmp);
	return node;
}

/* cleancache ops */
static void pfcache_put_page(int pool, struct cleancache_filekey key,
				     pgoff_t index, struct page *page)
{
#if 0
	struct pfc_node *node;

	if (pool < 0)
		return;

	//// XXX Place page to mem cache should be done here
	node = search_node(&key, 1);
	if (!node) {
		/* If node is not exist then this means that it was pruned,
		   and wasn't accessed recently, just skip that node */
		return;
	put_pnode(node);
#endif
	return ;
}

static int pfcache_get_page(int pool, struct cleancache_filekey key,
				    pgoff_t index, struct page *tgt_page)
{
	int ret = -1;
	char *addr1, *addr2;
	struct pfc_node *node;
	struct page *page = NULL;
	struct address_space *mapping;

	/* translate return values to linux semantics */
	if (pool < 0)
		return -1;

	node = search_node(&key, 1);
	if (!node) {
		node = insert_node(&key);
	}
	if (!node)
		return -1;
	if (!node->file)
		goto out;

	mapping = node->file->f_mapping;
	/* We just want uptodate pages. Readachead is supported by most
	 * filesystems, let's expoit that */
	page = find_get_page(mapping, index);
	if (!page) {
		page_cache_sync_readahead(mapping,
					  &node->file->f_ra, node->file,
					  index, NR_SYNCREAD_PAGES);
		page = find_get_page(mapping, index);
		if (unlikely(page == NULL))
			return -1;
	}
	if (PageReadahead(page)) {
		page_cache_async_readahead(mapping,
					   &node->file->f_ra, node->file,
					   page, index, NR_SYNCREAD_PAGES);
	}

	/* This is just an speculative lookup, RW access denied */
	if (!PageUptodate(page)) {
		ret = lock_page_killable(page);
		if (unlikely(ret))
			goto out;
		if (!PageUptodate(page)) {
			ret = -1;
			unlock_page(page);
			goto out;
		}
		unlock_page(page);
	}
	/* Copy data */
	addr1 = kmap_atomic(tgt_page, KM_USER0);
	addr2 = kmap_atomic(page, KM_USER1);
	memcpy(addr1, addr2, PAGE_SIZE);
	kunmap_atomic(addr2, KM_USER1);
	kunmap_atomic(addr1, KM_USER0);
	ret = 0;
out:
	if (page)
		page_cache_release(page);
	put_pnode(node);
	return ret;
}

static void pfcache_flush_page(int pool, struct cleancache_filekey key, pgoff_t index)
{
	// TODO shared pages should be putted here
	return;
}

static void pfcache_flush_inode(int pool, struct cleancache_filekey key)
{
	// TODO shared pages should be putted here
	return;
}

static void pfcache_flush_fs(int pool)
{
	struct fs_node *fnode;
	spin_lock(&list_lock);
	list_for_each_entry(fnode, &sb_list, list) {
		if (fnode->pool_id == pool) {
			list_del_init(&fnode->list);
			spin_unlock(&list_lock);
			kfree(fnode);
			return;
		}
	}
	spin_unlock(&list_lock);

	return;
}


static int pfcache_init_shared_fs(char *uuid, struct super_block *sb,
				  size_t pagesize)
{
	static int next_pool_id = 1;
	struct fs_node *new, *fnode;
	new  = kzalloc(sizeof(*new), GFP_KERNEL);
	if (!new)
		return -1;
	new->sb = sb;
	new->uuid = uuid;
	spin_lock(&list_lock);
collision:
	/*
	 * Our kernel is so reliable and server can has huge uptime so
	 * next_pool_id can overflow, let's do trivial sanity check
	 */
	new->pool_id = next_pool_id++;
	if (next_pool_id < 0)
		next_pool_id = 0;

	list_for_each_entry(fnode, &sb_list, list) {
		if (fnode->pool_id == new->pool_id)
			goto collision;
	}
	list_add(&new->list, &sb_list);
	spin_unlock(&list_lock);
	return new->pool_id;
}

static int pfcache_init_fs(struct super_block *sb, size_t pagesize)
{
	return pfcache_init_shared_fs(NULL, sb, pagesize);
}


static struct cleancache_ops pfcache_ops = {
	.put_page = pfcache_put_page,
	.get_page = pfcache_get_page,
	.flush_page = pfcache_flush_page,
	.flush_inode = pfcache_flush_inode,
	.flush_fs = pfcache_flush_fs,
	.init_shared_fs = pfcache_init_shared_fs,
	.init_fs = pfcache_init_fs,
};

static int prune_pfc_bucket(struct hlist_bl_head *head, gfp_t gfp_mask, unsigned int nr)
{
	struct pfc_node *pnode;
	struct hlist_bl_node *h;
	int count;
again:
	count = 0;
	spin_lock_bucket(head);
	hlist_bl_for_each_entry_rcu(pnode, h, head, hash_list) {
		/* XXX: Assume that GFP_FS is sufficient for close() */
		if (pnode->file && !(gfp_mask  & __GFP_FS))
			continue;
		count++;
		if (!nr == 0)
			continue;

		if (atomic_read(&pnode->cnt) != 1)
			continue;

		if (!atomic_dec_and_test(&pnode->cnt)) {
			/* We have dropped specualtive ref, but someone stil
			 * referenced it, remove it from list now so new user
			 * can not find it and refcont will goes to zero soon */
			hlist_bl_del_rcu(&pnode->hash_list);
		} else {
			if (!__pfc_release_pnode_noblock(pnode)) {
				/* Task may block, unlock bucket and restart */
				spin_unlock_bucket(head);
				pfc_release_pnode(pnode);
				goto again;
			}
		}
	}
	spin_unlock_bucket(head);
	return count;
}

static int shrink_pfcache_memory(struct shrinker *shrink, int nr_to_scan, gfp_t gfp_mask)
{

	int i, count = 0;
	for (i = 0; i <= pfc_hash_mask; i++) {
		count += prune_pfc_bucket(pfc_hashtable + i, gfp_mask,
					  nr_to_scan);
	}
	return (count / 100) * sysctl_vfs_cache_pressure;
}

static struct shrinker pfcache_shrinker = {
	.shrink = shrink_pfcache_memory,
	.seeks = DEFAULT_SEEKS,
};

static int pfc_init_hashtable(void)
{
	int i;
	unsigned long nr_hash;
	nr_hash = 1UL << (HASH_TBL_ORDER + PAGE_SHIFT);
	pfc_hashtable = (struct hlist_bl_head*)vmalloc(nr_hash);
	if (!pfc_hashtable)
		return -ENOMEM;
	nr_hash /= sizeof(struct hlist_bl_head);

	/* Find power-of-two hlist_heads which can fit into allocation */
	pfc_hash_bits = 0;
	do {
		pfc_hash_bits++;
	} while (nr_hash >> pfc_hash_bits);
	pfc_hash_bits--;

	nr_hash = 1UL << pfc_hash_bits;
	pfc_hash_mask = nr_hash - 1;
	for (i = 0; i < nr_hash; i++)
		INIT_HLIST_BL_HEAD(pfc_hashtable + i);

	printk("Persistent file cache hash table entries: %ld  (%ld bytes)\n",
			nr_hash, (PAGE_SIZE << HASH_TBL_ORDER));
	return 0;
}

static char *pfc_cache_str = "/vz/cache";
module_param(pfc_cache_str, charp, 0000);
MODULE_PARM_DESC(pfc_cache_str, "Path to cache root");

static struct ctl_table pfc_mod_table[] = {
	{
		.ctl_name	= CTL_UNNUMBERED,
		.procname	= "mtime_update_interval",
		.data		= &mtime_update_interval,
		.maxlen		= sizeof(unsigned),
		.mode		= 0644,
		.proc_handler	= &proc_dointvec,
	},
	{ .ctl_name = 0 }
};

static ctl_table pfc_kern_table[] = {
	{
		.ctl_name	= FS_PFCACHE,
		.procname	= "pfcache",
		.data		= NULL,
		.maxlen		= 0,
		.mode		= 0555,
		.child		= pfc_mod_table
	},
	{ .ctl_name = 0}
};

static ctl_table pfc_root_table[] = {
	{
		.ctl_name	= CTL_FS,
		.procname	= "fs",
		.data		= NULL,
		.maxlen		= 0,
		.mode		= 0555,
		.child		= pfc_kern_table
	},
	{ .ctl_name = 0 }
};

static struct ctl_table_header *pfc_table_header = NULL;
/*
 * It is not safe to switch cleancache hooks on runtime,
 * so this module is unloadable.
 */
static int __init pfcache_init(void)
{
	struct nameidata nd;
	int error;
	error = path_lookup(pfc_cache_str,
			LOOKUP_FOLLOW|LOOKUP_DIRECTORY, &nd);
	if (error)
		return error;

	pfc_table_header = register_sysctl_table(pfc_root_table);
	if (!pfc_table_header) {
		printk(KERN_ERR  "PFCache can not create sysctl table");
		error = -ENOMEM;
		goto out_path;
	}

	error = pfc_init_hashtable();
	if (error)
		goto out_sysctl;

	pfc_cache_path = nd.path;
	register_shrinker(&pfcache_shrinker);
	cleancache_register_ops(&pfcache_ops);
	return 0;

out_sysctl:
	if (pfc_table_header)
		unregister_sysctl_table(pfc_table_header);
out_path:
	path_put(&nd.path);
	return error;
};
module_init(pfcache_init);
MODULE_LICENSE("GPL");
