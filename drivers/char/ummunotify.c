/*
 * Copyright (c) 2009 Cisco Systems.  All rights reserved.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version
 * 2 as published by the Free Software Foundation.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <linux/fs.h>
#include <linux/init.h>
#include <linux/list.h>
#include <linux/miscdevice.h>
#include <linux/mm.h>
#include <linux/mmu_notifier.h>
#include <linux/module.h>
#include <linux/poll.h>
#include <linux/rbtree.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/uaccess.h>
#include <linux/ummunotify.h>

#include <asm/cacheflush.h>

MODULE_AUTHOR("Roland Dreier");
MODULE_DESCRIPTION("Userspace MMU notifiers");
MODULE_LICENSE("GPL v2");

/*
 * Information about an address range userspace has asked us to watch.
 *
 * user_cookie: Opaque cookie given to us when userspace registers the
 *   address range.
 *
 * start, end: Address range; start is inclusive, end is exclusive.
 *
 * hint_start, hint_end: If a single MMU notification event
 *   invalidates the address range, we hold the actual range of
 *   addresses that were invalidated (and set UMMUNOTIFY_FLAG_HINT).
 *   If another event hits this range before userspace reads the
 *   event, we give up and don't try to keep track of which subsets
 *   got invalidated.
 *
 * flags: Holds the INVALID flag for ranges that are on the invalid
 *   list and/or the HINT flag for ranges where the hint range holds
 *   good information.
 *
 * node: Used to put the range into an rbtree we use to be able to
 *   scan address ranges in order.
 *
 * list: Used to put the range on the invalid list when an MMU
 *   notification event hits the range.
 */
enum {
	UMMUNOTIFY_FLAG_INVALID	= 1,
	UMMUNOTIFY_FLAG_HINT	= 2,
};

struct ummunotify_reg {
	u64			user_cookie;
	unsigned long		start;
	unsigned long		end;
	unsigned long		hint_start;
	unsigned long		hint_end;
	unsigned long		flags;
	struct rb_node		node;
	struct list_head	list;
};

/*
 * Context attached to each file that userspace opens.
 *
 * mmu_notifier: MMU notifier registered for this context.
 *
 * mm: mm_struct for process that created the context; we use this to
 *   hold a reference to the mm to make sure it doesn't go away until
 *   we're done with it.
 *
 * reg_tree: RB tree of address ranges being watched, sorted by start
 *   address.
 *
 * invalid_list: List of address ranges that have been invalidated by
 *   MMU notification events; as userspace reads events, the address
 *   range corresponding to the event is removed from the list.
 *
 * counter: Page that can be mapped read-only by userspace, which
 *   holds a generation count that is incremented each time an event
 *   occurs.
 *
 * lock: Spinlock used to protect all context.
 *
 * read_wait: Wait queue used to wait for data to become available in
 *   blocking read()s.
 *
 * async_queue: Used to implement fasync().
 *
 * need_empty: Set when userspace reads an invalidation event, so that
 *   read() knows it must generate an "empty" event when userspace
 *   drains the invalid_list.
 *
 * used: Set after userspace does anything with the file, so that the
 *   "exchange flags" ioctl() knows it's too late to change anything.
 */
struct ummunotify_file {
	struct mmu_notifier	mmu_notifier;
	struct mm_struct       *mm;
	struct rb_root		reg_tree;
	struct list_head	invalid_list;
	u64		       *counter;
	spinlock_t		lock;
	wait_queue_head_t	read_wait;
	struct fasync_struct   *async_queue;
	int			need_empty;
	int			used;
};

static void ummunotify_handle_notify(struct mmu_notifier *mn,
				     unsigned long start, unsigned long end)
{
	struct ummunotify_file *priv =
		container_of(mn, struct ummunotify_file, mmu_notifier);
	struct rb_node *n;
	struct ummunotify_reg *reg;
	unsigned long flags;
	int hit = 0;

	spin_lock_irqsave(&priv->lock, flags);

	for (n = rb_first(&priv->reg_tree); n; n = rb_next(n)) {
		reg = rb_entry(n, struct ummunotify_reg, node);

		/*
		 * Ranges overlap if they're not disjoint; and they're
		 * disjoint if the end of one is before the start of
		 * the other one.  So if both disjointness comparisons
		 * fail then the ranges overlap.
		 *
		 * Since we keep the tree of regions we're watching
		 * sorted by start address, we can end this loop as
		 * soon as we hit a region that starts past the end of
		 * the range for the event we're handling.
		 */
		if (reg->start >= end)
			break;

		/*
		 * Just go to the next region if the start of the
		 * range is after then end of the region -- there
		 * might still be more overlapping ranges that have a
		 * greater start.
		 */
		if (start >= reg->end)
			continue;

		hit = 1;

		if (test_and_set_bit(UMMUNOTIFY_FLAG_INVALID, &reg->flags)) {
			/* Already on invalid list */
			clear_bit(UMMUNOTIFY_FLAG_HINT, &reg->flags);
		} else {
			list_add_tail(&reg->list, &priv->invalid_list);
			set_bit(UMMUNOTIFY_FLAG_HINT, &reg->flags);
			reg->hint_start = start;
			reg->hint_end   = end;
		}
	}

	if (hit) {
		++(*priv->counter);
		flush_dcache_page(virt_to_page(priv->counter));
		wake_up_interruptible(&priv->read_wait);
		kill_fasync(&priv->async_queue, SIGIO, POLL_IN);
	}

	spin_unlock_irqrestore(&priv->lock, flags);
}

static void ummunotify_invalidate_page(struct mmu_notifier *mn,
				       struct mm_struct *mm,
				       unsigned long addr)
{
	ummunotify_handle_notify(mn, addr, addr + PAGE_SIZE);
}

static void ummunotify_invalidate_range_start(struct mmu_notifier *mn,
					      struct mm_struct *mm,
					      unsigned long start,
					      unsigned long end)
{
	ummunotify_handle_notify(mn, start, end);
}

static const struct mmu_notifier_ops ummunotify_mmu_notifier_ops = {
	.invalidate_page	= ummunotify_invalidate_page,
	.invalidate_range_start	= ummunotify_invalidate_range_start,
};

static int ummunotify_open(struct inode *inode, struct file *filp)
{
	struct ummunotify_file *priv;
	int ret;

	if (filp->f_mode & FMODE_WRITE)
		return -EINVAL;

	priv = kmalloc(sizeof *priv, GFP_KERNEL);
	if (!priv)
		return -ENOMEM;

	priv->counter = (void *) get_zeroed_page(GFP_KERNEL);
	if (!priv->counter) {
		ret = -ENOMEM;
		goto err;
	}

	priv->reg_tree = RB_ROOT;
	INIT_LIST_HEAD(&priv->invalid_list);
	spin_lock_init(&priv->lock);
	init_waitqueue_head(&priv->read_wait);
	priv->async_queue = NULL;
	priv->need_empty  = 0;
	priv->used	  = 0;

	priv->mmu_notifier.ops = &ummunotify_mmu_notifier_ops;
	/*
	 * Register notifier last, since notifications can occur as
	 * soon as we register....
	 */
	ret = mmu_notifier_register(&priv->mmu_notifier, current->mm);
	if (ret)
		goto err_page;

	priv->mm = current->mm;
	atomic_inc(&priv->mm->mm_count);

	filp->private_data = priv;

	return 0;

err_page:
	free_page((unsigned long) priv->counter);

err:
	kfree(priv);
	return ret;
}

static int ummunotify_close(struct inode *inode, struct file *filp)
{
	struct ummunotify_file *priv = filp->private_data;
	struct rb_node *n;
	struct ummunotify_reg *reg;

	mmu_notifier_unregister(&priv->mmu_notifier, priv->mm);
	mmdrop(priv->mm);
	free_page((unsigned long) priv->counter);

	for (n = rb_first(&priv->reg_tree); n; n = rb_next(n)) {
		reg = rb_entry(n, struct ummunotify_reg, node);
		kfree(reg);
	}

	kfree(priv);

	return 0;
}

static bool ummunotify_readable(struct ummunotify_file *priv)
{
	return priv->need_empty || !list_empty(&priv->invalid_list);
}

static ssize_t ummunotify_read(struct file *filp, char __user *buf,
			       size_t count, loff_t *pos)
{
	struct ummunotify_file *priv = filp->private_data;
	struct ummunotify_reg *reg;
	ssize_t ret;
	struct ummunotify_event *events;
	int max;
	int n;

	priv->used = 1;

	events = (void *) get_zeroed_page(GFP_KERNEL);
	if (!events) {
		ret = -ENOMEM;
		goto out;
	}

	spin_lock_irq(&priv->lock);

	while (!ummunotify_readable(priv)) {
		spin_unlock_irq(&priv->lock);

		if (filp->f_flags & O_NONBLOCK) {
			ret = -EAGAIN;
			goto out;
		}

		if (wait_event_interruptible(priv->read_wait,
					     ummunotify_readable(priv))) {
			ret = -ERESTARTSYS;
			goto out;
		}

		spin_lock_irq(&priv->lock);
	}

	max = min_t(size_t, PAGE_SIZE, count) / sizeof *events;

	for (n = 0; n < max; ++n) {
		if (list_empty(&priv->invalid_list)) {
			events[n].type = UMMUNOTIFY_EVENT_TYPE_LAST;
			events[n].user_cookie_counter = *priv->counter;
			++n;
			priv->need_empty = 0;
			break;
		}

		reg = list_first_entry(&priv->invalid_list,
				       struct ummunotify_reg, list);

		events[n].type = UMMUNOTIFY_EVENT_TYPE_INVAL;
		if (test_bit(UMMUNOTIFY_FLAG_HINT, &reg->flags)) {
			events[n].flags	     = UMMUNOTIFY_EVENT_FLAG_HINT;
			events[n].hint_start = max(reg->start, reg->hint_start);
			events[n].hint_end   = min(reg->end, reg->hint_end);
		} else {
			events[n].hint_start = reg->start;
			events[n].hint_end   = reg->end;
		}
		events[n].user_cookie_counter = reg->user_cookie;

		list_del(&reg->list);
		reg->flags = 0;
		priv->need_empty = 1;
	}

	spin_unlock_irq(&priv->lock);

	if (copy_to_user(buf, events, n * sizeof *events))
		ret = -EFAULT;
	else
		ret = n * sizeof *events;

out:
	free_page((unsigned long) events);
	return ret;
}

static unsigned int ummunotify_poll(struct file *filp,
				    struct poll_table_struct *wait)
{
	struct ummunotify_file *priv = filp->private_data;

	poll_wait(filp, &priv->read_wait, wait);

	return ummunotify_readable(priv) ? (POLLIN | POLLRDNORM) : 0;
}

static long ummunotify_exchange_features(struct ummunotify_file *priv,
					 __u32 __user *arg)
{
	u32 feature_mask;

	if (priv->used)
		return -EINVAL;

	priv->used = 1;

	if (get_user(feature_mask, arg))
		return -EFAULT;

	/* No extensions defined at present. */
	feature_mask = 0;

	if (put_user(feature_mask, arg))
		return -EFAULT;

	return 0;
}

static long ummunotify_register_region(struct ummunotify_file *priv,
				       void __user *arg)
{
	struct ummunotify_register_ioctl parm;
	struct ummunotify_reg *reg, *treg;
	struct rb_node **n = &priv->reg_tree.rb_node;
	struct rb_node *pn;
	int ret = 0;

	if (copy_from_user(&parm, arg, sizeof parm))
		return -EFAULT;

	priv->used = 1;

	reg = kmalloc(sizeof *reg, GFP_KERNEL);
	if (!reg)
		return -ENOMEM;

	reg->user_cookie	= parm.user_cookie;
	reg->start		= parm.start;
	reg->end		= parm.end;
	reg->flags		= 0;

	spin_lock_irq(&priv->lock);

	for (pn = rb_first(&priv->reg_tree); pn; pn = rb_next(pn)) {
		treg = rb_entry(pn, struct ummunotify_reg, node);

		if (treg->user_cookie == parm.user_cookie) {
			kfree(reg);
			ret = -EINVAL;
			goto out;
		}
	}

	pn = NULL;
	while (*n) {
		pn = *n;
		treg = rb_entry(pn, struct ummunotify_reg, node);

		if (reg->start <= treg->start)
			n = &pn->rb_left;
		else
			n = &pn->rb_right;
	}

	rb_link_node(&reg->node, pn, n);
	rb_insert_color(&reg->node, &priv->reg_tree);

out:
	spin_unlock_irq(&priv->lock);

	return ret;
}

static long ummunotify_unregister_region(struct ummunotify_file *priv,
					 __u64 __user *arg)
{
	u64 user_cookie;
	struct rb_node *n;
	struct ummunotify_reg *reg;
	int ret = -EINVAL;

	if (copy_from_user(&user_cookie, arg, sizeof user_cookie))
		return -EFAULT;

	spin_lock_irq(&priv->lock);

	for (n = rb_first(&priv->reg_tree); n; n = rb_next(n)) {
		reg = rb_entry(n, struct ummunotify_reg, node);

		if (reg->user_cookie == user_cookie) {
			rb_erase(n, &priv->reg_tree);
			if (test_bit(UMMUNOTIFY_FLAG_INVALID, &reg->flags))
				list_del(&reg->list);
			kfree(reg);
			ret = 0;
			break;
		}
	}

	spin_unlock_irq(&priv->lock);

	return ret;
}

static long ummunotify_ioctl(struct file *filp, unsigned int cmd,
			     unsigned long arg)
{
	struct ummunotify_file *priv = filp->private_data;
	void __user *argp = (void __user *) arg;

	switch (cmd) {
	case UMMUNOTIFY_EXCHANGE_FEATURES:
		return ummunotify_exchange_features(priv, argp);
	case UMMUNOTIFY_REGISTER_REGION:
		return ummunotify_register_region(priv, argp);
	case UMMUNOTIFY_UNREGISTER_REGION:
		return ummunotify_unregister_region(priv, argp);
	default:
		return -ENOIOCTLCMD;
	}
}

static int ummunotify_fault(struct vm_area_struct *vma, struct vm_fault *vmf)
{
	struct ummunotify_file *priv = vma->vm_private_data;

	if (vmf->pgoff != 0)
		return VM_FAULT_SIGBUS;

	vmf->page = virt_to_page(priv->counter);
	get_page(vmf->page);

	return 0;

}

static struct vm_operations_struct ummunotify_vm_ops = {
	.fault		= ummunotify_fault,
};

static int ummunotify_mmap(struct file *filp, struct vm_area_struct *vma)
{
	struct ummunotify_file *priv = filp->private_data;

	if (vma->vm_end - vma->vm_start != PAGE_SIZE || vma->vm_pgoff != 0)
		return -EINVAL;

	vma->vm_ops		= &ummunotify_vm_ops;
	vma->vm_private_data	= priv;

	return 0;
}

static int ummunotify_fasync(int fd, struct file *filp, int on)
{
	struct ummunotify_file *priv = filp->private_data;

	return fasync_helper(fd, filp, on, &priv->async_queue);
}

static const struct file_operations ummunotify_fops = {
	.owner		= THIS_MODULE,
	.open		= ummunotify_open,
	.release	= ummunotify_close,
	.read		= ummunotify_read,
	.poll		= ummunotify_poll,
	.unlocked_ioctl	= ummunotify_ioctl,
#ifdef CONFIG_COMPAT
	.compat_ioctl	= ummunotify_ioctl,
#endif
	.mmap		= ummunotify_mmap,
	.fasync		= ummunotify_fasync,
};

static struct miscdevice ummunotify_misc = {
	.minor	= MISC_DYNAMIC_MINOR,
	.name	= "ummunotify",
	.fops	= &ummunotify_fops,
};

static int __init ummunotify_init(void)
{
	return misc_register(&ummunotify_misc);
}

static void __exit ummunotify_cleanup(void)
{
	misc_deregister(&ummunotify_misc);
}

module_init(ummunotify_init);
module_exit(ummunotify_cleanup);
