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

#include "soc.h"
#include "generic.h"

static struct at91_soc __initdata current_soc;

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

	if (cpu_is_at572d940hf())
		current_soc = at572d940hf_soc;
	else if (cpu_is_at91cap9())
		current_soc = at91cap9_soc;
	else if (cpu_is_at91rm9200())
		current_soc = at91rm9200_soc;
	else if (cpu_is_at91sam9260())
		current_soc = at91sam9260_soc;
	else if (cpu_is_at91sam9261())
		current_soc = at91sam9261_soc;
	else if (cpu_is_at91sam9263())
		current_soc = at91sam9263_soc;
	else if (cpu_is_at91sam9g45())
		current_soc = at91sam9g45_soc;
	else if (cpu_is_at91sam9rl())
		current_soc = at91sam9rl_soc;
	else if (cpu_is_at91sam9x5())
		current_soc = at91sam9x5_soc;
	else
		panic("Impossible to detect the CPU type");

	pr_info("AT91: detected soc: %s\n", current_soc.name);

	current_soc.init(main_clock);
}
