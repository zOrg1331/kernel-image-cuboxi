#include <linux/syscalls.h>
#include <linux/slab.h>
#include <linux/fs.h>
#include <linux/file.h>
#include <linux/mount.h>
#include <linux/namei.h>
#include <linux/exportfs.h>
#include <asm/uaccess.h>
#include "internal.h"

static long do_sys_name_to_handle(struct path *path,
				  struct file_handle __user *ufh,
				  int __user *mnt_id)
{
	long retval;
	struct file_handle f_handle;
	int handle_dwords, handle_bytes;
	struct file_handle *handle = NULL;

	if (copy_from_user(&f_handle, ufh, sizeof(struct file_handle))) {
		retval = -EFAULT;
		goto err_out;
	}
	if (f_handle.handle_bytes > MAX_HANDLE_SZ) {
		retval = -EINVAL;
		goto err_out;
	}
	handle = kmalloc(sizeof(struct file_handle) + f_handle.handle_bytes,
			 GFP_KERNEL);
	if (!handle) {
		retval = -ENOMEM;
		goto err_out;
	}

	/* convert handle size to  multiple of sizeof(u32) */
	handle_dwords = f_handle.handle_bytes >> 2;

	/* we ask for a non connected handle */
	retval = exportfs_encode_fh(path->dentry,
				    (struct fid *)handle->f_handle,
				    &handle_dwords,  0);
	handle->handle_type = retval;
	/* convert handle size to bytes */
	handle_bytes = handle_dwords * sizeof(u32);
	handle->handle_bytes = handle_bytes;
	if ((handle->handle_bytes > f_handle.handle_bytes) ||
	    (retval == 255) || (retval == -ENOSPC)) {
		/* As per old exportfs_encode_fh documentation
		 * we could return ENOSPC to indicate overflow
		 * But file system returned 255 always. So handle
		 * both the values
		 */
		/*
		 * set the handle size to zero so we copy only
		 * non variable part of the file_handle
		 */
		handle_bytes = 0;
		retval = -EOVERFLOW;
	} else
		retval = 0;
	/* copy the mount id */
	if (copy_to_user(mnt_id, &path->mnt->mnt_id, sizeof(*mnt_id))) {
		retval = -EFAULT;
		goto err_free_out;
	}
	if (copy_to_user(ufh, handle,
			 sizeof(struct file_handle) + handle_bytes))
		retval = -EFAULT;
err_free_out:
	kfree(handle);
err_out:
	return retval;
}

/**
 * sys_name_to_handle_at: convert name to handle
 * @dfd: directory relative to which name is interpreted if not absolute
 * @name: name that should be converted to handle.
 * @handle: resulting file handle
 * @mnt_id: mount id of the file system containing the file
 * @flag: flag value to indicate whether to follow symlink or not
 *
 * @handle->handle_size indicate the space available to store the
 * variable part of the file handle in bytes. If there is not
 * enough space, the field is updated to return the minimum
 * value required.
 */
SYSCALL_DEFINE5(name_to_handle_at, int, dfd, const char __user *, name,
		struct file_handle __user *, handle, int __user*, mnt_id,
		int, flag)
{

	int follow;
	int fput_needed;
	long ret = -EINVAL;
	struct path path, *pp;
	struct file *file = NULL;

	if ((flag & ~AT_SYMLINK_FOLLOW) != 0)
		goto err_out;

	if (name == NULL && dfd != AT_FDCWD) {
		file = fget_light(dfd, &fput_needed);
		if (file) {
			pp = &file->f_path;
			ret = 0;
		} else
			ret = -EBADF;
	} else {
		follow = (flag & AT_SYMLINK_FOLLOW) ? LOOKUP_FOLLOW : 0;
		ret = user_path_at(dfd, name, follow, &path);
		pp = &path;
	}
	if (ret)
		goto err_out;
	/*
	 * We need t make sure wether the file system
	 * support decoding of the file handle
	 */
	if (!pp->mnt->mnt_sb->s_export_op ||
	    !pp->mnt->mnt_sb->s_export_op->fh_to_dentry) {
		ret = -EOPNOTSUPP;
		goto out_path;
	}
	ret = do_sys_name_to_handle(pp, handle, mnt_id);

out_path:
	if (file)
		fput_light(file, fput_needed);
	else
		path_put(&path);
err_out:
	return ret;
}
