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

/* BB add missing functions here */
