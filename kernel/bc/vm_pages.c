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

#include <asm/pgtable.h>
#include <asm/page.h>

#include <bc/beancounter.h>
#include <bc/vmpages.h>
#include <bc/proc.h>
#include <bc/oom_kill.h>

static inline unsigned long pages_in_pte_range(struct vm_area_struct *vma,
		pmd_t *pmd, unsigned long addr, unsigned long end,
		unsigned long *ret)
{
	pte_t *pte;
	spinlock_t *ptl;

	pte = pte_offset_map_lock(vma->vm_mm, pmd, addr, &ptl);
	do {
		if (!pte_none(*pte) && pte_present(*pte))
			(*ret)++;
	} while (pte++, addr += PAGE_SIZE, (addr != end));
	pte_unmap_unlock(pte - 1, ptl);

	return addr;
}

static inline unsigned long pages_in_pmd_range(struct vm_area_struct *vma,
		pud_t *pud, unsigned long addr, unsigned long end,
		unsigned long *ret)
{
	pmd_t *pmd;
	unsigned long next;

	pmd = pmd_offset(pud, addr);
	do {
		next = pmd_addr_end(addr, end);
		if (pmd_none_or_clear_bad(pmd))
			continue;
		next = pages_in_pte_range(vma, pmd, addr, next, ret);
	} while (pmd++, addr = next, (addr != end));

	return addr;
}

static inline unsigned long pages_in_pud_range(struct vm_area_struct *vma,
		pgd_t *pgd, unsigned long addr, unsigned long end,
		unsigned long *ret)
{
	pud_t *pud;
	unsigned long next;

	pud = pud_offset(pgd, addr);
	do {
		next = pud_addr_end(addr, end);
		if (pud_none_or_clear_bad(pud))
			continue;
		next = pages_in_pmd_range(vma, pud, addr, next, ret);
	} while (pud++, addr = next, (addr != end));

	return addr;
}

unsigned long pages_in_vma_range(struct vm_area_struct *vma,
		unsigned long addr, unsigned long end)
{
	pgd_t *pgd;
	unsigned long next;
	unsigned long ret;

	ret = 0;
	BUG_ON(addr >= end);
	pgd = pgd_offset(vma->vm_mm, addr);
	do {
		next = pgd_addr_end(addr, end);
		if (pgd_none_or_clear_bad(pgd))
			continue;
		next = pages_in_pud_range(vma, pgd, addr, next, &ret);
	} while (pgd++, addr = next, (addr != end));
	return ret;
}

void __ub_update_oomguarpages(struct user_beancounter *ub)
{
	ub->ub_parms[UB_OOMGUARPAGES].held = ub_mapped_pages(ub) +
		ub->ub_parms[UB_SWAPPAGES].held;
	ub_adjust_maxheld(ub, UB_OOMGUARPAGES);
}

void __ub_update_privvm(struct user_beancounter *ub)
{
	ub->ub_parms[UB_PRIVVMPAGES].held = ub_mapped_pages(ub) +
		+ ub->ub_unused_privvmpages
		+ ub->ub_parms[UB_SHMPAGES].held;
	ub_adjust_maxheld(ub, UB_PRIVVMPAGES);
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
	__ub_update_privvm(ub);
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

unsigned long ub_mapped_pages(struct user_beancounter *ub)
{
	struct ub_percpu_struct *ub_pcpu;
	unsigned long file = 0, anon = 0;
	int cpu;

	for_each_possible_cpu(cpu) {
		ub_pcpu = ub_percpu(ub, cpu);
		file += ub_pcpu->mapped_file_pages;
		anon += ub_pcpu->anonymous_pages;
	}

	return max_t(long, 0, file) + max_t(long, 0, anon);
}

static inline int __charge_privvm_locked(struct user_beancounter *ub, 
		unsigned long s, enum ub_severity strict)
{
	__ub_update_privvm(ub);
	if (__charge_beancounter_locked(ub, UB_PRIVVMPAGES, s, strict) < 0)
		return -ENOMEM;

	ub->ub_unused_privvmpages += s;
	return 0;
}

static void __unused_privvm_dec_locked(struct user_beancounter *ub, 
		long size)
{
	/* catch possible overflow */
	if (ub->ub_unused_privvmpages < size) {
		uncharge_warn(ub, UB_UNUSEDPRIVVM,
				size, ub->ub_unused_privvmpages);
		size = ub->ub_unused_privvmpages;
	}
	ub->ub_unused_privvmpages -= size;
}

void __ub_unused_privvm_dec(struct mm_struct *mm, long size)
{
	unsigned long flags;
	struct user_beancounter *ub;

	ub = mm->mm_ub;
	if (ub == NULL)
		return;

	ub = top_beancounter(ub);
	spin_lock_irqsave(&ub->ub_lock, flags);
	__unused_privvm_dec_locked(ub, size);
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

void ub_unused_privvm_sub(struct mm_struct *mm,
		struct vm_area_struct *vma, unsigned long count)
{
	if (VM_UB_PRIVATE(vma->vm_flags, vma->vm_file))
		__ub_unused_privvm_dec(mm, count);
}

void ub_unused_privvm_add(struct mm_struct *mm,
		struct vm_area_struct *vma, unsigned long size)
{
	unsigned long flags;
	struct user_beancounter *ub;

	ub = mm->mm_ub;
	if (ub == NULL || !VM_UB_PRIVATE(vma->vm_flags, vma->vm_file))
		return;

	ub = top_beancounter(ub);
	spin_lock_irqsave(&ub->ub_lock, flags);
	ub->ub_unused_privvmpages += size;
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

int ub_protected_charge(struct mm_struct *mm, unsigned long size,
		unsigned long newflags, struct vm_area_struct *vma)
{
	unsigned long flags;
	struct file *file;
	struct user_beancounter *ub;

	ub = mm->mm_ub;
	if (ub == NULL)
		return PRIVVM_NO_CHARGE;

	flags = vma->vm_flags;
	if (!((newflags ^ flags) & VM_WRITE))
		return PRIVVM_NO_CHARGE;

	file = vma->vm_file;
	if (!VM_UB_PRIVATE(newflags | VM_WRITE, file))
		return PRIVVM_NO_CHARGE;

	if (flags & VM_WRITE)
		return PRIVVM_TO_SHARED;

	ub = top_beancounter(ub);
	spin_lock_irqsave(&ub->ub_lock, flags);
	if (__charge_privvm_locked(ub, size, UB_SOFT) < 0)
		goto err;
	spin_unlock_irqrestore(&ub->ub_lock, flags);
	return PRIVVM_TO_PRIVATE;

err:
	spin_unlock_irqrestore(&ub->ub_lock, flags);
	return PRIVVM_ERROR;
}

int ub_memory_charge(struct mm_struct *mm, unsigned long size,
		unsigned vm_flags, struct file *vm_file, int sv)
{
	struct user_beancounter *ub, *ubl;
	unsigned long flags;

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
		ubl = top_beancounter(ub);
		spin_lock_irqsave(&ubl->ub_lock, flags);
		if (__charge_privvm_locked(ubl, size, sv))
			goto out_private;
		spin_unlock_irqrestore(&ubl->ub_lock, flags);
	}
	return 0;

out_private:
	spin_unlock_irqrestore(&ubl->ub_lock, flags);
	if (vm_flags & VM_LOCKED)
		uncharge_beancounter(ub, UB_LOCKEDPAGES, size);
out_err:
	return -ENOMEM;
}

void ub_memory_uncharge(struct mm_struct *mm, unsigned long size,
		unsigned vm_flags, struct file *vm_file)
{
	struct user_beancounter *ub;
	unsigned long flags;

	ub = mm->mm_ub;
	if (ub == NULL)
		return;

	size >>= PAGE_SHIFT;

	if (vm_flags & VM_LOCKED)
		uncharge_beancounter(ub, UB_LOCKEDPAGES, size);
	if (VM_UB_PRIVATE(vm_flags, vm_file)) {
		ub = top_beancounter(ub);
		spin_lock_irqsave(&ub->ub_lock, flags);
		__unused_privvm_dec_locked(ub, size);
		spin_unlock_irqrestore(&ub->ub_lock, flags);
	}
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
	struct user_beancounter *ub;

	for (ub = shi->shmi_ub; ub != NULL; ub = ub->parent)
		do_ub_tmpfs_respages_inc(ub);
}

static inline void do_ub_tmpfs_respages_sub(struct user_beancounter *ub,
		unsigned long size)
{
	unsigned long flags;

	spin_lock_irqsave(&ub->ub_lock, flags);
	/* catch possible overflow */
	if (ub->ub_tmpfs_respages < size) {
		uncharge_warn(ub, UB_TMPFSPAGES,
				size, ub->ub_tmpfs_respages);
		size = ub->ub_tmpfs_respages;
	}
	ub->ub_tmpfs_respages -= size;
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

void ub_tmpfs_respages_sub(struct shmem_inode_info *shi,
		unsigned long size)
{
	struct user_beancounter *ub;

	for (ub = shi->shmi_ub; ub != NULL; ub = ub->parent)
		do_ub_tmpfs_respages_sub(ub, size);
}

int ub_shmpages_charge(struct shmem_inode_info *shi, unsigned long size)
{
	int ret;
	unsigned long flags;
	struct user_beancounter *ub;

	ub = shi->shmi_ub;
	if (ub == NULL)
		return 0;

	ub = top_beancounter(ub);
	spin_lock_irqsave(&ub->ub_lock, flags);
	ret = __charge_beancounter_locked(ub, UB_SHMPAGES, size, UB_HARD);
	spin_unlock_irqrestore(&ub->ub_lock, flags);
	return ret;
}

void ub_shmpages_uncharge(struct shmem_inode_info *shi, unsigned long size)
{
	unsigned long flags;
	struct user_beancounter *ub;

	ub = shi->shmi_ub;
	if (ub == NULL)
		return;

	ub = top_beancounter(ub);
	spin_lock_irqsave(&ub->ub_lock, flags);
	__uncharge_beancounter_locked(ub, UB_SHMPAGES, size);
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

int ub_check_ram_limits(struct user_beancounter *ub, gfp_t gfp_mask)
{
	if (get_exec_ub() != ub)
		return 0;

	if (ub->ub_parms[UB_PHYSPAGES].limit == UB_MAXVALUE)
		return 0;

	while (precharge_beancounter(ub, UB_PHYSPAGES, 1)) {
		unsigned long progress, flags;
		int no_swap_left = !ub_resource_excess(ub, UB_SWAPPAGES, UB_SOFT);

		if (test_thread_flag(TIF_MEMDIE))
			return -ENOMEM;

		ub_oom_start();

		progress = try_to_free_gang_pages(&ub->gang_set, no_swap_left, gfp_mask);
		/* FIXME account there progress into throttler */
		if (progress)
			continue;

		spin_lock_irqsave(&ub->ub_lock, flags);
		ub->ub_parms[UB_PHYSPAGES].failcnt++;
		if (no_swap_left)
			ub->ub_parms[UB_SWAPPAGES].failcnt++;
		spin_unlock_irqrestore(&ub->ub_lock, flags);

		if (nr_swap_pages <= 0 && !no_swap_left &&
				ub_ratelimit(&ub->ub_limit_rl)) {
			printk(KERN_INFO "Fatal resource shortage: %s, UB %d."
					" More physical swap space required.\n",
					ub_rnames[UB_SWAPPAGES], ub->ub_uid);
		}

		if (gfp_mask & __GFP_WAIT)
			out_of_memory_in_ub(ub, gfp_mask);
		else
			return -ENOMEM;
	}

	return 0;
}
EXPORT_SYMBOL(ub_check_ram_limits);

#ifdef CONFIG_BC_SWAP_ACCOUNTING
static inline void do_ub_swapentry_inc(struct user_beancounter *ub)
{
	unsigned long flags;

	spin_lock_irqsave(&ub->ub_lock, flags);
	__charge_beancounter_locked(ub, UB_SWAPPAGES, 1, UB_FORCE);
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

void ub_swapentry_inc(struct swap_info_struct *si, pgoff_t num,
		struct user_beancounter *ub)
{
	si->swap_ubs[num] = get_beancounter(ub);
	for (; ub != NULL; ub = ub->parent)
		do_ub_swapentry_inc(ub);
}
EXPORT_SYMBOL(ub_swapentry_inc);

static inline void do_ub_swapentry_dec(struct user_beancounter *ub)
{
	unsigned long flags;

	spin_lock_irqsave(&ub->ub_lock, flags);
	__uncharge_beancounter_locked(ub, UB_SWAPPAGES, 1);
	spin_unlock_irqrestore(&ub->ub_lock, flags);
}

void ub_swapentry_dec(struct swap_info_struct *si, pgoff_t num)
{
	struct user_beancounter *ub, *ubp;

	ub = si->swap_ubs[num];
	si->swap_ubs[num] = NULL;
	for (ubp = ub; ubp != NULL; ubp = ubp->parent)
		do_ub_swapentry_dec(ubp);
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

static int vmguar_enough_memory(struct vnotifier_block *self,
		unsigned long event, void *arg, int old_ret)
{
	struct user_beancounter *ub;
	unsigned long flags;

	if (event != VIRTINFO_ENOUGHMEM)
		return old_ret;
	/*
	 * If it's a kernel thread, don't care about it.
	 * Added in order aufsd to run smoothly over ramfs.
	 */
	if (!current->mm)
		return NOTIFY_DONE;

	ub = top_beancounter(current->mm->mm_ub);
	spin_lock_irqsave(&ub->ub_lock, flags);
	__ub_update_privvm(ub);
	if (ub->ub_parms[UB_PRIVVMPAGES].held <=
			ub->ub_parms[UB_VMGUARPAGES].barrier)
		old_ret = NOTIFY_OK;
	spin_unlock_irqrestore(&ub->ub_lock, flags);

	return old_ret;
}

static struct vnotifier_block vmguar_notifier_block = {
	.notifier_call = vmguar_enough_memory
};

static int __init init_vmguar_notifier(void)
{
	virtinfo_notifier_register(VITYPE_GENERAL, &vmguar_notifier_block);
	return 0;
}

static void __exit fini_vmguar_notifier(void)
{
	virtinfo_notifier_unregister(VITYPE_GENERAL, &vmguar_notifier_block);
}

module_init(init_vmguar_notifier);
module_exit(fini_vmguar_notifier);

#ifdef CONFIG_PROC_FS
static int bc_vmaux_show(struct seq_file *f, void *v)
{
	struct user_beancounter *ub;
	struct ub_percpu_struct *ub_pcpu;
	unsigned long swap, unmap;
	unsigned long mapped_file_pages, anonymous_pages;
	int i;

	ub = seq_beancounter(f);

	swap = unmap = 0;
	mapped_file_pages = anonymous_pages = 0;
	for_each_possible_cpu(i) {
		ub_pcpu = ub_percpu(ub, i);
		swap += ub_pcpu->swapin;
		unmap += ub_pcpu->unmap;
		mapped_file_pages += ub_pcpu->mapped_file_pages;
		anonymous_pages += ub_pcpu->anonymous_pages;
	}

	mapped_file_pages = max_t(long, 0, mapped_file_pages);
	anonymous_pages = max_t(long, 0, anonymous_pages);

	seq_printf(f, bc_proc_lu_fmt, ub_rnames[UB_UNUSEDPRIVVM],
			ub->ub_unused_privvmpages);
	seq_printf(f, bc_proc_lu_fmt, ub_rnames[UB_TMPFSPAGES],
			ub->ub_tmpfs_respages);

	seq_printf(f, bc_proc_lu_fmt, "swapin", swap);
	seq_printf(f, bc_proc_lu_fmt, "unmap", unmap);

	seq_printf(f, bc_proc_lu_fmt, ub_rnames[UB_MAPPED_FILE],
			mapped_file_pages);
	seq_printf(f, bc_proc_lu_fmt, ub_rnames[UB_ANONYMOUS],
			anonymous_pages);
	seq_printf(f, bc_proc_lu_fmt, "rss",
			mapped_file_pages + anonymous_pages);
	seq_printf(f, bc_proc_lu_fmt, "ram", ub_physical_pages(ub));

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
