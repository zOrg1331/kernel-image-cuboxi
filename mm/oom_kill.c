/*
 *  linux/mm/oom_kill.c
 * 
 *  Copyright (C)  1998,2000  Rik van Riel
 *	Thanks go out to Claus Fischer for some serious inspiration and
 *	for goading me into coding this file...
 *
 *  The routines in this file are used to kill a process when
 *  we're seriously out of memory. This gets called from __alloc_pages()
 *  in mm/page_alloc.c when we really run out of memory.
 *
 *  Since we won't call these routines often (on a well-configured
 *  machine) this file will double as a 'coding guide' and a signpost
 *  for newbie kernel hackers. It features several pointers to major
 *  kernel subsystems and hints as to where to find out what things do.
 */

#include <linux/oom.h>
#include <linux/mm.h>
#include <linux/err.h>
#include <linux/sched.h>
#include <linux/virtinfo.h>
#include <linux/swap.h>
#include <linux/timex.h>
#include <linux/jiffies.h>
#include <linux/cpuset.h>
#include <linux/module.h>
#include <linux/notifier.h>
#include <linux/memcontrol.h>
#include <linux/security.h>

#include <bc/beancounter.h>
#include <bc/oom_kill.h>
#include <bc/vmpages.h>

int sysctl_panic_on_oom;
int sysctl_oom_kill_allocating_task;
int sysctl_oom_dump_tasks;
int sysctl_would_have_oomkilled;
static DEFINE_SPINLOCK(zone_scan_lock);
/* #define DEBUG */

/*
 * Is all threads of the target process nodes overlap ours?
 */
static int has_intersects_mems_allowed(struct task_struct *tsk)
{
	struct task_struct *t;

	t = tsk;
	do {
		if (cpuset_mems_allowed_intersects(current, t))
			return 1;
		t = next_thread(t);
	} while (t != tsk);

	return 0;
}

static unsigned long mm_badness(struct mm_struct *mm)
{
	return get_mm_counter(mm, file_rss) + get_mm_counter(mm, anon_rss) +
		get_mm_counter(mm, swap_usage) +
		mm->nr_ptes + mm->nr_ptds + mm->locked_vm;
}

/**
 * badness - calculate a numeric value for how bad this task has been
 * @p: task struct of which task we should calculate
 * @uptime: current uptime in seconds
 *
 * The formula used is relatively simple and documented inline in the
 * function. The main rationale is that we want to select a good task
 * to kill when we run out of memory.
 *
 * Good in this context means that:
 * 1) we lose the minimum amount of work done
 * 2) we recover a large amount of memory
 * 3) we don't kill anything innocent of eating tons of memory
 * 4) we want to kill the minimum amount of processes (one)
 * 5) we try to kill the process the user expects us to kill, this
 *    algorithm has been meticulously tuned to meet the principle
 *    of least surprise ... (be careful when you change it)
 */

unsigned long badness(struct task_struct *p, unsigned long uptime,
		int oom_group)
{
	unsigned long points, cpu_time, run_time;
	struct mm_struct *mm;
	int oom_adj = p->signal->oom_adj;
	struct task_cputime task_time;
	unsigned long utime;
	unsigned long stime;

	if (oom_adj == OOM_DISABLE)
		return 0;

	task_lock(p);
	mm = p->mm;
	if (!mm) {
		task_unlock(p);
		return 0;
	}

	/*
	 * The memory size of the process is the basis for the badness.
	 */
	points = mm_badness(mm);

	/*
	 * After this unlock we can no longer dereference local variable `mm'
	 */
	task_unlock(p);

	/*
	 * swapoff can easily use up all memory, so kill those first.
	 */
	if (p->flags & PF_OOM_ORIGIN)
		return ULONG_MAX;

	/*
	 * CPU time is in tens of seconds and run time is in thousands
         * of seconds. There is no particular reason for this other than
         * that it turned out to work very well in practice.
	 */
	thread_group_cputime(p, &task_time);
	utime = cputime_to_jiffies(task_time.utime);
	stime = cputime_to_jiffies(task_time.stime);
	cpu_time = (utime + stime) >> (SHIFT_HZ + 3);


	if (uptime >= p->start_time.tv_sec)
		run_time = (uptime - p->start_time.tv_sec) >> 10;
	else
		run_time = 0;

	if (cpu_time)
		points /= int_sqrt(cpu_time);
	if (run_time)
		points /= int_sqrt(int_sqrt(run_time));

	/*
	 * Niced processes are most likely less important, so double
	 * their badness points.
	 */
	if (task_nice(p) > 0)
		points *= 2;

	/*
	 * Superuser processes are usually more important, so we make it
	 * less likely that we kill those.
	 */
	if (has_capability_noaudit(p, CAP_SYS_ADMIN) ||
	    has_capability_noaudit(p, CAP_SYS_RESOURCE))
		points /= 4;

	/*
	 * We don't want to kill a process with direct hardware access.
	 * Not only could that mess up the hardware, but usually users
	 * tend to only have this flag set on applications they think
	 * of as important.
	 */
	if (has_capability_noaudit(p, CAP_SYS_RAWIO))
		points /= 4;

	/*
	 * If p's nodes don't overlap ours, it may still help to kill p
	 * because p may have allocated or otherwise mapped memory on
	 * this node before. However it will be less likely.
	 */
	if (!has_intersects_mems_allowed(p))
		points /= 8;

	/*
	 * Adjust the score by oom_adj.
	 */
	if (oom_adj) {
		if (oom_adj > 0) {
			if (!points)
				points = 1;
			points <<= oom_adj;
		} else
			points >>= -(oom_adj);
	}

#ifdef DEBUG
	printk(KERN_DEBUG "OOMkill: task %d (%s) got %lu points\n",
	p->pid, p->comm, points);
#endif
	return points;
}

/*
 * Determine the type of allocation constraint.
 */
static inline enum oom_constraint constrained_alloc(struct zonelist *zonelist,
						    gfp_t gfp_mask)
{
#ifdef CONFIG_NUMA
	struct zone *zone;
	struct zoneref *z;
	enum zone_type high_zoneidx = gfp_zone(gfp_mask);
	nodemask_t nodes = node_states[N_HIGH_MEMORY];

	for_each_zone_zonelist(zone, z, zonelist, high_zoneidx)
		if (cpuset_zone_allowed_softwall(zone, gfp_mask))
			node_clear(zone_to_nid(zone), nodes);
		else
			return CONSTRAINT_CPUSET;

	if (!nodes_empty(nodes))
		return CONSTRAINT_MEMORY_POLICY;
#endif

	return CONSTRAINT_NONE;
}

/*
 * Simple selection loop. We chose the process with the highest
 * number of 'points'. We expect the caller will lock the tasklist.
 *
 * (not docbooked, we don't want this one cluttering up the manual)
 */
struct task_struct *select_bad_process(struct user_beancounter *ub,
						struct mem_cgroup *mem)
{
	struct task_struct *g, *p;
	struct task_struct *chosen = NULL;
	struct timespec uptime;
	unsigned long chosen_points = 0;
	int group, chosen_group = 0;

	do_posix_clock_monotonic_gettime(&uptime);
	do_each_thread_all(g, p) {
		unsigned long points;

		if (p->exit_state)
			continue;
		/* skip the init task */
		if (is_global_init(p))
			continue;
		if (mem && !task_in_mem_cgroup(p, mem))
			continue;
		if (ub_oom_task_skip(ub, p))
			continue;
		if (p->flags & PF_FROZEN)
			continue;

		/*
		 * This task already has access to memory reserves and is
		 * being killed. Don't allow any other task access to the
		 * memory reserve.
		 *
		 * Note: this may have a chance of deadlock if it gets
		 * blocked waiting for another task which itself is waiting
		 * for memory. Is there a better alternative?
		 *
		 * Deadlock fixed: we wait in ub_oom_lock() UB_OOM_TIMEOUT.
		 */
		if (test_tsk_thread_flag(p, TIF_MEMDIE))
			continue;
		/*
		 * skip kernel threads and tasks which have already released
		 * their mm.
		 */
		if (!p->mm)
			continue;

		if (p->signal->oom_adj == OOM_DISABLE)
			continue;

		/*
		 * This is in the process of releasing memory so wait for it
		 * to finish before killing some other task by mistake.
		 *
		 * However, if p is the current task, we allow the 'kill' to
		 * go ahead if it is exiting: this will simply set TIF_MEMDIE,
		 * which will allow it to gain access to memory reserves in
		 * the process of exiting and releasing its resources.
		 * Otherwise we could get an easy OOM deadlock.
		 */
		if (p->flags & PF_EXITING) {
			if (p != current)
				return p;

			chosen = p;
			chosen_points = ULONG_MAX;
		}

		group = get_oom_group(p);
		if (chosen && group > chosen_group)
			continue;

		points = badness(p, uptime.tv_sec, group);
		if (!chosen || group < chosen_group || \
		   (points > chosen_points && group == chosen_group)) {
			chosen = p;
			chosen_points = points;
			chosen_group = group;
		}
	} while_each_thread_all(g, p);

	return chosen;
}

/**
 * dump_tasks - dump current memory state of all system tasks
 * @mem: target memory controller
 *
 * Dumps the current memory state of all system tasks, excluding kernel threads.
 * State information includes task's pid, uid, tgid, vm size, rss, cpu, oom_adj
 * score, and name.
 *
 * If the actual is non-NULL, only tasks that are a member of the mem_cgroup are
 * shown.
 *
 * Call with tasklist_lock read-locked.
 */
static void dump_tasks(const struct mem_cgroup *mem)
{
	struct task_struct *g, *p;

	printk(KERN_INFO "[ pid ]   uid  tgid total_vm      rss cpu oom_adj "
	       "name\n");
	do_each_thread_all(g, p) {
		struct mm_struct *mm;

		if (mem && !task_in_mem_cgroup(p, mem))
			continue;
		if (!thread_group_leader(p))
			continue;

		task_lock(p);
		mm = p->mm;
		if (!mm) {
			/*
			 * total_vm and rss sizes do not exist for tasks with no
			 * mm so there's no need to report them; they can't be
			 * oom killed anyway.
			 */
			task_unlock(p);
			continue;
		}
		printk(KERN_INFO "[%5d] %5d %5d %8lu %8lu %3d     %3d %s\n",
		       p->pid, __task_cred(p)->uid, p->tgid, mm->total_vm,
		       get_mm_rss(mm), (int)task_cpu(p), p->signal->oom_adj,
		       p->comm);
		task_unlock(p);
	} while_each_thread_all(g, p);
}

static void __oom_kill_thread(struct task_struct *p,
		struct oom_control *oom_ctrl)
{
	/*
	 * We give our sacrificial lamb high priority and access to
	 * all the memory it needs. That way it should be able to
	 * exit() and clear out its resources quickly...
	 */
	p->rt.time_slice = HZ;
	set_tsk_thread_flag(p, TIF_MEMDIE);

	force_sig(SIGKILL, p);
	wake_up_process(p);

	if (current->task_bc.oom_generation == oom_ctrl->generation)
		oom_ctrl->kill_counter++;
}

static void __oom_kill_task(struct task_struct *tsk,
		struct oom_control *oom_ctrl)
{
	struct task_struct *p = tsk;

	do {
		__oom_kill_thread(p, oom_ctrl);
		p = next_thread(p);
	} while (p != tsk);
}

#define K(x) ((x) << (PAGE_SHIFT-10))

static int oom_kill_task(struct task_struct *p,
		struct oom_control *oom_ctrl, int verbose)
{
	unsigned long total_vm, total_rss, total_swap;
	struct mm_struct *mm;

	if (is_global_init(p)) {
		WARN_ON(1);
		printk(KERN_WARNING "tried to kill init!\n");
		return -EAGAIN;
	}

	if (sysctl_would_have_oomkilled == 1) {
		printk(KERN_ERR "Would have killed process %d (%s). But continuing instead.\n",
				task_pid_nr(p), p->comm);
		return -EAGAIN;
	}

	if (virtinfo_notifier_call(VITYPE_GENERAL, VIRTINFO_OOMKILL, p)
			& NOTIFY_FAIL) {
		printk(KERN_WARNING "OOM: disabled for process %d (%s) by virtinfo.\n",
				task_pid_nr(p), p->comm);
		return -EAGAIN;
	}

	if (p->signal->oom_adj == OOM_DISABLE) {
		printk(KERN_WARNING "OOM: disabled for process %d (%s) by oom_adj.\n",
				task_pid_nr(p), p->comm);
		return -EAGAIN;
	}

	task_lock(p);
	mm = p->mm;
	if (mm == NULL) {
		printk(KERN_WARNING "OOM: no mm for process %d (%s).\n",
				task_pid_nr(p), p->comm);
		/*
		 * FIXME: this is not really good. If we selected this task
		 * then it had valid mm. If we can't find mm here, then the
		 * task has released it's mm and it's dying. So, in this case,
		 * there is a probability, that some resources will be freed
		 * very soon. So maybe we need to design something more
		 * flexible here...
		 */
		task_unlock(p);
		return -EAGAIN;
	}

	total_vm = mm->total_vm;
	total_rss = get_mm_rss(mm);
	total_swap = get_mm_counter(mm, swap_usage);

	ub_oom_mark_mm(mm, oom_ctrl);
	task_unlock(p);

	__oom_kill_task(p, oom_ctrl);

	if (verbose) {
		struct ve_struct *ve;

		printk(KERN_ERR "OOM killed process %d (%s) "
				"vm:%lukB, rss:%lukB, swap:%lukB\n",
				task_pid_nr(p), p->comm,
				K(total_vm),
				K(total_rss),
				K(total_swap));
#ifdef CONFIG_VE
		ve = VE_TASK_INFO(p)->owner_env;
		if (!ve_is_super(ve)) {
			ve = set_exec_env(ve);
			ve_printk(VE_LOG, KERN_ERR "OOM killed process %d (%s) "
					"vm:%lukB, rss:%lukB, swap:%lukB\n",
					task_pid_vnr(p), p->comm,
					K(total_vm),
					K(total_rss),
					K(total_swap));
			set_exec_env(ve);
		}
#endif
	}
	return 0;
}

void oom_report_invocation(char *type, struct user_beancounter *ub,
		gfp_t gfp_mask, int order)
{
	if (printk_ratelimit()) {
		printk(KERN_WARNING "%d (%s) invoked %s oom-killer: "
				"gfp 0x%x order %d oomkilladj=%d\n",
				current->pid, current->comm, type,
				gfp_mask, order, current->signal->oom_adj);

		if (!ub) {
			dump_stack();
			show_mem();
			show_slab_info();
		} else if (__ratelimit(&ub->ub_ratelimit))
			show_ub_mem(ub);
	}
}

int oom_kill_process(struct task_struct *p, gfp_t gfp_mask, int order,
			    struct mem_cgroup *mem, struct user_beancounter *ub,
			    const char *message)
{
	struct oom_control *oom_ctrl = ub ? &ub->oom_ctrl : &global_oom_ctrl;
	struct task_struct *c, *child;
	int group, child_group;
	struct timespec uptime;
	unsigned long points, child_points;

	/*
	 * If the task is already exiting, don't alarm the sysadmin or kill
	 * its children or threads, just set TIF_MEMDIE so it can die quickly
	 */
	if (p->flags & PF_EXITING)
		return oom_kill_task(p, oom_ctrl, 0);

	printk(KERN_ERR "%s: kill process %d (%s) or a child\n",
					message, task_pid_nr(p), p->comm);

	group = get_oom_group(p);
	points = 0;
	child = NULL;
	do_posix_clock_monotonic_gettime(&uptime);
	/* Try to kill a worst child first */
	list_for_each_entry(c, &p->children, sibling) {
		child_group = get_oom_group(c);
		if (child_group > group)
			continue;
		if (!c->mm || c->mm == p->mm)
			continue;
		if (ub_oom_task_skip(ub, c))
			continue;
		if (mem && !task_in_mem_cgroup(c, mem))
			continue;
		if (c->flags & PF_FROZEN)
			continue;
		if (test_tsk_thread_flag(c, TIF_MEMDIE))
			continue;
		if (c->signal->oom_adj == OOM_DISABLE)
			continue;
		child_points = badness(c, uptime.tv_sec, child_group);
		if (child_group == group && child_points < points)
			continue;
		child = c;
		group = child_group;
		points = child_points;
	}
	if (child && !oom_kill_task(child, oom_ctrl, 1))
		return 0;
	return oom_kill_task(p, oom_ctrl, 1);
}

#ifdef CONFIG_CGROUP_MEM_RES_CTLR
void mem_cgroup_out_of_memory(struct mem_cgroup *mem, gfp_t gfp_mask)
{
	unsigned long points = 0;
	struct task_struct *p;

	read_lock(&tasklist_lock);
retry:
	p = select_bad_process(&points, mem);
	if (PTR_ERR(p) == -1UL)
		goto out;

	if (!p)
		p = current;

	if (oom_kill_process(p, gfp_mask, 0, mem, NULL,
				"Memory cgroup out of memory"))
		goto retry;
out:
	read_unlock(&tasklist_lock);
}
#endif

static BLOCKING_NOTIFIER_HEAD(oom_notify_list);

int register_oom_notifier(struct notifier_block *nb)
{
	return blocking_notifier_chain_register(&oom_notify_list, nb);
}
EXPORT_SYMBOL_GPL(register_oom_notifier);

int unregister_oom_notifier(struct notifier_block *nb)
{
	return blocking_notifier_chain_unregister(&oom_notify_list, nb);
}
EXPORT_SYMBOL_GPL(unregister_oom_notifier);

/*
 * Try to acquire the OOM killer lock for the zones in zonelist.  Returns zero
 * if a parallel OOM killing is already taking place that includes a zone in
 * the zonelist.  Otherwise, locks all zones in the zonelist and returns 1.
 */
int try_set_zone_oom(struct zonelist *zonelist, gfp_t gfp_mask)
{
	struct zoneref *z;
	struct zone *zone;
	int ret = 1;

	spin_lock(&zone_scan_lock);
	for_each_zone_zonelist(zone, z, zonelist, gfp_zone(gfp_mask)) {
		if (zone_is_oom_locked(zone)) {
			ret = 0;
			goto out;
		}
	}

	for_each_zone_zonelist(zone, z, zonelist, gfp_zone(gfp_mask)) {
		/*
		 * Lock each zone in the zonelist under zone_scan_lock so a
		 * parallel invocation of try_set_zone_oom() doesn't succeed
		 * when it shouldn't.
		 */
		zone_set_flag(zone, ZONE_OOM_LOCKED);
	}

out:
	spin_unlock(&zone_scan_lock);
	return ret;
}

/*
 * Clears the ZONE_OOM_LOCKED flag for all zones in the zonelist so that failed
 * allocation attempts with zonelists containing them may now recall the OOM
 * killer, if necessary.
 */
void clear_zonelist_oom(struct zonelist *zonelist, gfp_t gfp_mask)
{
	struct zoneref *z;
	struct zone *zone;

	spin_lock(&zone_scan_lock);
	for_each_zone_zonelist(zone, z, zonelist, gfp_zone(gfp_mask)) {
		zone_clear_flag(zone, ZONE_OOM_LOCKED);
	}
	spin_unlock(&zone_scan_lock);
}

/*
 * Must be called with tasklist_lock held for read.
 */
static void __out_of_memory(gfp_t gfp_mask, int order)
{
	struct task_struct *p;
	struct user_beancounter *ub = NULL;

	if (sysctl_oom_kill_allocating_task)
		if (!oom_kill_process(current, gfp_mask, order, NULL, NULL,
				"Out of memory (oom_kill_allocating_task)"))
			return;
retry:
	put_beancounter(ub);

	/*
	 * Rambo mode: Shoot down a process and hope it solves whatever
	 * issues we may have.
	 */
	ub = ub_oom_select_worst();
	p = select_bad_process(ub, NULL);

	if (PTR_ERR(p) == -1UL)
		goto exit;

	/* Found nothing?!?! Either we hang forever, or we panic. */
	if (!p) {
		if (ub != NULL)
			goto retry;

		read_unlock(&tasklist_lock);
		ub_oom_unlock(&global_oom_ctrl);
		panic("Out of memory and no killable processes...\n");
	}

	if (oom_kill_process(p, gfp_mask, order, NULL, NULL, "Out of memory"))
		goto retry;

exit:
	put_beancounter(ub);
}

/*
 * pagefault handler calls into here because it is out of memory but
 * doesn't know exactly how or why.
 */
void pagefault_out_of_memory(void)
{
	unsigned long freed = 0;

	blocking_notifier_call_chain(&oom_notify_list, 0, &freed);
	if (freed > 0)
		/* Got some memory back in the last second. */
		return;

	if (sysctl_panic_on_oom)
		panic("out of memory from page fault. panic_on_oom is selected.\n");

	if (ub_oom_lock(&global_oom_ctrl))
		goto rest_and_return;

	oom_report_invocation("PF", NULL, 0, 0);

	read_lock(&tasklist_lock);
	__out_of_memory(0, 0); /* unknown gfp_mask and order */
	read_unlock(&tasklist_lock);

	ub_oom_unlock(&global_oom_ctrl);

	/*
	 * Give "p" a good chance of killing itself before we
	 * retry to allocate memory.
	 */
rest_and_return:
	if (!test_thread_flag(TIF_MEMDIE))
		schedule_timeout_uninterruptible(1);
}

/**
 * out_of_memory - kill the "best" process when we run out of memory
 * @zonelist: zonelist pointer
 * @gfp_mask: memory allocation flags
 * @order: amount of memory being requested as a power of 2
 *
 * If we run out of memory, we have the choice between either
 * killing a random task (bad), letting the system crash (worse)
 * OR try to be smart about which process to kill. Note that we
 * don't have to be perfect here, we just have to be good.
 */
void out_of_memory(struct zonelist *zonelist, gfp_t gfp_mask, int order)
{
	unsigned long freed = 0;
	enum oom_constraint constraint;

	blocking_notifier_call_chain(&oom_notify_list, 0, &freed);
	if (freed > 0)
		/* Got some memory back in the last second. */
		return;

	if (sysctl_panic_on_oom == 2)
		panic("out of memory. Compulsory panic_on_oom is selected.\n");

	if (ub_oom_lock(&global_oom_ctrl))
		goto out_oom_lock;

	oom_report_invocation("glob", NULL, gfp_mask, order);

	/*
	 * Check if there were limitations on the allocation (only relevant for
	 * NUMA) that may require different handling.
	 */
	constraint = constrained_alloc(zonelist, gfp_mask);
	read_lock(&tasklist_lock);

	switch (constraint) {
	case CONSTRAINT_MEMORY_POLICY:
		oom_kill_process(current, gfp_mask, order, NULL, NULL,
				"No available memory (MPOL_BIND)");
		break;

	case CONSTRAINT_NONE:
		if (sysctl_panic_on_oom)
			panic("out of memory. panic_on_oom is selected\n");
		/* Fall-through */
	case CONSTRAINT_CPUSET:
		__out_of_memory(gfp_mask, order);
		break;
	}

	read_unlock(&tasklist_lock);
	ub_oom_unlock(&global_oom_ctrl);

out_oom_lock:
	/*
	 * Give "p" a good chance of killing itself before we
	 * retry to allocate memory unless "p" is current
	 */
	if (!test_thread_flag(TIF_MEMDIE))
		schedule_timeout_uninterruptible(1);
}
