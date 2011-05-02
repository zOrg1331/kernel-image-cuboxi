/*
 * arch/arm/mach-at91/devices.h
 *
 * Copyright (C) 2011 Jean-Christophe PLAGNIOL-VILLARD <plagnioj@jcrosoft.com>
 *
 * Under GPLv2
 *
 */

#ifndef _AT91_DEVICES_H
#define _AT91_DEVICES_H

#include <linux/types.h>
#include <linux/platform_device.h>

#define RES_MEM(size)				\
	{					\
		.end	= size - 1,		\
		.flags	= IORESOURCE_MEM,	\
	}

#define RES_IRQ()				\
	{					\
		.flags	= IORESOURCE_IRQ,	\
	}


static inline void set_resource_mem(struct resource *res, resource_size_t mmio_base)
{
	BUG_ON(res->flags != IORESOURCE_MEM);
	res->start = mmio_base;
	res->end  += mmio_base;
}

static inline void set_resource_irq(struct resource *res, int irq)
{
	if (!irq)
		return;

	BUG_ON(res->flags != IORESOURCE_IRQ);
	res->start = irq;
	res->end   = irq;
}

struct at91_dev_resource {
	resource_size_t	mmio_base;
	int		irq;
};

struct at91_dev_resource_array {
	struct at91_dev_resource *resource;
	int num_resources;
};

#endif /* _AT91_DEVICES_H */
