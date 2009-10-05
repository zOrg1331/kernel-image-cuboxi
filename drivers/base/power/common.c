/*
 * drivers/base/power/common.c - device PM common functions.
 *
 * Copyright (c) 2009 Rafael J. Wysocki <rjw@sisk.pl>, Novell Inc.
 *
 * This file is released under the GPLv2.
 */

#include <linux/rculist.h>
#include <linux/device.h>
#include <linux/srcu.h>
#include <linux/pm_link.h>

#include "power.h"

/**
 * device_pm_init - Initialize the PM part of a device object.
 * @dev: Device object being initialized.
 */
void device_pm_init(struct device *dev)
{
	dev->power.status = DPM_ON;
	spin_lock_init(&dev->power.lock);
	INIT_LIST_HEAD(&dev->power.master_links);
	INIT_LIST_HEAD(&dev->power.slave_links);
	pm_runtime_init(dev);
}

/**
 * device_pm_add - Handle the PM part of a device added to device tree.
 * @dev: Device object being added to device tree.
 */
void device_pm_add(struct device *dev)
{
	pr_debug("PM: Adding info for %s:%s\n",
		 dev->bus ? dev->bus->name : "No Bus",
		 kobject_name(&dev->kobj));
	device_pm_list_add(dev);
}

/**
 * device_pm_remove - Handle the PM part of a device removed from device tree.
 * @dev: Device object being removed from device tree.
 */
void device_pm_remove(struct device *dev)
{
	pr_debug("PM: Removing info for %s:%s\n",
		 dev->bus ? dev->bus->name : "No Bus",
		 kobject_name(&dev->kobj));
	device_pm_list_remove(dev);
	pm_runtime_remove(dev);
	pm_link_remove_all(dev);
}

/*
 * PM links framework.
 *
 * There are PM dependencies between devices that are not reflected by the
 * structure of the device tree.  In other words, as far as PM is concerned, a
 * device may depend on some other devices which are not its children and none
 * of which is its parent.
 *
 * Every such dependency involves two devices, one of which is a "master" and
 * the other of which is a "slave", meaning that the "slave" have to be
 * suspended before the "master" and cannot be woken up before it.  Thus every
 * device can be given two lists of "dependency objects", one for the
 * dependencies where the device is the "master" and the other for the
 * dependencies where the device is the "slave".  Then, each "dependency object"
 * can be represented as 'struct pm_link' as defined in include/linux/pm_link.h.
 *
 * The PM links of a device can help decide when the device should be suspended
 * or resumed.  Namely, In addition to checking the device's parent, the PM core
 * can walk the list of its "masters" and check their PM status.  Similarly, in
 * addition to walking the list of a device's children, the PM core can walk the
 * list of its "slaves".
 */

static struct srcu_struct pm_link_ss;
static DEFINE_MUTEX(pm_link_mtx);

/**
 * pm_link_add - Create a PM link object connecting two devices.
 * @slave: Device to be the slave in this link.
 * @master: Device to be the master in this link.
 */
int pm_link_add(struct device *slave, struct device *master)
{
	struct pm_link *link;
	int error = -ENODEV;

	if (!get_device(master))
		return error;

	if (!get_device(slave))
		goto err_slave;

	link = kzalloc(sizeof(*link), GFP_KERNEL);
	if (!link)
		goto err_link;

	dev_dbg(slave, "PM: Creating PM link to (master) %s %s\n",
		dev_driver_string(master), dev_name(master));

	link->master = master;
	INIT_LIST_HEAD(&link->master_hook);
	link->slave = slave;
	INIT_LIST_HEAD(&link->slave_hook);

	spin_lock_irq(&master->power.lock);
	list_add_tail_rcu(&link->master_hook, &master->power.master_links);
	spin_unlock_irq(&master->power.lock);

	spin_lock_irq(&slave->power.lock);
	list_add_tail_rcu(&link->slave_hook, &slave->power.slave_links);
	spin_unlock_irq(&slave->power.lock);

	return 0;

 err_link:
	error = -ENOMEM;
	put_device(slave);

 err_slave:
	put_device(master);

	return error;
}
EXPORT_SYMBOL_GPL(pm_link_add);

/**
 * __pm_link_remove - Remove a PM link object.
 * @link: PM link object to remove
 */
static void __pm_link_remove(struct pm_link *link)
{
	struct device *master = link->master;
	struct device *slave = link->slave;

	dev_dbg(slave, "PM: Removing PM link to (master) %s %s\n",
		dev_driver_string(master), dev_name(master));

	spin_lock_irq(&master->power.lock);
	list_del_rcu(&link->master_hook);
	spin_unlock_irq(&master->power.lock);

	spin_lock_irq(&slave->power.lock);
	list_del_rcu(&link->slave_hook);
	spin_unlock_irq(&slave->power.lock);

	synchronize_srcu(&pm_link_ss);

	kfree(link);

	put_device(master);
	put_device(slave);
}

/**
 * pm_link_remove_all - Remove all PM link objects for given device.
 * @dev: Device to handle.
 */
void pm_link_remove_all(struct device *dev)
{
	struct pm_link *link, *n;

	mutex_lock(&pm_link_mtx);

	list_for_each_entry_safe(link, n, &dev->power.master_links, master_hook)
		__pm_link_remove(link);

	list_for_each_entry_safe(link, n, &dev->power.slave_links, slave_hook)
		__pm_link_remove(link);

	mutex_unlock(&pm_link_mtx);
}

/**
 * pm_link_remove - Remove a PM link object connecting two devices.
 * @dev: Slave device of the PM link to remove.
 * @master: Master device of the PM link to remove.
 */
void pm_link_remove(struct device *dev, struct device *master)
{
	struct pm_link *link, *n;

	mutex_lock(&pm_link_mtx);

	list_for_each_entry_safe(link, n, &dev->power.slave_links, slave_hook) {
		if (link->master != master)
			continue;

		__pm_link_remove(link);
		break;
	}

	mutex_unlock(&pm_link_mtx);
}
EXPORT_SYMBOL_GPL(pm_link_remove);

/**
 * device_for_each_master - Execute given function for each master of a device.
 * @slave: Device whose masters to execute the function for.
 * @data: Data pointer to pass to the function.
 * @fn: Function to execute for each master of @slave.
 *
 * The function is executed for the parent of the device, if there is one, and
 * for each device connected to it via a pm_link object where @slave is the
 * "slave".
 */
int device_for_each_master(struct device *slave, void *data,
			   int (*fn)(struct device *dev, void *data))
{
	struct pm_link *link;
	int idx;
	int error = 0;

	if (slave->parent) {
		error = fn(slave->parent, data);
		if (error)
			return error;
	}

	idx = srcu_read_lock(&pm_link_ss);

	list_for_each_entry_rcu(link, &slave->power.slave_links, slave_hook) {
		struct device *master = link->master;

		error = fn(master, data);
		if (error)
			break;
	}

	srcu_read_unlock(&pm_link_ss, idx);

	return error;
}
EXPORT_SYMBOL_GPL(device_for_each_master);

/**
 * device_for_each_slave - Execute given function for each slave of a device.
 * @master: Device whose slaves to execute the function for.
 * @data: Data pointer to pass to the function.
 * @fn: Function to execute for each slave of @master.
 *
 * The function is executed for all children of the device, if there are any,
 * and for each device connected to it via a pm_link object where @master is the
 * "master".
 */
int device_for_each_slave(struct device *master, void *data,
			  int (*fn)(struct device *dev, void *data))
{
	struct pm_link *link;
	int idx;
	int error;

	error = device_for_each_child(master, data, fn);
	if (error)
		return error;

	idx = srcu_read_lock(&pm_link_ss);

	list_for_each_entry_rcu(link, &master->power.master_links,
				master_hook) {
		struct device *slave = link->slave;

		error = fn(slave, data);
		if (error)
			break;
	}

	srcu_read_unlock(&pm_link_ss, idx);

	return error;
}
EXPORT_SYMBOL_GPL(device_for_each_slave);

int __init pm_link_init(void)
{
	return init_srcu_struct(&pm_link_ss);
}
