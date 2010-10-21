/*
 *  include/ub/io_acct.h
 *
 *  Copyright (C) 2006 SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 *  Pavel Emelianov <xemul@openvz.org>
 *
 */

#ifndef __UB_IO_ACCT_H_
#define __UB_IO_ACCT_H_

#ifdef CONFIG_BC_IO_ACCOUNTING
#include <bc/beancounter.h>

/*
 * IO ub is required in task context only, so if exec_ub is set
 * to NULL this means that uses doesn't need to charge some
 * resources. nevertheless IO activity must be accounted, so we
 * account it to current's task beancounter.
 */

static inline struct user_beancounter *get_io_ub(void)
{
	struct user_beancounter *ub;

	ub = get_exec_ub();
	if (unlikely(ub == NULL))
		ub = get_task_ub(current);

	return top_beancounter(ub);
}

static inline struct user_beancounter *get_mapping_ub(struct address_space *mapping)
{
	struct user_beancounter *ub;

	if (!mapping)
		return NULL;

	rcu_read_lock();
	ub = rcu_dereference(mapping->dirtied_ub);
	if (ub)
		ub = get_beancounter_rcu(ub);
	rcu_read_unlock();

	return ub;
}

static inline void ub_io_account_read(size_t bytes)
{
	ub_percpu_add(get_io_ub(), sync_read_bytes, bytes);
}

static inline void ub_io_account_write(size_t bytes)
{
	ub_percpu_add(get_io_ub(), sync_write_bytes, bytes);
}

extern void ub_io_account_dirty(struct address_space *mapping, int pages);
extern void ub_io_account_clean(struct address_space *mapping, int pages, int cancel);

extern unsigned long ub_dirty_pages(struct user_beancounter *ub);
extern int ub_dirty_limits(long *pdirty, struct user_beancounter *ub);

#else /* UBC_IO_ACCT */

static inline void ub_io_account_read(size_t bytes)
{
}

static inline void ub_io_account_write(size_t bytes)
{
}

static inline void ub_io_account_dirty(struct address_space *mapping, int pages)
{
}

static inline void ub_io_account_clean(struct address_space *mapping, int pages, int cancel)
{
}

static inline unsigned long ub_dirty_pages(struct user_beancounter *ub)
{
	return 0;
}

static inline int ub_dirty_limits(long *pdirty, struct user_beancounter *ub)
{
	return 0;
}

#endif /* UBC_IO_ACCT */

#endif
