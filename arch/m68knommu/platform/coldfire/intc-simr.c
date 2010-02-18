/*
 * intc-simr.c
 *
 * (C) Copyright 2009, Greg Ungerer <gerg@snapgear.com>
 *
 * This file is subject to the terms and conditions of the GNU General Public
 * License.  See the file COPYING in the main directory of this archive
 * for more details.
 */

#include <linux/types.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/interrupt.h>
#include <linux/irq.h>
#include <linux/io.h>
#include <asm/coldfire.h>
#include <asm/mcfsim.h>
#include <asm/traps.h>

static void intc_irq_mask(unsigned int irq)
{
	if (irq >= MCFINT_VECBASE) {
		if (irq < MCFINT_VECBASE + 64)
			__raw_writeb(irq - MCFINT_VECBASE, MCFINTC0_SIMR);
		else if ((irq < MCFINT_VECBASE + 128) && MCFINTC1_SIMR)
			__raw_writeb(irq - MCFINT_VECBASE - 64, MCFINTC1_SIMR);
	}

	/* only on eport */
	if (irq >= MCFGPIO_IRQ_VECBASE ||
			irq < (MCFGPIO_IRQ_VECBASE + MCFGPIO_IRQ_MAX)) {

		u8 epier = __raw_readb(MCFEPORT_EPIER);
		epier &= ~(1 << (irq - MCFGPIO_IRQ_VECBASE));
		__raw_writeb(epier, MCFEPORT_EPIER);
	}
}

static void intc_irq_unmask(unsigned int irq)
{
	if (irq >= MCFINT_VECBASE) {
		if (irq < MCFINT_VECBASE + 64)
			__raw_writeb(irq - MCFINT_VECBASE, MCFINTC0_CIMR);
		else if ((irq < MCFINT_VECBASE + 128) && MCFINTC1_CIMR)
			__raw_writeb(irq - MCFINT_VECBASE - 64, MCFINTC1_CIMR);
	}

	/* only on eport */
	if (irq >= MCFGPIO_IRQ_VECBASE ||
			irq < (MCFGPIO_IRQ_VECBASE + MCFGPIO_IRQ_MAX)) {

		u8 epier = __raw_readb(MCFEPORT_EPIER);
		epier |= 1 << (irq - MCFGPIO_IRQ_VECBASE);
		__raw_writeb(epier, MCFEPORT_EPIER);
	}
}

static void intc_irq_ack(unsigned int irq)
{
	/* only on eport */
	if (irq >= MCFGPIO_IRQ_VECBASE ||
			irq < (MCFGPIO_IRQ_VECBASE + MCFGPIO_IRQ_MAX)) {
		u8 epfr = __raw_readb(MCFEPORT_EPFR);
		epfr |= 1 << (irq - MCFGPIO_IRQ_VECBASE);
		__raw_writeb(epfr, MCFEPORT_EPFR);
	}
}

static int intc_irq_set_type(unsigned int irq, unsigned int type)
{
	unsigned shift;
	u16 eppar;

	/* only on eport */
	if (irq < MCFGPIO_IRQ_VECBASE ||
			irq >= (MCFGPIO_IRQ_VECBASE + MCFGPIO_IRQ_MAX))
		return -EINVAL;

	/* we only support TRIGGER_LOW or either (or both) RISING and FALLING */
	if ((type & IRQF_TRIGGER_HIGH) ||
			((type & IRQF_TRIGGER_LOW) &&
			 (type & (IRQF_TRIGGER_RISING |
				       IRQF_TRIGGER_FALLING))))
		return -EINVAL;

	shift = (irq - MCFGPIO_IRQ_VECBASE) * 2;

	/* default to TRIGGER_LOW */
	eppar = 0;
	if (type & IRQF_TRIGGER_RISING)
		eppar |= (0x01 << shift);
	if (type & IRQF_TRIGGER_FALLING)
		eppar |= (0x02 << shift);

	if (eppar)
		set_irq_handler(irq, handle_edge_irq);
	else
		set_irq_handler(irq, handle_level_irq);

	eppar |= (__raw_readw(MCFEPORT_EPPAR) & ~(0x3 << shift));
	__raw_writew(eppar, MCFEPORT_EPPAR);


	if (irq >= MCFINT_VECBASE) {
		if (irq < MCFINT_VECBASE + 64)
			__raw_writeb(5, MCFINTC0_ICR0 + irq - MCFINT_VECBASE);
		else if ((irq < MCFINT_VECBASE) && MCFINTC1_ICR0)
			__raw_writeb(5, MCFINTC1_ICR0 + irq - MCFINT_VECBASE - 64);
	}
	return 0;
}

static struct irq_chip intc_irq_chip = {
	.name		= "CF-INTC",
	.mask		= intc_irq_mask,
	.unmask		= intc_irq_unmask,
	.ack		= intc_irq_ack,
	.set_type	= intc_irq_set_type,
};

void __init init_IRQ(void)
{
	int irq;

	init_vectors();

	/* Mask all interrupt sources */
	__raw_writeb(0xff, MCFINTC0_SIMR);
	if (MCFINTC1_SIMR)
		__raw_writeb(0xff, MCFINTC1_SIMR);

	for (irq = 0; (irq < NR_IRQS); irq++) {
		set_irq_chip_and_handler(irq, &intc_irq_chip, handle_level_irq);
		intc_irq_set_type(irq, 0);
	}
}

