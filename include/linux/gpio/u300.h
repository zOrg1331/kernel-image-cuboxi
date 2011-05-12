/*
 * U300 GPIO platform data header
 * Copyright (C) 2011 ST-Ericsson SA
 * Written on behalf of Linaro for ST-Ericsson
 *
 * Author: Linus Walleij <linus.walleij@linaro.org>
 *
 * License terms: GNU General Public License (GPL) version 2
 */

/**
 * enum u300_gpio_variant - the type of U300 GPIO employed
 */
enum u300_gpio_variant {
	U300_GPIO_COH901335,
	U300_GPIO_COH901571_3_BS335,
	U300_GPIO_COH901571_3_BS365,
};

/**
 * struct u300_gpio_platform - U300 GPIO platform data
 * @variant: IP block variant
 * @ports: number of GPIO block ports
 * @gpio_base: first GPIO number for this block (use a free range)
 * @gpio_irq_base: first GPIO IRQ number for this block (use a free range)
 */
struct u300_gpio_platform {
	enum u300_gpio_variant variant;
	u8 ports;
	int gpio_base;
	int gpio_irq_base;
};
