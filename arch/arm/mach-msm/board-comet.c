/* Copyright (c) 2009, Code Aurora Forum. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of Code Aurora Forum nor
 *       the names of its contributors may be used to endorse or promote
 *       products derived from this software without specific prior written
 *       permission.
 *
 * Alternatively, provided that this notice is retained in full, this software
 * may be relicensed by the recipient under the terms of the GNU General Public
 * License version 2 ("GPL") and only version 2, in which case the provisions of
 * the GPL apply INSTEAD OF those given above.  If the recipient relicenses the
 * software under the GPL, then the identification text in the MODULE_LICENSE
 * macro must be changed to reflect "GPLv2" instead of "Dual BSD/GPL".  Once a
 * recipient changes the license terms to the GPL, subsequent recipients shall
 * not relicense under alternate licensing terms, including the BSD or dual
 * BSD/GPL terms.  In addition, the following license statement immediately
 * below and between the words START and END shall also then apply when this
 * software is relicensed under the GPL:
 *
 * START
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License version 2 and only version 2 as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * END
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include <linux/kernel.h>
#include <linux/irq.h>
#include <linux/gpio.h>
#include <linux/platform_device.h>
#include <linux/bootmem.h>
#include <linux/i2c.h>
#include <linux/io.h>

#include <asm/mach-types.h>
#include <asm/mach/arch.h>

#include <mach/mmc.h>
#include <mach/vreg.h>
#include <mach/board.h>
#include <mach/sirc.h>
#include <linux/spi/spi.h>

#include "devices.h"
#include "timer.h"
#include "pm.h"

#define TOUCHPAD_SUSPEND	34
#define TOUCHPAD_IRQ            42

#define MSM_PMEM_MDP_SIZE	0x800000
#define MSM_FB_SIZE             0x500000
#define MSM_AUDIO_SIZE		0x200000

#define MSM_SMI_BASE		0x2b00000
#define MSM_SMI_SIZE		0x1500000

#define MSM_FB_BASE		MSM_SMI_BASE
#define MSM_PMEM_GPU0_BASE	(MSM_FB_BASE + MSM_FB_SIZE)
#define MSM_PMEM_GPU0_SIZE	(MSM_SMI_SIZE - MSM_FB_SIZE)

#define COMET_CPLD_START                 0x70004000
#define COMET_CPLD_PER_ENABLE            0x00000010
#define COMET_CPLD_PER_RESET             0x00000018
#define COMET_CPLD_STATUS                0x00000028
#define COMET_CPLD_EXT_PER_ENABLE        0x00000030
#define COMET_CPLD_I2C_ENABLE            0x00000038
#define COMET_CPLD_EXT_PER_RESET         0x00000048
#define COMET_CPLD_VERSION               0x00000058

#define COMET_CPLD_SIZE                  0x00000060
#define COMET_CPLD_STATUS_WVGA           0x0004
#define COMET_CPLD_VERSION_MAJOR         0xFF00
#define COMET_CPLD_PER_ENABLE_WVGA       0x0400
#define COMET_CPLD_PER_ENABLE_LVDS       0x0200
#define COMET_CPLD_PER_ENABLE_WXGA       0x0040
#define COMET_CPLD_EXT_PER_ENABLE_WXGA   0x0080

static unsigned long        vreg_sts, gpio_sts;
static struct vreg         *vreg_mmc;
static int                  gp6_enabled;

static int                  cpld_version;
static bool                 wvga_present;
static bool                 wxga_present;
static struct comet_cpld_t {
	u16 per_reset_all_reset;
	u16 ext_per_reset_all_reset;
	u16 i2c_enable;
	u16 per_enable_all;
	u16 ext_per_enable_all;
	u16 bt_reset_reg;
	u16 bt_reset_mask;
} comet_cpld[] = {
	[0] = {
		.per_reset_all_reset     = 0x00FF,
		/* enable all peripherals except microphones and */
		/* reset line for i2c touchpad                   */
		.per_enable_all          = 0xFFD8,
		.bt_reset_reg            = 0x0018,
		.bt_reset_mask           = 0x0001,
	},
	[1] = {
		.per_reset_all_reset     = 0x00BF,
		.ext_per_reset_all_reset = 0x0007,
		.i2c_enable              = 0x07F7,
		/* enable all peripherals except microphones and */
		/* displays                                      */
		.per_enable_all          = 0xF9B8,
		.ext_per_enable_all      = 0x007D,
		.bt_reset_reg            = 0x0048,
		.bt_reset_mask           = 0x0004,
	},
};
static struct comet_cpld_t *cpld_info;

static struct resource smc911x_resources[] = {
	[0] = {
		.start  = 0x84000000,
		.end    = 0x84000100,
		.flags  = IORESOURCE_MEM,
	},
	[1] = {
		.start  = MSM_GPIO_TO_INT(156),
		.end    = 156,
		.flags  = IORESOURCE_IRQ,
	},
};

static struct platform_device smc911x_device = {
	.name           = "smc911x",
	.id             = 0,
	.num_resources  = ARRAY_SIZE(smc911x_resources),
	.resource       = smc911x_resources,
};

static void __iomem *comet_cpld_base(void)
{
	static void __iomem *comet_cpld_base_addr;

	if (!comet_cpld_base_addr) {
		if (!request_mem_region(COMET_CPLD_START, COMET_CPLD_SIZE,
					"cpld")) {
			printk(KERN_ERR
			       "%s: request_mem_region for comet cpld failed\n",
			       __func__);
			goto cpld_base_exit;
		}
		comet_cpld_base_addr = ioremap(COMET_CPLD_START,
					       COMET_CPLD_SIZE);
		if (!comet_cpld_base_addr) {
			release_mem_region(COMET_CPLD_START,
					   COMET_CPLD_SIZE);
			printk(KERN_ERR "%s: Could not map comet cpld\n",
			       __func__);
		}
	}
cpld_base_exit:
	return comet_cpld_base_addr;
}

static struct platform_device *devices[] __initdata = {
	&msm_device_smd,
	&msm_device_dmov,
	&smc911x_device,
	&msm_device_nand,
};


#define KBD_RST 35
#define KBD_IRQ 144

static void kbd_gpio_release(void)
{
	gpio_free(KBD_IRQ);
	gpio_free(KBD_RST);
}

static int kbd_gpio_setup(void)
{
	int rc;
	int respin = KBD_RST;
	int irqpin = KBD_IRQ;
	unsigned rescfg =
		GPIO_CFG(respin, 0, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA);
	unsigned irqcfg =
		GPIO_CFG(irqpin, 0, GPIO_INPUT, GPIO_NO_PULL, GPIO_2MA);

	rc = gpio_request(irqpin, "gpio_keybd_irq");
	if (rc) {
		pr_err("gpio_request failed on pin %d (rc=%d)\n",
		       irqpin, rc);
		goto err_gpioconfig;
	}
	rc = gpio_request(respin, "gpio_keybd_reset");
	if (rc) {
		pr_err("gpio_request failed on pin %d (rc=%d)\n",
		       respin, rc);
		goto err_gpioconfig;
	}
	rc = gpio_tlmm_config(rescfg, GPIO_ENABLE);
	if (rc) {
		pr_err("gpio_tlmm_config failed on pin %d (rc=%d)\n",
		       respin, rc);
		goto err_gpioconfig;
	}
	rc = gpio_tlmm_config(irqcfg, GPIO_ENABLE);
	if (rc) {
		pr_err("gpio_tlmm_config failed on pin %d (rc=%d)\n",
		       irqpin, rc);
		goto err_gpioconfig;
	}
	return rc;

err_gpioconfig:
	kbd_gpio_release();
	return rc;
}

static void __init comet_init_irq(void)
{
	msm_init_irq();
	msm_init_sirc();
}

static void sdcc_gpio_init(void)
{
	/* SDC1 GPIOs */
	if (gpio_request(51, "sdc1_data_3"))
		pr_err("failed to request gpio sdc1_data_3\n");
	if (gpio_request(52, "sdc1_data_2"))
		pr_err("failed to request gpio sdc1_data_2\n");
	if (gpio_request(53, "sdc1_data_1"))
		pr_err("failed to request gpio sdc1_data_1\n");
	if (gpio_request(54, "sdc1_data_0"))
		pr_err("failed to request gpio sdc1_data_0\n");
	if (gpio_request(55, "sdc1_cmd"))
		pr_err("failed to request gpio sdc1_cmd\n");
	if (gpio_request(56, "sdc1_clk"))
		pr_err("failed to request gpio sdc1_clk\n");

	/* SDC2 GPIOs */
	if (gpio_request(62, "sdc2_clk"))
		pr_err("failed to request gpio sdc2_clk\n");
	if (gpio_request(63, "sdc2_cmd"))
		pr_err("failed to request gpio sdc2_cmd\n");
	if (gpio_request(64, "sdc2_data_3"))
		pr_err("failed to request gpio sdc2_data_3\n");
	if (gpio_request(65, "sdc2_data_2"))
		pr_err("failed to request gpio sdc2_data_2\n");
	if (gpio_request(66, "sdc2_data_1"))
		pr_err("failed to request gpio sdc2_data_1\n");
	if (gpio_request(67, "sdc2_data_0"))
		pr_err("failed to request gpio sdc2_data_0\n");

	/* SDC3 GPIOs */
	if (gpio_request(88, "sdc3_clk"))
		pr_err("failed to request gpio sdc3_clk\n");
	if (gpio_request(89, "sdc3_cmd"))
		pr_err("failed to request gpio sdc3_cmd\n");
	if (gpio_request(90, "sdc3_data_3"))
		pr_err("failed to request gpio sdc3_data_3\n");
	if (gpio_request(91, "sdc3_data_2"))
		pr_err("failed to request gpio sdc3_data_2\n");
	if (gpio_request(92, "sdc3_data_1"))
		pr_err("failed to request gpio sdc3_data_1\n");
	if (gpio_request(93, "sdc3_data_0"))
		pr_err("failed to request gpio sdc3_data_0\n");

}

static unsigned sdcc_cfg_data[][6] = {
	/* SDC1 configs */
	{
	GPIO_CFG(51, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(52, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(53, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(54, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(55, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(56, 1, GPIO_OUTPUT, GPIO_NO_PULL, GPIO_8MA),
	},
	/* SDC2 configs */
	{
	GPIO_CFG(62, 1, GPIO_OUTPUT, GPIO_NO_PULL, GPIO_8MA),
	GPIO_CFG(63, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(64, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(65, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(66, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(67, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	},
	/* SDC3 configs */
	{
	GPIO_CFG(88, 1, GPIO_OUTPUT, GPIO_NO_PULL, GPIO_8MA),
	GPIO_CFG(89, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(90, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(91, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(92, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	GPIO_CFG(93, 1, GPIO_OUTPUT, GPIO_PULL_UP, GPIO_8MA),
	},
};

static void msm_sdcc_setup_gpio(int dev_id, unsigned int enable)
{
	int i, rc;

	if (!(test_bit(dev_id, &gpio_sts)^enable))
		return;

	if (enable)
		set_bit(dev_id, &gpio_sts);
	else
		clear_bit(dev_id, &gpio_sts);

	for (i = 0; i < ARRAY_SIZE(sdcc_cfg_data[dev_id - 1]); i++) {
		rc = gpio_tlmm_config(sdcc_cfg_data[dev_id - 1][i],
			enable ? GPIO_ENABLE : GPIO_DISABLE);
		if (rc)
			printk(KERN_ERR "%s: gpio_tlmm_config(%#x)=%d\n",
				__func__, sdcc_cfg_data[dev_id - 1][i], rc);
	}
}

static uint32_t msm_sdcc_setup_power(struct device *dv, unsigned int vdd)
{
	int rc = 0;
	struct platform_device *pdev;

	pdev = container_of(dv, struct platform_device, dev);
	msm_sdcc_setup_gpio(pdev->id, !!vdd);

	if (vdd == 0) {
		if (!vreg_sts)
			return 0;

		clear_bit(pdev->id, &vreg_sts);

		if (!vreg_sts && !gp6_enabled) {
			rc = vreg_disable(vreg_mmc);
			if (rc)
				printk(KERN_ERR "%s: return val: %d \n",
					__func__, rc);
		}
		return 0;
	}

	if (!vreg_sts && !gp6_enabled) {
		rc = vreg_set_level(vreg_mmc, 2850);
		if (!rc)
			rc = vreg_enable(vreg_mmc);
		if (rc)
			printk(KERN_ERR "%s: return val: %d \n",
					__func__, rc);
	}
	set_bit(pdev->id, &vreg_sts);
	return 0;
}

static struct mmc_platform_data comet_sdcc_data = {
	.ocr_mask	= MMC_VDD_27_28 | MMC_VDD_28_29,
	.translate_vdd	= msm_sdcc_setup_power,
};

static struct msm_pm_platform_data msm_pm_data[MSM_PM_SLEEP_MODE_NR] = {
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE].supported = 1,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE].suspend_enabled = 1,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE].idle_enabled = 1,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE].latency = 8594,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE].residency = 23740,

	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE_NO_XO_SHUTDOWN].supported = 1,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE_NO_XO_SHUTDOWN].suspend_enabled = 1,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE_NO_XO_SHUTDOWN].idle_enabled = 1,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE_NO_XO_SHUTDOWN].latency = 4594,
	[MSM_PM_SLEEP_MODE_POWER_COLLAPSE_NO_XO_SHUTDOWN].residency = 23740,

	[MSM_PM_SLEEP_MODE_RAMP_DOWN_AND_WAIT_FOR_INTERRUPT].supported = 1,
	[MSM_PM_SLEEP_MODE_RAMP_DOWN_AND_WAIT_FOR_INTERRUPT].suspend_enabled
		= 1,
	[MSM_PM_SLEEP_MODE_RAMP_DOWN_AND_WAIT_FOR_INTERRUPT].idle_enabled = 0,
	[MSM_PM_SLEEP_MODE_RAMP_DOWN_AND_WAIT_FOR_INTERRUPT].latency = 443,
	[MSM_PM_SLEEP_MODE_RAMP_DOWN_AND_WAIT_FOR_INTERRUPT].residency = 1098,

	[MSM_PM_SLEEP_MODE_WAIT_FOR_INTERRUPT].supported = 1,
	[MSM_PM_SLEEP_MODE_WAIT_FOR_INTERRUPT].suspend_enabled = 1,
	[MSM_PM_SLEEP_MODE_WAIT_FOR_INTERRUPT].idle_enabled = 1,
	[MSM_PM_SLEEP_MODE_WAIT_FOR_INTERRUPT].latency = 2,
	[MSM_PM_SLEEP_MODE_WAIT_FOR_INTERRUPT].residency = 0,
};

static void __init comet_init(void)
{
	char __iomem *cpld_base;
	int           per_enable;
	int           ext_per_enable;

	cpld_base = comet_cpld_base();

	if (!cpld_base)
		return;

	cpld_version = (readw(cpld_base + COMET_CPLD_VERSION) &
			COMET_CPLD_VERSION_MAJOR) >> 8;
	if (cpld_version >= 2) {
		cpld_info = &comet_cpld[1];
		per_enable = cpld_info->per_enable_all;
		wvga_present = (readw(cpld_base + COMET_CPLD_STATUS)
				& COMET_CPLD_STATUS_WVGA) != 0;
		wxga_present = !wvga_present;
		ext_per_enable = cpld_info->ext_per_enable_all;
		if (wvga_present)
			per_enable |= COMET_CPLD_PER_ENABLE_WVGA;
		else {
			per_enable |= COMET_CPLD_PER_ENABLE_LVDS |
				COMET_CPLD_PER_ENABLE_WXGA;
			ext_per_enable |= COMET_CPLD_EXT_PER_ENABLE_WXGA;
		}
		writew(ext_per_enable,
		       cpld_base + COMET_CPLD_EXT_PER_ENABLE);
		writew(cpld_info->i2c_enable,
		       cpld_base + COMET_CPLD_I2C_ENABLE);
		writew(cpld_info->ext_per_reset_all_reset,
		       cpld_base + COMET_CPLD_EXT_PER_RESET);
	} else {
		cpld_info = &comet_cpld[0];
		wvga_present = 1;
		wxga_present = 0;
		per_enable = cpld_info->per_enable_all;
		smc911x_resources[0].start = 0x90000000;
		smc911x_resources[0].end   = 0x90000100;
	}

	writew(per_enable,
	       cpld_base + COMET_CPLD_PER_ENABLE);
	writew(cpld_info->per_reset_all_reset,
	       cpld_base + COMET_CPLD_PER_RESET);

	platform_add_devices(devices, ARRAY_SIZE(devices));
	msm_pm_set_platform_data(msm_pm_data);
}

static void __init comet_map_io(void)
{
	msm_map_comet_io();
	msm_clock_init(msm_clocks_8x50, msm_num_clocks_8x50);
}

MACHINE_START(QSD8X50_COMET, "QCT QSD8x50 Comet")
#ifdef CONFIG_MSM_DEBUG_UART
	.phys_io  = MSM_DEBUG_UART_PHYS,
	.io_pg_offst = ((MSM_DEBUG_UART_BASE) >> 18) & 0xfffc,
#endif
	.boot_params = 0x0,
	.map_io = comet_map_io,
	.init_irq = comet_init_irq,
	.init_machine = comet_init,
	.timer = &msm_timer,
MACHINE_END
