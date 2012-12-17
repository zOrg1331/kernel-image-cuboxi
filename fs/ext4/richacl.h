/*
 * Copyright IBM Corporation, 2010
 * Author Aneesh Kumar K.V <aneesh.kumar@linux.vnet.ibm.com>
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of version 2.1 of the GNU Lesser General Public License
 * as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it would be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 */

#ifndef __FS_EXT4_RICHACL_H
#define __FS_EXT4_RICHACL_H

#include <linux/richacl.h>

#ifdef CONFIG_EXT4_FS_RICHACL

# define EXT4_IS_RICHACL(inode) IS_RICHACL(inode)

/* Value for i_richacl if RICHACL has not been cached */
# define EXT4_RICHACL_NOT_CACHED ((void *)-1)

extern int ext4_permission(struct inode *, int);
extern int ext4_richacl_permission(struct inode *, unsigned int);
extern int ext4_may_create(struct inode *, int);
extern int ext4_may_delete(struct inode *, struct inode *, int);
extern int ext4_init_richacl(handle_t *, struct inode *, struct inode *);
extern int ext4_richacl_chmod(struct inode *);

#else  /* CONFIG_FS_EXT4_RICHACL */

# define EXT4_IS_RICHACL(inode) (0)

# define ext4_permission NULL
# define ext4_may_create NULL
# define ext4_may_delete NULL
# define ext4_richacl_permission NULL

static inline int
ext4_init_richacl(handle_t *handle, struct inode *inode, struct inode *dir)
{
	return 0;
}

static inline int
ext4_richacl_chmod(struct inode *inode)
{
	return 0;
}

#endif  /* CONFIG_FS_EXT4_RICHACL */
#endif  /* __FS_EXT4_RICHACL_H */
