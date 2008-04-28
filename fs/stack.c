/*
 * Copyright (c) 2006-2007 Erez Zadok
 * Copyright (c) 2006-2007 Josef 'Jeff' Sipek
 * Copyright (c) 2006-2007 Stony Brook University
 * Copyright (c) 2006-2007 The Research Foundation of SUNY
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */

#include <linux/module.h>
#include <linux/fs.h>
#include <linux/fs_stack.h>

/*
 * does _NOT_ require i_mutex to be held.
 *
 * This function cannot be inlined since i_size_{read,write} is rather
 * heavy-weight on 32-bit systems
 */
void fsstack_copy_inode_size(struct inode *dst, const struct inode *src)
{
#if BITS_PER_LONG == 32 && defined(CONFIG_SMP)
	spin_lock(&dst->i_lock);
#endif
	i_size_write(dst, i_size_read(src));
	dst->i_blocks = src->i_blocks;
#if BITS_PER_LONG == 32 && defined(CONFIG_SMP)
	spin_unlock(&dst->i_lock);
#endif
}
EXPORT_SYMBOL_GPL(fsstack_copy_inode_size);

/*
 * copy all attributes; get_nlinks is optional way to override the i_nlink
 * copying
 */
void fsstack_copy_attr_all(struct inode *dest, const struct inode *src)
{
	dest->i_mode = src->i_mode;
	dest->i_uid = src->i_uid;
	dest->i_gid = src->i_gid;
	dest->i_rdev = src->i_rdev;
	dest->i_atime = src->i_atime;
	dest->i_mtime = src->i_mtime;
	dest->i_ctime = src->i_ctime;
	dest->i_blkbits = src->i_blkbits;
	dest->i_flags = src->i_flags;
	dest->i_nlink = src->i_nlink;
}
EXPORT_SYMBOL_GPL(fsstack_copy_attr_all);
