/*
 * Structures and registers for GPIO access in the Nomadik SoC
 *
 * Copyright (C) 2008 STMicroelectronics
 *     Author: Prafulla WADASKAR <prafulla.wadaskar@st.com>
 * Copyright (C) 2009 Alessandro Rubini <rubini@unipv.it>
 * Copyright (C) 2011 ST-Ericsson SA
 *  Author: Rabin Vincent <rabin.vincent@stericsson.com> for ST-Ericsson
 *  Authot: Linus Walleij <linus.wallej@linaro.org>
 *
 * Pin config API based on arch/arm/mach-pxa/include/mach/mfp.h:
 *   Copyright (C) 2007 Marvell International Ltd.
 *   eric miao <eric.miao@marvell.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */
#ifndef __GPIO_NOMADIK_H
#define __GPIO_NOMADIK_H

#include <linux/gpio.h>
#include <asm-generic/gpio.h>

/*
 * Custom pin configuration options
 */
#define GPIO_CONFIG_NMK_ALTF_GPIO	(GPIO_CONFIG_CUSTOM_BASE+0)
#define GPIO_CONFIG_NMK_ALTF_A		(GPIO_CONFIG_CUSTOM_BASE+1)
#define GPIO_CONFIG_NMK_ALTF_B		(GPIO_CONFIG_CUSTOM_BASE+2)
#define GPIO_CONFIG_NMK_ALTF_C		(GPIO_CONFIG_CUSTOM_BASE+3)
#define GPIO_CONFIG_NMK_GET_ALTF	(GPIO_CONFIG_CUSTOM_BASE+4)
#define GPIO_CONFIG_NMK_SLPM_INPUT	(GPIO_CONFIG_CUSTOM_BASE+5)
#define GPIO_CONFIG_NMK_WAKEUP_ENABLE	(GPIO_CONFIG_CUSTOM_BASE+6)
#define GPIO_CONFIG_NMK_SLPM_NOCHANGE	(GPIO_CONFIG_CUSTOM_BASE+7)
#define GPIO_CONFIG_NMK_WAKEUP_DISABLE	(GPIO_CONFIG_CUSTOM_BASE+8)
#define GPIO_CONFIG_NMK_SETUP_PIN	(GPIO_CONFIG_CUSTOM_BASE+9)
#define GPIO_CONFIG_NMK_SETUP_PIN_LEGACY (GPIO_CONFIG_CUSTOM_BASE+10)

/*
 * Platform data to register a block: only the initial gpio/irq number.
 */
struct nmk_gpio_platform_data {
	char *name;
	int first_gpio;
	int first_irq;
	int num_gpio;
	u32 (*get_secondary_status)(unsigned int bank);
	void (*set_ioforce)(bool enable);
	bool supports_sleepmode;
};

/**
 * nmk_gpio_pin_config - configuration data for a single GPIO pin
 * @altfunc: the alternate function setting for the pin
 * @bias_mode: pull up/down/none (float) bias setting for the pin
 * @output: if this pin is to be configured for output or not
 * @outval: if configured for output, the default output value (0 or 1)
 * @sleep_mode: if true, this pin will wake up the system in sleep mode
 *	(DB8500v2) or force the pin to retain its value and not become an
 *	input (as is the default on DB8500v1, pull up/down is retained)
 */
struct nmk_gpio_pin_config {
	int pin;
	u16 altfunc;
	u16 bias_mode;
	bool output;
	int outval;
	bool sleep_mode;
};

/* A horde of exported functions */
extern void nmk_gpio_wakeups_suspend(void);
extern void nmk_gpio_wakeups_resume(void);
extern void nmk_gpio_clocks_enable(void);
extern void nmk_gpio_clocks_disable(void);
extern void nmk_gpio_read_pull(int gpio_bank, u32 *pull_up);

/*
 * pin configurations are represented by 32-bit integers:
 *
 *	bit  0.. 8 - Pin Number (512 Pins Maximum)
 *	bit  9..10 - Alternate Function Selection
 *	bit 11..12 - Pull up/down state
 *	bit     13 - Sleep mode behaviour
 *	bit     14 - Direction
 *	bit     15 - Value (if output)
 *	bit 16..18 - SLPM pull up/down state
 *	bit 19..20 - SLPM direction
 *	bit 21..22 - SLPM Value (if output)
 *
 * to facilitate the definition, the following macros are provided
 *
 * PIN_CFG_DEFAULT - default config (0):
 *		     pull up/down = disabled
 *		     sleep mode = input/wakeup
 *		     direction = input
 *		     value = low
 *		     SLPM direction = same as normal
 *		     SLPM pull = same as normal
 *		     SLPM value = same as normal
 *
 * PIN_CFG	   - default config with alternate function
 */

typedef unsigned long pin_cfg_t;

/* Alternate functions: function C is set in hw by setting both A and B */
#define NMK_GPIO_ALT_GPIO	0
#define NMK_GPIO_ALT_A	1
#define NMK_GPIO_ALT_B	2
#define NMK_GPIO_ALT_C	(NMK_GPIO_ALT_A | NMK_GPIO_ALT_B)

/* Pull up/down values */
enum nmk_gpio_pull {
	NMK_GPIO_PULL_NONE,
	NMK_GPIO_PULL_UP,
	NMK_GPIO_PULL_DOWN,
};

/* Sleep mode */
enum nmk_gpio_slpm {
	NMK_GPIO_SLPM_INPUT,
	NMK_GPIO_SLPM_WAKEUP_ENABLE = NMK_GPIO_SLPM_INPUT,
	NMK_GPIO_SLPM_NOCHANGE,
	NMK_GPIO_SLPM_WAKEUP_DISABLE = NMK_GPIO_SLPM_NOCHANGE,
};

#define PIN_NUM_MASK		0x1ff
#define PIN_NUM(x)		((x) & PIN_NUM_MASK)

#define PIN_ALT_SHIFT		9
#define PIN_ALT_MASK		(0x3 << PIN_ALT_SHIFT)
#define PIN_ALT(x)		(((x) & PIN_ALT_MASK) >> PIN_ALT_SHIFT)
#define PIN_GPIO		(NMK_GPIO_ALT_GPIO << PIN_ALT_SHIFT)
#define PIN_ALT_A		(NMK_GPIO_ALT_A << PIN_ALT_SHIFT)
#define PIN_ALT_B		(NMK_GPIO_ALT_B << PIN_ALT_SHIFT)
#define PIN_ALT_C		(NMK_GPIO_ALT_C << PIN_ALT_SHIFT)

#define PIN_PULL_SHIFT		11
#define PIN_PULL_MASK		(0x3 << PIN_PULL_SHIFT)
#define PIN_PULL(x)		(((x) & PIN_PULL_MASK) >> PIN_PULL_SHIFT)
#define PIN_PULL_NONE		(NMK_GPIO_PULL_NONE << PIN_PULL_SHIFT)
#define PIN_PULL_UP		(NMK_GPIO_PULL_UP << PIN_PULL_SHIFT)
#define PIN_PULL_DOWN		(NMK_GPIO_PULL_DOWN << PIN_PULL_SHIFT)

#define PIN_SLPM_SHIFT		13
#define PIN_SLPM_MASK		(0x1 << PIN_SLPM_SHIFT)
#define PIN_SLPM(x)		(((x) & PIN_SLPM_MASK) >> PIN_SLPM_SHIFT)
#define PIN_SLPM_MAKE_INPUT	(NMK_GPIO_SLPM_INPUT << PIN_SLPM_SHIFT)
#define PIN_SLPM_NOCHANGE	(NMK_GPIO_SLPM_NOCHANGE << PIN_SLPM_SHIFT)
/* These two replace the above in DB8500v2+ */
#define PIN_SLPM_WAKEUP_ENABLE	(NMK_GPIO_SLPM_WAKEUP_ENABLE << PIN_SLPM_SHIFT)
#define PIN_SLPM_WAKEUP_DISABLE	(NMK_GPIO_SLPM_WAKEUP_DISABLE << PIN_SLPM_SHIFT)

#define PIN_DIR_SHIFT		14
#define PIN_DIR_MASK		(0x1 << PIN_DIR_SHIFT)
#define PIN_DIR(x)		(((x) & PIN_DIR_MASK) >> PIN_DIR_SHIFT)
#define PIN_DIR_INPUT		(0 << PIN_DIR_SHIFT)
#define PIN_DIR_OUTPUT		(1 << PIN_DIR_SHIFT)

#define PIN_VAL_SHIFT		15
#define PIN_VAL_MASK		(0x1 << PIN_VAL_SHIFT)
#define PIN_VAL(x)		(((x) & PIN_VAL_MASK) >> PIN_VAL_SHIFT)
#define PIN_VAL_LOW		(0 << PIN_VAL_SHIFT)
#define PIN_VAL_HIGH		(1 << PIN_VAL_SHIFT)

#define PIN_SLPM_PULL_SHIFT	16
#define PIN_SLPM_PULL_MASK	(0x7 << PIN_SLPM_PULL_SHIFT)
#define PIN_SLPM_PULL(x)	\
	(((x) & PIN_SLPM_PULL_MASK) >> PIN_SLPM_PULL_SHIFT)
#define PIN_SLPM_PULL_NONE	\
	((1 + NMK_GPIO_PULL_NONE) << PIN_SLPM_PULL_SHIFT)
#define PIN_SLPM_PULL_UP	\
	((1 + NMK_GPIO_PULL_UP) << PIN_SLPM_PULL_SHIFT)
#define PIN_SLPM_PULL_DOWN	\
	((1 + NMK_GPIO_PULL_DOWN) << PIN_SLPM_PULL_SHIFT)

#define PIN_SLPM_DIR_SHIFT	19
#define PIN_SLPM_DIR_MASK	(0x3 << PIN_SLPM_DIR_SHIFT)
#define PIN_SLPM_DIR(x)		\
	(((x) & PIN_SLPM_DIR_MASK) >> PIN_SLPM_DIR_SHIFT)
#define PIN_SLPM_DIR_INPUT	((1 + 0) << PIN_SLPM_DIR_SHIFT)
#define PIN_SLPM_DIR_OUTPUT	((1 + 1) << PIN_SLPM_DIR_SHIFT)

#define PIN_SLPM_VAL_SHIFT	21
#define PIN_SLPM_VAL_MASK	(0x3 << PIN_SLPM_VAL_SHIFT)
#define PIN_SLPM_VAL(x)		\
	(((x) & PIN_SLPM_VAL_MASK) >> PIN_SLPM_VAL_SHIFT)
#define PIN_SLPM_VAL_LOW	((1 + 0) << PIN_SLPM_VAL_SHIFT)
#define PIN_SLPM_VAL_HIGH	((1 + 1) << PIN_SLPM_VAL_SHIFT)

/* Shortcuts.  Use these instead of separate DIR, PULL, and VAL.  */
#define PIN_INPUT_PULLDOWN	(PIN_DIR_INPUT | PIN_PULL_DOWN)
#define PIN_INPUT_PULLUP	(PIN_DIR_INPUT | PIN_PULL_UP)
#define PIN_INPUT_NOPULL	(PIN_DIR_INPUT | PIN_PULL_NONE)
#define PIN_OUTPUT_LOW		(PIN_DIR_OUTPUT | PIN_VAL_LOW)
#define PIN_OUTPUT_HIGH		(PIN_DIR_OUTPUT | PIN_VAL_HIGH)

#define PIN_SLPM_INPUT_PULLDOWN	(PIN_SLPM_DIR_INPUT | PIN_SLPM_PULL_DOWN)
#define PIN_SLPM_INPUT_PULLUP	(PIN_SLPM_DIR_INPUT | PIN_SLPM_PULL_UP)
#define PIN_SLPM_INPUT_NOPULL	(PIN_SLPM_DIR_INPUT | PIN_SLPM_PULL_NONE)
#define PIN_SLPM_OUTPUT_LOW	(PIN_SLPM_DIR_OUTPUT | PIN_SLPM_VAL_LOW)
#define PIN_SLPM_OUTPUT_HIGH	(PIN_SLPM_DIR_OUTPUT | PIN_SLPM_VAL_HIGH)

#define PIN_CFG_DEFAULT		(0)

#define PIN_CFG(num, alt)		\
	(PIN_CFG_DEFAULT |\
	 (PIN_NUM(num) | PIN_##alt))

#define PIN_CFG_INPUT(num, alt, pull)		\
	(PIN_CFG_DEFAULT |\
	 (PIN_NUM(num) | PIN_##alt | PIN_INPUT_##pull))

#define PIN_CFG_OUTPUT(num, alt, val)		\
	(PIN_CFG_DEFAULT |\
	 (PIN_NUM(num) | PIN_##alt | PIN_OUTPUT_##val))

/*
 * We want to keep this function outside the driver since it is only using the
 * externally visible gpio_config() function and merely twisting bits around
 * for the legacy pin configuration API.
 */
static inline int __nmk_config_pins(pin_cfg_t *cfgs, int num, bool sleep)
{
	pin_cfg_t cfg;
	int ret;
	int i;

	for (i = 0; i < num; i++) {
		cfg = cfgs[i];

		if (sleep) {
			/*
			 * We reconfigure for sleep mode, mask off the
			 * normal configs and replace them with sleep mode
			 * configs and pass into the same legacy config
			 * function, simply. Zero values mean "same as in
			 * normal mode".
			 */
			int slpm_pull = PIN_SLPM_PULL(cfg);
			int slpm_output = PIN_SLPM_DIR(cfg);
			int slpm_val = PIN_SLPM_VAL(cfg);

			/* Override bias mode */
			if (slpm_pull) {
				cfg &= ~PIN_PULL_MASK;
				cfg |= (slpm_pull - 1) << PIN_PULL_SHIFT;
			}

			/* Override in/output mode */
			if (slpm_output) {
				cfg &= ~PIN_DIR_MASK;
				cfg |= (slpm_output - 1) << PIN_DIR_SHIFT;
			}

			/* Override output value */
			if (slpm_val) {
				cfg &= ~PIN_VAL_MASK;
				cfg |= (slpm_output - 1) << PIN_VAL_SHIFT;
			}
		}

		ret = gpio_config(PIN_NUM(cfg),
				  GPIO_CONFIG_NMK_SETUP_PIN_LEGACY,
				  (unsigned long *) &cfg);
		if (ret < 0)
			return ret;
	}
	return 0;
}

extern int __nmk_config_pins(pin_cfg_t *cfgs, int num, bool sleep);

static inline int nmk_config_pin(pin_cfg_t cfg, bool sleep)
{
	return __nmk_config_pins(&cfg, 1, sleep);
}

static inline int nmk_config_pins(pin_cfg_t *cfgs, int num)
{
	return __nmk_config_pins(cfgs, num, false);
}

static inline int nmk_config_pins_sleep(pin_cfg_t *cfgs, int num)
{
	return __nmk_config_pins(cfgs, num, true);
}

#endif
