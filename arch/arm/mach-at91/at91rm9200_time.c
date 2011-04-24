/*
 * linux/arch/arm/mach-at91/at91rm9200_time.c
 *
 * Copyright (C) 2003 SAN People
 * Copyright (C) 2003 ATMEL
 * Copyright (C) 2011 Jean-Christophe PLAGNIOL-VILLARD <plagnioj@jcrosoft.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/interrupt.h>
#include <linux/irq.h>
#include <linux/clockchips.h>
#include <linux/slab.h>

#include <mach/at91_st.h>

struct at91_st_data {
	void __iomem *mapbase;
	unsigned long last_crtr;
	u32 irqmask;
	struct clock_event_device ced;
	struct clocksource cs;
	struct irqaction irqaction;
	struct platform_device *pdev;
};

static inline unsigned int at91_st_read(struct at91_st_data *data,
					 unsigned int reg_offset)
{
	return __raw_readl(data->mapbase + reg_offset);
}

static inline void at91_st_write(struct at91_st_data *data,
			unsigned int reg_offset, unsigned long value)
{
	__raw_writel(value, data->mapbase + reg_offset);
}

static struct at91_st_data *cs_to_at91_st(struct clocksource *cs)
{
	return container_of(cs, struct at91_st_data, cs);
}

static struct at91_st_data *ced_to_at91_st(struct clock_event_device *ced)
{
	return container_of(ced, struct at91_st_data, ced);
}

/*
 * The ST_CRTR is updated asynchronously to the master clock ... but
 * the updates as seen by the CPU don't seem to be strictly monotonic.
 * Waiting until we read the same value twice avoids glitching.
 */
static inline unsigned long read_CRTR(struct at91_st_data *data)
{
	unsigned long x1, x2;

	x1 = at91_st_read(data, AT91_ST_CRTR);
	do {
		x2 = at91_st_read(data, AT91_ST_CRTR);
		if (x1 == x2)
			break;
		x1 = x2;
	} while (1);
	return x1;
}

/*
 * IRQ handler for the timer.
 */
static irqreturn_t at91_st_interrupt(int irq, void *dev_id)
{
	struct at91_st_data *data = (struct at91_st_data*)dev_id;
	struct clock_event_device *ced = &data->ced;
	u32 sr;

	sr = at91_st_read(data, AT91_ST_SR) & data->irqmask;

	/*
	 * irqs should be disabled here, but as the irq is shared they are only
	 * guaranteed to be off if the timer irq is registered first.
	 */
	WARN_ON_ONCE(!irqs_disabled());

	/* simulate "oneshot" timer with alarm */
	if (sr & AT91_ST_ALMS) {
		ced->event_handler(ced);
		return IRQ_HANDLED;
	}

	/* periodic mode should handle delayed ticks */
	if (sr & AT91_ST_PITS) {
		u32	crtr = read_CRTR(data);

		while (((crtr - data->last_crtr) & AT91_ST_CRTV) >= LATCH) {
			data->last_crtr += LATCH;
			ced->event_handler(ced);
		}
		return IRQ_HANDLED;
	}

	/* this irq is shared ... */
	return IRQ_NONE;
}

static cycle_t at91_st_clocksource_read(struct clocksource *cs)
{
	struct at91_st_data *data = cs_to_at91_st(cs);

	return read_CRTR(data);
}

static void at91_st_clock_event_mode(enum clock_event_mode mode,
				      struct clock_event_device *dev)
{
	struct at91_st_data *data = ced_to_at91_st(dev);

	/* Disable and flush pending timer interrupts */
	at91_sys_write(AT91_ST_IDR, AT91_ST_PITS | AT91_ST_ALMS);
	(void) at91_st_read(data, AT91_ST_SR);

	data->last_crtr = read_CRTR(data);
	switch (mode) {
	case CLOCK_EVT_MODE_PERIODIC:
		/* PIT for periodic irqs; fixed rate of 1/HZ */
		data->irqmask = AT91_ST_PITS;
		at91_st_write(data, AT91_ST_PIMR, LATCH);
		break;
	case CLOCK_EVT_MODE_ONESHOT:
		/* ALM for oneshot irqs, set by next_event()
		 * before 32 seconds have passed
		 */
		data->irqmask = AT91_ST_ALMS;
		at91_st_write(data, AT91_ST_RTAR, data->last_crtr);
		break;
	case CLOCK_EVT_MODE_SHUTDOWN:
	case CLOCK_EVT_MODE_UNUSED:
	case CLOCK_EVT_MODE_RESUME:
		data->irqmask = 0;
		break;
	}
	at91_st_write(data, AT91_ST_IER, data->irqmask);
}

static int at91_st_clock_event_next(unsigned long delta,
				   struct clock_event_device *ced)
{
	struct at91_st_data *data = ced_to_at91_st(ced);
	u32 alm;
	int status = 0;

	BUG_ON(delta < 2);

	/* The alarm IRQ uses absolute time (now+delta), not the relative
	 * time (delta) in our calling convention.  Like all clockevents
	 * using such "match" hardware, we have a race to defend against.
	 *
	 * Our defense here is to have set up the clockevent device so the
	 * delta is at least two.  That way we never end up writing RTAR
	 * with the value then held in CRTR ... which would mean the match
	 * wouldn't trigger until 32 seconds later, after CRTR wraps.
	 */
	alm = read_CRTR(data);

	/* Cancel any pending alarm; flush any pending IRQ */
	at91_st_write(data, AT91_ST_RTAR, alm);
	(void) at91_st_read(data, AT91_ST_SR);

	/* Schedule alarm by writing RTAR. */
	alm += delta;
	at91_st_write(data, AT91_ST_RTAR, alm);

	return status;
}

static void at91_st_register_clockevent(struct at91_st_data *data)
{
	struct clock_event_device *ced = &data->ced;

	memset(ced, 0, sizeof(*ced));

	ced->name = "at91_tick";
	ced->features = CLOCK_EVT_FEAT_PERIODIC | CLOCK_EVT_FEAT_ONESHOT;
	ced->shift = 32;
	ced->rating = 150;
	ced->set_next_event = at91_st_clock_event_next;
	ced->set_mode = at91_st_clock_event_mode;
	ced->mult = div_sc(AT91_SLOW_CLOCK, NSEC_PER_SEC, ced->shift);
	ced->max_delta_ns = clockevent_delta2ns(AT91_ST_ALMV, ced);
	ced->min_delta_ns = clockevent_delta2ns(2, ced) + 1;
	ced->cpumask = cpumask_of(0);

	dev_info(&data->pdev->dev, "used for clock events\n");

	clockevents_register_device(ced);
}

static int at91_st_register_clocksource(struct at91_st_data *data)
{
	struct clocksource *cs = &data->cs;

	cs->name = "32k_counter";
	cs->rating = 150;
	cs->read = at91_st_clocksource_read;
	cs->flags = CLOCK_SOURCE_IS_CONTINUOUS;
	cs->mask = CLOCKSOURCE_MASK(20);

	dev_info(&data->pdev->dev, "used as clock source\n");

	clocksource_register_hz(cs, AT91_SLOW_CLOCK);

	return 0;
}

static int at91_st_setup(struct at91_st_data *data,
			  struct platform_device *pdev)
{
	struct resource	*res;
	int		irq;
	int		ret = -ENXIO;

	memset(data, 0, sizeof(struct at91_st_data));
	data->pdev = pdev;

	res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	if (!res) {
		dev_err(&pdev->dev, "failed to get I/O memory\n");
		goto err0;
	}

	irq = platform_get_irq(pdev, 0);
	if (irq < 0) {
		dev_err(&pdev->dev, "failed to get irq\n");
		goto err0;
	}

	/* map memory, let mapbase point to our channel */
	data->mapbase = (void * __iomem)(res->start + AT91_VA_BASE_SYS);

	/* request irq using setup_irq() (too early for request_irq()) */
	data->irqaction.name = "at91_tick";
	data->irqaction.handler = at91_st_interrupt;
	data->irqaction.dev_id = data;
	data->irqaction.flags = IRQF_SHARED | IRQF_DISABLED |
				IRQF_TIMER  | IRQF_IRQPOLL;

	/* Disable all timer interrupts, and clear any pending ones */
	at91_sys_write(AT91_ST_IDR,
		AT91_ST_PITS | AT91_ST_WDOVF | AT91_ST_RTTINC | AT91_ST_ALMS);
	(void) at91_sys_read(AT91_ST_SR);

	/* The 32KiHz "Slow Clock" (tick every 30517.58 nanoseconds) is used
	 * directly for the clocksource and all clockevents, after adjusting
	 * its prescaler from the 1 Hz default.
	 */
	at91_sys_write(AT91_ST_RTMR, 1);

	/*
	 * Register clocksource.  The high order bits of PIV are unused,
	 * so this isn't a 32-bit counter unless we get clockevent irqs.
	 */
	at91_st_register_clocksource(data);

	/* Set up irq handler */
	setup_irq(irq, &data->irqaction);

	/* Set up and register clockevents */
	at91_st_register_clockevent(data);

	return 0;

err0:
	return ret;
}

static int __devinit at91_st_probe(struct platform_device *pdev)
{
	int ret;
	struct at91_st_data *data;

	if (!is_early_platform_device(pdev)) {
		pr_info("at91_st.%d: call via non early plaform\n", pdev->id);
		return 0;
	}

	data = kmalloc(sizeof(struct at91_st_data), GFP_KERNEL);
	if (data == NULL) {
		dev_err(&pdev->dev, "failed to allocate driver data\n");
		return -ENOMEM;
	}

	ret = at91_st_setup(data, pdev);

	if (ret)
		kfree(data);

	return ret;
}

static int __devexit at91_st_remove(struct platform_device *pdev)
{
	return -EBUSY; /* cannot unregister clockevent and clocksource */
}

static struct platform_driver at91_st_device_driver = {
	.probe		= at91_st_probe,
	.remove		= __devexit_p(at91_st_remove),
	.driver		= {
		.name	= "at91_st",
	}
};

early_platform_init("earlytimer", &at91_st_device_driver);
