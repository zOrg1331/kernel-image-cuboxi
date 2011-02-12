/*
 *  include/bc/kmem.h
 *
 *  Copyright (C) 2005  SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 */

#ifndef __UB_SLAB_H_
#define __UB_SLAB_H_

#include <bc/beancounter.h>
#include <bc/decl.h>
#include <linux/mmgang.h>

/*
 * UB_KMEMSIZE accounting
 */

#ifdef CONFIG_BC_DEBUG_ITEMS
#define CHARGE_ORDER(__o)		(1 << (__o))
#define CHARGE_SIZE(__s)		1
#else
#define CHARGE_ORDER(__o)		(PAGE_SIZE << (__o))
#define CHARGE_SIZE(__s)		(__s)
#endif

#ifdef CONFIG_BEANCOUNTERS
static inline struct user_beancounter *page_ub(struct page *page)
{
	/* kernel pages hold ub, so no rcu_dereference there */
	struct gang *gang = page->gang;

	return gang ? get_gang_ub(gang) : NULL;
}
#else
#define page_ub(__page)	NULL
#endif

struct mm_struct;
struct page;
struct kmem_cache;

UB_DECLARE_FUNC(struct user_beancounter *, vmalloc_ub(void *obj))
UB_DECLARE_FUNC(struct user_beancounter *, mem_ub(void *obj))

UB_DECLARE_FUNC(int, ub_page_charge(struct page *page, int order,
			struct user_beancounter *ub, enum ub_severity strict))
UB_DECLARE_VOID_FUNC(ub_page_uncharge(struct page *page, int order))
UB_DECLARE_FUNC(int, ub_slab_charge(struct kmem_cache *cachep,
			void *objp, gfp_t flags))
UB_DECLARE_VOID_FUNC(ub_slab_uncharge(struct kmem_cache *cachep, void *obj))

static inline void *ub_kmem_alloc(struct user_beancounter *ub,
		struct kmem_cache *cachep, gfp_t gfp_flags)
{
	void *objp;

	if (charge_beancounter_fast(ub, UB_KMEMSIZE,
				cachep->objuse,
				(gfp_flags & __GFP_SOFT_UBC)?UB_SOFT:UB_HARD))
		return NULL;

	objp = kmem_cache_alloc(cachep, gfp_flags);

	if (unlikely(objp == NULL))
		uncharge_beancounter_fast(ub, UB_KMEMSIZE, cachep->objuse);

	return objp;
}

static inline void ub_kmem_free(struct user_beancounter *ub,
		struct kmem_cache *cachep, void *objp)
{
	kmem_cache_free(cachep, objp);
	uncharge_beancounter_fast(ub, UB_KMEMSIZE, cachep->objuse);
}

#ifdef CONFIG_BEANCOUNTERS
static inline int should_charge(unsigned long cflags, gfp_t flags)
{
	if (!(cflags & SLAB_UBC))
		return 0;
	if ((cflags & SLAB_NO_CHARGE) && !(flags & __GFP_UBC))
		return 0;
	return 1;
}

#define should_uncharge(cflags)	should_charge(cflags, __GFP_UBC)
#else
#define should_charge(cflags, f)	0
#define should_uncharge(cflags)		0
#endif

#endif /* __UB_SLAB_H_ */
