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

/*
 * Slab accounting
 */

#ifdef CONFIG_BC_DEBUG_KMEM

#define CC_HASH_SIZE	1024
static struct ub_cache_counter *cc_hash[CC_HASH_SIZE];
spinlock_t cc_lock;

static void __free_cache_counters(struct user_beancounter *ub,
		struct kmem_cache *cachep)
{
	struct ub_cache_counter *cc, **pprev, *del;
	int i;
	unsigned long flags;

	del = NULL;
	spin_lock_irqsave(&cc_lock, flags);
	for (i = 0; i < CC_HASH_SIZE; i++) {
		pprev = &cc_hash[i];
		cc = cc_hash[i];
		while (cc != NULL) {
			if (cc->ub != ub && cc->cachep != cachep) {
				pprev = &cc->next;
				cc = cc->next;
				continue;
			}

			list_del(&cc->ulist);
			*pprev = cc->next;
			cc->next = del;
			del = cc;
			cc = *pprev;
		}
	}
	spin_unlock_irqrestore(&cc_lock, flags);

	while (del != NULL) {
		cc = del->next;
		kfree(del);
		del = cc;
	}
}

void ub_free_counters(struct user_beancounter *ub)
{
	__free_cache_counters(ub, NULL);
}

void ub_kmemcache_free(struct kmem_cache *cachep)
{
	__free_cache_counters(NULL, cachep);
}

void __init init_cache_counters(void)
{
	memset(cc_hash, 0, CC_HASH_SIZE * sizeof(cc_hash[0]));
	spin_lock_init(&cc_lock);
}

#define cc_hash_fun(ub, cachep)	(				\
	(((unsigned long)(ub) >> L1_CACHE_SHIFT) ^		\
	 ((unsigned long)(ub) >> (BITS_PER_LONG / 2)) ^		\
	 ((unsigned long)(cachep) >> L1_CACHE_SHIFT) ^		\
	 ((unsigned long)(cachep) >> (BITS_PER_LONG / 2))	\
	) & (CC_HASH_SIZE - 1))

static int change_slab_charged(struct user_beancounter *ub,
		struct kmem_cache *cachep, long val)
{
	struct ub_cache_counter *cc, *new_cnt, **pprev;
	unsigned long flags;

	new_cnt = NULL;
again:
	spin_lock_irqsave(&cc_lock, flags);
	cc = cc_hash[cc_hash_fun(ub, cachep)];
	while (cc) {
		if (cc->ub == ub && cc->cachep == cachep)
			goto found;
		cc = cc->next;
	}

	if (new_cnt != NULL)
		goto insert;

	spin_unlock_irqrestore(&cc_lock, flags);

	new_cnt = kmalloc(sizeof(*new_cnt), GFP_ATOMIC);
	if (new_cnt == NULL)
		return -ENOMEM;

	new_cnt->counter = 0;
	new_cnt->ub = ub;
	new_cnt->cachep = cachep;
	goto again;

insert:
	pprev = &cc_hash[cc_hash_fun(ub, cachep)];
	new_cnt->next = *pprev;
	*pprev = new_cnt;
	list_add(&new_cnt->ulist, &ub->ub_cclist);
	cc = new_cnt;
	new_cnt = NULL;

found:
	cc->counter += val;
	spin_unlock_irqrestore(&cc_lock, flags);
	if (new_cnt)
		kfree(new_cnt);
	return 0;
}

static inline int inc_slab_charged(struct user_beancounter *ub,
	struct kmem_cache *cachep)
{
	return change_slab_charged(ub, cachep, 1);
}

static inline void dec_slab_charged(struct user_beancounter *ub,
	struct kmem_cache *cachep)
{
	if (change_slab_charged(ub, cachep, -1) < 0)
		BUG();
}

#include <linux/vmalloc.h>

#define inc_pages_charged(ub, order)	ub_percpu_add(ub, \
					pages_charged, 1 << order)
#define dec_pages_charged(ub, order)	ub_percpu_sub(ub, \
					pages_charged, 1 << order)

#ifdef CONFIG_PROC_FS
static int bc_kmem_debug_show(struct seq_file *f, void *v)
{
	struct user_beancounter *ub;
	struct ub_cache_counter *cc;
	long pages, vmpages;
	int i;

	ub = seq_beancounter(f);

	pages = vmpages = 0;
	for_each_online_cpu(i) {
		pages += per_cpu_ptr(ub->ub_percpu, i)->pages_charged;
		vmpages += per_cpu_ptr(ub->ub_percpu, i)->vmalloc_charged;
	}
	if (pages < 0)
		pages = 0;
	if (vmpages < 0)
		vmpages = 0;

	seq_printf(f, bc_proc_lu_lu_fmt, "pages", pages, PAGE_SIZE);
	seq_printf(f, bc_proc_lu_lu_fmt, "vmalloced", vmpages, PAGE_SIZE);

	spin_lock_irq(&cc_lock);
	list_for_each_entry (cc, &ub->ub_cclist, ulist) {
		struct kmem_cache *cachep;

		cachep = cc->cachep;
		seq_printf(f, bc_proc_lu_lu_fmt,
				kmem_cache_name(cachep),
				cc->counter,
				kmem_cache_objuse(cachep));
	}
	spin_unlock_irq(&cc_lock);
	return 0;
}

static struct bc_proc_entry bc_kmem_debug_entry = {
	.name = "kmem_debug",
	.u.show = bc_kmem_debug_show,
};

static int __init bc_kmem_debug_init(void)
{
	bc_register_proc_entry(&bc_kmem_debug_entry);
	return 0;
}

late_initcall(bc_kmem_debug_init);
#endif

#else
#define inc_slab_charged(ub, cache)		(0)
#define dec_slab_charged(ub, cache)		do { } while (0)
#define inc_pages_charged(ub, cache) 		do { } while (0)
#define dec_pages_charged(ub, cache)		do { } while (0)
#endif

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

	if (inc_slab_charged(ub, cachep) < 0) {
		uncharge_beancounter_fast(ub, UB_KMEMSIZE, size);
		goto out_err;
	}
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

	dec_slab_charged(*ub_ref, cachep);
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
