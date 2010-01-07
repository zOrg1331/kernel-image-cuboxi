/*
 * (C) Copyright 2009-2010
 * Nokia Siemens Networks, michael.lawnick.ext@nsn.com
 *
 * This is a driver for the i2c adapter in Cavium Networks' OCTEON processors.
 *
 * Release 0.1
 *
 * This file is licensed under the terms of the GNU General Public
 * License version 2. This program is licensed "as is" without any
 * warranty of any kind, whether express or implied.
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/sched.h>
#include <linux/init.h>

#include <linux/io.h>
#include <linux/i2c.h>
#include <linux/interrupt.h>
#include <linux/delay.h>
#include <linux/platform_device.h>

#include <asm/octeon/octeon.h>

#define DRV_NAME "i2c-octeon"
#define DRV_VERSION	"0.1"

/* register offsets */
#define SW_TWSI	 0x00
#define TWSI_INT 0x10

/* Controller command patterns */
#define SW_TWSI_V               0x8000000000000000ull
#define SW_TWSI_EOP_TWSI_DATA   0x0C00000100000000ull
#define SW_TWSI_EOP_TWSI_CTL    0x0C00000200000000ull
#define SW_TWSI_EOP_TWSI_CLKCTL 0x0C00000300000000ull
#define SW_TWSI_EOP_TWSI_STAT   0x0C00000300000000ull
#define SW_TWSI_EOP_TWSI_RST    0x0C00000700000000ull
#define SW_TWSI_OP_TWSI_CLK     0x0800000000000000ull
#define SW_TWSI_R               0x0100000000000000ull

/* Controller command and status bits */
#define TWSI_CTL_CE   0x80
#define TWSI_CTL_ENAB 0x40
#define TWSI_CTL_STA  0x20
#define TWSI_CTL_STP  0x10
#define TWSI_CTL_IFLG 0x08
#define TWSI_CTL_AAK  0x04

/* Some status values */
#define STAT_START      0x08
#define STAT_RSTART     0x10
#define STAT_TXADDR_ACK 0x18
#define STAT_TXDATA_ACK 0x28
#define STAT_RXADDR_ACK 0x40
#define STAT_RXDATA_ACK 0x50
#define STAT_IDLE       0xF8

#ifndef NO_IRQ
#define NO_IRQ (-1)
#endif

struct octeon_i2c {
	wait_queue_head_t queue;
	struct i2c_adapter adap;
	int irq;
	int twsi_freq;
	int sys_freq;
	uint8_t twsi_ctl;
	resource_size_t twsi_phys;
	void __iomem *twsi_base;
	resource_size_t regsize;
	struct device *dev;
};

/* Writes need to be flushed by a read. */
static void octeon_i2c_write_sw(struct octeon_i2c *i2c,
				uint64_t eop_reg,
				uint8_t data)
{
	uint64_t tmp;

	__raw_writeq(SW_TWSI_V | eop_reg | data, i2c->twsi_base + SW_TWSI);
	tmp = __raw_readq(i2c->twsi_base + SW_TWSI);
}

static uint8_t octeon_i2c_read_sw(struct octeon_i2c *i2c, uint64_t eop_reg)
{
	uint64_t tmp;

	__raw_writeq(SW_TWSI_V | eop_reg | SW_TWSI_R, i2c->twsi_base + SW_TWSI);
	tmp = __raw_readq(i2c->twsi_base + SW_TWSI);

	return __raw_readq(i2c->twsi_base + SW_TWSI) & 0xFF;
}

static void octeon_i2c_write_int(struct octeon_i2c *i2c, uint64_t data)
{
	uint64_t tmp;

	__raw_writeq(data, i2c->twsi_base + TWSI_INT);
	tmp = __raw_readq(i2c->twsi_base + TWSI_INT);
}

static void octeon_i2c_int_enable(struct octeon_i2c *i2c)
{
	octeon_i2c_write_int(i2c, 0x40);
}

static void octeon_i2c_int_disable(struct octeon_i2c *i2c)
{
	octeon_i2c_write_int(i2c, 0);
}

/* If there was a reset while a device was driving 0 to bus,
   bus is blocked. We toggle it free manually by some clock
   cycles and send a stop. */
static void octeon_i2c_unblock(struct octeon_i2c *i2c)
{
	int i;

	dev_dbg(i2c->dev, "%s\n", __func__);
	for (i = 0; i < 9; i++) {
		octeon_i2c_write_int(i2c, 0x0);
		udelay(5);
		octeon_i2c_write_int(i2c, 0x200);
		udelay(5);
	}
	octeon_i2c_write_int(i2c, 0x300);
	udelay(5);
	octeon_i2c_write_int(i2c, 0x100);
	udelay(5);
	octeon_i2c_write_int(i2c, 0x0);
}

static irqreturn_t octeon_i2c_isr(int irq, void *dev_id)
{
	struct octeon_i2c *i2c = dev_id;

	octeon_i2c_int_disable(i2c);
	i2c->twsi_ctl = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_CTL);
	wake_up_interruptible(&i2c->queue);

	return IRQ_HANDLED;
}

static int octeon_i2c_wait(struct octeon_i2c *i2c)
{
	unsigned long orig_jiffies = jiffies;
	uint8_t ctl;
	int result = 0;

	if (i2c->irq == NO_IRQ) {
		/* polling */
		do {
			ctl = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_CTL);
			if (ctl & TWSI_CTL_IFLG)
				break;
		} while (!time_after(jiffies,
					orig_jiffies + i2c->adap.timeout));

		if (!(ctl & TWSI_CTL_IFLG)) {
			dev_dbg(i2c->dev, "%s: timeout\n", __func__);
			result = -ETIMEDOUT;
		}
	} else {
		i2c->twsi_ctl = 0;
		/* interrupt mode */
		octeon_i2c_int_enable(i2c);

		result = wait_event_interruptible_timeout(i2c->queue,
				(i2c->twsi_ctl & TWSI_CTL_IFLG),
				i2c->adap.timeout);

		if (unlikely(result < 0)) {
			dev_dbg(i2c->dev, "%s: wait interrupted\n", __func__);
		} else if (unlikely(!(i2c->twsi_ctl & TWSI_CTL_IFLG))) {
			dev_dbg(i2c->dev, "%s: timeout\n", __func__);
			result = -ETIMEDOUT;
		}
	}

	return result < 0 ? result : 0;
}

static int octeon_i2c_start(struct octeon_i2c *i2c)
{
	uint8_t data;
	int result;

	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL,
				TWSI_CTL_ENAB | TWSI_CTL_STA);

	result = octeon_i2c_wait(i2c);
	if (unlikely(result < 0) &&
	    octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_STAT) == STAT_IDLE) {
		/*
		 * Controller refused to send start flag May be a
		 * client is holding SDA low - let's try to free it.
		 */
		octeon_i2c_unblock(i2c);
		octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL,
				    TWSI_CTL_ENAB | TWSI_CTL_STA);

		result = octeon_i2c_wait(i2c);
		if (result < 0)
			return result;
	}

	data = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_STAT);
	if ((data != STAT_START) && (data != STAT_RSTART)) {
		dev_dbg(i2c->dev, "%s: bad status (0x%x)\n", __func__, data);
		return -1;
	}

	return 0;
}

static int octeon_i2c_stop(struct octeon_i2c *i2c)
{
	unsigned long orig_jiffies = jiffies;
	uint8_t data;

	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL,
				TWSI_CTL_ENAB | TWSI_CTL_STP);

	/*
	 * Controller will change to idle, but that does not raise an
	 * interrupt, so we have to poll.
	 */
	do {
		data = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_STAT);
		if (data == STAT_IDLE)
			break;
		udelay(1);
	} while (!time_after(jiffies, orig_jiffies + 2));

	if (data != STAT_IDLE) {
		dev_dbg(i2c->dev, "%s: bad status(0x%x)\n", __func__, data);
		return -1;
	}
	return 0;
}

static int octeon_i2c_write(struct octeon_i2c *i2c, int target,
			    const uint8_t *data, int length)
{
	int i, result;
	uint8_t tmp;

	result = octeon_i2c_start(i2c);
	if (unlikely(result < 0))
		return result;

	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_DATA, target << 1);
	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL, TWSI_CTL_ENAB);

	result = octeon_i2c_wait(i2c);
	if (unlikely(result < 0))
		return result;

	for (i = 0; i < length; i++) {
		tmp = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_STAT);
		if ((tmp != STAT_TXADDR_ACK) && (tmp != STAT_TXDATA_ACK)) {
			dev_dbg(i2c->dev,
				"%s: bad status before write (0x%x)\n",
				__func__, tmp);
			return -(int)tmp;
		}

		octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_DATA, data[i]);
		octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL, TWSI_CTL_ENAB);

		result = octeon_i2c_wait(i2c);
		if (unlikely(result < 0))
			return result;
	}

	return 0;
}

static int octeon_i2c_read(struct octeon_i2c *i2c, int target,
			   uint8_t *data, int length)
{
	int i, result;
	uint8_t tmp;

	if (length < 1)
		return -EINVAL;

	result = octeon_i2c_start(i2c);
	if (result)
		return result;

	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_DATA, (target<<1) | 1);
	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL, TWSI_CTL_ENAB);

	result = octeon_i2c_wait(i2c);
	if (unlikely(result < 0))
		return result;

	for (i = 0; i < length; i++) {
		tmp = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_STAT);
		if ((tmp != STAT_RXDATA_ACK) && (tmp != STAT_RXADDR_ACK)) {
			dev_dbg(i2c->dev,
				"%s: bad status before read (0x%x)\n",
				__func__, tmp);
			return -(int)tmp;
		}

		if (i+1 < length)
			octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL,
						TWSI_CTL_ENAB | TWSI_CTL_AAK);
		else
			octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL,
						TWSI_CTL_ENAB);

		result = octeon_i2c_wait(i2c);
		if (unlikely(result < 0))
			return result;

		data[i] = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_DATA);
	}
	return length;
}

static int octeon_i2c_xfer(struct i2c_adapter *adap,
			   struct i2c_msg *msgs,
			   int num)
{
	struct i2c_msg *pmsg;
	int i;
	int ret = 0;
	struct octeon_i2c *i2c = i2c_get_adapdata(adap);

	for (i = 0; ret >= 0 && i < num; i++) {
		pmsg = &msgs[i];
		dev_dbg(i2c->dev,
			"%s: Doing %s %d byte(s) to/from 0x%02x - "
			"%d of %d messages\n",
			 __func__,
			 pmsg->flags & I2C_M_RD ? "read" : "write",
			 pmsg->len, pmsg->addr, i + 1, num);
		if (pmsg->flags & I2C_M_RD)
			ret = octeon_i2c_read(i2c, pmsg->addr, pmsg->buf,
						pmsg->len);
		else
			ret = octeon_i2c_write(i2c, pmsg->addr, pmsg->buf,
						pmsg->len);
	}
	octeon_i2c_stop(i2c);

	return (ret < 0) ? ret : num;
}

static u32 octeon_i2c_functionality(struct i2c_adapter *adap)
{
	return I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL;
}

static const struct i2c_algorithm octeon_i2c_algo = {
	.master_xfer = octeon_i2c_xfer,
	.functionality = octeon_i2c_functionality,
};

static struct i2c_adapter octeon_i2c_ops = {
	.owner = THIS_MODULE,
	.name = "OCTEON adapter",
	.algo = &octeon_i2c_algo,
	.timeout = 2,
};

static int __init octeon_i2c_setclock(struct octeon_i2c *i2c)
{
	int tclk, thp_base, inc, thp_idx, mdiv_idx, ndiv_idx, foscl, diff;
	int thp = 0x18, mdiv = 2, ndiv = 0, delta_hz = 1000000;

	for (ndiv_idx = 0; ndiv_idx < 8 && delta_hz != 0; ndiv_idx++) {
		/*
		 * An mdiv value of less than 2 seems to not work well
		 * with ds1337 RTCs, so we constrain it to larger
		 * values.
		 */
		for (mdiv_idx = 15; mdiv_idx >= 2 && delta_hz != 0; mdiv_idx--) {
			/*
			 * For given ndiv and mdiv values check the
			 * two closest thp values.
			 */
			tclk = i2c->twsi_freq * (mdiv_idx + 1) * 10;
			tclk *= (1 << ndiv_idx);
			thp_base = (i2c->sys_freq / (tclk * 2)) - 1;
			for (inc = 0; inc <= 1; inc++) {
				thp_idx = thp_base + inc;
				if (thp_idx < 5 || thp_idx > 0xff)
					continue;

				foscl = i2c->sys_freq / (2 * (thp_idx + 1));
				foscl = foscl / (1 << ndiv_idx);
				foscl = foscl / (mdiv_idx + 1) / 10;
				diff = abs(foscl - i2c->twsi_freq);
				if (diff < delta_hz) {
					delta_hz = diff;
					thp = thp_idx;
					mdiv = mdiv_idx;
					ndiv = ndiv_idx;
				}
			}
		}
	}
	octeon_i2c_write_sw(i2c, SW_TWSI_OP_TWSI_CLK, thp);
	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CLKCTL, (mdiv << 3) | ndiv);

	return 0;
}

static int __init octeon_i2c_initlowlevel(struct octeon_i2c *i2c)
{
	uint8_t status;
	int tries;

	/* disable high level controller, enable bus access */
	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_CTL, TWSI_CTL_ENAB);

	/* reset controller */
	octeon_i2c_write_sw(i2c, SW_TWSI_EOP_TWSI_RST, 0);

	for (tries = 10; tries; tries--) {
		udelay(1);
		status = octeon_i2c_read_sw(i2c, SW_TWSI_EOP_TWSI_STAT);
		if (status == STAT_IDLE)
			return 0;
	}
	dev_dbg(i2c->dev, "%s: TWSI_RST failed! (0x%x)\n", __func__, status);
	return -1;
}

static int __init octeon_i2c_probe(struct platform_device *pdev)
{
	int irq, result = 0;
	struct octeon_i2c *i2c;
	struct octeon_i2c_data *i2c_data;
	struct resource *res_mem;

	i2c = kzalloc(sizeof(*i2c), GFP_KERNEL);
	if (!i2c) {
		printk(KERN_ERR "%s i2c-cavium - kzalloc failed\n", __func__);
		return -ENOMEM;
	}
	i2c->dev = &pdev->dev;
	i2c_data = pdev->dev.platform_data;

	res_mem = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	irq = platform_get_irq(pdev, 0);

	if (res_mem == NULL) {
		dev_dbg(i2c->dev, "%s: found no memory resource\n", __func__);
		kfree(i2c);
		return -ENODEV;
	}

	if (i2c_data == NULL) {
		dev_dbg(i2c->dev, "%s: no I2C frequence data\n", __func__);
		kfree(i2c);
		return -ENODEV;
	}

	i2c->twsi_phys = res_mem->start;
	i2c->regsize = resource_size(res_mem);
	i2c->twsi_freq = i2c_data->i2c_freq;
	i2c->sys_freq = i2c_data->sys_freq;

	if (!request_mem_region(i2c->twsi_phys, i2c->regsize, res_mem->name)) {
		dev_dbg(i2c->dev,
			"%s i2c-cavium - request_mem_region failed\n",
			__func__);
		goto fail_region;
	}
	i2c->twsi_base = ioremap(i2c->twsi_phys, i2c->regsize);

	init_waitqueue_head(&i2c->queue);

	i2c->irq = irq;
	if (i2c->irq != NO_IRQ) {
		/* i2c->irq = NO_IRQ implies polling */
		result = request_irq(i2c->irq, octeon_i2c_isr, 0, DRV_NAME, i2c);
		if (result < 0) {
			dev_dbg(i2c->dev,
				"%s: - failed to attach interrupt\n",
				__func__);
			goto fail_irq;
		}
	}

	result = octeon_i2c_initlowlevel(i2c);
	if (result) {
		dev_dbg(i2c->dev, "%s: init low level failed\n", __func__);
		goto  fail_add;
	}

	result = octeon_i2c_setclock(i2c);
	if (result) {
		dev_dbg(i2c->dev, "%s: clock init failed\n", __func__);
		goto  fail_add;
	}

	i2c->adap = octeon_i2c_ops;
	i2c->adap.dev.parent = &pdev->dev;
	i2c->adap.nr = pdev->id >= 0 ? pdev->id : 0;
	i2c_set_adapdata(&i2c->adap, i2c);
	platform_set_drvdata(pdev, i2c);

	result = i2c_add_numbered_adapter(&i2c->adap);
	if (result < 0) {
		dev_dbg(i2c->dev, "%s: failed to add adapter\n", __func__);
		goto fail_add;
	}
	return result;

fail_add:
	platform_set_drvdata(pdev, NULL);
	if (i2c->irq != NO_IRQ)
		free_irq(i2c->irq, i2c);
fail_irq:
	iounmap(i2c->twsi_base);
	release_mem_region(i2c->twsi_phys, i2c->regsize);
fail_region:
	kfree(i2c);
	return result;
};

static int __exit octeon_i2c_remove(struct platform_device *pdev)
{
	struct octeon_i2c *i2c = platform_get_drvdata(pdev);

	i2c_del_adapter(&i2c->adap);
	platform_set_drvdata(pdev, NULL);
	if (i2c->irq != NO_IRQ)
		free_irq(i2c->irq, i2c);
	iounmap(i2c->twsi_base);
	release_mem_region(i2c->twsi_phys, i2c->regsize);
	kfree(i2c);
	return 0;
};

static struct platform_driver octeon_i2c_driver = {
	.probe		= octeon_i2c_probe,
	.remove		= __exit_p(octeon_i2c_remove),
	.driver		= {
		.owner	= THIS_MODULE,
		.name	= DRV_NAME,
	},
};

static int __init octeon_i2c_init(void)
{
	int rv;

	rv = platform_driver_register(&octeon_i2c_driver);
	printk(KERN_INFO "driver %s is loaded\n", DRV_NAME);
	return rv;
}

static void __exit octeon_i2c_exit(void)
{
	platform_driver_unregister(&octeon_i2c_driver);
	printk(KERN_INFO "driver %s unloaded\n", DRV_NAME);
}

MODULE_AUTHOR("Michael Lawnick <michael.lawnick.ext@nsn.com>");
MODULE_DESCRIPTION("I2C-Bus adapter for Cavium OCTEON processors");
MODULE_LICENSE("GPL");
MODULE_VERSION(DRV_VERSION);
MODULE_ALIAS("platform:" DRV_NAME);

module_init(octeon_i2c_init);
module_exit(octeon_i2c_exit);
