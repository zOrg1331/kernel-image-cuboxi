/***************************************************************************/

/*
 *	linux/arch/m68knommu/platform/523x/config.c
 *
 *	Sub-architcture dependant initialization code for the Freescale
 *	523x CPUs.
 *
 *	Copyright (C) 1999-2005, Greg Ungerer (gerg@snapgear.com)
 *	Copyright (C) 2001-2003, SnapGear Inc. (www.snapgear.com)
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

static struct mcf_platform_uart m523x_uart_platform[] = {
	{
		.mapbase	= MCF_MBAR + MCFUART_BASE1,
		.irq		= MCFINT_VECBASE + MCFINT_UART0,
	},
	{
		.mapbase 	= MCF_MBAR + MCFUART_BASE2,
		.irq		= MCFINT_VECBASE + MCFINT_UART0 + 1,
	},
	{
		.mapbase 	= MCF_MBAR + MCFUART_BASE3,
		.irq		= MCFINT_VECBASE + MCFINT_UART0 + 2,
	},
	{ },
};

static struct platform_device m523x_uart = {
	.name			= "mcfuart",
	.id			= 0,
	.dev.platform_data	= m523x_uart_platform,
};

static struct resource m523x_fec_resources[] = {
	{
		.start		= MCF_MBAR + 0x1000,
		.end		= MCF_MBAR + 0x1000 + 0x7ff,
		.flags		= IORESOURCE_MEM,
	},
	{
		.start		= 64 + 23,
		.end		= 64 + 23,
		.flags		= IORESOURCE_IRQ,
	},
	{
		.start		= 64 + 27,
		.end		= 64 + 27,
		.flags		= IORESOURCE_IRQ,
	},
	{
		.start		= 64 + 29,
		.end		= 64 + 29,
		.flags		= IORESOURCE_IRQ,
	},
};

static struct platform_device m523x_fec = {
	.name			= "fec",
	.id			= 0,
	.num_resources		= ARRAY_SIZE(m523x_fec_resources),
	.resource		= m523x_fec_resources,
};

#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
static struct resource m523x_i2c_resources[] = {
	{
		.start		= MCFI2C_IOBASE,
		.end		= MCFI2C_IOBASE + MCFI2C_IOSIZE - 1,
		.flags		= IORESOURCE_MEM,
	},
	{
		.start		= MCFINT_VECBASE + MCFINT_I2C,
		.end		= MCFINT_VECBASE + MCFINT_I2C,
		.flags		= IORESOURCE_IRQ,
	},
};

static struct mcfi2c_platform_data m523x_i2c_platform_data = {
	.bitrate		= 100000,
};

static struct platform_device m523x_i2c = {
	.name			= "i2c-mcf",
	.id			= 0,
	.num_resources		= ARRAY_SIZE(m523x_i2c_resources),
	.resource		= m523x_i2c_resources,
	.dev.platform_data	= &m523x_i2c_platform_data,
};

static void __init m523x_i2c_init(void)
{
	u8 par;

	/* setup Port AS Pin Assignment Register for I2C */
	/*  set PASPA0 to SCL and PASPA1 to SDA */
	par = readb(MCF_IPSBAR + MCFGPIO_PAR_FECI2C);
	par |= 0x0f;
	writeb(par, MCF_IPSBAR + MCFGPIO_PAR_FECI2C);
}

#endif

static struct platform_device *m523x_devices[] __initdata = {
	&m523x_uart,
	&m523x_fec,
#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
	&m523x_i2c,
#endif
};

/***************************************************************************/

static void __init m523x_fec_init(void)
{
	u16 par;
	u8 v;

	/* Set multi-function pins to ethernet use */
	par = readw(MCF_IPSBAR + 0x100082);
	writew(par | 0xf00, MCF_IPSBAR + 0x100082);
	v = readb(MCF_IPSBAR + 0x100078);
	writeb(v | 0xc0, MCF_IPSBAR + 0x100078);
}

/***************************************************************************/

static void m523x_cpu_reset(void)
{
	local_irq_disable();
	__raw_writeb(MCF_RCR_SWRESET, MCF_IPSBAR + MCF_RCR);
}

/***************************************************************************/

void __init config_BSP(char *commandp, int size)
{
	mach_reset = m523x_cpu_reset;
}

/***************************************************************************/

static int __init init_BSP(void)
{
	m523x_fec_init();
#if defined(CONFIG_I2C_MCF) || defined(CONFIG_I2C_MCF_MODULE)
	m523x_i2c_init();
#endif
	platform_add_devices(m523x_devices, ARRAY_SIZE(m523x_devices));
	return 0;
}

arch_initcall(init_BSP);

/***************************************************************************/
