/*
 *   fs/cifs/smb2proto.h
 *
 *   Copyright (c) International Business Machines  Corp., 2002,2011
 *   Author(s): Steve French (sfrench@us.ibm.com)
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
 *   You should have received a copy of the GNU Lesser General Public License
 *   along with this library; if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */
#ifndef _SMB2PROTO_H
#define _SMB2PROTO_H
#include <linux/nls.h>
#include <linux/key-type.h>

struct statfs;

/*
 *****************************************************************
 * All Prototypes
 *****************************************************************
 */

/* extern char *build_smb2path_from_dentry(struct dentry *);
extern __le16 *build_ucspath_from_dentry(struct dentry *);
extern __le16 *smb2_build_path_to_root(struct cifs_sb_info *smb2_sb);
extern void free_rsp_buf(int resp_buftype, void *pSMB2r);
extern struct smb2_hdr *smb2_buf_get(void);
extern void smb2_buf_release(void *);
extern struct smb2_hdr *smb2_small_buf_get(void);
extern void smb2_small_buf_release(void *);
extern __u64 get_mid(struct TCP_Server_Info *server);*/
extern int small_smb2_init_no_tc(__le16 smb2_cmd,
				struct cifs_ses *ses,
				void **request_buf);
extern int checkSMB2(struct smb2_hdr *smb2, __u64 mid, unsigned int length);
extern char *smb2_get_data_area_len(int *poff, int *pln, struct smb2_hdr *psmb);
extern unsigned int smb2_calc_size(struct smb2_hdr *ptr);
extern int map_smb2_to_linux_error(struct smb2_hdr *smb2, int logErr);

extern int smb2_send(struct TCP_Server_Info *, struct smb2_hdr *,
		     unsigned int /* length */);
extern int smb2_sendrcv2(const unsigned int /* xid */ , struct cifs_ses *,
			struct kvec *, int /* nvec to send */,
			int * /* type of buf returned */,
			int * /* smb2 network status code */, const int flags);
extern int smb2_send_complex(const unsigned int, struct cifs_ses *,
			     struct kvec *, int /* nvec to send */,
			     int * /* type of buf returned */,
			     int * /* smb2 network status code */,
			     struct mid_q_entry **mid, const unsigned int size);
extern int smb2_sendrcv_norsp(const unsigned int xid, struct cifs_ses *ses,
			struct smb2_hdr *in_buf, int flags);
extern int smb2_sendrcv_blocking(const unsigned int xid, struct cifs_tcon *tcon,
			struct smb2_hdr *in_buf,
			struct smb2_hdr *out_buf,
			int *pbytes_returned);
extern int sign_smb2(struct kvec *iov, int n_vec, struct TCP_Server_Info *);
/* BB FIXME - need to add SMB2's signing mechanism - not same as CIFS BB */
/*extern int smb2_verify_signature(struct smb2_hdr *,
				 const struct mac_key *mac_key);*/
extern int smb2_demultiplex_thread(struct TCP_Server_Info *server);
extern int smb2_observe_thread(struct TCP_Server_Info *server);
extern int smb2_reconnect(struct TCP_Server_Info *server);
extern int smb2_setup_session(unsigned int xid, struct cifs_ses *pses_info,
			      struct nls_table *nls_info);
extern int smb2_umount(struct super_block *, struct cifs_sb_info *);

extern int smb2_get_inode_info(struct inode **pinode, __le16 *search_path,
			FILE_ALL_INFO *pfile_info, struct super_block *sb,
			int xid);
extern struct smb2_file *smb2_new_fileinfo(struct inode *newinode,
					u64 persistfid, u64 volatile_fid,
					struct file *file, struct vfsmount *mnt,
					unsigned int oflags);
extern bool smb2_is_size_safe_to_change(struct smb2_inode *smb2_ind,
					__u64 end_of_file);
extern struct inode *smb2_iget(struct super_block *sb,
			       struct cifs_fattr *fattr);
extern void smb2_allinfo_to_fattr(struct cifs_fattr *attr,
				  FILE_ALL_INFO *pfile_info,
				  struct cifs_sb_info *smb2_sb);
extern void smb2_create_dfs_attr(struct cifs_fattr *fattr,
				 struct super_block *sb);
extern void cifs_fattr_to_inode(struct inode *pinode, struct cifs_fattr *attr);
extern int smb2_fsync(struct file *file, int datasync);
extern int smb2_flush(struct file *file, fl_owner_t id);

/* extern char *smb2_compose_mount_options(const char *sb_mountdata,
			const char *fullpath, const struct dfs_info3_param *ref,
			char **devname);
extern void smb2_dfs_release_automount_timer(void);

extern void smb2_del_oplock_entry(struct oplock_entry *);
extern struct oplock_entry *smb2_alloc_oplock_entry(struct inode *inode, u64 fd,
						 struct cifs_tcon *tcon);
extern int decode_neg_token_init(unsigned char *security_blob, int length,
				 enum security_enum *sec_type); */

/*
 *  SMB2 Worker functions - most of protocol specific implementation details
 *  are contained within these calls
 */
extern int SMB2_negotiate(unsigned int xid, struct cifs_ses *ses);
extern int SMB2_sess_setup(unsigned int xid, struct cifs_ses *ses,
			   const struct nls_table *nls_cp);
extern int SMB2_tcon(unsigned int xid, struct cifs_ses *ses,
		    const char *tree, struct cifs_tcon *tcon,
		    const struct nls_table *);
extern int SMB2_tdis(const int xid, struct cifs_tcon *tcon);
extern int SMB2_logoff(const int xid, struct cifs_ses *ses);
extern int SMB2_echo(const int xid, struct cifs_tcon *tcon);
extern int SMB2_QFS_info(const int xid, struct cifs_tcon *tcon,
			u64 persistent_file_id, u64 volatile_file_id,
			struct kstatfs *FSData);
extern int SMB2_QFS_vol_info(const int xid, struct cifs_tcon *tcon,
			u64 persistent_fid, u64 volatile_fid);
extern int SMB2_QFS_attribute_info(const int xid, struct cifs_tcon *tcon,
				   u64 persistent_fid, u64 volatile_fid);
extern int SMB2_QFS_device_info(const int xid, struct cifs_tcon *tcon,
				u64 persistent_fid, u64 volatile_fid);
extern int SMB2_oplock_break(struct cifs_tcon *ptcon, __u64 netfid);
extern int SMB2_query_info(const int xid, struct cifs_tcon *tcon,
			   u64 persistent_file_id, u64 volatile_file_id,
			   FILE_ALL_INFO *pFindData);
int SMB2_query_directory(const int xid, struct cifs_tcon *tcon,
	 u64 persistent_fid, u64 volatile_fid, int index, struct smb2_search *);
extern int SMB2_set_info(const int xid, struct cifs_tcon *tcon,
			   u64 persistent_file_id, u64 volatile_file_id,
			   FILE_BASIC_INFO *pFindData);
extern int SMB2_set_delete(const int xid, struct cifs_tcon *tcon,
			   u64 persistent_file_id, u64 volatile_file_id);
extern int SMB2_set_hardlink(const int xid, struct cifs_tcon *tcon,
		    u64 persistent_fid, u64 volatile_fid, __le16 *target_file);
extern int SMB2_rename(const int xid, struct cifs_tcon *tcon,
		    u64 persistent_fid, u64 volatile_fid, __le16 *target_file);
extern int SMB2_open(const int xid, struct cifs_tcon *tcon, __le16 *path,
	      u64 *persistent_fid, u64 *volatile_fid, __le32 desired_access,
	      __le32 create_disposition, __le32 file_attributes,
	      __le32 create_options);
extern int SMB2_symlink_ioctl(const int, struct cifs_tcon *, u32, u64, u64,
				const char *);
extern int SMB2_close(const int xid, struct cifs_tcon *tcon,
			u64 persistent_file_id, u64 volatile_file_id);
extern int SMB2_read(const int xid, struct cifs_tcon *tcon,
		u64 persistent_fid, u64 volatile_fid,
		const unsigned int count, const __u64 lseek,
		unsigned int *nbytes, char **buf, int *pbuf_type,
		unsigned int remaining_bytes);
extern int SMB2_write(const int xid, struct cifs_tcon *tcon,
	const u64 persistent_fid, const u64 volatile_fid,
	const unsigned int count, const __u64 lseek,
	unsigned int *nbytes, struct kvec *iov, int n_vec,
	const unsigned int remaining_bytes, int wtimeout);
extern int SMB2_write_complex(const int xid, struct cifs_tcon *tcon,
	const u64 persistent_fid, const u64 volatile_fid,
	const unsigned int count, const __u64 lseek,
	unsigned int *nbytes, struct kvec *iov, int n_vec,
	const unsigned int remaining_bytes, struct mid_q_entry **mid,
	const unsigned int size);
extern int SMB2_flush(const int xid, struct cifs_tcon *tcon,
			u64 persistent_file_id, u64 volatile_file_id);
extern int SMB2_query_full_ea_info(const int xid, struct cifs_tcon *tcon,
				u64 persistent_fid, u64 volatile_fid,
				char *pdata, int buf_len, int rsp_output_len,
				struct kvec *iov, int n_vec,
				const char *prefix, int prefix_len);
extern int SMB2_set_ea_info(const int xid, struct cifs_tcon *tcon,
			u64 persistent_fid, u64 volatile_fid,
			struct kvec iov[4]);
extern int SMB2_lock(const int xid, struct cifs_tcon *tcon,
		     const u64 persistent_fid, const u64 volatile_fid,
		     u64 length, u64 offset, u32 lockFlags, int wait);
extern void DeleteMidQEntryComplex(struct mid_q_entry *midEntry);
extern int new_read_req(struct kvec *iov, struct cifs_tcon *tcon,
			u64 persistent_fid, u64 volatile_fid,
			const unsigned int count, const __u64 lseek,
			unsigned int remaining_bytes,
			int request_type);
extern int smb2_sendv(struct TCP_Server_Info *server, struct kvec *iov,
		      int n_vec);
extern int smb2_wait_on_complex_mid(struct cifs_ses *ses,
				    struct mid_q_entry *mid,
				    unsigned long timeout,
				    unsigned long time_to_wait);
extern int smb2_readresp(struct TCP_Server_Info *server, bool cleanup);
/* extern void smb2_oplock_break(struct work_struct *);
extern bool is_smb2_oplock_break(struct smb2_hdr *, struct TCP_Server_Info *); */

#endif			/* _SMB2PROTO_H */
