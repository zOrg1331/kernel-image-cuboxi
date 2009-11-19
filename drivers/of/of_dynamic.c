/*
 * Procedures for creating, accessing and interpreting the device tree.
 *
 * Paul Mackerras	August 1996.
 * Copyright (C) 1996-2005 Paul Mackerras.
 *
 *  Adapted for 64bit PowerPC by Dave Engebretsen and Peter Bergner.
 *    {engebret|bergner}@us.ibm.com
 *
 *      This program is free software; you can redistribute it and/or
 *      modify it under the terms of the GNU General Public License
 *      as published by the Free Software Foundation; either version
 *      2 of the License, or (at your option) any later version.
 */

#include <linux/of.h>

/* temporary while merging */
extern struct device_node *allnodes;
extern rwlock_t devtree_lock;

/*
 * Plug a device node into the tree and global list.
 */
void of_attach_node(struct device_node *np)
{
	unsigned long flags;

	write_lock_irqsave(&devtree_lock, flags);
	np->sibling = np->parent->child;
	np->allnext = allnodes;
	np->parent->child = np;
	allnodes = np;
	write_unlock_irqrestore(&devtree_lock, flags);
}

