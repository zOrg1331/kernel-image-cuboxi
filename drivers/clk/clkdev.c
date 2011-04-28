/*
 * drivers/clk/clkdev.c
 *
 *  Copyright (C) 2008 Russell King.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 *
 * Helper for the clk API to assist looking up a struct clk.
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/list.h>
#include <linux/errno.h>
#include <linux/err.h>
#include <linux/string.h>
#include <linux/mutex.h>
#include <linux/clk.h>
#include <linux/clkdev.h>

static LIST_HEAD(clocks);
static DEFINE_MUTEX(clocks_mutex);

/*
 * Find the correct struct clk for the device and connection ID.
 * We do slightly fuzzy matching here:
 *  An entry with a NULL ID is assumed to be a wildcard.
 *  If an entry has a device ID, it must match
 *  If an entry has a connection ID, it must match
 * Then we take the most specific entry - with the following
 * order of precedence: dev+con > dev only > con only.
 *
 * if id > 0 the dev_id will just contain the base name of the device
 * it's need to search dev_id before slab is available
 */
static struct clk *clk_find(const char *dev_id, int id, const char *con_id)
{
	struct clk_lookup *p;
	struct clk *clk = NULL;
	int match, best = 0;

	list_for_each_entry(p, &clocks, node) {
		match = 0;
		if (p->dev_id) {
			if (!dev_id) {
				continue;
			} else if (id < 0 && strcmp(p->dev_id, dev_id)) {
				continue;
			} else {
				int len = strlen(dev_id);

				if (strncmp(p->dev_id, dev_id, len))
					continue;

				if (simple_strtoul(p->dev_id + len + 1, NULL, 10) != id)
					continue;
			}
			match += 2;
		}
		if (p->con_id) {
			if (!con_id || strcmp(p->con_id, con_id))
				continue;
			match += 1;
		}

		if (match > best) {
			clk = p->clk;
			if (match != 3)
				best = match;
			else
				break;
		}
	}
	return clk;
}

struct clk *clk_get_sys_id(const char *dev_id, int id, const char *con_id)
{
	struct clk *clk;

	mutex_lock(&clocks_mutex);
	clk = clk_find(dev_id, id, con_id);
	if (clk && !__clk_get(clk))
		clk = NULL;
	mutex_unlock(&clocks_mutex);

	return clk ? clk : ERR_PTR(-ENOENT);
}
EXPORT_SYMBOL(clk_get_sys_id);

struct clk *clk_get_pdev(struct platform_device *pdev, const char *con_id)
{
	const char *dev_id;

	if (!pdev)
		return clk_get_sys(NULL, con_id);

	dev_id = dev_name(&pdev->dev);

	/* if the slub is not available dev_id is NULL */
	if (is_early_platform_device(pdev) && !dev_id)
		return clk_get_sys_id(pdev->name, pdev->id, NULL);

	return clk_get_sys(dev_id, con_id);
}
EXPORT_SYMBOL(clk_get_pdev);

struct clk *clk_get(struct device *dev, const char *con_id)
{
	const char *dev_id = dev ? dev_name(dev) : NULL;

	return clk_get_sys(dev_id, con_id);
}
EXPORT_SYMBOL(clk_get);

void clk_put(struct clk *clk)
{
	__clk_put(clk);
}
EXPORT_SYMBOL(clk_put);

void clkdev_add(struct clk_lookup *cl)
{
	mutex_lock(&clocks_mutex);
	list_add_tail(&cl->node, &clocks);
	mutex_unlock(&clocks_mutex);
}
EXPORT_SYMBOL(clkdev_add);

void __init clkdev_add_table(struct clk_lookup *cl, size_t num)
{
	mutex_lock(&clocks_mutex);
	while (num--) {
		list_add_tail(&cl->node, &clocks);
		cl++;
	}
	mutex_unlock(&clocks_mutex);
}

#define MAX_DEV_ID	20
#define MAX_CON_ID	16

struct clk_lookup_alloc {
	struct clk_lookup cl;
	char	dev_id[MAX_DEV_ID];
	char	con_id[MAX_CON_ID];
};

struct clk_lookup * __init_refok
clkdev_alloc(struct clk *clk, const char *con_id, const char *dev_fmt, ...)
{
	struct clk_lookup_alloc *cla;

	cla = __clkdev_alloc(sizeof(*cla));
	if (!cla)
		return NULL;

	cla->cl.clk = clk;
	if (con_id) {
		strlcpy(cla->con_id, con_id, sizeof(cla->con_id));
		cla->cl.con_id = cla->con_id;
	}

	if (dev_fmt) {
		va_list ap;

		va_start(ap, dev_fmt);
		vscnprintf(cla->dev_id, sizeof(cla->dev_id), dev_fmt, ap);
		cla->cl.dev_id = cla->dev_id;
		va_end(ap);
	}

	return &cla->cl;
}
EXPORT_SYMBOL(clkdev_alloc);

int clk_add_alias(const char *alias, const char *alias_dev_name, char *id,
	struct device *dev)
{
	struct clk *r = clk_get(dev, id);
	struct clk_lookup *l;

	if (IS_ERR(r))
		return PTR_ERR(r);

	l = clkdev_alloc(r, alias, alias_dev_name);
	clk_put(r);
	if (!l)
		return -ENODEV;
	clkdev_add(l);
	return 0;
}
EXPORT_SYMBOL(clk_add_alias);

/*
 * clkdev_drop - remove a clock dynamically allocated
 */
void clkdev_drop(struct clk_lookup *cl)
{
	mutex_lock(&clocks_mutex);
	list_del(&cl->node);
	mutex_unlock(&clocks_mutex);
	kfree(cl);
}
EXPORT_SYMBOL(clkdev_drop);
