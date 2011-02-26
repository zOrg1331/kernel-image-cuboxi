/*
 *   fs/smb2/smb2glob.h
 *
 *   Definitions for various global variables and structures
 *
 *   Copyright (C) International Business Machines  Corp., 2002,2011
 *   Author(s): Steve French (sfrench@us.ibm.com)
 *              Jeremy Allison (jra@samba.org)
 *
 *   This library is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU Lesser General Public License as published
 *   by the Free Software Foundation; either version 2.1 of the License, or
 *   (at your option) any later version.
 *
 *   This library is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
 *   the GNU Lesser General Public License for more details.
 *
 */
#include <linux/in.h>
#include <linux/in6.h>
#include <linux/workqueue.h>
#include "smb2pdu.h"

/*
 * The sizes of various internal tables and strings
 */

#define SMB2_MIN_RCV_POOL 4


/*
 *****************************************************************
 * Except the SMB2 PDUs themselves all the
 * globally interesting structs should go here
 *****************************************************************
 */

#define SMB2_OBSERVE_CHECK_TIME	20
#define SMB2_OBSERVE_DELETE_TIME	45

/* Values for tcon->speed set by echo command */
#define SMB2_ECHO_FAST		1	/* Less than 3 jiffies, 12ms	     */
#define SMB2_ECHO_OK		2	/* Less than 15 jiffies, 60ms	     */
#define SMB2_ECHO_SLOW		3	/* Less than 125 jiffies, 1/2 sec    */
#define SMB2_ECHO_VERY_SLOW	4	/* Less than 1000 jiffies, 4 seconds */
#define SMB2_ECHO_TIMEOUT	5	/* Else Too long, server is sick ... */

/*
 * This info hangs off the smb2_file structure, pointed to by llist.
 * This is used to track byte stream locks on the file
 */
struct smb2_lock {
	struct list_head llist;	/* pointer to next smb2_lock */
	__u64 offset;
	__u64 length;
	__u32 flags;
};

/*
 * One of these for each open instance of a file
 */
struct smb2_search {
	loff_t index_of_last_entry;
	__u16 entries_in_buf;
	__u32 resume_key;
	char *ntwrk_buf_start;
	char *srch_entries_start;
	char *last_entry;
	char *presume_name;
	unsigned int resume_name_len;
	bool search_end:1;
	bool empty_dir:1;
	bool small_buf:1; /* so we know which buf_release function to call */
};

struct smb2_file {
	struct list_head tlist;	/* pointer to next fid owned by tcon */
	struct list_head flist;	/* next fid (file instance) for this inode */
	unsigned int uid;	/* allows finding which FileInfo structure */
	__u32 pid;		/* process id who opened file */
	u64 persist_fid;
	u64 volatile_fid;
	/* BB add lock scope info here if needed */ ;
	/* lock scope id (0 if none) */
	struct dentry *dentry; /* needed for writepage and oplock break */
	struct mutex lock_mutex;
	struct list_head llist; /* list of byte range locks we have. */
	unsigned int f_flags;
	bool close_pend:1;	/* file is marked to close */
	bool invalid_handle:1;	/* file closed via session abend */
	bool message_mode:1;	/* for pipes: message vs byte mode */
	bool is_dir:1;		/* Open directory rather than file */
	bool oplock_break_cancelled:1;
	atomic_t count;		/* reference count */
	atomic_t wrt_pending;   /* handle in use - defer close */
	struct work_struct oplock_break; /* work for oplock breaks */
	struct mutex fh_mutex; /* prevents reopen race after dead ses*/
	struct smb2_search srch_inf;
};

/*
 * One of these for each file inode
 */

struct smb2_inode {
	struct list_head lock_list;
	/* BB add in lists for dirty pages i.e. write caching info for oplock */
	struct list_head open_file_list;
	int write_behind_rc;
	__u32 dos_attrs; /* e.g. DOS archive bit, sparse, compressed, system */
	__u32 ea_size;
	unsigned long time;	/* jiffies of last update/check of inode */
	u64 server_eof;  /* current file size on server */
	bool can_cache_read:1;	/* read oplock */
	bool can_cache_all:1;	/* read and writebehind oplock */
	bool can_defer_close:1; /* batch oplock: as above but can defer close */
	bool oplock_pending:1;
	bool delete_pending:1;	/* DELETE_ON_CLOSE is set */
	u64 uniqueid; /* server inode number */
	struct fscache_cookie *fscache;
	struct inode vfs_inode;
};

static inline struct smb2_inode *
SMB2_I(struct inode *inode)
{
	return container_of(inode, struct smb2_inode, vfs_inode);
}


static inline void smb2_file_get(struct smb2_file *smb2_file)
{
	atomic_inc(&smb2_file->count);
}

/* Release a reference on the file private data */
/* BB see file.c cifsFileInfo_put MUSTFIX BB */
static inline void smb2_file_put(struct smb2_file *smb2_file)
{
	if (atomic_dec_and_test(&smb2_file->count)) {
		iput(smb2_file->dentry->d_inode);
		kfree(smb2_file);
	}
}

/* Represents a read request in page sized blocks.
 * Used by smb2_readpages().*/
struct page_req {
	struct list_head req_node; /* list of page_req's */
	struct list_head *page_list_index; /* list of pages */
	struct address_space *mapping;
	int num_pages;
	int read_size;
	int start_page_index; /* first expected index */
	int end_page_index; /* last expected index */
	struct mid_q_entry *midq; /* queue structure for demultiplex */
};

/* one of these for every pending SMB2 request to the server */
struct smb2_mid_entry {
	struct list_head qhead;	/* mids waiting on reply from this server */
	__u64 mid;		/* multiplex id(s) */
	__u16 pid;		/* process id */
	__u32 sequence_number;	/* for signing */ /* BB check if needed */
	unsigned long when_alloc;  /* when mid was created */
#ifdef CONFIG_CIFS_STATS2
	unsigned long when_sent; /* time when smb send finished */
	unsigned long when_received; /* when demux complete (taken off wire) */
#endif
	struct task_struct *tsk;	/* task waiting for response */
	struct smb2_hdr *resp_buf;	/* response buffer */
	char **pagebuf_list;	        /* response buffer */
	int num_pages;
	int mid_state;	/* wish this were enum but can not pass to wait_event */
	__le16 command;	/* smb command code */
	bool async_resp_rcvd:1; /* if server has responded with interim resp */
	bool large_buf:1;	/* if valid response, is pointer to large buf */
	bool is_kmap_buf:1;
/*	bool multi_rsp:1; BB do we have to account for something in SMB2 like
	we saw multiple trans2 responses for one request (possible in CIFS) */
	/* Async things */
	__u64 *mid_list;	/* multiplex id(s) */
	int *mid_state_list;
	short int *large_buf_list;
	unsigned int num_mid;
	unsigned int act_num_mid;
	unsigned int num_received;
	unsigned int cur_id;
	struct smb2_hdr **resp_buf_list;	/* response buffer */
	__le16 *command_list;
	bool async:1;
	bool complex_mid:1; /* complex entry - consists of several messages */
	int result;
	unsigned long last_rsp_time;
	int (*callback)(struct smb2_mid_entry * , void *);
	void *callback_data;
};


#define   SMB2SEC_DEF (SMB2SEC_MAY_SIGN | SMB2SEC_MAY_NTLM | SMB2SEC_MAY_NTLMV2)
#define   SMB2SEC_MAX (SMB2SEC_MUST_SIGN | SMB2SEC_MUST_NTLMV2)
#define   SMB2SEC_AUTH_MASK (SMB2SEC_MAY_NTLM | SMB2SEC_MAY_NTLMV2 | \
			     SMB2SEC_MAY_PLNTXT | SMB2SEC_MAY_KRB5)
/*
 *****************************************************************
 * Constants go here
 *****************************************************************
 */


/* BB since num credits could be negotiated higher, override with max_pending */
#define SMB2_MAX_REQ 256

/* Identifiers for functions that use the open, operation, close pattern
 * in inode.c:open_op_close() */
#define SMB2_OP_SET_DELETE 1
#define SMB2_OP_SET_INFO 2
#define SMB2_OP_QUERY_INFO 3
#define SMB2_OP_QUERY_DIR 4
#define SMB2_OP_MKDIR 5
#define SMB2_OP_RENAME 6

/* Used when constructing chained read requests. */
#define CHAINED_REQUEST 1
#define START_OF_CHAIN 2
#define END_OF_CHAIN 4
#define RELATED_REQUEST 8

/*
 * The externs for various global variables put here.  The actual declarations
 * of these should be mostly placed at the front of smb2fs.c to be easy to spot
 */


/*
 *  Global counters, updated atomically
 */
extern atomic_t smb2_tcon_reconnect_count;

/* Various Debug counters */
extern atomic_t smb2_buf_alloc_count;    /* current number allocated */
#ifdef CONFIG_SMB2_STATS2
extern atomic_t smb2_total_buf_alloc; /* total allocated over all time */
extern atomic_t smb2_total_smbuf_alloc;
#endif
extern atomic_t smb2_smbuf_alloc_count;
extern atomic_t smb2_mid_count;

/* Misc globals */
extern unsigned int SMB2_max_buf_size;  /* max size not including hdr */
extern unsigned int smb2_min_rcv;    /* min size of big ntwrk buf pool */
extern unsigned int smb2_min_small;  /* min size of small buf pool */
extern unsigned int smb2_max_pending; /* MAX requests at once to server*/
