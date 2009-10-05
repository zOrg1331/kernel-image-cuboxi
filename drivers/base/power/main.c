/*
 * drivers/base/power/main.c - Where the driver meets power management.
 *
 * Copyright (c) 2003 Patrick Mochel
 * Copyright (c) 2003 Open Source Development Lab
 *
 * This file is released under the GPLv2
 *
 *
 * The driver model core calls device_pm_add() when a device is registered.
 * This will intialize the embedded device_pm_info object in the device
 * and add it to the list of power-controlled devices. sysfs entries for
 * controlling device power management will also be added.
 *
 * A separate list is used for keeping track of power info, because the power
 * domain dependencies may differ from the ancestral dependencies that the
 * subsystem list maintains.
 */

#include <linux/device.h>
#include <linux/kallsyms.h>
#include <linux/mutex.h>
#include <linux/pm.h>
#include <linux/pm_link.h>
#include <linux/pm_runtime.h>
#include <linux/resume-trace.h>
#include <linux/rwsem.h>
#include <linux/interrupt.h>
#include <linux/async.h>
#include <linux/completion.h>

#include "../base.h"
#include "power.h"

/*
 * The entries in the dpm_list list are in a depth first order, simply
 * because children are guaranteed to be discovered after parents, and
 * are inserted at the back of the list on discovery.
 *
 * Since device_pm_add() may be called with a device semaphore held,
 * we must never try to acquire a device semaphore while holding
 * dpm_list_mutex.
 */

LIST_HEAD(dpm_list);

static DEFINE_MUTEX(dpm_list_mtx);
static pm_message_t pm_transition;

/*
 * Set once the preparation of devices for a PM transition has started, reset
 * before starting to resume devices.  Protected by dpm_list_mtx.
 */
static bool transition_started;

/**
 * device_pm_lock - Lock the list of active devices used by the PM core.
 */
void device_pm_lock(void)
{
	mutex_lock(&dpm_list_mtx);
}

/**
 * device_pm_unlock - Unlock the list of active devices used by the PM core.
 */
void device_pm_unlock(void)
{
	mutex_unlock(&dpm_list_mtx);
}

/**
 * device_pm_list_add - Add a device to the PM core's list of active devices.
 * @dev: Device to add to the list.
 */
void device_pm_list_add(struct device *dev)
{
	mutex_lock(&dpm_list_mtx);
	if (dev->parent) {
		if (dev->parent->power.status >= DPM_SUSPENDING)
			dev_warn(dev, "parent %s should not be sleeping\n",
				 dev_name(dev->parent));
	} else if (transition_started) {
		/*
		 * We refuse to register parentless devices while a PM
		 * transition is in progress in order to avoid leaving them
		 * unhandled down the road
		 */
		dev_WARN(dev, "Parentless device registered during a PM transaction\n");
	}
	list_add_tail(&dev->power.entry, &dpm_list);
	mutex_unlock(&dpm_list_mtx);
}

/**
 * device_pm_list_remove - Remove a device from the PM core's list of devices.
 * @dev: Device to be removed from the list.
 */
void device_pm_list_remove(struct device *dev)
{
	mutex_lock(&dpm_list_mtx);
	list_del_init(&dev->power.entry);
	mutex_unlock(&dpm_list_mtx);
}

/**
 * device_pm_move_before - Move device in the PM core's list of active devices.
 * @deva: Device to move in dpm_list.
 * @devb: Device @deva should come before.
 */
void device_pm_move_before(struct device *deva, struct device *devb)
{
	pr_debug("PM: Moving %s:%s before %s:%s\n",
		 deva->bus ? deva->bus->name : "No Bus",
		 kobject_name(&deva->kobj),
		 devb->bus ? devb->bus->name : "No Bus",
		 kobject_name(&devb->kobj));
	/* Delete deva from dpm_list and reinsert before devb. */
	list_move_tail(&deva->power.entry, &devb->power.entry);
}

/**
 * device_pm_move_after - Move device in the PM core's list of active devices.
 * @deva: Device to move in dpm_list.
 * @devb: Device @deva should come after.
 */
void device_pm_move_after(struct device *deva, struct device *devb)
{
	pr_debug("PM: Moving %s:%s after %s:%s\n",
		 deva->bus ? deva->bus->name : "No Bus",
		 kobject_name(&deva->kobj),
		 devb->bus ? devb->bus->name : "No Bus",
		 kobject_name(&devb->kobj));
	/* Delete deva from dpm_list and reinsert after devb. */
	list_move(&deva->power.entry, &devb->power.entry);
}

/**
 * device_pm_move_last - Move device to end of the PM core's list of devices.
 * @dev: Device to move in dpm_list.
 */
void device_pm_move_last(struct device *dev)
{
	pr_debug("PM: Moving %s:%s to end of list\n",
		 dev->bus ? dev->bus->name : "No Bus",
		 kobject_name(&dev->kobj));
	list_move_tail(&dev->power.entry, &dpm_list);
}

/**
 * dpm_reset - Clear power.op_started and power.op_complete for given device.
 * @dev: Device to handle.
 */
static void dpm_reset(struct device *dev)
{
	dev->power.op_started = false;
	dev->power.op_complete = false;
}

/**
 * dpm_reset_all - Call dpm_reset() for all devices.
 */
static void dpm_reset_all(void)
{
	struct device *dev;

	list_for_each_entry(dev, &dpm_list, power.entry)
		dpm_reset(dev);
}

/**
 * dpm_synchronize_noirq - Wait for "late" or "early" PM callbacks to complete.
 *
 * Wait for the "late" or "early" suspend/resume callbacks of all devices to
 * complete and clear power.op_started and power.op_complete for all devices.
 */
static void dpm_synchronize_noirq(void)
{
	async_synchronize_full();
	dpm_reset_all();
}

/**
 * dpm_synchronize_noirq - Wait for PM callbacks to complete.
 *
 * Wait for the "regular" suspend/resume callbacks of all devices to complete
 * and clear power.op_started and power.op_complete for all devices.
 */
static void dpm_synchronize(void)
{
	async_synchronize_full();
	mutex_lock(&dpm_list_mtx);
	dpm_reset_all();
	mutex_unlock(&dpm_list_mtx);
}

/**
 * device_pm_wait - Wait for a PM operation to complete.
 * @sub: "Slave" device.
 * @dev: Device to wait for.
 *
 * Wait for a PM operation carried out for @dev to complete, unless both @sub
 * and @dev have to be handled synchronously (in such a case they are going to
 * be handled in the right order anyway thanks to the pm_list ordering).
 */
static void device_pm_wait(struct device *sub, struct device *dev)
{
	if (!dev)
		return;

	if (!(sub->power.async_suspend || dev->power.async_suspend))
		return;

	if (!dev->power.op_complete) {
		dev_dbg(sub, "PM: Waiting for %s %s\n", dev_driver_string(dev),
			dev_name(dev));
		wait_event(dev->power.wait_queue, !!dev->power.op_complete);
	}
}

/**
 * device_pm_wait_fn - Wrapper for device_pm_wait().
 * @dev: Device to wait for.
 * @data: Pointer to the "slave" device object.
 */
static int device_pm_wait_fn(struct device *dev, void *data)
{
	device_pm_wait((struct device *)data, dev);
	return 0;
}

/**
 * device_pm_wait_for_masters - Wait for all masters of given device.
 * @slave: Device to wait for the masters of.
 */
static void device_pm_wait_for_masters(struct device *slave)
{
	if (!pm_trace_is_enabled())
		device_for_each_master(slave, slave, device_pm_wait_fn);
}

/**
 * device_pm_check - Check the power.op_complete flag of given device.
 * @dev: Device to check.
 */
static bool device_pm_check(struct device *dev)
{
	int ret = 0;

	if (dev)
		ret = !dev->power.op_complete;

	return ret;
}

/**
 * device_pm_check_fn - Wrapper for device_pm_check().
 * @dev: Device to check.
 * @data: Ignored.
 */
static int device_pm_check_fn(struct device *dev, void *data)
{
	return device_pm_check(dev);
}

/**
 * device_pm_check_masters - Check power.op_complete for masters of a device.
 * @slave: Device to check the masters of.
 */
static int device_pm_check_masters(struct device *slave)
{
	return device_for_each_master(slave, NULL, device_pm_check_fn);
}

/**
 * pm_op - Execute the PM operation appropriate for given PM event.
 * @dev: Device to handle.
 * @ops: PM operations to choose from.
 * @state: PM transition of the system being carried out.
 */
static int pm_op(struct device *dev,
		 const struct dev_pm_ops *ops,
		 pm_message_t state)
{
	int error = 0;

	switch (state.event) {
#ifdef CONFIG_SUSPEND
	case PM_EVENT_SUSPEND:
		if (ops->suspend) {
			error = ops->suspend(dev);
			suspend_report_result(ops->suspend, error);
		}
		break;
	case PM_EVENT_RESUME:
		if (ops->resume) {
			error = ops->resume(dev);
			suspend_report_result(ops->resume, error);
		}
		break;
#endif /* CONFIG_SUSPEND */
#ifdef CONFIG_HIBERNATION
	case PM_EVENT_FREEZE:
	case PM_EVENT_QUIESCE:
		if (ops->freeze) {
			error = ops->freeze(dev);
			suspend_report_result(ops->freeze, error);
		}
		break;
	case PM_EVENT_HIBERNATE:
		if (ops->poweroff) {
			error = ops->poweroff(dev);
			suspend_report_result(ops->poweroff, error);
		}
		break;
	case PM_EVENT_THAW:
	case PM_EVENT_RECOVER:
		if (ops->thaw) {
			error = ops->thaw(dev);
			suspend_report_result(ops->thaw, error);
		}
		break;
	case PM_EVENT_RESTORE:
		if (ops->restore) {
			error = ops->restore(dev);
			suspend_report_result(ops->restore, error);
		}
		break;
#endif /* CONFIG_HIBERNATION */
	default:
		error = -EINVAL;
	}
	return error;
}

/**
 * pm_noirq_op - Execute the PM operation appropriate for given PM event.
 * @dev: Device to handle.
 * @ops: PM operations to choose from.
 * @state: PM transition of the system being carried out.
 *
 * The driver of @dev will not receive interrupts while this function is being
 * executed.
 */
static int pm_noirq_op(struct device *dev,
			const struct dev_pm_ops *ops,
			pm_message_t state)
{
	int error = 0;

	switch (state.event) {
#ifdef CONFIG_SUSPEND
	case PM_EVENT_SUSPEND:
		if (ops->suspend_noirq) {
			error = ops->suspend_noirq(dev);
			suspend_report_result(ops->suspend_noirq, error);
		}
		break;
	case PM_EVENT_RESUME:
		if (ops->resume_noirq) {
			error = ops->resume_noirq(dev);
			suspend_report_result(ops->resume_noirq, error);
		}
		break;
#endif /* CONFIG_SUSPEND */
#ifdef CONFIG_HIBERNATION
	case PM_EVENT_FREEZE:
	case PM_EVENT_QUIESCE:
		if (ops->freeze_noirq) {
			error = ops->freeze_noirq(dev);
			suspend_report_result(ops->freeze_noirq, error);
		}
		break;
	case PM_EVENT_HIBERNATE:
		if (ops->poweroff_noirq) {
			error = ops->poweroff_noirq(dev);
			suspend_report_result(ops->poweroff_noirq, error);
		}
		break;
	case PM_EVENT_THAW:
	case PM_EVENT_RECOVER:
		if (ops->thaw_noirq) {
			error = ops->thaw_noirq(dev);
			suspend_report_result(ops->thaw_noirq, error);
		}
		break;
	case PM_EVENT_RESTORE:
		if (ops->restore_noirq) {
			error = ops->restore_noirq(dev);
			suspend_report_result(ops->restore_noirq, error);
		}
		break;
#endif /* CONFIG_HIBERNATION */
	default:
		error = -EINVAL;
	}
	return error;
}

/**
 * pm_op_started - Mark the beginning of a PM operation for given device.
 * @dev: Device to handle.
 */
static bool pm_op_started(struct device *dev)
{
	bool ret = false;

	spin_lock_irq(&dev->power.lock);
	if (dev->power.op_started)
		ret = true;
	else
		dev->power.op_started = true;
	spin_unlock_irq(&dev->power.lock);

	return ret;
}

static char *pm_verb(int event)
{
	switch (event) {
	case PM_EVENT_SUSPEND:
		return "suspend";
	case PM_EVENT_RESUME:
		return "resume";
	case PM_EVENT_FREEZE:
		return "freeze";
	case PM_EVENT_QUIESCE:
		return "quiesce";
	case PM_EVENT_HIBERNATE:
		return "hibernate";
	case PM_EVENT_THAW:
		return "thaw";
	case PM_EVENT_RESTORE:
		return "restore";
	case PM_EVENT_RECOVER:
		return "recover";
	default:
		return "(unknown PM event)";
	}
}

static void pm_dev_dbg(struct device *dev, pm_message_t state, char *info)
{
	dev_dbg(dev, "%s%s%s\n", info, pm_verb(state.event),
		((state.event & PM_EVENT_SLEEP) && device_may_wakeup(dev)) ?
		", may wakeup" : "");
}

static void pm_dev_err(struct device *dev, pm_message_t state, char *info,
			int error)
{
	printk(KERN_ERR "PM: Device %s failed to %s%s: error %d\n",
		kobject_name(&dev->kobj), pm_verb(state.event), info, error);
}

/*------------------------- Resume routines -------------------------*/

/**
 * __device_resume_noirq - Execute an "early resume" callback for given device.
 * @dev: Device to handle.
 * @state: PM transition of the system being carried out.
 *
 * The driver of @dev will not receive interrupts while this function is being
 * executed.
 */
static int __device_resume_noirq(struct device *dev, pm_message_t state)
{
	int error = 0;

	TRACE_DEVICE(dev);
	TRACE_RESUME(0);

	if (dev->bus && dev->bus->pm) {
		pm_dev_dbg(dev, state, "EARLY ");
		error = pm_noirq_op(dev, dev->bus->pm, state);
	}

	dev->power.op_complete = true;
	wake_up_all(&dev->power.wait_queue);

	TRACE_RESUME(error);
	return error;
}

/**
 * async_device_resume_noirq - Wrapper of __device_resume_noirq().
 * @dev: Device to resume.
 */
static void async_device_resume_noirq(struct device *dev)
{
	int error;

	pm_dev_dbg(dev, pm_transition, "async EARLY ");
	error = __device_resume_noirq(dev, pm_transition);
	if (error)
		pm_dev_err(dev, pm_transition, " async EARLY", error);
}

/**
 * async_resume_noirq - Execute "early" resume callbacks asynchronously.
 * @data: Pointer to the first device to resume.
 * @cookie: Ignored.
 *
 * The execution of this function is scheduled with async_schedule(), so it runs
 * in its own kernel thread.  It first calls the "early" resume callback for the
 * device passed to it as @data.  Next, it walks dpm_list looking for devices
 * that can be resumed without waiting for their "masters".  If such a device is
 * found, its "early" resume callback is run.
 */
static void async_resume_noirq(void *data, async_cookie_t cookie)
{
	struct device *dev = (struct device *)data;

	device_pm_wait_for_masters(dev);
	async_device_resume_noirq(dev);

	list_for_each_entry_continue(dev, &dpm_list, power.entry) {
		if (!dev->power.async_suspend || dev->power.status <= DPM_OFF)
			continue;

		if (device_pm_check_masters(dev))
			continue;

		if (pm_op_started(dev))
			continue;

		pm_dev_dbg(dev, pm_transition, "out of order EARLY ");
		async_device_resume_noirq(dev);
	}
}

/**
 * device_resume_noirq - Execute or schedule "early" resume callback.
 * @dev: Device to resume.
 *
 * If @dev can be resumed asynchronously, schedule the execution of
 * async_resume_noirq() for it.  Otherwise, execute its "early" resume callback
 * directly.
 */
static int device_resume_noirq(struct device *dev)
{
	if (pm_op_started(dev))
		return 0;

	if (dev->power.async_suspend && !pm_trace_is_enabled()) {
		async_schedule(async_resume_noirq, dev);
		return 0;
	}

	device_pm_wait_for_masters(dev);
	return __device_resume_noirq(dev, pm_transition);
}

/**
 * dpm_resume_noirq - Execute "early resume" callbacks for non-sysdev devices.
 * @state: PM transition of the system being carried out.
 *
 * Call the "noirq" resume handlers for all devices marked as DPM_OFF_IRQ and
 * enable device drivers to receive interrupts.
 */
void dpm_resume_noirq(pm_message_t state)
{
	struct device *dev;

	mutex_lock(&dpm_list_mtx);
	transition_started = false;
	pm_transition = state;
	list_for_each_entry(dev, &dpm_list, power.entry)
		if (dev->power.status > DPM_OFF) {
			int error;

			dev->power.status = DPM_OFF;
			error = device_resume_noirq(dev);
			if (error)
				pm_dev_err(dev, state, " EARLY", error);
		}
	dpm_synchronize_noirq();
	mutex_unlock(&dpm_list_mtx);
	resume_device_irqs();
}
EXPORT_SYMBOL_GPL(dpm_resume_noirq);

/**
 * __device_resume - Execute "resume" callbacks for given device.
 * @dev: Device to handle.
 * @state: PM transition of the system being carried out.
 */
static int __device_resume(struct device *dev, pm_message_t state)
{
	int error = 0;

	TRACE_DEVICE(dev);
	TRACE_RESUME(0);

	down(&dev->sem);

	if (dev->bus) {
		if (dev->bus->pm) {
			pm_dev_dbg(dev, state, "");
			error = pm_op(dev, dev->bus->pm, state);
		} else if (dev->bus->resume) {
			pm_dev_dbg(dev, state, "legacy ");
			error = dev->bus->resume(dev);
		}
		if (error)
			goto End;
	}

	if (dev->type) {
		if (dev->type->pm) {
			pm_dev_dbg(dev, state, "type ");
			error = pm_op(dev, dev->type->pm, state);
		}
		if (error)
			goto End;
	}

	if (dev->class) {
		if (dev->class->pm) {
			pm_dev_dbg(dev, state, "class ");
			error = pm_op(dev, dev->class->pm, state);
		} else if (dev->class->resume) {
			pm_dev_dbg(dev, state, "legacy class ");
			error = dev->class->resume(dev);
		}
	}
 End:
	up(&dev->sem);
	dev->power.op_complete = true;
	wake_up_all(&dev->power.wait_queue);

	TRACE_RESUME(error);
	return error;
}

/**
 * async_device_resume - Wrapper of __device_resume().
 * @dev: Device to resume.
 */
static void async_device_resume(struct device *dev)
{
	int error;

	pm_dev_dbg(dev, pm_transition, "async ");
	error = __device_resume(dev, pm_transition);
	if (error)
		pm_dev_err(dev, pm_transition, " async", error);
}

/**
 * async_resume - Execute resume callbacks asynchronously.
 * @data: Pointer to the first device to resume.
 * @cookie: Ignored.
 *
 * The execution of this function is scheduled with async_schedule(), so it runs
 * in its own kernel thread.  It first calls the resume callbacks for the device
 * passed to it as @data.  Next, it walks dpm_list looking for devices that can
 * be resumed without waiting for their "masters".  If such a device is found,
 * its resume callbacks are run.
 */
static void async_resume(void *data, async_cookie_t cookie)
{
	struct device *dev = (struct device *)data;

	device_pm_wait_for_masters(dev);

 repeat:
	async_device_resume(dev);
	put_device(dev);

	mutex_lock(&dpm_list_mtx);
	if (dev->power.status < DPM_OFF)
		dev = to_device(dpm_list.next);
	list_for_each_entry_continue(dev, &dpm_list, power.entry) {
		if (!dev->power.async_suspend || dev->power.status < DPM_OFF)
			continue;

		if (device_pm_check_masters(dev))
			continue;

		if (pm_op_started(dev))
			continue;

		get_device(dev);
		mutex_unlock(&dpm_list_mtx);
		pm_dev_dbg(dev, pm_transition, "out of order ");
		goto repeat;
	}
	mutex_unlock(&dpm_list_mtx);
}

/**
 * device_resume - Execute or schedule resume callbacks for given device.
 * @dev: Device to resume.
 *
 * If @dev can be resumed asynchronously, schedule the execution of
 * async_resume() for it.  Otherwise, execute its resume callbacks directly.
 */
static int device_resume(struct device *dev)
{
	if (pm_op_started(dev))
		return 0;

	if (dev->power.async_suspend && !pm_trace_is_enabled()) {
		get_device(dev);
		async_schedule(async_resume, dev);
		return 0;
	}

	device_pm_wait_for_masters(dev);
	return __device_resume(dev, pm_transition);
}

/**
 * dpm_resume - Execute "resume" callbacks for non-sysdev devices.
 * @state: PM transition of the system being carried out.
 *
 * Execute the appropriate "resume" callback for all devices whose status
 * indicates that they are suspended.
 */
static void dpm_resume(pm_message_t state)
{
	struct list_head list;

	INIT_LIST_HEAD(&list);
	mutex_lock(&dpm_list_mtx);
	pm_transition = state;
	while (!list_empty(&dpm_list)) {
		struct device *dev = to_device(dpm_list.next);

		get_device(dev);
		if (dev->power.status >= DPM_OFF) {
			int error;

			dev->power.status = DPM_RESUMING;
			mutex_unlock(&dpm_list_mtx);

			error = device_resume(dev);

			mutex_lock(&dpm_list_mtx);
			if (error)
				pm_dev_err(dev, state, "", error);
		} else if (dev->power.status == DPM_SUSPENDING) {
			/* Allow new children of the device to be registered */
			dev->power.status = DPM_RESUMING;
		}
		if (!list_empty(&dev->power.entry))
			list_move_tail(&dev->power.entry, &list);
		put_device(dev);
	}
	list_splice(&list, &dpm_list);
	mutex_unlock(&dpm_list_mtx);
	dpm_synchronize();
}

/**
 * device_complete - Complete a PM transition for given device.
 * @dev: Device to handle.
 * @state: PM transition of the system being carried out.
 */
static void device_complete(struct device *dev, pm_message_t state)
{
	down(&dev->sem);

	if (dev->class && dev->class->pm && dev->class->pm->complete) {
		pm_dev_dbg(dev, state, "completing class ");
		dev->class->pm->complete(dev);
	}

	if (dev->type && dev->type->pm && dev->type->pm->complete) {
		pm_dev_dbg(dev, state, "completing type ");
		dev->type->pm->complete(dev);
	}

	if (dev->bus && dev->bus->pm && dev->bus->pm->complete) {
		pm_dev_dbg(dev, state, "completing ");
		dev->bus->pm->complete(dev);
	}

	up(&dev->sem);
}

/**
 * dpm_complete - Complete a PM transition for all non-sysdev devices.
 * @state: PM transition of the system being carried out.
 *
 * Execute the ->complete() callbacks for all devices whose PM status is not
 * DPM_ON (this allows new devices to be registered).
 */
static void dpm_complete(pm_message_t state)
{
	struct list_head list;

	INIT_LIST_HEAD(&list);
	mutex_lock(&dpm_list_mtx);
	while (!list_empty(&dpm_list)) {
		struct device *dev = to_device(dpm_list.prev);

		get_device(dev);
		if (dev->power.status > DPM_ON) {
			dev->power.status = DPM_ON;
			mutex_unlock(&dpm_list_mtx);

			device_complete(dev, state);
			pm_runtime_put_noidle(dev);

			mutex_lock(&dpm_list_mtx);
		}
		if (!list_empty(&dev->power.entry))
			list_move(&dev->power.entry, &list);
		put_device(dev);
	}
	list_splice(&list, &dpm_list);
	mutex_unlock(&dpm_list_mtx);
}

/**
 * dpm_resume_end - Execute "resume" callbacks and complete system transition.
 * @state: PM transition of the system being carried out.
 *
 * Execute "resume" callbacks for all devices and complete the PM transition of
 * the system.
 */
void dpm_resume_end(pm_message_t state)
{
	might_sleep();
	dpm_resume(state);
	dpm_complete(state);
}
EXPORT_SYMBOL_GPL(dpm_resume_end);


/*------------------------- Suspend routines -------------------------*/

/**
 * resume_event - Return a "resume" message for given "suspend" sleep state.
 * @sleep_state: PM message representing a sleep state.
 *
 * Return a PM message representing the resume event corresponding to given
 * sleep state.
 */
static pm_message_t resume_event(pm_message_t sleep_state)
{
	switch (sleep_state.event) {
	case PM_EVENT_SUSPEND:
		return PMSG_RESUME;
	case PM_EVENT_FREEZE:
	case PM_EVENT_QUIESCE:
		return PMSG_RECOVER;
	case PM_EVENT_HIBERNATE:
		return PMSG_RESTORE;
	}
	return PMSG_ON;
}

/**
 * device_suspend_noirq - Execute a "late suspend" callback for given device.
 * @dev: Device to handle.
 * @state: PM transition of the system being carried out.
 *
 * The driver of @dev will not receive interrupts while this function is being
 * executed.
 */
static int device_suspend_noirq(struct device *dev, pm_message_t state)
{
	int error = 0;

	if (!dev->bus)
		return 0;

	if (dev->bus->pm) {
		pm_dev_dbg(dev, state, "LATE ");
		error = pm_noirq_op(dev, dev->bus->pm, state);
	}
	return error;
}

/**
 * dpm_suspend_noirq - Execute "late suspend" callbacks for non-sysdev devices.
 * @state: PM transition of the system being carried out.
 *
 * Prevent device drivers from receiving interrupts and call the "noirq" suspend
 * handlers for all non-sysdev devices.
 */
int dpm_suspend_noirq(pm_message_t state)
{
	struct device *dev;
	int error = 0;

	suspend_device_irqs();
	mutex_lock(&dpm_list_mtx);
	list_for_each_entry_reverse(dev, &dpm_list, power.entry) {
		error = device_suspend_noirq(dev, state);
		if (error) {
			pm_dev_err(dev, state, " late", error);
			break;
		}
		dev->power.status = DPM_OFF_IRQ;
	}
	mutex_unlock(&dpm_list_mtx);
	if (error)
		dpm_resume_noirq(resume_event(state));
	return error;
}
EXPORT_SYMBOL_GPL(dpm_suspend_noirq);

/**
 * device_suspend - Execute "suspend" callbacks for given device.
 * @dev: Device to handle.
 * @state: PM transition of the system being carried out.
 */
static int device_suspend(struct device *dev, pm_message_t state)
{
	int error = 0;

	down(&dev->sem);

	if (dev->class) {
		if (dev->class->pm) {
			pm_dev_dbg(dev, state, "class ");
			error = pm_op(dev, dev->class->pm, state);
		} else if (dev->class->suspend) {
			pm_dev_dbg(dev, state, "legacy class ");
			error = dev->class->suspend(dev, state);
			suspend_report_result(dev->class->suspend, error);
		}
		if (error)
			goto End;
	}

	if (dev->type) {
		if (dev->type->pm) {
			pm_dev_dbg(dev, state, "type ");
			error = pm_op(dev, dev->type->pm, state);
		}
		if (error)
			goto End;
	}

	if (dev->bus) {
		if (dev->bus->pm) {
			pm_dev_dbg(dev, state, "");
			error = pm_op(dev, dev->bus->pm, state);
		} else if (dev->bus->suspend) {
			pm_dev_dbg(dev, state, "legacy ");
			error = dev->bus->suspend(dev, state);
			suspend_report_result(dev->bus->suspend, error);
		}
	}
 End:
	up(&dev->sem);

	return error;
}

/**
 * dpm_suspend - Execute "suspend" callbacks for all non-sysdev devices.
 * @state: PM transition of the system being carried out.
 */
static int dpm_suspend(pm_message_t state)
{
	struct list_head list;
	int error = 0;

	INIT_LIST_HEAD(&list);
	mutex_lock(&dpm_list_mtx);
	while (!list_empty(&dpm_list)) {
		struct device *dev = to_device(dpm_list.prev);

		get_device(dev);
		mutex_unlock(&dpm_list_mtx);

		error = device_suspend(dev, state);

		mutex_lock(&dpm_list_mtx);
		if (error) {
			pm_dev_err(dev, state, "", error);
			put_device(dev);
			break;
		}
		dev->power.status = DPM_OFF;
		if (!list_empty(&dev->power.entry))
			list_move(&dev->power.entry, &list);
		put_device(dev);
	}
	list_splice(&list, dpm_list.prev);
	mutex_unlock(&dpm_list_mtx);
	return error;
}

/**
 * device_prepare - Prepare a device for system power transition.
 * @dev: Device to handle.
 * @state: PM transition of the system being carried out.
 *
 * Execute the ->prepare() callback(s) for given device.  No new children of the
 * device may be registered after this function has returned.
 */
static int device_prepare(struct device *dev, pm_message_t state)
{
	int error = 0;

	down(&dev->sem);

	if (dev->bus && dev->bus->pm && dev->bus->pm->prepare) {
		pm_dev_dbg(dev, state, "preparing ");
		error = dev->bus->pm->prepare(dev);
		suspend_report_result(dev->bus->pm->prepare, error);
		if (error)
			goto End;
	}

	if (dev->type && dev->type->pm && dev->type->pm->prepare) {
		pm_dev_dbg(dev, state, "preparing type ");
		error = dev->type->pm->prepare(dev);
		suspend_report_result(dev->type->pm->prepare, error);
		if (error)
			goto End;
	}

	if (dev->class && dev->class->pm && dev->class->pm->prepare) {
		pm_dev_dbg(dev, state, "preparing class ");
		error = dev->class->pm->prepare(dev);
		suspend_report_result(dev->class->pm->prepare, error);
	}
 End:
	up(&dev->sem);

	return error;
}

/**
 * dpm_prepare - Prepare all non-sysdev devices for a system PM transition.
 * @state: PM transition of the system being carried out.
 *
 * Execute the ->prepare() callback(s) for all devices.
 */
static int dpm_prepare(pm_message_t state)
{
	struct list_head list;
	int error = 0;

	INIT_LIST_HEAD(&list);
	mutex_lock(&dpm_list_mtx);
	transition_started = true;
	while (!list_empty(&dpm_list)) {
		struct device *dev = to_device(dpm_list.next);

		get_device(dev);
		dev->power.status = DPM_PREPARING;
		mutex_unlock(&dpm_list_mtx);

		pm_runtime_get_noresume(dev);
		if (pm_runtime_barrier(dev) && device_may_wakeup(dev)) {
			/* Wake-up requested during system sleep transition. */
			pm_runtime_put_noidle(dev);
			error = -EBUSY;
		} else {
			error = device_prepare(dev, state);
		}

		mutex_lock(&dpm_list_mtx);
		if (error) {
			dev->power.status = DPM_ON;
			if (error == -EAGAIN) {
				put_device(dev);
				error = 0;
				continue;
			}
			printk(KERN_ERR "PM: Failed to prepare device %s "
				"for power transition: error %d\n",
				kobject_name(&dev->kobj), error);
			put_device(dev);
			break;
		}
		dev->power.status = DPM_SUSPENDING;
		if (!list_empty(&dev->power.entry)) {
			list_move_tail(&dev->power.entry, &list);
			dpm_reset(dev);
		}
		put_device(dev);
	}
	list_splice(&list, &dpm_list);
	mutex_unlock(&dpm_list_mtx);
	return error;
}

/**
 * dpm_suspend_start - Prepare devices for PM transition and suspend them.
 * @state: PM transition of the system being carried out.
 *
 * Prepare all non-sysdev devices for system PM transition and execute "suspend"
 * callbacks for them.
 */
int dpm_suspend_start(pm_message_t state)
{
	int error;

	might_sleep();
	error = dpm_prepare(state);
	if (!error)
		error = dpm_suspend(state);
	return error;
}
EXPORT_SYMBOL_GPL(dpm_suspend_start);

void __suspend_report_result(const char *function, void *fn, int ret)
{
	if (ret)
		printk(KERN_ERR "%s(): %pF returns %d\n", function, fn, ret);
}
EXPORT_SYMBOL_GPL(__suspend_report_result);
