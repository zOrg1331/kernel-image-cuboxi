/*
 *  kernel/bc/kmem.c
 *
 *  Copyright (C) 2005  SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 */

#include <linux/slab.h>
#include <linux/highmem.h>
#include <linux/vmalloc.h>
#include <linux/mm.h>
#include <linux/gfp.h>
#include <linux/swap.h>
#include <linux/spinlock.h>
#include <linux/sched.h>
#include <linux/module.h>
#include <linux/init.h>

#include <bc/beancounter.h>
#include <bc/vmpages.h>
#include <bc/kmem.h>
#include <bc/proc.h>

int __ub_kmem_charge(struct user_beancounter *ub,
		struct ub_percpu_struct *ub_pcpu,
		unsigned long size, enum ub_severity strict)
{
	unsigned long charge;
	int retval;

	if (((ub->ub_parms[UB_KMEMSIZE].held + size) >> PAGE_SHIFT) >
			ub->ub_parms[UB_PHYSPAGES].limit)
		return -ENOMEM;

	charge = (size - ub_pcpu->precharge[UB_KMEMSIZE]
			+ (ub->ub_parms[UB_KMEMSIZE].max_precharge >> 1)
			+ PAGE_SIZE - 1) & PAGE_MASK;

	spin_lock(&ub->ub_lock);

	retval = __charge_beancounter_locked(ub, UB_KMEMSIZE,
			charge, strict | UB_TEST);
	if (retval) {
		init_beancounter_precharge(ub, UB_KMEMSIZE);
		charge = (size - ub_pcpu->precharge[UB_KMEMSIZE]
				+ PAGE_SIZE - 1) & PAGE_MASK;
		retval = __charge_beancounter_locked(ub, UB_KMEMSIZE,
				charge, strict);
		if (retval)
			goto out;
	}
	ub_pcpu->precharge[UB_KMEMSIZE] += charge - size;

	__charge_beancounter_locked(ub, UB_PHYSPAGES,
			charge >> PAGE_SHIFT, UB_FORCE);

out:
	spin_unlock(&ub->ub_lock);
	return retval;
}
EXPORT_SYMBOL(__ub_kmem_charge);

void __ub_kmem_uncharge(struct user_beancounter *ub,
		struct ub_percpu_struct *ub_pcpu,
		unsigned long size)
{
	unsigned long uncharge;

	spin_lock(&ub->ub_lock);

	if (ub->ub_parms[UB_KMEMSIZE].max_precharge !=
			ub_resource_precharge[UB_KMEMSIZE])
		init_beancounter_precharge(ub, UB_KMEMSIZE);

	if (!__try_uncharge_beancounter_percpu(ub, ub_pcpu, UB_KMEMSIZE, size))
		goto out;

	uncharge = (size + ub_pcpu->precharge[UB_KMEMSIZE]
			- (ub->ub_parms[UB_KMEMSIZE].max_precharge >> 1)
		   ) & PAGE_MASK;
	ub_pcpu->precharge[UB_KMEMSIZE] += size - uncharge;
	__uncharge_beancounter_locked(ub, UB_KMEMSIZE, uncharge);
	__uncharge_beancounter_locked(ub, UB_PHYSPAGES, uncharge >> PAGE_SHIFT);

out:
	spin_unlock(&ub->ub_lock);
}
EXPORT_SYMBOL(__ub_kmem_uncharge);

int ub_slab_charge(struct kmem_cache *cachep, void *objp, gfp_t flags)
{
	unsigned int size;
	struct user_beancounter *ub;

	ub = get_beancounter(get_exec_ub());
	if (ub == NULL)
		return 0;

	size = CHARGE_SIZE(kmem_cache_objuse(cachep));
	if (ub_kmem_charge(ub, size,
				(flags & __GFP_SOFT_UBC ? UB_SOFT : UB_HARD)))
		goto out_err;

	*ub_slab_ptr(cachep, objp) = ub;
	return 0;

out_err:
	put_beancounter(ub);
	return -ENOMEM;
}

void ub_slab_uncharge(struct kmem_cache *cachep, void *objp)
{
	unsigned int size;
	struct user_beancounter **ub_ref;

	ub_ref = ub_slab_ptr(cachep, objp);
	if (*ub_ref == NULL)
		return;

	size = CHARGE_SIZE(kmem_cache_objuse(cachep));
	ub_kmem_uncharge(*ub_ref, size);
	put_beancounter(*ub_ref);
	*ub_ref = NULL;
}

/* 
 * takes init_mm.page_table_lock 
 * some outer lock to protect pages from vmalloced area must be held
 */
struct user_beancounter *vmalloc_ub(void *obj)
{
	struct page *pg;

	pg = vmalloc_to_page(obj);
	if (pg == NULL)
		return NULL;

	return page_kmem_ub(pg);
}

EXPORT_SYMBOL(vmalloc_ub);

struct user_beancounter *mem_ub(void *obj)
{
	struct user_beancounter *ub;

	if ((unsigned long)obj >= VMALLOC_START &&
	    (unsigned long)obj  < VMALLOC_END)
		ub = vmalloc_ub(obj);
	else
		ub = slab_ub(obj);

	return ub;
}

EXPORT_SYMBOL(mem_ub);
