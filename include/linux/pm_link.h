/*
 * include/linux/pm_link.h - PM links manipulation core.
 *
 * Copyright (c) 2009 Rafael J. Wysocki <rjw@sisk.pl>, Novell Inc.
 *
 * This file is released under the GPLv2.
 */

#ifndef _LINUX_PM_LINK_H
#define _LINUX_PM_LINK_H

#include <linux/list.h>

struct device;

struct pm_link {
	struct device *master;
	struct list_head master_hook;
	struct device *slave;
	struct list_head slave_hook;
};

extern int pm_link_add(struct device *slave, struct device *master);
extern void pm_link_remove(struct device *dev, struct device *master);
extern int device_for_each_master(struct device *slave, void *data,
			   int (*fn)(struct device *dev, void *data));
extern int device_for_each_slave(struct device *master, void *data,
			  int (*fn)(struct device *dev, void *data));

#endif
