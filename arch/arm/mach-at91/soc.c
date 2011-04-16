/*
 *
 * Copyright (C) 2007 Atmel Corporation.
 * Copyright (C) 2011 Jean-Christophe PLAGNIOL-VILLARD <plagnioj@jcrosoft.com>
 *
 * Under GPLv2
 *
 */

#include <linux/module.h>
#include <linux/io.h>

#include <asm/mach/map.h>

#include <mach/hardware.h>
#include <mach/cpu.h>

#include "cpu.h"
#include "soc.h"
#include "generic.h"

static struct at91_soc __initdata current_soc;
static void __init at91_add_gpio(void);

struct at91_cpu_id cpu_id;
EXPORT_SYMBOL(cpu_id);

void __init at91rm9200_set_type(int type)
{
	if (type == ARCH_REVISON_9200_PQFP)
		cpu_id.is_at91rm9200 |= ARCH_REVISON_9200_PQFP;
	else
		cpu_id.is_at91rm9200 &= ~ARCH_REVISON_9200_PQFP;
}

void __init at91_init_interrupts(unsigned int *priority)
{
	if (!priority)
		priority = current_soc.default_irq_priority;

	/* Initialize the AIC interrupt controller */
	at91_aic_init(priority);

	/* Enable GPIO interrupts */
	at91_gpio_irq_setup();
}

static struct map_desc at91_io_desc __initdata = {
	.virtual	= AT91_VA_BASE_SYS,
	.pfn		= __phys_to_pfn(AT91_BASE_SYS),
	.length		= SZ_16K,
	.type		= MT_DEVICE,
};

void __init at91_initialize(unsigned long main_clock)
{
	/* Map peripherals */
	iotable_init(&at91_io_desc, 1);

	if (__cpu_is_at572d940hf()) {
		cpu_id.is_at572d940hf = 1;
		current_soc = at572d940hf_soc;
	} else if (__cpu_is_at91cap9()) {
		cpu_id.is_at91cap9 = AT91_CAP9;
		if (__cpu_is_at91cap9_revB())
			cpu_id.is_at91cap9 |= AT91_CAP9_REV_B;
		else if (__cpu_is_at91cap9_revC())
			cpu_id.is_at91cap9 |= AT91_CAP9_REV_C;
		current_soc = at91cap9_soc;
	} else if (__cpu_is_at91rm9200()) {
		cpu_id.is_at91rm9200 = 1;
		current_soc = at91rm9200_soc;
	} else if (__cpu_is_at91sam9260()) {
		cpu_id.is_at91sam9260 = AT91_SAM9260;
		if (__cpu_is_at91sam9xe())
			cpu_id.is_at91sam9260 |= AT91_SAM9XE;
		current_soc = at91sam9260_soc;
	} else if (__cpu_is_at91sam9261()) {
		cpu_id.is_at91sam9261 = 1;
		current_soc = at91sam9261_soc;
	} else if (__cpu_is_at91sam9263()) {
		cpu_id.is_at91sam9263 = 1;
		current_soc = at91sam9263_soc;
	} else if (__cpu_is_at91sam9g45()) {
		cpu_id.is_at91sam9g45 = AT91_SAM9G45;
		if (__cpu_is_at91sam9g45es())
			cpu_id.is_at91sam9g45 |= AT91_SAM9G45ES;
		else if (__cpu_is_at91sam9m10())
			cpu_id.is_at91sam9g45 |= AT91_SAM9M10;
		else if (__cpu_is_at91sam9g46())
			cpu_id.is_at91sam9g45 |= AT91_SAM9G46;
		else if (__cpu_is_at91sam9m11())
			cpu_id.is_at91sam9g45 |= AT91_SAM9M11;
		current_soc = at91sam9g45_soc;
	} else if (__cpu_is_at91sam9rl()) {
		cpu_id.is_at91sam9rl = 1;
		current_soc = at91sam9rl_soc;
	} else if (__cpu_is_at91sam9x5()) {
		cpu_id.is_at91sam9x5 = AT91_SAM9X5;
		if (__cpu_is_at91sam9g15())
			cpu_id.is_at91sam9x5 |= AT91_SAM9G15;
		else if (__cpu_is_at91sam9g35())
			cpu_id.is_at91sam9x5 |= AT91_SAM9G35;
		else if (__cpu_is_at91sam9x35())
			cpu_id.is_at91sam9x5 |= AT91_SAM9X35;
		else if (__cpu_is_at91sam9g25())
			cpu_id.is_at91sam9x5 |= AT91_SAM9G25;
		else if (__cpu_is_at91sam9x25())
			cpu_id.is_at91sam9x5 |= AT91_SAM9X25;
		current_soc = at91sam9x5_soc;
	} else {
		panic("Impossible to detect the CPU type");
	}

	pr_info("AT91: detected soc: %s\n", current_soc.name);

	current_soc.init(main_clock);

	/* Register GPIO subsystem */
	at91_add_gpio();
}

/* --------------------------------------------------------------------
 *  GPIO
 * -------------------------------------------------------------------- */

static struct resource pioa_resources[] = {
	[0] = RES_MEM(SZ_512),
	[1] = RES_IRQ(),
};

static struct platform_device at91_pioa_device = {
	.name		= "at91_gpio",
	.id		= 0,
	.resource	= pioa_resources,
	.num_resources	= ARRAY_SIZE(pioa_resources),
};

static struct resource piob_resources[] = {
	[0] = RES_MEM(SZ_512),
	[1] = RES_IRQ(),
};

static struct platform_device at91_piob_device = {
	.name		= "at91_gpio",
	.id		= 1,
	.resource	= piob_resources,
	.num_resources	= ARRAY_SIZE(piob_resources),
};

static struct resource pioc_resources[] = {
	[0] = RES_MEM(SZ_512),
	[1] = RES_IRQ(),
};

static struct platform_device at91_pioc_device = {
	.name		= "at91_gpio",
	.id		= 2,
	.resource	= pioc_resources,
	.num_resources	= ARRAY_SIZE(pioc_resources),
};

static struct resource piod_resources[] = {
	[0] = RES_MEM(SZ_512),
	[1] = RES_IRQ(),
};

static struct platform_device at91_piod_device = {
	.name		= "at91_gpio",
	.id		= 3,
	.resource	= piod_resources,
	.num_resources	= ARRAY_SIZE(piod_resources),
};

static struct resource pioe_resources[] = {
	[0] = RES_MEM(SZ_512),
	[1] = RES_IRQ(),
};

static struct platform_device at91_pioe_device = {
	.name		= "at91_gpio",
	.id		= 4,
	.resource	= pioe_resources,
	.num_resources	= ARRAY_SIZE(pioe_resources),
};

static struct platform_device *at91_pio_devices[] __initdata = {
	&at91_pioa_device,
	&at91_piob_device,
	&at91_pioc_device,
	&at91_piod_device,
	&at91_pioe_device,
};

static void __init at91_add_gpio(void)
{
	struct at91_dev_resource *gpios = current_soc.gpio.resource;
	int nb = current_soc.gpio.num_resources;

	int i;
	struct resource *r;

	BUG_ON(!gpios || nb < 0 || nb > ARRAY_SIZE(at91_pio_devices));

	for (i = 0; i < nb; i++) {
		r = at91_pio_devices[i]->resource;
		set_resource_mem(&r[0], gpios[i].mmio_base);
		set_resource_irq(&r[1], gpios[i].irq);
	}

	early_platform_add_devices(at91_pio_devices, nb);
	early_platform_driver_register_all("early_at91_gpio");
	early_platform_driver_probe("early_at91_gpio", nb , 0);
}
