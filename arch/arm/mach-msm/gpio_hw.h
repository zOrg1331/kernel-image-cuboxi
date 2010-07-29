/* Copyright (c) 2007, Google, Inc.
 * Copyright (c) 2008-2010, Code Aurora Forum. All rights reserved.
 *
 * This software is licensed under the terms of the GNU General Public
 * License version 2, as published by the Free Software Foundation, and
 * may be copied, distributed, and modified under those terms.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 */
#ifndef __ARCH_ARM_MACH_MSM_GPIO_HW_H
#define __ARCH_ARM_MACH_MSM_GPIO_HW_H

#include <mach/msm_iomap.h>

#if defined(CONFIG_ARCH_MSM7X30)
#define GPIO1_REG(off) (MSM_GPIO1_BASE + (off))
#define GPIO2_REG(off) (MSM_GPIO2_BASE + 0x400 + (off))
#else
#define GPIO1_REG(off) (MSM_GPIO1_BASE + 0x800 + (off))
#define GPIO2_REG(off) (MSM_GPIO2_BASE + 0xC00 + (off))
#endif

#if defined(CONFIG_ARCH_QSD8X50)
#include "gpio_hw-8x50.h"
#elif defined(CONFIG_ARCH_MSM7X30)
#include "gpio_hw-7x30.h"
#else
#include "gpio_hw-7xxx.h"
#endif

#endif
