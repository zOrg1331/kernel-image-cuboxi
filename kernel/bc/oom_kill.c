#include <linux/wait.h>
#include <linux/sched.h>
#include <linux/mm.h>
#include <linux/swap.h>
#include <linux/cpuset.h>
#include <linux/module.h>
#include <linux/oom.h>

#include <bc/beancounter.h>
#include <bc/oom_kill.h>
#include <bc/vmpages.h>

#define UB_OOM_TIMEOUT	(5 * HZ)

void ub_oom_start(struct oom_control *oom_ctrl)
{
	current->task_bc.oom_generation = oom_ctrl->generation;
}

/*
 * Must be called under task_lock() held
 */
void ub_oom_mark_mm(struct mm_struct *mm, struct oom_control *oom_ctrl)
{
	mm_ub(mm)->ub_parms[UB_OOMGUARPAGES].failcnt++;

	if (oom_ctrl == &global_oom_ctrl)
		mm->global_oom = 1;
	else {
		/*
		 * Task can be killed when using either global oom ctl
		 * or by task's beancounter one.
		 * When this task will die it'll have to decide with ctl
		 * to use lokking at this flag and we have to sure it
		 * will use the proper one.
		 */
		BUG_ON(mm->mm_ub != get_exec_ub());
		mm->ub_oom = 1;
	}
}

static inline int ub_oom_completed(struct oom_control *oom_ctrl)
{
	if (test_thread_flag(TIF_MEMDIE))
		/* we were oom killed - just die */
		return 1;
	if (current->task_bc.oom_generation != oom_ctrl->generation)
		/* some task was succesfully killed */
		return 1;
	return 0;
}

static void ub_clear_oom(void)
{
	struct user_beancounter *ub;

	rcu_read_lock();
	for_each_beancounter(ub)
		ub->ub_oom_noproc = 0;
	rcu_read_unlock();
}

int ub_oom_lock(struct oom_control *oom_ctrl)
{
	int timeout;
	DEFINE_WAIT(oom_w);

	if (oom_ctrl != &global_oom_ctrl && global_oom_ctrl.kill_counter) {
		/*
		 * Check if global OOM killeris on the way. If so -
		 * let the senior handle the situation.
		 */
		wait_event_killable(global_oom_ctrl.wq,
					global_oom_ctrl.kill_counter == 0);
		return -EAGAIN;
	}

	spin_lock(&oom_ctrl->lock);
	if (!oom_ctrl->kill_counter && !ub_oom_completed(oom_ctrl))
		goto out_do_oom;

	timeout = UB_OOM_TIMEOUT;
	while (1) {
		if (ub_oom_completed(oom_ctrl)) {
			spin_unlock(&oom_ctrl->lock);
			/*
			 * We raced with some other OOM killer and need
			 * to update generation to be sure, that we can
			 * call OOM killer on next loop iteration.
			 */
			ub_oom_start(oom_ctrl);
			return -EAGAIN;
		}

		if (timeout == 0)
			break;

		__set_current_state(TASK_UNINTERRUPTIBLE);
		add_wait_queue(&oom_ctrl->wq, &oom_w);
		spin_unlock(&oom_ctrl->lock);

		timeout = schedule_timeout(timeout);

		spin_lock(&oom_ctrl->lock);
		remove_wait_queue(&oom_ctrl->wq, &oom_w);

	}

out_do_oom:
	ub_clear_oom();
	return 0;
}

static inline long ub_current_overdraft(struct user_beancounter *ub)
{
	return ((ub->ub_parms[UB_KMEMSIZE].held
		  + ub->ub_parms[UB_TCPSNDBUF].held
		  + ub->ub_parms[UB_TCPRCVBUF].held
		  + ub->ub_parms[UB_OTHERSOCKBUF].held
		  + ub->ub_parms[UB_DGRAMRCVBUF].held)
		 >> PAGE_SHIFT) - ub_oomguarpages_left(ub);
}

int ub_oom_task_skip(struct user_beancounter *ub, struct task_struct *tsk)
{
	struct user_beancounter *mm_ub;

	if (ub == NULL)
		return 0;

	task_lock(tsk);
	if (tsk->mm == NULL)
		mm_ub = NULL;
	else
		mm_ub = tsk->mm->mm_ub;

	task_unlock(tsk);

	return mm_ub != ub;
}

struct user_beancounter *ub_oom_select_worst(void)
{
	struct user_beancounter *ub, *walkp;
	long ub_maxover;

	ub_maxover = 0;
	ub = NULL;

	rcu_read_lock();
	for_each_beancounter (walkp) {
		long ub_overdraft;

		if (walkp->ub_oom_noproc)
			continue;

		ub_overdraft = ub_current_overdraft(walkp);
		if (ub_overdraft > ub_maxover && get_beancounter_rcu(walkp)) {
			put_beancounter(ub);
			ub = walkp;
			ub_maxover = ub_overdraft;
		}
	}

	if (ub)
		ub->ub_oom_noproc = 1;
	rcu_read_unlock();

	return ub;
}

void ub_oom_unlock(struct oom_control *oom_ctrl)
{
	spin_unlock(&oom_ctrl->lock);
}

static void ub_release_oom_control(struct oom_control *oom_ctrl)
{
	spin_lock(&oom_ctrl->lock);
	oom_ctrl->kill_counter = 0;
	oom_ctrl->generation++;

	/* if there is time to sleep in ub_oom_lock -> sleep will continue */
	wake_up_all(&oom_ctrl->wq);
	spin_unlock(&oom_ctrl->lock);
}

void ub_oom_mm_dead(struct mm_struct *mm)
{
	printk("OOM killed process %s (pid=%d, ve=%d) exited, "
			"free=%lu.\n",
			current->comm, current->pid,
			VEID(current->ve_task_info.owner_env),
			nr_free_pages());

	if (mm->global_oom) {
		ub_release_oom_control(&global_oom_ctrl);
		if (printk_ratelimit())
			show_mem();
	}

	if (mm->ub_oom) {
		struct user_beancounter *ub = mm_ub(mm);

		ub_release_oom_control(&ub->oom_ctrl);
		if (__ratelimit(&ub->ub_ratelimit))
			show_ub_mem(ub);
	}
}

int out_of_memory_in_ub(struct user_beancounter *ub, gfp_t gfp_mask)
{
	struct task_struct *p;
	int res = 0;

	if (ub_oom_lock(&ub->oom_ctrl))
		goto out;

	read_lock(&tasklist_lock);

	do {
		p = select_bad_process(ub, NULL);
		if (PTR_ERR(p) == -1UL || !p)
			break;
	} while (oom_kill_process(p, gfp_mask, 0, NULL, ub, "Out of memory in UB"));

	read_unlock(&tasklist_lock);
	ub_oom_unlock(&ub->oom_ctrl);

	if (!p)
		res = -ENOMEM;
out:
	/*
	 * Give "p" a good chance of killing itself before we
	 * retry to allocate memory unless "p" is current
	 */
	if (!test_thread_flag(TIF_MEMDIE))
		schedule_timeout_uninterruptible(1);

	return res;
}

struct oom_control global_oom_ctrl;

void init_oom_control(struct oom_control *oom_ctrl)
{
	spin_lock_init(&oom_ctrl->lock);
	init_waitqueue_head(&oom_ctrl->wq);
}
