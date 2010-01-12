/***************************************************************************/

/*
 *	linux/arch/m68knommu/platform/5206e/config.c
 *
 *	Copyright (C) 1999-2002, Greg Ungerer (gerg@snapgear.com)
 */

/***************************************************************************/

#include <linux/kernel.h>
#include <linux/param.h>
#include <linux/init.h>
#include <linux/io.h>
#include <asm/machdep.h>
#include <asm/coldfire.h>
#include <asm/mcfsim.h>
#include <asm/mcfuart.h>
#include <asm/mcfdma.h>
#include <asm/mcfi2c.h>

/***************************************************************************/

static struct mcf_platform_uart m5206e_uart_platform[] = {
	{
		.mapbase	= MCF_MBAR + MCFUART_BASE1,
		.irq		= 73,
	},
	{
		.mapbase 	= MCF_MBAR + MCFUART_BASE2,
		.irq		= 74,
	},
	{ },
};

static struct platform_device m5206e_uart = {
	.name			= "mcfuart",
	.id			= 0,
	.dev.platform_data	= m5206e_uart_platform,
};

#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
static struct resource m5206e_i2c_resources[] = {
	{
		.start		= MCFI2C_IOBASE,
		.end		= MCFI2C_IOBASE + MCFI2C_IOSIZE - 1,
		.flags		= IORESOURCE_MEM,
	},
	{
		.start		= MCF_IRQ_I2C,
		.end		= MCF_IRQ_I2C,
		.flags		= IORESOURCE_IRQ,
	},
};

static struct mcfi2c_platform_data m5206e_i2c_platform_data = {
	.bitrate		= 100000,
};

static struct platform_device m5206e_i2c = {
	.name			= "i2c-mcf",
	.id			= 0,
	.num_resources		= ARRAY_SIZE(m5206e_i2c_resources),
	.resource		= m5206e_i2c_resources,
	.dev.platform_data	= &m5206e_i2c_platform_data,
};

static void __init m5206e_i2c_init(void)
{
	writeb(MCFSIM_ICR_AUTOVEC | MCFSIM_ICR_LEVEL5 | MCFSIM_ICR_PRI0,
			MCF_MBAR + MCFSIM_I2CICR);
	mcf_mapirq2imr(MCF_IRQ_I2C, MCFINTC_I2C);
}
#endif

static struct platform_device *m5206e_devices[] __initdata = {
	&m5206e_uart,
#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
	&m5206e_i2c,
#endif
};

/***************************************************************************/

static void __init m5206e_uart_init_line(int line, int irq)
{
	if (line == 0) {
		writel(MCFSIM_ICR_LEVEL6 | MCFSIM_ICR_PRI1, MCF_MBAR + MCFSIM_UART1ICR);
		writeb(irq, MCFUART_BASE1 + MCFUART_UIVR);
		mcf_mapirq2imr(irq, MCFINTC_UART0);
	} else if (line == 1) {
		writel(MCFSIM_ICR_LEVEL6 | MCFSIM_ICR_PRI2, MCF_MBAR + MCFSIM_UART2ICR);
		writeb(irq, MCFUART_BASE2 + MCFUART_UIVR);
		mcf_mapirq2imr(irq, MCFINTC_UART1);
	}
}

static void __init m5206e_uarts_init(void)
{
	const int nrlines = ARRAY_SIZE(m5206e_uart_platform);
	int line;

	for (line = 0; (line < nrlines); line++)
		m5206e_uart_init_line(line, m5206e_uart_platform[line].irq);
}

/***************************************************************************/

static void __init m5206e_timers_init(void)
{
	/* Timer1 is always used as system timer */
	writeb(MCFSIM_ICR_AUTOVEC | MCFSIM_ICR_LEVEL6 | MCFSIM_ICR_PRI3,
		MCF_MBAR + MCFSIM_TIMER1ICR);
	mcf_mapirq2imr(MCF_IRQ_TIMER, MCFINTC_TIMER1);

#ifdef CONFIG_HIGHPROFILE
	/* Timer2 is to be used as a high speed profile timer  */
	writeb(MCFSIM_ICR_AUTOVEC | MCFSIM_ICR_LEVEL7 | MCFSIM_ICR_PRI3,
		MCF_MBAR + MCFSIM_TIMER2ICR);
	mcf_mapirq2imr(MCF_IRQ_PROFILER, MCFINTC_TIMER2);
#endif
}

/***************************************************************************/

void m5206e_cpu_reset(void)
{
	local_irq_disable();
	/* Set watchdog to soft reset, and enabled */
	__raw_writeb(0xc0, MCF_MBAR + MCFSIM_SYPCR);
	for (;;)
		/* wait for watchdog to timeout */;
}

/***************************************************************************/

void __init config_BSP(char *commandp, int size)
{
#if defined(CONFIG_NETtel)
	/* Copy command line from FLASH to local buffer... */
	memcpy(commandp, (char *) 0xf0004000, size);
	commandp[size-1] = 0;
#endif /* CONFIG_NETtel */

	mach_reset = m5206e_cpu_reset;
	m5206e_timers_init();
	m5206e_uarts_init();
#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
	m5206e_i2c_init();
#endif

	/* Only support the external interrupts on their primary level */
	mcf_mapirq2imr(25, MCFINTC_EINT1);
	mcf_mapirq2imr(28, MCFINTC_EINT4);
	mcf_mapirq2imr(31, MCFINTC_EINT7);
}

/***************************************************************************/

static int __init init_BSP(void)
{
	platform_add_devices(m5206e_devices, ARRAY_SIZE(m5206e_devices));
	return 0;
}

arch_initcall(init_BSP);

/***************************************************************************/
