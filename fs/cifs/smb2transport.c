/*
 *   fs/cifs/transport.c
 *
 *   Copyright (C) International Business Machines  Corp., 2002,2011
 *   Author(s): Steve French (sfrench@us.ibm.com)
 *   Jeremy Allison (jra@samba.org) 2006.
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

#include <linux/fs.h>
#include <linux/list.h>
#include <linux/wait.h>
#include <linux/net.h>
#include <linux/delay.h>
#include <linux/uaccess.h>
#include <asm/processor.h>
#include <linux/mempool.h>
#include "smb2pdu.h"
#include "cifsglob.h"
#include "cifsproto.h"
#include "smb2proto.h"
#include "cifs_debug.h"
#include "smb2status.h"

extern mempool_t *smb2_mid_poolp;

/*
 *  Send an (optionally, already signed) SMB2 request over a socket.
 *  This socket is already locked (by a mutex) by the caller so we
 *  won't have framing problems or mess up SMB2 signatures.
 */

int smb2_sendv(struct TCP_Server_Info *server, struct kvec *iov, int n_vec)
{
	int rc = -EHOSTDOWN;

	cFYI(1, "function not merged yet");  /* BB fixme */

	return rc;
}



/*
 *
 * Send an SMB Request.  No response info (other than return code)
 * needs to be parsed.
 *
 * flags indicate the type of request buffer and how long to wait
 * and whether to log NT STATUS code (error) before mapping it to POSIX error
 *
 */
int
smb2_sendrcv_norsp(const unsigned int xid, struct cifs_ses *ses,
		struct smb2_hdr *in_buf, int flags)
{
	int rc;
	struct kvec iov[1];
	int resp_buf_type;

	iov[0].iov_base = (char *)in_buf;
	iov[0].iov_len = be32_to_cpu(in_buf->smb2_buf_length) + 4;
	flags |= CIFS_NO_RESP;
	rc = smb2_sendrcv2(xid, ses, iov, 1, &resp_buf_type, NULL, flags);
	/* BB remove the following debug line eventually */
	cFYI(1, "SendRcvNoRsp flags %d rc %d", flags, rc);

	return rc;
}

static int
smb2_send_lock_cancel(const unsigned int xid, struct cifs_tcon *tcon,
			struct kvec *iov)
{
	int rsp_buf_type;
	struct cifs_ses *ses = tcon->ses;
	struct lock_req *pSMB2 = (struct lock_req *)iov[0].iov_base;

	pSMB2->locks[0].Flags = SMB2_LOCKFLAG_UNLOCK;

	return smb2_sendrcv2(xid, ses, iov, 1, &rsp_buf_type,
				NULL, CIFS_STD_OP);
}

int
smb2_sendrcv_blocking(const unsigned int xid, struct cifs_tcon *tcon,
		struct smb2_hdr *in_buf,
		struct smb2_hdr *out_buf,
		int *pbytes_returned)
{
	int rc = -EHOSTDOWN;

	cFYI(1, "function not merged yet");  /* BB fixme */

	return rc;
}

/* sendrcv2 is passed a cifs_ses structure (rather than simply being
   passed the ses->server->socket), because it needs the creds
   contained in the cifs_ses struct in order to sign requests */
int
smb2_sendrcv2(const unsigned int xid, struct cifs_ses *ses,
	     struct kvec *iov, int n_vec, int *presp_buftype /* ret */,
	     int *status /* ret SMB2 network status code */, const int flags)
{
	int rc = -EHOSTDOWN;

	cFYI(1, "function not merged yet");  /* BB fixme */

	return rc;
}

/* smb2_send_complex is passed a cifs_ses structure (rather than simply being
   passed the ses->server->socket), because it needs the creds
   contained in the cifs_ses struct in order to sign requests */
int
smb2_send_complex(const unsigned int xid, struct cifs_ses *ses,
		     struct kvec *iov, int n_vec, int *presp_buftype /* ret */,
		     int *status /* ret SMB2 network status code */,
		     struct mid_q_entry **mid, const unsigned int size)
{
	int rc = -EHOSTDOWN;

	cFYI(1, "function not merged yet");  /* BB fixme */

	return rc;
}

static void
wake_up_smb2_task(struct smb2_mid_entry *mid)
{
	wake_up_process(mid->callback_data);
}

static struct smb2_mid_entry *
smb2_mid_entry_alloc(const struct smb2_hdr *smb_buffer,
		     struct TCP_Server_Info *server)
{
	struct smb2_mid_entry *temp;

	if (server == NULL) {
		cERROR(1, "Null TCP session in smb2_mid_entry_alloc");
		return NULL;
	}

	temp = mempool_alloc(smb2_mid_poolp, GFP_NOFS);
	if (temp == NULL)
		return temp;
	else {
		memset(temp, 0, sizeof(struct smb2_mid_entry));
		temp->mid = smb_buffer->MessageId;	/* always LE */
		temp->pid = current->pid;
		temp->command = smb_buffer->Command;	/* Always LE */
		temp->when_alloc = jiffies;

		/*
		 * The default is for the mid to be synchronous, so the
		 * default callback just wakes up the current task.
		 */
		temp->callback = wake_up_smb2_task;
		temp->callback_data = current;
	}

	atomic_inc(&midCount);
	temp->mid_state = MID_REQUEST_ALLOCATED;
	return temp;
}

static int get_smb2_mid(struct cifs_ses *ses, struct smb2_hdr *in_buf,
			struct smb2_mid_entry **ppmidQ)
{
	if (ses->server->tcpStatus == CifsExiting)
		return -ENOENT;

	if (ses->server->tcpStatus == CifsNeedReconnect) {
		cFYI(1, "tcp session dead - return to caller to retry");
		return -EAGAIN;
	}

	if (ses->status != CifsGood) {
		/* check if SMB session is bad because we are setting it up */
		if ((in_buf->Command != SMB2_SESSION_SETUP) &&
			(in_buf->Command != SMB2_NEGOTIATE))
			return -EAGAIN;
		/* else ok - we are setting up session */
	}
	*ppmidQ = smb2_mid_entry_alloc(in_buf, ses->server);
	if (*ppmidQ == NULL)
		return -ENOMEM;
	spin_lock(&GlobalMid_Lock);
	list_add_tail(&(*ppmidQ)->qhead, &ses->server->pending_mid_q);
	spin_unlock(&GlobalMid_Lock);
	return 0;
}


/* BB add missing functions here */
