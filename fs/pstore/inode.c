/*
 * Persistent Storage - ramfs parts.
 *
 * Copyright (C) 2010 Intel Corporation <tony.luck@intel.com>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License version 2 as
 *  published by the Free Software Foundation.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <linux/module.h>
#include <linux/fs.h>
#include <linux/pagemap.h>
#include <linux/highmem.h>
#include <linux/time.h>
#include <linux/init.h>
#include <linux/string.h>
#include <linux/mount.h>
#include <linux/ramfs.h>
#include <linux/sched.h>
#include <linux/magic.h>
#include <linux/slab.h>
#include <linux/uaccess.h>

#include "internal.h"

#define pstore_get_inode ramfs_get_inode

static int pstore_unlink(struct inode *dir, struct dentry *dentry)
{
	pstore_erase(dentry->d_inode->i_private);

	return simple_unlink(dir, dentry);
}

static const struct inode_operations pstore_dir_inode_operations = {
	.lookup		= simple_lookup,
	.unlink		= pstore_unlink,
};

static const struct super_operations pstore_ops = {
	.statfs		= simple_statfs,
	.drop_inode	= generic_delete_inode,
	.show_options	= generic_show_options,
};

static struct super_block *pstore_sb;
static struct vfsmount *pstore_mnt;

int pstore_is_mounted(void)
{
	return pstore_mnt != NULL;
}

/*
 * Set up a file structure as if we had opened this file and
 * write our data to it.
 */
static int pstore_writefile(struct inode *inode, struct dentry *dentry,
	char *data, size_t size)
{
	struct file f;
	ssize_t n;
	mm_segment_t old_fs = get_fs();

	memset(&f, '0', sizeof f);
	f.f_mapping = inode->i_mapping;
	f.f_path.dentry = dentry;
	f.f_path.mnt = pstore_mnt;
	f.f_pos = 0;
	f.f_op = inode->i_fop;
	set_fs(KERNEL_DS);
	n = do_sync_write(&f, data, size, &f.f_pos);
	set_fs(old_fs);

	return n == size;
}

/*
 * Make a regular file in the root directory of our file system.
 * Load it up with "size" bytes of data from "buf".
 * Set the mtime & ctime to the date that this record was originally stored.
 */
int pstore_mkfile(char *name, char *data, size_t size, struct timespec time,
		  void *private)
{
	struct dentry	*root = pstore_sb->s_root;
	struct dentry	*dentry;
	struct inode	*inode;
	int		rc;

	rc = -ENOMEM;
	inode = pstore_get_inode(pstore_sb, root->d_inode, S_IFREG | 0444, 0);
	if (!inode)
		goto fail;

	inode->i_private = private;

	mutex_lock(&root->d_inode->i_mutex);

	rc = -ENOSPC;
	dentry = d_alloc_name(root, name);
	if (IS_ERR(dentry))
		goto fail_alloc;

	d_add(dentry, inode);

	mutex_unlock(&root->d_inode->i_mutex);

	if (!pstore_writefile(inode, dentry, data, size))
		goto fail_write;

	if (time.tv_sec)
		inode->i_mtime = inode->i_ctime = time;

	return 0;

fail_write:
	inode->i_nlink--;
	mutex_lock(&root->d_inode->i_mutex);
	d_delete(dentry);
	dput(dentry);
	mutex_unlock(&root->d_inode->i_mutex);
	goto fail;

fail_alloc:
	mutex_unlock(&root->d_inode->i_mutex);
	iput(inode);

fail:
	return rc;
}

int pstore_fill_super(struct super_block *sb, void *data, int silent)
{
	struct inode *inode = NULL;
	struct dentry *root;
	int err;

	save_mount_options(sb, data);

	pstore_sb = sb;

	sb->s_maxbytes		= MAX_LFS_FILESIZE;
	sb->s_blocksize		= PAGE_CACHE_SIZE;
	sb->s_blocksize_bits	= PAGE_CACHE_SHIFT;
	sb->s_magic		= PSTOREFS_MAGIC;
	sb->s_op		= &pstore_ops;
	sb->s_time_gran		= 1;

	inode = pstore_get_inode(sb, NULL, S_IFDIR | 0755, 0);
	if (!inode) {
		err = -ENOMEM;
		goto fail;
	}
	/* override ramfs "dir" options so we catch unlink(2) */
	inode->i_op = &pstore_dir_inode_operations;

	root = d_alloc_root(inode);
	sb->s_root = root;
	if (!root) {
		err = -ENOMEM;
		goto fail;
	}

	pstore_get_records();

	return 0;
fail:
	iput(inode);
	return err;
}

static int pstore_get_sb(struct file_system_type *fs_type,
	int flags, const char *dev_name, void *data, struct vfsmount *mnt)
{
	struct dentry *root;

	root = mount_nodev(fs_type, flags, data, pstore_fill_super);
	if (IS_ERR(root))
		return -ENOMEM;

	mnt->mnt_root = root;
	mnt->mnt_sb = root->d_sb;
	pstore_mnt = mnt;

	return 0;
}

static void pstore_kill_sb(struct super_block *sb)
{
	kill_litter_super(sb);
	pstore_sb = NULL;
	pstore_mnt = NULL;
}

static struct file_system_type pstore_fs_type = {
	.name		= "pstore",
	.get_sb		= pstore_get_sb,
	.kill_sb	= pstore_kill_sb,
};

static int __init init_pstore_fs(void)
{
	return register_filesystem(&pstore_fs_type);
}
module_init(init_pstore_fs)

MODULE_AUTHOR("Tony Luck <tony.luck@intel.com>");
MODULE_LICENSE("GPL");
