/*
 *  als_sys.c - Ambient Light Sensor Sysfs support.
 *
 *  Copyright (C) 2009 Intel Corp
 *  Copyright (C) 2009 Zhang Rui <rui.zhang@intel.com>
 *
 *  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; version 2 of the License.
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License along
 *  with this program; if not, write to the Free Software Foundation, Inc.,
 *  59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
 *
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 */

#include <linux/module.h>
#include <linux/device.h>
#include <linux/err.h>
#include <linux/kdev_t.h>

MODULE_AUTHOR("Zhang Rui <rui.zhang@intel.com>");
MODULE_DESCRIPTION("Ambient Light Sensor sysfs/class support");
MODULE_LICENSE("GPL");

static struct class *als_class;

/**
 * als_device_register - register a new Ambient Light Sensor class device
 * @parent:	the device to register.
 *
 * Returns the pointer to the new device
 */
struct device *als_device_register(struct device *dev, char *name)
{
	return device_create(als_class, dev, MKDEV(0, 0), NULL, name);
}
EXPORT_SYMBOL(als_device_register);

/**
 * als_device_unregister - removes the registered ALS class device
 * @dev:	the class device to destroy.
 */
void als_device_unregister(struct device *dev)
{
	device_unregister(dev);
}
EXPORT_SYMBOL(als_device_unregister);

static int __init als_init(void)
{
	als_class = class_create(THIS_MODULE, "als");
	if (IS_ERR(als_class)) {
		printk(KERN_ERR "als_sys.c: couldn't create sysfs class\n");
		return PTR_ERR(als_class);
	}
	return 0;
}

static void __exit als_exit(void)
{
	class_destroy(als_class);
}

subsys_initcall(als_init);
module_exit(als_exit);
