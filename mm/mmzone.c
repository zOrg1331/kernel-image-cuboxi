/*
 * linux/mm/mmzone.c
 *
 * management codes for pgdats and zones.
 */


#include <linux/stddef.h>
#include <linux/mm.h>
#include <linux/mmzone.h>
#include <linux/mmgang.h>
#include <linux/swap.h>
#include <linux/module.h>

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
		BUG_ON(gang->lru[lru].nr_pages);
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
	return -ENOMEM;
}

void free_mem_gangs(struct gang_set *gs)
{
	int node;

	for_each_node(node)
		kfree(gs->gangs[node]);
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
	int restart;
	struct user_beancounter *src_ub = get_gang_ub(gang);
	struct user_beancounter *dst_ub = get_gang_ub(dst_gang);

again:
	restart = 0;
	for_each_lru(lru) {
		struct page *page;
		LIST_HEAD(list);
		unsigned long nr_pages = 0, file_mapped = 0, anon_mapped = 0;

		spin_lock_irq(&gang->lru_lock);
		list_splice(&gang->lru[lru].list, &list);
		list_for_each_entry_reverse(page, &list, lru) {
			if (nr_pages >= MAX_MOVE_BATCH) {
				restart = 1;
				break;
			}
			nr_pages++;
			if (page_mapped(page)) { // FIXME races
				if (PageAnon(page))
					anon_mapped++;
				else
					file_mapped++;
			}
			ClearPageLRU(page);
			set_page_gang(page, dst_gang);
		}
		list_cut_position(&gang->lru[lru].list, &list, &page->lru);
		gang->lru[lru].nr_pages -= nr_pages;
		spin_unlock_irq(&gang->lru_lock);

		if (!nr_pages)
			continue;

		spin_lock_irq(&dst_gang->lru_lock);
		list_for_each_entry(page, &list, lru)
			SetPageLRU(page);
		list_splice(&list, &dst_gang->lru[lru].list);
		dst_gang->lru[lru].nr_pages += nr_pages;
		spin_unlock_irq(&dst_gang->lru_lock);

		uncharge_beancounter_fast(src_ub, UB_PHYSPAGES, nr_pages);
		charge_beancounter_fast(dst_ub, UB_PHYSPAGES, nr_pages, UB_FORCE);
		ub_percpu_tree_sub(src_ub, mapped_file_pages, file_mapped);
		ub_percpu_tree_sub(src_ub, anonymous_pages, anon_mapped);
		ub_percpu_tree_add(dst_ub, mapped_file_pages, file_mapped);
		ub_percpu_tree_add(dst_ub, anonymous_pages, anon_mapped);
	}
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

#endif /* CONFIG_MEMORY_GANGS */

#ifndef CONFIG_BC_RSS_ACCOUNTING
struct gang_set init_gang_set;
#endif
