/*
 * linux/kernel/irq/spurious.c
 *
 * Copyright (C) 1992, 1998-2004 Linus Torvalds, Ingo Molnar
 *
 * This file contains spurious interrupt handling.
 */

#include <linux/jiffies.h>
#include <linux/irq.h>
#include <linux/log2.h>
#include <linux/module.h>
#include <linux/kallsyms.h>
#include <linux/interrupt.h>
#include <linux/moduleparam.h>

#include "internals.h"

enum {
	/* irqfixup levels */
	IRQFIXUP_SPURIOUS		= 0,		/* spurious storm detection */
	IRQFIXUP_MISROUTED		= 1,		/* misrouted IRQ fixup */
	IRQFIXUP_POLL			= 2,		/* enable polling by default */

	/* IRQ polling common parameters */
	IRQ_POLL_INTV			= HZ / 100,	/* from the good ol' 100HZ tick */

	IRQ_POLL_SLACK			= HZ / 250,	/* 1 tick slack w/ the popular 250HZ config */

	/*
	 * Spurious IRQ handling parameters.
	 *
	 * As this per-IRQ spurious handling is cheaper than the
	 * previous system wide spurious handling, it can afford to
	 * use more responsive settings but these parameters are still
	 * pretty conservative.  If ever necessary, making it more
	 * responsive shouldn't cause any problem.
	 *
	 * Spurious IRQs are monitored in segments of PERIOD_SAMPLES
	 * IRQs which can stretch PERIOD_DURATION at maximum.  If
	 * there are less than PERIOD_SAMPLES IRQs per
	 * PERIOD_DURATION, the period is considered good.
	 *
	 * If >=BAD_THRESHOLD IRQs are bad ones, the period is
	 * considered bad and spurious IRQ handling kicks in - the IRQ
	 * is disabled and polled.  The IRQ is given another shot
	 * after certain number IRQs are handled, which is at minimum
	 * POLL_CNT_MIN, increased by 1 << POLL_CNT_INC_SHIFT times
	 * after each bad period and decreased by factor of
	 * POLL_CNT_INC_DEC_SHIFT after each good one.
	 */
	IRQ_SPR_PERIOD_DURATION		= 10 * HZ,
	IRQ_SPR_PERIOD_SAMPLES		= 10000,
	IRQ_SPR_BAD_THRESHOLD		= 9900,
	IRQ_SPR_POLL_CNT_MIN		= 10000,
	IRQ_SPR_POLL_CNT_INF		= UINT_MAX,
	IRQ_SPR_POLL_CNT_INC_SHIFT	= 3,
	IRQ_SPR_POLL_CNT_DEC_SHIFT	= 1,
	IRQ_SPR_POLL_CNT_MAX_DEC_SHIFT	= BITS_PER_BYTE * sizeof(int) / 4,
};

int noirqdebug __read_mostly;
static int irqfixup __read_mostly = IRQFIXUP_SPURIOUS;

static void print_irq_handlers(struct irq_desc *desc)
{
	struct irqaction *action;

	printk(KERN_ERR "handlers:\n");

	action = desc->action;
	while (action) {
		printk(KERN_ERR "[<%p>]", action->handler);
		print_symbol(" (%s)", (unsigned long)action->handler);
		printk("\n");
		action = action->next;
	}
}

static unsigned long irq_poll_slack(unsigned long intv)
{
	return IRQ_POLL_SLACK;
}

/**
 * irq_schedule_poll - schedule IRQ poll
 * @desc: IRQ desc to schedule poll for
 * @intv: poll interval
 *
 * Schedules @desc->poll_timer.  If the timer is already scheduled,
 * it's modified iff jiffies + @intv + slack is before the timer's
 * expires.  poll_timers aren't taken offline behind this function's
 * back and the users of this function are guaranteed that poll_irq()
 * will be called at or before jiffies + @intv + slack.
 *
 * CONTEXT:
 * desc->lock
 */
static void irq_schedule_poll(struct irq_desc *desc, unsigned long intv)
{
	unsigned long expires = jiffies + intv;
	int slack = irq_poll_slack(intv);

	if (timer_pending(&desc->poll_timer) &&
	    time_before_eq(desc->poll_timer.expires, expires + slack))
		return;

	set_timer_slack(&desc->poll_timer, slack);
	mod_timer(&desc->poll_timer, expires);
}

/* start a new spurious handling period */
static void irq_spr_new_period(struct irq_spr *spr)
{
	spr->period_start = jiffies;
	spr->nr_samples = 0;
	spr->nr_bad = 0;
}

/* Reset spurious handling.  After this, poll_timer will offline itself soon. */
static void irq_spr_reset(struct irq_spr *spr)
{
	irq_spr_new_period(spr);
	spr->poll_cnt = IRQ_SPR_POLL_CNT_MIN;
	spr->poll_rem = 0;
}

/*
 * Perform an actual poll.
 */
static int try_one_irq(int irq, struct irq_desc *desc)
{
	struct irqaction *action;
	int ok = 0, work = 0;

	/* Already running on another processor */
	if (desc->status & IRQ_INPROGRESS) {
		/*
		 * Already running: If it is shared get the other
		 * CPU to go looking for our mystery interrupt too
		 */
		if (desc->action && (desc->action->flags & IRQF_SHARED))
			desc->status |= IRQ_PENDING;
		return ok;
	}
	/* Honour the normal IRQ locking */
	desc->status |= IRQ_INPROGRESS;
	action = desc->action;
	raw_spin_unlock(&desc->lock);

	while (action) {
		/* Only shared IRQ handlers are safe to call */
		if (action->flags & IRQF_SHARED) {
			if (action->handler(irq, action->dev_id) ==
				IRQ_HANDLED)
				ok = 1;
		}
		action = action->next;
	}
	local_irq_disable();
	/* Now clean up the flags */
	raw_spin_lock(&desc->lock);
	action = desc->action;

	/*
	 * While we were looking for a fixup someone queued a real
	 * IRQ clashing with our walk:
	 */
	while ((desc->status & IRQ_PENDING) && action) {
		/*
		 * Perform real IRQ processing for the IRQ we deferred
		 */
		work = 1;
		raw_spin_unlock(&desc->lock);
		handle_IRQ_event(irq, action);
		raw_spin_lock(&desc->lock);
		desc->status &= ~IRQ_PENDING;
	}
	desc->status &= ~IRQ_INPROGRESS;
	/*
	 * If we did actual work for the real IRQ line we must let the
	 * IRQ controller clean up too
	 */
	if (work && desc->chip && desc->chip->end)
		desc->chip->end(irq);

	return ok;
}

static int misrouted_irq(int irq)
{
	struct irq_desc *desc;
	int i, ok = 0;

	for_each_irq_desc(i, desc) {
		if (!i)
			 continue;

		if (i == irq)	/* Already tried */
			continue;

		raw_spin_lock(&desc->lock);
		if (try_one_irq(i, desc))
			ok = 1;
		raw_spin_unlock(&desc->lock);
	}
	/* So the caller can adjust the irq error counts */
	return ok;
}

/*
 * IRQ delivery notification function.  Called after each IRQ delivery.
 */
void __note_interrupt(unsigned int irq, struct irq_desc *desc,
		      irqreturn_t action_ret)
{
	struct irq_spr *spr = &desc->spr;
	unsigned long dur;
	unsigned int cnt, abbr;
	char unit = 'k';

	/*
	 * Account for unhandled interrupt.  We don't care whether
	 * spurious accounting update races with irq open/close and
	 * gets some values wrong.  Do it w/o locking.
	 */
	if (unlikely(action_ret != IRQ_HANDLED)) {
		static int bogus_count = 100;

		spr->last_bad = jiffies - INITIAL_JIFFIES;
		spr->nr_bad++;
		if (likely(action_ret == IRQ_NONE)) {
			if (unlikely(irqfixup >= IRQFIXUP_MISROUTED &&
				     misrouted_irq(irq)))
				spr->nr_bad--;
		} else if (bogus_count > 0) {
			bogus_count--;
			printk(KERN_ERR "IRQ %u: bogus return value %x\n",
			       irq, action_ret);
			dump_stack();
			print_irq_handlers(desc);
		}
	}

	/* did we finish this spurious period? */
	spr->nr_samples++;
	if (likely(spr->nr_samples < IRQ_SPR_PERIOD_SAMPLES))
		return;

	/* if so, was it a good one? */
	dur = jiffies - spr->period_start;
	if (likely(spr->nr_bad < IRQ_SPR_BAD_THRESHOLD ||
		   dur > IRQ_SPR_PERIOD_DURATION)) {
		/*
		 * If longer than PERIOD_DURATION has passed, consider
		 * multiple good periods have happened.
		 */
		int sft = IRQ_SPR_POLL_CNT_DEC_SHIFT *
			(dur >> order_base_2(IRQ_SPR_PERIOD_DURATION));

		/* but don't kill poll_cnt at once */
		sft = clamp(sft, 1, IRQ_SPR_POLL_CNT_MAX_DEC_SHIFT);

		spr->poll_cnt >>= sft;
		irq_spr_new_period(spr);
		return;
	}

	/*
	 * It was a bad one, start polling.  This is a slow path and
	 * we're gonna be changing states which require proper
	 * synchronization, grab desc->lock.
	 */
	raw_spin_lock(&desc->lock);

	irq_spr_new_period(spr);

	/* update spr_poll_cnt considering the lower and upper bounds */
	cnt = max_t(unsigned int, spr->poll_cnt, IRQ_SPR_POLL_CNT_MIN);
	spr->poll_cnt = cnt << IRQ_SPR_POLL_CNT_INC_SHIFT;
	if (spr->poll_cnt < cnt)	/* did it overflow? */
		spr->poll_cnt = IRQ_SPR_POLL_CNT_INF;

	/* whine, plug IRQ and kick poll timer */
	abbr = cnt / 1000;
	if (abbr > 1000) {
		abbr /= 1000;
		unit = 'm';
	}
	printk(KERN_ERR "IRQ %u: too many spurious IRQs, disabling and "
	       "polling for %u%c %umsec intervals.\n",
	       desc->irq, abbr, unit, jiffies_to_msecs(IRQ_POLL_INTV));
	printk(KERN_ERR "IRQ %u: system performance may be affected\n",
	       desc->irq);
	print_irq_handlers(desc);

	desc->status |= IRQ_DISABLED | IRQ_SPURIOUS_DISABLED;
	desc->depth++;
	desc->chip->disable(desc->irq);

	spr->poll_rem = cnt;
	irq_schedule_poll(desc, IRQ_POLL_INTV);

	raw_spin_unlock(&desc->lock);
}

/*
 * IRQ poller.  Called from desc->poll_timer.
 */
void poll_irq(unsigned long arg)
{
	struct irq_desc *desc = (void *)arg;
	struct irq_spr *spr = &desc->spr;
	unsigned long intv = MAX_JIFFY_OFFSET;
	bool reenable_irq = false;

	raw_spin_lock_irq(&desc->lock);

	/* poll the IRQ */
	try_one_irq(desc->irq, desc);

	/* take care of spurious handling */
	if (spr->poll_rem) {
		if (spr->poll_rem != IRQ_SPR_POLL_CNT_INF)
			spr->poll_rem--;
		if (spr->poll_rem)
			intv = IRQ_POLL_INTV;
		else
			irq_spr_new_period(spr);
	}
	if (!spr->poll_rem)
		reenable_irq = desc->status & IRQ_SPURIOUS_DISABLED;

	/* need to poll again? */
	if (intv < MAX_JIFFY_OFFSET)
		irq_schedule_poll(desc, intv);

	raw_spin_unlock_irq(&desc->lock);

	if (!reenable_irq)
		return;

	/* need to do locking dance for chip_bus_lock() to reenable IRQ */
	chip_bus_lock(desc->irq, desc);
	raw_spin_lock_irq(&desc->lock);

	/* make sure we haven't raced with anyone inbetween */
	if (!spr->poll_rem && (desc->status & IRQ_SPURIOUS_DISABLED)) {
		printk(KERN_INFO "IRQ %u: spurious polling finished, "
		       "reenabling IRQ\n", desc->irq);
		__enable_irq(desc, desc->irq, false);
		desc->status &= ~IRQ_SPURIOUS_DISABLED;
	}

	raw_spin_unlock_irq(&desc->lock);
	chip_bus_sync_unlock(desc->irq, desc);
}

void irq_poll_action_added(struct irq_desc *desc, struct irqaction *action)
{
	struct irq_spr *spr = &desc->spr;
	unsigned long flags;

	raw_spin_lock_irqsave(&desc->lock, flags);

	if ((action->flags & IRQF_SHARED) && irqfixup >= IRQFIXUP_POLL) {
		if (!spr->poll_rem)
			printk(KERN_INFO "IRQ %u: starting IRQFIXUP_POLL\n",
			       desc->irq);
		spr->poll_rem = IRQ_SPR_POLL_CNT_INF;
		irq_schedule_poll(desc, IRQ_POLL_INTV);
	} else {
		/* new irqaction registered, give the IRQ another chance */
		irq_spr_reset(spr);
	}

	raw_spin_unlock_irqrestore(&desc->lock, flags);
}

void irq_poll_action_removed(struct irq_desc *desc, struct irqaction *action)
{
	bool irq_enabled = false, timer_killed = false;
	unsigned long flags;
	int rc;

	raw_spin_lock_irqsave(&desc->lock, flags);

	/* give the IRQ another chance */
	if (irqfixup < IRQFIXUP_POLL)
		irq_spr_reset(&desc->spr);

	/*
	 * Make sure the timer is offline if no irqaction is left as
	 * the irq_desc will be reinitialized when the next irqaction
	 * is added; otherwise, the timer can be left alone.  It will
	 * offline itself if no longer necessary.
	 */
	while (!desc->action) {
		rc = try_to_del_timer_sync(&desc->poll_timer);
		if (rc >= 0) {
			timer_killed = rc > 0;
			break;
		}
		raw_spin_unlock_irqrestore(&desc->lock, flags);
		cpu_relax();
		raw_spin_lock_irqsave(&desc->lock, flags);
	}

	/*
	 * If the timer was forcefully shut down, it might not have
	 * had the chance to reenable IRQ.  Make sure it's enabled.
	 */
	if (timer_killed && (desc->status & IRQ_SPURIOUS_DISABLED)) {
		__enable_irq(desc, desc->irq, false);
		desc->status &= ~IRQ_SPURIOUS_DISABLED;
		irq_enabled = true;
	}

	if (timer_killed || irq_enabled)
		printk(KERN_INFO "IRQ %u:%s%s%s\n", desc->irq,
		       timer_killed ? " polling stopped" : "",
		       timer_killed && irq_enabled ? " and" : "",
		       irq_enabled ? " IRQ reenabled" : "");

	raw_spin_unlock_irqrestore(&desc->lock, flags);
}

int noirqdebug_setup(char *str)
{
	noirqdebug = 1;
	printk(KERN_INFO "IRQ lockup detection disabled\n");

	return 1;
}

__setup("noirqdebug", noirqdebug_setup);
module_param(noirqdebug, bool, 0644);
MODULE_PARM_DESC(noirqdebug, "Disable irq lockup detection when true");

static int __init irqfixup_setup(char *str)
{
	irqfixup = max(irqfixup, IRQFIXUP_MISROUTED);
	printk(KERN_WARNING "Misrouted IRQ fixup support enabled.\n");
	printk(KERN_WARNING "This may impact system performance.\n");

	return 1;
}

__setup("irqfixup", irqfixup_setup);
module_param(irqfixup, int, 0644);

static int __init irqpoll_setup(char *str)
{
	irqfixup = IRQFIXUP_POLL;
	printk(KERN_WARNING "Misrouted IRQ fixup and polling support "
				"enabled\n");
	printk(KERN_WARNING "This may significantly impact system "
				"performance\n");
	return 1;
}

__setup("irqpoll", irqpoll_setup);
