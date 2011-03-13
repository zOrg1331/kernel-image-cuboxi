/*
 *   fs/cifs/smb2pdu.h
 *
 *   Copyright (c) International Business Machines  Corp., 2009, 2010
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

#ifndef _SMB2PDU_H
#define _SMB2PDU_H

#include <net/sock.h>

#define SMB2_PORT 445
#define RFC1001_PORT 139

/*
 * Note that, due to trying to use names similar to the protocol specifications,
 * there are many mixed case field names in the structures below.  Although
 * this does not match typical Linux kernel style, it is necessary to be
 * be able to match against the protocol specfication.
 *
 * SMB2 commands
 * Some commands have minimal (wct=0,bcc=0), or uninteresting, responses
 * (ie no useful data other than the SMB error code itself) and are marked such
 * Knowing this helps avoid response buffer allocations and copy in some cases
 */

/* List is sent on wire as little endian */
#define SMB2_NEGOTIATE		cpu_to_le16(0x0000)
#define SMB2_SESSION_SETUP	cpu_to_le16(0x0001)
#define SMB2_LOGOFF		cpu_to_le16(0x0002) /* trivial request/resp */
#define SMB2_TREE_CONNECT	cpu_to_le16(0x0003)
#define SMB2_TREE_DISCONNECT	cpu_to_le16(0x0004) /* trivial req/resp */
#define SMB2_CREATE		cpu_to_le16(0x0005)
#define SMB2_CLOSE		cpu_to_le16(0x0006)
#define SMB2_FLUSH		cpu_to_le16(0x0007) /* trivial resp */
#define SMB2_READ		cpu_to_le16(0x0008)
#define SMB2_WRITE		cpu_to_le16(0x0009)
#define SMB2_LOCK		cpu_to_le16(0x000A)
#define SMB2_IOCTL		cpu_to_le16(0x000B)
#define SMB2_CANCEL		cpu_to_le16(0x000C)
#define SMB2_ECHO		cpu_to_le16(0x000D)
#define SMB2_QUERY_DIRECTORY	cpu_to_le16(0x000E)
#define SMB2_CHANGE_NOTIFY	cpu_to_le16(0x000F)
#define SMB2_QUERY_INFO		cpu_to_le16(0x0010)
#define SMB2_SET_INFO		cpu_to_le16(0x0011)
#define SMB2_OPLOCK_BREAK	cpu_to_le16(0x0012)

/* Same List of commands in host endian */
#define SMB2NEGOTIATE		0x0000
#define SMB2SESSION_SETUP	0x0001
#define SMB2LOGOFF		0x0002 /* trivial request/resp */
#define SMB2TREE_CONNECT	0x0003
#define SMB2TREE_DISCONNECT	0x0004 /* trivial req/resp */
#define SMB2CREATE		0x0005
#define SMB2CLOSE		0x0006
#define SMB2FLUSH		0x0007 /* trivial resp */
#define SMB2READ		0x0008
#define SMB2WRITE		0x0009
#define SMB2LOCK		0x000A
#define SMB2IOCTL		0x000B
#define SMB2CANCEL		0x000C
#define SMB2ECHO		0x000D
#define SMB2QUERY_DIRECTORY	0x000E
#define SMB2CHANGE_NOTIFY	0x000F
#define SMB2QUERY_INFO		0x0010
#define SMB2SET_INFO		0x0011
#define SMB2OPLOCK_BREAK	0x0012

#define NUMBER_OF_SMB2_COMMANDS	0x0013

/*  BB FIXME - analyze following three length fields BB */
#define MAX_SMB2_SMALL_BUFFER_SIZE 460 /* big enough for most */
#define MAX_SMB2_HDR_SIZE 0x78 /* 4 len + 64 hdr + (2*24 wct) + 2 bct + 2 pad */
#define SMB2_SMALL_PATH 112 /* allows for one fewer than (460-120)/3 */

/* File Attrubutes */

#define FILE_ATTRIBUTE_READONLY			0x00000001
#define FILE_ATTRIBUTE_HIDDEN			0x00000002
#define FILE_ATTRIBUTE_SYSTEM			0x00000004
#define FILE_ATTRIBUTE_DIRECTORY		0x00000010
#define FILE_ATTRIBUTE_ARCHIVE			0x00000020
#define FILE_ATTRIBUTE_NORMAL			0x00000080
#define FILE_ATTRIBUTE_TEMPORARY		0x00000100
#define FILE_ATTRIBUTE_SPARSE_FILE		0x00000200
#define FILE_ATTRIBUTE_REPARSE_POINT		0x00000400
#define FILE_ATTRIBUTE_COMPRESSED		0x00000800
#define FILE_ATTRIBUTE_OFFLINE			0x00001000
#define FILE_ATTRIBUTE_NOT_CONTENT_INDEXED	0x00002000
#define FILE_ATTRIBUTE_ENCRYPTED		0x00004000

/*
 * SMB2 flag definitions
 */

#define SMB2FLG_RESPONSE 0x0001    /* this PDU is a response from server */

/*
 *	SMB2 Header Definition
 *
 *	"MBZ" :  Must be Zero
 *      "BB"  :  BugBug, Something to check/review/analyze later
 *      "PDU" :  "Protocol Data Unit" (ie a network "frame")
 *
 */
struct smb2_hdr {
	__be32 smb2_buf_length;	/* big endian on wire */
				/* length is only two or three bytes - with
				 one or two byte type preceding it that MBZ */
	__u8   ProtocolId[4];	/* 0xFE 'S' 'M' 'B' */
	__le16 StructureSize;	/* 64 */
	__le16 CreditCharge;	/* MBZ */
	__le32 Status;		/* Error from server */
	__le16 Command;
	__le16 CreditRequest;  /* CreditResponse */
	__le32 Flags;
	__le32 NextCommand;
	__u64  MessageId;	/* opaque - so can stay little endian */
	__le32 ProcessId;
	__u32  TreeId;		/* opaque - so do not make little endian */
	__u64  SessionId;	/* opaque - so do not make little endian */
	__u8   Signature[16];
	/* Usually followed by __le16 StructureSize of request or response
	   structure which follows */
} __attribute__((packed));

struct smb2_async_hdr {
	__be32 smb2_buf_length;	/* big endian on wire */
				/* length is only two or three bytes - with
				 one or two byte type preceding it that MBZ */
	__u8   ProtocolId[4];	/* 0xFE 'S' 'M' 'B' */
	__le16 StructureSize;	/* 64 */
	__le16 CreditCharge;	/* MBZ */
	__le32 Status;		/* Error from server */
	__le16 Command;
	__le16 CreditResponse;
	__le32 Flags;
	__le32 NextCommand;
	__u64  MessageId;	/* opaque - so can stay little endian */
	__u64  AsyncId;
	__u64  SessionId;	/* opaque - so do not make little endian */
	__u8   Signature[16];
	/* Usually followed by __le16 StructureSize of request or response
	   structure which follows */
} __attribute__((packed));

struct smb2_pdu {
	struct smb2_hdr hdr;
	__le16 StructureSize2; /* size of wct area (varies, request specific) */
} __attribute__((packed));

/*
 *	SMB2 flag definitions
 */
#define SMB2_FLAGS_SERVER_TO_REDIR	cpu_to_le32(0x00000001) /* Response */
#define SMB2_FLAGS_ASYNC_COMMAND	cpu_to_le32(0x00000002)
#define SMB2_FLAGS_RELATED_OPERATIONS	cpu_to_le32(0x00000004)
#define SMB2_FLAGS_SIGNED		cpu_to_le32(0x00000008)
#define SMB2_FLAGS_DFS_OPERATIONS	cpu_to_le32(0x10000000)

/*
 *	Definitions for SMB2 Protocol Data Units (network frames)
 *
 *  See MS-SMB2.PDF specification for protocol details.
 *  The Naming convention is the lower case version of the SMB2
 *  command code name for the struct. Note that structures must be packed.
 *
 */
struct smb2_err_rsp {
	struct	smb2_hdr hdr;
	__le16	StructureSize;
	__le16	Reserved; /* MBZ */
	__le32	ByteCount;  /* even if zero, at least one byte follows */
	__u8	ErrorData[1];  /* variable length */
}  __attribute__((packed));

/* Symlink error response for error STATUS_STOPPED_ON_SYMLINK
   Following is the ErrorData structure */
struct symlink_err_data {
	__le32	SymLinkLength;
	__le32	SymLinkErrorTag;
	__le32	ReparseTag;
	__le16	ReparseDataLength;
	__le16	Reserved;	/* MBZ */
	__le16	SubstituteNameOffset;
	__le16	SubstituteNameLength;
	__le16	PrintNameOffset;
	__le16	PrintNameLength;
	__le32	Flags;
	__u8	PathBuffer[0]; /* variable length */
} __attribute__((packed));

struct smb2_negotiate_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize; /* Must be 36 */
	__le16 DialectCount;
	__le16 SecurityMode;
	__le16 Reserved;	/* MBZ */
	__le32 Capabilities;
	__u8   ClientGUID[16];	/* MBZ */
	__le64 ClientStartTime;	/* MBZ */
	__le16 Dialects[2]; /* variable length */ /* Must include 0x0202 */
} __attribute__((packed));
/* SecurityMode flags */
#define	SMB2_NEGOTIATE_SIGNING_ENABLED	0x0001
#define SMB2_NEGOTIATE_SIGNING_REQUIRED	0x0002
/* Capabilities flags */
#define SMB2_GLOBAL_CAP_DFS		0x00000001
#define SMB2_GLOBAL_CAP_LEASING		0x00000002 /* Resp only New to SMB2.1 */
#define SMB2_GLOBAL_CAP_LARGE_MTU	0X00000004 /* Resp only New to SMB2.1 */

struct smb2_negotiate_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 65 */
	__le16 SecurityMode;
	__le16 DialectRevision; /* Should be 0x0202 */
	__le16 Reserved;	/* MBZ */
	__u8   ServerGUID[16];
	__le32 Capabilities;
	__le32 MaxTransactSize;
	__le32 MaxReadSize;
	__le32 MaxWriteSize;
	__le64 SystemTime;	/* MBZ */
	__le64 ServerStartTime;
	__le16 SecurityBufferOffset;
	__le16 SecurityBufferLength;
	__le32 Reserved2;	/* may be any value, Ignore */
	__u8   Buffer[1];	/* variable length GSS security buffer */
} __attribute__((packed));

struct sess_setup_req {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 25 */
	__u8   VcNumber;
	__u8   SecurityMode;
	__le32 Capabilities;
	__le32 Channel;
	__le16 SecurityBufferOffset;
	__le16 SecurityBufferLength;
	__le64 PreviousSessionId;
	__u8   Buffer[1];	/* variable length GSS security buffer */
}  __attribute__((packed));

/* Currently defined SessionFlags */
#define SMB2_SESSION_FLAG_IS_GUEST	0x0001
#define SMB2_SESSION_FLAG_IS_NULL	0x0002
struct sess_setup_rsp {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 9 */
	__le16 SessionFlags;
	__le16 SecurityBufferOffset;
	__le16 SecurityBufferLength;
	__u8   Buffer[1];	/* variable length GSS security buffer */
}  __attribute__((packed));

struct logoff_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 4 */
	__le16 Reserved;
} __attribute__((packed));

struct logoff_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 4 */
	__le16 Reserved;
} __attribute__((packed));

struct tree_connect_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 9 */
	__le16 Reserved;
	__le16 PathOffset;
	__le16 PathLength;
	__u8   Buffer[1];	/* variable length */
} __attribute__((packed));

struct tree_connect_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 16 */
	__u8   ShareType;  /* see below */
	__u8   Reserved;
	__le32 ShareFlags; /* see below */
	__le32 Capabilities; /* see below */
	__le32 MaximalAccess;
} __attribute__((packed));

/* Possible ShareType values */
#define SMB2_SHARE_TYPE_DISK	0x01
#define SMB2_SHARE_TYPE_PIPE	0x02
#define	SMB2_SHARE_TYPE_PRINT	0x03

/* Possible ShareFlags - exactly one and only one of the first 4 caching flags
   must be set (any of the remaining, SHI1005, flags may be set individually
   or in combination */
#define SMB2_SHAREFLAG_MANUAL_CACHING			0x00000000
#define SMB2_SHAREFLAG_AUTO_CACHING			0x00000010
#define SMB2_SHAREFLAG_VDO_CACHING			0x00000020
#define SMB2_SHAREFLAG_NO_CACHING			0x00000030
#define SHI1005_FLAGS_DFS				0x00000001
#define SHI1005_FLAGS_DFS_ROOT				0x00000002
#define SHI1005_FLAGS_RESTRICT_EXCLUSIVE_OPENS		0x00000100
#define SHI1005_FLAGS_FORCE_SHARED_DELETE		0x00000200
#define SHI1005_FLAGS_ALLOW_NAMESPACE_CACHING		0x00000400
#define SHI1005_FLAGS_ACCESS_BASED_DIRECTORY_ENUM	0x00000800
#define SHI1005_FLAGS_FORCE_LEVELII_OPLOCK		0x00001000
#define SHI1005_FLAGS_ENABLE_HASH			0x00002000

/* Possible share capabilities */
#define SMB2_SHARE_CAP_DFS	cpu_to_le32(0x00000008)

struct tree_disconnect_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 4 */
	__le16 Reserved;
}  __attribute__((packed));

struct tree_disconnect_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 4 */
	__le16 Reserved;
}  __attribute__((packed));

/* Oplock levels */
#define SMB2_OPLOCK_LEVEL_NONE		0x00
#define SMB2_OPLOCK_LEVEL_II		0x01
#define SMB2_OPLOCK_LEVEL_EXCLUSIVE	0x08
#define SMB2_OPLOCK_LEVEL_BATCH		0x09
#define SMB2_OPLOCK_LEVEL_LEASE		0xFF

/* Desired Access Flags */
#define FILE_READ_DATA_LE		cpu_to_le32(0x00000001)
#define FILE_WRITE_DATA_LE		cpu_to_le32(0x00000002)
#define FILE_APPEND_DATA_LE		cpu_to_le32(0x00000004)
#define FILE_READ_EA_LE			cpu_to_le32(0x00000008)
#define FILE_WRITE_EA_LE		cpu_to_le32(0x00000010)
#define FILE_EXECUTE_LE			cpu_to_le32(0x00000020)
#define FILE_READ_ATTRIBUTES_LE		cpu_to_le32(0x00000080)
#define FILE_WRITE_ATTRIBUTES_LE	cpu_to_le32(0x00000100)
#define FILE_DELETE_LE			cpu_to_le32(0x00010000)
#define FILE_READ_CONTROL_LE		cpu_to_le32(0x00020000)
#define FILE_WRITE_DAC_LE		cpu_to_le32(0x00040000)
#define FILE_WRITE_OWNER_LE		cpu_to_le32(0x00080000)
#define FILE_SYNCHRONIZE_LE		cpu_to_le32(0x00100000)
#define FILE_ACCESS_SYSTEM_SECURITY_LE	cpu_to_le32(0x01000000)
#define FILE_MAXIMAL_ACCESS_LE		cpu_to_le32(0x02000000)
#define FILE_GENERIC_ALL_LE		cpu_to_le32(0x10000000)
#define FILE_GENERIC_EXECUTE_LE		cpu_to_le32(0x20000000)
#define FILE_GENERIC_WRITE_LE		cpu_to_le32(0x40000000)
#define FILE_GENERIC_READ_LE		cpu_to_le32(0x80000000)

/* ShareAccess Flags */
#define FILE_SHARE_READ_LE		cpu_to_le32(0x00000001)
#define FILE_SHARE_WRITE_LE		cpu_to_le32(0x00000002)
#define FILE_SHARE_DELETE_LE		cpu_to_le32(0x00000004)
#define FILE_SHARE_ALL_LE		cpu_to_le32(0x00000007)

/* CreateDisposition Flags */
#define FILE_SUPERSEDE_LE		cpu_to_le32(0x00000000)
#define FILE_OPEN_LE			cpu_to_le32(0x00000001)
#define FILE_CREATE_LE			cpu_to_le32(0x00000002)
#define	FILE_OPEN_IF_LE			cpu_to_le32(0x00000003)
#define FILE_OVERWRITE_LE		cpu_to_le32(0x00000004)
#define FILE_OVERWRITE_IF_LE		cpu_to_le32(0x00000005)

/* CreateOptions Flags */
#define FILE_DIRECTORY_FILE_LE		cpu_to_le32(0x00000001)
#define FILE_WRITE_THROUGH_LE		cpu_to_le32(0x00000002)
#define FILE_SEQUENTIAL_ONLY_LE		cpu_to_le32(0x00000004)
#define FILE_NO_INTERMEDIATE_BUFFERRING_LE cpu_to_le32(0x00000008)
#define FILE_SYNCHRONOUS_IO_ALERT_LE	cpu_to_le32(0x00000010)
#define FILE_SYNCHRONOUS_IO_NON_ALERT_LE	cpu_to_le32(0x00000020)
#define FILE_NON_DIRECTORY_FILE_LE	cpu_to_le32(0x00000040)
#define FILE_COMPLETE_IF_OPLOCKED_LE	cpu_to_le32(0x00000100)
#define FILE_NO_EA_KNOWLEDGE_LE		cpu_to_le32(0x00000200)
#define FILE_RANDOM_ACCESS_LE		cpu_to_le32(0x00000800)
#define FILE_DELETE_ON_CLOSE_LE		cpu_to_le32(0x00001000)
#define FILE_OPEN_BY_FILE_ID_LE		cpu_to_le32(0x00002000)
#define FILE_OPEN_FOR_BACKUP_INTENT_LE	cpu_to_le32(0x00004000)
#define FILE_NO_COMPRESSION_LE		cpu_to_le32(0x00008000)
#define FILE_RESERVE_OPFILTER_LE	cpu_to_le32(0x00100000)
#define FILE_OPEN_REPARSE_POINT_LE	cpu_to_le32(0x00200000)
#define FILE_OPEN_NO_RECALL_LE		cpu_to_le32(0x00400000)
#define FILE_OPEN_FOR_FREE_SPACE_QUERY_LE cpu_to_le32(0x00800000)

#define FILE_READ_RIGHTS_LE (FILE_READ_DATA_LE | FILE_READ_EA_LE \
			| FILE_READ_ATTRIBUTES_LE)
#define FILE_WRITE_RIGHTS_LE (FILE_WRITE_DATA_LE | FILE_APPEND_DATA_LE \
			| FILE_WRITE_EA_LE | FILE_WRITE_ATTRIBUTES_LE)
#define FILE_EXEC_RIGHTS_LE (FILE_EXECUTE_LE)

/* Impersonation Levels */
#define IL_ANONYMOUS		cpu_to_le32(0x00000000)
#define IL_IDENTIFICATION	cpu_to_le32(0x00000001)
#define IL_IMPERSONATION	cpu_to_le32(0x00000002)
#define IL_DELEGATE		cpu_to_le32(0x00000003)

/* Create Context Values */
#define SMB2_CREATE_EA_BUFFER			"ExtA" /* extended attributes */
#define SMB2_CREATE_SD_BUFFER			"SecD" /* security descriptor */
#define SMB2_CREATE_DURABLE_HANDLE_REQUEST	"DHnQ"
#define SMB2_CREATE_DURABLE_HANDLE_RECONNECT	"DHnC"
#define SMB2_CREATE_ALLOCATION_SIZE		"AlSi"
#define SMB2_CREATE_QUERY_MAXIMAL_ACCESS_REQUEST "MxAc"
#define SMB2_CREATE_TIMEWARP_REQUEST		"TWrp"
#define SMB2_CREATE_QUERY_ON_DISK_ID		"QFid"
#define SMB2_CREATE_REQUEST_LEASE		"RqLs"

struct create_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 57 */
	__u8   SecurityFlags;
	__u8   RequestedOplockLevel;
	__le32 ImpersonationLevel;
	__le64 SmbCreateFlags;
	__le64 Reserved;
	__le32 DesiredAccess;
	__le32 FileAttributes;
	__le32 ShareAccess;
	__le32 CreateDisposition;
	__le32 CreateOptions;
	__le16 NameOffset;
	__le16 NameLength;
	__le32 CreateContextsOffset;
	__le32 CreateContextsLength;
	__u8    Buffer[1];
}  __attribute__((packed));

struct create_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 89 */
	__u8   OplockLevel;
	__u8   Reserved;
	__le32 CreateAction;
	__le64 CreationTime;
	__le64 LastAccessTime;
	__le64 LastWriteTime;
	__le64 ChangeTime;
	__le64 AllocationSize;
	__le64 EndofFile;
	__le32 FileAttributes;
	__le32 Reserved2;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
	__le32 CreateContextsOffset;
	__le32 CreateContextsLength;
	__u8   Buffer[1];
}  __attribute__((packed));

/* Currently defined values for close flags */
#define SMB2_CLOSE_FLAG_POSTQUERY_ATTRIB	cpu_to_le16(0x0001)
struct close_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 24 */
	__le16 Flags;
	__le32 Reserved;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
}  __attribute__((packed));

struct close_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize; /* 60 */
	__le16 Flags;
	__le32 Reserved;
	__le64 CreationTime;
	__le64 LastAccessTime;
	__le64 LastWriteTime;
	__le64 ChangeTime;
	__le64 AllocationSize;	/* Beginning of FILE_STANDARD_INFO equivalent */
	__le64 EndOfFile;
	__le32 Attributes;
} __attribute__((packed));

struct flush_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 24 */
	__le16 Reserved1;
	__le32 Reserved2;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
}  __attribute__((packed));

struct flush_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;
	__le16 Reserved;
} __attribute__((packed));

struct read_req {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 49 */
	__u8   Padding; /* offset from start of SMB2 header to place read */
	__u8   Reserved;
	__le32 Length;
	__le64 Offset;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
	__le32 MinimumCount;
	__le32 Channel; /* Reserved MBZ */
	__le32 RemainingBytes;
	__le16 ReadChannelInfoOffset; /* Reserved MBZ */
	__le16 ReadChannelInfoLength; /* Reserved MBZ */
	__u8   Buffer[1];
} __attribute__((packed));

struct read_rsp {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 17 */
	__u8   DataOffset;
	__u8   Reserved;
	__le32 DataLength;
	__le32 DataRemaining;
	__u32  Reserved2;
	__u8   Buffer[1];
} __attribute__((packed));

/* For write request Flags field below the following flag is defined: */
#define SMB2_WRITEFLAG_WRITE_THROUGH 0x00000001

struct write_req {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 49 */
	__le16 DataOffset; /* offset from start of SMB2 header to write data */
	__le32 Length;
	__le64 Offset;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
	__le32 Channel; /* Reserved MBZ */
	__le32 RemainingBytes;
	__le16 WriteChannelInfoOffset; /* Reserved MBZ */
	__le16 WriteChannelInfoLength; /* Reserved MBZ */
	__le32 Flags;
	__u8   Buffer[1];
} __attribute__((packed));

struct write_rsp {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 17 */
	__u8   DataOffset;
	__u8   Reserved;
	__le32 DataLength;
	__le32 DataRemaining;
	__u32  Reserved2;
	__u8   Buffer[1];
} __attribute__((packed));

#define SMB2_LOCKFLAG_SHARED_LOCK	0x0001
#define SMB2_LOCKFLAG_EXCLUSIVE_LOCK	0x0002
#define SMB2_LOCKFLAG_UNLOCK		0x0004
#define SMB2_LOCKFLAG_FAIL_IMMEDIATELY	0x0010

struct smb2_lock_element {
	__le64 Offset;
	__le64 Length;
	__le16 Flags;
	__le16 Reserved;
} __attribute__((packed));

#define LOCKING_ANDX_OPLOCK_RELEASE  0x02

struct smb2_lock_req {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 48 */
	__le16 LockCount;
	__le32 Reserved;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
	/* Followed by at least one */
	struct smb2_lock_element locks[1];
} __attribute__((packed));

struct smb2_lock_rsp {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 4 */
	__le16 Reserved;
} __attribute__((packed));

struct echo_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 4 */
	__u16  Reserved;
} __attribute__((packed));

struct echo_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 4 */
	__u16  Reserved;
} __attribute__((packed));

/* search (query_directory) Flags field */
#define SMB2_RESTART_SCANS		0x01
#define SMB2_RETURN_SINGLE_ENTRY	0x02
#define SMB2_INDEX_SPECIFIED		0x04
#define SMB2_REOPEN			0x10

struct query_directory_req {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 33 */
	__u8 FileInformationClass;
	__u8 Flags;
	__le32 FileIndex;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
	__le16 FileNameOffset;
	__le16 FileNameLength;
	__le32 OutputBufferLength;
	__u8   Buffer[1];
} __attribute__((packed));

struct query_directory_rsp {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 9 */
	__le16 OutputBufferOffset;
	__le32 OutputBufferLength;
	__u8   Buffer[1];
} __attribute__((packed));

/* Possible InfoType values */
#define SMB2_O_INFO_FILE	0x01
#define SMB2_O_INFO_FILESYSTEM	0x02
#define SMB2_O_INFO_SECURITY	0x03
#define SMB2_O_INFO_QUOTA	0x04

struct query_info_req {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 41 */
	__u8 InfoType;
	__u8 FileInfoClass;
	__le32 OutputBufferLength;
	__le16 InputBufferOffset;
	__u16  Reserved;
	__le32 InputBufferLength;
	__le32 AdditionalInformation;
	__le32 Flags;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
	__u8   Buffer[1];
} __attribute__((packed));

struct query_info_rsp {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 9 */
	__le16 OutputBufferOffset;
	__le32 OutputBufferLength;
	__u8   Buffer[1];
} __attribute__((packed));

struct set_info_req {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 33 */
	__u8 InfoType;
	__u8 FileInfoClass;
	__le32 BufferLength;
	__le16 BufferOffset;
	__u16 Reserved;
	__le32 AdditionalInformation;
	__u64  PersistentFileId; /* opaque endianness */
	__u64  VolatileFileId; /* opaque endianness */
	__u8 Buffer[1];
} __attribute__((packed));

struct set_info_rsp {
	struct smb2_hdr hdr;
	__le16 StructureSize; /* Must be 2 */
} __attribute__((packed));

struct ioctl_req {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 57 */
	__le16 Reserved;
	__le32 Ctlcode;
	__u64 Fileid[2];	/* persistent and volatile */
	__le32 Inputoffset;
	__le32 Inputcount;
	__le32 Maxinputresp;
	__le32 Outputoffset;
	__le32 Outputcount;
	__le32 Maxoutputresp;
	__le32 Flags;
	__le32 Reserved2;
	__u8   Buffer[1];
}  __attribute__((packed));

struct ioctl_rsp {
	struct	smb2_hdr hdr;
	__le16 StructureSize;	/* Must be 49 */
	__le16 Reserved;
	__le32 Ctlcode;
	__u64 Fileid[2];	/* persistent and volatile */
	__le32 Inputoffset;
	__le32 Inputcount;
	__le32 Outputoffset;
	__le32 Outputcount;
	__le32 Flags;
	__le32 Reserved2;
	__u8   Buffer[1];
}  __attribute__((packed));

/*****************************************************************
 * All constants go here
 *****************************************************************
 */

/*
 * Starting value for maximum SMB size negotiation
 */
#define SMB2_MAX_MSGSIZE (4*4096)


#define SMB2_NETWORK_OPSYS "SMB2 VFS Client for Linux"

/*
 *	PDU infolevel structure definitions
 *	BB consider moving to a different header
 */

/* File System Information Classes */
#define FS_VOLUME_INFORMATION	1 /* Query */
#define FS_LABEL_INFORMATION	2 /* Set */
#define FS_SIZE_INFORMATION	3 /* Query */
#define FS_DEVICE_INFORMATION	4 /* Query */
#define FS_ATTRIBUTE_INFORMATION 5 /* Query */
#define FS_CONTROL_INFORMATION	6 /* Query, Set */
#define FS_FULL_SIZE_INFORMATION 7 /* Query */
#define FS_OBJECT_ID_INFORMATION 8 /* Query, Set */
#define FS_DRIVER_PATH_INFORMATION 9 /* Query */

struct fs_full_size_info {
	__le64 TotalAllocationUnits;
	__le64 CallerAvailableAllocationUnits;
	__le64 ActualAvailableAllocationUnits;
	__le32 SectorsPerAllocationUnit;
	__le32 BytesPerSector;
};

struct fs_volume_info {
	__le64 VolumeCreationTime;
	__le32 VolumeSerialNumber;
	__le32 VolumeLabelLength;
	__u8   SupportsObjects;  /* 1 = supports object oriented fs objects */
	__u8   Reserved;
	/* Variable Length VolumeLabel follows */
};

struct fs_device_info {
	__le32 DeviceType; /* see below */
	__le32 DeviceCharacteristics;
} __attribute__((packed)); /* device info level 0x104 */

/* DeviceType Flags (remember to endian convert them) */
#define FILE_DEVICE_CD_ROM              0x00000002
#define FILE_DEVICE_CD_ROM_FILE_SYSTEM  0x00000003
#define FILE_DEVICE_DFS                 0x00000006
#define FILE_DEVICE_DISK                0x00000007
#define FILE_DEVICE_DISK_FILE_SYSTEM    0x00000008
#define FILE_DEVICE_FILE_SYSTEM         0x00000009
#define FILE_DEVICE_NAMED_PIPE          0x00000011
#define FILE_DEVICE_NETWORK             0x00000012
#define FILE_DEVICE_NETWORK_FILE_SYSTEM 0x00000014
#define FILE_DEVICE_NULL                0x00000015
#define FILE_DEVICE_PARALLEL_PORT       0x00000016
#define FILE_DEVICE_PRINTER             0x00000018
#define FILE_DEVICE_SERIAL_PORT         0x0000001b
#define FILE_DEVICE_STREAMS             0x0000001e
#define FILE_DEVICE_TAPE                0x0000001f
#define FILE_DEVICE_TAPE_FILE_SYSTEM    0x00000020
#define FILE_DEVICE_VIRTUAL_DISK        0x00000024
#define FILE_DEVICE_NETWORK_REDIRECTOR  0x00000028

#define MAX_FS_NAME 20 /* twice size of longest name ("FAT32") is plenty */
/* this field is for debugging/informational purposes anyway, so could be
truncated if extremely long fs names were later created */
struct fs_attribute_info {
	__le32 Attributes;
	__le32 MaximumComponentNameLength;
	__le32 FileSystemNameLength;
	char FileSystemName[MAX_FS_NAME]; /* not null terminated */
} __attribute__((packed));

/* Attributes  (remember to endian convert them) */
#define FILE_CASE_SENSITIVE_SEARCH	0x00000001
#define FILE_CASE_PRESERVED_NAMES	0x00000002
#define FILE_UNICODE_ON_DISK		0x00000004
#define FILE_PERSISTENT_ACLS		0x00000008
#define FILE_FILE_COMPRESSION		0x00000010
#define FILE_VOLUME_QUOTAS		0x00000020
#define FILE_SUPPORTS_SPARSE_FILES	0x00000040
#define FILE_SUPPORTS_REPARSE_POINTS	0x00000080
#define FILE_SUPPORTS_REMOTE_STORAGE	0x00000100
#define FILE_VOLUME_IS_COMPRESSED	0x00008000
#define FILE_SUPPORTS_OBJECT_IDS	0x00010000
#define FILE_SUPPORTS_ENCRYPTION	0x00020000
#define FILE_NAMED_STREAMS		0x00040000
#define FILE_READ_ONLY_VOLUME		0x00080000
#define FILE_SEQUENTIAL_WRITE_ONCE	0x00100000
#define FILE_SUPPORTS_TRANSACTIONS	0x00200000
#define FILE_SUPPORTS_HARD_LINKS	0x00400000
#define FILE_SUPPORTS_EXTENDED_ATTRS	0x00800000
#define FILE_SUPPORTS_OPEN_BY_FILE_ID	0x01000000
#define FILE_SUPPORTS_USN_JOURNAL	0x02000000

/* partial list of QUERY INFO levels */
#define FILE_DIRECTORY_INFORMATION	1
#define FILE_FULL_DIRECTORY_INFORMATION 2
#define FILE_BOTH_DIRECTORY_INFORMATION 3
#define FILE_BASIC_INFORMATION		4
#define FILE_STANDARD_INFORMATION	5
#define FILE_INTERNAL_INFORMATION	6
#define FILE_EA_INFORMATION	        7
#define FILE_ACCESS_INFORMATION		8
#define FILE_NAME_INFORMATION		9
#define FILE_RENAME_INFORMATION		10
#define FILE_LINK_INFORMATION		11
#define FILE_NAMES_INFORMATION		12
#define FILE_DISPOSITION_INFORMATION	13
#define FILE_POSITION_INFORMATION	14
#define FILE_FULL_EA_INFORMATION	15
#define FILE_MODE_INFORMATION		16
#define FILE_ALIGNMENT_INFORMATION	17
#define FILE_ALL_INFORMATION		18
#define FILE_ALLOCATION_INFORMATION	19
#define FILE_END_OF_FILE_INFORMATION	20
#define FILE_ALTERNATE_NAME_INFORMATION 21
#define FILE_STREAM_INFORMATION		22
#define FILE_PIPE_INFORMATION		23
#define FILE_PIPE_LOCAL_INFORMATION	24
#define FILE_PIPE_REMOTE_INFORMATION	25
#define FILE_MAILSLOT_QUERY_INFORMATION 26
#define FILE_MAILSLOT_SET_INFORMATION	27
#define FILE_COMPRESSION_INFORMATION	28
#define FILE_OBJECT_ID_INFORMATION	29
/* Number 30 not defined in documents */
#define FILE_MOVE_CLUSTER_INFORMATION	31
#define FILE_QUOTA_INFORMATION		32
#define FILE_REPARSE_POINT_INFORMATION	33
#define FILE_NETWORK_OPEN_INFORMATION	34
#define FILE_ATTRIBUTE_TAG_INFORMATION	35
#define FILE_TRACKING_INFORMATION	36
#define FILEID_BOTH_DIRECTORY_INFORMATION 37
#define FILEID_FULL_DIRECTORY_INFORMATION 38
#define FILE_VALID_DATA_LENGTH_INFORMATION 39
#define FILE_SHORT_NAME_INFORMATION	40
#define FILE_SFIO_RESERVE_INFORMATION	44
#define FILE_SFIO_VOLUME_INFORMATION	45
#define FILE_HARD_LINK_INFORMATION	46
#define FILE_NORMALIZED_NAME_INFORMATION 48
#define FILEID_GLOBAL_TX_DIRECTORY_INFORMATION 50
#define FILE_STANDARD_LINK_INFORMATION	54

struct file_both_directory_info {
	__le32 next_entry_offset;
	__u32 file_index;
	__le64 creation_time;
	__le64 last_access_time;
	__le64 last_write_time;
	__le64 change_time;
	__le64 end_of_file;
	__le64 allocation_size;
	__le32 file_attribute;
	__le32 filename_length;
	__le32 easize;
	__u8 shortname_length;
	__u8 reserved1;
	__u8 short_name[24];
	__u16 reserved2;
	__le64 file_id;
	char filename[0];
}  __attribute__((packed));

struct file_full_directory_info {
	__le32 next_entry_offset;
	__u32 file_index;
	__le64 creation_time;
	__le64 last_access_time;
	__le64 last_write_time;
	__le64 change_time;
	__le64 end_of_file;
	__le64 allocation_size;
	__le32 file_attribute;
	__le32 filename_length;
	__le32 easize;
	__u32 reserved2;
	__le64 file_id;
	char filename[0];
}  __attribute__((packed));

typedef struct { /* data block encoding of response to level 5 query */
	__le64 AllocationSize;
	__le64 EndOfFile;	/* size ie offset to first free byte in file */
	__le32 NumberOfLinks;	/* hard links */
	__u8 DeletePending;
	__u8 Directory;
	__u16 Pad2;
} __attribute__((packed)) FILE_STANDARD_INFO;	/* level 5 QPathInfo */

struct FileRenameInformation { /* encoding of request for level 10 */
	__u8 ReplaceIfExists; /* 1 = replace existing file with new */
			      /* 0 = fail if target file already exists */
	__u8 Reserved[7];
	__u64 RootDirectory;  /* MBZ for network operations (why says spec?) */
	__le32 FileNameLength;
	char FileName[0];     /* New name to be assigned */
} __attribute__((packed)); /* level 10 set */

struct FileLinkInformation { /* encoding of request for level 11 */
	__u8 ReplaceIfExists; /* 1 = replace existing link with new */
			      /* 0 = fail if link already exists */
	__u8 Reserved[7];
	__u64 RootDirectory;  /* MBZ for network operations (why says spec?) */
	__le32 FileNameLength;
	char FileName[0];     /* Name to be assigned to new link */
} __attribute__((packed)); /* level 11 set */


/* This level 18, although with struct with same name is different from cifs
   level 0x107.  level 0x107 has an extra u64 between AccessFlags and
   CurrentByteOffset */
typedef struct { /* data block encoding of response to level 18 */
	__le64 CreationTime;	/* Beginning of FILE_BASIC_INFO equivalent */
	__le64 LastAccessTime;
	__le64 LastWriteTime;
	__le64 ChangeTime;
	__le32 Attributes;
	__u32 Pad1;		/* End of FILE_BASIC_INFO_INFO equivalent */
	__le64 AllocationSize;	/* Beginning of FILE_STANDARD_INFO equivalent */
	__le64 EndOfFile;	/* size ie offset to first free byte in file */
	__le32 NumberOfLinks;	/* hard links */
	__u8 DeletePending;
	__u8 Directory;
	__u16 Pad2;		/* End of FILE_STANDARD_INFO equivalent */
	__le64 IndexNumber;
	__le32 EASize;
	__le32 AccessFlags;
	__le64 CurrentByteOffset;
	__le32 Mode;
	__le32 AlignmentRequirement;
	__le32 FileNameLength;
	char FileName[1];
} __attribute__((packed)) FILE_ALL_INFO_SMB2;	/* level 18 Query */

typedef struct { /* data block encoding of request to level 15 */
	__le64 NextEntryOffset;
	__u8 EaNameLength;
	char EaName[1];
} __attribute__((packed)) FILE_GET_EA_INFO; /* level 15 Query */

typedef struct { /* data block encoding of response to level 15 */
	__le32 NextEntryOffset;
	__u8 Flags;
	__u8 EaNameLength;
	__le16 EaValueLength;
	char EaName[1];
	char EaValue[1];
} __attribute__((packed)) FILE_FULL_EA_INFO; /* level 15 Query */

/* DFS Flags */  /* BB check if these changed in SMB2 from old transact2
   get DFS referral flags BB */
#define DFSREF_REFERRAL_SERVER  0x00000001 /* all targets are DFS roots */
#define DFSREF_STORAGE_SERVER   0x00000002 /* no further ref requests needed */
#define DFSREF_TARGET_FAILBACK  0x00000004 /* only for DFS referral version 4 */

/* BB note that various other infolevels are defined in cifspdu.h, although most
   are obsolete now (for SMB2) or unneeded, some may be useful to move here */

#define SMB2_IOCTL_IS_FSCTL 0x1
#define SYMLINK_FLAG_RELATIVE 0x1
#define MS_REPARSE_TAG 0xA000000C

struct symlink_reparse_data_buf {
	__le32 reparse_tag;
	__le16 reparse_datalength;
	__le16 reserved1;
	__le16 sub_nameoffset;
	__le16 sub_namelength;
	__le16 print_nameoffset;
	__le16 print_namelength;
	__le32 flags;
	char pathbuffer[1];
} __attribute__((packed));

#endif				/* _SMB2PDU_H */
