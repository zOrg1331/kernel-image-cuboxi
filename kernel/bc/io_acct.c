/*
 *  kernel/ub/io_acct.c
 *
 *  Copyright (C) 2006  SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 *  Pavel Emelianov <xemul@openvz.org>
 *
 */

#include <linux/mm.h>
#include <linux/mempool.h>
#include <linux/proc_fs.h>
#include <linux/virtinfo.h>
#include <linux/pagemap.h>
#include <linux/module.h>
#include <linux/writeback.h>

#include <bc/beancounter.h>
#include <bc/io_acct.h>
#include <bc/proc.h>
#include <bc/vmpages.h>

/* under write lock mapping->tree_lock */

void ub_io_account_dirty(struct address_space *mapping, int pages)
{
	struct user_beancounter *ub = mapping->dirtied_ub;

	WARN_ON_ONCE(!radix_tree_tagged(&mapping->page_tree,
				PAGECACHE_TAG_DIRTY));

	if (!ub)
		ub = mapping->dirtied_ub = get_beancounter(get_io_ub());

	ub_percpu_add(ub, dirty_pages, pages);
}

void ub_io_account_clean(struct address_space *mapping, int pages, int cancel)
{
	struct user_beancounter *ub = mapping->dirtied_ub;

	if (unlikely(!ub)) {
		WARN_ON_ONCE(1);
		return;
	}

	ub_percpu_sub(ub, dirty_pages, pages);

	if (cancel)
		ub_percpu_add(ub, async_write_canceled, pages);
	else
		ub_percpu_add(ub, async_write_complete, pages);

	if (!radix_tree_tagged(&mapping->page_tree, PAGECACHE_TAG_DIRTY)) {
		mapping->dirtied_ub = NULL;
		__put_beancounter(ub);
	}
}

unsigned long ub_dirty_pages(struct user_beancounter *ub)
{
	unsigned long dirty_pages = 0;
	int cpu;

	for_each_online_cpu(cpu)
		dirty_pages += per_cpu_ptr(ub->ub_percpu, cpu)->dirty_pages;

	if ((long)dirty_pages < 0)
		dirty_pages = 0;

	return dirty_pages;
}
EXPORT_SYMBOL(ub_dirty_pages);

int ub_dirty_limits(long *pdirty, struct user_beancounter *ub)
{
	int dirty_ratio, unmapped_ratio;
	unsigned long available_memory;

	available_memory = ub->ub_parms[UB_PHYSPAGES].limit;
	if (available_memory == UB_MAXVALUE)
		return 0;

	/* math taken from get_dirty_limits */
	unmapped_ratio = 100 - (100 * ub_mapped_pages(ub)) / available_memory;

	dirty_ratio = vm_dirty_ratio;
	if ((dirty_ratio > unmapped_ratio / 2) && (dirty_ratio != 100))
		dirty_ratio = unmapped_ratio / 2;

	if (dirty_ratio < 5)
		dirty_ratio = 5;

	*pdirty = (dirty_ratio * available_memory) / 100;

	return 1;
}

#ifdef CONFIG_PROC_FS
#define in_flight(var)	(var > var##_done ? var - var##_done : 0)

static int bc_ioacct_show(struct seq_file *f, void *v)
{
	int i;
	unsigned long long read, write, cancel;
	unsigned long sync, sync_done;
	unsigned long fsync, fsync_done;
	unsigned long fdsync, fdsync_done;
	unsigned long frsync, frsync_done;
	unsigned long reads, writes;
	unsigned long long rchar, wchar;
	struct user_beancounter *ub;
	unsigned long dirty_pages = 0;
	unsigned long long dirtied;

	ub = seq_beancounter(f);

	read = write = cancel = 0;
	sync = sync_done = fsync = fsync_done =
		fdsync = fdsync_done = frsync = frsync_done = 0;
	reads = writes = 0;
	rchar = wchar = 0;
	for_each_online_cpu(i) {
		struct ub_percpu_struct *ub_percpu;
		ub_percpu = per_cpu_ptr(ub->ub_percpu, i);

		read += ub_percpu->sync_read_bytes;
		write += ub_percpu->sync_write_bytes;

		dirty_pages += ub_percpu->dirty_pages;
		write += (u64)ub_percpu->async_write_complete << PAGE_SHIFT;
		cancel += (u64)ub_percpu->async_write_canceled << PAGE_SHIFT;

		sync += ub_percpu->sync;
		fsync += ub_percpu->fsync;
		fdsync += ub_percpu->fdsync;
		frsync += ub_percpu->frsync;
		sync_done += ub_percpu->sync_done;
		fsync_done += ub_percpu->fsync_done;
		fdsync_done += ub_percpu->fdsync_done;
		frsync_done += ub_percpu->frsync_done;

		reads += ub_percpu->read;
		writes += ub_percpu->write;
		rchar += ub_percpu->rchar;
		wchar += ub_percpu->wchar;
	}

	if ((long)dirty_pages < 0)
		dirty_pages = 0;

	dirtied = write + cancel;
	dirtied += (u64)dirty_pages << PAGE_SHIFT;

	seq_printf(f, bc_proc_llu_fmt, "read", read);
	seq_printf(f, bc_proc_llu_fmt, "write", write);
	seq_printf(f, bc_proc_llu_fmt, "dirty", dirtied);
	seq_printf(f, bc_proc_llu_fmt, "cancel", cancel);
	seq_printf(f, bc_proc_llu_fmt, "missed", 0ull);

	seq_printf(f, bc_proc_lu_lfmt, "syncs_total", sync);
	seq_printf(f, bc_proc_lu_lfmt, "fsyncs_total", fsync);
	seq_printf(f, bc_proc_lu_lfmt, "fdatasyncs_total", fdsync);
	seq_printf(f, bc_proc_lu_lfmt, "range_syncs_total", frsync);

	seq_printf(f, bc_proc_lu_lfmt, "syncs_active", in_flight(sync));
	seq_printf(f, bc_proc_lu_lfmt, "fsyncs_active", in_flight(fsync));
	seq_printf(f, bc_proc_lu_lfmt, "fdatasyncs_active", in_flight(fsync));
	seq_printf(f, bc_proc_lu_lfmt, "range_syncs_active", in_flight(frsync));

	seq_printf(f, bc_proc_lu_lfmt, "vfs_reads", reads);
	seq_printf(f, bc_proc_llu_fmt, "vfs_read_chars", rchar);
	seq_printf(f, bc_proc_lu_lfmt, "vfs_writes", writes);
	seq_printf(f, bc_proc_llu_fmt, "vfs_write_chars", wchar);

	seq_printf(f, bc_proc_lu_lfmt, "io_pbs", dirty_pages);
	return 0;
}

static struct bc_proc_entry bc_ioacct_entry = {
	.name = "ioacct",
	.u.show = bc_ioacct_show,
};

static int bc_ioacct_notify(struct vnotifier_block *self,
		unsigned long event, void *arg, int old_ret)
{
	struct user_beancounter *ub;
	struct ub_percpu_struct *ub_pcpu;
	unsigned long *vm_events;
	unsigned long long bin, bout;
	int i;

	if (event != VIRTINFO_VMSTAT)
		return old_ret;

	ub = top_beancounter(get_exec_ub());
	if (ub == get_ub0())
		return old_ret;

	/* Think over: do we need to account here bytes_dirty_missed? */
	bout = 0;
	bin = 0;
	for_each_online_cpu(i) {
		ub_pcpu = per_cpu_ptr(ub->ub_percpu, i);
		bout += (u64)ub_pcpu->async_write_complete << PAGE_SHIFT;
		bout += ub_pcpu->sync_write_bytes;
		bin += ub_pcpu->sync_read_bytes;
	}

	/* convert to Kbytes */
	bout >>= 10;
	bin >>= 10;

	vm_events = ((unsigned long *)arg) + NR_VM_ZONE_STAT_ITEMS;
	vm_events[PGPGOUT] = (unsigned long)bout;
	vm_events[PGPGIN] = (unsigned long)bin;
	return NOTIFY_OK;
}

static struct vnotifier_block bc_ioacct_nb = {
	.notifier_call = bc_ioacct_notify,
};

static int __init bc_ioacct_init(void)
{
	bc_register_proc_entry(&bc_ioacct_entry);

	virtinfo_notifier_register(VITYPE_GENERAL, &bc_ioacct_nb);
	return 0;
}

late_initcall(bc_ioacct_init);
#endif
