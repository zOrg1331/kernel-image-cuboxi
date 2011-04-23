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
}
