/*
 *  kernel/bc/vm_pages.c
 *
 *  Copyright (C) 2005  SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 */

#include <linux/mm.h>
#include <linux/highmem.h>
#include <linux/virtinfo.h>
#include <linux/module.h>
#include <linux/shmem_fs.h>
#include <linux/vmalloc.h>
#include <linux/init.h>
#include <linux/mmgang.h>

#include <asm/pgtable.h>
#include <asm/page.h>

#include <bc/beancounter.h>
#include <bc/vmpages.h>
#include <bc/proc.h>
#include <bc/oom_kill.h>

void __ub_update_oomguarpages(struct user_beancounter *ub)
{
	ub->ub_parms[UB_OOMGUARPAGES].held = ub_mapped_pages(ub) +
		ub->ub_parms[UB_SWAPPAGES].held;
	ub_adjust_maxheld(ub, UB_OOMGUARPAGES);
}

long ub_oomguarpages_left(struct user_beancounter *ub)
{
	unsigned long flags;
	long left;

	spin_lock_irqsave(&ub->ub_lock, flags);
	__ub_update_oomguarpages(ub);
	left = ub->ub_parms[UB_OOMGUARPAGES].barrier -
		ub->ub_parms[UB_OOMGUARPAGES].held;
	spin_unlock_irqrestore(&ub->ub_lock, flags);

	return left;
}

void ub_update_resources_locked(struct user_beancounter *ub)
{
	__ub_update_oomguarpages(ub);
}
EXPORT_SYMBOL(ub_update_resources_locked);

void ub_update_resources(struct user_beancounter *ub)
{
	unsigned long flags;

	spin_lock_irqsave(&ub->ub_lock, flags);
	ub_update_resources_locked(ub);
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}
EXPORT_SYMBOL(ub_update_resources);

int ub_memory_charge(struct mm_struct *mm, unsigned long size,
		unsigned vm_flags, struct file *vm_file, int sv)
{
	struct user_beancounter *ub;

	ub = mm->mm_ub;
	if (ub == NULL)
		return 0;

	size >>= PAGE_SHIFT;
	if (size > UB_MAXVALUE)
		return -EINVAL;

	BUG_ON(sv != UB_SOFT && sv != UB_HARD);

	if (vm_flags & VM_LOCKED) {
		if (charge_beancounter(ub, UB_LOCKEDPAGES, size, sv))
			goto out_err;
	}
	if (VM_UB_PRIVATE(vm_flags, vm_file)) {
               if (charge_beancounter_fast(ub, UB_PRIVVMPAGES, size, sv))
			goto out_private;
	}
	return 0;

out_private:
	if (vm_flags & VM_LOCKED)
		uncharge_beancounter(ub, UB_LOCKEDPAGES, size);
out_err:
	return -ENOMEM;
}

void ub_memory_uncharge(struct mm_struct *mm, unsigned long size,
		unsigned vm_flags, struct file *vm_file)
{
	struct user_beancounter *ub;

	ub = mm->mm_ub;
	if (ub == NULL)
		return;

	size >>= PAGE_SHIFT;

	if (vm_flags & VM_LOCKED)
		uncharge_beancounter(ub, UB_LOCKEDPAGES, size);
       if (VM_UB_PRIVATE(vm_flags, vm_file))
               uncharge_beancounter_fast(ub, UB_PRIVVMPAGES, size);
}

int ub_locked_charge(struct mm_struct *mm, unsigned long size)
{
	struct user_beancounter *ub;

	ub = mm->mm_ub;
	if (ub == NULL)
		return 0;

	return charge_beancounter(ub, UB_LOCKEDPAGES,
			size >> PAGE_SHIFT, UB_HARD);
}

void ub_locked_uncharge(struct mm_struct *mm, unsigned long size)
{
	struct user_beancounter *ub;

	ub = mm->mm_ub;
	if (ub == NULL)
		return;

	uncharge_beancounter(ub, UB_LOCKEDPAGES, size >> PAGE_SHIFT);
}

int ub_lockedshm_charge(struct shmem_inode_info *shi, unsigned long size)
{
	struct user_beancounter *ub;

	ub = shi->shmi_ub;
	if (ub == NULL)
		return 0;

	return charge_beancounter(ub, UB_LOCKEDPAGES,
			size >> PAGE_SHIFT, UB_HARD);
}

void ub_lockedshm_uncharge(struct shmem_inode_info *shi, unsigned long size)
{
	struct user_beancounter *ub;

	ub = shi->shmi_ub;
	if (ub == NULL)
		return;

	uncharge_beancounter(ub, UB_LOCKEDPAGES, size >> PAGE_SHIFT);
}


static inline void do_ub_tmpfs_respages_inc(struct user_beancounter *ub)
{
	unsigned long flags;

	spin_lock_irqsave(&ub->ub_lock, flags);
	ub->ub_tmpfs_respages++;
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

void ub_tmpfs_respages_inc(struct shmem_inode_info *shi)
{
	if (shi->shmi_ub)
		do_ub_tmpfs_respages_inc(shi->shmi_ub);
}

static inline void do_ub_tmpfs_respages_sub(struct user_beancounter *ub,
		unsigned long size)
{
	unsigned long flags;

	spin_lock_irqsave(&ub->ub_lock, flags);
	/* catch possible overflow */
	if (ub->ub_tmpfs_respages < size) {
		uncharge_warn(ub, "tmpfs_respages",
				size, ub->ub_tmpfs_respages);
		size = ub->ub_tmpfs_respages;
	}
	ub->ub_tmpfs_respages -= size;
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

void ub_tmpfs_respages_sub(struct shmem_inode_info *shi,
		unsigned long size)
{
	if (shi->shmi_ub)
		do_ub_tmpfs_respages_sub(shi->shmi_ub, size);
}

int ub_shmpages_charge(struct shmem_inode_info *shi, unsigned long size)
{
       struct user_beancounter *ub = shi->shmi_ub;
	int ret;

       ret = charge_beancounter(ub, UB_SHMPAGES, size, UB_HARD);
       if (ret)
               goto no_shm;

       ret = charge_beancounter_fast(ub, UB_PRIVVMPAGES, size, UB_HARD);
       if (ret)
               goto no_privvm;

       return 0;

no_privvm:
       uncharge_beancounter(ub, UB_SHMPAGES, size);
no_shm:
	return ret;
}

void ub_shmpages_uncharge(struct shmem_inode_info *shi, unsigned long size)
{
       struct user_beancounter *ub = shi->shmi_ub;

       uncharge_beancounter_fast(ub, UB_PRIVVMPAGES, size);
       uncharge_beancounter(ub, UB_SHMPAGES, size);
}

int __ub_check_ram_limits(struct user_beancounter *ub, gfp_t gfp_mask)
{
	int ret;
	if (get_exec_ub() != ub)
		return 0;

	ub_oom_start(&ub->oom_ctrl);

	do {
		unsigned long progress, flags;
		int no_swap_left = 0;

		if (test_thread_flag(TIF_MEMDIE))
			return -ENOMEM;

		progress = try_to_free_gang_pages(&ub->gang_set, gfp_mask);
		/* FIXME account there progress into throttler */
		if (progress)
			continue;

		spin_lock_irqsave(&ub->ub_lock, flags);
		ub->ub_parms[UB_PHYSPAGES].failcnt++;
		if (!ub_resource_excess(ub, UB_SWAPPAGES, UB_SOFT)) {
			ub->ub_parms[UB_SWAPPAGES].failcnt++;
			no_swap_left = 1;
		}
		spin_unlock_irqrestore(&ub->ub_lock, flags);

		if (nr_swap_pages <= 0 && !no_swap_left &&
				__ratelimit(&ub->ub_ratelimit)) {
			printk(KERN_INFO "Fatal resource shortage: %s, UB %d."
					" More physical swap space required.\n",
					ub_rnames[UB_SWAPPAGES], ub->ub_uid);
		}

		if (gfp_mask & __GFP_WAIT) {
			ret = out_of_memory_in_ub(ub, gfp_mask);
			if (ret == -EAGAIN)
				/*
				 * We raced with some other OOM killer and nned
				 * to ypdate generation to be sure, that we can
				 * call OOM killer on next loop iteration.
				 */
				ub_oom_start(&ub->oom_ctrl);
			else if (ret == -ENOMEM)
				return -ENOMEM;
		} else
			return -ENOMEM;
	} while (precharge_beancounter(ub, UB_PHYSPAGES, 1));

	return 0;
}
EXPORT_SYMBOL(__ub_check_ram_limits);

#ifdef CONFIG_BC_SWAP_ACCOUNTING
void ub_swapentry_inc(struct swap_info_struct *si, pgoff_t num,
		struct user_beancounter *ub)
{
	si->swap_ubs[num] = get_beancounter(ub);
	charge_beancounter_fast(ub, UB_SWAPPAGES, 1, UB_FORCE);
}
EXPORT_SYMBOL(ub_swapentry_inc);

void ub_swapentry_dec(struct swap_info_struct *si, pgoff_t num)
{
	struct user_beancounter *ub;

	ub = si->swap_ubs[num];
	si->swap_ubs[num] = NULL;
	uncharge_beancounter_fast(ub, UB_SWAPPAGES, 1);
	put_beancounter(ub);
}
EXPORT_SYMBOL(ub_swapentry_dec);

int ub_swap_init(struct swap_info_struct *si, pgoff_t num)
{
	struct user_beancounter **ubs;

	ubs = vmalloc(num * sizeof(struct user_beancounter *));
	if (ubs == NULL)
		return -ENOMEM;

	memset(ubs, 0, num * sizeof(struct user_beancounter *));
	si->swap_ubs = ubs;
	return 0;
}

void ub_swap_fini(struct swap_info_struct *si)
{
	if (si->swap_ubs) {
		vfree(si->swap_ubs);
		si->swap_ubs = NULL;
	}
}
#endif

static int bc_fill_sysinfo(struct user_beancounter *ub, struct sysinfo *si, int old_ret)
{
	unsigned long used, total;

	if (ub->ub_parms[UB_PHYSPAGES].limit == UB_MAXVALUE ||
	    ub->ub_parms[UB_SWAPPAGES].limit == UB_MAXVALUE)
		return old_ret;

	memset(si, 0, sizeof(*si));

	total = ub->ub_parms[UB_PHYSPAGES].limit;
	used = ub->ub_parms[UB_PHYSPAGES].held;

	si->totalram = total;
	si->freeram = (total >= used ? total - used : 0);

	total = ub->ub_parms[UB_SWAPPAGES].limit;
	used = ub->ub_parms[UB_SWAPPAGES].held;

	si->totalswap = total;
	si->freeswap = (total > used ? total - used : 0);

	si->mem_unit = PAGE_SIZE;

	return NOTIFY_OK | NOTIFY_STOP_MASK;
}

static int bc_fill_meminfo(struct user_beancounter *ub, struct meminfo *mi, int old_ret)
{
	int cpu, ret;
	long dcache, kmem;

	ret = bc_fill_sysinfo(ub, mi->si, old_ret);
	if (!(ret & NOTIFY_STOP_MASK))
		goto out;

	gang_page_stat(&ub->gang_set, mi->pages);

	mi->cached = min(mi->si->totalram - mi->si->freeram,
			mi->pages[LRU_INACTIVE_FILE] +
			mi->pages[LRU_ACTIVE_FILE]);
	mi->locked = ub->ub_parms[UB_LOCKEDPAGES].held;
	mi->shmem = ub->ub_parms[UB_SHMPAGES].held;
	dcache = ub->ub_parms[UB_DCACHESIZE].held;
	kmem = ub->ub_parms[UB_KMEMSIZE].held;

	mi->file_mapped = __ub_stat_get(ub, mapped_file_pages);
	mi->anon_mapped = __ub_stat_get(ub, anonymous_pages);
	mi->dirty_pages = __ub_stat_get(ub, dirty_pages);
	for_each_possible_cpu(cpu) {
		struct ub_percpu_struct *pcpu = ub_percpu(ub, cpu);

		mi->anon_mapped += pcpu->anonymous_pages;
		mi->file_mapped += pcpu->mapped_file_pages;
		mi->dirty_pages	+= pcpu->dirty_pages;
		dcache		-= pcpu->precharge[UB_DCACHESIZE];
		kmem		-= pcpu->precharge[UB_KMEMSIZE];
	}

	mi->anon_mapped = max_t(long, 0, mi->anon_mapped);
	mi->file_mapped = max_t(long, 0, mi->file_mapped);
	mi->dirty_pages = max_t(long, 0, mi->dirty_pages);

	mi->slab_reclaimable = DIV_ROUND_UP(max(0L, dcache), PAGE_SIZE);
	mi->slab_unreclaimable =
		DIV_ROUND_UP(max(0L, kmem - dcache), PAGE_SIZE);
out:
	return ret;
}

static int bc_mem_notify(struct vnotifier_block *self,
		unsigned long event, void *arg, int old_ret)
{
	switch (event) {
	case VIRTINFO_MEMINFO: {
		struct meminfo *mi = arg;
		return bc_fill_meminfo(mi->ub, mi, old_ret);
	}
	case VIRTINFO_SYSINFO:
		return bc_fill_sysinfo(get_exec_ub(), arg, old_ret);
	};

	return old_ret;
}

static struct vnotifier_block bc_mem_notifier_block = {
	.notifier_call = bc_mem_notify,
	.priority = INT_MAX,
};

static int __init init_vmguar_notifier(void)
{
	virtinfo_notifier_register(VITYPE_GENERAL, &bc_mem_notifier_block);
	return 0;
}

static void __exit fini_vmguar_notifier(void)
{
	virtinfo_notifier_unregister(VITYPE_GENERAL, &bc_mem_notifier_block);
}

module_init(init_vmguar_notifier);
module_exit(fini_vmguar_notifier);

#ifdef CONFIG_PROC_FS
static int bc_vmaux_show(struct seq_file *f, void *v)
{
	struct user_beancounter *ub;
	struct ub_percpu_struct *ub_pcpu;
	unsigned long swap, unmap, phys_pages;
	unsigned long mapped_file_pages, anonymous_pages;
	int i;

	ub = seq_beancounter(f);

	swap = unmap = 0;
	mapped_file_pages = __ub_stat_get(ub, mapped_file_pages);
	anonymous_pages = __ub_stat_get(ub, anonymous_pages);
	phys_pages = ub->ub_parms[UB_PHYSPAGES].held;
	for_each_possible_cpu(i) {
		ub_pcpu = ub_percpu(ub, i);
		swap += ub_pcpu->swapin;
		unmap += ub_pcpu->unmap;
		phys_pages -= ub_pcpu->precharge[UB_PHYSPAGES];
		mapped_file_pages += ub_pcpu->mapped_file_pages;
		anonymous_pages += ub_pcpu->anonymous_pages;
	}

	phys_pages = max_t(long, 0, phys_pages);
	mapped_file_pages = max_t(long, 0, mapped_file_pages);
	anonymous_pages = max_t(long, 0, anonymous_pages);

	seq_printf(f, bc_proc_lu_fmt, "tmpfs_respages",
			ub->ub_tmpfs_respages);

	seq_printf(f, bc_proc_lu_fmt, "swapin", swap);
	seq_printf(f, bc_proc_lu_fmt, "unmap", unmap);

	seq_printf(f, bc_proc_lu_fmt, "mapped_file",
			mapped_file_pages);
	seq_printf(f, bc_proc_lu_fmt, "anonymous",
			anonymous_pages);
	seq_printf(f, bc_proc_lu_fmt, "rss",
			mapped_file_pages + anonymous_pages);
	seq_printf(f, bc_proc_lu_fmt, "ram", phys_pages);

	return 0;
}
static struct bc_proc_entry bc_vmaux_entry = {
	.name = "vmaux",
	.u.show = bc_vmaux_show,
};

static int __init bc_vmaux_init(void)
{
	bc_register_proc_entry(&bc_vmaux_entry);
	return 0;
}

late_initcall(bc_vmaux_init);
#endif
