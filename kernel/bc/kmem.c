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
#include <bc/kmem.h>
#include <bc/proc.h>

/*
 * Initialization
 */

/* called with IRQ disabled */
int ub_slab_charge(struct kmem_cache *cachep, void *objp, gfp_t flags)
{
	unsigned int size;
	struct user_beancounter *ub;

	ub = get_beancounter(get_exec_ub());
	if (ub == NULL)
		return 0;

	size = CHARGE_SIZE(kmem_cache_objuse(cachep));
	if (charge_beancounter_fast(ub, UB_KMEMSIZE, size,
				(flags & __GFP_SOFT_UBC ? UB_SOFT : UB_HARD)))
		goto out_err;

	*ub_slab_ptr(cachep, objp) = ub;
	return 0;

out_err:
	put_beancounter(ub);
	return -ENOMEM;
}

/* called with IRQ disabled */
void ub_slab_uncharge(struct kmem_cache *cachep, void *objp)
{
	unsigned int size;
	struct user_beancounter **ub_ref;

	ub_ref = ub_slab_ptr(cachep, objp);
	if (*ub_ref == NULL)
		return;

	size = CHARGE_SIZE(kmem_cache_objuse(cachep));
	uncharge_beancounter_fast(*ub_ref, UB_KMEMSIZE, size);
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
