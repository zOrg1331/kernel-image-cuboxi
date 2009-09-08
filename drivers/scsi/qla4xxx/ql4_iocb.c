/*
 * QLogic iSCSI HBA Driver
 * Copyright (c)  2003-2006 QLogic Corporation
 *
 * See LICENSE.qla4xxx for copyright and licensing details.
 */

#include "ql4_def.h"
#include "ql4_version.h"
#include "ql4_glbl.h"
#include "ql4_dbg.h"
#include "ql4_inline.h"

#include <scsi/scsi_tcq.h>

static void qla4xxx_build_scsi_iocbs(struct srb *srb,
				     struct command_t3_entry *cmd_entry,
				     uint16_t tot_dsds)
{
	struct scsi_qla_host *ha;
	uint16_t avail_dsds;
	struct data_seg_a64 *cur_dsd;
	struct scsi_cmnd *cmd;
	struct scatterlist *sg;
	int i;

	cmd = srb->cmd;
	ha = srb->ha;

	avail_dsds = COMMAND_SEG;
	cur_dsd = (struct data_seg_a64 *) & (cmd_entry->dataseg[0]);

	if (srb->flags & SRB_SCSI_PASSTHRU) {
		cur_dsd->base.addrLow = cpu_to_le32(LSDW(srb->dma_handle));
		cur_dsd->base.addrHigh = cpu_to_le32(MSDW(srb->dma_handle));
		cur_dsd->count = cpu_to_le32(srb->dma_len);
		return;
	}

	if (!scsi_bufflen(cmd) || cmd->sc_data_direction == DMA_NONE) {
		/* No data being transferred */
		cmd_entry->ttlByteCnt = __constant_cpu_to_le32(0);
		return;
	}

	scsi_for_each_sg(cmd, sg, tot_dsds, i) {
		dma_addr_t sle_dma;

		/* Allocate additional continuation packets? */
		if (avail_dsds == 0) {
			struct continuation_t1_entry *cont_entry;

			cont_entry = qla4xxx_alloc_cont_entry(ha);
			cur_dsd =
				(struct data_seg_a64 *)
				&cont_entry->dataseg[0];
			avail_dsds = CONTINUE_SEG;
		}

		sle_dma = sg_dma_address(sg);
		cur_dsd->base.addrLow = cpu_to_le32(LSDW(sle_dma));
		cur_dsd->base.addrHigh = cpu_to_le32(MSDW(sle_dma));
		cur_dsd->count = cpu_to_le32(sg_dma_len(sg));
		avail_dsds--;

		cur_dsd++;
	}
}

/**
 * qla4xxx_send_command_to_isp - issues command to HBA
 * @ha: pointer to host adapter structure.
 * @srb: pointer to SCSI Request Block to be sent to ISP
 *
 * This routine is called by qla4xxx_queuecommand to build an ISP
 * command and pass it to the ISP for execution.
 **/
int qla4xxx_send_command_to_isp(struct scsi_qla_host *ha, struct srb * srb)
{
	struct scsi_cmnd *cmd = srb->cmd;
	struct ddb_entry *ddb_entry;
	struct command_t3_entry *cmd_entry;

	int nseg;
	uint16_t tot_dsds;
	uint16_t req_cnt;

	unsigned long flags;
	uint16_t cnt;
	uint16_t i;
	uint32_t index;
	char tag[2];

	/* Get real lun and adapter */
	ddb_entry = srb->ddb;

	tot_dsds = 0;

	/* Acquire hardware specific lock */
	spin_lock_irqsave(&ha->hardware_lock, flags);

	//index = (uint32_t)cmd->request->tag;
	index = ha->current_active_index;
	for (i = 0; i < MAX_SRBS; i++) {
		index++;
		if (index == MAX_SRBS)
			index = 1;
		if (ha->active_srb_array[index] == 0) {
			ha->current_active_index = index;
			break;
		}
	}
	if (i >= MAX_SRBS) {
		printk(KERN_INFO "scsi%ld: %s: NO more SRB entries used "
		       "iocbs=%d, \n reqs remaining=%d\n", ha->host_no,
		       __func__, ha->iocb_cnt, ha->req_q_count);
		goto queuing_error;
	}

	/* Calculate the number of request entries needed. */
	if (srb->flags & SRB_SCSI_PASSTHRU)
		tot_dsds = 1;
	else {
		nseg = scsi_dma_map(cmd);
		if (nseg < 0)
			goto queuing_error;
		tot_dsds = nseg;
	}

	req_cnt = qla4xxx_calc_request_entries(tot_dsds);

	if (ha->req_q_count < (req_cnt + 2)) {
		cnt = (uint16_t) le32_to_cpu(ha->shadow_regs->req_q_out);
		if (ha->request_in < cnt)
			ha->req_q_count = cnt - ha->request_in;
		else
			ha->req_q_count = REQUEST_QUEUE_DEPTH -
				(ha->request_in - cnt);
	}

	if (ha->req_q_count < (req_cnt + 2))
		goto queuing_error;

	/* total iocbs active */
	if ((ha->iocb_cnt + req_cnt) >= REQUEST_QUEUE_DEPTH)
		goto queuing_error;

	/* Build command packet */
	cmd_entry = (struct command_t3_entry *) ha->request_ptr;
	memset(cmd_entry, 0, sizeof(struct command_t3_entry));
	cmd_entry->hdr.entryType = ET_COMMAND;
	cmd_entry->handle = cpu_to_le32(index);
	cmd_entry->target = cpu_to_le16(ddb_entry->fw_ddb_index);
	cmd_entry->connection_id = cpu_to_le16(ddb_entry->connection_id);

	int_to_scsilun(cmd->device->lun, &cmd_entry->lun);
	cmd_entry->cmdSeqNum = cpu_to_le32(ddb_entry->CmdSn);

	memcpy(cmd_entry->cdb, cmd->cmnd, cmd->cmd_len);
	cmd_entry->dataSegCnt = cpu_to_le16(tot_dsds);
	cmd_entry->hdr.entryCount = req_cnt;

	/* Set data transfer direction control flags
         * NOTE: Look at data_direction bits iff there is data to be
         *       transferred, as the data direction bit is sometimed filled
         *       in when there is no data to be transferred */
	cmd_entry->control_flags = CF_NO_DATA;

	cmd_entry->ttlByteCnt = cpu_to_le32(scsi_bufflen(cmd));

	if (scsi_bufflen(cmd)) {
		if (cmd->sc_data_direction == DMA_TO_DEVICE)
			cmd_entry->control_flags = CF_WRITE;
		else if (cmd->sc_data_direction == DMA_FROM_DEVICE)
			cmd_entry->control_flags = CF_READ;

		ha->bytes_xfered += scsi_bufflen(cmd);
		if (ha->bytes_xfered & ~0xFFFFF){
			ha->total_mbytes_xferred += ha->bytes_xfered >> 20;
			ha->bytes_xfered &= 0xFFFFF;
		}
	}

	/* Set tagged queueing control flags */
	cmd_entry->control_flags |= CF_SIMPLE_TAG;
	if (scsi_populate_tag_msg(cmd, tag))
		switch (tag[0]) {
		case MSG_HEAD_TAG:
			cmd_entry->control_flags |= CF_HEAD_TAG;
			break;
		case MSG_ORDERED_TAG:
			cmd_entry->control_flags |= CF_ORDERED_TAG;
			break;
		}

	/* Advance request queue pointer */
	ha->request_in++;
	if (ha->request_in == REQUEST_QUEUE_DEPTH) {
		ha->request_in = 0;
		ha->request_ptr = ha->request_ring;
	} else
		ha->request_ptr++;


	qla4xxx_build_scsi_iocbs(srb, cmd_entry, tot_dsds);
	wmb();

	/*
         * Check to see if adapter is online before placing request on
         * request queue.  If a reset occurs and a request is in the queue,
         * the firmware will still attempt to process the request, retrieving
         * garbage for pointers.
         */
	if (!test_bit(AF_ONLINE, &ha->flags)) {
		DEBUG2(printk("scsi%ld: %s: Adapter OFFLINE! "
			      "Do not issue command.\n",
			      ha->host_no, __func__));
		goto queuing_error;
	}

	srb->cmd->host_scribble = (unsigned char *)srb;
	ha->active_srb_array[index] = srb;

	/* update counters */
	srb->state = SRB_ACTIVE_STATE;
	srb->flags |= SRB_DMA_VALID;

	/* Track IOCB used */
	ha->iocb_cnt += req_cnt;
	srb->iocb_cnt = req_cnt;
	ha->req_q_count -= req_cnt;

	/* Debug print statements */
	writel(ha->request_in, &ha->reg->req_q_in);
	readl(&ha->reg->req_q_in);
	spin_unlock_irqrestore(&ha->hardware_lock, flags);

	return QLA_SUCCESS;

queuing_error:
	if (!(srb->flags & SRB_SCSI_PASSTHRU))
		if (tot_dsds)
			scsi_dma_unmap(cmd);

	spin_unlock_irqrestore(&ha->hardware_lock, flags);

	return QLA_ERROR;
}
