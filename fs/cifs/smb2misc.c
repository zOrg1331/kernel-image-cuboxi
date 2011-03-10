/*
 *   fs/cifs/smb2misc.c
 *
 *   Copyright (C) International Business Machines  Corp., 2002,2011
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
#include <linux/ctype.h>
#include "smb2pdu.h"
#include "cifsglob.h"
#include "cifsproto.h"
#include "smb2proto.h"
#include "cifs_debug.h"
#include "cifs_unicode.h"
#include "smb2status.h"

/*
__u64 get_mid(struct tcp_srv_inf *server)
{
	__u64 mid;

	if (server == NULL)
		return 0;

	spin_lock(&SMB2_mid_lock);
	mid = server->current_mid++;
	spin_unlock(&SMB2_mid_lock);
	return mid;
} */ /* BB do we eventually need an SMB2 version of this routine? BB */

static int
check_smb2_hdr(struct smb2_hdr *smb, __u16 mid)
{
	/* Make sure that this really is an SMB, that it is a response,
	   and that the message ids match */
	if ((*(__le32 *) smb->ProtocolId == cpu_to_le32(0x424d53fe)) &&
		(mid == smb->MessageId)) {
		if (smb->Flags & SMB2_FLAGS_SERVER_TO_REDIR)
			return 0;
		else {
		/* only one valid case where server sends us request */
			if (smb->Command == SMB2_OPLOCK_BREAK)
				return 0;
			else
				cERROR(1, "Received Request not response");
		}
	} else { /* bad signature or mid */
		if (*(__le32 *) smb->ProtocolId != cpu_to_le32(0x424d53fe))
 			cERROR(1, "Bad protocol string signature header %x",
				*(unsigned int *) smb->ProtocolId);
		if (mid != smb->MessageId)
			cERROR(1, "Mids do not match");
	}
	cERROR(1, "bad smb detected. The Mid=%lld", smb->MessageId);
	return 1;
}

/*
 *  The following table defines the expected "StructureSize" of SMB2 responses
 *  in order by SMB2 command.  This is similar to "wct" in SMB/CIFS responses.
 *
 *  Note that commands are defined in smb2pdu.h in le16 but the array below is
 *  indexed by command in host byte order
 */
static const int smb2_rsp_struct_sizes[NUMBER_OF_SMB2_COMMANDS] = {
	/* SMB2_NEGOTIATE */ 65,
	/* SMB2_SESSION_SETUP */ 9,
	/* SMB2_LOGOFF */ 4,
	/* SMB2_TREE_CONNECT */	16,
	/* SMB2_TREE_DISCONNECT */ 4,
	/* SMB2_CREATE */ 89,
	/* SMB2_CLOSE */ 60,
	/* SMB2_FLUSH */ 4,
	/* SMB2_READ */	17,
	/* SMB2_WRITE */ 17,
	/* SMB2_LOCK */	4,
	/* SMB2_IOCTL */ 49,
	/* SMB2_CANCEL */ 0, /* BB CHECK this ... not listed in documentation */
	/* SMB2_ECHO */ 4,
	/* SMB2_QUERY_DIRECTORY */ 9,
	/* SMB2_CHANGE_NOTIFY */ 9,
	/* SMB2_QUERY_INFO */ 9,
	/* SMB2_SET_INFO */ 2,
	/* SMB2_OPLOCK_BREAK */ 24 /* BB FIXME can also be 44 for lease break */
};

int
checkSMB2(struct smb2_hdr *smb, __u64 mid, unsigned int length)
{
	struct smb2_pdu * smb2 = (struct smb2_pdu *)smb;
	__u32 len = be32_to_cpu(smb->smb2_buf_length);
	__u32 clc_len;  /* calculated length */
	__u16 command;

	/* BB disable following printk later */
	cFYI(1, "checkSMB Length: 0x%x, smb_buf_length: 0x%x", length, len);

	/* Add function to do table lookup of StructureSize by command
	   ie Validate the wct via smb2_struct_sizes table above */

	if (length < 2 + sizeof(struct smb2_hdr)) {
		if ((length >= sizeof(struct smb2_hdr))
			    && (smb->Status != 0)) {
			smb2->StructureSize2 = 0;
			/* As with SMB/CIFS, on some error cases servers may
			   not return wct properly */
			return 0;
		} else {
			cERROR(1, "Length less than smb header size");
		}
		return 1;
	}
	if (len > CIFSMaxBufSize + MAX_CIFS_HDR_SIZE - 4) {
		cERROR(1, "smb length greater than maximum, mid=%lld",
				   smb->MessageId);
		return 1;
	}

	if (check_smb2_hdr(smb, mid))
		return 1;

	if (le16_to_cpu(smb->StructureSize) != 64) {
		cERROR(1, "Illegal structure size %d",
			  le16_to_cpu(smb->StructureSize));
		return 1;
	}

	command = le16_to_cpu(smb->Command);
	if (command >= NUMBER_OF_SMB2_COMMANDS) {
		cERROR(1, "illegal SMB2 command %d", command);
		return 1;
	}

	if (smb2_rsp_struct_sizes[command] !=
	    le16_to_cpu(smb2->StructureSize2)) {
		if ((smb->Status == 0) ||
		    (le16_to_cpu(smb2->StructureSize2) != 9)) {
			/* error packets have 9 byte structure size */
			cERROR(1, "Illegal response size %d for command %d",
				   le16_to_cpu(smb2->StructureSize2), command);
			return 1;
		}
	}

	clc_len = smb2_calc_size(smb);

	if (4 + len != length) {
		cERROR(1, "Length read does not match RFC1001 length %d",
			   len);
		return 1;
	}

	if (4 + len != clc_len) {
		cFYI(1, "Calculated size %d length %d mismatch for mid %lld",
			 clc_len, 4 + len, smb->MessageId);
		if (clc_len == 4 + len + 1) /* BB FIXME (fix samba) */
			return 0; /* BB workaround Samba 3 bug SessSetup rsp */
		return 1;
	}
	return 0;
}

void
dump_smb2(struct smb2_hdr *smb_buf, int smb_buf_length)
{
	dump_smb((struct smb_hdr *)smb_buf, smb_buf_length);
}

/*
 *  The size of the variable area depends on the offset and length fields
 *  located in different fields for various SMB2 responses.  SMB2 responses
 *  with no variable length info, show an offset of zero for the offset field.
 */
static const bool has_smb2_data_area[NUMBER_OF_SMB2_COMMANDS] = {
	/* SMB2_NEGOTIATE */ true,
	/* SMB2_SESSION_SETUP */ true,
	/* SMB2_LOGOFF */ false,
	/* SMB2_TREE_CONNECT */	false,
	/* SMB2_TREE_DISCONNECT */ false,
	/* SMB2_CREATE */ true,
	/* SMB2_CLOSE */ false,
	/* SMB2_FLUSH */ false,
	/* SMB2_READ */	true,
	/* SMB2_WRITE */ false,
	/* SMB2_LOCK */	false,
	/* SMB2_IOCTL */ true,
	/* SMB2_CANCEL */ false, /* BB CHECK this not listed in documentation */
	/* SMB2_ECHO */ false,
	/* SMB2_QUERY_DIRECTORY */ true,
	/* SMB2_CHANGE_NOTIFY */ true,
	/* SMB2_QUERY_INFO */ true,
	/* SMB2_SET_INFO */ false,
	/* SMB2_OPLOCK_BREAK */ false
};

/* Returns the pointer to the beginning of the data area
   Length of the data area and the offset to it (from the beginning of the smb
   are also returned */
char *smb2_get_data_area_len(int *poff, int *plen, struct smb2_hdr *pSMB2)
{
	*poff = 0;
	*plen = 0;

	/* error responses do not have data area */
	if (pSMB2->Status &&
	   (le32_to_cpu(pSMB2->Status) != STATUS_MORE_PROCESSING_REQUIRED) &&
	   (le16_to_cpu(((struct smb2_err_rsp *)pSMB2)->StructureSize) == 9))
		return NULL;

	/* Following commands have data areas so we have to get the location
	   of the data buffer offset and data buffer length for the particular
	   command */
	switch (pSMB2->Command) {
	case SMB2_NEGOTIATE:
		*poff = le16_to_cpu(
			((struct smb2_negotiate_rsp *)pSMB2)->SecurityBufferOffset);
		*plen = le16_to_cpu(
			((struct smb2_negotiate_rsp *)pSMB2)->SecurityBufferLength);
		break;
	case SMB2_SESSION_SETUP:
		*poff = le16_to_cpu(
			((struct sess_setup_rsp *)pSMB2)->SecurityBufferOffset);
		*plen = le16_to_cpu(
			((struct sess_setup_rsp *)pSMB2)->SecurityBufferLength);
		break;
	case SMB2_CREATE:
		*poff = le32_to_cpu(
			((struct create_rsp *)pSMB2)->CreateContextsOffset);
		*plen = le32_to_cpu(
			((struct create_rsp *)pSMB2)->CreateContextsLength);
		break;
	case SMB2_READ:
		*poff = ((struct read_rsp *)pSMB2)->DataOffset;
		*plen = le32_to_cpu(
			((struct read_rsp *)pSMB2)->DataLength);
		break;
	case SMB2_QUERY_INFO:
		*poff = le16_to_cpu(
			((struct query_info_rsp *)pSMB2)->OutputBufferOffset);
		*plen = le32_to_cpu(
			((struct query_info_rsp *)pSMB2)->OutputBufferLength);
		break;
	case SMB2_QUERY_DIRECTORY:
		*poff = le16_to_cpu(
		((struct query_directory_rsp *)pSMB2)->OutputBufferOffset);
		*plen = le32_to_cpu(
		((struct query_directory_rsp *)pSMB2)->OutputBufferLength);
		break;
	case SMB2_IOCTL:
	case SMB2_CHANGE_NOTIFY:
	default:
		/* BB FIXME for unimplemented cases above */
		cERROR(1, "no length check for command");
		break;
	}

	/* Invalid length or offset probably means data area is invalid, but
	   we have little choice but to ignore the data area in this case */
	if (*poff > 4096) {
		dump_stack();
		cERROR(1, "offset %d too large, data area ignored", *poff);
		*plen = 0;
		*poff = 0;
	} else if (*poff < 0) {
		cERROR(1, "negative offset to data invalid ignore data area");
		*poff = 0;
		*plen = 0;
	} else if (*plen < 0) {
		cERROR(1, "negative data length invalid, data area ignored");
		*plen = 0;
	} else if (*plen > 128 * 1024) {
		cERROR(1, "data area larger than 128K");
		*plen = 0;
	}

	/* return pointer to beginning of data area, ie offset from SMB start */
	if ((*poff != 0) && (*plen != 0))
		return pSMB2->ProtocolId + *poff;
	else
		return NULL;
}

/*
 * calculate the size of the SMB message based on the fixed header
 * portion, the number of word parameters and the data portion of the message
 */
unsigned int
smb2_calc_size(struct smb2_hdr *pSMB2h)
{
	struct smb2_pdu *pSMB2 = (struct smb2_pdu *)pSMB2h;
	int offset; /* the offset from the beginning of SMB to data area */
	int data_length; /* the length of the variable length data area */
	/* Structure Size has already been checked to make sure it is 64 */
	int len = 4 + le16_to_cpu(pSMB2->hdr.StructureSize);

	/* StructureSize2, ie length of fixed parameter area has already
	   been checked to make sure it is the correct length */
	len += le16_to_cpu(pSMB2->StructureSize2);

	if (has_smb2_data_area[le16_to_cpu(pSMB2h->Command)] == false)
		goto calc_size_exit;

	smb2_get_data_area_len(&offset, &data_length, pSMB2h);
	cFYI(1, "smb2 data length %d offset %d", data_length, offset);

	if (data_length > 0) {
		/* Check to make sure that data area begins after fixed area,
		   Note that last byte of the fixed area is part of data area
		   for some commands, typically those with odd StructureSize,
		   so we must add one to the calculation (and 4 to account for
		   the size of the RFC1001 hdr */
		if (offset + 4 + 1 < len) {
			cERROR(1, "data area overlaps SMB2 header, ignoring");
			data_length = 0;
		} else {
			len = 4 + offset + data_length;
		}
	}
calc_size_exit:
	cFYI(1, "smb2 len %d", len);
	return len;
}

