#ifndef __LINUX_GPIO_H
#define __LINUX_GPIO_H

/* see Documentation/gpio.txt */

/*
 * Bias modes for GPIOs - if you have more biases, add them here or provide
 * custom enumerators for your driver if you find they are not generally
 * useful.
 *
 * GPIO_CONFIG_BIAS_UNKNOWN: this bias mode is not known to us
 * GPIO_CONFIG_BIAS_FLOAT: no specific bias, the GPIO will float or state
 *	is not controlled by software
 * GPIO_CONFIG_BIAS_PULL_UP: the GPIO will be pulled up (usually with high
 *	impedance to VDD)
 * GPIO_CONFIG_BIAS_PULL_DOWN: the GPIO will be pulled down (usually with high
 *	impedance to GROUND)
 * GPIO_BIAS_HIGH: the GPIO will be wired high, connected to VDD
 * GPIO_BIAS_GROUND: the GPIO will be grounded, connected to GROUND
 */
#define GPIO_CONFIG_BIAS_UNKNOWN	0x1000
#define GPIO_CONFIG_BIAS_FLOAT		0x1001
#define GPIO_CONFIG_BIAS_PULL_UP	0x1002
#define GPIO_CONFIG_BIAS_PULL_DOWN	0x1003
#define GPIO_CONFIG_BIAS_HIGH		0x1004
#define GPIO_CONFIG_BIAS_GROUND		0x1005

/*
 * Drive modes for GPIOs (output) - if you have more custom modes either
 * add them here or keep them to your driver if you think they are not
 * generally useful.
 *
 * GPIO_CONFIG_DRIVE_UNKNOWN: we don't know the drive mode of this GPIO, for
 *	example since it is controlled by hardware or the information is not
 *	accessible but we need a meaningful enumerator in e.g. initialization
 *	code
 * GPIO_CONFIG_DRIVE_PUSH_PULL: the GPIO will be driven actively high and
 *	low, this is the most typical case and is typically achieved with two
 *	active transistors on the output
 * GPIO_CONFIG_DRIVE_OPEN_DRAIN: the GPIO will be driven with open drain (open
 *	collector) which means it is usually wired with other output ports
 *	which are then pulled up with an external resistor
 * GPIO_CONFIG_DRIVE_OPEN_SOURCE: the GPIO will be driven with open drain
 *	(open emitter) which is the same as open drain mutatis mutandis but
 *	pulled to ground
 * GPIO_CONFIG_DRIVE_OFF: the GPIO pin is set to inactive mode, off
 */
#define GPIO_CONFIG_DRIVE_UNKNOWN	0x2010
#define GPIO_CONFIG_DRIVE_PUSH_PULL	0x2011
#define GPIO_CONFIG_DRIVE_OPEN_DRAIN	0x2012
#define GPIO_CONFIG_DRIVE_OPEN_SOURCE	0x2013
#define GPIO_CONFIG_DRIVE_OFF		0x2014

/*
 * From this value on, the configuration commands are custom and shall be
 * defined in the header file for your specific GPIO driver.
 */
#define GPIO_CONFIG_CUSTOM_BASE		0x8000

#ifdef CONFIG_GENERIC_GPIO
#include <asm/gpio.h>

#else

#include <linux/kernel.h>
#include <linux/types.h>
#include <linux/errno.h>

struct device;
struct gpio;
struct gpio_chip;

/*
 * Some platforms don't support the GPIO programming interface.
 *
 * In case some driver uses it anyway (it should normally have
 * depended on GENERIC_GPIO), these routines help the compiler
 * optimize out much GPIO-related code ... or trigger a runtime
 * warning when something is wrongly called.
 */

static inline int gpio_is_valid(int number)
{
	return 0;
}

static inline int gpio_request(unsigned gpio, const char *label)
{
	return -ENOSYS;
}

static inline int gpio_request_one(unsigned gpio,
					unsigned long flags, const char *label)
{
	return -ENOSYS;
}

static inline int gpio_request_array(struct gpio *array, size_t num)
{
	return -ENOSYS;
}

static inline void gpio_free(unsigned gpio)
{
	might_sleep();

	/* GPIO can never have been requested */
	WARN_ON(1);
}

static inline void gpio_free_array(struct gpio *array, size_t num)
{
	might_sleep();

	/* GPIO can never have been requested */
	WARN_ON(1);
}

static inline int gpio_direction_input(unsigned gpio)
{
	return -ENOSYS;
}

static inline int gpio_direction_output(unsigned gpio, int value)
{
	return -ENOSYS;
}

static inline int gpio_set_debounce(unsigned gpio, unsigned debounce)
{
	return -ENOSYS;
}

static inline int gpio_get_value(unsigned gpio)
{
	/* GPIO can never have been requested or set as {in,out}put */
	WARN_ON(1);
	return 0;
}

static inline void gpio_set_value(unsigned gpio, int value)
{
	/* GPIO can never have been requested or set as output */
	WARN_ON(1);
}

static inline int gpio_cansleep(unsigned gpio)
{
	/* GPIO can never have been requested or set as {in,out}put */
	WARN_ON(1);
	return 0;
}

static inline int gpio_get_value_cansleep(unsigned gpio)
{
	/* GPIO can never have been requested or set as {in,out}put */
	WARN_ON(1);
	return 0;
}

static inline void gpio_set_value_cansleep(unsigned gpio, int value)
{
	/* GPIO can never have been requested or set as output */
	WARN_ON(1);
}

static inline int gpio_export(unsigned gpio, bool direction_may_change)
{
	/* GPIO can never have been requested or set as {in,out}put */
	WARN_ON(1);
	return -EINVAL;
}

static inline int gpio_export_link(struct device *dev, const char *name,
				unsigned gpio)
{
	/* GPIO can never have been exported */
	WARN_ON(1);
	return -EINVAL;
}

static inline int gpio_sysfs_set_active_low(unsigned gpio, int value)
{
	/* GPIO can never have been requested */
	WARN_ON(1);
	return -EINVAL;
}

static inline void gpio_unexport(unsigned gpio)
{
	/* GPIO can never have been exported */
	WARN_ON(1);
}

static inline int gpio_to_irq(unsigned gpio)
{
	/* GPIO can never have been requested or set as input */
	WARN_ON(1);
	return -EINVAL;
}

static inline int irq_to_gpio(unsigned irq)
{
	/* irq can never have been returned from gpio_to_irq() */
	WARN_ON(1);
	return -EINVAL;
}

static inline int gpio_config(unsigned gpio, u16 param, unsigned long *data)
{
	/* GPIO can never have been requested */
	WARN_ON(1);
	return -EINVAL;
}

#endif

#endif /* __LINUX_GPIO_H */
