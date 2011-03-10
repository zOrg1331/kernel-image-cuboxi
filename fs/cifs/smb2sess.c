/*
 *   fs/smb2/sess.c
 *
 *   SMB/CIFS session setup handling routines
 *
 *   Copyright (c) International Business Machines  Corp., 2009
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

#include "smb2pdu.h"
#include "cifsglob.h"
#include "cifsproto.h"
#include "smb2proto.h"
#include "cifs_debug.h"

int smb2_setup_session(unsigned int xid, struct cifs_ses *psesinfo,
			struct nls_table *nls_info)
{
	int rc = 0;
	struct TCP_Server_Info *server = psesinfo->server;

	/* We used to server->check max_buf in cifs, but does not get
	   returned in smb2 so check max_read instead */
	if (server->max_read == 0) /* no need to send on reconnect */ {
		atomic_set(&server->credits, 1);
		rc = SMB2_negotiate(xid, psesinfo);
		if (rc == -EAGAIN) {
			/* retry only once on 1st time connection */
			rc = SMB2_negotiate(xid, psesinfo);
			if (rc == -EAGAIN)
				rc = -EHOSTDOWN;
		}
		if (rc == 0) {
			spin_lock(&GlobalMid_Lock);
			if (server->tcpStatus != CifsExiting)
				server->tcpStatus = CifsGood;
			else
				rc = -EHOSTDOWN;
			spin_unlock(&GlobalMid_Lock);

		}
	}

	if (rc)
		goto ss_err_exit;

	/*	psesinfo->sequence_number = 0;*/
	cFYI(1, "Security Mode: 0x%x Capabilities: 0x%x TimeAdjust: %d",
		 server->sec_mode, server->capabilities, server->timeAdj);

	rc = SMB2_sess_setup(xid, psesinfo, nls_info);
	if (rc) {
		cERROR(1, "error in SessSetup = %d", rc);
		goto ss_err_exit;
	}

	cFYI(1, "SMB2 Session Established successfully");
	spin_lock(&GlobalMid_Lock);
	psesinfo->status = CifsGood;
	psesinfo->need_reconnect = false;
	spin_unlock(&GlobalMid_Lock);

ss_err_exit:
	return rc;
}

