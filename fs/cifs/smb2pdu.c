/*
 *   fs/cifs/smb2pdu.c
 *
 *   Copyright (C) International Business Machines  Corp., 2009,2011
 *   Author(s): Steve French (sfrench@us.ibm.com)
 *
 *   Contains the routines for constructing the SMB2 PDUs themselves
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

 /* SMB2 PDU handling routines here - except for leftovers (eg session setup) */
 /* Note that there are handle based routines which must be		      */
 /* treated slightly differently for reconnection purposes since we never     */
 /* want to reuse a stale file handle and only the caller knows the file info */

#include <linux/fs.h>
#include <linux/kernel.h>
#include <linux/vfs.h>
#include <linux/uaccess.h>
#include <linux/xattr.h>
#include "smb2pdu.h"
#include "cifsglob.h"
#include "cifsacl.h"
#include "cifsproto.h"
#include "smb2proto.h"
#include "cifs_unicode.h"
#include "cifs_debug.h"
#include "ntlmssp.h"
#include "smb2status.h"

/* Mark as invalid, all open files on tree connections since they
   were closed when session to server was lost */
static void mark_open_files_invalid(struct cifs_tcon *ptcon)
{
	struct smb2_file *open_file = NULL;
	struct list_head *tmp;
	struct list_head *tmp1;

/* list all files open on tree connection and mark them invalid */
	spin_lock(&cifs_file_list_lock);
	list_for_each_safe(tmp, tmp1, &ptcon->openFileList) {
		open_file = list_entry(tmp, struct smb2_file, tlist);
		open_file->invalid_handle = true;
	}
	spin_unlock(&cifs_file_list_lock);
	/* BB Add call to invalidate_inodes(sb) for all superblocks mounted
	   to this tcon */
}


/*
 *  The following table defines the expected "StructureSize" of SMB2 requests
 *  in order by SMB2 command.  This is similar to "wct" in SMB/CIFS requests.
 *
 *  Note that commands are defined in smb2pdu.h in le16 but the array below is
 *  indexed by command in host byte order
 */
static const int smb2_req_struct_sizes[NUMBER_OF_SMB2_COMMANDS] = {
	/* SMB2_NEGOTIATE */ 36,
	/* SMB2_SESSION_SETUP */ 25,
	/* SMB2_LOGOFF */ 4,
	/* SMB2_TREE_CONNECT */	9,
	/* SMB2_TREE_DISCONNECT */ 4,
	/* SMB2_CREATE */ 57,
	/* SMB2_CLOSE */ 24,
	/* SMB2_FLUSH */ 24,
	/* SMB2_READ */	49,
	/* SMB2_WRITE */ 49,
	/* SMB2_LOCK */	48,
	/* SMB2_IOCTL */ 57,
	/* SMB2_CANCEL */ 4,
	/* SMB2_ECHO */ 4,
	/* SMB2_QUERY_DIRECTORY */ 33,
	/* SMB2_CHANGE_NOTIFY */ 32,
	/* SMB2_QUERY_INFO */ 41,
	/* SMB2_SET_INFO */ 33,
	/* SMB2_OPLOCK_BREAK */  24 /* BB this is 36 for LEASE_BREAK variant */
};


/* NB: MID can not be set if tcon not passed in, in that
   case it is responsbility of caller to set the mid */
static void
smb2_hdr_assemble(struct smb2_hdr *buffer, __le16 smb2_cmd /* command */ ,
		const struct cifs_tcon *tcon)
{
	struct list_head *temp_item;
	struct cifs_ses *ses;
	struct smb2_pdu *smb = (struct smb2_pdu *)buffer;
	char *temp = (char *) buffer;
	/* lookup word count ie StructureSize from table */
	__u16 parmsize = smb2_req_struct_sizes[le16_to_cpu(smb2_cmd)];

	/* smaller than SMALL_BUFFER_SIZE but bigger than fixed area of
	   largest operations (Create) */
	memset(temp, 0, 256);

	/* Note this is only network field converted to big endian */
	buffer->smb2_buf_length = cpu_to_be32(parmsize + sizeof(struct smb2_hdr)
			- 4 /*  RFC 1001 length field itself not counted */);

	buffer->ProtocolId[0] = 0xFE;
	buffer->ProtocolId[1] = 'S';
	buffer->ProtocolId[2] = 'M';
	buffer->ProtocolId[3] = 'B';
	buffer->StructureSize = cpu_to_le16(64);
	buffer->Command = smb2_cmd;
	buffer->CreditRequest = cpu_to_le16(2); /* BB make this dynamic */
	buffer->ProcessId = cpu_to_le32((__u16)current->tgid);
	if (tcon) {
		buffer->TreeId = tcon->tid;
		/* For the multiuser case, there are few obvious technically  */
		/* possible mechanisms to match the local linux user (uid)    */
		/* to a valid remote smb user (smb_uid):		      */
		/*	1) Query Winbind (or other local pam/nss daemon       */
		/*	  for userid/password/logon_domain or credential      */
		/*      2) Query Winbind for uid to sid to username mapping   */
		/*	   and see if we have a matching password for existing*/
		/*         session for that user perhas getting password by   */
		/*         adding a new pam_smb2 module that stores passwords */
		/*         so that the smb2 vfs can get at that for all logged*/
		/*	   on users					      */
		/*	3) (Which is the mechanism we have chosen)	      */
		/*	   Search through sessions to the same server for a   */
		/*	   a match on the uid that was passed in on mount     */
		/*         with the current processes uid (or euid?) and use  */
		/*	   that smb uid.   If no existing smb session for     */
		/* 	   that uid found, use the default smb session ie     */
		/*         the smb session for the volume mounted which is    */
		/*	   the same as would be used if the multiuser mount   */
		/*	   flag were disabled.  */

		/*  BB Add support for establishing new tcon and SMB Session  */
		/*      with userid/password pairs found on the smb session   */
		/*	for other target tcp/ip addresses		BB    */
		if (tcon->ses) {
			/* Uid is not converted */
			buffer->SessionId = tcon->ses->Suid;
			/* BB check this against related recent cifs changes */
			if (multiuser_mount != 0) {
				if (current_fsuid() !=
				    tcon->ses->linux_uid) {
					cFYI(1, "Multiuser mode and UID "
						 "did not match tcon uid");
					spin_lock(&cifs_tcp_ses_lock);
					list_for_each(temp_item,
					    &tcon->ses->server->smb_ses_list) {
						ses = list_entry(temp_item,
							struct cifs_ses,
							smb_ses_list);
						if (ses->linux_uid == current_fsuid()) {
							if (ses->server == tcon->ses->server) {
								buffer->SessionId = ses->Suid;
								break;
							} else {
				/* BB eventually call smb2_setup_session here */
								cFYI(1, "local UID found but no smb sess with this server exists");
							}
						}
					}
					spin_unlock(&cifs_tcp_ses_lock);
				}
			}
		}
		 /* BB check following DFS flags BB */
		/* BB do we have to add check for SHI1005_FLAGS_DFS_ROOT too? */
		if (tcon->share_flags & SHI1005_FLAGS_DFS)
			buffer->Flags |= SMB2_FLAGS_DFS_OPERATIONS;
/* BB how does SMB2 do case sensitive? */
/*		if (tcon->nocase)
			buffer->Flags  |= SMBFLG_CASELESS; */
		if ((tcon->ses) && (tcon->ses->server))
			if (tcon->ses->server->sec_mode &
			      SMB2_NEGOTIATE_SIGNING_REQUIRED)
				buffer->Flags |= SMB2_FLAGS_SIGNED;
	}

	smb->StructureSize2 = cpu_to_le16(parmsize);
	return;
}

/* Allocate and return pointer to an SMB request buffer, and set basic
   SMB information in the SMB header.  If the return code is zero, this
   function must have filled in request_buf pointer */
static int
small_smb2_init(__le16 smb2_command, struct cifs_tcon *tcon,
		void **request_buf)
{
	int rc = 0;

	/* SMBs NegProt, SessSetup, uLogoff do not have tcon yet so
	   check for tcp and smb session status done differently
	   for those three - in the calling routine */
	if (tcon) {
		if (tcon->tidStatus == CifsExiting) {
			/* only tree disconnect, open, and write,
			(and ulogoff which does not have tcon)
			are allowed as we start force umount */
			if ((smb2_command != SMB2_WRITE) &&
			   (smb2_command != SMB2_CREATE) &&
			   (smb2_command != SMB2_TREE_DISCONNECT)) {
				cFYI(1, "can not send cmd %d while umounting",
					smb2_command);
				return -ENODEV;
			}
		}
		if ((tcon->ses) && (tcon->ses->status != CifsExiting) &&
				  (tcon->ses->server)) {
			struct nls_table *nls_codepage;
				/* Give Demultiplex thread up to 10 seconds to
				   reconnect, should be greater than smb2 socket
				   timeout which is 7 seconds */
			while (tcon->ses->server->tcpStatus ==
				CifsNeedReconnect) {
				/* Return to caller for TREE_DISCONNECT
				   and LOGOFF and CLOSE here ... since they
				   are implicitly done when session drops */
				switch (smb2_command) {
				/* special case next three in caller */
				/* BB Should we keep oplock break and
				   add flush to the four exceptions? */
				case SMB2_TREE_DISCONNECT:
				case SMB2_CANCEL:
				case SMB2_CLOSE:
				case SMB2_OPLOCK_BREAK:
					return -EAGAIN;
				}
				wait_event_interruptible_timeout(
					tcon->ses->server->response_q,
					(tcon->ses->server->tcpStatus ==
							CifsGood),
					10 * HZ);
				if (tcon->ses->server->tcpStatus ==
							CifsNeedReconnect) {
					/* on "soft" mounts we wait once */
					if (!tcon->retry ||
					   (tcon->ses->status == CifsExiting)) {
						cFYI(1, "gave up waiting on "
						      "reconnect in smb_init");
						return -EHOSTDOWN;
					} /* else "hard" mount - keep retrying
					     until process is killed or server
					     comes back on-line */
				} else /* TCP session is reestablished now */
					break;
			}

			nls_codepage = load_nls_default();
		/* need to prevent multiple threads trying to
		simultaneously reconnect the same SMB session */
			mutex_lock(&tcon->ses->session_mutex);
			if (tcon->ses->need_reconnect)
				rc = smb2_setup_session(0, tcon->ses,
							nls_codepage);


			if (smb2_command == SMB2_TREE_CONNECT) {
				mutex_unlock(&tcon->ses->session_mutex);
				goto get_buf;
			}

		/* we need to prevent multiple threads in this case too */
			if (!rc && (tcon->need_reconnect)) {
				mark_open_files_invalid(tcon);
				rc = SMB2_tcon(0, tcon->ses, tcon->treeName,
					      tcon, nls_codepage);
				/* BB FIXME add code to check if wsize needs
				   update due to negotiated smb buffer size
				   shrinking */
				if (rc == 0)
					atomic_inc(&tconInfoReconnectCount);

				cFYI(1, "reconnect tcon rc = %d", rc);
				/* Removed call to reopen open files here.
				   It is safer (and faster) to reopen files
				   one at a time as needed in read and write */

				/* Check if handle based operation so we
				   know whether we can continue or not without
				   returning to caller to reset file handle */
				/* BB Is flush done by server on drop
				   of tcp session? Should we special
				   case it and skip above? */
				switch (smb2_command) {
				case SMB2_FLUSH:
				case SMB2_READ:
				case SMB2_WRITE:
				case SMB2_LOCK:
				case SMB2_IOCTL:
				case SMB2_QUERY_DIRECTORY:
				case SMB2_CHANGE_NOTIFY:
				case SMB2_QUERY_INFO:
				case SMB2_SET_INFO: {
					mutex_unlock(&tcon->ses->session_mutex);
					unload_nls(nls_codepage);
					return -EAGAIN;
				}
				}
			}
			mutex_unlock(&tcon->ses->session_mutex);
			unload_nls(nls_codepage);

		} else {
			return -EIO;
		}
	}
	if (rc)
		return rc;

get_buf:
	/* BB eventually switch this to SMB2 specific small buf size */
	*request_buf = cifs_small_buf_get();
	if (*request_buf == NULL) {
		/* BB should we add a retry in here if not a writepage? */
		return -ENOMEM;
	}

	smb2_hdr_assemble((struct smb2_hdr *) *request_buf, smb2_command,
			tcon);

	if (tcon != NULL) {
		cifs_stats_inc(&tcon->num_smbs_sent);
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_sent[le16_to_cpu(smb2_command)]);
	}

	return rc;
}

int
small_smb2_init_no_tc(__le16 smb2_command, struct cifs_ses *ses,
		      void **request_buf)
{
	int rc;
	struct smb2_hdr *buffer;

	rc = small_smb2_init(smb2_command, NULL, request_buf);
	if (rc)
		return rc;

	buffer = (struct smb2_hdr *)*request_buf;

	/* BB Set SMB2 flags */

	/* uid, tid can stay at zero as set in header assemble */

	/* BB add support for turning on the signing when
	this function is used after 1st of session setup requests */

	return rc;
}

static int
validate_buf(unsigned int offset, unsigned int buffer_length,
	     struct smb2_hdr *hdr, unsigned int min_buf_size)

{
	unsigned int smb_len = be32_to_cpu(hdr->smb2_buf_length);
	char *end_of_smb = smb_len + 4 /* RFC1001 length field */ + (char *)hdr;
	char *begin_of_buf = 4 /* RFC1001 len field */ + offset + (char *)hdr;
	char *end_of_buf = begin_of_buf + buffer_length;


	if (buffer_length < min_buf_size) {
		cERROR(1, "buffer length %d smaller than minimum size %d",
			   buffer_length, min_buf_size);
		return -EINVAL;
	}

	/* check if beyond RFC1001 maximum length */
	if ((smb_len > 0x7FFFFF) || (buffer_length > 0x7FFFFF)) {
		cERROR(1, "buffer length %d or smb length %d too large",
			   buffer_length, smb_len);
		return -EINVAL;
	}

	if ((begin_of_buf > end_of_smb) || (end_of_buf > end_of_smb)) {
		cERROR(1, "illegal server response, bad offset to data");
		return -EINVAL;
	}

	return 0;
}

/*
 * If SMB buffer fields valid, copy into temporary buffer to hold result
 * Caller must free buffer
 */
static int
validate_and_copy_buf(unsigned int offset, unsigned int buffer_length,
		     struct smb2_hdr *hdr, unsigned int minbufsize, char *pdata)

{
	char *begin_of_buf = 4 /* RFC1001 len field */ + offset + (char *)hdr;
	int rc;

	if (!pdata)
		return -EINVAL;

	rc = validate_buf(offset, buffer_length, hdr, minbufsize);
	if (rc)
		return rc;

	memcpy(pdata, begin_of_buf, buffer_length);

	return 0;
}

static int
validate_and_copy_ea_buf(int ret_value,
			int output_buf_offset, int output_buf_len,
			struct smb2_hdr *hdr, int min_buf_size,
			char *pdata, int pdata_len, char *ea_name,
			const char *prefix, int prefix_len)
{
	int smb_len = be32_to_cpu(hdr->smb2_buf_length);
	char *end_of_smb = smb_len + 4 /* RFC1001 length field */ + (char *)hdr;
	char *begin_of_buf = 4 /* RFC1001 len field */
		+ output_buf_offset + (char *)hdr;
	char *end_of_buf = begin_of_buf + output_buf_len;
	char *curr_buf_pos = begin_of_buf;
	int next_ea_offset = 1, pdata_offset = 0, curr_buf_offset = 0,
		name_len, value_len, tot_written = 0;
	FILE_FULL_EA_INFO *curr_ea = (FILE_FULL_EA_INFO *)begin_of_buf;

	if (output_buf_len < min_buf_size) {
		cERROR(1, "buffer length %d smaller than minimum size %d",
			   output_buf_len, min_buf_size);
		return -EINVAL;
	}

	/* check if beyond RFC1001 maximum length */
	if ((smb_len > 0x7FFFFF) || (output_buf_len > 0x7FFFFF)) {
		cERROR(1, "buffer length %d or smb length %d too large",
			   output_buf_len, smb_len);
		return -EINVAL;
	}

	if (end_of_buf > end_of_smb) {
		cERROR(1, "illegal server response, bad offset to data");
		return -EINVAL;
	}

	while (curr_buf_pos < end_of_buf
		&& curr_buf_offset < output_buf_len
		&& tot_written <= pdata_len
		&& next_ea_offset != 0) {
		next_ea_offset = le32_to_cpu(curr_ea->NextEntryOffset);
		/*= curr_ea->Flags;*/
		name_len = curr_ea->EaNameLength;
		value_len = le16_to_cpu(curr_ea->EaValueLength);

		/* check there aren't too many eas */
		if (pdata_offset + name_len + 6 > pdata_len) {
			cERROR(1, "EA list excedes size of user buffer.");
			return -EINVAL;
		}

		if (ea_name != NULL) { /* Find single value user requested. */
			if (strlen(ea_name) == name_len
				&& ((!strncmp(curr_ea->EaName,
						prefix, prefix_len)
					&& strncmp(ea_name, curr_ea->EaName
						+ prefix_len, name_len
						- prefix_len) == 0)
				|| (strncmp(XATTR_USER_PREFIX, prefix,
						prefix_len) == 0
					&& strncmp(ea_name, curr_ea->EaName,
						name_len) == 0))) {

				memcpy(pdata, curr_ea->EaName + name_len + 1,
					value_len);
				memcpy(pdata+value_len, "\0", 1);
				tot_written += value_len;
				break;
			}
		} else { /* Form a list of all ea names */
			if (strncmp(curr_ea->EaName, XATTR_SECURITY_PREFIX,
					XATTR_SECURITY_PREFIX_LEN)
				&& strncmp(curr_ea->EaName, XATTR_OS2_PREFIX,
					XATTR_OS2_PREFIX_LEN)) {

				memcpy(pdata, XATTR_USER_PREFIX,
					XATTR_USER_PREFIX_LEN);
				memcpy(pdata+XATTR_USER_PREFIX_LEN,
					curr_ea->EaName, name_len);
				memcpy(pdata+XATTR_USER_PREFIX_LEN+name_len,
					"\0", 1);
				tot_written += name_len +
					XATTR_USER_PREFIX_LEN + 1;
				pdata += name_len + XATTR_USER_PREFIX_LEN + 1;
			} else {
				memcpy(pdata, curr_ea->EaName, name_len);
				memcpy(pdata+name_len, "\0", 1);
				tot_written += name_len + 1;
				pdata += name_len + 1;
			}
		}

		if (next_ea_offset == 0)
			break;
		curr_buf_offset += next_ea_offset;
		curr_buf_pos += next_ea_offset;
		curr_ea = (FILE_FULL_EA_INFO *)curr_buf_pos;
	}
	return tot_written;
}

static void free_rsp_buf(int resp_buftype, void *pSMB2r)
{
	if (resp_buftype == CIFS_SMALL_BUFFER)
		cifs_small_buf_release(pSMB2r);
	else if (resp_buftype == CIFS_LARGE_BUFFER)
		cifs_buf_release(pSMB2r);
}

#define SMB2_NUM_PROT 2

#define SMB2_PROT   0
#define SMB21_PROT  1
#define BAD_PROT 0xFFFF

static struct {
	int index;
	__le16 name;
} smb2protocols[] = {
	{SMB2_PROT,  cpu_to_le16(0x0202)},
	{SMB21_PROT, cpu_to_le16(0x0210)},
	{BAD_PROT,   cpu_to_le16(0xFFFF)}
};

/*
 *
 *	SMB2 Worker functions follow:
 *
 *	The general structure of the worker functions is:
 *	1) Call smb2_init (assembles SMB2 header)
 *	2) Initialize SMB2 command specific fields in fixed length area of SMB
 *	3) Call smb_sendrcv2 (sends request on socket and waits for response)
 *	4) Decode SMB2 command specific fields in the fixed length area
 *	5) Decode variable length data area (if any for this SMB2 command type)
 *	6) Call free smb buffer
 *	7) return
 *
 */

int
SMB2_negotiate(unsigned int xid, struct cifs_ses *ses)
{
	struct smb2_negotiate_req *pSMB2;
	struct smb2_negotiate_rsp *pSMB2r;
	struct kvec iov[1];
	int rc = 0;
	int status;
	int resp_buftype;
	struct TCP_Server_Info *server;
	unsigned int sec_flags;
	u16 i;
	u16 temp = 0;
	int blob_offset, blob_length;
	char *security_blob;

	cFYI(1, "Negotiate protocol");

	if (ses->server)
		server = ses->server;
	else {
		rc = -EIO;
		return rc;
	}

	rc = small_smb2_init(SMB2_NEGOTIATE, NULL, (void **) &pSMB2);
	if (rc)
		return rc;

	/* if any of auth flags (ie not sign or seal) are overriden use them */
	if (ses->overrideSecFlg & (~(CIFSSEC_MUST_SIGN | CIFSSEC_MUST_SEAL)))
		sec_flags = ses->overrideSecFlg;  /* BB FIXME fix sign flags?*/
	else /* if override flags set only sign/seal OR them with global auth */
		sec_flags = global_secflags | ses->overrideSecFlg;

	cFYI(1, "sec_flags 0x%x", sec_flags);

	pSMB2->hdr.SessionId = 0;

	for (i = 0; i < SMB2_NUM_PROT; i++)
		pSMB2->Dialects[i] = smb2protocols[i].name;

	pSMB2->DialectCount = cpu_to_le16(i);
	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length) + (i * 2));

	/* only one of SMB2 signing flags may be set in SMB2 request */
	if ((sec_flags & CIFSSEC_MUST_SIGN) == CIFSSEC_MUST_SIGN)
		temp = SMB2_NEGOTIATE_SIGNING_REQUIRED;
	else if (sec_flags & CIFSSEC_MAY_SIGN) /* MAY_SIGN is a single flag */
		temp = SMB2_NEGOTIATE_SIGNING_ENABLED;

	pSMB2->SecurityMode = cpu_to_le16(temp);

	pSMB2->Capabilities = cpu_to_le32(SMB2_GLOBAL_CAP_DFS);

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4;

	rc = smb2_sendrcv2(xid, ses, iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);

	cFYI(1, "negotiate returned buftype %d with rc %d status 0x%x",
		 resp_buftype, rc, status);
	pSMB2r = (struct smb2_negotiate_rsp *)iov[0].iov_base;
	/* no tcon so can't do cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2...]); */
	if (rc != 0)
		goto neg_exit;

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto neg_exit;
	}

	cFYI(1, "mode 0x%x", pSMB2r->SecurityMode);

	if (pSMB2r->DialectRevision == smb2protocols[SMB21_PROT].name)
		cFYI(1, "negotiated smb2.1 dialect");
	else if (pSMB2r->DialectRevision == smb2protocols[SMB2_PROT].name)
		cFYI(1, "negotiated smb2 dialect");
	else {
		cERROR(1, "Illegal dialect returned by server %d",
			   le16_to_cpu(pSMB2r->DialectRevision));
		rc = -EIO;
		goto neg_exit;
	}
	ses->server->smb2_dialect_revision = pSMB2r->DialectRevision;

	ses->server->max_read = le32_to_cpu(pSMB2r->MaxReadSize);
	ses->server->max_write = le32_to_cpu(pSMB2r->MaxWriteSize);
	/* BB Do we need to validate the SecurityMode? */
	ses->server->sec_mode = le16_to_cpu(pSMB2r->SecurityMode);
	ses->server->capabilities = le32_to_cpu(pSMB2r->Capabilities);

	security_blob = smb2_get_data_area_len(&blob_offset, &blob_length,
						&pSMB2r->hdr);
	if (blob_length == 0) {
		cERROR(1, "missing security blob on negprot");
		rc = -EIO;
		goto neg_exit;
	}
#ifdef CONFIG_SMB2_ASN1  /* BB REMOVEME when updated asn1.c ready */
	rc = decode_neg_token_init(security_blob, blob_length,
				   &ses->server->sec_type);
	if (rc == 1)
		rc = 0;
	else if (rc == 0) {
		rc = -EIO;
		goto neg_exit;
	}
#endif

neg_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

int
SMB2_sess_setup(unsigned int xid, struct cifs_ses *ses,
		const struct nls_table *nls_cp)
{
	struct sess_setup_req *pSMB2;
	struct sess_setup_rsp *pSMB2r = NULL;
	struct kvec iov[2];
	int rc = 0;
	int status;
	int resp_buftype;
	__le32 phase = NtLmNegotiate; /* NTLMSSP, if needed, is multistage */
	struct TCP_Server_Info *server;
	unsigned int sec_flags;
	u8 temp = 0;
	u16 blob_length = 0;
	char *security_blob;
	char *ntlmssp_blob = NULL;
	bool use_spnego = false; /* else use raw ntlmssp */

	cFYI(1, "Session Setup");

	if (ses->server)
		server = ses->server;
	else {
		rc = -EIO;
		return rc;
	}

ssetup_ntlmssp_authenticate:
	if (phase == NtLmChallenge)
		phase = NtLmAuthenticate; /* if ntlmssp, now final phase */

	rc = small_smb2_init(SMB2_SESSION_SETUP, NULL, (void **) &pSMB2);
	if (rc)
		return rc;

	/* if any of auth flags (ie not sign or seal) are overriden use them */
	if (ses->overrideSecFlg & (~(CIFSSEC_MUST_SIGN | CIFSSEC_MUST_SEAL)))
		sec_flags = ses->overrideSecFlg;  /* BB FIXME fix sign flags?*/
	else /* if override flags set only sign/seal OR them with global auth */
		sec_flags = global_secflags | ses->overrideSecFlg;

	cFYI(1, "sec_flags 0x%x", sec_flags);

	pSMB2->hdr.SessionId = 0; /* First session, not a reauthenticate */
	pSMB2->VcNumber = 0; /* MBZ */

	/* only one of SMB2 signing flags may be set in SMB2 request */
	if ((sec_flags & CIFSSEC_MUST_SIGN) == CIFSSEC_MUST_SIGN)
		temp = SMB2_NEGOTIATE_SIGNING_REQUIRED;
	else if (ses->server->sec_mode & SMB2_NEGOTIATE_SIGNING_REQUIRED)
		temp = SMB2_NEGOTIATE_SIGNING_REQUIRED;
	else if (sec_flags & CIFSSEC_MAY_SIGN) /* MAY_SIGN is a single flag */
		temp = SMB2_NEGOTIATE_SIGNING_ENABLED;

	pSMB2->SecurityMode = temp;

	/* We only support the DFS cap (others are currently undefined) */
	pSMB2->Capabilities = cpu_to_le32(SMB2_GLOBAL_CAP_DFS
						& ses->server->capabilities);
	pSMB2->Channel = 0; /* MBZ */
	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length)
					+ 4 /* rfc1001 len */ - 1 /* pad */;
	if (phase == NtLmNegotiate) {
		ntlmssp_blob = kmalloc(sizeof(struct _NEGOTIATE_MESSAGE),
					GFP_KERNEL);
		if (ntlmssp_blob == NULL) {
			rc = -ENOMEM;
			goto ssetup_exit;
		}

		build_ntlmssp_negotiate_blob(ntlmssp_blob, ses);
		if (use_spnego) {
/*			blob_length = build_spnego_ntlmssp_blob(&security_blob,
					sizeof(struct _NEGOTIATE_MESSAGE),
					ntlmssp_blob); */
			/* BB eventually need to add this */
			cERROR(1, "spnego not supported for SMB2 yet");
			rc = -EOPNOTSUPP;
			kfree(ntlmssp_blob);
			goto ssetup_exit;
		} else {
			blob_length = sizeof(struct _NEGOTIATE_MESSAGE);
			/* with raw NTLMSSP we don't encapsulate in SPNEGO */
			security_blob = ntlmssp_blob;
		}
	} else if (phase == NtLmAuthenticate) {
		pSMB2->hdr.SessionId = ses->Suid;
		ntlmssp_blob = kzalloc(sizeof(struct _NEGOTIATE_MESSAGE) + 500,
					GFP_KERNEL);
		if (ntlmssp_blob == NULL) {
			cERROR(1, "failed to malloc ntlmssp blob");
			rc = -ENOMEM;
			goto ssetup_exit;
		}
		rc = build_ntlmssp_auth_blob(ntlmssp_blob, &blob_length,
					ses, nls_cp);
		if (rc) {
			cFYI(1, "build_ntlmssp_auth_blob failed %d", rc);
			goto ssetup_exit; /* BB double check error handling */
		}
		if (use_spnego) {
/*			blob_length = build_spnego_ntlmssp_blob(&security_blob,
								blob_length,
								ntlmssp_blob);*/
			cERROR(1, "spnego not supported for SMB2 yet");
			rc = -EOPNOTSUPP;
			kfree(ntlmssp_blob);
			goto ssetup_exit;
		} else {
			security_blob = ntlmssp_blob;
		}
	} else {
		cERROR(1, "illegal ntlmssp phase");
		rc = -EIO;
		goto ssetup_exit;
	}

	/* Testing shows that buffer offset must be at location of Buffer[0] */
	pSMB2->SecurityBufferOffset = cpu_to_le16(sizeof(struct sess_setup_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->SecurityBufferLength = cpu_to_le16(blob_length);
	iov[1].iov_base = security_blob;
	iov[1].iov_len = blob_length;

	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length)
			    - 1 /* pad */ + blob_length);

	/* BB add code to build os and lm fields */

	rc = smb2_sendrcv2(xid, ses, iov, 2, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	kfree(security_blob);
	cFYI(1, "sess setup returned buftype %d with rc %d status 0x%x",
		 resp_buftype, rc, status);
	pSMB2r = (struct sess_setup_rsp *)iov[0].iov_base;
	if (pSMB2r->hdr.Status ==
			cpu_to_le32(STATUS_MORE_PROCESSING_REQUIRED)) {
		if (phase != NtLmNegotiate) {
			cERROR(1, "Unexpected more processing error");
			goto ssetup_exit;
		}
		if (offsetof(struct sess_setup_rsp, Buffer) - 4 /* RFC hdr */ !=
			le16_to_cpu(pSMB2r->SecurityBufferOffset)) {
			cERROR(1, "Invalid security buffer offset %d",
				    le16_to_cpu(pSMB2r->SecurityBufferOffset));
			rc = -EIO;
			goto ssetup_exit;
		}

		/* NTLMSSP Negotiate sent now processing challenge (response) */
		phase = NtLmChallenge; /* process ntlmssp challenge */
		rc = 0; /* MORE_PROCESSING is not an error here but expected */
		ses->Suid = pSMB2r->hdr.SessionId;
		rc = decode_ntlmssp_challenge(pSMB2r->Buffer,
				le16_to_cpu(pSMB2r->SecurityBufferLength), ses);
	}

	/* BB eventually add code for SPNEGO decoding of NtlmChallenge blob,
	   but at least the raw NTLMSSP case works */

	/* no tcon so can't do cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2...]); */
	if (rc != 0)
		goto ssetup_exit;

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto ssetup_exit;
	}

	ses->session_flags = le16_to_cpu(pSMB2r->SessionFlags);
ssetup_exit:
	kfree(ntlmssp_blob);
	ntlmssp_blob = NULL;
	free_rsp_buf(resp_buftype, pSMB2r);

	/* if ntlmssp, and negotiate succeeded, proceed to authenticate phase */
	if ((phase == NtLmChallenge) && (rc == 0))
		goto ssetup_ntlmssp_authenticate;
	return rc;
}

int
SMB2_tcon(unsigned int xid, struct cifs_ses *ses,
	 const char *tree, struct cifs_tcon *tcon,
	 const struct nls_table *cp)
{
	struct tree_connect_req *pSMB2;
	struct tree_connect_rsp *pSMB2r = NULL;
	struct kvec iov[2];
	int rc = 0;
	int resp_buftype;
	int unc_path_len;
	int status;
	struct TCP_Server_Info *server;
	__le16 *unc_path = NULL;

	cFYI(1, "TCON");

	if ((ses->server) && tree)
		server = ses->server;
	else
		return -EIO;

	if (tcon && tcon->bad_network_name)
		return -ENOENT;

	unc_path = smb2_strndup_to_ucs(tree, MAX_NAME /* BB find better */,
				       &unc_path_len, cp);
	if (unc_path == NULL)
		return -ENOMEM;

	if (unc_path_len < 2) {
		kfree(unc_path);
		return -EINVAL;
	}

	rc = small_smb2_init(SMB2_TREE_CONNECT, tcon, (void **) &pSMB2);
	if (rc) {
		kfree(unc_path);
		return rc;
	}

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length)
					+ 4 /* rfc1001 len */ - 1 /* pad */;

	/* Testing shows that buffer offset must be at location of Buffer[0] */
	pSMB2->PathOffset = cpu_to_le16(sizeof(struct tree_connect_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->PathLength = cpu_to_le16(unc_path_len - 2);
	iov[1].iov_base = unc_path;
	iov[1].iov_len = unc_path_len;

	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length)
			    - 1 /* pad */ + unc_path_len);

	rc = smb2_sendrcv2(xid, ses, iov, 2, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "tcon buftype %d rc %d status %d", resp_buftype, rc, status);
	pSMB2r = (struct tree_connect_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2TREE_CONNECT]);
		tcon->need_reconnect = true;
		goto tcon_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto tcon_exit;
	}

	if (pSMB2r->ShareType & SMB2_SHARE_TYPE_DISK)
		cFYI(1, "connection to disk share");
	else if (pSMB2r->ShareType & SMB2_SHARE_TYPE_PIPE) {
		tcon->ipc = true;
		cFYI(1, "connection to pipe share");
	} else if (pSMB2r->ShareType & SMB2_SHARE_TYPE_PRINT) {
		tcon->print = true;
		cFYI(1, "connection to printer");
	} else {
		cERROR(1, "unknown share type %d", pSMB2r->ShareType);
		rc = -EOPNOTSUPP;
		goto tcon_exit;
	}

	tcon->share_flags = le32_to_cpu(pSMB2r->ShareFlags);
	tcon->tidStatus = CifsGood;
	tcon->need_reconnect = false;
	tcon->tid = pSMB2r->hdr.TreeId;
	if ((pSMB2r->Capabilities & SMB2_SHARE_CAP_DFS) &&
	    ((tcon->share_flags & SHI1005_FLAGS_DFS) == 0))
		cERROR(1, "DFS capability contradicts DFS flag");

	tcon->maximal_access = le32_to_cpu(pSMB2r->MaximalAccess);

	strncpy(tcon->treeName, tree, MAX_TREE_SIZE);
tcon_exit:
	if (pSMB2r->hdr.Status == cpu_to_le32(STATUS_BAD_NETWORK_NAME)) {
		cERROR(1, "BAD_NETWORK_NAME: %s", tree);
		tcon->bad_network_name = true;
	}
	free_rsp_buf(resp_buftype, pSMB2r);
	kfree(unc_path);

	return rc;
}

int
SMB2_logoff(const int xid, struct cifs_ses *ses)
{
	struct logoff_req *pSMB2; /* response is also trivial struct */
	int rc = 0;
	struct TCP_Server_Info *server;

	cFYI(1, "disconnect session %p", ses);

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_LOGOFF, NULL, (void **) &pSMB2);
	if (rc)
		return rc;

	 /* since no tcon, smb2_init can not do this, so do here */
	pSMB2->hdr.SessionId = ses->Suid;

	rc = smb2_sendrcv_norsp(xid, ses, &pSMB2->hdr,
				CIFS_STD_OP | CIFS_LOG_ERROR);
	/* no tcon so can't do cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2...]); */
	return rc;
}

int SMB2_tdis(const int xid, struct cifs_tcon *tcon)
{
	struct tree_disconnect_req *pSMB2; /* response is also trivial struct */
	int rc = 0;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;

	cFYI(1, "Tree Disconnect");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	if ((tcon->need_reconnect) || (tcon->ses->need_reconnect))
		return 0;

	rc = small_smb2_init(SMB2_TREE_DISCONNECT, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	rc = smb2_sendrcv_norsp(xid, ses, &pSMB2->hdr,
				CIFS_STD_OP | CIFS_LOG_ERROR);
	if (rc)
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2TREE_DISCONNECT]);

	return rc;
}

int SMB2_open(const int xid, struct cifs_tcon *tcon, __le16 *path,
	      u64 *persistent_fid, u64 *volatile_fid, __le32 desired_access,
	      __le32 create_disposition, __le32 file_attributes,
	      __le32 create_options)
{
	struct create_req *pSMB2;
	struct create_rsp *pSMB2r;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;
	struct kvec iov[2];
	int resp_buftype;
	int status;
	int uni_path_len;
	int rc = 0;
	int num_iovecs = 2;

	cFYI(1, "create/open");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_CREATE, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	if (oplockEnabled)
		pSMB2->RequestedOplockLevel = SMB2_OPLOCK_LEVEL_BATCH;
	else
		pSMB2->RequestedOplockLevel = SMB2_OPLOCK_LEVEL_NONE;
	pSMB2->ImpersonationLevel = IL_IMPERSONATION;
	pSMB2->DesiredAccess = desired_access;
	pSMB2->FileAttributes = file_attributes; /* ignored on open */
	pSMB2->ShareAccess = FILE_SHARE_ALL_LE;
	pSMB2->CreateDisposition = create_disposition;
	pSMB2->CreateOptions = create_options;
	uni_path_len = (2 * UniStrnlen((wchar_t *)path, PATH_MAX)) + 2;
	pSMB2->NameOffset = cpu_to_le16(sizeof(struct create_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);

	iov[0].iov_base = (char *)pSMB2;

	/*  rfc1001 length field is 4 bytes so added below */
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4;

	 /* MUST set path len (NameLength) to 0 opening root of share */
	if (uni_path_len >= 4) {
		pSMB2->NameLength = cpu_to_le16(uni_path_len - 2);
		/* -1 since last byte is buf[0] which is sent below (path) */
		iov[0].iov_len--;
		iov[1].iov_len = uni_path_len;
		iov[1].iov_base = path;
	 /* -1 since last byte is buf[0] which was counted in smb2_buf_len */
		pSMB2->hdr.smb2_buf_length = cpu_to_be32(be32_to_cpu(
				pSMB2->hdr.smb2_buf_length) + uni_path_len - 1);
	} else {
		num_iovecs = 1;
		pSMB2->NameLength = 0;
	}

/*	cERROR(1, "unipathlen 0x%x iov0len 0x%x iov1len 0x%x", uni_path_len,
		iov[0].iov_len, iov[1].iov_len); */ /* BB REMOVEME BB */
	rc = smb2_sendrcv2(xid, ses, iov, num_iovecs, &resp_buftype /* ret */,
			   &status, CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "creat buftype %d rc %d status %d", resp_buftype, rc, status);
	pSMB2r = (struct create_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2CREATE]);
		goto creat_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto creat_exit;
	}
	*persistent_fid = pSMB2r->PersistentFileId;
	*volatile_fid = pSMB2r->VolatileFileId;
creat_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

int SMB2_close(const int xid, struct cifs_tcon *tcon,
		u64 persistent_file_id, u64 volatile_file_id)
{
	struct close_req *pSMB2;
	struct close_rsp *pSMB2r;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;
	struct kvec iov[1];
	int resp_buftype;
	int status;
	int rc = 0;

	cFYI(1, "Close");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_CLOSE, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->PersistentFileId = persistent_file_id;
	pSMB2->VolatileFileId = volatile_file_id;

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length)
					+ 4 /* rfc1001 len */;

	rc = smb2_sendrcv2(xid, ses, iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "CLOSE buftype %d rc %d status %d", resp_buftype, rc, status);
	pSMB2r = (struct close_rsp *)iov[0].iov_base;

	if (rc != 0) {
		if (tcon)
			cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2CLOSE]);
		goto close_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto close_exit;
	}

	/* BB FIXME - decode close response, update inode for caching */

close_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

int SMB2_flush(const int xid, struct cifs_tcon *tcon,
		u64 persistent_file_id, u64 volatile_file_id)
{
	struct flush_req *pSMB2;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;
	struct kvec iov[1];
	int resp_buftype;
	int status;
	int rc = 0;

	cFYI(1, "Flush");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_FLUSH, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->PersistentFileId = persistent_file_id;
	pSMB2->VolatileFileId = volatile_file_id;

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length)
					+ 4 /* rfc1001 len */;

	rc = smb2_sendrcv2(xid, ses, iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "FLUSH rc %d status %d", rc, status);

	if ((rc != 0) && tcon)
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2FLUSH]);

	free_rsp_buf(resp_buftype, iov[0].iov_base);
	return rc;
}


/* Although the tcon value is not needed to send the echo, the
   echo is useful when problems with slow operations show up
   on a tcon, and also after a mount to recognize very slow links
   so it is useful to associate the results of echo with a tcon
   and pass in a tcon to this function */
int SMB2_echo(const int xid, struct cifs_tcon *tcon)
{
	struct echo_req *pSMB2;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;
	struct kvec iov[1];
	int resp_buftype;
	int status;
	int rc = 0;
	unsigned long when_sent;

	cFYI(1, "Echo");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_ECHO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length)
					+ 4 /* rfc1001 len */;

	when_sent = jiffies;
	rc = smb2_sendrcv2(xid, ses, iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);

	/* 15 jiffies is about 60 milliseconds - and plenty of time for network
	   request to reach server and be processed but if it takes 1000 jiffies
	   (about 4 seconds) then network or server is sick. 15 seconds and it
	   would have timed out and returned an error */
	if (time_before(jiffies, when_sent + 3))
		tcon->ses->server->speed = SMB2_ECHO_FAST;
	else if (time_before(jiffies, when_sent + 15))
		tcon->ses->server->speed = SMB2_ECHO_OK;
	else if (time_before(jiffies, when_sent + 125)) {
		tcon->ses->server->speed = SMB2_ECHO_SLOW;
		cERROR(1, "slow network, SMB2 echo took %lu jiffies",
			when_sent - jiffies);
	} else if (time_before(jiffies, when_sent + 1000)) {
		tcon->ses->server->speed = SMB2_ECHO_VERY_SLOW;
		cERROR(1, "bad network? SMB2 echo took %lu jiffies",
			when_sent - jiffies);
	} else {
		tcon->ses->server->speed = SMB2_ECHO_TIMEOUT;
		cERROR(1, "server may be down - echo took %lu jiffies",
			when_sent - jiffies);
	}

	cFYI(1, "ECHO speed %d rc %d status %d", tcon->ses->server->speed, rc, status);

	if (rc != 0)
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2ECHO]);

	free_rsp_buf(resp_buftype, iov[0].iov_base);
	return rc;
}

static unsigned
int is_symlink_relative(const char *symname)
{
	if ((strstr(symname, "./")) || (strstr(symname, "../")))
		return 1;
	else
		return 0;
}

static int
build_symlink_inputbuf(struct symlink_reparse_data_buf *inpbuf,
		const char *symname, __le16 *pathbuf, unsigned int *pathbuflen)
{
	int uni_sym_len;
	__le16 *nameptr = pathbuf;

	uni_sym_len = cifs_strtoUCS(nameptr, symname,
			strlen(symname), load_nls_default());
	nameptr += uni_sym_len;
	cifs_strtoUCS(nameptr, symname, strlen(symname), load_nls_default());

	*pathbuflen = 4 * uni_sym_len;
	inpbuf->reparse_tag = cpu_to_le32(MS_REPARSE_TAG);
	inpbuf->reparse_datalength = cpu_to_le16(*pathbuflen + 12);
	inpbuf->reserved1 = 0x0;
	inpbuf->sub_nameoffset = 0x0;
	inpbuf->sub_namelength = cpu_to_le16(2 * uni_sym_len);
	inpbuf->print_nameoffset = cpu_to_le16(2 * uni_sym_len);
	inpbuf->print_namelength = cpu_to_le16(2 * uni_sym_len);
	if (is_symlink_relative(symname))
		inpbuf->flags = cpu_to_le32(SYMLINK_FLAG_RELATIVE);
	else
		inpbuf->flags = 0x0;

	return 0;
}

int
SMB2_symlink_ioctl(const int xid, struct cifs_tcon *tcon, u32 ctlcode,
	      u64 persistent_fid, u64 volatile_fid, const char *symname)
{
	struct ioctl_req *pSMB2;
	struct ioctl_rsp *pSMB2r = NULL;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;
	struct kvec iov[3];
	int resp_buftype;
	int status;
	int rc = 0;
	int num_iovecs = 3;
	unsigned int symbuflen = 0;
	unsigned int pathbuflen = 0;
	__le16 *pathbuf;
	struct symlink_reparse_data_buf symlinkbuf;

	cFYI(1, "SMB2_symlink_ioctl");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_IOCTL, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	/* allocate large enough buffer to hold unichar symname, twice */
	pathbuf = kmalloc(2 * 4 * strlen(symname), GFP_KERNEL);
	if (pathbuf == NULL) {
		rc = -ENOMEM;
		goto ioctl_exit;
	}

	pSMB2->Ctlcode = cpu_to_le32(ctlcode);
	pSMB2->Fileid[0] = persistent_fid;
	pSMB2->Fileid[1] = volatile_fid;

	symlinkbuf.reparse_datalength = 0x0;
	rc = build_symlink_inputbuf(&symlinkbuf, symname,
			pathbuf, &pathbuflen);
	if (rc) {
		cERROR(1, "Error %d buidling symlink ioctl input buffer", rc);
		goto ioctl_exit;
	}
	symbuflen = sizeof(struct symlink_reparse_data_buf) - 1;

	pSMB2->Inputoffset = cpu_to_le32(sizeof(struct ioctl_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->Inputcount = cpu_to_le32(symbuflen + pathbuflen);
	pSMB2->Maxinputresp = 0;

	pSMB2->Outputoffset = cpu_to_le32(sizeof(struct ioctl_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->Outputcount = 0;
	pSMB2->Maxoutputresp = 0;

	pSMB2->Flags = cpu_to_le32(SMB2_IOCTL_IS_FSCTL);

	iov[0].iov_base = (char *)pSMB2;
	/*  added 4 bytes of rfc1001 length field and subtracted 1 for buffer */
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;

	iov[1].iov_base = &symlinkbuf;
	iov[1].iov_len = symbuflen;

	iov[2].iov_base = pathbuf;
	iov[2].iov_len = pathbuflen;

	pSMB2->hdr.smb2_buf_length = cpu_to_be32(be32_to_cpu(
		pSMB2->hdr.smb2_buf_length) + symbuflen + pathbuflen - 1);

	rc = smb2_sendrcv2(xid, ses, iov, num_iovecs, &resp_buftype /* ret */,
			   &status, CIFS_STD_OP | CIFS_LOG_ERROR);

	pSMB2r = (struct ioctl_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2IOCTL]);
		goto ioctl_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto ioctl_exit;
	}

ioctl_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	kfree(pathbuf);
	return rc;
}

static unsigned int
num_entries(char *bufstart, char *end_of_buf, char **lastentry)
{
	int len;
	unsigned int entrycount = 0;
	unsigned int next_offset = 0;
	struct file_full_directory_info *entryptr;

	if (bufstart == NULL)
		return 0;

	entryptr = (struct file_full_directory_info *)bufstart;

	while (1) {
		entryptr = (struct file_full_directory_info *)
					((char *)entryptr + next_offset);

		if ((char *)entryptr + sizeof(struct file_full_directory_info) >
		    end_of_buf) {
			cERROR(1, "malformed search entry would overflow");
			break;
		}

		len = le32_to_cpu(entryptr->filename_length);
		if ((char *)entryptr + sizeof(struct file_full_directory_info) +
		     len > end_of_buf) {
			cERROR(1, "directory entry name would overflow frame"
				" end of buf %p", end_of_buf);
			break;
		}

		*lastentry = (char *)entryptr;

		entrycount += 1;

		next_offset =  le32_to_cpu(entryptr->next_entry_offset);
		if (!next_offset)
			break;
	}

	return entrycount;
}

/*
 * Readdir/FindFirst
 *
 */
int SMB2_query_directory(const int xid, struct cifs_tcon *tcon,
		u64 persistent_fid, u64 volatile_fid, int index,
		struct smb2_search *psrch_inf)
{
	struct query_directory_req *pSMB2;
	struct query_directory_rsp *pSMB2r = NULL;
	struct kvec iov[2];
	int rc = 0;
	int len;
	int resp_buftype;
	int status;
	unsigned char *bufptr;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;
	__le16 asteriks = cpu_to_le16('*');
	char *end_of_smb;


	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_QUERY_DIRECTORY, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->FileInformationClass = FILEID_FULL_DIRECTORY_INFORMATION;

	pSMB2->FileIndex = cpu_to_le32(index);
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;

	len = 0x2;
	bufptr = pSMB2->Buffer;
	memcpy(bufptr, &asteriks, len);

	pSMB2->FileNameOffset =
		cpu_to_le16(sizeof(struct query_directory_req) - 1 - 4);
	pSMB2->FileNameLength = cpu_to_le16(len);
	/*  BB could be 30 bytes or so longer if we used SMB2 specific
	    buffer lengths, but this is safe and close enough */
	pSMB2->OutputBufferLength = cpu_to_le32(CIFSMaxBufSize -
		sizeof(struct query_directory_rsp));

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;

	iov[1].iov_base = (char *)(pSMB2->Buffer);
	iov[1].iov_len = len;

	pSMB2->hdr.smb2_buf_length = cpu_to_be32(be32_to_cpu(
			pSMB2->hdr.smb2_buf_length) + len - 1);

	rc = smb2_sendrcv2(xid, ses, iov, 2, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "rddir buftype %d rc %d status %d", resp_buftype, rc, status);
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2QUERY_DIRECTORY]);
		goto qdir_exit;
	}
	pSMB2r = (struct query_directory_rsp *)iov[0].iov_base;

	rc = validate_buf(le16_to_cpu(pSMB2r->OutputBufferOffset),
			le32_to_cpu(pSMB2r->OutputBufferLength), &pSMB2r->hdr,
			sizeof(struct file_full_directory_info));
	if (rc)
		goto qdir_exit;

	psrch_inf->ntwrk_buf_start = (char *)pSMB2r;
	psrch_inf->srch_entries_start = psrch_inf->last_entry = 4 /* RFCLEN */ +
		(char *)&pSMB2r->hdr +	le16_to_cpu(pSMB2r->OutputBufferOffset);
	end_of_smb = be32_to_cpu(pSMB2r->hdr.smb2_buf_length) +
				4 /* RFC1001len field */ + (char *)&pSMB2r->hdr;
	psrch_inf->entries_in_buf = num_entries(psrch_inf->srch_entries_start,
						end_of_smb,
						&psrch_inf->last_entry);
	psrch_inf->index_of_last_entry += psrch_inf->entries_in_buf;
	cFYI(1, "num entries %d last_index %lld srch start %p srch end %p",
		psrch_inf->entries_in_buf, psrch_inf->index_of_last_entry,
		psrch_inf->srch_entries_start, psrch_inf->last_entry);
	if (resp_buftype == CIFS_LARGE_BUFFER)
		psrch_inf->small_buf = false;
	else if (resp_buftype == CIFS_SMALL_BUFFER)
		psrch_inf->small_buf = true;
	else
		cERROR(1, "illegal search buffer type");

	if (le32_to_cpu(pSMB2r->hdr.Status) == STATUS_NO_MORE_FILES)
		psrch_inf->search_end = 1;
	else
		psrch_inf->search_end = 0;

	return rc;

qdir_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

static void copy_fs_info_to_kstatfs(struct fs_full_size_info *pfs_inf,
			     struct kstatfs *pkstat)
{
	pkstat->f_bsize = le32_to_cpu(pfs_inf->BytesPerSector) *
			  le32_to_cpu(pfs_inf->SectorsPerAllocationUnit);
	pkstat->f_blocks = le64_to_cpu(pfs_inf->TotalAllocationUnits);
	pkstat->f_bfree  = le64_to_cpu(pfs_inf->ActualAvailableAllocationUnits);
	pkstat->f_bavail = le64_to_cpu(pfs_inf->CallerAvailableAllocationUnits);

/*	__kernel_fsid_t f_fsid; */ /* get volume uuid from other level (once) */
/*	long f_frsize;    what are these?
	long f_spare[5]; */
	return;
}

static int build_qfs_info_req(struct kvec *iov, struct cifs_tcon *tcon,
			      int level, int outbuf_len,
			      u64 persistent_fid, u64 volatile_fid)
{
	int rc;
	struct query_info_req *pSMB2;

	cFYI(1, "Query FSInfo level %d", level);

	if ((tcon->ses == NULL) || (tcon->ses->server == NULL))
		return -EIO;

	rc = small_smb2_init(SMB2_QUERY_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType = SMB2_O_INFO_FILESYSTEM;
	pSMB2->FileInfoClass = level;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->InputBufferOffset = cpu_to_le16(sizeof(struct query_info_req)
			- 1 /* pad */ - 4 /* do not count RFC1001 len field */);
	pSMB2->OutputBufferLength =
		cpu_to_le32(outbuf_len + sizeof(struct query_info_rsp) - 1 - 4);

	iov->iov_base = (char *)pSMB2;
	iov->iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4;
	return 0;
}

int SMB2_QFS_info(const int xid, struct cifs_tcon *tcon,
		  u64 persistent_fid, u64 volatile_fid, struct kstatfs *fsdat)
{
	struct query_info_rsp *pSMB2r = NULL;
	struct kvec iov;
	int rc = 0;
	int resp_buftype;
	int status;
	struct cifs_ses *ses = tcon->ses;
	struct fs_full_size_info *psize_inf = NULL;

	rc = build_qfs_info_req(&iov, tcon, FS_FULL_SIZE_INFORMATION,
				sizeof(struct fs_full_size_info),
				persistent_fid, volatile_fid);
	if (rc)
		return rc;

	rc = smb2_sendrcv2(xid, ses, &iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "qfsinfo buftype %d rc %d status %d", resp_buftype, rc, status);
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2QUERY_INFO]);
		goto qinf_exit;
	}
	pSMB2r = (struct query_info_rsp *)iov.iov_base;

	psize_inf = (struct fs_full_size_info *)(4 /* RFC1001 len field */ +
		le16_to_cpu(pSMB2r->OutputBufferOffset) + (char *)&pSMB2r->hdr);
	rc = validate_buf(le16_to_cpu(pSMB2r->OutputBufferOffset),
				le32_to_cpu(pSMB2r->OutputBufferLength),
				&pSMB2r->hdr, sizeof(struct fs_full_size_info));
	if (!rc)
		copy_fs_info_to_kstatfs(psize_inf, fsdat);

qinf_exit:
	free_rsp_buf(resp_buftype, iov.iov_base);
	return rc;
}

#define MAX_NTFS_VOL_LABEL_LEN 32 /* We don't use this, but allow for its len */

int SMB2_QFS_vol_info(const int xid, struct cifs_tcon *tcon, u64 persistent_fid,
		 u64 volatile_fid)
{
	struct query_info_rsp *pSMB2r = NULL;
	struct kvec iov;
	int rc = 0;
	int resp_buftype;
	int status;
	struct cifs_ses *ses = tcon->ses;
	struct fs_volume_info *pvol_inf = NULL;

	rc = build_qfs_info_req(&iov, tcon, FS_VOLUME_INFORMATION,
				sizeof(struct fs_volume_info)
				+ (2 * MAX_NTFS_VOL_LABEL_LEN),
				persistent_fid, volatile_fid);
	if (rc)
		return rc;

	rc = smb2_sendrcv2(xid, ses, &iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);

	cFYI(1, "volinfo buftype %d rc %d status %d", resp_buftype, rc, status);
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2QUERY_INFO]);
		goto qvolinf_exit;
	}
	pSMB2r = (struct query_info_rsp *)iov.iov_base;

	pvol_inf = (struct fs_volume_info *)(4 /* RFC1001 len field */ +
		le16_to_cpu(pSMB2r->OutputBufferOffset) + (char *)&pSMB2r->hdr);
	rc = validate_buf(le16_to_cpu(pSMB2r->OutputBufferOffset),
				le32_to_cpu(pSMB2r->OutputBufferLength),
				&pSMB2r->hdr, sizeof(struct fs_volume_info));
	if (rc)
		goto qvolinf_exit;

	tcon->vol_serial_number = le32_to_cpu(pvol_inf->VolumeSerialNumber);
	tcon->vol_create_time = pvol_inf->VolumeCreationTime;
qvolinf_exit:
	free_rsp_buf(resp_buftype, iov.iov_base);
	return rc;
}

int SMB2_QFS_attribute_info(const int xid, struct cifs_tcon *tcon,
			    u64 persistent_fid, u64 volatile_fid)
{
	struct query_info_rsp *pSMB2r = NULL;
	struct kvec iov;
	int rc = 0;
	int resp_buftype;
	int status;
	unsigned int struct_len;
	struct cifs_ses *ses = tcon->ses;
	struct fs_attribute_info *pattr_inf = NULL;

	rc = build_qfs_info_req(&iov, tcon, FS_ATTRIBUTE_INFORMATION,
				sizeof(struct fs_attribute_info),
				persistent_fid, volatile_fid);
	if (rc)
		return rc;

	rc = smb2_sendrcv2(xid, ses, &iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "qfsattr buftype %d rc %d status %d", resp_buftype, rc, status);
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2QUERY_INFO]);
		goto qfsattr_exit;
	}
	pSMB2r = (struct query_info_rsp *)iov.iov_base;

	pattr_inf = (struct fs_attribute_info *)(4 /* RFC1001 len field */ +
		le16_to_cpu(pSMB2r->OutputBufferOffset) + (char *)&pSMB2r->hdr);
	struct_len = le32_to_cpu(pSMB2r->OutputBufferLength);
	rc = validate_buf(le16_to_cpu(pSMB2r->OutputBufferOffset), struct_len,
				&pSMB2r->hdr,
				/* attr info includes a name so have to
				   make sure struct is at least big enough
				   for fixed portion */
				sizeof(struct fs_attribute_info) - MAX_FS_NAME);
	if (!rc) {
		if (struct_len > sizeof(struct fs_attribute_info))
			struct_len = sizeof(struct fs_attribute_info);
		/* In case srv returned less than attr info, need to zero 1st */
		memset(&tcon->fsAttrInfo, 0, sizeof(struct fs_attribute_info));
		memcpy(&tcon->fsAttrInfo, pattr_inf, struct_len);
	}

qfsattr_exit:
	free_rsp_buf(resp_buftype, iov.iov_base);

	return rc;
}

int SMB2_QFS_device_info(const int xid, struct cifs_tcon *tcon,
			 u64 persistent_fid, u64 volatile_fid)
{
	struct query_info_rsp *pSMB2r = NULL;
	struct kvec iov;
	int rc = 0;
	int resp_buftype;
	int status;
	struct cifs_ses *ses = tcon->ses;
	struct fs_device_info *pdev_inf = NULL;

	rc = build_qfs_info_req(&iov, tcon, FS_DEVICE_INFORMATION,
				sizeof(struct fs_device_info),
				persistent_fid, volatile_fid);
	if (rc)
		return rc;

	rc = smb2_sendrcv2(xid, ses, &iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "qfsdev buftype %d rc %d status %d", resp_buftype, rc, status);
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2QUERY_INFO]);
		goto qfsdev_exit;
	}
	pSMB2r = (struct query_info_rsp *)iov.iov_base;

	pdev_inf = (struct fs_device_info *)(4 /* RFC1001 len field */ +
		le16_to_cpu(pSMB2r->OutputBufferOffset) + (char *)&pSMB2r->hdr);
	rc = validate_buf(le16_to_cpu(pSMB2r->OutputBufferOffset),
				le32_to_cpu(pSMB2r->OutputBufferLength),
				&pSMB2r->hdr, sizeof(struct fs_device_info));
	if (!rc)
		memcpy(&tcon->fsDevInfo, pdev_inf,
			sizeof(struct fs_device_info));

qfsdev_exit:
	free_rsp_buf(resp_buftype, iov.iov_base);

	return rc;
}

int SMB2_oplock_break(struct cifs_tcon *ptcon, __u64 netfid)
{
	/* BB FIXME BB */
	return -EOPNOTSUPP;
}

int SMB2_query_info(const int xid, struct cifs_tcon *tcon,
		    u64 persistent_fid, u64 volatile_fid,
		    FILE_ALL_INFO *pdata)
{
	struct query_info_req *pSMB2;
	struct query_info_rsp *pSMB2r = NULL;
	struct kvec iov[2];
	int rc = 0;
	int resp_buftype;
	int status;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;

	cFYI(1, "Query Info");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_QUERY_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType = SMB2_O_INFO_FILE;
	pSMB2->FileInfoClass = FILE_ALL_INFORMATION;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->InputBufferOffset = cpu_to_le16(sizeof(struct query_info_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->OutputBufferLength = cpu_to_le32(sizeof(FILE_ALL_INFO_SMB2)
			+ sizeof(struct query_info_rsp));

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4;

	rc = smb2_sendrcv2(xid, ses, iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "qinfo buftype %d rc %d status %d", resp_buftype, rc, status);
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2QUERY_INFO]);
		goto qinf_exit;
	}
	pSMB2r = (struct query_info_rsp *)iov[0].iov_base;

	rc = validate_and_copy_buf(le16_to_cpu(pSMB2r->OutputBufferOffset),
				le32_to_cpu(pSMB2r->OutputBufferLength),
				&pSMB2r->hdr, sizeof(FILE_ALL_INFO_SMB2),
				(char *)pdata);

qinf_exit:
	free_rsp_buf(resp_buftype, iov[0].iov_base);
	return rc;
}

int SMB2_query_full_ea_info(const int xid, struct cifs_tcon *tcon,
			u64 persistent_fid, u64 volatile_fid,
			char *pdata, int buf_len, int rsp_output_len,
			struct kvec *iov, int n_vec, const char *prefix,
			int prefix_len)
{
	struct query_info_req *pSMB2;
	struct query_info_rsp *pSMB2r = NULL;
	int rc = 0;
	int resp_buftype;
	int status;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;
	int ret_value = iov[1].iov_len == 0;

	cFYI(1, "Query Full EA Info");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_QUERY_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType	= SMB2_O_INFO_FILE;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->InputBufferLength = cpu_to_le32(iov[1].iov_len);
	pSMB2->InputBufferOffset =
		cpu_to_le16(offsetof(struct query_info_req, Buffer) - 4);

	if (rsp_output_len == 0) /* No hint output buffer size? */
		pSMB2->OutputBufferLength = cpu_to_le32(
			sizeof(FILE_FULL_EA_INFO)*10*2);
	else /* Hint to output buffer size given (plus some for metadata) */
		pSMB2->OutputBufferLength = cpu_to_le32(
			sizeof(FILE_FULL_EA_INFO)*rsp_output_len*2);

	iov[0].iov_base = (char *)pSMB2;

	if (n_vec > 2) { /* Requesting specific attribute name */
		iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length)
			+ 4 - 1;
		pSMB2->hdr.smb2_buf_length =
			cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length)
				- 1 /*pad*/ + iov[1].iov_len + iov[2].iov_len);
		pSMB2->FileInfoClass = FILE_FULL_EA_INFORMATION;
	} else { /* Requesting list of attributes */
		iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4;
		pSMB2->FileInfoClass = FILE_FULL_EA_INFORMATION;
	}

	rc = smb2_sendrcv2(xid, ses, iov, n_vec, &resp_buftype, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "qfulleainfo buftype %d rc %d status %d",
			resp_buftype, rc, status);
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2QUERY_INFO]);
		goto qinf_exit;
	}

	pSMB2r = (struct query_info_rsp *)iov[0].iov_base;
	rc = validate_and_copy_ea_buf(ret_value,
				le16_to_cpu(pSMB2r->OutputBufferOffset),
				le32_to_cpu(pSMB2r->OutputBufferLength),
				&pSMB2r->hdr, 8, pdata, buf_len,
				(char *)iov[2].iov_base, prefix, prefix_len);
qinf_exit:
	free_rsp_buf(resp_buftype, iov[0].iov_base);
	return rc;
}

/* BB Following two functions could merge to use common helper later */
int SMB2_set_delete(const int xid, struct cifs_tcon *tcon,
		    u64 persistent_fid, u64 volatile_fid)
{
	struct set_info_req *pSMB2;
	struct set_info_rsp *pSMB2r = NULL;
	struct kvec iov[1];
	int rc = 0;
	int resp_buftype;
	int status;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;

	cFYI(1, "Set Info");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_SET_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType = SMB2_O_INFO_FILE;
	pSMB2->FileInfoClass = FILE_DISPOSITION_INFORMATION;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->BufferOffset = cpu_to_le16(sizeof(struct set_info_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->BufferLength = cpu_to_le32(1);
	pSMB2->Buffer[0] = 1;
	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4;

	rc = smb2_sendrcv2(xid, ses, iov, 1, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "sinfo buftype %d rc %d status %d", resp_buftype, rc, status);
	pSMB2r = (struct set_info_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2SET_INFO]);
		goto set_delete_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto set_delete_exit;
	}

set_delete_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

int SMB2_set_hardlink(const int xid, struct cifs_tcon *tcon,
		    u64 persistent_fid, u64 volatile_fid, __le16 *target_file)
{
	struct set_info_req *pSMB2;
	struct set_info_rsp *pSMB2r = NULL;
	struct kvec iov[2];
	int rc = 0;
	int resp_buftype;
	int status;
	int uni_path_len;
	struct TCP_Server_Info *server;
	struct FileLinkInformation *pfli;
	struct cifs_ses *ses = tcon->ses;

	cFYI(1, "Create hard link");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_SET_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType = SMB2_O_INFO_FILE;
	pSMB2->FileInfoClass = FILE_LINK_INFORMATION;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->BufferOffset = cpu_to_le16(sizeof(struct set_info_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);

	uni_path_len = (2 * UniStrnlen((wchar_t *)target_file, PATH_MAX)) + 2;
	pSMB2->BufferOffset = cpu_to_le16(sizeof(struct set_info_req) - 1
		/* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->BufferLength = cpu_to_le32(sizeof(struct FileLinkInformation) +
					uni_path_len);

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;
	iov[0].iov_len += sizeof(struct FileLinkInformation);
	iov[1].iov_base = target_file;
	iov[1].iov_len = uni_path_len; /* This is two bytes more - includes
					  null - is it better to send without */

	pfli = (struct FileLinkInformation *)pSMB2->Buffer;
	pfli->ReplaceIfExists = 0; /* 1 = replace existing link with new */
			      /* 0 = fail if link already exists */
	pfli->RootDirectory = 0;  /* MBZ for network ops (why does spec say?) */
	pfli->FileNameLength = cpu_to_le32(uni_path_len - 2);
	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length) - 1 +
			sizeof(struct FileLinkInformation) + uni_path_len);

	rc = smb2_sendrcv2(xid, ses, iov, 2, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "sinfo buftype %d rc %d status %d", resp_buftype, rc, status);
	pSMB2r = (struct set_info_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2SET_INFO]);
		goto set_link_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto set_link_exit;
	}

set_link_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

int SMB2_rename(const int xid, struct cifs_tcon *tcon,
		    u64 persistent_fid, u64 volatile_fid, __le16 *target_file)
{
	struct set_info_req *pSMB2;
	struct set_info_rsp *pSMB2r = NULL;
	struct kvec iov[2];
	int rc = 0;
	int resp_buftype;
	int status;
	int uni_path_len;
	struct TCP_Server_Info *server;
	struct FileRenameInformation *pfli;
	struct cifs_ses *ses = tcon->ses;

	cFYI(1, "rename");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_SET_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType = SMB2_O_INFO_FILE;
	pSMB2->FileInfoClass = FILE_RENAME_INFORMATION;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->BufferOffset = cpu_to_le16(sizeof(struct set_info_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);

	uni_path_len = (2 * UniStrnlen((wchar_t *)target_file, PATH_MAX)) + 2;
	pSMB2->BufferOffset = cpu_to_le16(sizeof(struct set_info_req) - 1
		/* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->BufferLength = cpu_to_le32(sizeof(struct FileRenameInformation) +
					uni_path_len);

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;
	iov[0].iov_len += sizeof(struct FileRenameInformation);
	iov[1].iov_base = target_file;
	iov[1].iov_len = uni_path_len; /* This is two bytes more - includes
					  null - is it better to send without */

	pfli = (struct FileRenameInformation *)pSMB2->Buffer;
	pfli->ReplaceIfExists = 0; /* 1 = replace existing link with new */
			      /* 0 = fail if link already exists */
	pfli->RootDirectory = 0;  /* MBZ for network ops (why does spec say?) */
	pfli->FileNameLength = cpu_to_le32(uni_path_len - 2);
	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length) - 1 +
			sizeof(struct FileRenameInformation) + uni_path_len);

	rc = smb2_sendrcv2(xid, ses, iov, 2, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	pSMB2r = (struct set_info_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2SET_INFO]);
		goto rename_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto rename_exit;
	}

rename_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

int SMB2_set_info(const int xid, struct cifs_tcon *tcon,
		    u64 persistent_fid, u64 volatile_fid,
		    FILE_BASIC_INFO *pdata)
{
	struct set_info_req *pSMB2;
	struct set_info_rsp *pSMB2r = NULL;
	struct kvec iov[2];
	int rc = 0;
	int resp_buftype;
	int status;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;

	cFYI(1, "Set Info");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	if (pdata == NULL)
		return -EINVAL;

	rc = small_smb2_init(SMB2_SET_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType = SMB2_O_INFO_FILE;
	pSMB2->FileInfoClass = FILE_BASIC_INFORMATION;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->BufferOffset = cpu_to_le16(sizeof(struct set_info_req)
			- 1 /* pad */ - 4 /* do not count rfc1001 len field */);
	pSMB2->BufferLength = cpu_to_le32(sizeof(FILE_BASIC_INFO));

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;

	iov[1].iov_base = pdata;
	iov[1].iov_len = sizeof(FILE_BASIC_INFO);

	pSMB2->hdr.smb2_buf_length = cpu_to_be32(be32_to_cpu(
		pSMB2->hdr.smb2_buf_length) + sizeof(FILE_BASIC_INFO) - 1);
	rc = smb2_sendrcv2(xid, ses, iov, 2, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	cFYI(1, "sinfo buftype %d rc %d status %d", resp_buftype, rc, status);
	pSMB2r = (struct set_info_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2SET_INFO]);
		goto set_info_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto set_info_exit;
	}

set_info_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

int SMB2_set_ea_info(const int xid, struct cifs_tcon *tcon,
		u64 persistent_fid, u64 volatile_fid, struct kvec iov[4])
{
	struct set_info_req *pSMB2;
	struct set_info_rsp *pSMB2r = NULL;
	int rc = 0;
	int resp_buftype;
	int status;
	struct TCP_Server_Info *server;
	struct cifs_ses *ses = tcon->ses;

	cFYI(1, "set_ea_info");

	if (ses && (ses->server))
		server = ses->server;
	else
		return -EIO;

	rc = small_smb2_init(SMB2_SET_INFO, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	pSMB2->InfoType = SMB2_O_INFO_FILE;
	pSMB2->FileInfoClass = FILE_FULL_EA_INFORMATION;
	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;

	pSMB2->BufferOffset = cpu_to_le16(sizeof(struct set_info_req) - 1
					/* pad */ - 4 /* rfc1001 len field */);
	pSMB2->BufferLength = cpu_to_le32(sizeof(FILE_FULL_EA_INFO) - 2 +
					iov[2].iov_len /* name */
					+ iov[3].iov_len /* value */);

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;

	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length)
			- 1 /*pad*/ + iov[1].iov_len + iov[2].iov_len
			+ iov[3].iov_len);

	rc = smb2_sendrcv2(xid, ses, iov, 4, &resp_buftype /* ret */, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	pSMB2r = (struct set_info_rsp *)iov[0].iov_base;

	if (rc != 0) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2SET_INFO]);
		goto rename_exit;
	}

	if (pSMB2r == NULL) {
		rc = -EIO;
		goto rename_exit;
	}

rename_exit:
	free_rsp_buf(resp_buftype, pSMB2r);
	return rc;
}

/* To form a chain of read requests, any read requests after the
 * first should have the end_of_chain boolean set to true. */
int new_read_req(struct kvec *iov, struct cifs_tcon *tcon,
		u64 persistent_fid, u64 volatile_fid,
		const unsigned int count, const __u64 lseek,
		unsigned int remaining_bytes,
		int request_type)
{
	int rc = -EACCES;
	struct read_req *pSMB2 = NULL;

	rc = small_smb2_init(SMB2_READ, tcon, (void **) &pSMB2);
	if (rc)
		return rc;
	if (tcon->ses->server == NULL)
		return -ECONNABORTED;

	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->ReadChannelInfoOffset = 0; /* reserved */
	pSMB2->ReadChannelInfoLength = 0; /* reserved */
	pSMB2->Channel = 0; /* reserved */
	pSMB2->MinimumCount = 0;
	pSMB2->Length = cpu_to_le32(count);
	pSMB2->Offset = cpu_to_le64(lseek);

	if (request_type & CHAINED_REQUEST) {
		if (!(request_type & END_OF_CHAIN)) {
			pSMB2->hdr.NextCommand = cpu_to_le32(
				be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4);
		} else /* END_OF_CHAIN */
			pSMB2->hdr.NextCommand = 0;
		if (request_type & RELATED_REQUEST) {
			pSMB2->hdr.Flags |= SMB2_FLAGS_RELATED_OPERATIONS;
			/* related requests use info from previous
			 * read request in chain. */
			pSMB2->hdr.SessionId = 0xFFFFFFFF;
			pSMB2->hdr.TreeId = 0xFFFFFFFF;
			pSMB2->PersistentFileId = 0xFFFFFFFF;
			pSMB2->VolatileFileId = 0xFFFFFFFF;
		}
	}
	if (remaining_bytes > count)
		pSMB2->RemainingBytes = cpu_to_le32(remaining_bytes);
	else
		pSMB2->RemainingBytes = 0;

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4;
	return rc;
}

int SMB2_read(const int xid, struct cifs_tcon *tcon,
	u64 persistent_fid, u64 volatile_fid,
	const unsigned int count, const __u64 lseek,
	unsigned int *nbytes, char **buf, int *pbuf_type,
	unsigned int remaining_bytes)
{
	int status, resp_buftype, rc = -EACCES;
	struct read_rsp *pSMB2r = NULL;
	struct kvec iov[1];

	*nbytes = 0;
	rc = new_read_req(iov, tcon, persistent_fid, volatile_fid,
			count, lseek, remaining_bytes, 0);
	if (rc)
		return rc;
	rc = smb2_sendrcv2(xid, tcon->ses, iov, 1,
			   &resp_buftype, &status,
			   CIFS_STD_OP | CIFS_LOG_ERROR);
	if (status == STATUS_END_OF_FILE) {
		free_rsp_buf(resp_buftype, iov[0].iov_base);
		return 0;
	}

	cFYI(1, "read returned buftype %d with rc %d status 0x%x",
		 resp_buftype, rc, status);

	pSMB2r = (struct read_rsp *)iov[0].iov_base;

	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2READ]);
		cERROR(1, "Send error in read = %d", rc);
	} else {
		*nbytes = le32_to_cpu(pSMB2r->DataLength);
		if ((*nbytes > SMB2_MAX_MSGSIZE)
			|| (*nbytes > count)) {
			cFYI(1, "bad length %d for count %d",
					*nbytes, count);
			rc = -EIO;
			*nbytes = 0;
		}
	}
	if (resp_buftype != CIFS_NO_BUFFER) {
		*buf = iov[0].iov_base;
		if (resp_buftype == CIFS_SMALL_BUFFER)
			*pbuf_type = CIFS_SMALL_BUFFER;
		else if (resp_buftype == CIFS_LARGE_BUFFER)
			*pbuf_type = CIFS_LARGE_BUFFER;
	}
	return rc;
}

/* SMB2_write function gets iov pointer to kvec array with n_vec as a length.
   The length must be at least 2 because the first element of the array is
   SMB2 header. Other elements contain a data to write, its length is specified
   by count. */
int SMB2_write(const int xid, struct cifs_tcon *tcon,
	const u64 persistent_fid, const u64 volatile_fid,
	const unsigned int count, const __u64 lseek,
	unsigned int *nbytes, struct kvec *iov, int n_vec,
	const unsigned int remaining_bytes, int wtimeout)
{
	int rc = 0;
	struct write_req *pSMB2 = NULL;
	struct write_rsp *pSMB2r = NULL;
	int status, resp_buftype;
	*nbytes = 0;

	if (n_vec < 2)
		return rc;

	rc = small_smb2_init(SMB2_WRITE, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	if (tcon->ses->server == NULL)
		return -ECONNABORTED;

	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->WriteChannelInfoOffset = 0;
	pSMB2->WriteChannelInfoLength = 0;
	pSMB2->Channel = 0;
	pSMB2->Length = cpu_to_le32(count);
	pSMB2->Offset = cpu_to_le64(lseek);
	pSMB2->DataOffset = cpu_to_le16(offsetof(struct write_req, Buffer) - 4);
	pSMB2->RemainingBytes = 0;

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;

	/* length of entire message including data to be written */
	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length)
			    - 1 /* pad */ + count);

	rc = smb2_sendrcv2(xid, tcon->ses, iov, n_vec, &resp_buftype, &status,
			wtimeout | CIFS_LOG_ERROR);

	cFYI(1, "write returned buftype %d with rc %d status 0x%x",
		 resp_buftype, rc, status);

	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2WRITE]);
		cERROR(1, "Send error in write = %d", rc);
	} else {
		pSMB2r = (struct write_rsp *)iov[0].iov_base;
		*nbytes = le32_to_cpu(pSMB2r->DataLength);
		free_rsp_buf(resp_buftype, pSMB2r);
	}
	return rc;
}

/* SMB2_write_complex function gets iov pointer to kvec array with n_vec as a
   length. The length must be at least 2 because the first element of the array
   is SMB2 header. Other elements contain a data to write, its length is
   specified by count. */
int SMB2_write_complex(const int xid, struct cifs_tcon *tcon,
	const u64 persistent_fid, const u64 volatile_fid,
	const unsigned int count, const __u64 lseek,
	unsigned int *nbytes, struct kvec *iov, int n_vec,
	const unsigned int remaining_bytes, struct mid_q_entry **mid,
	const unsigned int size)
{
	int rc = 0;
	struct write_req *pSMB2 = NULL;
	struct write_rsp *pSMB2r = NULL;
	int status, resp_buftype;
	*nbytes = 0;

	if (n_vec < 2)
		return rc;

	rc = small_smb2_init(SMB2_WRITE, tcon, (void **) &pSMB2);
	if (rc)
		return rc;

	if (tcon->ses->server == NULL)
		return -ECONNABORTED;

	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;
	pSMB2->WriteChannelInfoOffset = 0;
	pSMB2->WriteChannelInfoLength = 0;
	pSMB2->Channel = 0;
	pSMB2->Length = cpu_to_le32(count);
	pSMB2->Offset = cpu_to_le64(lseek);
	pSMB2->DataOffset = cpu_to_le16(offsetof(struct write_req, Buffer) - 4);
	pSMB2->RemainingBytes = 0;

	iov[0].iov_base = (char *)pSMB2;
	iov[0].iov_len = be32_to_cpu(pSMB2->hdr.smb2_buf_length) + 4 - 1;

	/* length of entire message including data to be written */
	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length)
			    - 1 /* pad */ + count);

	rc = smb2_send_complex(xid, tcon->ses, iov, n_vec, &resp_buftype,
			       &status, mid, size);

	cFYI(1, "write returned buftype %d with rc %d status 0x%x",
		 resp_buftype, rc, status);

	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2WRITE]);
		cERROR(1, "Send error in write = %d", rc);
	} else {
		pSMB2r = (struct write_rsp *)iov[0].iov_base;
		*nbytes = le32_to_cpu(pSMB2r->DataLength);
		free_rsp_buf(resp_buftype, pSMB2r);
	}

	return rc;
}

int SMB2_lock(const int xid, struct cifs_tcon *tcon,
	const u64 persistent_fid, const u64 volatile_fid,
	u64 length, u64 offset, u32 lockFlags, int wait)
{
	int rc = 0;
	struct smb2_lock_req *pSMB2 = NULL;
/*	lock_rsp *pSMB2r = NULL; */ /* No resp data other than rc to parse */
	int pbytes_returned;
	int timeout = 0;

	cFYI(1, "SMB2_lock timeout %d numLock %d", wait, 1);
	rc = small_smb2_init(SMB2_LOCK, tcon, (void **) &pSMB2);

	if (rc)
		return rc;

	if (wait)
		timeout = CIFS_BLOCKING_OP; /* blocking operation, no timeout */

	pSMB2->LockCount = cpu_to_le16(1);

	pSMB2->PersistentFileId = persistent_fid;
	pSMB2->VolatileFileId = volatile_fid;

	pSMB2->locks[0].Length = cpu_to_le64(length);
	pSMB2->locks[0].Offset = cpu_to_le64(offset);
	pSMB2->locks[0].Flags = cpu_to_le16(lockFlags);

	pSMB2->hdr.smb2_buf_length =
		cpu_to_be32(be32_to_cpu(pSMB2->hdr.smb2_buf_length)
			- 1 /* pad */ + sizeof(struct smb2_lock_element));

	if (wait) {
		rc = smb2_sendrcv_blocking(xid, tcon,
					   (struct smb2_hdr *)pSMB2,
					   (struct smb2_hdr *)pSMB2,
					   &pbytes_returned);

	} else {
		rc = smb2_sendrcv_norsp(xid, tcon->ses,
					(struct smb2_hdr *)pSMB2, timeout);
		/* SMB2 buffer freed by function above */
	}
	if (rc) {
		cifs_stats_inc(&tcon->stats.smb2_stats.smb2_com_fail[SMB2LOCK]);
		cFYI(1, "Send error in Lock = %d", rc);
	}

	/* Note: On -EAGAIN error only caller can retry on handle based calls
	since file handle passed in no longer valid */
	return rc;
}

