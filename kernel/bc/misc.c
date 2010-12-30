/*
 *  kernel/bc/misc.c
 *
 *  Copyright (C) 2005  SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 */

#include <linux/tty.h>
#include <linux/tty_driver.h>
#include <linux/signal.h>
#include <linux/slab.h>
#include <linux/fs.h>
#include <linux/file.h>
#include <linux/sched.h>
#include <linux/module.h>

#include <bc/beancounter.h>
#include <bc/kmem.h>
#include <bc/proc.h>

/*
 * Task staff
 */

static void init_task_sub(struct task_struct *parent,
		struct task_struct *tsk,
  		struct task_beancounter *old_bc)
{
	struct task_beancounter *new_bc;
	struct user_beancounter *sub;

	new_bc = &tsk->task_bc;
	sub = old_bc->fork_sub;
	new_bc->fork_sub = get_beancounter(sub);
}

int ub_task_charge(struct task_struct *parent, struct task_struct *task)
{
	struct task_beancounter *old_bc;
	struct task_beancounter *new_bc;
	struct user_beancounter *ub;

	old_bc = &parent->task_bc;
	ub = old_bc->fork_sub;

	if (charge_beancounter_fast(ub, UB_NUMPROC, 1, UB_HARD) < 0)
		return -ENOMEM;

	new_bc = &task->task_bc;
	new_bc->task_ub = get_beancounter(ub);
	new_bc->exec_ub = get_beancounter(ub);
	init_task_sub(parent, task, old_bc);

	return 0;
}

extern atomic_t dbgpre;

void ub_task_uncharge(struct task_struct *task)
{
	uncharge_beancounter_fast(task->task_bc.task_ub, UB_NUMPROC, 1);
}

void ub_task_put(struct task_struct *task)
{
	struct task_beancounter *task_bc;

	task_bc = &task->task_bc;

	put_beancounter(task_bc->exec_ub);
	put_beancounter(task_bc->task_ub);
	put_beancounter(task_bc->fork_sub);

	task_bc->exec_ub = (struct user_beancounter *)0xdeadbcbc;
	task_bc->task_ub = (struct user_beancounter *)0xdead100c;
}

int ub_file_charge(struct file *f)
{
	struct user_beancounter *ub = get_exec_ub();
	int err;

	err = charge_beancounter_fast(ub, UB_NUMFILE, 1, UB_HARD);
	if (unlikely(err))
		goto no_file;

	err = charge_beancounter_fast(ub, UB_KMEMSIZE,
			CHARGE_SIZE(kmem_cache_objuse(filp_cachep)), UB_HARD);
	if (unlikely(err))
		goto no_kmem;

	f->f_ub = get_beancounter(ub);

	return 0;

no_kmem:
	uncharge_beancounter_fast(ub, UB_NUMFILE, 1);
no_file:
	return err;
}

void ub_file_uncharge(struct file *f)
{
	struct user_beancounter *ub = f->f_ub;

	uncharge_beancounter_fast(ub, UB_KMEMSIZE,
			CHARGE_SIZE(kmem_cache_objuse(filp_cachep)));
	uncharge_beancounter_fast(ub, UB_NUMFILE, 1);
	put_beancounter(ub);
}

int ub_flock_charge(struct file_lock *fl, int hard)
{
	struct user_beancounter *ub;
	int err;

	/* No need to get_beancounter here since it's already got in slab */
	ub = slab_ub(fl);
	if (ub == NULL)
		return 0;

	err = charge_beancounter(ub, UB_NUMFLOCK, 1, hard ? UB_HARD : UB_SOFT);
	if (!err)
		fl->fl_charged = 1;
	return err;
}

void ub_flock_uncharge(struct file_lock *fl)
{
	struct user_beancounter *ub;

	/* Ub will be put in slab */
	ub = slab_ub(fl);
	if (ub == NULL || !fl->fl_charged)
		return;

	uncharge_beancounter(ub, UB_NUMFLOCK, 1);
	fl->fl_charged = 0;
}

/*
 * Signal handling
 */

int ub_siginfo_charge(struct sigqueue *sq, struct user_beancounter *ub)
{
	unsigned long size;

	size = CHARGE_SIZE(kmem_obj_objuse(sq));
	if (charge_beancounter_fast(ub, UB_KMEMSIZE, size, UB_HARD))
		goto out_kmem;

	if (charge_beancounter_fast(ub, UB_NUMSIGINFO, 1, UB_HARD))
		goto out_num;

	sq->sig_ub = get_beancounter(ub);
	return 0;

out_num:
	uncharge_beancounter_fast(ub, UB_KMEMSIZE, size);
out_kmem:
	return -ENOMEM;
}
EXPORT_SYMBOL(ub_siginfo_charge);

void ub_siginfo_uncharge(struct sigqueue *sq)
{
	unsigned long size;
	struct user_beancounter *ub;

	ub = sq->sig_ub;
	sq->sig_ub = NULL;
	size = CHARGE_SIZE(kmem_obj_objuse(sq));
	uncharge_beancounter_fast(ub, UB_NUMSIGINFO, 1);
	uncharge_beancounter_fast(ub, UB_KMEMSIZE, size);
	put_beancounter(ub);
}

/*
 * PTYs
 */

int ub_pty_charge(struct tty_struct *tty)
{
	struct user_beancounter *ub;
	int retval;

	ub = slab_ub(tty);
	retval = 0;
	if (ub && tty->driver->subtype == PTY_TYPE_MASTER &&
			!test_bit(TTY_CHARGED, &tty->flags)) {
		retval = charge_beancounter(ub, UB_NUMPTY, 1, UB_HARD);
		if (!retval)
			set_bit(TTY_CHARGED, &tty->flags);
	}
	return retval;
}

void ub_pty_uncharge(struct tty_struct *tty)
{
	struct user_beancounter *ub;

	ub = slab_ub(tty);
	if (ub && tty->driver->subtype == PTY_TYPE_MASTER &&
			test_bit(TTY_CHARGED, &tty->flags)) {
		uncharge_beancounter(ub, UB_NUMPTY, 1);
		clear_bit(TTY_CHARGED, &tty->flags);
	}
}
