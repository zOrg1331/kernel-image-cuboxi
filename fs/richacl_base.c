/*
 * Copyright (C) 2006, 2010  Novell, Inc.
 * Written by Andreas Gruenbacher <agruen@suse.de>
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2, or (at your option) any
 * later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 */

#include <linux/sched.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/richacl.h>

MODULE_LICENSE("GPL");

/*
 * Special e_who identifiers:  ACEs which have ACE4_SPECIAL_WHO set in
 * ace->e_flags use these constants in ace->u.e_who.
 *
 * For efficiency, we compare pointers instead of comparing strings.
 */
const char richace_owner_who[]	  = "OWNER@";
EXPORT_SYMBOL_GPL(richace_owner_who);
const char richace_group_who[]	  = "GROUP@";
EXPORT_SYMBOL_GPL(richace_group_who);
const char richace_everyone_who[] = "EVERYONE@";
EXPORT_SYMBOL_GPL(richace_everyone_who);

/**
 * richacl_alloc  -  allocate a richacl
 * @count:	number of entries
 */
struct richacl *
richacl_alloc(int count)
{
	size_t size = sizeof(struct richacl) + count * sizeof(struct richace);
	struct richacl *acl = kzalloc(size, GFP_KERNEL);

	if (acl) {
		atomic_set(&acl->a_refcount, 1);
		acl->a_count = count;
	}
	return acl;
}
EXPORT_SYMBOL_GPL(richacl_alloc);

/**
 * richacl_clone  -  create a copy of a richacl
 */
static struct richacl *
richacl_clone(const struct richacl *acl)
{
	int count = acl->a_count;
	size_t size = sizeof(struct richacl) + count * sizeof(struct richace);
	struct richacl *dup = kmalloc(size, GFP_KERNEL);

	if (dup) {
		memcpy(dup, acl, size);
		atomic_set(&dup->a_refcount, 1);
	}
	return dup;
}

/**
 * richacl_mask_to_mode  -  compute the file permission bits which correspond to @mask
 * @mask:	%ACE4_* permission mask
 *
 * See richacl_masks_to_mode().
 */
static int
richacl_mask_to_mode(unsigned int mask)
{
	int mode = 0;

	if (mask & ACE4_POSIX_MODE_READ)
		mode |= MAY_READ;
	if (mask & ACE4_POSIX_MODE_WRITE)
		mode |= MAY_WRITE;
	if (mask & ACE4_POSIX_MODE_EXEC)
		mode |= MAY_EXEC;

	return mode;
}

/**
 * richacl_masks_to_mode  -  compute the file permission bits from the file masks
 *
 * When setting a richacl, we set the file permission bits to indicate maximum
 * permissions: for example, we set the Write permission when a mask contains
 * ACE4_APPEND_DATA even if it does not also contain ACE4_WRITE_DATA.
 *
 * Permissions which are not in ACE4_POSIX_MODE_READ, ACE4_POSIX_MODE_WRITE, or
 * ACE4_POSIX_MODE_EXEC cannot be represented in the file permission bits.
 * Such permissions can still be effective, but not for new files or after a
 * chmod(), and only if they were set explicitly, for example, by setting a
 * richacl.
 */
int
richacl_masks_to_mode(const struct richacl *acl)
{
	return richacl_mask_to_mode(acl->a_owner_mask) << 6 |
	       richacl_mask_to_mode(acl->a_group_mask) << 3 |
	       richacl_mask_to_mode(acl->a_other_mask);
}
EXPORT_SYMBOL_GPL(richacl_masks_to_mode);

/**
 * richacl_mode_to_mask  - compute a file mask from the lowest three mode bits
 *
 * When the file permission bits of a file are set with chmod(), this specifies
 * the maximum permissions that processes will get.  All permissions beyond
 * that will be removed from the file masks, and become ineffective.
 *
 * We also add in the permissions which are always allowed no matter what the
 * acl says.
 */
unsigned int
richacl_mode_to_mask(mode_t mode)
{
	unsigned int mask = ACE4_POSIX_ALWAYS_ALLOWED;

	if (mode & MAY_READ)
		mask |= ACE4_POSIX_MODE_READ;
	if (mode & MAY_WRITE)
		mask |= ACE4_POSIX_MODE_WRITE;
	if (mode & MAY_EXEC)
		mask |= ACE4_POSIX_MODE_EXEC;

	return mask;
}

/**
 * richacl_want_to_mask  - convert the iop->permission want argument to a mask
 * @want:	@want argument of the permission inode operation
 *
 * When checking for append, @want is (MAY_WRITE | MAY_APPEND).
 *
 * Richacls use the iop->may_create and iop->may_delete hooks which are
 * used for checking if creating and deleting files is allowed.  These hooks do
 * not use richacl_want_to_mask(), so we do not have to deal with mapping
 * MAY_WRITE to ACE4_ADD_FILE, ACE4_ADD_SUBDIRECTORY, and ACE4_DELETE_CHILD
 * here.
 */
unsigned int
richacl_want_to_mask(int want)
{
	unsigned int mask = 0;

	if (want & MAY_READ)
		mask |= ACE4_READ_DATA;
	if (want & MAY_APPEND)
		mask |= ACE4_APPEND_DATA;
	else if (want & MAY_WRITE)
		mask |= ACE4_WRITE_DATA;
	if (want & MAY_EXEC)
		mask |= ACE4_EXECUTE;

	return mask;
}
EXPORT_SYMBOL_GPL(richacl_want_to_mask);

/**
 * richace_is_same_identifier  -  are both identifiers the same?
 */
int
richace_is_same_identifier(const struct richace *a, const struct richace *b)
{
#define WHO_FLAGS (ACE4_SPECIAL_WHO | ACE4_IDENTIFIER_GROUP)
	if ((a->e_flags & WHO_FLAGS) != (b->e_flags & WHO_FLAGS))
		return 0;
	if (a->e_flags & ACE4_SPECIAL_WHO)
		return a->u.e_who == b->u.e_who;
	else
		return a->u.e_id == b->u.e_id;
#undef WHO_FLAGS
}

/**
 * richacl_set_who  -  set a special who value
 * @ace:	acl entry
 * @who:	who value to use
 */
int
richace_set_who(struct richace *ace, const char *who)
{
	if (!strcmp(who, richace_owner_who))
		who = richace_owner_who;
	else if (!strcmp(who, richace_group_who))
		who = richace_group_who;
	else if (!strcmp(who, richace_everyone_who))
		who = richace_everyone_who;
	else
		return -EINVAL;

	ace->u.e_who = who;
	ace->e_flags |= ACE4_SPECIAL_WHO;
	ace->e_flags &= ~ACE4_IDENTIFIER_GROUP;
	return 0;
}
EXPORT_SYMBOL_GPL(richace_set_who);
