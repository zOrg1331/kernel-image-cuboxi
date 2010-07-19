/*
 * linux/drivers/serial/8250_pnx.c
 *
 * Copyright (C) ST-Ericsson SA 2010
 * Author: Ludovic Barre <ludovic.barre@stericsson.com> for ST-Ericsson.
 * License terms:  GNU General Public License (GPL), version 2
 */

#include <linux/serial_core.h>
#include <linux/io.h>
#include <linux/clk.h>
#include <linux/interrupt.h>
#include <linux/irq.h>

#include <mach/serial.h>
#include <mach/hardware.h>
#include <mach/clock.h>

/* Register description for FDIV_CTRL */
/* UART FDIV_CTRL Register (8 bits) */
#define UARTX_FDIV_CTRL_OFFSET         0xC00
/* UART FDIV_M Register (16 bits) */
#define UARTX_FDIV_M_OFFSET            0xC04
/* UART FDIV_N Register (16 bits) */
#define UARTX_FDIV_N_OFFSET            0xC08

/* Bits definition for register UARTX_FDIV_CTRL */
#define UARTX_FDIV_ENABLE_SHIFT  7
#define UARTX_FDIV_ENABLE_FIELD  (0xFFFFFFFF - (0x1UL<<UARTX_FDIV_ENABLE_SHIFT))
#define UARTX_FDIV_ENABLE_OFF    (0x0UL<<UARTX_FDIV_ENABLE_SHIFT)
#define UARTX_FDIV_ENABLE_ON     (0x1UL<<UARTX_FDIV_ENABLE_SHIFT)
#define UARTX_FDIV_ENABLE        (0x1UL<<UARTX_FDIV_ENABLE_SHIFT)
#define UARTX_CLKSEL_SHIFT       0
#define UARTX_CLKSEL_FIELD       (0xFFFFFFFF - (0x3UL<<UARTX_CLKSEL_SHIFT))
#define UARTX_CLKSEL_PCLK        (0x0UL<<UARTX_CLKSEL_SHIFT)
#define UARTX_CLKSEL_13M         (0x1UL<<UARTX_CLKSEL_SHIFT)
#define UARTX_CLKSEL_26M         (0x2UL<<UARTX_CLKSEL_SHIFT)
#define UARTX_CLKSEL_3           (0x3UL<<UARTX_CLKSEL_SHIFT)

/*
 * console and pctools has needed to start before serial_init
 * (with cgu interface)
 */
static int uart_enable_clock(struct uart_port *port)
{
	u32 v;
	v = readl(CGU_GATESC1_REG);

	if (port->irq == IRQ_UART1)
		v |= CGU_UART1EN_1;
	else if (port->irq == IRQ_UART2)
		v |= CGU_UART2EN_1;

	writel(v, CGU_GATESC1_REG);

	return 0;
}

static int uart_disable_clock(struct uart_port *port)
{
	u32 v;
	v = readl(CGU_GATESC1_REG);

	if (port->irq == IRQ_UART1)
		v &= ~CGU_UART1EN_0;
	else if (port->irq == IRQ_UART2)
		v &= ~CGU_UART2EN_0;

	writel(v, CGU_GATESC1_REG);

	return 0;
}

unsigned int serial8250_enable_clock(struct uart_port *port)
{
	struct u6_uart *uart_u6 = port->private_data;

	if (!uart_u6)
		return uart_enable_clock(port);

	if (IS_ERR(uart_u6->uartClk)) {
		printk(KERN_WARNING "%s - uart clock failed error:%ld\n",
		       __func__, PTR_ERR(uart_u6->uartClk));
		return PTR_ERR(uart_u6->uartClk);
	}

	if (clk_get_usecount(uart_u6->uartClk) == 0)
		clk_enable(uart_u6->uartClk);
	return 0;
}

unsigned int serial8250_disable_clock(struct uart_port *port)
{
	struct u6_uart *uart_u6 = port->private_data;

	if (!uart_u6)
		return uart_disable_clock(port);

	if (IS_ERR(uart_u6->uartClk)) {
		printk(KERN_WARNING "%s - uart clk error :%ld\n", __func__,
		       PTR_ERR(uart_u6->uartClk));
		return PTR_ERR(uart_u6->uartClk);
	}
	if (clk_get_usecount(uart_u6->uartClk) >= 1)
		clk_disable(uart_u6->uartClk);

	return 0;
}

unsigned int serial8250_get_custom_clock(struct uart_port *port,
					 unsigned int baud)
{
	switch (baud) {
	case 3250000:
		return 52000000;
	case 2000000:
		return 32000000;
	case 1843200:
		return 29491200;
	case 921600:
		return 14745600;
	default:
		return 7372800;
	}
}

void serial8250_set_custom_clock(struct uart_port *port)
{
	u32 fdiv_m = 0x5F37;
	u32 fdiv_n = 0x3600;
	u32 fdiv_ctrl = UARTX_FDIV_ENABLE_ON;
	struct u6_uart *uart_u6 = port->private_data;

	switch (port->uartclk) {
	case 7372800: /* clk=13MHz */
		fdiv_ctrl |= UARTX_CLKSEL_13M;
		break;
	case 14745600: /* clk=26MHz */
		fdiv_ctrl |= UARTX_CLKSEL_26M;
		break;
	case 29491200: /* clk=pclk */
		fdiv_ctrl |= UARTX_CLKSEL_PCLK;
		break;
	case 32000000: /* clk=pclk */
		fdiv_n = 0x3A98;
		fdiv_ctrl |= UARTX_CLKSEL_PCLK;
		break;
	case 52000000: /* clk=pclk */
		fdiv_n = 0x5F37;
		fdiv_ctrl |= UARTX_CLKSEL_PCLK;
		break;
	}

	if (uart_u6 != NULL && !IS_ERR(uart_u6->uartClk)) {
		/* if cgu interface is ready and u6_serial_init */
		struct clk *parentClk;

		if (fdiv_ctrl & UARTX_CLKSEL_26M)
			parentClk = clk_get(NULL, "clk26m_ck");
		else if (fdiv_ctrl & UARTX_CLKSEL_PCLK)
			parentClk = clk_get(NULL, "pclk2_ck");
		else
			parentClk = clk_get(NULL, "clk13m_ck");

		if (!IS_ERR(parentClk)) {
			serial8250_disable_clock(port);

			if (clk_set_parent(uart_u6->uartClk, parentClk) != 0)
				printk(KERN_WARNING "%s: set parent failed\n", __func__);

			serial8250_enable_clock(port);
			clk_put(parentClk);
		}
	}

	writel(fdiv_m, port->membase + UARTX_FDIV_M_OFFSET);
	writel(fdiv_n, port->membase + UARTX_FDIV_N_OFFSET);
	writel(fdiv_ctrl, port->membase + UARTX_FDIV_CTRL_OFFSET);
}
