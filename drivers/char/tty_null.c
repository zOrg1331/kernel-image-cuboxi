/*
 * NULL console - the /dev/null analogue in the ttys world.
 * Taken from linux/arch/alpha/kernel/nullcons.c
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/tty.h>
#include <linux/tty_driver.h>

static int nullcons_write(struct tty_struct *tty,
	      const unsigned char *buf, int count)
{
	return count;
}

static int nullcons_open(struct tty_struct *tty, struct file *filp)
{
	return 0;
}

static void nullcons_close(struct tty_struct *tty, struct file *filp)
{
}

static int nullcons_write_room(struct tty_struct *tty)
{
	return 512;
}

static int nullcons_chars_in_buffer(struct tty_struct *tty)
{
	return 0;
}


static struct tty_driver *nullcons_driver;

static const struct tty_operations nullcons_ops = {
	.open		= nullcons_open,
	.close		= nullcons_close,
	.write		= nullcons_write,
	.write_room	= nullcons_write_room,
	.chars_in_buffer= nullcons_chars_in_buffer,
};

static int __init nullcons_init(void)
{
	struct tty_driver *driver;
	int err;

	driver = alloc_tty_driver(1);
	if (!driver)
		return -ENOMEM;
	driver->driver_name = "null";
	driver->name = "null";
	driver->major = TTYAUX_MAJOR;
	driver->minor_start = 240;
	driver->type = TTY_DRIVER_TYPE_SYSTEM;
	driver->subtype = SYSTEM_TYPE_SYSCONS;
	driver->init_termios = tty_std_termios;
	tty_set_operations(driver, &nullcons_ops);
	err = tty_register_driver(driver);
	if (err) {
		put_tty_driver(driver);
		return err;
	}
	nullcons_driver = driver;

	return 0;
}
module_init(nullcons_init);

static void __exit nullcons_exit(void)
{
	tty_unregister_driver(nullcons_driver);
}
module_exit(nullcons_exit);

MODULE_LICENSE("GPL");
