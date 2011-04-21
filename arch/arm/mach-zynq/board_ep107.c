/* arch/arm/mach-zynq/board_ep107.c
 *
 * This file contains code specific to the Xilinx EP107 board.
 *
 *  Copyright (C) 2011 Xilinx
 *
 * based on /arch/arm/mach-realview/core.c
 *
 *  Copyright (C) 1999 - 2003 ARM Limited
 *  Copyright (C) 2000 Deep Blue Solutions Ltd
 *
 * This software is licensed under the terms of the GNU General Public
 * License version 2, as published by the Free Software Foundation, and
 * may be copied, distributed, and modified under those terms.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

#include <linux/platform_device.h>
#include <linux/clkdev.h>

#include <asm/mach-types.h>
#include <asm/mach/arch.h>

#include <mach/zynq_soc.h>
#include <mach/irqs.h>
#include <mach/memory.h>
#include "common.h"

/*
 * Fixed clocks for now
 */

static struct clk ref50_clk = {
	.rate	= 50000000,
};

/* Create all the platform devices for the board */

static struct resource uart0[] = {
	{
		.start = UART0_PHYS,
		.end = UART0_PHYS + 0xFFF,
		.flags = IORESOURCE_MEM,
	}, {
		.start = IRQ_UART0,
		.end = IRQ_UART0,
		.flags = IORESOURCE_IRQ,
	},
};

static struct platform_device uart_device0 = {
	.name = "xuartpss",
	.id = 0,
	.dev = {
		.platform_data = &ref50_clk.rate,
	},
	.resource = uart0,
	.num_resources = ARRAY_SIZE(uart0),
};

static struct platform_device *xilinx_pdevices[] __initdata = {
	&uart_device0,
};

/**
 * board_ep107_init - Board specific initialization for the Xilinx EP107 board.
 *
 **/
static void __init board_ep107_init(void)
{
	xilinx_system_init();
	platform_add_devices(&xilinx_pdevices[0], ARRAY_SIZE(xilinx_pdevices));
}

MACHINE_START(XILINX_EP107, "Xilinx EP107")
	.boot_params    = PLAT_PHYS_OFFSET + 0x00000100,
	.map_io         = xilinx_map_io,
	.init_irq       = xilinx_irq_init,
	.init_machine   = board_ep107_init,
	.timer          = &xttcpss_sys_timer,
MACHINE_END
