#include <linux/dcache.h>
#include <linux/err.h>
#include <linux/fs.h>
#include <linux/gfp.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/list.h>
#include <linux/mm.h>
#include <linux/memcontrol.h>
#include <linux/mm_inline.h>
#include <linux/mmgang.h>
#include <linux/module.h>
#include <linux/mount.h>
#include <linux/mutex.h>
#include <linux/namei.h>
#include <linux/pagemap.h>
#include <linux/pagevec.h>
#include <linux/parser.h>
#include <linux/pram.h>
#include <linux/ramfs.h>
#include <linux/spinlock.h>
#include <linux/string.h>
#include <linux/types.h>
#include <linux/uaccess.h>

#define PRAM_FS_META	"pram.meta"
#define PRAM_FS_DATA	"pram.data"

#define eprintk(fmt, args...)				\
do {							\
	printk(KERN_ERR "PRAMFS: " fmt "\n", ##args);	\
} while (0)

static int save_str(const char *str, int len, struct pram_stream *stream)
{
	__le32 __len = cpu_to_le32(len);

	if (pram_write(stream, &__len, 4) != 4 ||
	    pram_write(stream, str, len) != len)
		return -EIO;
	return 0;
}

static int load_str(char *buf, int buflen, struct pram_stream *stream)
{
	__le32 __len;
	int len;

	if (pram_read(stream, &__len, 4) != 4)
		return -EIO;
	len = le32_to_cpu(__len);
	if (len > buflen)
		return -ENAMETOOLONG;
	if (pram_read(stream, buf, len) != len)
		return -EIO;
	return len;
}

static int save_mapping_pages(struct address_space *mapping,
			      struct pram_stream *meta_stream,
			      struct pram_stream *data_stream)
{
	struct pagevec pvec;
	pgoff_t next = 0;
	__le64 __offset;
	int err = 0;

	pagevec_init(&pvec, 0);
	while (!err && pagevec_lookup(&pvec, mapping, next, PAGEVEC_SIZE)) {
		int i;

		for (i = 0; i < pagevec_count(&pvec); i++) {
			struct page *page = pvec.pages[i];
			pgoff_t offset;

			lock_page(page);
			if (unlikely(page->mapping != mapping)) {
				unlock_page(page);
				continue;
			}

			offset = page->index;
			if (offset > next)
				next = offset;
			next++;

			__offset = cpu_to_le64(offset);
			if (pram_write(meta_stream, &__offset, 8) != 8 ||
			    pram_push_page(data_stream, page, NULL) != 0) {
				unlock_page(page);
				err = -EIO;
				break;
			}

			remove_from_page_cache(page);
			page_cache_release(page);
			unlock_page(page);
		}
		pagevec_release(&pvec);
	}

#define OFFSET_END_MARK ((__le64)~0ULL)
	__offset = OFFSET_END_MARK;
	if (pram_write(meta_stream, &__offset, 8) != 8)
		err = -EIO;

	return err;
}

static int load_mapping_pages(struct address_space *mapping,
			      struct pram_stream *meta_stream,
			      struct pram_stream *data_stream)
{
	int err = 0;

	for ( ; ; ) {
		struct page *page;
		__le64 __offset;
		pgoff_t offset;

		if (pram_read(meta_stream, &__offset, 8) != 8) {
			err = -EIO;
			break;
		}
		if (__offset == OFFSET_END_MARK)
			break;

		page = pram_pop_page(data_stream);
		if (IS_ERR_OR_NULL(page)) {
			err = -EIO;
			break;
		}

		offset = le64_to_cpu(__offset);
		if (!page_gang(page)) {
			err = add_to_page_cache_lru(page, mapping, offset,
						    GFP_KERNEL);
		} else {
			struct user_beancounter *ub;

			/* page already accounted and in lru */
			ub = get_gang_ub(page_gang(page));
			ub = set_exec_ub(ub);
			err = add_to_page_cache(page, mapping, offset,
						GFP_KERNEL);
			ub = set_exec_ub(ub);
			ub_phys_uncharge(ub, 1);
		}
		if (err) {
			put_page(page);
			break;
		}

		SetPageUptodate(page);
		set_page_dirty(page);
		unlock_page(page);
		put_page(page);
	}

	return err;
}

static int save_symlink_value(struct dentry *dentry,
			      struct pram_stream *meta_stream)
{
	mm_segment_t oldfs;
	int len;
	char *buf;
	int err;

	buf = (char *)__get_free_page(GFP_TEMPORARY);
	if (!buf)
		return -ENOMEM;

	BUG_ON(!dentry->d_inode->i_op->readlink);
	oldfs = get_fs(); set_fs(KERNEL_DS);
	err = len = dentry->d_inode->i_op->readlink(dentry, buf, PAGE_SIZE);
	set_fs(oldfs);
	if (len >= 0)
		err = save_str(buf, len, meta_stream);

	free_page((unsigned long)buf);
	return err;
}

static inline int load_make_symlink(struct dentry *parent,
				    struct dentry *dentry,
				    struct pram_stream *meta_stream)
{
	int len;
	char *buf;
	int err;

	buf = (char *)__get_free_page(GFP_TEMPORARY);
	if (!buf)
		return -ENOMEM;

	err = len = load_str(buf, PAGE_SIZE - 1, meta_stream);
	if (len >= 0) {
		buf[len] = '\0';
		err = vfs_symlink(parent->d_inode, dentry, buf);
	}

	free_page((unsigned long)buf);
	return err;
}

struct file_header {
	__le32	mode;
	__le32	uid;
	__le32	gid;
	__le32	dev;
	__le32	atime;
	__le32	mtime;
	__le32	ctime;
	__le64	size;
};

static int save_file(struct dentry *dentry,
		     struct pram_stream *meta_stream,
		     struct pram_stream *data_stream)
{
	struct inode *inode = dentry->d_inode;
	struct file_header hdr;
	umode_t mode;
	int err;

	mode = inode->i_mode;
	hdr.mode = cpu_to_le32(mode);
	hdr.uid = cpu_to_le32(inode->i_uid);
	hdr.gid = cpu_to_le32(inode->i_gid);
	hdr.dev = cpu_to_le32(inode->i_rdev);
	hdr.atime = cpu_to_le32(inode->i_atime.tv_sec);
	hdr.mtime = cpu_to_le32(inode->i_mtime.tv_sec);
	hdr.ctime = cpu_to_le32(inode->i_ctime.tv_sec);
	hdr.size = cpu_to_le64(i_size_read(inode));

	if (pram_write(meta_stream, &hdr, sizeof(hdr)) != sizeof(hdr))
		return -EIO;

	err = save_str(dentry->d_name.name, dentry->d_name.len, meta_stream);
	if (err)
		return err;

	if (S_ISLNK(mode))
		err = save_symlink_value(dentry, meta_stream);
	else if (S_ISREG(mode))
		err = save_mapping_pages(inode->i_mapping,
					 meta_stream, data_stream);

	return err;
}

static struct dentry *load_file(struct dentry *parent,
				struct pram_stream *meta_stream,
				struct pram_stream *data_stream)
{
	struct dentry *dentry;
	struct inode *inode;
	struct file_header hdr;
	umode_t mode;
	int len;
	char *buf;
	int err;

	if (pram_read(meta_stream, &hdr, sizeof(hdr)) != sizeof(hdr))
		return ERR_PTR(-EIO);

	buf = (char *)__get_free_page(GFP_TEMPORARY);
	if (!buf)
		return ERR_PTR(-ENOMEM);

	err = len = load_str(buf, PAGE_SIZE, meta_stream);
	if (len < 0)
		goto out;

	mutex_lock_nested(&parent->d_inode->i_mutex, I_MUTEX_PARENT);

	dentry = lookup_one_len(buf, parent, len);
	if (IS_ERR(dentry)) {
		err = PTR_ERR(dentry);
		goto out_unlock;
	}

	free_page((unsigned long)buf);
	buf = NULL;

	mode = le32_to_cpu(hdr.mode);
	if (S_ISLNK(mode))
		err = load_make_symlink(parent, dentry, meta_stream);
	else if (S_ISREG(mode))
		err = vfs_create(parent->d_inode, dentry, mode, NULL);
	else if (S_ISDIR(mode))
		err = vfs_mkdir(parent->d_inode, dentry, mode);
	else if (S_ISCHR(mode) || S_ISBLK(mode) ||
		 S_ISFIFO(mode) || S_ISSOCK(mode))
		err = vfs_mknod(parent->d_inode, dentry, mode,
				le32_to_cpu(hdr.dev));
	else
		err = -EINVAL;
	if (err)
		goto out_dput;

	inode = dentry->d_inode;

	inode->i_mode = mode;
	inode->i_uid = le32_to_cpu(hdr.uid);
	inode->i_gid = le32_to_cpu(hdr.gid);
	inode->i_atime.tv_sec = le32_to_cpu(hdr.atime);
	inode->i_atime.tv_nsec = 0;
	inode->i_mtime.tv_sec = le32_to_cpu(hdr.mtime);
	inode->i_mtime.tv_nsec = 0;
	inode->i_ctime.tv_sec = le32_to_cpu(hdr.ctime);
	inode->i_ctime.tv_nsec = 0;

	if (S_ISREG(mode)) {
		i_size_write(inode, le64_to_cpu(hdr.size));
		err = load_mapping_pages(inode->i_mapping,
					 meta_stream, data_stream);
		if (err)
			goto out_dput;
	}
out_unlock:
	mutex_unlock(&parent->d_inode->i_mutex);
out:
	if (buf)
		free_page((unsigned long)buf);
	if (err)
		dentry = ERR_PTR(err);
	return dentry;
out_dput:
	dput(dentry);
	goto out_unlock;
}

static int save_link(struct dentry *dentry, struct dentry *target,
		     struct pram_stream *stream)
{
	char *str;
	void *buf;
	int err = 0;

	buf = (void *)__get_free_page(GFP_TEMPORARY);
	if (!buf)
		return -ENOMEM;

	str = dentry_path(target, buf, PAGE_SIZE);
	if (IS_ERR(str))
		err = PTR_ERR(str);

	if (!err)
		err = save_str(str, strlen(str), stream);

	free_page((unsigned long)buf);

	if (!err)
		err = save_str(dentry->d_name.name, dentry->d_name.len, stream);

	return err;
}

static int load_link(struct dentry *parent, struct vfsmount *mnt,
		     struct pram_stream *stream)
{
	struct dentry *dentry;
	struct nameidata nd;
	int len;
	char *buf;
	int err;

	buf = (char *)__get_free_page(GFP_TEMPORARY);
	if (!buf)
		return -ENOMEM;

	err = len = load_str(buf, PAGE_SIZE - 1, stream);
	if (len < 0)
		goto out;
	buf[len] = '\0';

	err = vfs_path_lookup(mnt->mnt_root, mnt, buf, 0, &nd);
	if (err)
		goto out;

	err = len = load_str(buf, PAGE_SIZE, stream);
	if (len < 0)
		goto out_path_put;

	mutex_lock_nested(&parent->d_inode->i_mutex, I_MUTEX_PARENT);

	dentry = lookup_one_len(buf, parent, len);
	if (IS_ERR(dentry)) {
		err = PTR_ERR(dentry);
		goto out_unlock;
	}

	free_page((unsigned long)buf);
	buf = NULL;

	err = vfs_link(nd.path.dentry, parent->d_inode, dentry);

	dput(dentry);
out_unlock:
	mutex_unlock(&parent->d_inode->i_mutex);
out_path_put:
	path_put(&nd.path);
out:
	if (buf)
		free_page((unsigned long)buf);
	return err;
}

#define CONTENT_FILE	1
#define CONTENT_LINK	2
#define ENDOFDIR_MARK	3

static int save_tree(struct dentry *root,
		     struct pram_stream *meta_stream,
		     struct pram_stream *data_stream)
{
	struct dentry *dget_list = NULL;
	struct dentry *dir, *dentry;
	__le16 __content;
	int err = 0;

	dir = root;
	dentry = NULL;
next_dir:
	spin_lock(&dcache_lock);
	if (!dentry)
		dentry = list_entry(&dir->d_subdirs, struct dentry, d_u.d_child);
	list_for_each_entry_continue(dentry, &dir->d_subdirs, d_u.d_child) {
		struct inode *inode;
		int content;

		if (d_unhashed(dentry) || !dentry->d_inode)
			continue;

		dget(dentry);
		spin_unlock(&dcache_lock);

		BUG_ON(dentry->d_fsdata);
		dentry->d_fsdata = dget_list;
		dget_list = dentry;

		inode = dentry->d_inode;
		if (inode->i_private) {
			BUG_ON(S_ISDIR(inode->i_mode));
			content = CONTENT_LINK;
		} else {
			content = CONTENT_FILE;
		}

		__content = cpu_to_le16(content);
		if (pram_write(meta_stream, &__content, 2) != 2) {
			err = -EIO;
			goto out;
		}

		switch (content) {
		case CONTENT_FILE:
			err = save_file(dentry, meta_stream, data_stream);
			if (!err && S_ISDIR(inode->i_mode)) {
				dir = dentry;
				dentry = NULL;
				goto next_dir;
			}
			inode->i_private = dentry;
			break;
		case CONTENT_LINK:
			err = save_link(dentry, inode->i_private, meta_stream);
			break;
		}
		if (err)
			goto out;
		spin_lock(&dcache_lock);
	}
	spin_unlock(&dcache_lock);
out:
	if (!err && dir != root) {
		__content = cpu_to_le32(ENDOFDIR_MARK);
		if (pram_write(meta_stream, &__content, 2) != 2) {
			err = -EIO;
		} else {
			dentry = dir;
			dir = dir->d_parent;
			goto next_dir;
		}
	}

	while (dget_list) {
		dentry = dget_list;
		dget_list = dentry->d_fsdata;
		dentry->d_inode->i_private = dentry->d_fsdata = NULL;
		dput(dentry);
	}
	return err;
}

static int load_tree(struct vfsmount *mnt,
		     struct pram_stream *meta_stream,
		     struct pram_stream *data_stream)
{
	struct dentry *root = mnt->mnt_root;
	struct dentry *dir, *dentry;
	__le16 __content;
	int content;
	ssize_t ret;
	int err = 0;

	dir = root;
next:
	ret = pram_read(meta_stream, &__content, 2);
	if (!ret)
		goto out;
	if (ret != 2) {
		err = -EIO;
		goto out;
	}

	content = le16_to_cpu(__content);
	switch (content) {
	case CONTENT_FILE:
		dentry = load_file(dir, meta_stream, data_stream);
		if (IS_ERR(dentry))
			err = PTR_ERR(dentry);
		else if (S_ISDIR(dentry->d_inode->i_mode))
			dir = dentry;
		else
			dput(dentry);
		break;
	case CONTENT_LINK:
		err = load_link(dir, mnt, meta_stream);
		break;
	case ENDOFDIR_MARK:
		if (dir != root) {
			dentry = dir;
			dir = dir->d_parent;
			dput(dentry);
			goto next;
		}
	default:
		err = -EIO;
		break;
	}
	if (!err)
		goto next;
out:
	if (dir != root && !err)
		err = -EIO;
	while (dir != root) {
		dentry = dir;
		dir = dir->d_parent;
		dput(dentry);
	}
	return err;
}

static void save_pram_fs(struct super_block *sb)
{
	struct pram_stream meta_stream, data_stream;
	int err;

	err = pram_open(PRAM_FS_META, PRAM_WRITE, &meta_stream);
	if (err) {
		eprintk("failed to create metadata stream: %d", err);
		return;
	}

	err = pram_open(PRAM_FS_DATA, PRAM_WRITE, &data_stream);
	if (err) {
		eprintk("failed to create data stream: %d", err);
		goto out_close_meta;
	}

	err = save_tree(sb->s_root, &meta_stream, &data_stream);
	if (err)
		eprintk("failed to save fs tree: %d", err);

	pram_close(&data_stream, err);
out_close_meta:
	pram_close(&meta_stream, err);
}

static int load_pram_fs(struct vfsmount *mnt)
{
	struct pram_stream meta_stream, data_stream;
	int err;

	err = pram_open(PRAM_FS_META, PRAM_READ, &meta_stream);
	if (err) {
		eprintk("failed to load metadata: %d", err);
		goto out;
	}

	err = pram_open(PRAM_FS_DATA, PRAM_READ, &data_stream);
	if (err) {
		eprintk("failed to load data: %d", err);
		goto out_close_meta;
	}

	err = load_tree(mnt, &meta_stream, &data_stream);
	if (err)
		eprintk("failed to load fs tree: %d", err);

	pram_close(&data_stream, 0);
out_close_meta:
	pram_close(&meta_stream, 0);
out:
	return err;
}

static void destroy_pram_fs(void)
{
	pram_destroy(PRAM_FS_META);
	pram_destroy(PRAM_FS_DATA);
}

enum { Opt_noload, Opt_err, };

static const match_table_t tokens = {
	{Opt_noload, "noload"},
	{Opt_err, NULL}
};

static int pram_fs_load;
static int pram_fs_save;

static int parse_options(char *options)
{
	substring_t args[MAX_OPT_ARGS];
	int token;
	char *p;

	pram_fs_load = 1;

	if (!options)
		goto out;

	while ((p = strsep(&options, ",")) != NULL) {
		if (!*p)
			continue;

		token = match_token(p, tokens, args);
		switch (token) {
		case Opt_noload:
			pram_fs_load = 0;
			break;
		/*
		 * Ignore unrecognized options
		 * since they can be intended ramfs
		 */
		}
	}
out:
	return 0;
}

static int pram_fill_super(struct super_block *sb, void *data, int silent)
{
	int err;
	char *options;

	options = kstrdup(data, GFP_KERNEL);
	if (!options && data)
		return -ENOMEM;

	err = parse_options(options);
	if (err)
		goto out;

	err = ramfs_fill_super(sb, data, silent);
out:
	kfree(options);
	return err;
}

static int pram_get_sb(struct file_system_type *fs_type, int flags,
		       const char *dev_name, void *data, struct vfsmount *mnt)
{
	int err;

	pram_fs_load = pram_fs_save = 0;

	err = get_sb_single(fs_type, flags, data, pram_fill_super, mnt);
	if (err)
		return err;

	if (pram_fs_load)
		err = load_pram_fs(mnt);
	else
		destroy_pram_fs();

	if (err) {
		dput(mnt->mnt_sb->s_root);
		deactivate_locked_super(mnt->mnt_sb);
		return err;
	}

	pram_fs_save = 1;
	return 0;
}

static void pram_kill_sb(struct super_block *sb)
{
	if (pram_fs_save)
		save_pram_fs(sb);
	kfree(sb->s_fs_info);
	kill_litter_super(sb);
}

static struct file_system_type pram_fs_type = {
	.name		= "pram",
	.get_sb		= pram_get_sb,
	.kill_sb	= pram_kill_sb,
};

static int __init init_pram_fs(void)
{
	return register_filesystem(&pram_fs_type);
}
module_init(init_pram_fs);
