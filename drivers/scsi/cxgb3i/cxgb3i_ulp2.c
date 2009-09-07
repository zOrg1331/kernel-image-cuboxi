/*
 * cxgb3i_ulp2.c: Chelsio S3xx iSCSI driver.
 *
 * Copyright (c) 2008 Chelsio Communications, Inc.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation.
 *
 * Written by: Karen Xie (kxie@chelsio.com)
 */

#include <linux/skbuff.h>
#include <scsi/scsi_cmnd.h>
#include <scsi/scsi_host.h>
#include <linux/crypto.h>

#include "cxgb3i.h"
#include "cxgb3i_ulp2.h"

#ifdef __DEBUG_CXGB3I_RX__
#define cxgb3i_rx_debug		cxgb3i_log_debug
#else
#define cxgb3i_rx_debug(fmt...)
#endif

#ifdef __DEBUG_CXGB3I_TX__
#define cxgb3i_tx_debug		cxgb3i_log_debug
#else
#define cxgb3i_tx_debug(fmt...)
#endif

#ifdef __DEBUG_CXGB3I_TAG__
#define cxgb3i_tag_debug	cxgb3i_log_debug
#else
#define cxgb3i_tag_debug(fmt...)
#endif

#ifdef __DEBUG_CXGB3I_DDP__
#define cxgb3i_ddp_debug	cxgb3i_log_debug
#else
#define cxgb3i_ddp_debug(fmt...)
#endif

static struct page *pad_page;

#define ULP2_PGIDX_MAX		4
#define ULP2_DDP_THRESHOLD	2048
static unsigned char ddp_page_order[ULP2_PGIDX_MAX] = {0, 1, 2, 4};
static unsigned char ddp_page_shift[ULP2_PGIDX_MAX] = {12, 13, 14, 16};
static unsigned char sw_tag_idx_bits;
static unsigned char sw_tag_age_bits;
static unsigned char page_idx = ULP2_PGIDX_MAX;
static unsigned int skb_copymax = SKB_MAX_HEAD(TX_HEADER_LEN);

static void cxgb3i_ddp_page_init(void)
{
	int i;

	sw_tag_idx_bits = (__ilog2_u32(ISCSI_ITT_MASK)) + 1;
	sw_tag_age_bits = (__ilog2_u32(ISCSI_AGE_MASK)) + 1;

	cxgb3i_log_info("tag itt 0x%x, %u bits, age 0x%x, %u bits.\n",
					ISCSI_ITT_MASK, sw_tag_idx_bits,
					ISCSI_AGE_MASK, sw_tag_age_bits);

	for (i = 0; i < ULP2_PGIDX_MAX; i++) {
		if (PAGE_SIZE == (1UL << ddp_page_shift[i])) {
			page_idx = i;
			cxgb3i_log_info("PAGE_SIZE %lu, idx %u.\n",
					PAGE_SIZE, page_idx);
		}
	}

	if (page_idx == ULP2_PGIDX_MAX)
		cxgb3i_log_info("PAGE_SIZE %lu, no match.\n", PAGE_SIZE);
}

static inline void ulp_mem_io_set_hdr(struct sk_buff *skb, unsigned int addr)
{
	struct ulp_mem_io *req = (struct ulp_mem_io *)skb->head;

	req->wr.wr_lo = 0;
	req->wr.wr_hi = htonl(V_WR_OP(FW_WROPCODE_BYPASS));
	req->cmd_lock_addr = htonl(V_ULP_MEMIO_ADDR(addr >> 5) |
				   V_ULPTX_CMD(ULP_MEM_WRITE));
	req->len = htonl(V_ULP_MEMIO_DATA_LEN(PPOD_SIZE >> 5) |
			 V_ULPTX_NFLITS((PPOD_SIZE >> 3) + 1));
}

static int set_ddp_map(struct cxgb3i_adapter *snic, struct pagepod_hdr *hdr,
		       unsigned int idx, unsigned int npods,
		       struct cxgb3i_gather_list *gl)
{
	struct cxgb3i_ddp_info *ddp = snic->ddp;
	unsigned int pm_addr = (idx << PPOD_SIZE_SHIFT) + ddp->llimit;
	int i;

	for (i = 0; i < npods; i++, idx++, pm_addr += PPOD_SIZE) {
		struct sk_buff *skb = ddp->gl_skb[idx];
		struct pagepod *ppod;
		int j, pidx;

		/* hold on to the skb until we clear the ddp mapping */
		skb_get(skb);

		ulp_mem_io_set_hdr(skb, pm_addr);
		ppod =
		    (struct pagepod *)(skb->head + sizeof(struct ulp_mem_io));
		memcpy(&(ppod->hdr), hdr, sizeof(struct pagepod));
		for (pidx = 4 * i, j = 0; j < 5; ++j, ++pidx)
			ppod->addr[j] = pidx < gl->nelem ?
				     cpu_to_be64(gl->phys_addr[pidx]) : 0UL;

		skb->priority = CPL_PRIORITY_CONTROL;
		cxgb3_ofld_send(snic->tdev, skb);
	}
	return 0;
}

static int clear_ddp_map(struct cxgb3i_adapter *snic, unsigned int idx,
			 unsigned int npods)
{
	struct cxgb3i_ddp_info *ddp = snic->ddp;
	unsigned int pm_addr = (idx << PPOD_SIZE_SHIFT) + ddp->llimit;
	int i;

	for (i = 0; i < npods; i++, idx++, pm_addr += PPOD_SIZE) {
		struct sk_buff *skb = ddp->gl_skb[idx];

		ddp->gl_skb[idx] = NULL;
		memset((skb->head + sizeof(struct ulp_mem_io)), 0, PPOD_SIZE);
		ulp_mem_io_set_hdr(skb, pm_addr);
		skb->priority = CPL_PRIORITY_CONTROL;
		cxgb3_ofld_send(snic->tdev, skb);
	}
	return 0;
}

static struct cxgb3i_gather_list *ddp_make_gl(unsigned int xferlen,
					      struct scatterlist *sgl,
					      unsigned int sgcnt, int gfp)
{
	struct cxgb3i_gather_list *gl;
	struct scatterlist *sg = sgl;
	struct page *sgpage = sg_page(sg);
	unsigned int sglen = sg->length;
	unsigned int sgoffset = sg->offset;
	unsigned int npages = (xferlen + sgoffset + PAGE_SIZE - 1) >>
			      PAGE_SHIFT;
	int i = 1, j = 0;

	if (sgoffset)
		return NULL;

	gl = kzalloc(sizeof(struct cxgb3i_gather_list) +
		     npages * (sizeof(dma_addr_t) + sizeof(struct page *)),
		     gfp);
	if (!gl)
		return NULL;

	gl->pages = (struct page **)&gl->phys_addr[npages];
	gl->length = xferlen;
	gl->offset = sgoffset;
	gl->pages[0] = sgpage;

	sg = sg_next(sg);
	while (sg) {
		struct page *page = sg_page(sg);

		if (sgpage == page && sg->offset == sgoffset + sglen)
			sglen += sg->length;
		else {
			/* make sure the sgl is fit for ddp:
			 * each has the same page size, and
			 * all of the middle pages are used completely
			 */
			if ((j && sgoffset) ||
			    ((i != sgcnt - 1) &&
			     ((sglen + sgoffset) & ~PAGE_MASK)))
				goto error_out;

			j++;
			if (j == gl->nelem || sg->offset)
				goto error_out;
			gl->pages[j] = page;
			sglen = sg->length;
			sgoffset = sg->offset;
			sgpage = page;
		}
		i++;
		sg = sg_next(sg);
	}
	gl->nelem = ++j;
	return gl;

error_out:
	kfree(gl);
	return NULL;
}

static inline int ddp_find_unused_entries(struct cxgb3i_ddp_info *ddp,
					  int start, int max, int count,
					  struct cxgb3i_gather_list *gl)
{
	unsigned int i, j;

	spin_lock(&ddp->map_lock);
	for (i = start; i <= max;) {
		for (j = 0; j < count; j++) {
			if (ddp->gl_map[i + j])
				break;
		}
		if (j == count) {
			for (j = 0; j < count; j++)
				ddp->gl_map[i + j] = gl;
			spin_unlock(&ddp->map_lock);
			return i;
		}
		i += j + 1;
	}
	spin_unlock(&ddp->map_lock);
	return -EBUSY;
}

static inline void ddp_unmark_entries(struct cxgb3i_ddp_info *ddp,
				      int start, int count)
{
	spin_lock(&ddp->map_lock);
	memset(&ddp->gl_map[start], 0,
	       count * sizeof(struct cxgb3i_gather_list *));
	spin_unlock(&ddp->map_lock);
}

static inline void ddp_free_gl_skb(struct cxgb3i_ddp_info *ddp,
				   int idx, int count)
{
	int i;

	for (i = 0; i < count; i++, idx++)
		if (ddp->gl_skb[idx]) {
			kfree_skb(ddp->gl_skb[idx]);
			ddp->gl_skb[idx] = NULL;
		}
}

static inline int ddp_alloc_gl_skb(struct cxgb3i_ddp_info *ddp,
				   int idx, int count, int gfp)
{
	int i;

	for (i = 0; i < count; i++) {
		struct sk_buff *skb = alloc_skb(sizeof(struct ulp_mem_io) +
						PPOD_SIZE, gfp);
		if (skb) {
			ddp->gl_skb[idx + i] = skb;
			skb_put(skb, sizeof(struct ulp_mem_io) + PPOD_SIZE);
		} else {
			ddp_free_gl_skb(ddp, idx, i);
			return -ENOMEM;
		}
	}
	return 0;
}

static inline void ddp_gl_unmap(struct pci_dev *pdev,
				struct cxgb3i_gather_list *gl)
{
	int i;

	for (i = 0; i < gl->nelem; i++)
		pci_unmap_page(pdev, gl->phys_addr[i], PAGE_SIZE,
			       PCI_DMA_FROMDEVICE);
}

static inline int ddp_gl_map(struct pci_dev *pdev,
			     struct cxgb3i_gather_list *gl)
{
	int i;

	for (i = 0; i < gl->nelem; i++) {
		gl->phys_addr[i] = pci_map_page(pdev, gl->pages[i], 0,
						PAGE_SIZE,
						PCI_DMA_FROMDEVICE);
		if (unlikely(pci_dma_mapping_error(pdev, gl->phys_addr[i])))
			goto unmap;
	}

	return i;

unmap:
	if (i) {
		unsigned int nelem = gl->nelem;

		gl->nelem = i;
		ddp_gl_unmap(pdev, gl);
		gl->nelem = nelem;
	}
	return -ENOMEM;
}

u32 cxgb3i_ddp_tag_reserve(struct cxgb3i_adapter *snic, unsigned int tid,
			   u32 sw_tag, unsigned int xferlen,
			   struct scatterlist *sgl, unsigned int sgcnt,
			   int gfp)
{
	struct cxgb3i_ddp_info *ddp = snic->ddp;
	struct cxgb3i_gather_list *gl;
	struct pagepod_hdr hdr;
	unsigned int npods;
	int idx = -1, idx_max;
	u32 tag;

	if (page_idx >= ULP2_PGIDX_MAX || !ddp || !sgcnt ||
		xferlen < ULP2_DDP_THRESHOLD) {
		cxgb3i_tag_debug("pgidx %u, sgcnt %u, xfer %u/%u, NO ddp.\n",
				 page_idx, sgcnt, xferlen, ULP2_DDP_THRESHOLD);
		return RESERVED_ITT;
	}

	gl = ddp_make_gl(xferlen, sgl, sgcnt, gfp);
	if (!gl) {
		cxgb3i_tag_debug("sgcnt %u, xferlen %u, SGL check fail.\n",
				 sgcnt, xferlen);
		return RESERVED_ITT;
	}

	npods = (gl->nelem + PPOD_PAGES_MAX - 1) >> PPOD_PAGES_SHIFT;
	idx_max = ddp->nppods - npods;

	if (ddp->idx_last >= idx_max)
		idx = ddp_find_unused_entries(ddp, 0, idx_max, npods, gl);
	else {
		idx = ddp_find_unused_entries(ddp, ddp->idx_last + 1, idx_max,
					      npods, gl);
		if ((idx < 0) && (ddp->idx_last >= npods))
			idx = ddp_find_unused_entries(ddp, 0,
						      ddp->idx_last - npods + 1,
						      npods, gl);
	}
	if (idx < 0) {
		cxgb3i_tag_debug("sgcnt %u, xferlen %u, npods %u NO DDP.\n",
				 sgcnt, xferlen, npods);
		goto free_gl;
	}

	if (ddp_alloc_gl_skb(ddp, idx, npods, gfp) < 0)
		goto unmark_entries;

	if (ddp_gl_map(snic->pdev, gl) < 0)
		goto unmap_sgl;

	tag = cxgb3i_ddp_tag_base(&snic->tag_format, sw_tag);
	tag |= idx << PPOD_IDX_SHIFT;

	hdr.rsvd = 0;
	hdr.vld_tid = htonl(F_PPOD_VALID | V_PPOD_TID(tid));
	hdr.pgsz_tag_clr = htonl(tag & ddp->rsvd_tag_mask);
	hdr.maxoffset = htonl(xferlen);
	hdr.pgoffset = htonl(gl->offset);

	if (set_ddp_map(snic, &hdr, idx, npods, gl) < 0)
		goto unmap_sgl;

	ddp->idx_last = idx;
	cxgb3i_tag_debug("tid 0x%x, xfer %u, 0x%x -> ddp 0x%x (0x%x, %u).\n",
			 tid, xferlen, sw_tag, tag, idx, npods);
	return tag;

unmap_sgl:
	ddp_gl_unmap(snic->pdev, gl);
	ddp_free_gl_skb(ddp, idx, npods);
unmark_entries:
	ddp_unmark_entries(ddp, idx, npods);
free_gl:
	kfree(gl);
	return RESERVED_ITT;
}

void cxgb3i_ddp_tag_release(struct cxgb3i_adapter *snic, u32 tag)
{
	struct cxgb3i_ddp_info *ddp = snic->ddp;
	u32 idx;

	if (!ddp) {
		cxgb3i_log_error("release ddp tag 0x%x, ddp NULL.\n", tag);
		return;
	}

	idx = (tag >> PPOD_IDX_SHIFT) & ddp->idx_mask;
	if (idx < ddp->nppods) {
		struct cxgb3i_gather_list *gl = ddp->gl_map[idx];
		unsigned int npods;

		if (!gl || !gl->nelem) {
			cxgb3i_log_error("release tag 0x%x, idx 0x%x, no gl.\n",
					 tag, idx);
			return;
		}
		npods = (gl->nelem + PPOD_PAGES_MAX - 1) >> PPOD_PAGES_SHIFT;
		cxgb3i_tag_debug("ddp tag 0x%x, release idx 0x%x, npods %u.\n",
				 tag, idx, npods);
		clear_ddp_map(snic, idx, npods);
		ddp_unmark_entries(ddp, idx, npods);
		ddp_gl_unmap(snic->pdev, gl);
	} else
		 cxgb3i_log_error("ddp tag 0x%x, idx 0x%x > max 0x%x.\n",
						  tag, idx, ddp->nppods);
}

int cxgb3i_conn_ulp_setup(struct cxgb3i_conn *cconn, int hcrc, int dcrc)
{
	struct iscsi_tcp_conn *tcp_conn = cconn->conn->dd_data;
	struct s3_conn *c3cn = (struct s3_conn *)(tcp_conn->sock);
	struct sk_buff *skb = alloc_skb(sizeof(struct cpl_set_tcb_field),
					GFP_KERNEL);
	struct cpl_set_tcb_field *req;
	u64 val = (hcrc ? 1 : 0) | (dcrc ? 2 : 0);

	if (!skb)
		return -ENOMEM;

	if (page_idx < ULP2_PGIDX_MAX)
		val |= page_idx << 4;
	else
		cxgb3i_log_warn("TID 0x%x, host page 0x%lx default to 4K.\n",
				c3cn->tid, PAGE_SIZE);

	/* set up ulp submode and page size */
	req = (struct cpl_set_tcb_field *)skb_put(skb, sizeof(*req));
	req->wr.wr_hi = htonl(V_WR_OP(FW_WROPCODE_FORWARD));
	OPCODE_TID(req) = htonl(MK_OPCODE_TID(CPL_SET_TCB_FIELD, c3cn->tid));
	req->reply = V_NO_REPLY(1);
	req->cpu_idx = 0;
	req->word = htons(31);
	req->mask = cpu_to_be64(0xFF000000);
	req->val = cpu_to_be64(val << 24);
	skb->priority = CPL_PRIORITY_CONTROL;

	cxgb3_ofld_send(c3cn->cdev, skb);
	return 0;
}

static int cxgb3i_conn_read_pdu_skb(struct iscsi_conn *conn,
				    struct sk_buff *skb)
{
	struct iscsi_tcp_conn *tcp_conn = conn->dd_data;
	struct iscsi_segment *segment = &tcp_conn->in.segment;
	struct iscsi_hdr *hdr = (struct iscsi_hdr *)tcp_conn->in.hdr_buf;
	unsigned char *buf = (unsigned char *)hdr;
	unsigned int offset = sizeof(struct iscsi_hdr);
	int err;

	cxgb3i_rx_debug("conn 0x%p, skb 0x%p, len %u, flag 0x%x.\n",
			conn, skb, skb->len, skb_ulp_mode(skb));

	/* read bhs */
	err = skb_copy_bits(skb, 0, buf, sizeof(struct iscsi_hdr));
	if (err < 0)
		return err;
	segment->copied = sizeof(struct iscsi_hdr);
	/* read ahs */
	if (hdr->hlength) {
		unsigned int ahslen = hdr->hlength << 2;
		/* Make sure we don't overflow */
		if (sizeof(*hdr) + ahslen > sizeof(tcp_conn->in.hdr_buf))
			return -ISCSI_ERR_AHSLEN;
		err = skb_copy_bits(skb, offset, buf + offset, ahslen);
		if (err < 0)
			return err;
		offset += ahslen;
	}
	/* header digest */
	if (conn->hdrdgst_en)
		offset += ISCSI_DIGEST_SIZE;

	/* check header digest */
	segment->status = (conn->hdrdgst_en &&
			   (skb_ulp_mode(skb) & ULP2_FLAG_HCRC_ERROR)) ?
	    ISCSI_SEGMENT_DGST_ERR : 0;

	hdr->itt = ntohl(hdr->itt);
	segment->total_copied = segment->total_size;
	tcp_conn->in.hdr = hdr;
	err = iscsi_tcp_hdr_dissect(conn, hdr);
	if (err)
		return err;

	if (tcp_conn->in.datalen) {
		segment = &tcp_conn->in.segment;
		segment->status = (conn->datadgst_en &&
				   (skb_ulp_mode(skb) & ULP2_FLAG_DCRC_ERROR)) ?
		    ISCSI_SEGMENT_DGST_ERR : 0;
		if (skb_ulp_mode(skb) & ULP2_FLAG_DATA_DDPED) {
			cxgb3i_rx_debug("skb 0x%p, opcode 0x%x, data %u, "
					"ddp'ed, itt 0x%x.\n",
					skb, hdr->opcode & ISCSI_OPCODE_MASK,
					tcp_conn->in.datalen, hdr->itt);
			segment->total_copied = segment->total_size;
		} else {
			cxgb3i_rx_debug("skb 0x%p, opcode 0x%x, data %u, "
					"not ddp'ed, itt 0x%x.\n",
					 skb, hdr->opcode & ISCSI_OPCODE_MASK,
					 tcp_conn->in.datalen, hdr->itt);
			offset += sizeof(struct cpl_iscsi_hdr_norss);
		}

		while (segment->total_copied < segment->total_size) {
			iscsi_tcp_segment_map(segment, 1);
			err = skb_copy_bits(skb, offset, segment->data,
					    segment->size);
			iscsi_tcp_segment_unmap(segment);
			if (err)
				return err;
			segment->total_copied += segment->size;
			offset += segment->size;

			if (segment->total_copied < segment->total_size)
				iscsi_tcp_segment_init_sg(segment,
							  sg_next(segment->sg),
							  0);
		}
		err = segment->done(tcp_conn, segment);
	}
	return err;
}

static inline void tx_skb_setmode(struct sk_buff *skb, int hcrc, int dcrc)
{
	u8 submode = 0;

	if (hcrc)
		submode |= 1;
	if (dcrc)
		submode |= 2;
	skb_ulp_mode(skb) = (ULP_MODE_ISCSI << 4) | submode;
}

static int sg_page_coalesce(struct scatterlist *sg, unsigned int offset,
			    unsigned int dlen, skb_frag_t *frags, int frag_max)
{
	unsigned int sglen = sg->length - offset;
	struct page *page = sg_page(sg);
	unsigned int datalen = dlen, copy;
	int i;

	i = 0;
	do {
		if (!sglen) {
			sg = sg_next(sg);
			offset = 0;
			sglen = sg->length;
			page = sg_page(sg);
		}
		copy = min(datalen, sglen);
		if (i && page == frags[i - 1].page &&
		    offset + sg->offset ==
			frags[i - 1].page_offset + frags[i - 1].size) {
			frags[i - 1].size += copy;
		} else {
			if (i >= frag_max) {
				cxgb3i_log_error("%s, too many pages > %u, "
						 "dlen %u.\n", __func__,
						 frag_max, dlen);
				return -EINVAL;
			}

			frags[i].page = page;
			frags[i].page_offset = sg->offset + offset;
			frags[i].size = copy;
			i++;
		}
		datalen -= copy;
		offset += copy;
		sglen -= copy;
	} while (datalen);

	return i;
}

static int copy_frags_to_skb_pages(struct sk_buff *skb, skb_frag_t *frags,
				   int frag_cnt, unsigned int datalen)
{
	struct page *page = NULL;
	unsigned char *dp;
	unsigned int pg_left = 0;
	unsigned int copy_total = 0;
	int i;

	for (i = 0; i < frag_cnt; i++, frags++) {
		while (frags->size) {
			unsigned char *sp = page_address(frags->page);
			unsigned int copy;

			if (!pg_left) {
				int cnt = skb_shinfo(skb)->nr_frags;

				if (cnt >= MAX_SKB_FRAGS) {
					cxgb3i_log_error("%s: pdu data %u.\n",
							 __func__, datalen);
					return -EINVAL;
				}
				page = alloc_page(GFP_ATOMIC);
				if (!page)
					return -ENOMEM;
				dp = page_address(page);
				pg_left = PAGE_SIZE;

				copy = min(pg_left, datalen);
				skb_fill_page_desc(skb, cnt, page, 0, copy);

				skb->len += copy;
				skb->data_len += copy;
				skb->truesize += copy;
				datalen -= copy;
			}
			copy = min(pg_left, frags->size);
			memcpy(dp, sp + frags->page_offset, copy);

			frags->size -= copy;
			frags->page_offset += copy;
			dp += copy;
			pg_left -= copy;
			copy_total += copy;
		}
	}

	return copy_total;
}

int cxgb3i_conn_ulp2_xmit(struct iscsi_conn *conn)
{
	struct cxgb3i_conn *cconn = conn->dd_data;
	struct iscsi_tcp_conn *tcp_conn = &cconn->tcp_conn;
	struct iscsi_segment *hdr_seg = &tcp_conn->out.segment;
	struct iscsi_segment *data_seg = &tcp_conn->out.data_segment;
	unsigned int hdrlen = hdr_seg->total_size;
	unsigned int datalen = data_seg->total_size;
	unsigned int padlen = iscsi_padding(datalen);
	unsigned int copylen = hdrlen;
	unsigned int copy_dlen = 0;
	struct sk_buff *skb;
	unsigned char *dst;
	int i, frag_cnt = 0;
	int err = -EAGAIN;

	/*
	 * the whole pdu needs to fit into one skb, make sure we don't overrun
	 * the skb's frag_list. If there are more sg pages than MAX_SKB_FRAGS,
	 * we have to copy the data either to the head or newly allocated
	 * whole new page(s). This could happen if the sg contains a lot of
	 * fragmented data chunks (pages).
	 */
	if (datalen) {
		if (!data_seg->data) {
			err = sg_page_coalesce(data_seg->sg,
						data_seg->sg_offset,
						data_seg->total_size,
						cconn->frags,
						TX_PDU_PAGES_MAX);
			if (err < 0)
				return err;
			frag_cnt = err;

			if (frag_cnt > MAX_SKB_FRAGS ||
			    (padlen && frag_cnt + 1 > MAX_SKB_FRAGS))
				copy_dlen = datalen + padlen;
		} else
			copy_dlen += datalen + padlen;
	}

	if (copylen + copy_dlen < skb_copymax)
		copylen += copy_dlen;

	/* supports max. 16K pdus, so one skb is enough to hold all the data */
	skb = alloc_skb(TX_HEADER_LEN + copylen, GFP_ATOMIC);
	if (!skb)
		return -EAGAIN;

	skb_reserve(skb, TX_HEADER_LEN);
	skb_put(skb, copylen);
	dst = skb->data;

	tx_skb_setmode(skb, conn->hdrdgst_en, datalen ? conn->datadgst_en : 0);

	memcpy(dst, hdr_seg->data, hdrlen);
	dst += hdrlen;

	if (!datalen)
		goto send_pdu;

	if (data_seg->data) {
		/* data is in a linear buffer */
		if (copylen > hdrlen) {
			/* data fits in the skb's headroom */
			memcpy(dst, data_seg->data, datalen);
			dst += datalen;
			if (padlen)
				memset(dst, 0, padlen);
		} else {
			struct page *pg = virt_to_page(data_seg->data);

			get_page(pg);
			skb_fill_page_desc(skb, 0, pg,
					   offset_in_page(data_seg->data),
					   datalen);
			skb->len += datalen;
			skb->data_len += datalen;
			skb->truesize += datalen;
		}
	} else if (copy_dlen) {
		/* need to copy the page fragments */
		if (copylen > hdrlen) {
			skb_frag_t *frag = cconn->frags;

			/* data fits in the skb's headroom */
			for (i = 0; i < frag_cnt; i++, frag++) {
				memcpy(dst,
					page_address(frag->page) +
						frag->page_offset,
					frag->size);
				dst += frag->size;
			}
			if (padlen)
				memset(dst, 0, padlen);
		} else {
			/* allocate pages to hold the data */
			err = copy_frags_to_skb_pages(skb, cconn->frags,
						      frag_cnt, datalen);
			if (err < 0) {
				err = -EAGAIN;
				goto free_skb;
			}
			WARN_ON(err != datalen);
			if (padlen) {
				skb_frag_t *frag;

				i = skb_shinfo(skb)->nr_frags;
				frag = &skb_shinfo(skb)->frags[i];
				dst = page_address(frag->page);

				memset(dst + frag->page_offset + frag->size,
				       0, padlen);
				frag->size += padlen;
			}
		}
	} else {
		/* sg pages fit into frag_list */
		for (i = 0; i < frag_cnt; i++)
			get_page(cconn->frags[i].page);
		memcpy(skb_shinfo(skb)->frags, cconn->frags,
			sizeof(skb_frag_t) * frag_cnt);
		skb_shinfo(skb)->nr_frags = frag_cnt;
		skb->len += datalen;
		skb->data_len += datalen;
		skb->truesize += datalen;

		if (padlen) {
			i = skb_shinfo(skb)->nr_frags;
			get_page(pad_page);
			skb_fill_page_desc(skb, i, pad_page, 0, padlen);
			skb->len += padlen;
			skb->data_len += padlen;
			skb->truesize += padlen;
		}
	}

send_pdu:
	err = cxgb3i_c3cn_send_pdus((struct s3_conn *)tcp_conn->sock, skb);
	if (err > 0) {
		int pdulen = hdrlen + datalen + padlen;

		if (conn->hdrdgst_en)
			pdulen += ISCSI_DIGEST_SIZE;
		if (datalen && conn->datadgst_en)
			pdulen += ISCSI_DIGEST_SIZE;

		hdr_seg->total_copied = hdr_seg->total_size;
		data_seg->total_copied = data_seg->total_size;
		conn->txdata_octets += pdulen;
		return pdulen;
	}

free_skb:
	kfree_skb(skb);
	if (err < 0 && err != -EAGAIN) {
		cxgb3i_log_error("conn 0x%p, xmit err %d, skb len %u/%u.\n",
				 conn, err, skb->len, skb->data_len);
		iscsi_conn_failure(conn, ISCSI_ERR_CONN_FAILED);
		return err;
	}
	return -EAGAIN;
}

int cxgb3i_ulp2_init(void)
{
	pad_page = alloc_page(GFP_KERNEL);
	if (!pad_page)
		return -ENOMEM;
	memset(page_address(pad_page), 0, PAGE_SIZE);
	cxgb3i_ddp_page_init();
	cxgb3i_log_info("skb max. frag %u, head %u.\n",
			(unsigned int)MAX_SKB_FRAGS,
			(unsigned int)skb_copymax);
	return 0;
}

void cxgb3i_ulp2_cleanup(void)
{
	if (pad_page) {
		__free_page(pad_page);
		pad_page = NULL;
	}
}

void cxgb3i_conn_pdu_ready(struct s3_conn *c3cn)
{
	struct sk_buff *skb;
	unsigned int read = 0;
	struct iscsi_conn *conn = c3cn->user_data;
	int err = 0;

	cxgb3i_rx_debug("cn 0x%p.\n", c3cn);

	read_lock(&c3cn->callback_lock);
	if (unlikely(!conn || conn->suspend_rx)) {
		cxgb3i_rx_debug("conn 0x%p, id %d, suspend_rx %lu!\n",
				conn, conn ? conn->id : 0xFF,
				conn ? conn->suspend_rx : 0xFF);
		read_unlock(&c3cn->callback_lock);
		return;
	}
	skb = skb_peek(&c3cn->receive_queue);
	while (!err && skb) {
		__skb_unlink(skb, &c3cn->receive_queue);
		read += skb_ulp_pdulen(skb);
		err = cxgb3i_conn_read_pdu_skb(conn, skb);
		__kfree_skb(skb);
		skb = skb_peek(&c3cn->receive_queue);
	}
	read_unlock(&c3cn->callback_lock);
	if (c3cn) {
		c3cn->copied_seq += read;
		cxgb3i_c3cn_rx_credits(c3cn, read);
	}
	conn->rxdata_octets += read;

	if (err) {
		cxgb3i_log_info("conn 0x%p rx failed err %d.\n", conn, err);
		iscsi_conn_failure(conn, ISCSI_ERR_CONN_FAILED);
	}
}

void cxgb3i_conn_tx_open(struct s3_conn *c3cn)
{
	struct iscsi_conn *conn = c3cn->user_data;
	struct iscsi_tcp_conn *tcp_conn;

	cxgb3i_tx_debug("cn 0x%p.\n", c3cn);
	if (conn) {
		cxgb3i_tx_debug("cn 0x%p, cid %d.\n", c3cn, conn->id);
		tcp_conn = conn->dd_data;
		scsi_queue_work(conn->session->host, &conn->xmitwork);
	}
}

void cxgb3i_conn_closing(struct s3_conn *c3cn)
{
	struct iscsi_conn *conn;

	read_lock(&c3cn->callback_lock);
	conn = c3cn->user_data;
	if (conn)
		iscsi_conn_failure(conn, ISCSI_ERR_CONN_FAILED);
	read_unlock(&c3cn->callback_lock);
}

int cxgb3i_adapter_ulp_init(struct cxgb3i_adapter *snic)
{
	struct t3cdev *tdev = snic->tdev;
	struct cxgb3i_ddp_info *ddp;
	struct ulp_iscsi_info uinfo;
	unsigned int ppmax, bits;
	int i, err;

	err = tdev->ctl(tdev, ULP_ISCSI_GET_PARAMS, &uinfo);
	if (err < 0) {
		cxgb3i_log_error("%s, failed to get iscsi param err=%d.\n",
				 tdev->name, err);
		return err;
	}

	snic->tx_max_size = min_t(unsigned int,
				  uinfo.max_txsz, ULP2_MAX_PKT_SIZE);
	snic->rx_max_size = min_t(unsigned int,
				  uinfo.max_rxsz, ULP2_MAX_PKT_SIZE);
	cxgb3i_log_info("ddp max pkt size: %u/%u,%u, %u/%u,%u.\n",
			snic->tx_max_size, uinfo.max_txsz, ULP2_MAX_PKT_SIZE,
			snic->rx_max_size, uinfo.max_rxsz, ULP2_MAX_PKT_SIZE);

	snic->tag_format.sw_bits = sw_tag_idx_bits + sw_tag_age_bits;

	ppmax = (uinfo.ulimit - uinfo.llimit + 1) >> PPOD_SIZE_SHIFT;
	bits = __ilog2_u32(ppmax) + 1;
	if (bits > PPOD_IDX_MAX_SIZE)
		bits = PPOD_IDX_MAX_SIZE;
	ppmax = (1 << (bits - 1)) - 1;

	ddp = cxgb3i_alloc_big_mem(sizeof(struct cxgb3i_ddp_info) +
				   ppmax *
				   (sizeof(struct cxgb3i_gather_list *) +
				    sizeof(struct sk_buff *)),
				   GFP_KERNEL);
	if (!ddp) {
		cxgb3i_log_warn("snic %s unable to alloc ddp ppod 0x%u, "
				"ddp disabled.\n", tdev->name, ppmax);
		return 0;
	}
	ddp->gl_map = (struct cxgb3i_gather_list **)(ddp + 1);
	ddp->gl_skb = (struct sk_buff **)(((char *)ddp->gl_map) +
					  ppmax *
					  sizeof(struct cxgb3i_gather_list *));

	spin_lock_init(&ddp->map_lock);
	ddp->llimit = uinfo.llimit;
	ddp->ulimit = uinfo.ulimit;
	ddp->nppods = ppmax;
	ddp->idx_last = ppmax;
	ddp->idx_bits = bits;
	ddp->idx_mask = (1 << bits) - 1;
	ddp->rsvd_tag_mask = (1 << (bits + PPOD_IDX_SHIFT)) - 1;

	uinfo.tagmask = ddp->idx_mask << PPOD_IDX_SHIFT;
	for (i = 0; i < ULP2_PGIDX_MAX; i++)
		uinfo.pgsz_factor[i] = ddp_page_order[i];
	uinfo.ulimit = uinfo.llimit + (ppmax << PPOD_SIZE_SHIFT);

	err = tdev->ctl(tdev, ULP_ISCSI_SET_PARAMS, &uinfo);
	if (err < 0) {
		cxgb3i_log_warn("snic unable to set iscsi param err=%d, "
				"ddp disabled.\n", err);
		goto free_ppod_map;
	}

	tdev->ulp_iscsi = snic->ddp = ddp;

	cxgb3i_log_info("nppods %u (0x%x ~ 0x%x), bits %u, mask 0x%x,0x%x.\n",
			ppmax, ddp->llimit, ddp->ulimit, ddp->idx_bits,
			ddp->idx_mask, ddp->rsvd_tag_mask);

	snic->tag_format.rsvd_bits = ddp->idx_bits;
	snic->tag_format.rsvd_shift = PPOD_IDX_SHIFT;
	snic->tag_format.rsvd_mask = (1 << snic->tag_format.rsvd_bits) - 1;

	cxgb3i_log_info("tag format: sw %u, rsvd %u,%u, mask 0x%x.\n",
			snic->tag_format.sw_bits, snic->tag_format.rsvd_bits,
			snic->tag_format.rsvd_shift,
			snic->tag_format.rsvd_mask);
	return 0;

free_ppod_map:
	cxgb3i_free_big_mem(ddp);
	return 0;
}

void cxgb3i_adapter_ulp_cleanup(struct cxgb3i_adapter *snic)
{
	struct cxgb3i_ddp_info *ddp = snic->ddp;

	if (ddp) {
		int i = 0;

		snic->tdev->ulp_iscsi = NULL;
		spin_lock(&snic->lock);
		snic->ddp = NULL;
		spin_unlock(&snic->lock);

		while (i < ddp->nppods) {
			struct cxgb3i_gather_list *gl = ddp->gl_map[i];
			if (gl) {
				int npods = (gl->nelem + PPOD_PAGES_MAX - 1)
					     >> PPOD_PAGES_SHIFT;

				kfree(gl);
				ddp_free_gl_skb(ddp, i, npods);
			} else
				i++;
		}
		cxgb3i_free_big_mem(ddp);
	}
}
