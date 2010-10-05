/*
 * linux/kernel/irq/spurious.c
 *
 * Copyright (C) 1992, 1998-2004 Linus Torvalds, Ingo Molnar
 * Copyright (C) 2010            SUSE Linux Products GmbH
 * Copyright (C) 2010            Tejun Heo <tj@kernel.org>
 *
 * There are two ways interrupt handling can go wrong - too few or too
 * many.  Due to misrouting or other issues, sometimes IRQs don't
 * reach the driver while at other times an interrupt line gets stuck
 * and a continuous spurious interrupts are generated.
 *
 * This file implements workaround for both cases.  Lost interrupts
 * are handled by IRQ expecting and watching, and spurious interrupts
 * by spurious polling.  All mechanisms need IRQF_SHARED to be set on
 * the irqaction in question.
 *
 * Both lost interrupt workarounds require cooperation from drivers
 * and can be chosen depending on how much information the driver can
 * provide.
 *
 * - IRQ expecting
 *
 *   IRQ expecting is useful when the driver can tell when IRQs can be
 *   expected; in other words, when IRQs are used to signal completion
 *   of host initiated operations.  This is the surest way to work
 *   around lost interrupts.
 *
 *   When the controller is expected to raise an IRQ, the driver
 *   should call expect_irq() and, when the expected event happens or
 *   times out, unexpect_irq().  IRQ subsystem polls the interrupt
 *   inbetween.
 *
 *   As interrupts tend to keep working if it works at the beginning,
 *   IRQ expecting implements "verified state".  After certain number
 *   of successful IRQ deliveries, the irqaction becomes verified and
 *   much longer polling interval is used.
 *
 * - IRQ watching
 *
 *   This can be used when the driver doesn't know when to exactly
 *   expect and unexpect IRQs.  Once watch_irq() is called, the
 *   irqaction is slowly polled for certain amount of time (1min).  If
 *   IRQs are missed during that time, the irqaction is marked and
 *   actively polled; otherwise, the watching is stopped.
 *
 *   In the most basic case, drivers can call this right after
 *   registering an irqaction to verify IRQ delivery.  In many cases,
 *   if IRQ works at the beginning, it keeps working, so just calling
 *   watch_irq() once can provide decent protection against misrouted
 *   IRQs.  It would also be a good idea to call watch_irq() when
 *   timeouts are detected.
 *
 * - Spurious IRQ handling
 *
 *   All IRQs are continuously monitored and spurious IRQ handling
 *   kicks in if there are too many spurious IRQs.  The IRQ is
 *   disabled and the registered irqactions are polled.  The IRQ is
 *   given another shot after certain number IRQs are handled or an
 *   irqaction is added or removed.
 *
 * All of the above three mechanisms can be used together.  Spurious
 * IRQ handling is enabled by default and drivers are free to expect
 * and watch IRQs as they see fit.
 */

#include <linux/jiffies.h>
#include <linux/irq.h>
#include <linux/log2.h>
#include <linux/module.h>
#include <linux/kallsyms.h>
#include <linux/interrupt.h>
#include <linux/moduleparam.h>
#include <linux/slab.h>

#include "internals.h"

/*
 * I spent quite some time thinking about each parameter but they
 * still are just numbers pulled out of my ass.  If you think your ass
 * is prettier than mine, please go ahead and suggest better ones.
 *
 * Most parameters are intentionally fixed constants and not
 * adjustable through API.  The nature of IRQ delivery failures isn't
 * usually dependent on specific drivers and the timing parameters are
 * more about human perceivable latencies rather than any specific
 * controller timing details, so figuring out constant values which
 * can work for most cases shouldn't be too hard.  This allows tighter
 * control over polling behaviors, eases future changes and makes the
 * interface easy for drivers.
 */
enum {
	/* irqfixup levels */
	IRQFIXUP_SPURIOUS		= 0,		/* spurious storm detection */
	IRQFIXUP_MISROUTED		= 1,		/* misrouted IRQ fixup */
	IRQFIXUP_POLL			= 2,		/* enable polling by default */

	/* IRQ polling common parameters */
	IRQ_POLL_SLOW_INTV		= 3 * HZ,	/* not too slow for ppl, slow enough for machine */
	IRQ_POLL_INTV			= HZ / 100,	/* from the good ol' 100HZ tick */
	IRQ_POLL_QUICK_INTV		= HZ / 1000,	/* on every tick, basically */

	IRQ_POLL_SLOW_SLACK		= HZ,
	IRQ_POLL_SLACK			= HZ / 250,	/* 1 tick slack w/ the popular 250HZ config */
	IRQ_POLL_QUICK_SLACK		= HZ / 10000,	/* no slack, basically */

	/*
	 * IRQ expect parameters.
	 *
	 * Because IRQ expecting is tightly coupled with the actual
	 * activity of the controller, we can be slightly aggressive
	 * and try to minimize the effect of lost interrupts.
	 *
	 * An irqaction must accumulate VERIFY_GOAL good deliveries,
	 * where one bad delivery (delivered by polling) costs
	 * BAD_FACTOR good ones, before reaching the verified state.
	 *
	 * QUICK_SAMPLES IRQ deliveries are examined and if
	 * >=QUICK_THRESHOLD of them are polled on the first poll, the
	 * IRQ is considered to be quick and QUICK_INTV is used
	 * instead.
	 *
	 * Keep QUICK_SAMPLES much higher than VERIFY_GOAL so that
	 * quick polling doesn't interfact with the initial
	 * verification attempt (quicker polling increases the chance
	 * of polled deliveries).
	 */
	IRQ_EXP_BAD_FACTOR		= 10,
	IRQ_EXP_VERIFY_GOAL		= 256,
	IRQ_EXP_QUICK_SAMPLES		= IRQ_EXP_VERIFY_GOAL * 4,
	IRQ_EXP_QUICK_THRESHOLD		= IRQ_EXP_QUICK_SAMPLES * 8 / 10,

	/* IRQ expect flags */
	IRQ_EXPECTING			= (1 << 0),	/* expecting in progress */
	IRQ_EXP_VERIFIED		= (1 << 1),	/* delivery verified, use slow interval */
	IRQ_EXP_QUICK			= (1 << 2),	/* quick polling enabled */
	IRQ_EXP_WARNED			= (1 << 3),	/* already whined */

	/*
	 * IRQ watch parameters.
	 *
	 * As IRQ watching has much less information about what's
	 * going on, the parameters are more conservative.  It will
	 * terminate unless it can reliably determine that IRQ
	 * delivery isn't working.
	 *
	 * IRQs are watched in timed intervals which is BASE_PERIOD
	 * long by default.  Polling interval starts at BASE_INTV and
	 * grows upto SLOW_INTV if no bad delivery is detected.
	 *
	 * If a period contains zero sample and no bad delivery was
	 * seen since watch started, watch terminates.
	 *
	 * If a period contains >=1 but <MIN_SAMPLES deliveries,
	 * collected samples are inherited to the next period.
	 *
	 * If it contains enough samples, the ratio between good and
	 * bad deliveries are examined, if >=BAD_PCT% are bad, the
	 * irqaction is tagged bad and watched indefinitely.  if
	 * BAD_PCT% > nr_bad >= WARY_PCT%, WARY_PERIOD is used instead
	 * of BASE_PERIOD and the whole process is restarted.  If
	 * <WARY_PCT% are bad, watch terminates.
	 */
	IRQ_WAT_MIN_SAMPLES		= 10,
	IRQ_WAT_BASE_INTV		= HZ / 2,
	IRQ_WAT_BASE_PERIOD		= 60 * HZ,
	IRQ_WAT_WARY_PERIOD		= 600 * HZ,
	IRQ_WAT_WARY_PCT		= 1,
	IRQ_WAT_BAD_PCT			= 10,

	/* IRQ watch flags */
	IRQ_WATCHING			= (1 << 0),
	IRQ_WAT_POLLED			= (1 << 1),
	IRQ_WAT_WARY			= (1 << 2),
	IRQ_WAT_BAD			= (1 << 3),

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

struct irq_expect {
	struct irq_expect	*next;
	struct irq_desc		*desc;		/* the associated IRQ desc */
	struct irqaction	*act;		/* the associated IRQ action */

	unsigned int		flags;		/* IRQ_EXP_* flags */
	unsigned int		nr_samples;	/* nr of collected samples in this period */
	unsigned int		nr_quick;	/* nr of polls completed after single attempt */
	unsigned int		nr_good;	/* nr of good IRQ deliveries */
	unsigned long		started;	/* when this period started */
};

int noirqdebug __read_mostly;
static int irqfixup __read_mostly = IRQFIXUP_SPURIOUS;

static struct irqaction *find_irq_action(struct irq_desc *desc, void *dev_id)
{
	struct irqaction *act;

	for (act = desc->action; act; act = act->next)
		if (act->dev_id == dev_id)
			return act;
	return NULL;
}

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

static void warn_irq_poll(struct irq_desc *desc, struct irqaction *act)
{
	if (desc->poll_warned)
		return;

	desc->poll_warned = true;

	printk(KERN_WARNING "IRQ %u: %s: can't verify IRQ, will keep polling\n",
	       desc->irq_data.irq, act->name);
	printk(KERN_WARNING "IRQ %u: %s: system performance may be affected\n",
	       desc->irq_data.irq, act->name);
}

static unsigned long irq_poll_slack(unsigned long intv)
{
	if (intv >= IRQ_POLL_SLOW_INTV)
		return IRQ_POLL_SLOW_SLACK;
	else if (intv >= IRQ_POLL_INTV)
		return IRQ_POLL_SLACK;
	else
		return IRQ_POLL_QUICK_SLACK;
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

static unsigned long irq_exp_intv(struct irq_expect *exp)
{
	if (!(exp->flags & IRQ_EXPECTING))
		return MAX_JIFFY_OFFSET;
	if (exp->flags & IRQ_EXP_VERIFIED)
		return IRQ_POLL_SLOW_INTV;
	if (exp->flags & IRQ_EXP_QUICK)
		return IRQ_POLL_QUICK_INTV;
	return IRQ_POLL_INTV;
}

/**
 * init_irq_expect - initialize IRQ expecting
 * @irq: IRQ to expect
 * @dev_id: dev_id of the irqaction to expect
 *
 * Initializes IRQ expecting and returns expect token to use.  This
 * function can be called multiple times for the same irqaction and
 * each token can be used independently.
 *
 * CONTEXT:
 * Does GFP_KERNEL allocation.
 *
 * RETURNS:
 * irq_expect token to use on success, %NULL on failure.
 */
struct irq_expect *init_irq_expect(unsigned int irq, void *dev_id)
{
	struct irq_desc *desc = irq_to_desc(irq);
	struct irqaction *act;
	struct irq_expect *exp;
	unsigned long flags;

	if (noirqdebug || WARN_ON_ONCE(!desc))
		return NULL;

	exp = kzalloc(sizeof(*exp), GFP_KERNEL);
	if (!exp) {
		printk(KERN_WARNING "IRQ %u: failed to initialize IRQ expect, "
		       "allocation failed\n", irq);
		return NULL;
	}

	exp->desc = desc;

	raw_spin_lock_irqsave(&desc->lock, flags);

	act = find_irq_action(desc, dev_id);
	if (!WARN_ON_ONCE(!act)) {
		exp->act = act;
		exp->next = act->expects;
		act->expects = exp;
	} else {
		kfree(exp);
		exp = NULL;
	}

	raw_spin_unlock_irqrestore(&desc->lock, flags);

	return exp;
}
EXPORT_SYMBOL_GPL(init_irq_expect);

/**
 * expect_irq - expect IRQ
 * @exp: expect token acquired from init_irq_expect(), %NULL is allowed
 *
 * Tell IRQ subsystem to expect an IRQ.  The IRQ might be polled until
 * unexpect_irq() is called on @exp.  If @exp is %NULL, this function
 * becomes noop.
 *
 * This function is fairly cheap and drivers can call it for each
 * interrupt driven operation without adding noticeable overhead in
 * most cases.
 *
 * CONTEXT:
 * Don't care.  The caller is responsible for ensuring
 * [un]expect_irq() calls don't overlap.  Overlapping may lead to
 * unexpected polling behaviors but won't directly cause a failure.
 */
void expect_irq(struct irq_expect *exp)
{
	struct irq_desc *desc;
	unsigned long intv, deadline;
	unsigned long flags;

	/* @exp is NULL if noirqdebug */
	if (unlikely(!exp))
		return;

	desc = exp->desc;
	exp->flags |= IRQ_EXPECTING;

	/*
	 * Paired with mb in poll_irq().  Either we see timer pending
	 * cleared or poll_irq() sees IRQ_EXPECTING.
	 */
	smp_mb();

	exp->started = jiffies;
	intv = irq_exp_intv(exp);
	deadline = exp->started + intv + irq_poll_slack(intv);

	/*
	 * poll_timer is never explicitly killed unless there's no
	 * action left on the irq; also, while it's online, timer
	 * duration is only shortened, which means that if we see
	 * ->expires in the future and not later than our deadline,
	 * the timer is guaranteed to fire before it.
	 */
	if (!timer_pending(&desc->poll_timer) ||
	    time_after_eq(jiffies, desc->poll_timer.expires) ||
	    time_before(deadline, desc->poll_timer.expires)) {
		raw_spin_lock_irqsave(&desc->lock, flags);
		irq_schedule_poll(desc, intv);
		raw_spin_unlock_irqrestore(&desc->lock, flags);
	}
}
EXPORT_SYMBOL_GPL(expect_irq);

/**
 * unexpect_irq - unexpect IRQ
 * @exp: expect token acquired from init_irq_expect(), %NULL is allowed
 * @timedout: did the IRQ timeout?
 *
 * Tell IRQ subsystem to stop expecting an IRQ.  Set @timedout to
 * %true if the expected IRQ never arrived.  If @exp is %NULL, this
 * function becomes noop.
 *
 * This function is fairly cheap and drivers can call it for each
 * interrupt driven operation without adding noticeable overhead in
 * most cases.
 *
 * CONTEXT:
 * Don't care.  The caller is responsible for ensuring
 * [un]expect_irq() calls don't overlap.  Overlapping may lead to
 * unexpected polling behaviors but won't directly cause a failure.
 */
void unexpect_irq(struct irq_expect *exp, bool timedout)
{
	struct irq_desc *desc;

	/* @exp is NULL if noirqdebug */
	if (unlikely(!exp) || (!(exp->flags & IRQ_EXPECTING) && !timedout))
		return;

	desc = exp->desc;
	exp->flags &= ~IRQ_EXPECTING;

	/* succesful completion from IRQ? */
	if (likely(!(desc->status & IRQ_IN_POLLING) && !timedout)) {
		/*
		 * IRQ seems a bit more trustworthy.  Allow nr_good to
		 * increase till VERIFY_GOAL + BAD_FACTOR - 1 so that
		 * single succesful delivery can recover verified
		 * state after an accidental polling hit.
		 */
		if (unlikely(exp->nr_good <
			     IRQ_EXP_VERIFY_GOAL + IRQ_EXP_BAD_FACTOR - 1) &&
		    ++exp->nr_good >= IRQ_EXP_VERIFY_GOAL) {
			exp->flags |= IRQ_EXP_VERIFIED;
			exp->nr_samples = 0;
			exp->nr_quick = 0;
		}
		return;
	}

	/* timedout or polled */
	if (timedout) {
		exp->nr_good = 0;
	} else {
		exp->nr_good -= min_t(unsigned int,
				      exp->nr_good, IRQ_EXP_BAD_FACTOR);

		if (time_before_eq(jiffies, exp->started + IRQ_POLL_INTV))
			exp->nr_quick++;

		if (++exp->nr_samples >= IRQ_EXP_QUICK_SAMPLES) {
			/*
			 * Use quick sampling checkpoints as warning
			 * checkpoints too.
			 */
			if (!(exp->flags & IRQ_EXP_WARNED) &&
			    !desc->spr.poll_rem) {
				warn_irq_poll(desc, exp->act);
				exp->flags |= IRQ_EXP_WARNED;
			}

			exp->flags &= ~IRQ_EXP_QUICK;
			if (exp->nr_quick >= IRQ_EXP_QUICK_THRESHOLD)
				exp->flags |= IRQ_EXP_QUICK;
			exp->nr_samples = 0;
			exp->nr_quick = 0;
		}
	}

	exp->flags &= ~IRQ_EXP_VERIFIED;
}
EXPORT_SYMBOL_GPL(unexpect_irq);

/**
 * irq_update_watch - IRQ handled, update watch state
 * @desc: IRQ desc of interest
 * @act: IRQ action of interest
 * @via_poll: IRQ was handled via poll
 *
 * Called after IRQ is successfully delievered or polled.  Updates
 * watch state accordingly and determines which watch interval to use.
 *
 * CONTEXT:
 * desc->lock
 *
 * RETURNS:
 * Watch poll interval to use, MAX_JIFFY_OFFSET if watch polling isn't
 * necessary.
 */
static unsigned long irq_update_watch(struct irq_desc *desc,
				      struct irqaction *act, bool via_poll)
{
	struct irq_watch *wat = &act->watch;
	unsigned long period = wat->flags & IRQ_WAT_WARY ?
		IRQ_WAT_WARY_PERIOD : IRQ_WAT_BASE_PERIOD;

	/* if not watching or already determined to be bad, it's easy */
	if (!(wat->flags & IRQ_WATCHING))
		return MAX_JIFFY_OFFSET;
	if (wat->flags & IRQ_WAT_BAD)
		return IRQ_POLL_INTV;

	/* don't expire watch period while spurious polling is in effect */
	if (desc->spr.poll_rem) {
		wat->started = jiffies;
		return IRQ_POLL_INTV;
	}

	/* IRQ was handled, record whether it was a good or bad delivery */
	if (wat->last_ret == IRQ_HANDLED) {
		wat->nr_samples++;
		if (via_poll) {
			wat->nr_polled++;
			wat->flags |= IRQ_WAT_POLLED;
		}
	}

	/* is this watch period over? */
	if (time_after(jiffies, wat->started + period)) {
		unsigned int wry_thr = wat->nr_samples * IRQ_WAT_WARY_PCT / 100;
		unsigned int bad_thr = wat->nr_samples * IRQ_WAT_BAD_PCT / 100;

		if (wat->nr_samples >= IRQ_WAT_MIN_SAMPLES) {
			/* have enough samples, determine what to do */
			if (wat->nr_polled <= wry_thr)
				wat->flags &= ~IRQ_WATCHING;
			else if (wat->nr_polled <= bad_thr)
				wat->flags |= IRQ_WAT_WARY;
			else {
				warn_irq_poll(desc, act);
				wat->flags |= IRQ_WAT_BAD;
			}
			wat->nr_samples = 0;
			wat->nr_polled = 0;
		} else if (!wat->nr_samples || !(wat->flags & IRQ_WAT_POLLED)) {
			/* not sure but let's not hold onto it */
			wat->flags &= ~IRQ_WATCHING;
		}

		wat->started = jiffies;
	}

	if (!(wat->flags & IRQ_WATCHING))
		return MAX_JIFFY_OFFSET;
	if (wat->flags & IRQ_WAT_POLLED)
		return IRQ_POLL_INTV;
	/* every delivery upto this point has been successful, grow interval */
	return clamp_t(unsigned long, jiffies - wat->started,
		       IRQ_WAT_BASE_INTV, IRQ_POLL_SLOW_INTV);
}

/**
 * watch_irq - watch an irqaction
 * @irq: IRQ the irqaction to watch belongs to
 * @dev_id: dev_id for the irqaction to watch
 *
 * LOCKING:
 * Grabs and releases desc->lock.
 */
void watch_irq(unsigned int irq, void *dev_id)
{
	struct irq_desc *desc = irq_to_desc(irq);
	struct irqaction *act;
	unsigned long flags;

	if (WARN_ON_ONCE(!desc))
		return;

	raw_spin_lock_irqsave(&desc->lock, flags);

	act = find_irq_action(desc, dev_id);
	if (!WARN_ON_ONCE(!act)) {
		struct irq_watch *wat = &act->watch;

		wat->flags |= IRQ_WATCHING;
		wat->started = jiffies;
		wat->nr_samples = 0;
		wat->nr_polled = 0;
		desc->status |= IRQ_CHECK_WATCHES;
		irq_schedule_poll(desc, IRQ_WAT_BASE_INTV);
	}

	raw_spin_unlock_irqrestore(&desc->lock, flags);
}
EXPORT_SYMBOL_GPL(watch_irq);

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
			action->watch.last_ret =
				action->handler(irq, action->dev_id);
			if (action->watch.last_ret == IRQ_HANDLED)
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
	if (work)
		irq_end(irq, desc);

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

	/* first, take care of IRQ watches */
	if (unlikely(desc->status & IRQ_CHECK_WATCHES)) {
		unsigned long intv = MAX_JIFFY_OFFSET;
		struct irqaction *act;

		raw_spin_lock(&desc->lock);

		for (act = desc->action; act; act = act->next)
			intv = min(intv, irq_update_watch(desc, act, false));

		if (intv < MAX_JIFFY_OFFSET)
			irq_schedule_poll(desc, intv);
		else
			desc->status &= ~IRQ_CHECK_WATCHES;

		raw_spin_unlock(&desc->lock);
	}

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
	       desc->irq_data.irq, abbr, unit, jiffies_to_msecs(IRQ_POLL_INTV));
	printk(KERN_ERR "IRQ %u: system performance may be affected\n",
	       desc->irq_data.irq);
	print_irq_handlers(desc);

	desc->status |= IRQ_DISABLED | IRQ_SPURIOUS_DISABLED;
	desc->depth++;
	desc->irq_data.chip->irq_disable(&desc->irq_data);

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
	struct irqaction *act;
	struct irq_expect *exp;

	raw_spin_lock_irq(&desc->lock);

	/* poll the IRQ */
	desc->status |= IRQ_IN_POLLING;
	try_one_irq(desc->irq_data.irq, desc);
	desc->status &= ~IRQ_IN_POLLING;

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

	/*
	 * Paired with mb in expect_irq() so that either they see
	 * timer pending cleared or irq_exp_intv() below sees
	 * IRQ_EXPECTING.
	 */
	smp_mb();

	/* take care of expects and watches */
	for (act = desc->action; act; act = act->next) {
		intv = min(irq_update_watch(desc, act, true), intv);
		for (exp = act->expects; exp; exp = exp->next)
			intv = min(irq_exp_intv(exp), intv);
	}

	/* need to poll again? */
	if (intv < MAX_JIFFY_OFFSET)
		irq_schedule_poll(desc, intv);

	raw_spin_unlock_irq(&desc->lock);

	if (!reenable_irq)
		return;

	/* need to do locking dance for chip_bus_lock() to reenable IRQ */
	chip_bus_lock(desc);
	raw_spin_lock_irq(&desc->lock);

	/* make sure we haven't raced with anyone inbetween */
	if (!spr->poll_rem && (desc->status & IRQ_SPURIOUS_DISABLED)) {
		printk(KERN_INFO "IRQ %u: spurious polling finished, "
		       "reenabling IRQ\n", desc->irq_data.irq);
		__enable_irq(desc, desc->irq_data.irq, false);
		desc->status &= ~IRQ_SPURIOUS_DISABLED;
	}

	raw_spin_unlock_irq(&desc->lock);
	chip_bus_sync_unlock(desc);
}

void irq_poll_action_added(struct irq_desc *desc, struct irqaction *action)
{
	struct irq_spr *spr = &desc->spr;
	unsigned long flags;

	raw_spin_lock_irqsave(&desc->lock, flags);

	if ((action->flags & IRQF_SHARED) && irqfixup >= IRQFIXUP_POLL) {
		if (!spr->poll_rem)
			printk(KERN_INFO "IRQ %u: starting IRQFIXUP_POLL\n",
			       desc->irq_data.irq);
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
	struct irq_expect *exp, *next;
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
		__enable_irq(desc, desc->irq_data.irq, false);
		desc->status &= ~IRQ_SPURIOUS_DISABLED;
		irq_enabled = true;
	}

	if (timer_killed || irq_enabled)
		printk(KERN_INFO "IRQ %u:%s%s%s\n", desc->irq_data.irq,
		       timer_killed ? " polling stopped" : "",
		       timer_killed && irq_enabled ? " and" : "",
		       irq_enabled ? " IRQ reenabled" : "");

	/* free expect tokens */
	for (exp = action->expects; exp; exp = next) {
		next = exp->next;
		kfree(exp);
	}
	action->expects = NULL;

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
