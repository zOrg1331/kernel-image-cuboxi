/*
 * arch/arm/mach-at91/include/mach/cpu.h
 *
 * Copyright (C) 2006 SAN People
 * Copyright (C) 2011 Jean-Christophe PLAGNIOL-VILLARD <plagnioj@jcrosoft.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 */

#ifndef __MACH_CPU_H__
#define __MACH_CPU_H__

struct at91_cpu_id {
	u8 is_at572d940hf;
#define AT91_CAP9		(1 << 0)
#define AT91_CAP9_REV_B		(1 << 1)
#define AT91_CAP9_REV_C		(1 << 2)
	u8 is_at91cap9;
#define ARCH_REVISON_9200	(1 << 0)
#define ARCH_REVISON_9200_BGA	(0 << 1)
#define ARCH_REVISON_9200_PQFP	(1 << 1)
	u8 is_at91rm9200;
#define AT91_SAM9260		(1 << 0)
#define AT91_SAM9XE		(1 << 1)
	u8 is_at91sam9260;
	u8 is_at91sam9261;
	u8 is_at91sam9263;
	u8 is_at91sam9g10;
	u8 is_at91sam9g20;
#define AT91_SAM9G45		(1 << 0)
#define AT91_SAM9G45ES		(1 << 1)
#define AT91_SAM9M10		(1 << 2)
#define AT91_SAM9G46		(1 << 3)
#define AT91_SAM9M11		(1 << 4)
	u8 is_at91sam9g45;
	u8 is_at91sam9rl;
#define AT91_SAM9X5		(1 << 0)
#define AT91_SAM9G15		(1 << 1)
#define AT91_SAM9G35		(1 << 2)
#define AT91_SAM9X35		(1 << 3)
#define AT91_SAM9G25		(1 << 4)
#define AT91_SAM9X25		(1 << 5)
	u8 is_at91sam9x5;
};

extern struct at91_cpu_id cpu_id;

#ifdef CONFIG_ARCH_AT91RM9200
#define cpu_is_at91rm9200()	(cpu_id.is_at91rm9200)
#define cpu_is_at91rm9200_bga()	(!cpu_is_at91rm9200_pqfp())
#define cpu_is_at91rm9200_pqfp() (cpu_is_at91rm9200() && cpu_id.is_at91rm9200 & ARCH_REVISON_9200_PQFP)
#else
#define cpu_is_at91rm9200()	(0)
#define cpu_is_at91rm9200_bga()	(0)
#define cpu_is_at91rm9200_pqfp() (0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9260
#define cpu_is_at91sam9xe()	(cpu_id.is_at91sam9260 & AT91_SAM9XE)
#define cpu_is_at91sam9260()	(cpu_id.is_at91sam9260)
#else
#define cpu_is_at91sam9xe()	(0)
#define cpu_is_at91sam9260()	(0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9G20
#define cpu_is_at91sam9g20()	(cpu_id.is_at91sam9g20)
#else
#define cpu_is_at91sam9g20()	(0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9261
#define cpu_is_at91sam9261()	(cpu_id.is_at91sam9261)
#else
#define cpu_is_at91sam9261()	(0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9G10
#define cpu_is_at91sam9g10()	(cpu_id.is_at91sam9g10)
#else
#define cpu_is_at91sam9g10()	(0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9263
#define cpu_is_at91sam9263()	(cpu_id.is_at91sam9263)
#else
#define cpu_is_at91sam9263()	(0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9RL
#define cpu_is_at91sam9rl()	(cpu_id.is_at91sam9rl)
#else
#define cpu_is_at91sam9rl()	(0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9G45
#define cpu_is_at91sam9g45()	(cpu_id.is_at91sam9g45 & AT91_SAM9G45)
#define cpu_is_at91sam9g45es()	(cpu_id.is_at91sam9g45 & AT91_SAM9G45ES)
#define cpu_is_at91sam9m10()	(cpu_id.is_at91sam9g45 & AT91_SAM9M10)
#define cpu_is_at91sam9g46()	(cpu_id.is_at91sam9g45 & AT91_SAM9G46)
#define cpu_is_at91sam9m11()	(cpu_id.is_at91sam9g45 & AT91_SAM9M11)
#else
#define cpu_is_at91sam9g45()	(0)
#define cpu_is_at91sam9g45es()	(0)
#define cpu_is_at91sam9m10()	(0)
#define cpu_is_at91sam9g46()	(0)
#define cpu_is_at91sam9m11()	(0)
#endif

#ifdef CONFIG_ARCH_AT91SAM9X5
#define cpu_is_at91sam9x5()	(cpu_id.is_at91sam9x5 & AT91_SAM9X5)
#define cpu_is_at91sam9g15()	(cpu_id.is_at91sam9x5 & AT91_SAM9G15)
#define cpu_is_at91sam9g35()	(cpu_id.is_at91sam9x5 & AT91_SAM9G35)
#define cpu_is_at91sam9x35()	(cpu_id.is_at91sam9x5 & AT91_SAM9X35)
#define cpu_is_at91sam9g25()	(cpu_id.is_at91sam9x5 & AT91_SAM9G25)
#define cpu_is_at91sam9x25()	(cpu_id.is_at91sam9x5 & AT91_SAM9X25)
#else
#define cpu_is_at91sam9x5()	(0)
#define cpu_is_at91sam9g15()	(0)
#define cpu_is_at91sam9g35()	(0)
#define cpu_is_at91sam9x35()	(0)
#define cpu_is_at91sam9g25()	(0)
#define cpu_is_at91sam9x25()	(0)
#endif

#ifdef CONFIG_ARCH_AT91CAP9
#define cpu_is_at91cap9()	(cpu_id.is_at91cap9 & AT91_CAP9)
#define cpu_is_at91cap9_revB()	(cpu_id.is_at91cap9 & AT91_CAP9_REV_B)
#define cpu_is_at91cap9_revC()	(cpu_id.is_at91cap9 & AT91_CAP9_REV_C)
#else
#define cpu_is_at91cap9()	(0)
#define cpu_is_at91cap9_revB()	(0)
#define cpu_is_at91cap9_revC()	(0)
#endif

#ifdef CONFIG_ARCH_AT572D940HF
#define cpu_is_at572d940hf()	(cpu_id.is_at572d940hf)
#else
#define cpu_is_at572d940hf()	(0)
#endif

/*
 * Since this is ARM, we will never run on any AVR32 CPU. But these
 * definitions may reduce clutter in common drivers.
 */
#define cpu_is_at32ap7000()	(0)

#endif /* __MACH_CPU_H__ */
