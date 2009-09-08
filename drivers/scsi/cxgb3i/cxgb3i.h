/*
 * cxgb3i.h: Chelsio S3xx iSCSI driver.
 *
 * Copyright (c) 2008 Chelsio Communications, Inc.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation.
 *
 * Written by: Karen Xie (kxie@chelsio.com)
 */

#ifndef __CXGB3I_H__
#define __CXGB3I_H__

#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/errno.h>
#include <linux/types.h>
#include <linux/list.h>
#include <linux/netdevice.h>
#include <linux/scatterlist.h>

/* from cxgb3 LLD */
#include "common.h"
#include "t3_cpl.h"
#include "t3cdev.h"
#include "cxgb3_ctl_defs.h"
#include "cxgb3_offload.h"
#include "firmware_exports.h"
#include "cxgb3i_offload.h"
/* from iscsi */
#include "../iscsi_tcp.h"

#define CXGB3I_SCSI_QDEPTH_DFLT	128
#define CXGB3I_MAX_TARGET	CXGB3I_MAX_CONN
#define CXGB3I_MAX_LUN		512
#define ISCSI_PDU_HEADER_MAX	(56 + 256) /* bhs + digests + ahs */
#define ULP2_MAX_PKT_SIZE		16224
#define ISCSI_PDU_NONPAYLOAD_MAX  \
	(sizeof(struct iscsi_hdr) + ISCSI_MAX_AHS_SIZE + 2*ISCSI_DIGEST_SIZE)
#define ULP2_MAX_PDU_PAYLOAD \
	(ULP2_MAX_PKT_SIZE - ISCSI_PDU_NONPAYLOAD_MAX)


struct cxgb3i_adapter;
struct cxgb3i_hba;
struct cxgb3i_endpoint;

/**
 * struct cxgb3i_tag_format - cxgb3i ulp tag for steering pdu payload
 *
 * @idx_bits:	# of bits used to store itt (from iscsi laryer)
 * @age_bits:	# of bits used to store age (from iscsi laryer)
 * @rsvd_bits:	# of bits used by h/w
 * @rsvd_shift:	shift left
 * @rsvd_mask:  bit mask
 * @rsvd_tag_mask:  h/w tag bit mask
 *
 */
struct cxgb3i_tag_format {
	unsigned char sw_bits;
	unsigned char rsvd_bits;
	unsigned char rsvd_shift;
	unsigned char filler[1];
	u32 rsvd_mask;
};

/**
 * struct cxgb3i_gather_list - cxgb3i direct data placement memory
 *
 * @tag:	ddp tag
 * @length:	total data buffer length
 * @offset:	initial offset to the 1st page
 * @nelem:	# of pages
 * @pages:	pages
 * @phys_addr:	physical address
 */
struct cxgb3i_gather_list {
	u32 tag;
	unsigned int length;
	unsigned int offset;
	unsigned int nelem;
	struct page **pages;
	dma_addr_t phys_addr[0];
};

/**
 * struct cxgb3i_ddp_info - cxgb3i direct data placement for pdu payload
 *
 * @llimit:	lower bound of the page pod memory
 * @ulimit:	upper bound of the page pod memory
 * @nppods:	# of page pod entries
 * @idx_last:	page pod entry last used
 * @map_lock:	lock to synchonize access to the page pod map
 * @map:	page pod map
 */
struct cxgb3i_ddp_info {
	unsigned int llimit;
	unsigned int ulimit;
	unsigned int nppods;
	unsigned int idx_last;
	unsigned char idx_bits;
	unsigned char filler[3];
	u32 idx_mask;
	u32 rsvd_tag_mask;
	spinlock_t map_lock;
	struct cxgb3i_gather_list **gl_map;
	struct sk_buff **gl_skb;
};

/*
 * cxgb3i ddp tag are 32 bits, it consists of reserved bits used by h/w and
 * non-reserved bits that can be used by the iscsi s/w.
 * The reserved bits are identified by the rsvd_bits and rsvd_shift fields
 * in struct cxgb3i_tag_format.
 *
 * The upper most reserved bit can be used to check if a tag is ddp tag or not:
 * 	if the bit is 0, the tag is a valid ddp tag
 */

/**
 * cxgb3i_is_ddp_tag - check if a given tag is a hw/ddp tag
 * @tformat: tag format information
 * @tag: tag to be checked
 *
 * return true if the tag is a ddp tag, false otherwise.
 */
static inline int cxgb3i_is_ddp_tag(struct cxgb3i_tag_format *tformat, u32 tag)
{
	return !(tag & (1 << (tformat->rsvd_bits + tformat->rsvd_shift - 1)));
}

/**
 * cxgb3i_sw_tag_usable - check if a given s/w tag has enough bits left for
 *			  the reserved/hw bits
 * @tformat: tag format information
 * @sw_tag: s/w tag to be checked
 *
 * return true if the tag is a ddp tag, false otherwise.
 */
static inline int cxgb3i_sw_tag_usable(struct cxgb3i_tag_format *tformat,
					u32 sw_tag)
{
	sw_tag >>= (32 - tformat->rsvd_bits);
	return !sw_tag;
}

/**
 * cxgb3i_set_non_ddp_tag - mark a given s/w tag as an invalid ddp tag
 * @tformat: tag format information
 * @sw_tag: s/w tag to be checked
 *
 * insert 1 at the upper most reserved bit to mark it as an invalid ddp tag.
 */
static inline u32 cxgb3i_set_non_ddp_tag(struct cxgb3i_tag_format *tformat,
					 u32 sw_tag)
{
	unsigned char shift = tformat->rsvd_bits + tformat->rsvd_shift - 1;
	u32 mask = (1 << shift) - 1;

	if (sw_tag && (sw_tag & ~mask)) {
		u32 v1 = sw_tag & ((1 << shift) - 1);
		u32 v2 = (sw_tag >> (shift - 1)) << shift;

		return v2 | v1 | 1 << shift;
	}
	return sw_tag | 1 << shift;
}

/**
 * cxgb3i_ddp_tag_base - shift the s/w tag bits so that reserved bits are not
 *			 used.
 * @tformat: tag format information
 * @sw_tag: s/w tag to be checked
 */
static inline u32 cxgb3i_ddp_tag_base(struct cxgb3i_tag_format *tformat,
				      u32 sw_tag)
{
	u32 mask = (1 << tformat->rsvd_shift) - 1;

	if (sw_tag && (sw_tag & ~mask)) {
		u32 v1 = sw_tag & mask;
		u32 v2 = sw_tag >> tformat->rsvd_shift;

		v2 <<= tformat->rsvd_shift + tformat->rsvd_bits;
		return v2 | v1;
	}
	return sw_tag;
}

/**
 * cxgb3i_tag_rsvd_bits - get the reserved bits used by the h/w
 * @tformat: tag format information
 * @tag: tag to be checked
 *
 * return the reserved bits in the tag
 */
static inline u32 cxgb3i_tag_rsvd_bits(struct cxgb3i_tag_format *tformat,
				       u32 tag)
{
	if (cxgb3i_is_ddp_tag(tformat, tag))
		return (tag >> tformat->rsvd_shift) & tformat->rsvd_mask;
	return 0;
}

/**
 * cxgb3i_tag_nonrsvd_bits - get the non-reserved bits used by the s/w
 * @tformat: tag format information
 * @tag: tag to be checked
 *
 * return the non-reserved bits in the tag.
 */
static inline u32 cxgb3i_tag_nonrsvd_bits(struct cxgb3i_tag_format *tformat,
					  u32 tag)
{
	unsigned char shift = tformat->rsvd_bits + tformat->rsvd_shift - 1;
	u32 v1, v2;

	if (cxgb3i_is_ddp_tag(tformat, tag)) {
		v1 = tag & ((1 << tformat->rsvd_shift) - 1);
		v2 = (tag >> (shift + 1)) << tformat->rsvd_shift;
	} else {
		u32 mask = (1 << shift) - 1;

		tag &= ~(1 << shift);
		v1 = tag & mask;
		v2 = (tag >> 1) & ~mask;
	}
	return v1 | v2;
}


/**
 * struct cxgb3i_hba - cxgb3i iscsi structure (per port)
 *
 * @snic:	cxgb3i adapter containing this port
 * @ndev:	pointer to netdev structure
 * @shost:	pointer to scsi host structure
 */
struct cxgb3i_hba {
	struct cxgb3i_adapter *snic;
	struct net_device *ndev;
	struct Scsi_Host *shost;
};

/**
 * struct cxgb3i_adapter - cxgb3i adapter structure (per pci)
 *
 * @listhead:	list head to link elements
 * @lock:	lock for this structure
 * @tdev:	pointer to t3cdev used by cxgb3 driver
 * @pdev:	pointer to pci dev
 * @hba_cnt:	# of hbas (the same as # of ports)
 * @hba:	all the hbas on this adapter
 * @tx_max_size: max. tx packet size supported
 * @rx_max_size: max. rx packet size supported
 * @tag_format: ulp tag format settings
 * @ddp:	ulp ddp state
 */
struct cxgb3i_adapter {
	struct list_head list_head;
	spinlock_t lock;
	struct t3cdev *tdev;
	struct pci_dev *pdev;
	unsigned char hba_cnt;
	struct cxgb3i_hba *hba[MAX_NPORTS];

	unsigned int tx_max_size;
	unsigned int rx_max_size;

	struct cxgb3i_tag_format tag_format;
	struct cxgb3i_ddp_info *ddp;
};

/**
 * struct cxgb3i_conn - cxgb3i iscsi connection
 *
 * @tcp_conn:	pointer to iscsi_tcp_conn structure
 * @list_head:	list head to link elements
 * @cep:	pointer to iscsi_endpoint structure
 * @conn:	pointer to iscsi_conn structure
 * @hba:	pointer to the hba this conn. is going through
 * @task_idx_bits: # of bits needed for session->cmds_max
 * @frags:	temp. holding area for tx coalesced sg list pages.
 */
#define TX_PDU_PAGES_MAX   (16384/512 + 1)
struct cxgb3i_conn {
	struct iscsi_tcp_conn tcp_conn;
	struct list_head list_head;
	struct cxgb3i_endpoint *cep;
	struct iscsi_conn *conn;
	struct cxgb3i_hba *hba;
	unsigned int task_idx_bits;
	skb_frag_t frags[TX_PDU_PAGES_MAX];
};

/**
 * struct cxgb3i_endpoint - iscsi tcp endpoint
 *
 * @c3cn:	the h/w tcp connection representation
 * @hba:	pointer to the hba this conn. is going through
 * @cconn:	pointer to the associated cxgb3i iscsi connection
 */
struct cxgb3i_endpoint {
	struct s3_conn *c3cn;
	struct cxgb3i_hba *hba;
	struct cxgb3i_conn *cconn;
};

/*
 * Function Prototypes
 */
int cxgb3i_iscsi_init(void);
void cxgb3i_iscsi_cleanup(void);

struct cxgb3i_adapter *cxgb3i_adapter_add(struct t3cdev *);
void cxgb3i_adapter_remove(struct t3cdev *);
int cxgb3i_adapter_ulp_init(struct cxgb3i_adapter *);
void cxgb3i_adapter_ulp_cleanup(struct cxgb3i_adapter *);

struct cxgb3i_hba *cxgb3i_hba_find_by_netdev(struct net_device *);
struct cxgb3i_hba *cxgb3i_hba_host_add(struct cxgb3i_adapter *,
				       struct net_device *);
void cxgb3i_hba_host_remove(struct cxgb3i_hba *);

int cxgb3i_ulp2_init(void);
void cxgb3i_ulp2_cleanup(void);
int cxgb3i_conn_ulp_setup(struct cxgb3i_conn *, int, int);
void cxgb3i_ddp_tag_release(struct cxgb3i_adapter *, u32);
u32 cxgb3i_ddp_tag_reserve(struct cxgb3i_adapter *, unsigned int,
			   u32, unsigned int, struct scatterlist *,
			   unsigned int, int);
int cxgb3i_conn_ulp2_xmit(struct iscsi_conn *);
#endif
