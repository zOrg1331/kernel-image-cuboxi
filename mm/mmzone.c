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

void gang_move_mapped_isolated_page(struct page *page, struct gang_set *gs)
{
	struct gang_set *page_gs;

	VM_BUG_ON(!page_mapped(page));
	VM_BUG_ON(PageLRU(page));

	rcu_read_lock();
	page_gs = page_gang(page)->set;
	if (page_gs == gs) {
		/* nop */
	} else if (PageAnon(page)) {
		gang_unmap_anon_page(page_gs);
		gang_mod_user_page(page, gs);
		gang_map_anon_page(gs);
	} else {
		gang_unmap_file_page(page_gs);
		gang_mod_user_page(page, gs);
		gang_map_file_page(gs);
	}
	rcu_read_unlock();
}

#define MAX_MOVE_BATCH	256

static void move_gang_pages(struct gang *gang, struct gang *dst_gang)
{
	enum lru_list lru;
	int restart;
	struct user_beancounter *src_ub = get_gang_ub(gang);
	struct user_beancounter *dst_ub = get_gang_ub(dst_gang);
	LIST_HEAD(pages_to_wait);

again:
	restart = 0;
	for_each_lru(lru) {
		struct page *page, *next;
		LIST_HEAD(list);
		unsigned long nr_pages = 0, file_mapped = 0, anon_mapped = 0;
		unsigned long file_mapped2 = 0, anon_mapped2 = 0;

		spin_lock_irq(&gang->lru_lock);
		list_splice(&gang->lru[lru].list, &list);
		list_for_each_entry_reverse(page, &list, lru) {
			if (nr_pages >= MAX_MOVE_BATCH) {
				restart = 1;
				break;
			}
			if (!get_page_unless_zero(page)) {
				next = list_entry(page->lru.prev,
						struct page, lru);
				list_move(&page->lru, &pages_to_wait);
				page = next;
				continue;
			}
			nr_pages++;
			if (!atomic_inc_and_test(&page->_mapcount)) {
				if (PageAnon(page))
					anon_mapped2++;
				else
					file_mapped2++;
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
		list_for_each_entry(page, &list, lru) {
			SetPageLRU(page);
			if (!atomic_add_negative(-1, &page->_mapcount)) {
				if (PageAnon(page))
					anon_mapped++;
				else
					file_mapped++;
			}
			put_page(page);
		}
		list_splice(&list, &dst_gang->lru[lru].list);
		dst_gang->lru[lru].nr_pages += nr_pages;
		spin_unlock_irq(&dst_gang->lru_lock);

		/* FIXME NR_ANON_TRANSPARENT_HUGEPAGES */
		mod_zone_page_state(gang->zone, NR_ANON_PAGES,
				anon_mapped - anon_mapped2);
		mod_zone_page_state(gang->zone, NR_FILE_MAPPED,
				file_mapped - file_mapped2);
		uncharge_beancounter_fast(src_ub, UB_PHYSPAGES, nr_pages);
		charge_beancounter_fast(dst_ub, UB_PHYSPAGES, nr_pages, UB_FORCE);
		ub_stat_mod(src_ub, mapped_file_pages, -file_mapped);
		ub_stat_mod(src_ub, anonymous_pages, -anon_mapped);
		ub_stat_mod(dst_ub, mapped_file_pages, file_mapped);
		ub_stat_mod(dst_ub, anonymous_pages, anon_mapped);
	}
	if (restart)
		goto again;

	/* wait for page releasing */
	while (!list_empty(&pages_to_wait))
		schedule_timeout_uninterruptible(1);
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

#else /* CONFIG_MEMORY_GANGS */

void gang_page_stat(struct gang_set *gs, unsigned long *stat)
{
	enum lru_list lru;

	for_each_lru(lru)
		stat[lru] = global_page_state(NR_LRU_BASE + lru);
}

#endif /* CONFIG_MEMORY_GANGS */

struct gang *init_gang_array[MAX_NUMNODES];

#ifndef CONFIG_BC_RSS_ACCOUNTING
struct gang_set init_gang_set = {
	.gangs = init_gang_array,
}
#endif
