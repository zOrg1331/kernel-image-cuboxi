/*
 *  linux/kernel/bc/beancounter.c
 *
 *  Copyright (C) 1998  Alan Cox
 *                1998-2000  Andrey V. Savochkin <saw@saw.sw.com.sg>
 *  Copyright (C) 2000-2005 SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 * TODO:
 *   - more intelligent limit check in mremap(): currently the new size is
 *     charged and _then_ old size is uncharged
 *     (almost done: !move_vma case is completely done,
 *      move_vma in its current implementation requires too many conditions to
 *      do things right, because it may be not only expansion, but shrinking
 *      also, plus do_munmap will require an additional parameter...)
 *   - problem: bad pmd page handling
 *   - consider /proc redesign
 *   - TCP/UDP ports
 *   + consider whether __charge_beancounter_locked should be inline
 *
 * Changes:
 *   1999/08/17  Marcelo Tosatti <marcelo@conectiva.com.br>
 *	- Set "barrier" and "limit" parts of limits atomically.
 *   1999/10/06  Marcelo Tosatti <marcelo@conectiva.com.br>
 *	- setublimit system call.
 */

#include <linux/slab.h>
#include <linux/module.h>
#include <linux/mm.h>
#include <linux/mmgang.h>
#include <linux/sched.h>
#include <linux/random.h>
#include <linux/cgroup.h>
#include <linux/pid_namespace.h>

#include <bc/beancounter.h>
#include <bc/vmpages.h>
#include <bc/proc.h>

static struct kmem_cache *ub_cachep;
static struct user_beancounter default_beancounter;
struct user_beancounter ub0 = {
	.gang_set.gangs = init_gang_array,
};
EXPORT_SYMBOL(ub0);

static struct workqueue_struct *ub_clean_wq;

const char *ub_rnames[] = {
	"kmemsize",	/* 0 */
	"lockedpages",
	"privvmpages",
	"shmpages",
	"dummy",
	"numproc",	/* 5 */
	"physpages",
	"vmguarpages",
	"oomguarpages",
	"numtcpsock",
	"numflock",	/* 10 */
	"numpty",
	"numsiginfo",
	"tcpsndbuf",
	"tcprcvbuf",
	"othersockbuf",	/* 15 */
	"dgramrcvbuf",
	"numothersock",
	"dcachesize",
	"numfile",
	"dummy",	/* 20 */
	"dummy",
	"dummy",
	"numiptent",
	"swappages",
	"unused_privvmpages",	/* UB_RESOURCES */
	"tmpfs_respages",
	"mapped_file",
	"anonymous",
};

unsigned int ub_dcache_threshold __read_mostly = 1024;

/* default maximum perpcu resources precharge */
static int resource_precharge[UB_RESOURCES] = {
	[UB_KMEMSIZE]	= 32 * PAGE_SIZE,
	[UB_NUMPROC]	= 4,
	[UB_PHYSPAGES]	= 256,	/* up to 1Mb */
	[UB_NUMSIGINFO]	= 4,
	[UB_DCACHESIZE] = 4 * PAGE_SIZE,
	[UB_NUMFILE]	= 8,
	[UB_SWAPPAGES]	= 256,
};

/* natural limits for percpu precharge bounds */
static int resource_precharge_min = 0;
static int resource_precharge_max = INT_MAX / NR_CPUS;

void init_beancounter_precharge(struct user_beancounter *ub, int resource)
{
	/* limit maximum precharge with one half of current resource excess */
	ub->ub_parms[resource].max_precharge = min_t(long,
			resource_precharge[resource],
			ub_resource_excess(ub, resource, UB_SOFT) /
			(2 * num_possible_cpus()));
}

static void init_beancounter_precharges(struct user_beancounter *ub)
{
	int resource;

	for ( resource = 0 ; resource < UB_RESOURCES ; resource++ )
		init_beancounter_precharge(ub, resource);
}

static void __init init_beancounter_precharges_early(struct user_beancounter *ub)
{
	int resource;

	for ( resource = 0 ; resource < UB_RESOURCES ; resource++ ) {

		/* DEBUG: sanity checks for initial prechage bounds */
		BUG_ON(resource_precharge[resource] < resource_precharge_min);
		BUG_ON(resource_precharge[resource] > resource_precharge_max);

		ub->ub_parms[resource].max_precharge =
			resource_precharge[resource];
	}
}

static void uncharge_beancounter_precharge(struct user_beancounter *ub)
{
	int resource, precharge;

	for ( resource = 0 ; resource < UB_RESOURCES ; resource++ ) {
		/* DEBUG: to trigger BUG_ON in precharge/charge/uncharge */
		ub->ub_parms[resource].max_precharge = -1;
		precharge = __ub_percpu_sum(ub, precharge[resource]);
		if (!precharge)
			continue;
		BUG_ON(ub->ub_parms[resource].held < precharge);
		__uncharge_beancounter_locked(ub, resource, precharge);
	}
}

static void init_beancounter_struct(struct user_beancounter *ub);
static void init_beancounter_nolimits(struct user_beancounter *ub);

#define UB_HASH_SIZE 256
#define ub_hash_fun(x) ((((x) >> 8) ^ (x)) & (UB_HASH_SIZE - 1))
static struct hlist_head ub_hash[UB_HASH_SIZE];
static DEFINE_SPINLOCK(ub_hash_lock);
LIST_HEAD(ub_list_head); /* protected by ub_hash_lock */
EXPORT_SYMBOL(ub_list_head);

static struct cgroup *ub_cgroup_root;

int set_task_exec_ub(struct task_struct *tsk, struct user_beancounter *ub)
{
	int err;

	err = cgroup_kernel_attach(ub->ub_cgroup, tsk);
	if (err)
		return err;

	put_beancounter(tsk->task_bc.exec_ub);
	tsk->task_bc.exec_ub = get_beancounter(ub);

	return 0;
}
EXPORT_SYMBOL(set_task_exec_ub);

/*
 *	Per user resource beancounting. Resources are tied to their luid.
 *	The resource structure itself is tagged both to the process and
 *	the charging resources (a socket doesn't want to have to search for
 *	things at irq time for example). Reference counters keep things in
 *	hand.
 *
 *	The case where a user creates resource, kills all his processes and
 *	then starts new ones is correctly handled this way. The refcounters
 *	will mean the old entry is still around with resource tied to it.
 */

static struct user_beancounter *alloc_ub(uid_t uid)
{
	struct user_beancounter *new_ub;
	char name[16];

	ub_debug(UBD_ALLOC, "Creating ub %p\n", new_ub);

	new_ub = (struct user_beancounter *)kmem_cache_alloc(ub_cachep, 
			GFP_KERNEL);
	if (new_ub == NULL)
		return NULL;

	memcpy(new_ub, &default_beancounter, sizeof(*new_ub));
	init_beancounter_struct(new_ub);

	init_beancounter_precharges(new_ub);

	snprintf(name, sizeof(name), "%u", uid);
	new_ub->ub_cgroup = cgroup_kernel_open(ub_cgroup_root,
			CGRP_CREAT|CGRP_WEAK, name);
	if (IS_ERR(new_ub->ub_cgroup))
		goto fail_cgroup;

	if (alloc_mem_gangs(&new_ub->gang_set))
		goto fail_gangs;

	if (percpu_counter_init(&new_ub->ub_orphan_count, 0))
		goto fail_pcpu;

	new_ub->ub_percpu = alloc_percpu(struct ub_percpu_struct);
	if (new_ub->ub_percpu == NULL)
		goto fail_free;

	new_ub->ub_uid = uid;
	return new_ub;

fail_free:
	percpu_counter_destroy(&new_ub->ub_orphan_count);
fail_pcpu:
	free_mem_gangs(&new_ub->gang_set);
fail_gangs:
	cgroup_kernel_close(new_ub->ub_cgroup);
fail_cgroup:
	kmem_cache_free(ub_cachep, new_ub);
	return NULL;
}

static inline void __free_ub(struct user_beancounter *ub)
{
	free_percpu(ub->ub_percpu);
	kfree(ub->ub_store);
	free_mem_gangs(&ub->gang_set);
	kfree(ub->private_data2);
	kmem_cache_free(ub_cachep, ub);
}

static inline void free_ub(struct user_beancounter *ub)
{
	percpu_counter_destroy(&ub->ub_orphan_count);
	cgroup_kernel_close(ub->ub_cgroup);
	__free_ub(ub);
}

int ub_count;

struct user_beancounter *get_beancounter_byuid(uid_t uid, int create)
{
	struct user_beancounter *new_ub, *ub;
	unsigned long flags;
	struct hlist_head *hash;
	struct hlist_node *ptr;

	hash = &ub_hash[ub_hash_fun(uid)];

	rcu_read_lock();
	hlist_for_each_entry_rcu(ub, ptr, hash, ub_hash) {
		if (ub->ub_uid != uid)
			continue;

		if (get_beancounter_rcu(ub)) {
			rcu_read_unlock();
			return ub;
		}

		spin_lock_irqsave(&ub_hash_lock, flags);
		if (!hlist_unhashed(&ub->ub_hash)) {
			get_beancounter(ub);
			spin_unlock_irqrestore(&ub_hash_lock, flags);
			rcu_read_unlock();
			cancel_work_sync(&ub->work);
			return ub;
		}
		spin_unlock_irqrestore(&ub_hash_lock, flags);
	}
	rcu_read_unlock();

	if (!create)
		return NULL;

	new_ub = alloc_ub(uid);
	if (new_ub == NULL)
		return NULL;

	spin_lock_irqsave(&ub_hash_lock, flags);

	hlist_for_each_entry(ub, ptr, hash, ub_hash) {
		if (ub->ub_uid != uid)
			continue;

		get_beancounter(ub);
		spin_unlock_irqrestore(&ub_hash_lock, flags);
		free_ub(new_ub);
		cancel_work_sync(&ub->work);
		return ub;
	}

	ub_count++;
	list_add_rcu(&new_ub->ub_list, &ub_list_head);
	hlist_add_head_rcu(&new_ub->ub_hash, hash);
	add_mem_gangs(&new_ub->gang_set);
	spin_unlock_irqrestore(&ub_hash_lock, flags);

	return new_ub;
}
EXPORT_SYMBOL(get_beancounter_byuid);

#ifdef CONFIG_BC_KEEP_UNUSED

void release_beancounter(struct user_beancounter *ub)
{
}

#else

static int verify_res(struct user_beancounter *ub, int resource,
		unsigned long held)
{
	if (likely(held == 0))
		return 1;

	printk(KERN_WARNING "Ub %u helds %ld in %s on put\n",
			ub->ub_uid, held, ub_rnames[resource]);
	return 0;
}

static inline void bc_verify_held(struct user_beancounter *ub)
{
	int i, clean;

	uncharge_beancounter_precharge(ub);
	ub_update_resources_locked(ub);

	clean = 1;
	for (i = 0; i < UB_RESOURCES; i++)
		clean &= verify_res(ub, i, ub->ub_parms[i].held);

	clean &= verify_res(ub, UB_UNUSEDPRIVVM, ub->ub_unused_privvmpages);
	clean &= verify_res(ub, UB_TMPFSPAGES, ub->ub_tmpfs_respages);
	clean &= verify_res(ub, UB_MAPPED_FILE,
			__ub_percpu_sum(ub, mapped_file_pages));
	clean &= verify_res(ub, UB_ANONYMOUS,
			__ub_percpu_sum(ub, anonymous_pages));

	ub_debug_trace(!clean, 5, 60*HZ);
}

static void bc_free_rcu(struct rcu_head *rcu)
{
	struct user_beancounter *ub;

	ub = container_of(rcu, struct user_beancounter, rcu);
	__free_ub(ub);
}

static void delayed_release_beancounter(struct work_struct *w)
{
	struct user_beancounter *ub;
	unsigned long flags;
	int refcount;

	ub = container_of(w, struct user_beancounter, work);

	spin_lock_irqsave(&ub_hash_lock, flags);

	refcount = atomic_read(&ub->ub_refcount);
	if (refcount > 0)
		/* raced with get_beancounter_byuid */
		goto out;

	if (WARN_ON(refcount < 0)) {
		printk(KERN_ERR "UB: Bad refcount (%d) on put of %u (%p)\n",
				refcount, ub->ub_uid, ub);
		goto out;
	}

	if (WARN_ON((ub == get_ub0()))) {
		printk(KERN_ERR "Trying to put ub0\n");
		goto out;
	}

	ub_count--;
	hlist_del_init_rcu(&ub->ub_hash);
	list_del_rcu(&ub->ub_list);
	spin_unlock_irqrestore(&ub_hash_lock, flags);

	BUG_ON(!list_empty(&ub->ub_dentry_lru));

	del_mem_gangs(&ub->gang_set);
	bc_verify_held(ub);
	ub_free_counters(ub);
	percpu_counter_destroy(&ub->ub_orphan_count);
	cgroup_kernel_close(ub->ub_cgroup);

	call_rcu(&ub->rcu, bc_free_rcu);
	return;

out:
	spin_unlock_irqrestore(&ub_hash_lock, flags);
}

void release_beancounter(struct user_beancounter *ub)
{
	unsigned long flags;

	spin_lock_irqsave(&ub_hash_lock, flags);
	if (!atomic_read(&ub->ub_refcount))
		queue_work(ub_clean_wq, &ub->work);
	spin_unlock_irqrestore(&ub_hash_lock, flags);
}

#endif /* CONFIG_BC_KEEP_UNUSED */

EXPORT_SYMBOL(release_beancounter);

/*
 *	Generic resource charging stuff
 */

int __charge_beancounter_locked(struct user_beancounter *ub,
		int resource, unsigned long val, enum ub_severity strict)
{
	ub_debug_resource(resource, "Charging %lu for %d of %p with %lu\n",
			val, resource, ub, ub->ub_parms[resource].held);
	/*
	 * ub_value <= UB_MAXVALUE, value <= UB_MAXVALUE, and only one addition
	 * at the moment is possible so an overflow is impossible.  
	 */
	ub->ub_parms[resource].held += val;

	switch (strict & ~UB_SEV_FLAGS) {
		case UB_HARD:
			if (ub->ub_parms[resource].held >
					ub->ub_parms[resource].barrier)
				break;
		case UB_SOFT:
			if (ub->ub_parms[resource].held >
					ub->ub_parms[resource].limit)
				break;
		case UB_FORCE:
			ub_adjust_maxheld(ub, resource);
			return 0;
		default:
			BUG();
	}

	if (!(strict & UB_TEST)) {
		if (strict == UB_SOFT && __ratelimit(&ub->ub_ratelimit))
			printk(KERN_INFO "Fatal resource shortage: %s, UB %d.\n",
			       ub_rnames[resource], ub->ub_uid);
		ub->ub_parms[resource].failcnt++;
	}
	ub->ub_parms[resource].held -= val;
	return -ENOMEM;
}

int charge_beancounter(struct user_beancounter *ub,
		int resource, unsigned long val, enum ub_severity strict)
{
	int retval;
	unsigned long flags;

	retval = -EINVAL;
	if (val > UB_MAXVALUE)
		goto out;

	if (ub) {
		spin_lock_irqsave(&ub->ub_lock, flags);
		retval = __charge_beancounter_locked(ub, resource, val, strict);
		spin_unlock_irqrestore(&ub->ub_lock, flags);
	}
out:
	return retval;
}

EXPORT_SYMBOL(charge_beancounter);

void uncharge_warn(struct user_beancounter *ub, int resource,
		unsigned long val, unsigned long held)
{
	printk(KERN_ERR "Uncharging too much %lu h %lu, res %s ub %u\n",
			val, held, ub_rnames[resource], ub->ub_uid);
	ub_debug_trace(1, 10, 10*HZ);
}

void __uncharge_beancounter_locked(struct user_beancounter *ub,
		int resource, unsigned long val)
{
	ub_debug_resource(resource, "Uncharging %lu for %d of %p with %lu\n",
			val, resource, ub, ub->ub_parms[resource].held);
	if (ub->ub_parms[resource].held < val) {
		uncharge_warn(ub, resource,
				val, ub->ub_parms[resource].held);
		val = ub->ub_parms[resource].held;
	}
	ub->ub_parms[resource].held -= val;
}

void uncharge_beancounter(struct user_beancounter *ub,
		int resource, unsigned long val)
{
	unsigned long flags;

	if (ub) {
		spin_lock_irqsave(&ub->ub_lock, flags);
		__uncharge_beancounter_locked(ub, resource, val);
		spin_unlock_irqrestore(&ub->ub_lock, flags);
	}
}

EXPORT_SYMBOL(uncharge_beancounter);

/* called with disabled interrupts and preemption */
static int __precharge_beancounter_percpu(struct user_beancounter *ub,
		int resource, unsigned long val)
{
	struct ub_percpu_struct *ub_pcpu = ub_percpu(ub, smp_processor_id());
	int charge, retval;

	BUG_ON(ub->ub_parms[resource].max_precharge < 0);

	if (likely(ub_pcpu->precharge[resource] >= val))
		return 0;

	if (val > ub->ub_parms[resource].max_precharge)
		return -ENOMEM;

	spin_lock(&ub->ub_lock);
	charge = max((int)val, ub->ub_parms[resource].max_precharge >> 1) -
		ub_pcpu->precharge[resource];
	retval = __charge_beancounter_locked(ub, resource,
			charge, UB_SOFT | UB_TEST);
	if (!retval)
		ub_pcpu->precharge[resource] += charge;
	spin_unlock(&ub->ub_lock);

	return retval;
}

/* called with disabled interrupts and preemption */
static int __charge_beancounter_percpu(struct user_beancounter *ub,
		int resource, unsigned long val, enum ub_severity strict)
{
	struct ub_percpu_struct *ub_pcpu = ub_percpu(ub, smp_processor_id());
	int retval, precharge;

	BUG_ON(ub->ub_parms[resource].max_precharge < 0);

	if (likely(ub_pcpu->precharge[resource] >= val)) {
		ub_pcpu->precharge[resource] -= val;
		return 0;
	}

	spin_lock(&ub->ub_lock);
	precharge = max(0, (ub->ub_parms[resource].max_precharge >> 1) -
			ub_pcpu->precharge[resource]);
	retval = __charge_beancounter_locked(ub, resource,
			val + precharge, UB_SOFT | UB_TEST);
	if (!retval)
		ub_pcpu->precharge[resource] += precharge;
	else {
		init_beancounter_precharge(ub, resource);
		retval = __charge_beancounter_locked(ub, resource,
				val, strict);
	}
	spin_unlock(&ub->ub_lock);

	return retval;
}

/* called with disabled interrupts and preemption */
void __uncharge_beancounter_percpu(struct user_beancounter *ub,
		int resource, unsigned long val)
{
	struct ub_percpu_struct *ub_pcpu = ub_percpu(ub, smp_processor_id());
	int uncharge;

	BUG_ON(ub->ub_parms[resource].max_precharge < 0);

	if (likely(ub_pcpu->precharge[resource] + val <=
				ub->ub_parms[resource].max_precharge)) {
		ub_pcpu->precharge[resource] += val;
		return;
	}

	spin_lock(&ub->ub_lock);
	if (ub->ub_parms[resource].max_precharge !=
			resource_precharge[resource])
		init_beancounter_precharge(ub, resource);
	uncharge = max(0, ub_pcpu->precharge[resource] -
			(ub->ub_parms[resource].max_precharge >> 1));
	ub_pcpu->precharge[resource] -= uncharge;
	smp_wmb();
	__uncharge_beancounter_locked(ub, resource, val + uncharge);
	spin_unlock(&ub->ub_lock);
}

unsigned long __get_beancounter_usage_percpu(struct user_beancounter *ub,
		int resource)
{
	long held, precharge;

	held = ub->ub_parms[resource].held;
	smp_rmb();
	precharge = __ub_percpu_sum(ub, precharge[resource]);

	return max(0l, held - precharge);
}

int precharge_beancounter(struct user_beancounter *ub,
		int resource, unsigned long val)
{
	unsigned long flags;
	int retval;

	retval = -EINVAL;
	local_irq_save(flags);
	preempt_disable();

	if (ub)
		retval = __precharge_beancounter_percpu(ub, resource, val);

	preempt_enable();
	local_irq_restore(flags);

	return retval;
}
EXPORT_SYMBOL(precharge_beancounter);

int charge_beancounter_fast(struct user_beancounter *ub,
		int resource, unsigned long val, enum ub_severity strict)
{
	unsigned long flags;
	int retval;

	retval = -EINVAL;
	if (val > UB_MAXVALUE)
		goto out;

	local_irq_save(flags);
	preempt_disable();
	if (ub)
		retval = __charge_beancounter_percpu(ub, resource, val, strict);
	preempt_enable();
	local_irq_restore(flags);
out:
	return retval;
}
EXPORT_SYMBOL(charge_beancounter_fast);

void uncharge_beancounter_fast(struct user_beancounter *ub,
		int resource, unsigned long val)
{
	unsigned long flags;

	local_irq_save(flags);
	preempt_disable();

	if (ub)
		__uncharge_beancounter_percpu(ub, resource, val);

	preempt_enable();
	local_irq_restore(flags);
}
EXPORT_SYMBOL(uncharge_beancounter_fast);

/*
 *	Initialization
 *
 *	struct user_beancounter contains
 *	 - limits and other configuration settings,
 *	   with a copy stored for accounting purposes,
 *	 - structural fields: lists, spinlocks and so on.
 *
 *	Before these parts are initialized, the structure should be memset
 *	to 0 or copied from a known clean structure.  That takes care of a lot
 *	of fields not initialized explicitly.
 */

static void init_beancounter_struct(struct user_beancounter *ub)
{
	ub->ub_magic = UB_MAGIC;
	atomic_set(&ub->ub_refcount, 1);
	spin_lock_init(&ub->ub_lock);
	INIT_LIST_HEAD(&ub->ub_tcp_sk_list);
	INIT_LIST_HEAD(&ub->ub_other_sk_list);
#ifdef CONFIG_BC_DEBUG_KMEM
	INIT_LIST_HEAD(&ub->ub_cclist);
#endif
	INIT_LIST_HEAD(&ub->ub_dentry_lru);
#ifndef CONFIG_BC_KEEP_UNUSED
	INIT_WORK(&ub->work, delayed_release_beancounter);
#endif
}

static void init_beancounter_nolimits(struct user_beancounter *ub)
{
	int k;

	for (k = 0; k < UB_RESOURCES; k++) {
		ub->ub_parms[k].limit = UB_MAXVALUE;
		/* FIXME: whether this is right for physpages and guarantees? */
		ub->ub_parms[k].barrier = UB_MAXVALUE;
	}

	/* FIXME: set unlimited rate? */
	ub->ub_ratelimit.burst = 4;
	ub->ub_ratelimit.interval = 300*HZ;
}

static void init_beancounter_syslimits(struct user_beancounter *ub)
{
	unsigned long mp;
	extern int max_threads;
	int k;

	mp = num_physpages;
	ub->ub_parms[UB_KMEMSIZE].limit = 
		mp > (192*1024*1024 >> PAGE_SHIFT) ?
				32*1024*1024 : (mp << PAGE_SHIFT) / 6;
	ub->ub_parms[UB_LOCKEDPAGES].limit = 8;
	ub->ub_parms[UB_PRIVVMPAGES].limit = UB_MAXVALUE;
	ub->ub_parms[UB_SHMPAGES].limit = 64;
	ub->ub_parms[UB_NUMPROC].limit = max_threads / 2;
	ub->ub_parms[UB_NUMTCPSOCK].limit = 1024;
	ub->ub_parms[UB_TCPSNDBUF].limit = 1024*4*1024; /* 4k per socket */
	ub->ub_parms[UB_TCPRCVBUF].limit = 1024*6*1024; /* 6k per socket */
	ub->ub_parms[UB_NUMOTHERSOCK].limit = 256;
	ub->ub_parms[UB_DGRAMRCVBUF].limit = 256*4*1024; /* 4k per socket */
	ub->ub_parms[UB_OTHERSOCKBUF].limit = 256*8*1024; /* 8k per socket */
	ub->ub_parms[UB_NUMFLOCK].limit = 1024;
	ub->ub_parms[UB_NUMPTY].limit = 16;
	ub->ub_parms[UB_NUMSIGINFO].limit = 1024;
	ub->ub_parms[UB_DCACHESIZE].limit = 1024*1024;
	ub->ub_parms[UB_NUMFILE].limit = 1024;
	ub->ub_parms[UB_PHYSPAGES].limit = UB_MAXVALUE;
	ub->ub_parms[UB_SWAPPAGES].limit = UB_MAXVALUE;

	for (k = 0; k < UB_RESOURCES; k++)
		ub->ub_parms[k].barrier = ub->ub_parms[k].limit;

	ub->ub_ratelimit.burst = 4;
	ub->ub_ratelimit.interval = 300*HZ;
}

static DEFINE_PER_CPU(struct ub_percpu_struct, ub0_percpu);

void __init ub_init_early(void)
{
	struct user_beancounter *ub;

	init_cache_counters();
	ub = get_ub0();
	ub->ub_uid = 0;
	init_beancounter_nolimits(ub);
	init_beancounter_struct(ub);
	init_beancounter_precharges_early(ub);
	ub->ub_percpu = &per_cpu_var(ub0_percpu);

	memset(&current->task_bc, 0, sizeof(struct task_beancounter));
	(void)set_exec_ub(ub);
	current->task_bc.task_ub = get_beancounter(ub);
	__charge_beancounter_locked(ub, UB_NUMPROC, 1, UB_FORCE);
	current->task_bc.fork_sub = get_beancounter(ub);
	init_mm.mm_ub = get_beancounter(ub);

	hlist_add_head(&ub->ub_hash, &ub_hash[ub->ub_uid]);
	list_add(&ub->ub_list, &ub_list_head);
	ub_count++;
}

static int proc_resource_precharge(ctl_table *table, int write,
		void __user *buffer, size_t *lenp, loff_t *ppos)
{
	static DEFINE_MUTEX(lock);
	struct user_beancounter *ub;
	int err;

	mutex_lock(&lock);

	err = proc_dointvec_minmax(table, write, buffer, lenp, ppos);
	if (err || !write)
		goto out;

	rcu_read_lock();
	for_each_beancounter(ub) {
		spin_lock_irq(&ub->ub_lock);
		init_beancounter_precharges(ub);
		spin_unlock_irq(&ub->ub_lock);
	}
	rcu_read_unlock();

out:
	mutex_unlock(&lock);
	return err;
}

static ctl_table ub_sysctl_table[] = {
	{
		.procname	= "resource_precharge",
		.ctl_name	= -2,
		.data		= &resource_precharge,
		.extra1		= &resource_precharge_min,
		.extra2		= &resource_precharge_max,
		.maxlen		= sizeof(resource_precharge),
		.mode		= 0644,
		.proc_handler	= &proc_resource_precharge,
	},
	{
		.procname	= "dcache_threshold",
		.ctl_name	= CTL_UNNUMBERED,
		.data		= &ub_dcache_threshold,
		.maxlen		= sizeof(ub_dcache_threshold),
		.mode		= 0644,
		.proc_handler	= &proc_dointvec,
	},
	{ .ctl_name = 0 }
};

static ctl_table ub_sysctl_root[] = {
       {
	       .ctl_name	= -2,
	       .procname	= "ubc",
	       .mode		= 0555,
	       .child		= ub_sysctl_table,
       },
       { .ctl_name = 0 }
};

void __init ub_init_late(void)
{
	register_sysctl_table(ub_sysctl_root);
	ub_cachep = kmem_cache_create("user_beancounters",
			sizeof(struct user_beancounter),
			0, SLAB_HWCACHE_ALIGN | SLAB_PANIC, NULL);

	memset(&default_beancounter, 0, sizeof(default_beancounter));
#ifdef CONFIG_BC_UNLIMITED
	init_beancounter_nolimits(&default_beancounter);
#else
	init_beancounter_syslimits(&default_beancounter);
#endif
	init_beancounter_struct(&default_beancounter);
}

static __init int ub_init_wq(void)
{
	ub_clean_wq = create_singlethread_workqueue("ubcleand");
	if (ub_clean_wq == NULL)
		panic("Can't create ubclean wq");
	return 0;
}

late_initcall(ub_init_wq);

int __init ub_init_cgroup(void)
{
	struct vfsmount *mnt;
	struct cgroup_sb_opts opts = {
		.subsys_bits    = 1ul << blkio_subsys_id,
	};

	mnt = cgroup_kernel_mount(&opts);
	if (IS_ERR(mnt))
		return PTR_ERR(mnt);
	ub_cgroup_root = cgroup_get_root(mnt);

	ub0.ub_cgroup = cgroup_kernel_open(ub_cgroup_root, CGRP_CREAT, "0");
	if (IS_ERR(ub0.ub_cgroup))
		return PTR_ERR(ub0.ub_cgroup);

	return cgroup_kernel_attach(ub0.ub_cgroup, init_pid_ns.child_reaper);
}
late_initcall(ub_init_cgroup);
