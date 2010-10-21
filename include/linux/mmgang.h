#ifndef _LINIX_MMGANG_H
#define _LINIX_MMGANG_H

#include <linux/mm.h>
#include <linux/sched.h>
#include <bc/beancounter.h>

void setup_zone_gang(struct gang_set *gs, struct zone *zone, struct gang *gang);

#ifndef CONFIG_BC_RSS_ACCOUNTING

extern struct gang_set init_gang_set;

static inline struct gang_set *get_mapping_gang(struct address_space *mapping)
{
	return &init_gang_set;
}

static inline struct gang_set *get_mm_gang(struct mm_struct *mm)
{
	return &init_gang_set;
}

static inline struct user_beancounter *get_gangs_ub(struct gang_set *gs)
{
	return get_ub0();
}

static inline struct user_beancounter *get_gang_ub(struct gang *gang)
{
	return get_ub0();
}

#else /* CONFIG_BC_RSS_ACCOUNTING */

#define init_gang_set	(ub0.gang_set)

static inline struct gang_set *get_mapping_gang(struct address_space *mapping)
{
	return &get_exec_ub()->gang_set;
}

static inline struct gang_set *get_mm_gang(struct mm_struct *mm)
{
	return &mm_ub(mm)->gang_set;
}

static inline struct user_beancounter *get_gangs_ub(struct gang_set *gs)
{
	return container_of(gs, struct user_beancounter, gang_set);
}

static inline struct user_beancounter *get_gang_ub(struct gang *gang)
{
	return get_gangs_ub(gang->set);
}

#endif /* CONFIG_BC_RSS_ACCOUNTING */

#ifdef CONFIG_MEMORY_GANGS

static inline struct gang *page_gang(struct page *page)
{
	return rcu_dereference(page->gang);
}

static inline void set_page_gang(struct page *page, struct gang *gang)
{
	rcu_assign_pointer(page->gang, gang);
}

static inline struct gang *mem_zone_gang(struct gang_set *gs, struct zone *zone)
{
	return &gs->gangs[zone_to_nid(zone)][zone_idx(zone)];
}

static inline struct gang *mem_page_gang(struct gang_set *gs, struct page *page)
{
	return &gs->gangs[page_to_nid(page)][page_zonenum(page)];
}

void add_zone_gang(struct zone *zone, struct gang *gang);
static inline int get_zone_nr_gangs(struct zone *zone) { return zone->nr_gangs; }
int alloc_mem_gangs(struct gang_set *gs);
void free_mem_gangs(struct gang_set *gs);
void add_mem_gangs(struct gang_set *gs);
void del_mem_gangs(struct gang_set *gs);
#define for_each_gang(gang, zone)			\
	list_for_each_entry_rcu(gang, &zone->gangs, list)
static inline int pin_mem_gang(struct gang *gang)
{
	return get_beancounter_rcu(get_gang_ub(gang)) ? 0 : -EBUSY;
}
static inline void unpin_mem_gang(struct gang *gang)
{
	put_beancounter(get_gang_ub(gang));
}

static inline void gang_add_free_page(struct page *page)
{
	set_page_gang(page, NULL);
}
static inline void gang_add_user_page(struct page *page, struct gang_set *gs)
{
	set_page_gang(page, mem_page_gang(gs, page));
	charge_beancounter_fast(get_gangs_ub(gs), UB_PHYSPAGES, 1, UB_FORCE);
}
static inline void gang_mod_user_page(struct page *page, struct gang_set *gs)
{
	uncharge_beancounter_fast(get_gang_ub(page_gang(page)), UB_PHYSPAGES, 1);
	charge_beancounter_fast(get_gangs_ub(gs), UB_PHYSPAGES, 1, UB_FORCE);
	set_page_gang(page, mem_page_gang(gs, page));
}
static inline void gang_del_user_page(struct page *page)
{
	uncharge_beancounter_fast(get_gang_ub(page_gang(page)), UB_PHYSPAGES, 1);
	set_page_gang(page, NULL);
}
static inline void gang_add_kernel_page(struct page *page, struct gang_set *gs)
{
	set_page_gang(page, mem_page_gang(gs, page));
}
static inline void gang_del_kernel_page(struct page *page)
{
	set_page_gang(page, NULL);
}

static inline void gang_map_anon_page(struct page *page)
{
	rcu_read_lock();
	ub_percpu_tree_add(get_gang_ub(page_gang(page)), anonymous_pages, 1);
	rcu_read_unlock();
}
static inline void gang_unmap_anon_page(struct page *page)
{
	rcu_read_lock();
	ub_percpu_tree_sub(get_gang_ub(page_gang(page)), anonymous_pages, 1);
	rcu_read_unlock();
}
static inline void gang_map_file_page(struct page *page)
{
	rcu_read_lock();
	ub_percpu_tree_add(get_gang_ub(page_gang(page)), mapped_file_pages, 1);
	rcu_read_unlock();
}
static inline void gang_unmap_file_page(struct page *page)
{
	rcu_read_lock();
	ub_percpu_tree_sub(get_gang_ub(page_gang(page)), mapped_file_pages, 1);
	rcu_read_unlock();
}

static inline struct gang *lock_page_lru(struct page *page)
{
	struct gang *gang;

	rcu_read_lock();
	while (1) {
		gang = page_gang(page);
		spin_lock(&gang->lru_lock);
		if (likely(page_gang(page) == gang))
			break;
		spin_unlock(&gang->lru_lock);
	}
	rcu_read_unlock();

	return gang;
}

static inline struct gang *try_lock_page_lru(struct page *page)
{
	struct gang *gang = NULL;

	rcu_read_lock();
	while (PageLRU(page)) {
		gang = page_gang(page);
		if (unlikely(gang == NULL))
			break;
		spin_lock(&gang->lru_lock);
		if (likely(page_gang(page) == gang))
			break;
		spin_unlock(&gang->lru_lock);
		gang = NULL;
	}
	rcu_read_unlock();

	return gang;
}

#else /* CONFIG_MEMORY_GANGS */

static inline struct gang *page_gang(struct page *page)
{
       return zone_init_gang(page_zone(page));
}

static inline void set_page_gang(struct page *page, struct gang *gang)
{
}

static inline struct gang *mem_zone_gang(struct gang_set *gs, struct zone *zone)
{
	return &zone->init_gang;
}

static inline struct gang *mem_page_gang(struct gang_set *gs, struct page *page)
{
	return &page_zone(page)->init_gang;
}

static inline void add_zone_gang(struct zone *zone, struct gang *gang) { }
static inline int get_zone_nr_gangs(struct zone *zone) { return 1; }
static inline void free_mem_gangs(struct gang_set *gs) { }
static inline int alloc_mem_gangs(struct gang_set *gs) { return -EFAULT; }
static inline void add_mem_gangs(struct gang_set *gs) { }
static inline void del_mem_gangs(struct gang_set *gs) { }
#define for_each_gang(gang, zone)			\
	for ( gang = &(zone)->init_gang ; gang ; gang = NULL )
static inline int pin_mem_gang(struct gang *gang) { return 0; }
static inline void unpin_mem_gang(struct gang *gang) { }

static inline void gang_add_free_page(struct page *page) { }
static inline void gang_add_user_page(struct page *page, struct gang_set *gs) { }
static inline void gang_mod_user_page(struct page *page, struct gang_set *gs) { }
static inline void gang_del_user_page(struct page *page) { }
static inline void gang_add_kernel_page(struct page *page, struct gang_set *gs) { }
static inline void gang_del_kernel_page(struct page *page) { }

static inline void gang_map_anon_page(struct page *page) { }
static inline void gang_unmap_anon_page(struct page *page) { }
static inline void gang_map_file_page(struct page *page) { }
static inline void gang_unmap_file_page(struct page *page) { }

static inline struct gang *lock_page_lru(struct page *page)
{
	struct gang *gang = page_gang(page);

	spin_lock(&gang->lru_lock);
	return gang;
}

static inline struct gang *try_lock_page_lru(struct page *page)
{
	return lock_page_lru(page);
}

#endif /* CONFIG_MEMORY_GANGS */

static inline struct user_beancounter *get_page_ub(struct page *page)
{
	struct user_beancounter *ub;

	rcu_read_lock();
	ub = get_gang_ub(page_gang(page));
	if (ub)
		ub = get_beancounter_rcu(ub);
	rcu_read_unlock();

	return ub;
}

#endif /* _LINIX_MMGANG_H */
