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

/**
 * richacl_allowed_to_who  -  mask flags allowed to a specific who value
 *
 * Computes the mask values allowed to a specific who value, taking
 * EVERYONE@ entries into account.
 */
static unsigned int richacl_allowed_to_who(struct richacl *acl,
					   struct richace *who)
{
	struct richace *ace;
	unsigned int allowed = 0;

	richacl_for_each_entry_reverse(ace, acl) {
		if (richace_is_inherit_only(ace))
			continue;
		if (richace_is_same_identifier(ace, who) ||
		    richace_is_everyone(ace)) {
			if (richace_is_allow(ace))
				allowed |= ace->e_mask;
			else if (richace_is_deny(ace))
				allowed &= ~ace->e_mask;
		}
	}
	return allowed;
}

/**
 * richacl_group_class_allowed  -  maximum permissions the group class is allowed
 *
 * See richacl_compute_max_masks().
 */
static unsigned int richacl_group_class_allowed(struct richacl *acl)
{
	struct richace *ace;
	unsigned int everyone_allowed = 0, group_class_allowed = 0;
	int had_group_ace = 0;

	richacl_for_each_entry_reverse(ace, acl) {
		if (richace_is_inherit_only(ace) ||
		    richace_is_owner(ace))
			continue;

		if (richace_is_everyone(ace)) {
			if (richace_is_allow(ace))
				everyone_allowed |= ace->e_mask;
			else if (richace_is_deny(ace))
				everyone_allowed &= ~ace->e_mask;
		} else {
			group_class_allowed |=
				richacl_allowed_to_who(acl, ace);

			if (richace_is_group(ace))
				had_group_ace = 1;
		}
	}
	if (!had_group_ace)
		group_class_allowed |= everyone_allowed;
	return group_class_allowed;
}

/**
 * richacl_compute_max_masks  -  compute upper bound masks
 *
 * Computes upper bound owner, group, and other masks so that none of
 * the mask flags allowed by the acl are disabled (for any choice of the
 * file owner or group membership).
 */
void richacl_compute_max_masks(struct richacl *acl)
{
	unsigned int gmask = ~0;
	struct richace *ace;

	/*
	 * @gmask contains all permissions which the group class is ever
	 * allowed.  We use it to avoid adding permissions to the group mask
	 * from everyone@ allow aces which the group class is always denied
	 * through other aces.  For example, the following acl would otherwise
	 * result in a group mask or rw:
	 *
	 *	group@:w::deny
	 *	everyone@:rw::allow
	 *
	 * Avoid computing @gmask for acls which do not include any group class
	 * deny aces: in such acls, the group class is never denied any
	 * permissions from everyone@ allow aces.
	 */

restart:
	acl->a_owner_mask = 0;
	acl->a_group_mask = 0;
	acl->a_other_mask = 0;

	richacl_for_each_entry_reverse(ace, acl) {
		if (richace_is_inherit_only(ace))
			continue;

		if (richace_is_owner(ace)) {
			if (richace_is_allow(ace))
				acl->a_owner_mask |= ace->e_mask;
			else if (richace_is_deny(ace))
				acl->a_owner_mask &= ~ace->e_mask;
		} else if (richace_is_everyone(ace)) {
			if (richace_is_allow(ace)) {
				acl->a_owner_mask |= ace->e_mask;
				acl->a_group_mask |= ace->e_mask & gmask;
				acl->a_other_mask |= ace->e_mask;
			} else if (richace_is_deny(ace)) {
				acl->a_owner_mask &= ~ace->e_mask;
				acl->a_group_mask &= ~ace->e_mask;
				acl->a_other_mask &= ~ace->e_mask;
			}
		} else {
			if (richace_is_allow(ace)) {
				acl->a_owner_mask |= ace->e_mask & gmask;
				acl->a_group_mask |= ace->e_mask & gmask;
			} else if (richace_is_deny(ace) && gmask == ~0) {
				gmask = richacl_group_class_allowed(acl);
				if (likely(gmask != ~0))  /* should always be true */
					goto restart;
			}
		}
	}
}
EXPORT_SYMBOL_GPL(richacl_compute_max_masks);

/**
 * richacl_chmod  -  update the file masks to reflect the new mode
 * @mode:	new file permission bits
 *
 * Return a copy of @acl where the file masks have been replaced by the file
 * masks corresponding to the file permission bits in @mode, or returns @acl
 * itself if the file masks are already up to date.  Takes over a reference
 * to @acl.
 */
struct richacl *
richacl_chmod(struct richacl *acl, mode_t mode)
{
	unsigned int owner_mask, group_mask, other_mask;
	struct richacl *clone;

	owner_mask = richacl_mode_to_mask(mode >> 6);
	group_mask = richacl_mode_to_mask(mode >> 3);
	other_mask = richacl_mode_to_mask(mode);

	if (acl->a_owner_mask == owner_mask &&
	    acl->a_group_mask == group_mask &&
	    acl->a_other_mask == other_mask &&
	    (!richacl_is_auto_inherit(acl) || richacl_is_protected(acl)))
		return acl;

	clone = richacl_clone(acl);
	richacl_put(acl);
	if (!clone)
		return ERR_PTR(-ENOMEM);

	clone->a_owner_mask = owner_mask;
	clone->a_group_mask = group_mask;
	clone->a_other_mask = other_mask;
	if (richacl_is_auto_inherit(clone))
		clone->a_flags |= ACL4_PROTECTED;

	return clone;
}
EXPORT_SYMBOL_GPL(richacl_chmod);

/**
 * richacl_permission  -  richacl permission check algorithm
 * @inode:	inode to check
 * @acl:	rich acl of the inode
 * @mask:	requested access (ACE4_* bitmask)
 *
 * Checks if the current process is granted @mask flags in @acl.
 */
int
richacl_permission(struct inode *inode, const struct richacl *acl,
		   unsigned int mask)
{
	const struct richace *ace;
	unsigned int file_mask, requested = mask, denied = 0;
	int in_owning_group = in_group_p(inode->i_gid);
	int in_owner_or_group_class = in_owning_group;

	/*
	 * A process is
	 *   - in the owner file class if it owns the file,
	 *   - in the group file class if it is in the file's owning group or
	 *     it matches any of the user or group entries, and
	 *   - in the other file class otherwise.
	 */

	/*
	 * Check if the acl grants the requested access and determine which
	 * file class the process is in.
	 */
	richacl_for_each_entry(ace, acl) {
		unsigned int ace_mask = ace->e_mask;

		if (richace_is_inherit_only(ace))
			continue;
		if (richace_is_owner(ace)) {
			if (current_fsuid() != inode->i_uid)
				continue;
			goto is_owner;
		} else if (richace_is_group(ace)) {
			if (!in_owning_group)
				continue;
		} else if (richace_is_unix_id(ace)) {
			if (ace->e_flags & ACE4_IDENTIFIER_GROUP) {
				if (!in_group_p(ace->u.e_id))
					continue;
			} else {
				if (current_fsuid() != ace->u.e_id)
					continue;
			}
		} else
			goto is_everyone;

		/*
		 * Apply the group file mask to entries other than OWNER@ and
		 * EVERYONE@. This is not required for correct access checking
		 * but ensures that we grant the same permissions as the acl
		 * computed by richacl_apply_masks() would grant.  See
		 * richacl_apply_masks() for a more detailed explanation.
		 */
		if (richace_is_allow(ace))
			ace_mask &= acl->a_group_mask;

is_owner:
		/* The process is in the owner or group file class. */
		in_owner_or_group_class = 1;

is_everyone:
		/* Check which mask flags the ACE allows or denies. */
		if (richace_is_deny(ace))
			denied |= ace_mask & mask;
		mask &= ~ace_mask;

		/*
		 * Keep going until we know which file class
		 * the process is in.
		 */
		if (!mask && in_owner_or_group_class)
			break;
	}
	denied |= mask;

	/*
	 * The file class a process is in determines which file mask applies.
	 * Check if that file mask also grants the requested access.
	 */
	if (current_fsuid() == inode->i_uid)
		file_mask = acl->a_owner_mask;
	else if (in_owner_or_group_class)
		file_mask = acl->a_group_mask;
	else
		file_mask = acl->a_other_mask;
	denied |= requested & ~file_mask;

	return denied ? -EACCES : 0;
}
EXPORT_SYMBOL_GPL(richacl_permission);

/**
 * richacl_inherit  -  compute the inherited acl of a new file
 * @dir_acl:	acl of the containing direcory
 * @inode:	inode of the new file (create mode in i_mode)
 *
 * A directory can have acl entries which files and/or directories created
 * inside the directory will inherit.  This function computes the acl for such
 * a new file.  If there is no inheritable acl, it will return %NULL.
 *
 * The file permission bits in inode->i_mode must be set to the create mode.
 * If there is an inheritable acl, the maximum permissions that the acl grants
 * will be computed and permissions not granted by the acl will be removed from
 * inode->i_mode.  If there is no inheritable acl, the umask will be applied
 * instead.
 */
struct richacl *
richacl_inherit(const struct richacl *dir_acl, struct inode *inode)
{
	const struct richace *dir_ace;
	struct richacl *acl = NULL;
	struct richace *ace;
	int count = 0;
	mode_t mask = ~current_umask();

	if (S_ISDIR(inode->i_mode)) {
		richacl_for_each_entry(dir_ace, dir_acl) {
			if (!richace_is_inheritable(dir_ace))
				continue;
			count++;
		}
		if (!count)
			goto mask;
		acl = richacl_alloc(count);
		if (!acl)
			return ERR_PTR(-ENOMEM);
		ace = acl->a_entries;
		richacl_for_each_entry(dir_ace, dir_acl) {
			if (!richace_is_inheritable(dir_ace))
				continue;
			memcpy(ace, dir_ace, sizeof(struct richace));
			if (dir_ace->e_flags & ACE4_NO_PROPAGATE_INHERIT_ACE)
				richace_clear_inheritance_flags(ace);
			if ((dir_ace->e_flags & ACE4_FILE_INHERIT_ACE) &&
			    !(dir_ace->e_flags & ACE4_DIRECTORY_INHERIT_ACE))
				ace->e_flags |= ACE4_INHERIT_ONLY_ACE;
			ace++;
		}
	} else {
		richacl_for_each_entry(dir_ace, dir_acl) {
			if (!(dir_ace->e_flags & ACE4_FILE_INHERIT_ACE))
				continue;
			count++;
		}
		if (!count)
			goto mask;
		acl = richacl_alloc(count);
		if (!acl)
			return ERR_PTR(-ENOMEM);
		ace = acl->a_entries;
		richacl_for_each_entry(dir_ace, dir_acl) {
			if (!(dir_ace->e_flags & ACE4_FILE_INHERIT_ACE))
				continue;
			memcpy(ace, dir_ace, sizeof(struct richace));
			richace_clear_inheritance_flags(ace);
			/*
			 * ACE4_DELETE_CHILD is meaningless for
			 * non-directories, so clear it.
			 */
			ace->e_mask &= ~ACE4_DELETE_CHILD;
			ace++;
		}
	}

	richacl_compute_max_masks(acl);

	/*
	 * Ensure that the acl will not grant any permissions beyond the create
	 * mode.
	 */
	acl->a_owner_mask &= richacl_mode_to_mask(inode->i_mode >> 6);
	acl->a_group_mask &= richacl_mode_to_mask(inode->i_mode >> 3);
	acl->a_other_mask &= richacl_mode_to_mask(inode->i_mode);
	mask = ~S_IRWXUGO | richacl_masks_to_mode(acl);

	if (richacl_is_auto_inherit(dir_acl)) {
		/*
		 * We need to set ACL4_PROTECTED because we are
		 * doing an implicit chmod
		 */
		acl->a_flags = ACL4_AUTO_INHERIT | ACL4_PROTECTED;
		richacl_for_each_entry(ace, acl)
			ace->e_flags |= ACE4_INHERITED_ACE;
	}

mask:
	inode->i_mode &= mask;
	return acl;
}
EXPORT_SYMBOL_GPL(richacl_inherit);

/**
 * richacl_equiv_mode  -  check if @acl is equivalent to file permission bits
 * @mode_p:	the file mode (including the file type)
 *
 * If @acl can be fully represented by file permission bits, this function
 * returns 0, and the file permission bits in @mode_p are set to the equivalent
 * of @acl.
 *
 * This function is used to avoid storing richacls on disk if the acl can be
 * computed from the file permission bits.  It allows user-space to make sure
 * that a file has no explicit richacl set.
 */
int
richacl_equiv_mode(const struct richacl *acl, mode_t *mode_p)
{
	const struct richace *ace = acl->a_entries;
	unsigned int x;
	mode_t mode;

	if (acl->a_count != 1 ||
	    acl->a_flags ||
	    !richace_is_everyone(ace) ||
	    !richace_is_allow(ace) ||
	    ace->e_flags & ~ACE4_SPECIAL_WHO)
		return -1;

	/*
	 * Figure out the permissions we care about: ACE4_DELETE_CHILD is
	 * meaningless for non-directories, so we ignore it.
	 */
	x = ~ACE4_POSIX_ALWAYS_ALLOWED;
	if (!S_ISDIR(*mode_p))
		x &= ~ACE4_DELETE_CHILD;

	if ((ace->e_mask & x) != (ACE4_POSIX_MODE_ALL & x))
		return -1;

	mode = richacl_masks_to_mode(acl);
	if ((acl->a_owner_mask & x) != (richacl_mode_to_mask(mode >> 6) & x) ||
	    (acl->a_group_mask & x) != (richacl_mode_to_mask(mode >> 3) & x) ||
	    (acl->a_other_mask & x) != (richacl_mode_to_mask(mode) & x))
		return -1;

	*mode_p = (*mode_p & ~S_IRWXUGO) | mode;
	return 0;
}
EXPORT_SYMBOL_GPL(richacl_equiv_mode);
