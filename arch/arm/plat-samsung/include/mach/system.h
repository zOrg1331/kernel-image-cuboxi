/* linux/arch/arm/plat-samsung/include/mach/idle.h
 *
 * Copyright (c) 2009 Samsung Electronics Co., Ltd.
 *		http://www.samsung.com/
 *
 * Idle support
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
*/

#ifndef __ASM_PLAT_SYSTEM_H
#define __ASM_PLAT_SYSTEM_H __FILE__

void (*s3c_idle_fn)(void);

static void s3c_default_idle(void)
{
	/* nothing here yet */
}

static void arch_idle(void)
{
	if (s3c_idle_fn != NULL)
		(s3c_idle_fn)();
	else
		s3c_default_idle();
}

static void arch_reset(char mode, const char *cmd)
{
	/* nothing here yet */
}

#endif /* __ASM_PLAT_SYSTEM_H */
