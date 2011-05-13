/*
 * Generic GPIO driver for logic cells found in the Nomadik SoC
 *
 * Copyright (C) 2008,2009 STMicroelectronics
 * Copyright (C) 2009 Alessandro Rubini <rubini@unipv.it>
 *   Rewritten based on work by Prafulla WADASKAR <prafulla.wadaskar@st.com>
 * Copyright (C) 2011 Linus Walleij <linus.walleij@linaro.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/device.h>
#include <linux/platform_device.h>
#include <linux/io.h>
#include <linux/clk.h>
#include <linux/err.h>
#include <linux/gpio.h>
#include <linux/spinlock.h>
#include <linux/interrupt.h>
#include <linux/irq.h>
#include <linux/slab.h>
#include <linux/gpio/nomadik.h>

#include <asm/mach/irq.h>

#include <mach/hardware.h>
#include <mach/gpio.h>

/*
 * The GPIO module in the Nomadik family of Systems-on-Chip is an
 * AMBA device, managing 32 pins and alternate functions.  The logic block
 * is currently used in the Nomadik and ux500.
 *
 * Symbols in this file are called "nmk_gpio" for "nomadik gpio"
 */

#define NMK_GPIO_PER_CHIP	32

/* Register in the logic block */
#define NMK_GPIO_DAT	0x00
#define NMK_GPIO_DATS	0x04
#define NMK_GPIO_DATC	0x08
#define NMK_GPIO_PDIS	0x0c
#define NMK_GPIO_DIR	0x10
#define NMK_GPIO_DIRS	0x14
#define NMK_GPIO_DIRC	0x18
#define NMK_GPIO_SLPC	0x1c
#define NMK_GPIO_AFSLA	0x20
#define NMK_GPIO_AFSLB	0x24

#define NMK_GPIO_RIMSC	0x40
#define NMK_GPIO_FIMSC	0x44
#define NMK_GPIO_IS	0x48
#define NMK_GPIO_IC	0x4c
#define NMK_GPIO_RWIMSC	0x50
#define NMK_GPIO_FWIMSC	0x54
#define NMK_GPIO_WKS	0x58

struct nmk_gpio_chip {
	struct gpio_chip chip;
	void __iomem *addr;
	struct clk *clk;
	unsigned int bank;
	unsigned int parent_irq;
	int secondary_parent_irq;
	u32 (*get_secondary_status)(unsigned int bank);
	void (*set_ioforce)(bool enable);
	spinlock_t lock;
	bool sleepmode;
	/* Keep track of configured edges */
	u32 edge_rising;
	u32 edge_falling;
	u32 real_wake;
	u32 rwimsc;
	u32 fwimsc;
	u32 slpm;
	u32 pull_up;
};

/* FIXME: this is insane since it will create chips for the GPIO expanders! */
static struct nmk_gpio_chip *
nmk_gpio_chips[DIV_ROUND_UP(ARCH_NR_GPIOS, NMK_GPIO_PER_CHIP)];

static DEFINE_SPINLOCK(nmk_gpio_slpm_lock);

#define NUM_BANKS ARRAY_SIZE(nmk_gpio_chips)

static inline struct nmk_gpio_chip *to_nmk_chip(struct gpio_chip *chip)
{
	struct nmk_gpio_chip *nmk_chip =
		container_of(chip, struct nmk_gpio_chip, chip);

	return nmk_chip;
}

static void __nmk_gpio_set_mode(struct nmk_gpio_chip *nmk_chip,
				unsigned offset, u16 altfunc)
{
	u32 bit = 1 << offset;
	u32 afunc, bfunc;
	bool glitch = (altfunc == GPIO_CONFIG_NMK_ALTF_C);
	u32 rwimsc = readl(nmk_chip->addr + NMK_GPIO_RWIMSC);
	u32 fwimsc = readl(nmk_chip->addr + NMK_GPIO_FWIMSC);
	unsigned long flags = 0;
	int i;

	/*
	 * If we're setting altfunc C by setting both AFSLA and AFSLB to 1,
	 * we may pass through an undesired state. In this case we take
	 * some extra care.
	 *
	 * Safe sequence used to switch IOs between GPIO and Alternate-C mode:
	 *  - Save SLPM registers (since we have a shadow register in the
	 *    nmk_chip we're using that as backup)
	 *  - Set SLPM=0 for the IOs you want to switch and others to 1
	 *  - Configure the GPIO registers for the IOs that are being switched
	 *  - Set IOFORCE=1
	 *  - Modify the AFLSA/B registers for the IOs that are being switched
	 *  - Set IOFORCE=0
	 *  - Restore SLPM registers
	 *  - Any spurious wake up event during switch sequence to be ignored
	 *    and cleared
	 *
	 * We REALLY need to save ALL slpm registers, because the external
	 * IOFORCE will switch *all* ports to their sleepmode setting to as
	 * to avoid glitches. (Not just one port!)
	 */
	if (glitch) {
		u32 bit = BIT(offset);

		/* Take the special sleep mode spinlock */
		spin_lock_irqsave(&nmk_gpio_slpm_lock, flags);
		for (i = 0; i < NUM_BANKS; i++) {
			struct nmk_gpio_chip *chip = nmk_gpio_chips[i];

			if (!chip)
				break;
			clk_enable(chip->clk);
			writel(0xFFFFFFFFU, chip->addr + NMK_GPIO_SLPC);
		}

		/* Set "my" sleep bit to 0 */
		writel(0xFFFFFFFFU & ~bit, nmk_chip->addr + NMK_GPIO_SLPC);
		/* Prevent spurious wakeups */
		writel(rwimsc & ~bit, nmk_chip->addr + NMK_GPIO_RWIMSC);
		writel(fwimsc & ~bit, nmk_chip->addr + NMK_GPIO_FWIMSC);
		if (nmk_chip->set_ioforce)
			nmk_chip->set_ioforce(true);
	}

	/* Set desired altfunc */
	afunc = readl(nmk_chip->addr + NMK_GPIO_AFSLA) & ~bit;
	bfunc = readl(nmk_chip->addr + NMK_GPIO_AFSLB) & ~bit;
	if ((altfunc == GPIO_CONFIG_NMK_ALTF_A) ||
	    (altfunc == GPIO_CONFIG_NMK_ALTF_C))
		afunc |= bit;
	if ((altfunc == GPIO_CONFIG_NMK_ALTF_B) ||
	    (altfunc == GPIO_CONFIG_NMK_ALTF_C))
		bfunc |= bit;
	writel(afunc, nmk_chip->addr + NMK_GPIO_AFSLA);
	writel(bfunc, nmk_chip->addr + NMK_GPIO_AFSLB);

	if (glitch) {
		if (nmk_chip->set_ioforce)
			nmk_chip->set_ioforce(false);
		writel(rwimsc, nmk_chip->addr + NMK_GPIO_RWIMSC);
		writel(fwimsc, nmk_chip->addr + NMK_GPIO_FWIMSC);

		for (i = 0; i < NUM_BANKS; i++) {
			struct nmk_gpio_chip *chip = nmk_gpio_chips[i];

			if (!chip)
				break;
			writel(chip->slpm, chip->addr + NMK_GPIO_SLPC);
			clk_disable(chip->clk);
		}
		spin_unlock_irqrestore(&nmk_gpio_slpm_lock, flags);
	}
}

static int __nmk_gpio_get_mode(struct nmk_gpio_chip *nmk_chip,
			       unsigned offset, u16 *data)
{
	u32 afunc, bfunc, bit;

	bit = 1 << offset;

	afunc = readl(nmk_chip->addr + NMK_GPIO_AFSLA) & bit;
	bfunc = readl(nmk_chip->addr + NMK_GPIO_AFSLB) & bit;

	if (afunc && bfunc)
		*data = GPIO_CONFIG_NMK_ALTF_C;
	else if (afunc)
		*data = GPIO_CONFIG_NMK_ALTF_A;
	else if (bfunc)
		*data = GPIO_CONFIG_NMK_ALTF_B;
	else
		*data = GPIO_CONFIG_NMK_ALTF_GPIO;
	return 0;
}

/**
 * __nmk_gpio_set_slpm() - configure the sleep mode of a pin
 * @offset: pin number
 * @enable: enable wakeup on the pin and force the pin to retain
 * its value in sleep mode (not become an input).
 *
 * This register is actually in the pinmux layer, not the GPIO block itself.
 * The GPIO1B_SLPM register defines the GPIO mode when SLEEP/DEEP-SLEEP
 * mode is entered (i.e. when signal IOFORCE is HIGH by the platform code).
 * Each GPIO can be configured to be forced into GPIO mode when IOFORCE is
 * HIGH, overriding the normal setting defined by GPIO_AFSELx registers.
 * When IOFORCE returns LOW (by software, after SLEEP/DEEP-SLEEP exit),
 * the GPIOs return to the normal setting defined by GPIO_AFSELx registers.
 *
 * If @enable is true, the corresponding GPIO is switched to GPIO mode when
 * signal IOFORCE is HIGH (i.e. when SLEEP/DEEP-SLEEP mode is entered)
 * regardless of the altfunction selected. Also wake-up detection is ENABLED.
 *
 * If @enable is false, the corresponding GPIO remains controlled by
 * NMK_GPIO_DATC, NMK_GPIO_DATS, NMK_GPIO_DIR, NMK_GPIO_PDIS (for altfunction
 * GPIO) or respective on-chip peripherals (for other altfuncs) when IOFORCE
 * is HIGH. Also wake-up detection DISABLED.
 *
 * Note that enable_irq_wake() will automatically enable wakeup detection by
 * calling this function on DB8500v2 and later versions.
 */
static void __nmk_gpio_set_slpm(struct nmk_gpio_chip *nmk_chip,
				unsigned offset, bool enable)
{
	u32 bit = 1 << offset;

	/*
	 * NOTE: the meaning of "enable" is inverted, nominally every GPIO
	 * will wake up the system (or convert the pin to an input on DB8500v1)
	 */
	if (enable)
		nmk_chip->slpm &= ~bit;
	else
		/*
		 * So setting this bit disables wakeups (or makes the pin
		 * retain its value on DB8500v1)
		 */
		nmk_chip->slpm |= bit;

	writel(nmk_chip->slpm, nmk_chip->addr + NMK_GPIO_SLPC);
}

static void __nmk_gpio_set_pull(struct nmk_gpio_chip *nmk_chip,
				unsigned offset, u16 pullmode)
{
	u32 bit = 1 << offset;
	u32 pdis;

	/* FIXME: use shadow registers instead of read-modify-write */
	pdis = readl(nmk_chip->addr + NMK_GPIO_PDIS);
	if ((pullmode == GPIO_CONFIG_BIAS_UNKNOWN) ||
	    (pullmode == GPIO_CONFIG_BIAS_FLOAT)) {
		pdis |= bit;
		nmk_chip->pull_up &= ~bit;
	} else {
		pdis &= ~bit;
	}

	writel(pdis, nmk_chip->addr + NMK_GPIO_PDIS);

	if (pullmode == GPIO_CONFIG_BIAS_PULL_UP) {
		nmk_chip->pull_up |= bit;
		writel(bit, nmk_chip->addr + NMK_GPIO_DATS);
	} else if (pullmode == GPIO_CONFIG_BIAS_PULL_DOWN) {
		nmk_chip->pull_up &= ~bit;
		writel(bit, nmk_chip->addr + NMK_GPIO_DATC);
	}
}

static void __nmk_gpio_make_input(struct nmk_gpio_chip *nmk_chip,
				  unsigned offset)
{
	writel(1 << offset, nmk_chip->addr + NMK_GPIO_DIRC);
}

static void __nmk_gpio_set_output(struct nmk_gpio_chip *nmk_chip,
				  unsigned offset, int val)
{
	if (val)
		writel(1 << offset, nmk_chip->addr + NMK_GPIO_DATS);
	else
		writel(1 << offset, nmk_chip->addr + NMK_GPIO_DATC);
}

static void __nmk_gpio_make_output(struct nmk_gpio_chip *nmk_chip,
				  unsigned offset, int val)
{
	writel(1 << offset, nmk_chip->addr + NMK_GPIO_DIRS);
	__nmk_gpio_set_output(nmk_chip, offset, val);
}


static void __nmk_setup_pin(struct nmk_gpio_chip *nmk_chip, unsigned offset,
			    struct nmk_gpio_pin_config *cfg)
{
	static const char *afnames[] = {
		[GPIO_CONFIG_NMK_ALTF_GPIO]	= "GPIO",
		[GPIO_CONFIG_NMK_ALTF_A]	= "A",
		[GPIO_CONFIG_NMK_ALTF_B]	= "B",
		[GPIO_CONFIG_NMK_ALTF_C]	= "C"
	};
	static const char *biasnames[] = {
		[GPIO_CONFIG_BIAS_UNKNOWN]	= "none",
		[GPIO_CONFIG_BIAS_FLOAT]	= "none",
		[GPIO_CONFIG_BIAS_PULL_UP]	= "up",
		[GPIO_CONFIG_BIAS_PULL_DOWN]	= "down",
	};

	dev_dbg(nmk_chip->chip.dev, "pin %d: af: %s, bias: %s, "
		"slpm: %s (%s%s)\n",
		cfg->pin, afnames[cfg->altfunc],
		biasnames[cfg->bias_mode],
		cfg->sleep_mode ? "input/wakeup" : "no-change/no-wakeup",
		cfg->output ? "output " : "input",
		cfg->output ? (cfg->outval ? "high" : "low") : "");

	if (cfg->output)
		__nmk_gpio_make_output(nmk_chip, offset, cfg->outval);
	else {
		__nmk_gpio_make_input(nmk_chip, offset);
		__nmk_gpio_set_pull(nmk_chip, offset, cfg->bias_mode);
	}
	__nmk_gpio_set_slpm(nmk_chip, offset, cfg->sleep_mode);
	__nmk_gpio_set_mode(nmk_chip, offset, cfg->altfunc);
}

/**
 * This translates the old pin config parameter type into a config
 * struct and passes to the new API
 */
static void __nmk_setup_pin_legacy(struct nmk_gpio_chip *nmk_chip,
				   unsigned offset,
				   pin_cfg_t pincfg)
{
	struct nmk_gpio_pin_config cfg;

	cfg.pin = PIN_NUM(pincfg);

	switch (PIN_ALT(pincfg)) {
	case NMK_GPIO_ALT_GPIO:
		cfg.altfunc = GPIO_CONFIG_NMK_ALTF_GPIO;
		break;
	case NMK_GPIO_ALT_A:
		cfg.altfunc = GPIO_CONFIG_NMK_ALTF_A;
		break;
	case NMK_GPIO_ALT_B:
		cfg.altfunc = GPIO_CONFIG_NMK_ALTF_B;
		break;
	case NMK_GPIO_ALT_C:
		cfg.altfunc = GPIO_CONFIG_NMK_ALTF_C;
		break;
	default:
		cfg.altfunc = GPIO_CONFIG_NMK_ALTF_GPIO;
		break;
	}

	if (PIN_DIR(pincfg))
		cfg.output = true;

	if (PIN_VAL(pincfg))
		cfg.outval = 1;

	switch (PIN_PULL(pincfg)) {
	case NMK_GPIO_PULL_NONE:
		cfg.bias_mode = GPIO_CONFIG_BIAS_FLOAT;
		break;
	case NMK_GPIO_PULL_UP:
		cfg.bias_mode = GPIO_CONFIG_BIAS_PULL_UP;
		break;
	case NMK_GPIO_PULL_DOWN:
		cfg.bias_mode = GPIO_CONFIG_BIAS_PULL_DOWN;
		break;
	default:
		cfg.bias_mode = GPIO_CONFIG_BIAS_FLOAT;
		break;
	}

	switch (PIN_SLPM(pincfg)) {
	case NMK_GPIO_SLPM_WAKEUP_ENABLE:
		/* Also NMK_GPIO_SLPM_INPUT */
		break;
	case NMK_GPIO_SLPM_WAKEUP_DISABLE:
		/* Also NMK_GPIO_SLPM_NOCHANGE */
		cfg.sleep_mode = true;
	default:
		break;
	}

	__nmk_setup_pin(nmk_chip, offset, &cfg);
}

static int nmk_gpio_config(struct gpio_chip *chip, unsigned offset,
			   u16 param, unsigned long *data)
{
	struct nmk_gpio_chip *nmk_chip = to_nmk_chip(chip);
	unsigned long flags;

	if (!nmk_chip)
		return -EINVAL;

	clk_enable(nmk_chip->clk);

	switch (param) {
	case GPIO_CONFIG_BIAS_UNKNOWN:
	case GPIO_CONFIG_BIAS_FLOAT:
	case GPIO_CONFIG_BIAS_PULL_UP:
	case GPIO_CONFIG_BIAS_PULL_DOWN:
		__nmk_gpio_set_pull(nmk_chip, offset, param);
		break;
	case GPIO_CONFIG_NMK_ALTF_GPIO:
	case GPIO_CONFIG_NMK_ALTF_A:
	case GPIO_CONFIG_NMK_ALTF_B:
	case GPIO_CONFIG_NMK_ALTF_C:
		__nmk_gpio_set_mode(nmk_chip, offset, param);
		break;
	case GPIO_CONFIG_NMK_GET_ALTF:
		__nmk_gpio_get_mode(nmk_chip, offset, (u16 *) data);
		break;
	case GPIO_CONFIG_NMK_SLPM_INPUT:
	case GPIO_CONFIG_NMK_WAKEUP_ENABLE:
		spin_lock_irqsave(&nmk_gpio_slpm_lock, flags);
		spin_lock(&nmk_chip->lock);
		__nmk_gpio_set_slpm(nmk_chip, offset, true);
		spin_unlock(&nmk_chip->lock);
		spin_unlock_irqrestore(&nmk_gpio_slpm_lock, flags);
		break;
	case GPIO_CONFIG_NMK_SLPM_NOCHANGE:
	case GPIO_CONFIG_NMK_WAKEUP_DISABLE:
		spin_lock_irqsave(&nmk_gpio_slpm_lock, flags);
		spin_lock(&nmk_chip->lock);
		__nmk_gpio_set_slpm(nmk_chip, offset, false);
		spin_unlock(&nmk_chip->lock);
		spin_unlock_irqrestore(&nmk_gpio_slpm_lock, flags);
		break;
	case GPIO_CONFIG_NMK_SETUP_PIN:
		__nmk_setup_pin(nmk_chip, offset,
				(struct nmk_gpio_pin_config *) data);
		break;
	case GPIO_CONFIG_NMK_SETUP_PIN_LEGACY:
		__nmk_setup_pin_legacy(nmk_chip, offset, (pin_cfg_t) *data);
		break;
	default:
		dev_err(nmk_chip->chip.dev,
			"illegal configuration requested\n");
		clk_disable(nmk_chip->clk);
		return -EINVAL;
	};

	clk_disable(nmk_chip->clk);

	return 0;
}



/* IRQ functions */
static inline int nmk_gpio_get_bitmask(int gpio)
{
	return 1 << (gpio % 32);
}

static void nmk_gpio_irq_ack(struct irq_data *d)
{
	int gpio;
	struct nmk_gpio_chip *nmk_chip;

	gpio = NOMADIK_IRQ_TO_GPIO(d->irq);
	nmk_chip = irq_data_get_irq_chip_data(d);
	if (!nmk_chip)
		return;

	clk_enable(nmk_chip->clk);
	writel(nmk_gpio_get_bitmask(gpio), nmk_chip->addr + NMK_GPIO_IC);
	clk_disable(nmk_chip->clk);
}

enum nmk_gpio_irq_type {
	NORMAL,
	WAKE,
};

static void __nmk_gpio_irq_modify(struct nmk_gpio_chip *nmk_chip,
				  int gpio, enum nmk_gpio_irq_type which,
				  bool enable)
{
	u32 rimsc = which == WAKE ? NMK_GPIO_RWIMSC : NMK_GPIO_RIMSC;
	u32 fimsc = which == WAKE ? NMK_GPIO_FWIMSC : NMK_GPIO_FIMSC;
	u32 bitmask = nmk_gpio_get_bitmask(gpio);
	u32 reg;

	/* we must individually set/clear the two edges */
	if (nmk_chip->edge_rising & bitmask) {
		reg = readl(nmk_chip->addr + rimsc);
		if (enable)
			reg |= bitmask;
		else
			reg &= ~bitmask;
		writel(reg, nmk_chip->addr + rimsc);
	}
	if (nmk_chip->edge_falling & bitmask) {
		reg = readl(nmk_chip->addr + fimsc);
		if (enable)
			reg |= bitmask;
		else
			reg &= ~bitmask;
		writel(reg, nmk_chip->addr + fimsc);
	}
}

static void __nmk_gpio_set_wake(struct nmk_gpio_chip *nmk_chip,
				int gpio, bool on)
{
	if (nmk_chip->sleepmode)
		__nmk_gpio_set_slpm(nmk_chip, gpio - nmk_chip->chip.base, on);

	__nmk_gpio_irq_modify(nmk_chip, gpio, WAKE, on);
}

static int nmk_gpio_irq_maskunmask(struct irq_data *d, bool enable)
{
	int gpio;
	struct nmk_gpio_chip *nmk_chip;
	unsigned long flags;
	u32 bitmask;

	gpio = NOMADIK_IRQ_TO_GPIO(d->irq);
	nmk_chip = irq_data_get_irq_chip_data(d);
	bitmask = nmk_gpio_get_bitmask(gpio);
	if (!nmk_chip)
		return -EINVAL;

	clk_enable(nmk_chip->clk);
	spin_lock_irqsave(&nmk_gpio_slpm_lock, flags);
	spin_lock(&nmk_chip->lock);

	__nmk_gpio_irq_modify(nmk_chip, gpio, NORMAL, enable);

	if (!(nmk_chip->real_wake & bitmask))
		__nmk_gpio_set_wake(nmk_chip, gpio, enable);

	spin_unlock(&nmk_chip->lock);
	spin_unlock_irqrestore(&nmk_gpio_slpm_lock, flags);
	clk_disable(nmk_chip->clk);

	return 0;
}

static void nmk_gpio_irq_mask(struct irq_data *d)
{
	nmk_gpio_irq_maskunmask(d, false);
}

static void nmk_gpio_irq_unmask(struct irq_data *d)
{
	nmk_gpio_irq_maskunmask(d, true);
}

static int nmk_gpio_irq_set_wake(struct irq_data *d, unsigned int on)
{
	struct nmk_gpio_chip *nmk_chip;
	unsigned long flags;
	u32 bitmask;
	int gpio;

	gpio = NOMADIK_IRQ_TO_GPIO(d->irq);
	nmk_chip = irq_data_get_irq_chip_data(d);
	if (!nmk_chip)
		return -EINVAL;
	bitmask = nmk_gpio_get_bitmask(gpio);

	clk_enable(nmk_chip->clk);
	spin_lock_irqsave(&nmk_gpio_slpm_lock, flags);
	spin_lock(&nmk_chip->lock);

	/* Make sure we wake up on this pin */
	if (irqd_irq_disabled(d))
		__nmk_gpio_set_wake(nmk_chip, gpio, on);

	if (on)
		nmk_chip->real_wake |= bitmask;
	else
		nmk_chip->real_wake &= ~bitmask;

	spin_unlock(&nmk_chip->lock);
	spin_unlock_irqrestore(&nmk_gpio_slpm_lock, flags);
	clk_disable(nmk_chip->clk);

	return 0;
}

static int nmk_gpio_irq_set_type(struct irq_data *d, unsigned int type)
{
	bool enabled = !irqd_irq_disabled(d);
	bool wake = irqd_is_wakeup_set(d);
	int gpio;
	struct nmk_gpio_chip *nmk_chip;
	unsigned long flags;
	u32 bitmask;

	gpio = NOMADIK_IRQ_TO_GPIO(d->irq);
	nmk_chip = irq_data_get_irq_chip_data(d);
	bitmask = nmk_gpio_get_bitmask(gpio);
	if (!nmk_chip)
		return -EINVAL;

	if (type & IRQ_TYPE_LEVEL_HIGH)
		return -EINVAL;
	if (type & IRQ_TYPE_LEVEL_LOW)
		return -EINVAL;

	clk_enable(nmk_chip->clk);
	spin_lock_irqsave(&nmk_chip->lock, flags);

	if (enabled)
		__nmk_gpio_irq_modify(nmk_chip, gpio, NORMAL, false);

	if (enabled || wake)
		__nmk_gpio_irq_modify(nmk_chip, gpio, WAKE, false);

	nmk_chip->edge_rising &= ~bitmask;
	if (type & IRQ_TYPE_EDGE_RISING)
		nmk_chip->edge_rising |= bitmask;

	nmk_chip->edge_falling &= ~bitmask;
	if (type & IRQ_TYPE_EDGE_FALLING)
		nmk_chip->edge_falling |= bitmask;

	if (enabled)
		__nmk_gpio_irq_modify(nmk_chip, gpio, NORMAL, true);

	if (enabled || wake)
		__nmk_gpio_irq_modify(nmk_chip, gpio, WAKE, true);

	spin_unlock_irqrestore(&nmk_chip->lock, flags);
	clk_disable(nmk_chip->clk);

	return 0;
}

static unsigned int nmk_gpio_irq_startup(struct irq_data *d)
{
	struct nmk_gpio_chip *nmk_chip = irq_data_get_irq_chip_data(d);

	clk_enable(nmk_chip->clk);
	nmk_gpio_irq_unmask(d);
	return 0;
}

static void nmk_gpio_irq_shutdown(struct irq_data *d)
{
	struct nmk_gpio_chip *nmk_chip = irq_data_get_irq_chip_data(d);

	nmk_gpio_irq_mask(d);
	clk_disable(nmk_chip->clk);
}

static struct irq_chip nmk_gpio_irq_chip = {
	.name		= "Nomadik-GPIO",
	.irq_ack	= nmk_gpio_irq_ack,
	.irq_mask	= nmk_gpio_irq_mask,
	.irq_unmask	= nmk_gpio_irq_unmask,
	.irq_set_type	= nmk_gpio_irq_set_type,
	.irq_set_wake	= nmk_gpio_irq_set_wake,
	.irq_startup	= nmk_gpio_irq_startup,
	.irq_shutdown	= nmk_gpio_irq_shutdown,
};

static void __nmk_gpio_irq_handler(unsigned int irq, struct irq_desc *desc,
				   u32 status)
{
	struct nmk_gpio_chip *nmk_chip;
	struct irq_chip *host_chip = irq_get_chip(irq);
	unsigned int first_irq;

	chained_irq_enter(host_chip, desc);

	nmk_chip = irq_get_handler_data(irq);
	first_irq = NOMADIK_GPIO_TO_IRQ(nmk_chip->chip.base);
	while (status) {
		int bit = __ffs(status);

		generic_handle_irq(first_irq + bit);
		status &= ~BIT(bit);
	}

	chained_irq_exit(host_chip, desc);
}

static void nmk_gpio_irq_handler(unsigned int irq, struct irq_desc *desc)
{
	struct nmk_gpio_chip *nmk_chip = irq_get_handler_data(irq);
	u32 status;

	clk_enable(nmk_chip->clk);
	status = readl(nmk_chip->addr + NMK_GPIO_IS);
	clk_disable(nmk_chip->clk);

	__nmk_gpio_irq_handler(irq, desc, status);
}

static void nmk_gpio_secondary_irq_handler(unsigned int irq,
					   struct irq_desc *desc)
{
	struct nmk_gpio_chip *nmk_chip = irq_get_handler_data(irq);
	u32 status = nmk_chip->get_secondary_status(nmk_chip->bank);

	__nmk_gpio_irq_handler(irq, desc, status);
}

static int nmk_gpio_init_irq(struct nmk_gpio_chip *nmk_chip)
{
	unsigned int first_irq;
	int i;

	first_irq = NOMADIK_GPIO_TO_IRQ(nmk_chip->chip.base);
	for (i = first_irq; i < first_irq + nmk_chip->chip.ngpio; i++) {
		irq_set_chip_and_handler(i, &nmk_gpio_irq_chip,
					 handle_edge_irq);
		set_irq_flags(i, IRQF_VALID);
		irq_set_chip_data(i, nmk_chip);
		irq_set_irq_type(i, IRQ_TYPE_EDGE_FALLING);
	}

	irq_set_chained_handler(nmk_chip->parent_irq, nmk_gpio_irq_handler);
	irq_set_handler_data(nmk_chip->parent_irq, nmk_chip);

	if (nmk_chip->secondary_parent_irq >= 0) {
		irq_set_chained_handler(nmk_chip->secondary_parent_irq,
					nmk_gpio_secondary_irq_handler);
		irq_set_handler_data(nmk_chip->secondary_parent_irq, nmk_chip);
	}

	return 0;
}

/* I/O Functions */
static int nmk_gpio_make_input(struct gpio_chip *chip, unsigned offset)
{
	struct nmk_gpio_chip *nmk_chip = to_nmk_chip(chip);

	clk_enable(nmk_chip->clk);

	writel(1 << offset, nmk_chip->addr + NMK_GPIO_DIRC);

	clk_disable(nmk_chip->clk);

	return 0;
}

static int nmk_gpio_get_input(struct gpio_chip *chip, unsigned offset)
{
	struct nmk_gpio_chip *nmk_chip = to_nmk_chip(chip);
	u32 bit = 1 << offset;
	int value;

	clk_enable(nmk_chip->clk);

	value = (readl(nmk_chip->addr + NMK_GPIO_DAT) & bit) != 0;

	clk_disable(nmk_chip->clk);

	return value;
}

static void nmk_gpio_set_output(struct gpio_chip *chip, unsigned offset,
				int val)
{
	struct nmk_gpio_chip *nmk_chip = to_nmk_chip(chip);

	clk_enable(nmk_chip->clk);

	__nmk_gpio_set_output(nmk_chip, offset, val);

	clk_disable(nmk_chip->clk);
}

static int nmk_gpio_make_output(struct gpio_chip *chip, unsigned offset,
				int val)
{
	struct nmk_gpio_chip *nmk_chip = to_nmk_chip(chip);

	clk_enable(nmk_chip->clk);

	__nmk_gpio_make_output(nmk_chip, offset, val);

	clk_disable(nmk_chip->clk);

	return 0;
}

static int nmk_gpio_to_irq(struct gpio_chip *chip, unsigned offset)
{
	struct nmk_gpio_chip *nmk_chip = to_nmk_chip(chip);

	return NOMADIK_GPIO_TO_IRQ(nmk_chip->chip.base) + offset;
}

#ifdef CONFIG_DEBUG_FS

#include <linux/seq_file.h>

static void nmk_gpio_dbg_show(struct seq_file *s, struct gpio_chip *chip)
{
	u16 mode;
	unsigned		i;
	unsigned		gpio = chip->base;
	int			is_out;
	struct nmk_gpio_chip *nmk_chip = to_nmk_chip(chip);

	clk_enable(nmk_chip->clk);

	for (i = 0; i < chip->ngpio; i++, gpio++) {
		const char *label = gpiochip_is_requested(chip, i);
		const char *modetxt;
		bool pull;
		u32 bit = 1 << i;

		is_out = readl(nmk_chip->addr + NMK_GPIO_DIR) & bit;
		pull = !(readl(nmk_chip->addr + NMK_GPIO_PDIS) & bit);
		__nmk_gpio_get_mode(nmk_chip, gpio, &mode);
		switch (mode) {
		case GPIO_CONFIG_NMK_ALTF_GPIO:
			modetxt = "gpio";
			break;
		case GPIO_CONFIG_NMK_ALTF_A:
			modetxt = "altA";
			break;
		case GPIO_CONFIG_NMK_ALTF_B:
			modetxt = "altB";
			break;
		case GPIO_CONFIG_NMK_ALTF_C:
			modetxt = "altC";
			break;
		default:
			modetxt = "unknown";
			break;
		}
		seq_printf(s, " gpio-%-3d (%-20.20s) %s %s %s %s",
			gpio, label ?: "(none)",
			is_out ? "out" : "in ",
			chip->get
				? (chip->get(chip, i) ? "hi" : "lo")
				: "?  ",
			(mode < 0) ? "unknown" : modetxt,
			pull ? "pull" : "none");

		if (label && !is_out) {
			int		irq = gpio_to_irq(gpio);
			struct irq_desc	*desc = irq_to_desc(irq);

			/* This races with request_irq(), set_irq_type(),
			 * and set_irq_wake() ... but those are "rare".
			 */
			if (irq >= 0 && desc->action) {
				char *trigger;
				u32 bitmask = nmk_gpio_get_bitmask(gpio);

				if (nmk_chip->edge_rising & bitmask)
					trigger = "edge-rising";
				else if (nmk_chip->edge_falling & bitmask)
					trigger = "edge-falling";
				else
					trigger = "edge-undefined";

				seq_printf(s, " irq-%d %s%s",
					irq, trigger,
					irqd_is_wakeup_set(&desc->irq_data)
						? " wakeup" : "");
			}
		}

		seq_printf(s, "\n");
	}

	clk_disable(nmk_chip->clk);
}

#else
#define nmk_gpio_dbg_show	NULL
#endif

/* This structure is replicated for each GPIO block allocated at probe time */
static struct gpio_chip nmk_gpio_chip = {
	.direction_input	= nmk_gpio_make_input,
	.get			= nmk_gpio_get_input,
	.direction_output	= nmk_gpio_make_output,
	.set			= nmk_gpio_set_output,
	.config			= nmk_gpio_config,
	.to_irq			= nmk_gpio_to_irq,
	.dbg_show		= nmk_gpio_dbg_show,
	.can_sleep		= 0,
};

/**
 * nmk_gpio_clocks_enable() - enable the clocks on all GPIO blocks
 */
void nmk_gpio_clocks_enable(void)
{
	int i;

	for (i = 0; i < NUM_BANKS; i++) {
		struct nmk_gpio_chip *chip = nmk_gpio_chips[i];

		if (!chip)
			continue;

		clk_enable(chip->clk);
	}
}

/**
 * nmk_gpio_clocks_disable() - disable the clocks on all GPIO blocks
 */
void nmk_gpio_clocks_disable(void)
{
	int i;

	for (i = 0; i < NUM_BANKS; i++) {
		struct nmk_gpio_chip *chip = nmk_gpio_chips[i];

		if (!chip)
			continue;

		clk_disable(chip->clk);
	}
}

/*
 * Called from the suspend/resume path to only keep the real wakeup interrupts
 * (those that have had set_irq_wake() called on them) as wakeup interrupts,
 * and not the rest of the interrupts which we needed to have as wakeups for
 * cpuidle.
 *
 * PM ops are not used since this needs to be done at the end, after all the
 * other drivers are done with their suspend callbacks.
 */
void nmk_gpio_wakeups_suspend(void)
{
	int i;

	for (i = 0; i < NUM_BANKS; i++) {
		struct nmk_gpio_chip *chip = nmk_gpio_chips[i];

		if (!chip)
			break;

		clk_enable(chip->clk);

		chip->rwimsc = readl(chip->addr + NMK_GPIO_RWIMSC);
		chip->fwimsc = readl(chip->addr + NMK_GPIO_FWIMSC);

		writel(chip->rwimsc & chip->real_wake,
		       chip->addr + NMK_GPIO_RWIMSC);
		writel(chip->fwimsc & chip->real_wake,
		       chip->addr + NMK_GPIO_FWIMSC);

		if (chip->sleepmode) {
			chip->slpm = readl(chip->addr + NMK_GPIO_SLPC);

			/* 0 -> wakeup enable */
			writel(~chip->real_wake, chip->addr + NMK_GPIO_SLPC);
		}

		clk_disable(chip->clk);
	}
}

void nmk_gpio_wakeups_resume(void)
{
	int i;

	for (i = 0; i < NUM_BANKS; i++) {
		struct nmk_gpio_chip *chip = nmk_gpio_chips[i];

		if (!chip)
			break;

		clk_enable(chip->clk);

		writel(chip->rwimsc, chip->addr + NMK_GPIO_RWIMSC);
		writel(chip->fwimsc, chip->addr + NMK_GPIO_FWIMSC);

		if (chip->sleepmode)
			writel(chip->slpm, chip->addr + NMK_GPIO_SLPC);

		clk_disable(chip->clk);
	}
}

/*
 * Read the pull up/pull down status.
 * A bit set in 'pull_up' means that pull up
 * is selected if pull is enabled in PDIS register.
 * Note: only pull up/down set via this driver can
 * be detected due to HW limitations.
 */
void nmk_gpio_read_pull(int gpio_bank, u32 *pull_up)
{
	if (gpio_bank < NUM_BANKS) {
		struct nmk_gpio_chip *chip = nmk_gpio_chips[gpio_bank];

		if (!chip)
			return;

		*pull_up = chip->pull_up;
	}
}

static int __devinit nmk_gpio_probe(struct platform_device *dev)
{
	struct nmk_gpio_platform_data *pdata = dev->dev.platform_data;
	struct nmk_gpio_chip *nmk_chip;
	struct gpio_chip *chip;
	struct resource *res;
	struct clk *clk;
	int secondary_irq;
	int irq;
	int ret;

	if (!pdata)
		return -ENODEV;

	res = platform_get_resource(dev, IORESOURCE_MEM, 0);
	if (!res) {
		ret = -ENOENT;
		goto out;
	}

	irq = platform_get_irq(dev, 0);
	if (irq < 0) {
		ret = irq;
		goto out;
	}

	secondary_irq = platform_get_irq(dev, 1);
	if (secondary_irq >= 0 && !pdata->get_secondary_status) {
		ret = -EINVAL;
		goto out;
	}

	if (request_mem_region(res->start, resource_size(res),
			       dev_name(&dev->dev)) == NULL) {
		ret = -EBUSY;
		goto out;
	}

	clk = clk_get(&dev->dev, NULL);
	if (IS_ERR(clk)) {
		ret = PTR_ERR(clk);
		goto out_release;
	}

	nmk_chip = kzalloc(sizeof(*nmk_chip), GFP_KERNEL);
	if (!nmk_chip) {
		ret = -ENOMEM;
		goto out_clk;
	}
	/*
	 * The virt address in nmk_chip->addr is in the nomadik register space,
	 * so we can simply convert the resource address, without remapping
	 */
	nmk_chip->bank = dev->id;
	nmk_chip->clk = clk;
	nmk_chip->addr = io_p2v(res->start);
	nmk_chip->chip = nmk_gpio_chip;
	nmk_chip->parent_irq = irq;
	nmk_chip->secondary_parent_irq = secondary_irq;
	nmk_chip->get_secondary_status = pdata->get_secondary_status;
	nmk_chip->set_ioforce = pdata->set_ioforce;
	nmk_chip->sleepmode = pdata->supports_sleepmode;
	spin_lock_init(&nmk_chip->lock);

	chip = &nmk_chip->chip;
	chip->base = pdata->first_gpio;
	chip->ngpio = pdata->num_gpio;
	chip->label = pdata->name ?: dev_name(&dev->dev);
	chip->dev = &dev->dev;
	chip->owner = THIS_MODULE;

	ret = gpiochip_add(&nmk_chip->chip);
	if (ret)
		goto out_free;

	BUG_ON(nmk_chip->bank >= ARRAY_SIZE(nmk_gpio_chips));

	nmk_gpio_chips[nmk_chip->bank] = nmk_chip;
	platform_set_drvdata(dev, nmk_chip);

	nmk_gpio_init_irq(nmk_chip);

	dev_info(&dev->dev, "Bits %i-%i at address %p\n",
		 nmk_chip->chip.base, nmk_chip->chip.base+31, nmk_chip->addr);
	return 0;

out_free:
	kfree(nmk_chip);
out_clk:
	clk_disable(clk);
	clk_put(clk);
out_release:
	release_mem_region(res->start, resource_size(res));
out:
	dev_err(&dev->dev, "Failure %i for GPIO %i-%i\n", ret,
		  pdata->first_gpio, pdata->first_gpio+31);
	return ret;
}

static struct platform_driver nmk_gpio_driver = {
	.driver = {
		.owner = THIS_MODULE,
		.name = "gpio",
	},
	.probe = nmk_gpio_probe,
};

static int __init nmk_gpio_init(void)
{
	return platform_driver_register(&nmk_gpio_driver);
}

core_initcall(nmk_gpio_init);

MODULE_AUTHOR("Prafulla WADASKAR and Alessandro Rubini");
MODULE_DESCRIPTION("Nomadik GPIO Driver");
MODULE_LICENSE("GPL");
