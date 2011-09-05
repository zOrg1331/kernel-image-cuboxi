/*
 * linux/mm/mmzone.c
 *
 * management codes for pgdats and zones.
 */


#include <linux/stddef.h>
#include <linux/mm.h>
#include <linux/mmzone.h>
#include <linux/mmgang.h>
#include <linux/pagemap.h>
#include <linux/swap.h>
#include <linux/module.h>
#include <linux/mm_inline.h>

#include "internal.h"

struct pglist_data *first_online_pgdat(void)
{
	return NODE_DATA(first_online_node);
}
EXPORT_SYMBOL(first_online_pgdat);

struct pglist_data *next_online_pgdat(struct pglist_data *pgdat)
{
	int nid = next_online_node(pgdat->node_id);

	if (nid == MAX_NUMNODES)
		return NULL;
	return NODE_DATA(nid);
}
EXPORT_SYMBOL(next_online_pgdat);

/*
 * next_zone - helper magic for for_each_zone()
 */
struct zone *next_zone(struct zone *zone)
{
	pg_data_t *pgdat = zone->zone_pgdat;

	if (zone < pgdat->node_zones + MAX_NR_ZONES - 1)
		zone++;
	else {
		pgdat = next_online_pgdat(pgdat);
		if (pgdat)
			zone = pgdat->node_zones;
		else
			zone = NULL;
	}
	return zone;
}

static inline int zref_in_nodemask(struct zoneref *zref, nodemask_t *nodes)
{
#ifdef CONFIG_NUMA
	return node_isset(zonelist_node_idx(zref), *nodes);
#else
	return 1;
#endif /* CONFIG_NUMA */
}

/* Returns the next zone at or below highest_zoneidx in a zonelist */
struct zoneref *next_zones_zonelist(struct zoneref *z,
					enum zone_type highest_zoneidx,
					nodemask_t *nodes,
					struct zone **zone)
{
	/*
	 * Find the next suitable zone to use for the allocation.
	 * Only filter based on nodemask if it's set
	 */
	if (likely(nodes == NULL))
		while (zonelist_zone_idx(z) > highest_zoneidx)
			z++;
	else
		while (zonelist_zone_idx(z) > highest_zoneidx ||
				(z->zone && !zref_in_nodemask(z, nodes)))
			z++;

	*zone = zonelist_zone(z);
	return z;
}

#ifdef CONFIG_ARCH_HAS_HOLES_MEMORYMODEL
int memmap_valid_within(unsigned long pfn,
					struct page *page, struct zone *zone)
{
	if (page_to_pfn(page) != pfn)
		return 0;

	if (page_zone(page) != zone)
		return 0;

	return 1;
}
#endif /* CONFIG_ARCH_HAS_HOLES_MEMORYMODEL */

void setup_zone_gang(struct gang_set *gs, struct zone *zone, struct gang *gang)
{
	enum lru_list lru;

	gang->zone = zone;
	gang->set = gs;
	spin_lock_init(&gang->lru_lock);
	for_each_lru(lru) {
		INIT_LIST_HEAD(&gang->lru[lru].list);
		gang->lru[lru].nr_pages = 0;
	}
}

#ifdef CONFIG_MEMORY_GANGS

void add_zone_gang(struct zone *zone, struct gang *gang)
{
	unsigned long flags;

	spin_lock_irqsave(&zone->gangs_lock, flags);
	list_add_tail_rcu(&gang->list, &zone->gangs);
	list_add_tail(&gang->rr_list, &zone->gangs_rr);
	zone->nr_gangs++;
	spin_unlock_irqrestore(&zone->gangs_lock, flags);
}

static void del_zone_gang(struct zone *zone, struct gang *gang)
{
	unsigned long flags;
	enum lru_list lru;

	for_each_lru(lru) {
		BUG_ON(!list_empty(&gang->lru[lru].list));
		if (gang->lru[lru].nr_pages) {
			printk(KERN_EMERG "gang leak:%ld lru:%d gang:%p\n",
					gang->lru[lru].nr_pages, lru, gang);
			add_taint(TAINT_CRAP);
		}
	}

	spin_lock_irqsave(&zone->gangs_lock, flags);
	list_del_rcu(&gang->list);
	list_del(&gang->rr_list);
	zone->nr_gangs--;
	spin_unlock_irqrestore(&zone->gangs_lock, flags);
}

int alloc_mem_gangs(struct gang_set *gs)
{
	struct zone *zone;
	struct gang *gang;
	int node;

	memset(gs, 0, sizeof(struct gang_set));

	gs->gangs = kzalloc(nr_node_ids * sizeof(struct gang *), GFP_KERNEL);
	if (!gs->gangs)
		goto noarr;

	for_each_online_node(node) {
		gs->gangs[node] = kzalloc_node(sizeof(struct gang)*MAX_NR_ZONES,
						GFP_KERNEL, node);
		if (!gs->gangs[node])
			goto nomem;
	}

	for_each_populated_zone(zone) {
		gang = mem_zone_gang(gs, zone);
		setup_zone_gang(gs, zone, gang);
	}

	return 0;

nomem:
	free_mem_gangs(gs);
noarr:
	return -ENOMEM;
}

void free_mem_gangs(struct gang_set *gs)
{
	int node;

	for_each_node(node)
		kfree(gs->gangs[node]);
	kfree(gs->gangs);
}

void add_mem_gangs(struct gang_set *gs)
{
	struct zone *zone;

	for_each_populated_zone(zone)
		add_zone_gang(zone, mem_zone_gang(gs, zone));
}

#define MAX_MOVE_BATCH	256

static void move_gang_pages(struct gang *gang, struct gang *dst_gang)
{
	enum lru_list lru;
	int restart, wait;
	struct user_beancounter *src_ub = get_gang_ub(gang);
	struct user_beancounter *dst_ub = get_gang_ub(dst_gang);
	LIST_HEAD(pages_to_wait);
	LIST_HEAD(pages_to_free);

again:
	restart = wait = 0;
	for_each_lru(lru) {
		struct page *page, *next;
		LIST_HEAD(list);
		unsigned long nr_pages = 0;
		unsigned batch = 0;

		spin_lock_irq(&gang->lru_lock);
		list_splice(&gang->lru[lru].list, &list);
		list_for_each_entry_safe_reverse(page, next, &list, lru) {
			int numpages = hpage_nr_pages(page);

			if (batch >= MAX_MOVE_BATCH) {
				restart = 1;
				break;
			}
			if (!get_page_unless_zero(page)) {
				list_move(&page->lru, &pages_to_wait);
				restart = wait = 1;
				continue;
			}
			batch++;
			nr_pages += numpages;
			ClearPageLRU(page);
			set_page_gang(page, dst_gang);
		}
		list_cut_position(&gang->lru[lru].list, &list, &page->lru);
		list_splice_init(&pages_to_wait, &gang->lru[lru].list);
		gang->lru[lru].nr_pages -= nr_pages;
		spin_unlock_irq(&gang->lru_lock);

		if (!nr_pages)
			continue;

#ifdef CONFIG_BC_SWAP_ACCOUNTING
		if (!is_file_lru(lru)) {
			list_for_each_entry(page, &list, lru) {
				if (PageSwapCache(page)) {
					lock_page(page);
					ub_unuse_swap_page(page);
					unlock_page(page);
				}
			}
		}
#endif

		uncharge_beancounter_fast(src_ub, UB_PHYSPAGES, nr_pages);
		charge_beancounter_fast(dst_ub, UB_PHYSPAGES, nr_pages, UB_FORCE);

		spin_lock_irq(&dst_gang->lru_lock);
		dst_gang->lru[lru].nr_pages += nr_pages;
		list_for_each_entry_safe(page, next, &list, lru) {
			SetPageLRU(page);
			if (unlikely(put_page_testzero(page))) {
				__ClearPageLRU(page);
				del_page_from_lru(dst_gang, page);
				gang_del_user_page(page);
				list_add(&page->lru, &pages_to_free);
			}
		}
		list_splice(&list, &dst_gang->lru[lru].list);
		spin_unlock_irq(&dst_gang->lru_lock);

		list_for_each_entry_safe(page, next, &pages_to_free, lru) {
			list_del(&page->lru);
			VM_BUG_ON(PageTail(page));
			if (PageCompound(page))
				get_compound_page_dtor(page)(page);
			else
				free_hot_page(page);
		}
	}
	if (wait)
		schedule_timeout_uninterruptible(1);
	if (restart)
		goto again;
}

void del_mem_gangs(struct gang_set *gs)
{
	struct zone *zone;
	struct gang *gang;

	lru_add_drain_all();

	for_each_populated_zone(zone) {
		gang = mem_zone_gang(gs, zone);
		move_gang_pages(gang, zone_init_gang(zone));
		del_zone_gang(zone, gang);
	}
}

void gang_page_stat(struct gang_set *gs, unsigned long *stat)
{
	struct zone *zone;
	struct gang *gang;
	enum lru_list lru;

	memset(stat, 0, sizeof(unsigned long) * NR_LRU_LISTS);
	for_each_populated_zone(zone) {
		gang = mem_zone_gang(gs, zone);
		for_each_lru(lru)
			stat[lru] += gang->lru[lru].nr_pages;
	}
}

void gang_show_state(struct gang_set *gs)
{
	struct zone *zone;
	struct gang *gang;
	unsigned long stat[NR_LRU_LISTS];

	for_each_populated_zone(zone) {
		gang = mem_zone_gang(gs, zone);
		printk("Node %d %s scan:%lu"
			" a_anon:%lu i_anon:%lu"
			" a_file:%lu i_file:%lu"
			" unevictable:%lu\n",
			zone_to_nid(zone), zone->name, gang->pages_scanned,
			gang->lru[LRU_ACTIVE_ANON].nr_pages,
			gang->lru[LRU_INACTIVE_ANON].nr_pages,
			gang->lru[LRU_ACTIVE_FILE].nr_pages,
			gang->lru[LRU_INACTIVE_FILE].nr_pages,
			gang->lru[LRU_UNEVICTABLE].nr_pages);
	}

	gang_page_stat(gs, stat);

	printk("Total %lu anon:%lu file:%lu"
			" a_anon:%lu i_anon:%lu"
			" a_file:%lu i_file:%lu"
			" unevictable:%lu\n",
			stat[LRU_ACTIVE_ANON] + stat[LRU_INACTIVE_ANON] +
			stat[LRU_ACTIVE_FILE] + stat[LRU_INACTIVE_FILE] +
			stat[LRU_UNEVICTABLE],
			stat[LRU_ACTIVE_ANON] + stat[LRU_INACTIVE_ANON],
			stat[LRU_ACTIVE_FILE] + stat[LRU_INACTIVE_FILE],
			stat[LRU_ACTIVE_ANON],
			stat[LRU_INACTIVE_ANON],
			stat[LRU_ACTIVE_FILE],
			stat[LRU_INACTIVE_FILE],
			stat[LRU_UNEVICTABLE]);
}

void gang_rate_limit(struct gang_set *gs, int wait, unsigned count)
{
	struct user_beancounter *ub = get_gangs_ub(gs);
	ktime_t wall;
	u64 step;

	if (!ub->rl_step)
		return;

	spin_lock(&ub->rl_lock);
	step = (u64)ub->rl_step * count;
	wall = ktime_add_ns(ktime_get(), step);
	if (wall.tv64 < ub->rl_wall.tv64)
		wall = ktime_add_ns(ub->rl_wall, step);
	ub->rl_wall = wall;
	spin_unlock(&ub->rl_lock);

	if (wait && !test_thread_flag(TIF_MEMDIE)) {
		set_current_state(TASK_KILLABLE);
		schedule_hrtimeout(&wall, HRTIMER_MODE_ABS);
	}
}

#else /* CONFIG_MEMORY_GANGS */

void gang_page_stat(struct gang_set *gs, unsigned long *stat)
{
	enum lru_list lru;

	for_each_lru(lru)
		stat[lru] = global_page_state(NR_LRU_BASE + lru);
}

void gang_show_state(struct gang_set *gs) { }

#endif /* CONFIG_MEMORY_GANGS */

struct gang *init_gang_array[MAX_NUMNODES];

#ifndef CONFIG_BC_RSS_ACCOUNTING
struct gang_set init_gang_set = {
#ifdef CONFIG_MEMORY_GANGS
	.gangs = init_gang_array,
#endif
};
#endif
