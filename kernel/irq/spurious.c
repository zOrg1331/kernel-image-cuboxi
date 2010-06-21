/*
 * linux/kernel/irq/spurious.c
 *
 * Copyright (C) 1992, 1998-2004 Linus Torvalds, Ingo Molnar
 *
 * This file contains spurious interrupt handling.
 */

#include <linux/jiffies.h>
#include <linux/irq.h>
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

/*
 * Recovery handler for misrouted interrupts.
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
 * If 99,900 of the previous 100,000 interrupts have not been handled
 * then assume that the IRQ is stuck in some manner. Drop a diagnostic
 * and try to turn the IRQ off.
 *
 * (The other 100-of-100,000 interrupts may have been a correctly
 *  functioning device sharing an IRQ with the failing one)
 *
 * Called under desc->lock
 */

static void
__report_bad_irq(unsigned int irq, struct irq_desc *desc,
		 irqreturn_t action_ret)
{
	if (action_ret != IRQ_HANDLED && action_ret != IRQ_NONE) {
		printk(KERN_ERR "irq event %d: bogus return value %x\n",
				irq, action_ret);
	} else {
		printk(KERN_ERR "irq %d: nobody cared (try booting with "
				"the \"irqpoll\" option)\n", irq);
	}
	dump_stack();
	print_irq_handlers(desc);
}

static void
report_bad_irq(unsigned int irq, struct irq_desc *desc, irqreturn_t action_ret)
{
	static int count = 100;

	if (count > 0) {
		count--;
		__report_bad_irq(irq, desc, action_ret);
	}
}

void __note_interrupt(unsigned int irq, struct irq_desc *desc,
		      irqreturn_t action_ret)
{
	if (unlikely(action_ret != IRQ_HANDLED)) {
		/*
		 * If we are seeing only the odd spurious IRQ caused by
		 * bus asynchronicity then don't eventually trigger an error,
		 * otherwise the counter becomes a doomsday timer for otherwise
		 * working systems
		 */
		if (time_after(jiffies, desc->last_unhandled + HZ/10))
			desc->irqs_unhandled = 1;
		else
			desc->irqs_unhandled++;
		desc->last_unhandled = jiffies;
		if (unlikely(action_ret != IRQ_NONE))
			report_bad_irq(irq, desc, action_ret);
	}

	if (unlikely(irqfixup >= IRQFIXUP_MISROUTED &&
		     action_ret == IRQ_NONE)) {
		int ok = misrouted_irq(irq);
		if (action_ret == IRQ_NONE)
			desc->irqs_unhandled -= ok;
	}

	desc->irq_count++;
	if (likely(desc->irq_count < 100000))
		return;

	desc->irq_count = 0;
	if (unlikely(desc->irqs_unhandled > 99900)) {
		/*
		 * The interrupt is stuck
		 */
		__report_bad_irq(irq, desc, action_ret);
		/*
		 * Now kill the IRQ
		 */
		printk(KERN_EMERG "Disabling IRQ #%d\n", irq);
		desc->status |= IRQ_DISABLED | IRQ_SPURIOUS_DISABLED;
		desc->depth++;
		desc->chip->disable(irq);

		mod_timer(&desc->poll_timer, jiffies + IRQ_POLL_INTV);
	}
	desc->irqs_unhandled = 0;
}

/*
 * IRQ poller.  Called from desc->poll_timer.
 */
void poll_irq(unsigned long arg)
{
	struct irq_desc *desc = (void *)arg;

	raw_spin_lock_irq(&desc->lock);
	try_one_irq(desc->irq, desc);
	raw_spin_unlock_irq(&desc->lock);

	mod_timer(&desc->poll_timer, jiffies + IRQ_POLL_INTV);
}

void irq_poll_action_added(struct irq_desc *desc, struct irqaction *action)
{
	unsigned long flags;

	raw_spin_lock_irqsave(&desc->lock, flags);

	/* if the interrupt was killed before, give it one more chance */
	if (desc->status & IRQ_SPURIOUS_DISABLED) {
		desc->status &= ~IRQ_SPURIOUS_DISABLED;
		__enable_irq(desc, desc->irq, false);
	}

	raw_spin_unlock_irqrestore(&desc->lock, flags);

	if ((action->flags & IRQF_SHARED) && irqfixup >= IRQFIXUP_POLL)
		mod_timer(&desc->poll_timer, jiffies + IRQ_POLL_INTV);
}

void irq_poll_action_removed(struct irq_desc *desc, struct irqaction *action)
{
	unsigned long flags;

	raw_spin_lock_irqsave(&desc->lock, flags);

	/*
	 * Make sure the timer is offline if no irqaction is left as
	 * the irq_desc will be reinitialized when the next irqaction
	 * is added.
	 */
	while (!desc->action && try_to_del_timer_sync(&desc->poll_timer) < 0) {
		raw_spin_unlock_irqrestore(&desc->lock, flags);
		cpu_relax();
		raw_spin_lock_irqsave(&desc->lock, flags);
	}

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
