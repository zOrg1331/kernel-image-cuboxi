/***************************************************************************/

/*
 *	linux/arch/m68knommu/platform/5249/config.c
 *
 *	Copyright (C) 2002, Greg Ungerer (gerg@snapgear.com)
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
#include <asm/mcfi2c.h>

/***************************************************************************/

static struct mcf_platform_uart m5249_uart_platform[] = {
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

static struct platform_device m5249_uart = {
	.name			= "mcfuart",
	.id			= 0,
	.dev.platform_data	= m5249_uart_platform,
};

#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
static struct resource m5249_i2c0_resources[] = {
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

static struct resource m5249_i2c1_resources[] = {
	{
		.start		= MCFI2C_IOBASE2,
		.end		= MCFI2C_IOBASE2 + MCFI2C_IOSIZE - 1,
		.flags		= IORESOURCE_MEM,
	},
	{
		.start		= MCFINTC2_I2C,
		.end		= MCFINTC2_I2C,
		.flags		= IORESOURCE_IRQ,
	},
};

static struct mcfi2c_platform_data m5249_i2c0_platform_data = {
	.bitrate		= 100000,
};

static struct mcfi2c_platform_data m5249_i2c1_platform_data = {
	.bitrate		= 100000,
};

static struct platform_device m5249_i2c[] = {
	{
		.name			= "i2c-mcf",
		.id			= 0,
		.num_resources		= ARRAY_SIZE(m5249_i2c0_resources),
		.resource		= m5249_i2c0_resources,
		.dev.platform_data	= &m5249_i2c0_platform_data,
	},
	{
		.name			= "i2c-mcf",
		.id			= 1,
		.num_resources		= ARRAY_SIZE(m5249_i2c1_resources),
		.resource		= m5249_i2c1_resources,
		.dev.platform_data	= &m5249_i2c1_platform_data,
	},
};

static void __init m5249_i2c_init(void)
{
	u32 pri;

	/* first I2C controller uses regular irq setup */
	writeb(MCFSIM_ICR_AUTOVEC | MCFSIM_ICR_LEVEL5 | MCFSIM_ICR_PRI0,
			MCF_MBAR + MCFSIM_I2CICR);
	mcf_mapirq2imr(MCF_IRQ_I2C, MCFINTC_I2C);

	/* second I2C controller is completely different */
	pri = readl(MCF_MBAR2 + MCFSIM2_INTLEVEL8);
	pri &= ~MCFSIM2_INTPRI_62;
	pri |= MCFSIM2_INTPRI_I2C;
	writel(pri, MCF_MBAR2 + MCFSIM2_INTLEVEL8);
}
#endif

static struct platform_device *m5249_devices[] __initdata = {
	&m5249_uart,
#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
	&m5249_i2c[0],
	&m5249_i2c[1],
#endif
};

/***************************************************************************/

static void __init m5249_uart_init_line(int line, int irq)
{
	if (line == 0) {
		writeb(MCFSIM_ICR_LEVEL6 | MCFSIM_ICR_PRI1, MCF_MBAR + MCFSIM_UART1ICR);
		writeb(irq, MCF_MBAR + MCFUART_BASE1 + MCFUART_UIVR);
		mcf_mapirq2imr(irq, MCFINTC_UART0);
	} else if (line == 1) {
		writeb(MCFSIM_ICR_LEVEL6 | MCFSIM_ICR_PRI2, MCF_MBAR + MCFSIM_UART2ICR);
		writeb(irq, MCF_MBAR + MCFUART_BASE2 + MCFUART_UIVR);
		mcf_mapirq2imr(irq, MCFINTC_UART1);
	}
}

static void __init m5249_uarts_init(void)
{
	const int nrlines = ARRAY_SIZE(m5249_uart_platform);
	int line;

	for (line = 0; (line < nrlines); line++)
		m5249_uart_init_line(line, m5249_uart_platform[line].irq);
}

/***************************************************************************/

static void __init m5249_timers_init(void)
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

void m5249_cpu_reset(void)
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
	mach_reset = m5249_cpu_reset;
	m5249_timers_init();
	m5249_uarts_init();
#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
	m5249_i2c_init();
#endif
}

/***************************************************************************/

static int __init init_BSP(void)
{
	platform_add_devices(m5249_devices, ARRAY_SIZE(m5249_devices));
	return 0;
}

arch_initcall(init_BSP);

/***************************************************************************/
