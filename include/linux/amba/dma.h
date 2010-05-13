/*
 *  linux/include/amba/dma.h
 *
 *  Copyright (C) 2010 ST-Ericsson AB
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */
#if !defined(AMBA_DMA_H) && defined(CONFIG_DMADEVICES)
#define AMBA_DMA_H

#include <linux/dma-mapping.h>
struct dma_chan;

/**
 * struct amba_dma_channel_config - this struct is passed in as
 * configuration data to a DMA engine in order to set up a certain
 * channel for DMA transport. Anything the DMA engine needs to
 * know about the PrimeCell shall be passed through this struct.
 * The DMA engine has to provide an additional function:
 * dma_set_ambaconfig() in order for it to work with PrimeCells.
 * @addr: this is the physical address where DMA data should be
 * read (RX) or written (TX)
 * @addr_width: this is the width of the source (RX) or target
 * (TX) register where DMA data shall be read/written, in bytes.
 * legal values: 1, 2, 4, 8.
 * @direction: whether the data goes in or out on this channel,
 * right now.
 * @maxburst: the maximum number of words (note: words, not bytes)
 * that can be sent in one burst to the device. Typically something
 * like half the FIFO depth on I/O peripherals so you don't
 * overflow it.
 */
struct amba_dma_channel_config {
	dma_addr_t addr;
	u8 addr_width:4;
	enum dma_data_direction direction;
	int maxburst;
};

/*
 * The following is an extension to the DMA engine framework
 * that is needed to use the engine with PrimeCells.
 */
void dma_set_ambaconfig(struct dma_chan *chan,
			struct amba_dma_channel_config *config);

#endif /* AMBA_DMA_H */
