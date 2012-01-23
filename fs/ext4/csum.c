/*
 * linux/fs/ext4/csum.c
 *
 * Automatic SHA-1 (FIPS 180-1) data checksummig
 *
 * Copyright (C) 2012 Parallels, inc.
 *
 * Author: Konstantin Khlebnikov
 *
 */

#include <linux/fs.h>
#include <linux/jbd2.h>
#include <linux/cryptohash.h>
#include "ext4.h"
#include "xattr.h"

#include <trace/events/ext4.h>

static void ext4_init_data_csum(struct inode *inode)
{
	EXT4_I(inode)->i_data_csum_end = 0;
	sha_init((__u32 *)EXT4_I(inode)->i_data_csum);
	ext4_set_inode_state(inode, EXT4_STATE_CSUM);
	percpu_counter_inc(&EXT4_SB(inode->i_sb)->s_csum_partial);
}

void ext4_clear_data_csum(struct inode *inode)
{
	ext4_clear_inode_state(inode, EXT4_STATE_CSUM);
	if (!S_ISREG(inode->i_mode))
		return;
	if (EXT4_I(inode)->i_data_csum_end < 0)
		percpu_counter_dec(&EXT4_SB(inode->i_sb)->s_csum_complete);
	else
		percpu_counter_dec(&EXT4_SB(inode->i_sb)->s_csum_partial);
}

void ext4_start_data_csum(struct inode *inode)
{
	if (!ext4_test_inode_state(inode, EXT4_STATE_CSUM)) {
		spin_lock(&inode->i_lock);
		if (!ext4_test_inode_state(inode, EXT4_STATE_CSUM))
			ext4_init_data_csum(inode);
		spin_unlock(&inode->i_lock);
	}
	trace_ext4_start_data_csum(inode, inode->i_size);
}

int ext4_get_data_csum(struct inode *inode, u8 *csum, size_t size)
{
	if (size != EXT4_DATA_CSUM_SIZE)
		return -EINVAL;
	if (ext4_test_inode_state(inode, EXT4_STATE_CSUM)) {
		spin_lock(&inode->i_lock);
		memcpy(csum, EXT4_I(inode)->i_data_csum, size);
		spin_unlock(&inode->i_lock);
		return 0;
	}
	return -ESRCH;
}

int ext4_load_data_csum(struct inode *inode)
{
	int ret;

	ret = ext4_xattr_get(inode, EXT4_XATTR_INDEX_TRUSTED,
			EXT4_DATA_CSUM_NAME, EXT4_I(inode)->i_data_csum,
			EXT4_DATA_CSUM_SIZE);
	if (ret < 0)
		return ret;
	if (ret != EXT4_DATA_CSUM_SIZE)
		return -EIO;

	EXT4_I(inode)->i_data_csum_end = -1;
	ext4_set_inode_state(inode, EXT4_STATE_CSUM);
	percpu_counter_inc(&EXT4_SB(inode->i_sb)->s_csum_complete);
	return 0;
}

static int ext4_save_data_csum(struct inode *inode, u8 *csum)
{
	int ret;

	spin_lock(&inode->i_lock);
	if (ext4_test_inode_state(inode, EXT4_STATE_CSUM))
		ext4_clear_data_csum(inode);
	memcpy(EXT4_I(inode)->i_data_csum, csum, EXT4_DATA_CSUM_SIZE);
	EXT4_I(inode)->i_data_csum_end = -1;
	ext4_set_inode_state(inode, EXT4_STATE_CSUM);
	percpu_counter_inc(&EXT4_SB(inode->i_sb)->s_csum_complete);
	spin_unlock(&inode->i_lock);
	trace_ext4_save_data_csum(inode, inode->i_size);

	/* In order to guarantie csum consistenty force block allocation first */
	ret = ext4_alloc_da_blocks(inode);
	if (ret)
		return ret;

	return ext4_xattr_set(inode, EXT4_XATTR_INDEX_TRUSTED,
			EXT4_DATA_CSUM_NAME, EXT4_I(inode)->i_data_csum,
			EXT4_DATA_CSUM_SIZE, 0);
}

void ext4_load_dir_csum(struct inode *inode)
{
	char value[EXT4_DIR_CSUM_VALUE_LEN];
	int ret;

	ret = ext4_xattr_get(inode, EXT4_XATTR_INDEX_TRUSTED,
			     EXT4_DATA_CSUM_NAME, value, sizeof(value));
	if (ret == EXT4_DIR_CSUM_VALUE_LEN &&
	    !strncmp(value, EXT4_DIR_CSUM_VALUE, sizeof(value)))
		ext4_set_inode_state(inode, EXT4_STATE_CSUM);
}

void ext4_save_dir_csum(struct inode *inode)
{
	ext4_set_inode_state(inode, EXT4_STATE_CSUM);
	ext4_xattr_set(inode, EXT4_XATTR_INDEX_TRUSTED,
			EXT4_DATA_CSUM_NAME,
			EXT4_DIR_CSUM_VALUE,
			EXT4_DIR_CSUM_VALUE_LEN, 0);
}

int ext4_truncate_data_csum(struct inode *inode, loff_t pos)
{
	int ret = 0;

	if (!S_ISREG(inode->i_mode))
		return 0;

	trace_ext4_truncate_data_csum(inode, pos);

	if (EXT4_I(inode)->i_data_csum_end < 0)
		ext4_xattr_set(inode, EXT4_XATTR_INDEX_TRUSTED,
				EXT4_DATA_CSUM_NAME, NULL, 0, 0);

	if (EXT4_I(inode)->i_data_csum_end < 0 ||
	    EXT4_I(inode)->i_data_csum_end > pos) {
		spin_lock(&inode->i_lock);
		ext4_clear_data_csum(inode);
		if (!pos && test_opt2(inode->i_sb, CSUM))
			ext4_init_data_csum(inode);
		else
			ret = -1;
		spin_unlock(&inode->i_lock);
	}
	return ret;
}

void ext4_update_data_csum(struct inode *inode, loff_t pos,
			   unsigned len, struct page* page)
{
	__u32 *digest = (__u32 *)EXT4_I(inode)->i_data_csum;
	__u32 work[SHA_WORKSPACE_WORDS];
	const u8 *kaddr, *data;

	len += pos & (SHA_MESSAGE_BYTES-1);
	len &= ~(SHA_MESSAGE_BYTES-1);
	pos &= ~(loff_t)(SHA_MESSAGE_BYTES-1);

	if ((pos != EXT4_I(inode)->i_data_csum_end &&
	     ext4_truncate_data_csum(inode, pos)) || !len)
		return;

	EXT4_I(inode)->i_data_csum_end += len;

	kaddr = kmap_atomic(page, KM_USER0);
	data = kaddr + (pos & (PAGE_CACHE_SIZE - 1));
	for ( ; len ; len -= SHA_MESSAGE_BYTES, data += SHA_MESSAGE_BYTES )
		sha_transform(digest, data, work);
	kunmap_atomic(kaddr, KM_USER0);

	trace_ext4_update_data_csum(inode, pos);
}

static int ext4_finish_data_csum(struct inode *inode, u8 *csum)
{
	__u32 *digest = (__u32 *)csum;
	__u8 data[SHA_MESSAGE_BYTES * 2];
	__u32 work[SHA_WORKSPACE_WORDS];
	loff_t end;
	unsigned tail;
	__be64 bits;

	BUILD_BUG_ON(EXT4_DATA_CSUM_SIZE != SHA_DIGEST_WORDS * 4);

	memcpy(csum, EXT4_I(inode)->i_data_csum, EXT4_DATA_CSUM_SIZE);

	end = EXT4_I(inode)->i_data_csum_end;
	if (end < 0)
		return 0;

	tail = inode->i_size - end;
	if (tail >= SHA_MESSAGE_BYTES)
		return -EIO;

	if (tail) {
		struct page *page;
		const u8 *kaddr;

		page = read_cache_page_gfp(inode->i_mapping,
					   end >> PAGE_CACHE_SHIFT,
					   GFP_NOFS);
		if (IS_ERR(page))
			return PTR_ERR(page);

		kaddr = kmap_atomic(page, KM_USER0);
		memcpy(data, kaddr + (end & (PAGE_CACHE_SIZE-1)), tail);
		kunmap_atomic(kaddr, KM_USER0);
		page_cache_release(page);
	}

	memset(data + tail, 0, sizeof(data) - tail);
	data[tail] = 0x80;

	bits = cpu_to_be64((end + tail) << 3);
	if (tail >= SHA_MESSAGE_BYTES - sizeof(bits)) {
		memcpy(data + SHA_MESSAGE_BYTES * 2 - sizeof(bits),
				&bits, sizeof(bits));
		sha_transform(digest, data, work);
		sha_transform(digest, data + SHA_MESSAGE_BYTES, work);
	} else {
		memcpy(data + SHA_MESSAGE_BYTES - sizeof(bits),
				&bits, sizeof(bits));
		sha_transform(digest, data, work);
	}

	for (tail = 0; tail < SHA_DIGEST_WORDS ; tail++)
		digest[tail] = cpu_to_be32(digest[tail]);

	return 0;
}

void ext4_commit_data_csum(struct inode *inode)
{
	u8 csum[EXT4_DATA_CSUM_SIZE];

	if (!S_ISREG(inode->i_mode) || EXT4_I(inode)->i_data_csum_end < 0)
		return;

	mutex_lock(&inode->i_mutex);
	if (ext4_test_inode_state(inode, EXT4_STATE_CSUM) &&
	    !ext4_finish_data_csum(inode, csum))
		ext4_save_data_csum(inode, csum);
	else
		ext4_truncate_data_csum(inode, 0);
	mutex_unlock(&inode->i_mutex);
}

static int ext4_xattr_trusted_csum_get(struct inode *inode, const char *name,
				       void *buffer, size_t size)
{
	int i, ret = EXT4_DATA_CSUM_SIZE * 2;
	u8 csum[EXT4_DATA_CSUM_SIZE];

	if (strcmp(name, ""))
		return -ENODATA;

	if (!test_opt2(inode->i_sb, CSUM))
		return -EOPNOTSUPP;

	if (S_ISDIR(inode->i_mode))
		return ext4_xattr_get(inode, EXT4_XATTR_INDEX_TRUSTED,
				      EXT4_DATA_CSUM_NAME, buffer, size);

	if (!S_ISREG(inode->i_mode))
		return -ENODATA;

	if (!buffer)
		return ret;

	if (size < ret)
		return -ERANGE;

	spin_lock(&inode->i_lock);
	if (ext4_test_inode_state(inode, EXT4_STATE_CSUM) &&
	    EXT4_I(inode)->i_data_csum_end < 0) {
		memcpy(csum, EXT4_I(inode)->i_data_csum, EXT4_DATA_CSUM_SIZE);
	} else
		ret = -ENODATA;
	spin_unlock(&inode->i_lock);

	for ( i = 0 ; ret > 0 && i < EXT4_DATA_CSUM_SIZE ; i++ )
		buffer = pack_hex_byte(buffer, csum[i]);

	return ret;
}

static int ext4_xattr_trusted_csum_set(struct inode *inode, const char *name,
				const void *value, size_t size, int flags)
{
	const char *text = value;
	u8 csum[EXT4_DATA_CSUM_SIZE];
	int i;

	if (strcmp(name, ""))
		return -ENODATA;

	if (!test_opt2(inode->i_sb, CSUM))
		return -EOPNOTSUPP;

	if (S_ISDIR(inode->i_mode)) {
		if (!value)
			ext4_clear_inode_state(inode, EXT4_STATE_CSUM);
		else if (size == EXT4_DIR_CSUM_VALUE_LEN &&
			 !strncmp(value, EXT4_DIR_CSUM_VALUE, size))
			ext4_set_inode_state(inode, EXT4_STATE_CSUM);
		else
			return -EINVAL;

		return ext4_xattr_set(inode, EXT4_XATTR_INDEX_TRUSTED,
				      EXT4_DATA_CSUM_NAME, value, size, flags);
	}

	if (!S_ISREG(inode->i_mode))
		return -ENODATA;

	if (ext4_test_inode_state(inode, EXT4_STATE_CSUM)) {
		if (flags & XATTR_CREATE)
			return -EEXIST;
	} else {
		if (flags & XATTR_REPLACE)
			return -ENODATA;
	}

	if (!value) {
		ext4_truncate_data_csum(inode, 1);
		return 0;
	}

	if (size != EXT4_DATA_CSUM_SIZE * 2)
		return -EINVAL;

	for ( i = 0 ; i < EXT4_DATA_CSUM_SIZE ; i++ ) {
		int hi = hex_to_bin(text[i*2]);
		int lo = hex_to_bin(text[i*2+1]);
		if ((hi < 0) || (lo < 0))
			return -EINVAL;
		csum[i] = (hi << 4) | lo;
	}

	if (mapping_writably_mapped(inode->i_mapping))
		return -EBUSY;

	return ext4_save_data_csum(inode, csum);
}

#define XATTR_TRUSTED_CSUM_PREFIX XATTR_TRUSTED_PREFIX EXT4_DATA_CSUM_NAME
#define XATTR_TRUSTED_CSUM_PREFIX_LEN (sizeof (XATTR_TRUSTED_CSUM_PREFIX) - 1)

static size_t
ext4_xattr_trusted_csum_list(struct inode *inode, char *list, size_t list_size,
			     const char *name, size_t name_len)
{
	return 0;
}

struct xattr_handler ext4_xattr_trusted_csum_handler = {
	.prefix = XATTR_TRUSTED_CSUM_PREFIX,
	.list   = ext4_xattr_trusted_csum_list,
	.get    = ext4_xattr_trusted_csum_get,
	.set    = ext4_xattr_trusted_csum_set,
};
