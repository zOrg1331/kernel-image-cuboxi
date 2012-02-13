#include <linux/bitops.h>
#include <linux/buffer_head.h>
#include <linux/err.h>
#include <linux/fs.h>
#include <linux/gfp.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/kobject.h>
#include <linux/list.h>
#include <linux/module.h>
#include <linux/mm.h>
#include <linux/mmgang.h>
#include <linux/pagemap.h>
#include <linux/pagevec.h>
#include <linux/pram.h>
#include <linux/pramcache.h>
#include <linux/rbtree.h>
#include <linux/rcupdate.h>
#include <linux/spinlock.h>
#include <linux/string.h>
#include <linux/sysfs.h>
#include <linux/types.h>
#include <linux/writeback.h>

static int pramcache_enabled;	/* if set, page & bdev caches
				   will be saved to pram on umount */

struct pramcache_struct {
	unsigned long nr_pages;
	struct rb_root inode_tree;
	struct list_head inode_list;
	struct shrinker shrinker;
	spinlock_t lock;
};

struct inode_cache {
	unsigned long ino;
	unsigned long nr_pages;
	struct list_head pages;
	struct rb_node tree_node;
	struct list_head list_node;
};

static void pramcache_msg(struct super_block *sb, const char *prefix,
			  const char *fmt, ...)
{
	va_list ap;

	va_start(ap, fmt);
	printk("%sPRAMCACHE (%s): ", prefix, sb->s_id);
	vprintk(fmt, ap);
	printk("\n");
	va_end(ap);
}

static int pramcache_shrink(struct shrinker *shrink,
			    int nr_to_scan, gfp_t gfp_mask);

static inline void init_pramcache_struct(struct pramcache_struct *cache)
{
	memset(cache, 0, sizeof(struct pramcache_struct));
	cache->inode_tree = RB_ROOT;
	INIT_LIST_HEAD(&cache->inode_list);
	cache->shrinker.shrink = pramcache_shrink;
	cache->shrinker.seeks = DEFAULT_SEEKS;
	spin_lock_init(&cache->lock);
}

static inline void init_inode_cache(struct inode_cache *icache,
				    unsigned long ino)
{
	memset(icache, 0, sizeof(struct inode_cache));
	icache->ino = ino;
	INIT_LIST_HEAD(&icache->pages);
}

static void drain_page_list(struct list_head *list)
{
	struct page *page;

	while (!list_empty(list)) {
		page = list_entry(list->next, struct page, lru);
		list_del_init(&page->lru);
		put_page(page);
	}
}

static inline void drain_inode_cache(struct inode_cache *icache)
{
	icache->nr_pages = 0;
	drain_page_list(&icache->pages);
}

static void pramcache_drain(struct pramcache_struct *cache)
{
	struct inode_cache *icache;

	cache->nr_pages = 0;
	cache->inode_tree = RB_ROOT;
	while (!list_empty(&cache->inode_list)) {
		icache = list_entry(cache->inode_list.next,
				    struct inode_cache, list_node);
		list_del(&icache->list_node);
		drain_inode_cache(icache);
		kfree(icache);
	}
}

static void pramcache_destroy(struct pramcache_struct *cache)
{
	unregister_shrinker(&cache->shrinker);
	pramcache_drain(cache);
	kfree(cache);
}

static inline const char *pramcache_pram_basename(struct super_block *sb,
						  char *buf, size_t size)
{
	snprintf(buf, size, "pramcache.%pU.", sb->s_uuid);
	return buf;
}

static int open_streams(struct super_block *sb, const char *name, int mode,
			struct pram_stream *meta_stream,
			struct pram_stream *data_stream)
{
	char *buf;
	size_t basename_len;
	int err = -ENOMEM;

	buf = (char *)__get_free_page(GFP_TEMPORARY);
	if (!buf)
		goto out;

	pramcache_pram_basename(sb, buf, PAGE_SIZE);
	strlcat(buf, name, PAGE_SIZE);
	basename_len = strlen(buf);

	/*
	 * Since loss of several pages is not critical when saving
	 * page cache, we will be using GFP_NOWAIT & pram_prealloc()
	 */

	strlcat(buf, ".meta", PAGE_SIZE);
	err = __pram_open(buf, mode, GFP_NOWAIT | __GFP_HIGHMEM, meta_stream);
	if (err)
		goto out_free_buf;

	buf[basename_len] = '\0';
	strlcat(buf, ".data", PAGE_SIZE);
	err = __pram_open(buf, mode, GFP_NOWAIT | __GFP_HIGHMEM, data_stream);
	if (err)
		goto out_close_meta;

	free_page((unsigned long)buf);
	return 0;

out_close_meta:
	pram_close(meta_stream, -1);
out_free_buf:
	free_page((unsigned long)buf);
out:
	return err;
}

static inline void close_streams(struct pram_stream *meta_stream,
				 struct pram_stream *data_stream, int err)
{
	pram_close(meta_stream, err);
	pram_close(data_stream, err);
}

static unsigned long page_buffers_uptodate(struct page *page)
{
	struct buffer_head *head, *bh;
	unsigned long uptodate = 0;
	int i = 0;

	if (PageUptodate(page))
		return ~0UL;

	if (!page_has_buffers(page))
		return 0;

	head = bh = page_buffers(page);
	do {
		/* there can't be more than 8 buffers per page, can it? */
		WARN_ON_ONCE(i >= BITS_PER_LONG);
		if (buffer_uptodate(bh))
			__set_bit(i, &uptodate);
		bh = bh->b_this_page;
		i++;
	} while (bh != head);

	return uptodate;
}

static void create_uptodate_buffers(struct page *page,
		unsigned long blocksize, unsigned long uptodate)
{
	struct buffer_head *head, *bh;
	int page_uptodate = 1;
	int i = 0;

	create_empty_buffers(page, blocksize, 0);

	bh = head = page_buffers(page);
	do {
		WARN_ON_ONCE(i >= BITS_PER_LONG);
		if (test_bit(i, &uptodate))
			set_buffer_uptodate(bh);
		else
			page_uptodate = 0;
		bh = bh->b_this_page;
		i++;
	} while (bh != head);

	if (page_uptodate)
		SetPageUptodate(page);
}

static int save_page(struct page *page,
		     struct pram_stream *meta_stream,
		     struct pram_stream *data_stream)
{
	unsigned long uptodate;
	__le64 __index, __uptodate;
	int err = 0;

	/* ignore outdated pages */
	uptodate = page_buffers_uptodate(page);
	if (!uptodate)
		return 0;

	/* if prealloc fails, silently skip the page */
	if (pram_prealloc2(GFP_NOWAIT | __GFP_HIGHMEM, 16, PAGE_SIZE) == 0) {
		__uptodate = cpu_to_le64(uptodate);
		__index = cpu_to_le64(page->index);

		if (pram_write(meta_stream, &__uptodate, 8) != 8 ||
		    pram_write(meta_stream, &__index, 8) != 8 ||
		    pram_push_page(data_stream, page, NULL) != 0)
			err = -EIO;

		pram_prealloc_end();
	}
	return err;
}

static struct page *load_page(struct pram_stream *meta_stream,
			      struct pram_stream *data_stream)
{
	struct page *page;
	__le64 __index, __uptodate;
	ssize_t ret;

	/* since we do not save outdated pages, empty uptodate mask
	 * can be used as the 'end of mapping' mark */
	ret = pram_read(meta_stream, &__uptodate, 8);
	if (!ret || !__uptodate)
		return NULL;
	if (ret != 8)
		return ERR_PTR(-EIO);

	ret = pram_read(meta_stream, &__index, 8);
	if (ret != 8)
		return ERR_PTR(-EIO);

	page = pram_pop_page(data_stream);
	if (IS_ERR_OR_NULL(page))
		return ERR_PTR(-EIO);

	if (page_gang(page) != NULL) {
		put_page(page);
		return ERR_PTR(-EBUSY);
	}

	/* temporarily save uptodate mask to page's private field
	 * to be used later */
	set_page_private(page, le64_to_cpu(__uptodate));
	page->index = le64_to_cpu(__index);
	return page;
}

static int save_invalidate_mapping_pages(struct address_space *mapping,
					 struct pram_stream *meta_stream,
					 struct pram_stream *data_stream)
{
	struct pagevec pvec;
	pgoff_t next = 0;
	int err = 0;
	int i;

	pagevec_init(&pvec, 0);
	while (!err && pagevec_lookup(&pvec, mapping, next, PAGEVEC_SIZE)) {
		for (i = 0; !err && i < pagevec_count(&pvec); i++) {
			struct page *page = pvec.pages[i];
			pgoff_t index;

			lock_page(page);
			if (unlikely(page->mapping != mapping)) {
				unlock_page(page);
				continue;
			}

			index = page->index;
			if (index > next)
				next = index;
			next++;

			if (page_mapped(page) ||
			    PageDirty(page) || PageWriteback(page)) {
				unlock_page(page);
				continue;
			}

			err = save_page(page, meta_stream, data_stream);

			/* we prefer truncate_inode_page() here rather than
			 * invalidate_inode_page() because the latter does
			 * some bad tricks with page's refcount */
			truncate_inode_page(mapping, page);
			unlock_page(page);
		}
		pagevec_release(&pvec);
	}
	return err;
}

static long load_mapping_pages(struct pram_stream *meta_stream,
			       struct pram_stream *data_stream,
			       struct list_head *list)
{
	struct page *page;
	long nr_pages = 0;

	BUG_ON(!list_empty(list));
next:
	page = load_page(meta_stream, data_stream);
	if (IS_ERR(page)) {
		drain_page_list(list);
		return PTR_ERR(page);
	}
	if (!page)
		return nr_pages;

	list_add(&page->lru, list);
	nr_pages++;
	goto next;
}

static int save_invalidate_inode(struct inode *inode, int *first,
				 struct pram_stream *meta_stream,
				 struct pram_stream *data_stream)
{
	const __le64 __zero = 0;
	__le64 __ino;
	int err = 0;

	if (!inode->i_data.nrpages)
		return 0;

	/* if prealloc fails, silently skip the inode ... */
	if (pram_prealloc(GFP_NOWAIT | __GFP_HIGHMEM, 16) == 0) {
		__ino = cpu_to_le64(inode->i_ino);

		/* if we have already saved inodes, write the 'end of mapping'
		 * mark (see load_page()) */
		if (!*first && pram_write(meta_stream, &__zero, 8) != 8)
			err = -EIO;

		if (!err && pram_write(meta_stream, &__ino, 8) != 8)
			err = -EIO;

		pram_prealloc_end();

		if (!err)
			err = save_invalidate_mapping_pages(&inode->i_data,
						meta_stream, data_stream);
		*first = 0;
	} else {
		/* ... but don't forget to invalidate it */
		invalidate_mapping_pages(&inode->i_data, 0, ~0UL);
	}
	return err;
}

static struct inode_cache *load_inode(struct pram_stream *meta_stream,
				      struct pram_stream *data_stream)
{
	struct inode_cache *icache;
	__le64 __ino;
	ssize_t ret;
	long nr_pages;

	ret = pram_read(meta_stream, &__ino, 8);
	if (!ret)
		return NULL;
	if (ret != 8)
		return ERR_PTR(-EIO);

	icache = kmalloc(sizeof(struct inode_cache), GFP_KERNEL);
	if (!icache)
		return ERR_PTR(-ENOMEM);

	init_inode_cache(icache, le64_to_cpu(__ino));

	nr_pages = load_mapping_pages(meta_stream, data_stream, &icache->pages);
	if (nr_pages < 0) {
		kfree(icache);
		return ERR_PTR(nr_pages);
	}

	icache->nr_pages = nr_pages;
	return icache;
}

static inline struct inode_cache *
find_inode_cache(struct pramcache_struct *cache, unsigned long ino)
{
	struct rb_node *n = cache->inode_tree.rb_node;
	struct inode_cache *entry;

	while (n) {
		entry = rb_entry(n, struct inode_cache, tree_node);
		if (entry->ino < ino)
			n = n->rb_left;
		else if (entry->ino > ino)
			n = n->rb_right;
		else
			return entry;
	}
	return NULL;
}

static inline int
insert_inode_cache(struct pramcache_struct *cache, struct inode_cache *new)
{
	struct rb_node **p = &cache->inode_tree.rb_node;
	struct rb_node *parent = NULL;
	struct inode_cache *entry;

	while (*p) {
		parent = *p;
		entry = rb_entry(parent, struct inode_cache, tree_node);
		if (entry->ino < new->ino)
			p = &parent->rb_left;
		else if (entry->ino > new->ino)
			p = &parent->rb_right;
		else
			return 0;
	}
	rb_link_node(&new->tree_node, parent, p);
	rb_insert_color(&new->tree_node, &cache->inode_tree);
	list_add(&new->list_node, &cache->inode_list);
	cache->nr_pages += new->nr_pages;
	return 1;
}

static inline void
remove_inode_cache(struct pramcache_struct *cache, struct inode_cache *entry)
{
	rb_erase(&entry->tree_node, &cache->inode_tree);
	list_del(&entry->list_node);
	BUG_ON(cache->nr_pages < entry->nr_pages);
	cache->nr_pages -= entry->nr_pages;
}

static int populate_mapping(struct super_block *sb,
		struct address_space *mapping, struct list_head *pages)
{
	struct page *page;
	unsigned long uptodate;
	int err = 0;

	while (!err && !list_empty(pages)) {
		page = list_entry(pages->next, struct page, lru);
		list_del_init(&page->lru);

		/* see load_page() */
		uptodate = page_private(page);
		set_page_private(page, 0);
		BUG_ON(!uptodate);

		err = add_to_page_cache_lru(page, mapping, page->index,
					    GFP_KERNEL);
		if (!err) {
			if (~uptodate) {
				create_uptodate_buffers(page, sb->s_blocksize,
							uptodate);
			} else {
				/* no need to create buffers:
				 * it will be done later */
				SetPageUptodate(page);
			}
			unlock_page(page);
		}
		put_page(page);
		if (err == -EEXIST)
			err = 0;
	}
	return err;
}

static void save_invalidate_page_cache(struct super_block *sb)
{
	struct pram_stream meta_stream, data_stream;
	struct inode *inode;
	int first = 1;
	int err;

	err = open_streams(sb, "page_cache", PRAM_WRITE,
			   &meta_stream, &data_stream);
	if (err)
		goto out;

	spin_lock(&inode_lock);
	list_for_each_entry(inode, &sb->s_inodes, i_sb_list) {
		err = save_invalidate_inode(inode, &first,
					    &meta_stream, &data_stream);
		if (err)
			break;
	}
	spin_unlock(&inode_lock);

	close_streams(&meta_stream, &data_stream, err);
out:
	if (err)
		pramcache_msg(sb, KERN_ERR,
			      "Failed to save page cache: %d", err);
}

static void load_page_cache(struct super_block *sb)
{
	struct pram_stream meta_stream, data_stream;
	struct pramcache_struct *cache;
	struct inode_cache *icache;
	int err;

	err = open_streams(sb, "page_cache", PRAM_READ,
			   &meta_stream, &data_stream);
	if (err) {
		if (err == -ENOENT)
			err = 0;
		goto out;
	}

	cache = kmalloc(sizeof(struct pramcache_struct), GFP_KERNEL);
	if (!cache) {
		err = -ENOMEM;
		goto out_close_streams;
	}

	init_pramcache_struct(cache);

next:
	icache = load_inode(&meta_stream, &data_stream);
	if (IS_ERR(icache)) {
		err = PTR_ERR(icache);
		goto out_free_cache;
	}
	if (!icache)
		goto done;
	if (likely(icache->nr_pages)) {
		if (!insert_inode_cache(cache, icache))
			BUG();
	} else {
		/* no need to keep empty caches */
		kfree(icache);
	}
	goto next;

done:
	close_streams(&meta_stream, &data_stream, 0);
	register_shrinker(&cache->shrinker);
	sb->s_pramcache = cache;
	return;

out_free_cache:
	pramcache_drain(cache);
	kfree(cache);
out_close_streams:
	close_streams(&meta_stream, &data_stream, 0);
out:
	if (err)
		pramcache_msg(sb, KERN_ERR,
			      "Failed to load page cache: %d", err);
}

static void save_invalidate_bdev_cache(struct super_block *sb)
{
	struct pram_stream meta_stream, data_stream;
	int err;

	err = open_streams(sb, "bdev_cache", PRAM_WRITE,
			   &meta_stream, &data_stream);
	if (err)
		goto out;

	err = save_invalidate_mapping_pages(sb->s_bdev->bd_inode->i_mapping,
					    &meta_stream, &data_stream);
	close_streams(&meta_stream, &data_stream, err);
out:
	if (err)
		pramcache_msg(sb, KERN_ERR,
			      "Failed to save bdev cache: %d", err);
}

static void load_bdev_cache(struct super_block *sb)
{
	struct pram_stream meta_stream, data_stream;
	LIST_HEAD(pages);
	long nr_pages;
	int err;

	err = open_streams(sb, "bdev_cache", PRAM_READ,
			   &meta_stream, &data_stream);
	if (err) {
		if (err == -ENOENT)
			err = 0;
		goto out;
	}

	nr_pages = load_mapping_pages(&meta_stream, &data_stream, &pages);
	if (nr_pages < 0) {
		err = nr_pages;
		goto out_close_streams;
	}

	err = populate_mapping(sb, sb->s_bdev->bd_inode->i_mapping, &pages);
	drain_page_list(&pages);

out_close_streams:
	close_streams(&meta_stream, &data_stream, 0);
out:
	if (err)
		pramcache_msg(sb, KERN_ERR,
			      "Failed to load bdev cache: %d", err);
}

static int pramcache_shrink(struct shrinker *shrink,
			    int nr_to_scan, gfp_t gfp_mask)
{
	struct pramcache_struct *cache = container_of(shrink,
				struct pramcache_struct, shrinker);
	struct inode_cache *icache, *tmp;
	struct page *page;
	int nr_left = cache->nr_pages;

	if (!nr_to_scan || !nr_left)
		return nr_left;

	spin_lock(&cache->lock);
again:
	/* try to shrink caches evenly across inodes */
	list_for_each_entry_safe(icache, tmp,
				 &cache->inode_list, list_node) {
		BUG_ON(list_empty(&icache->pages));
		page = list_entry(icache->pages.next, struct page, lru);

		list_del_init(&page->lru);
		icache->nr_pages--;
		cache->nr_pages--;

		if (list_empty(&icache->pages)) {
			remove_inode_cache(cache, icache);
			kfree(icache);
		}

		put_page(page);
		nr_to_scan--;

		if (!cache->nr_pages || !nr_to_scan)
			goto out;
	}
	goto again;
out:
	nr_left = cache->nr_pages;
	spin_unlock(&cache->lock);

	return nr_left;
}

void pramcache_load(struct super_block *sb)
{
	BUG_ON(!sb->s_bdev);

	load_bdev_cache(sb);
	load_page_cache(sb);
}
EXPORT_SYMBOL(pramcache_load);

void pramcache_populate_inode(struct inode *inode)
{
	struct super_block *sb = inode->i_sb;
	struct pramcache_struct *cache = sb->s_pramcache;
	struct inode_cache *icache;
	int err;

	if (!cache || !cache->nr_pages)
		return;

	spin_lock(&cache->lock);
	icache = find_inode_cache(cache, inode->i_ino);
	if (icache)
		remove_inode_cache(cache, icache);
	spin_unlock(&cache->lock);

	if (!icache)
		return;

	err = populate_mapping(sb, &inode->i_data, &icache->pages);
	if (err)
		pramcache_msg(sb, KERN_ERR,
			      "Failed to populate inode: %ld", err);

	drain_inode_cache(icache);
	kfree(icache);
}
EXPORT_SYMBOL(pramcache_populate_inode);

void pramcache_save_page_cache(struct super_block *sb)
{
	struct pramcache_struct *cache = sb->s_pramcache;

	BUG_ON(!sb->s_bdev);

	/* if we're saving page cache, pram cache won't be used any more
	 * so it can be safely destroyed */
	if (cache)
		pramcache_destroy(cache);

	if (pramcache_enabled)
		save_invalidate_page_cache(sb);
}
EXPORT_SYMBOL(pramcache_save_page_cache);

void pramcache_save_bdev_cache(struct super_block *sb)
{
	BUG_ON(!sb->s_bdev);

	if (pramcache_enabled)
		save_invalidate_bdev_cache(sb);
}
EXPORT_SYMBOL(pramcache_save_bdev_cache);

static ssize_t pramcache_show(struct kobject *kobj,
			      struct kobj_attribute *attr,
			      char *buf)
{
	return sprintf(buf, "%d\n", pramcache_enabled);
}

static ssize_t pramcache_store(struct kobject *kobj,
			       struct kobj_attribute *attr,
			       const char *buf, size_t count)
{
	unsigned long val;

	if (strict_strtoul(buf, 10, &val) != 0)
		return -EINVAL;
	pramcache_enabled = !!val;
	return count;
}

static struct kobj_attribute pramcache_attr =
	__ATTR(pramcache, 0644, pramcache_show, pramcache_store);

static struct attribute *pramcache_attrs[] = {
	&pramcache_attr.attr,
	NULL,
};

static struct attribute_group pramcache_attr_group = {
	.attrs = pramcache_attrs,
};

static int __init pramcache_init(void)
{
	sysfs_update_group(kernel_kobj, &pramcache_attr_group);
	return 0;
}
module_init(pramcache_init);
