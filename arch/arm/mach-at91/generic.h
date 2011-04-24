/*
 * linux/arch/arm/mach-at91/generic.h
 *
 *  Copyright (C) 2005 David Brownell
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */

#include <linux/clkdev.h>

 /* Processors */
extern void __init at91rm9200_set_type(int type);
extern void __init at91_initialize(unsigned long main_clock);
extern void __init at91x40_initialize(unsigned long main_clock);

 /* Interrupts */
extern void __init at91_init_interrupts(unsigned int priority[]);
extern void __init at91x40_init_interrupts(unsigned int priority[]);
extern void __init at91_aic_init(unsigned int priority[]);

 /* Timer */
struct sys_timer;
extern struct sys_timer at91_timer;
extern struct sys_timer at91_timer;
extern struct sys_timer at91x40_timer;

 /* Clocks */
extern int __init at91_clock_init(unsigned long main_clock);
extern struct clk* __init at91rm9200_get_uart_clock(int id);
extern struct clk* __init at91sam9260_get_uart_clock(int id);
extern struct clk* __init at91sam9261_get_uart_clock(int id);
extern struct clk* __init at91sam9263_get_uart_clock(int id);
extern struct clk* __init at91sam9rl_get_uart_clock(int id);
extern struct clk* __init at91sam9g45_get_uart_clock(int id);
extern struct clk* __init at91x40_get_uart_clock(int id);
extern struct clk* __init at91cap9_get_uart_clock(int id);
extern struct clk* __init at572d940hf_get_uart_clock(int id);
struct device;

 /* Power Management */
extern void at91_irq_suspend(void);
extern void at91_irq_resume(void);

/* reset */
extern void at91sam9_alt_reset(void);

 /* GPIO */
#define AT91RM9200_PQFP		3	/* AT91RM9200 PQFP package has 3 banks */
#define AT91RM9200_BGA		4	/* AT91RM9200 BGA package has 4 banks */

extern void __init at91_gpio_irq_setup(void);

extern void (*at91_arch_reset)(void);
extern int at91_extern_irq;
