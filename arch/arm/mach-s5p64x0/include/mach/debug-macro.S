/* linux/arch/arm/mach-s5p64x0/include/mach/debug-macro.S
 *
 * Copyright (c) 2009-2010 Samsung Electronics Co., Ltd.
 *		http://www.samsung.com
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
*/

/* pull in the relevant register and map files. */

#include <plat/map-base.h>
#include <plat/map-s5p.h>

#include <plat/regs-serial.h>

	.macro addruart, rx, tmp
		mrc	p15, 0, \rx, c1, c0
		tst	\rx, #1			@ MMU enabled?
		bne	1002f

		mov	\rx, #0xE0000000
		orr	\rx, \rx, #0x00100000
		ldr	\rx, [\rx, #0x118 ]
		and	\rx, \rx, #0xff000
		teq	\rx, #0x50000		@@ S5P6450
		ldreq	\rx, =0xEC800000
		movne	\rx, #0xEC000000	@@ S5P6440
		b	1003f
	1002:
		ldrne	\rx, = S3C_VA_UART
	1003:
#if CONFIG_DEBUG_S3C_UART != 0
		add	\rx, \rx, #(0x400 * CONFIG_DEBUG_S3C_UART)
#endif
	.endm

#include <plat/debug-macro.S>
