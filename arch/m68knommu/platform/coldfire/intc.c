/*
 * intc.c  -- support for the old ColdFire interrupt controller
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
#include <asm/traps.h>
#include <asm/coldfire.h>
#include <asm/mcfsim.h>

/*
 * The mapping of irq number to a mask register bit is not one-to-one.
 * The irq numbers are either based on "level" of interrupt or fixed
 * for an autovector-able interrupt. So we keep a local data structure
 * that maps from irq to mask register. Not all interrupts will have
 * an IMR bit.
 */
unsigned char mcf_irq2imr[NR_IRQS];

/*
 * Define the miniumun and maximum external interrupt numbers.
 * This is also used as the "level" interrupt numbers.
 */
#define	EIRQ1	25
#define	EIRQ7	31

/*
 * In the early version 2 core ColdFire parts the IMR register was 16 bits
 * in size. Version 3 (and later version 2) core parts have a 32 bit
 * sized IMR register. Provide some size independant methods to access the
 * IMR register.
 */
#ifdef MCFSIM_IMR_IS_16BITS

void mcf_setimr(int index)
{
	u16 imr;
	imr = __raw_readw(MCF_MBAR + MCFSIM_IMR);
	__raw_writew(imr | (0x1 << index), MCF_MBAR + MCFSIM_IMR);
}

void mcf_clrimr(int index)
{
	u16 imr;
	imr = __raw_readw(MCF_MBAR + MCFSIM_IMR);
	__raw_writew(imr & ~(0x1 << index), MCF_MBAR + MCFSIM_IMR);
}

void mcf_maskimr(unsigned int mask)
{
	u16 imr;
	imr = __raw_readw(MCF_MBAR + MCFSIM_IMR);
	imr |= mask;
	__raw_writew(imr, MCF_MBAR + MCFSIM_IMR);
}

#else

void mcf_setimr(int index)
{
	u32 imr;
	imr = __raw_readl(MCF_MBAR + MCFSIM_IMR);
	__raw_writel(imr | (0x1 << index), MCF_MBAR + MCFSIM_IMR);
}

void mcf_clrimr(int index)
{
	u32 imr;
	imr = __raw_readl(MCF_MBAR + MCFSIM_IMR);
	__raw_writel(imr & ~(0x1 << index), MCF_MBAR + MCFSIM_IMR);
}

void mcf_maskimr(unsigned int mask)
{
	u32 imr;
	imr = __raw_readl(MCF_MBAR + MCFSIM_IMR);
	imr |= mask;
	__raw_writel(imr, MCF_MBAR + MCFSIM_IMR);
}

#endif

/*
 * Interrupts can be "vectored" on the ColdFire cores that support this old
 * interrupt controller. That is, the device raising the interrupt can also
 * supply the vector number to interrupt through. The AVR register of the
 * interrupt controller enables or disables this for each external interrupt,
 * so provide generic support for this. Setting this up is out-of-band for
 * the interrupt system API's, and needs to be done by the driver that
 * supports this device. Very few devices actually use this.
 */
void mcf_autovector(int irq)
{
#ifdef MCFSIM_AVR
	if ((irq >= EIRQ1) && (irq <= EIRQ7)) {
		u8 avec;
		avec = __raw_readb(MCF_MBAR + MCFSIM_AVR);
		avec |= (0x1 << (irq - EIRQ1 + 1));
		__raw_writeb(avec, MCF_MBAR + MCFSIM_AVR);
	}
#endif
}

static void intc_irq_mask(unsigned int irq)
{
	if (mcf_irq2imr[irq])
		mcf_setimr(mcf_irq2imr[irq]);

#if defined MCFINTC2_GPIOIRQ0
	if (irq >= MCFINTC2_GPIOIRQ0 && irq <= MCFINTC2_GPIOIRQ7) {
		u32 gpiointenable = __raw_readl(MCFSIM2_GPIOINTENABLE);

		gpiointenable &= ~(0x101 << (irq - MCFINTC2_GPIOIRQ0));
		__raw_writel(gpiointenable, MCFSIM2_GPIOINTENABLE);
	}
#endif
}

static void intc_irq_unmask(unsigned int irq)
{
	if (mcf_irq2imr[irq])
		mcf_clrimr(mcf_irq2imr[irq]);

#if defined MCFINTC2_GPIOIRQ0
	if (irq >= MCFINTC2_GPIOIRQ0 && irq <= MCFINTC2_GPIOIRQ7) {
		struct irq_desc *desc = irq_to_desc(irq);
		u32 gpiointenable = __raw_readl(MCFSIM2_GPIOINTENABLE);

		if (desc->status & IRQF_TRIGGER_RISING)
			gpiointenable |= 0x0001 << (irq - MCFINTC2_GPIOIRQ0);
		if (desc->status & IRQF_TRIGGER_FALLING)
			gpiointenable |= 0x0100 << (irq - MCFINTC2_GPIOIRQ0);
		__raw_writel(gpiointenable, MCFSIM2_GPIOINTENABLE);
	}
#endif
}

static void intc_irq_ack(unsigned int irq)
{
#if defined MCFINTC2_GPIOIRQ0
	if (irq >= MCFINTC2_GPIOIRQ0 && irq <= MCFINTC2_GPIOIRQ7) {
		u32 gpiointclear = __raw_readl(MCFSIM2_GPIOINTCLEAR);

		gpiointclear |= 0x0101 << (irq - MCFINTC2_GPIOIRQ0);
		__raw_writel(gpiointclear, MCFSIM2_GPIOINTCLEAR);
	}
#endif
}

static int intc_irq_set_type(unsigned int irq, unsigned int type)
{
#if defined MCFINTC2_GPIOIRQ0
	u32 gpiointenable;

	if (type & ~(IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING))
		return -EINVAL;

	if ((irq < MCFINTC2_GPIOIRQ0) || (irq > MCFINTC2_GPIOIRQ7))
		return -EINVAL;

	/* enable rising or falling or both */
	gpiointenable = __raw_readl(MCFSIM2_GPIOINTENABLE);
	gpiointenable &= ~(0x101 << (irq - MCFINTC2_GPIOIRQ0));
	if (type & IRQF_TRIGGER_RISING)
		gpiointenable |= 0x0001 << (irq - MCFINTC2_GPIOIRQ0);
	if (type & IRQF_TRIGGER_FALLING)
		gpiointenable |= 0x0100 << (irq - MCFINTC2_GPIOIRQ0);
	__raw_writel(gpiointenable, MCFSIM2_GPIOINTENABLE);
#endif

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
	mcf_maskimr(0xffffffff);

	for (irq = 0; (irq < NR_IRQS); irq++) {
		set_irq_chip_and_handler(irq, &intc_irq_chip, handle_level_irq);
		intc_irq_set_type(irq, 0);
	}
}

