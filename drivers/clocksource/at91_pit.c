/*
 * at91sam926x_time.c - Periodic Interval Timer (PIT) for at91sam926x
 *
 * Copyright (C) 2005-2006 M. Amine SAYA, ATMEL Rousset, France
 * Revision	 2005 M. Nicolas Diremdjian, ATMEL Rousset, France
 * Converted to ClockSource/ClockEvents by David Brownell.
 * Copyright (C) 2011 Jean-Christophe PLAGNIOL-VILLARD <plagnioj@jcrosoft.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */
#include <linux/init.h>
#include <linux/platform_device.h>
#include <linux/interrupt.h>
#include <linux/irq.h>
#include <linux/kernel.h>
#include <linux/clk.h>
#include <linux/clockchips.h>
#include <linux/slab.h>

#include <mach/at91_pit.h>

struct at91_pit_data {
	void __iomem *mapbase;
	u32 pit_cycle;		/* write-once */
	u32 pit_cnt;		/* access only w/system irq blocked */
	struct clock_event_device ced;
	struct clocksource cs;
	struct irqaction irqaction;
	struct platform_device *pdev;
};

#define PIT_CPIV(x)	((x) & AT91_PIT_CPIV)
#define PIT_PICNT(x)	(((x) & AT91_PIT_PICNT) >> 20)

static inline unsigned int at91_pit_read(struct at91_pit_data *data,
					 unsigned int reg_offset)
{
	return __raw_readl(data->mapbase + reg_offset);
}

static inline void at91_pit_write(struct at91_pit_data *data,
			unsigned int reg_offset, unsigned long value)
{
	__raw_writel(value, data->mapbase + reg_offset);
}

static struct at91_pit_data *cs_to_at91_pit(struct clocksource *cs)
{
	return container_of(cs, struct at91_pit_data, cs);
}

static struct at91_pit_data *ced_to_at91_pit(struct clock_event_device *ced)
{
	return container_of(ced, struct at91_pit_data, ced);
}

/*
 * Clocksource:  just a monotonic counter of MCK/16 cycles.
 * We don't care whether or not PIT irqs are enabled.
 */
static cycle_t at91_pit_clocksource_read(struct clocksource *cs)
{
	struct at91_pit_data *data = cs_to_at91_pit(cs);
	unsigned long flags;
	u32 elapsed;
	u32 t;

	raw_local_irq_save(flags);
	elapsed = data->pit_cnt;
	t = at91_pit_read(data, AT91_PIT_PIIR);
	raw_local_irq_restore(flags);

	elapsed += PIT_PICNT(t) * data->pit_cycle;
	elapsed += PIT_CPIV(t);
	return elapsed;
}


/*
 * Clockevent device:  interrupts every 1/HZ (== pit_cycles * MCK/16)
 */
static void at91_pit_clock_event_mode(enum clock_event_mode mode,
				      struct clock_event_device *dev)
{
	struct at91_pit_data *data = ced_to_at91_pit(dev);
	u32 tmp;

	switch (mode) {
	case CLOCK_EVT_MODE_PERIODIC:
		/* update clocksource counter */
		tmp = PIT_PICNT(at91_pit_read(data, AT91_PIT_PIVR));
		data->pit_cnt += data->pit_cycle * tmp;
		at91_pit_write(data, AT91_PIT_MR, (data->pit_cycle - 1)
				| AT91_PIT_PITEN | AT91_PIT_PITIEN);
		break;
	case CLOCK_EVT_MODE_ONESHOT:
		BUG();
		/* FALLTHROUGH */
	case CLOCK_EVT_MODE_SHUTDOWN:
	case CLOCK_EVT_MODE_UNUSED:
		/* disable irq, leaving the clocksource active */
		at91_pit_write(data, AT91_PIT_MR,
				(data->pit_cycle - 1) | AT91_PIT_PITEN);
		break;
	case CLOCK_EVT_MODE_RESUME:
		break;
	}
}


/*
 * IRQ handler for the timer.
 */
static irqreturn_t at91_pit_interrupt(int irq, void *dev_id)
{
	struct at91_pit_data *data = (struct at91_pit_data*)dev_id;

	/*
	 * irqs should be disabled here, but as the irq is shared they are only
	 * guaranteed to be off if the timer irq is registered first.
	 */
	WARN_ON_ONCE(!irqs_disabled());

	/* The PIT interrupt may be disabled, and is shared */
	if ((data->ced.mode == CLOCK_EVT_MODE_PERIODIC)
			&& (at91_pit_read(data, AT91_PIT_SR) & AT91_PIT_PITS)) {
		unsigned nr_ticks;

		/* Get number of ticks performed before irq, and ack it */
		nr_ticks = PIT_PICNT(at91_pit_read(data, AT91_PIT_PIVR));
		do {
			data->pit_cnt += data->pit_cycle;
			data->ced.event_handler(&data->ced);
			nr_ticks--;
		} while (nr_ticks);

		return IRQ_HANDLED;
	}

	return IRQ_NONE;
}

static void at91_pit_stop(struct at91_pit_data *data)
{
	/* Disable timer and irqs */
	at91_pit_write(data, AT91_PIT_MR, 0);
}

static void at91_pit_reset(struct at91_pit_data *data)
{
	/* Disable timer and irqs */
	at91_pit_stop(data);

	/* Clear any pending interrupts, wait for PIT to stop counting */
	while (PIT_CPIV(at91_pit_read(data, AT91_PIT_PIVR)) != 0)
		cpu_relax();

	/* Start PIT but don't enable IRQ */
	at91_pit_write(data, AT91_PIT_MR, (data->pit_cycle - 1) | AT91_PIT_PITEN);
}

static int at91_pit_clocksource_enable(struct clocksource *cs)
{
	struct at91_pit_data *data = cs_to_at91_pit(cs);

	at91_pit_reset(data);

	return 0;
}

static void at91_pit_clocksource_resume(struct clocksource *cs)
{
	struct at91_pit_data *data = cs_to_at91_pit(cs);

	at91_pit_reset(data);
}

static void at91_pit_clocksource_disable(struct clocksource *cs)
{
	struct at91_pit_data *data = cs_to_at91_pit(cs);

	at91_pit_stop(data);
}

static void at91_pit_register_clockevent(struct at91_pit_data *data,
					 unsigned long pit_rate)
{
	struct clock_event_device *ced = &data->ced;

	memset(ced, 0, sizeof(*ced));

	ced->name = "pit";
	ced->features = CLOCK_EVT_FEAT_PERIODIC;
	ced->shift = 32;
	ced->rating = 100;
	ced->set_mode = at91_pit_clock_event_mode;
	ced->cpumask = cpumask_of(0);
	ced->mult = div_sc(pit_rate, NSEC_PER_SEC, ced->shift);

	dev_info(&data->pdev->dev, "used for clock events\n");

	clockevents_register_device(ced);
}

static int at91_pit_register_clocksource(struct at91_pit_data *data,
					 unsigned long pit_rate)
{
	struct clocksource *cs = &data->cs;
	unsigned bits;

	cs->name = "pit";
	cs->rating = 175;
	cs->shift = 20;
	cs->read = at91_pit_clocksource_read;
	cs->enable = at91_pit_clocksource_enable;
	cs->disable = at91_pit_clocksource_disable;
	cs->suspend = at91_pit_clocksource_disable;
	cs->resume = at91_pit_clocksource_resume;
	cs->flags = CLOCK_SOURCE_IS_CONTINUOUS;

	cs->mult = clocksource_hz2mult(pit_rate, cs->shift);
	bits = 12 /* PICNT */ + ilog2(data->pit_cycle) /* PIV */;
	cs->mask = CLOCKSOURCE_MASK(bits);

	dev_info(&data->pdev->dev, "used as clock source\n");

	clocksource_register_hz(cs, pit_rate);

	return 0;
}

static int at91_pit_setup(struct at91_pit_data *data,
			  struct platform_device *pdev)
{
	unsigned long	pit_rate;
	struct resource	*res;
	int		irq;
	int		ret = -ENXIO;

	memset(data, 0, sizeof(struct at91_pit_data));
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
	data->irqaction.handler = at91_pit_interrupt;
	data->irqaction.dev_id = data;
	data->irqaction.flags = IRQF_SHARED | IRQF_DISABLED |
				IRQF_TIMER  | IRQF_IRQPOLL;

	/*
	 * Use our actual MCK to figure out how many MCK/16 ticks per
	 * 1/HZ period (instead of a compile-time constant LATCH).
	 */
	pit_rate = clk_get_rate(clk_get(NULL, "mck")) / 16;
	data->pit_cycle = (pit_rate + HZ/2) / HZ;
	WARN_ON(((data->pit_cycle - 1) & ~AT91_PIT_PIV) != 0);

	/* Initialize and enable the timer */
	at91_pit_reset(data);

	/*
	 * Register clocksource.  The high order bits of PIV are unused,
	 * so this isn't a 32-bit counter unless we get clockevent irqs.
	 */
	at91_pit_register_clocksource(data, pit_rate);

	/* Set up irq handler */
	setup_irq(irq, &data->irqaction);

	/* Set up and register clockevents */
	at91_pit_register_clockevent(data, pit_rate);

	return 0;

err0:
	return ret;
}

static int __devinit at91_pit_probe(struct platform_device *pdev)
{
	int ret;
	struct at91_pit_data *data;

	if (!is_early_platform_device(pdev)) {
		pr_info("at91_pit.%d: call via non early plaform\n", pdev->id);
		return 0;
	}

	data = kmalloc(sizeof(struct at91_pit_data), GFP_KERNEL);
	if (data == NULL) {
		dev_err(&pdev->dev, "failed to allocate driver data\n");
		return -ENOMEM;
	}

	ret = at91_pit_setup(data, pdev);

	if (ret)
		kfree(data);

	return ret;
}

static int __devexit at91_pit_remove(struct platform_device *pdev)
{
	return -EBUSY; /* cannot unregister clockevent and clocksource */
}

static struct platform_driver at91_pit_device_driver = {
	.probe		= at91_pit_probe,
	.remove		= __devexit_p(at91_pit_remove),
	.driver		= {
		.name	= "at91_pit",
	}
};

early_platform_init("earlytimer", &at91_pit_device_driver);
