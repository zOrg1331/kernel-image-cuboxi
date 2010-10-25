/*
 * Simple lock-less NULL terminated single list implementation
 *
 * Copyright 2010 Intel Corp.
 *   Author: Huang Ying <ying.huang@intel.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version
 * 2 as published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/llist.h>
#include <linux/errno.h>

#include <asm/system.h>

/**
 * llist_add - add a new entry
 * @new:	new entry to be added
 * @head:	the head for your lock-less list
 */
void llist_add(struct llist_head *new, struct llist_head *head)
{
	struct llist_head *entry;

	do {
		entry = head->next;
		new->next = entry;
	} while (cmpxchg(&head->next, entry, new) != entry);
}
EXPORT_SYMBOL_GPL(llist_add);

/**
 * llist_del_first - delete the first entry of lock-less list
 * @head:	the head for your lock-less list
 *
 * If list is empty, return NULL, otherwise, return the first entry deleted
 */
struct llist_head *llist_del_first(struct llist_head *head)
{
	struct llist_head *entry;

	do {
		entry = head->next;
		if (entry == NULL)
			return NULL;
	} while (cmpxchg(&head->next, entry, entry->next) != entry);

	return entry;
}
EXPORT_SYMBOL_GPL(llist_del_first);

/**
 * llist_move_all - delete all entries from one list and add them to another list
 * @list:	the head of lock-less list to delete all entries
 * @head:	the head of lock-less list to add the entries
 *
 * Remove all entries from @list lock-lessly, then add the entries to
 * lock-less list @head.
 */
void llist_move_all(struct llist_head *list, struct llist_head *head)
{
	struct llist_head *entry;

	entry = xchg(&list->next, NULL);
	head->next = entry;
}
EXPORT_SYMBOL_GPL(llist_move_all);
