#include <linux/kernel.h>
#include <linux/mm.h>
#include <linux/sched.h>
#include <linux/poll.h>
#include <linux/smp_lock.h>
#include <linux/string.h>
#include <linux/file.h>
#include <linux/types.h>
#include <linux/vmalloc.h>
#include <linux/grinternal.h>

extern ssize_t write_grsec_handler(struct file * file, const char __user * buf,
				   size_t count, loff_t *ppos);
extern int gr_acl_is_enabled(void);

static DECLARE_WAIT_QUEUE_HEAD(learn_wait);
static int gr_learn_attached;

/* use a 512k buffer */
#define LEARN_BUFFER_SIZE (512 * 1024)

static DEFINE_SPINLOCK(gr_learn_lock);
static DECLARE_MUTEX(gr_learn_user_sem);

/* we need to maintain two buffers, so that the kernel context of grlearn
   uses a semaphore around the userspace copying, and the other kernel contexts
   use a spinlock when copying into the buffer, since they cannot sleep
*/
static char *learn_buffer;
static char *learn_buffer_user;
static int learn_buffer_len;
static int learn_buffer_user_len;

static ssize_t
read_learn(struct file *file, char __user * buf, size_t count, loff_t * ppos)
{
	DECLARE_WAITQUEUE(wait, current);
	ssize_t retval = 0;

	add_wait_queue(&learn_wait, &wait);
	set_current_state(TASK_INTERRUPTIBLE);
	do {
		down(&gr_learn_user_sem);
		spin_lock(&gr_learn_lock);
		if (learn_buffer_len)
			break;
		spin_unlock(&gr_learn_lock);
		up(&gr_learn_user_sem);
		if (file->f_flags & O_NONBLOCK) {
			retval = -EAGAIN;
			goto out;
		}
		if (signal_pending(current)) {
			retval = -ERESTARTSYS;
			goto out;
		}

		schedule();
	} while (1);

	memcpy(learn_buffer_user, learn_buffer, learn_buffer_len);
	learn_buffer_user_len = learn_buffer_len;
	retval = learn_buffer_len;
	learn_buffer_len = 0;

	spin_unlock(&gr_learn_lock);

	if (copy_to_user(buf, learn_buffer_user, learn_buffer_user_len))
		retval = -EFAULT;

	up(&gr_learn_user_sem);
out:
	set_current_state(TASK_RUNNING);
	remove_wait_queue(&learn_wait, &wait);
	return retval;
}

static unsigned int
poll_learn(struct file * file, poll_table * wait)
{
	poll_wait(file, &learn_wait, wait);

	if (learn_buffer_len)
		return (POLLIN | POLLRDNORM);

	return 0;
}

void
gr_clear_learn_entries(void)
{
	char *tmp;

	down(&gr_learn_user_sem);
	if (learn_buffer != NULL) {
		spin_lock(&gr_learn_lock);
		tmp = learn_buffer;
		learn_buffer = NULL;
		spin_unlock(&gr_learn_lock);
		vfree(learn_buffer);
	}
	if (learn_buffer_user != NULL) {
		vfree(learn_buffer_user);
		learn_buffer_user = NULL;
	}
	learn_buffer_len = 0;
	up(&gr_learn_user_sem);

	return;
}

void
gr_add_learn_entry(const char *fmt, ...)
{
	va_list args;
	unsigned int len;

	if (!gr_learn_attached)
		return;

	spin_lock(&gr_learn_lock);

	/* leave a gap at the end so we know when it's "full" but don't have to
	   compute the exact length of the string we're trying to append
	*/
	if (learn_buffer_len > LEARN_BUFFER_SIZE - 16384) {
		spin_unlock(&gr_learn_lock);
		wake_up_interruptible(&learn_wait);
		return;
	}
	if (learn_buffer == NULL) {
		spin_unlock(&gr_learn_lock);
		return;
	}

	va_start(args, fmt);
	len = vsnprintf(learn_buffer + learn_buffer_len, LEARN_BUFFER_SIZE - learn_buffer_len, fmt, args);
	va_end(args);

	learn_buffer_len += len + 1;

	spin_unlock(&gr_learn_lock);
	wake_up_interruptible(&learn_wait);

	return;
}

static int
open_learn(struct inode *inode, struct file *file)
{
	if (file->f_mode & FMODE_READ && gr_learn_attached)
		return -EBUSY;
	if (file->f_mode & FMODE_READ) {
		int retval = 0;
		down(&gr_learn_user_sem);
		if (learn_buffer == NULL)
			learn_buffer = vmalloc(LEARN_BUFFER_SIZE);
		if (learn_buffer_user == NULL)
			learn_buffer_user = vmalloc(LEARN_BUFFER_SIZE);
		if (learn_buffer == NULL) {
			retval = -ENOMEM;
			goto out_error;
		}
		if (learn_buffer_user == NULL) {
			retval = -ENOMEM;
			goto out_error;
		}
		learn_buffer_len = 0;
		learn_buffer_user_len = 0;
		gr_learn_attached = 1;
out_error:
		up(&gr_learn_user_sem);
		return retval;
	}
	return 0;
}

static int
close_learn(struct inode *inode, struct file *file)
{
	char *tmp;

	if (file->f_mode & FMODE_READ) {
		down(&gr_learn_user_sem);
		if (learn_buffer != NULL) {
			spin_lock(&gr_learn_lock);
			tmp = learn_buffer;
			learn_buffer = NULL;
			spin_unlock(&gr_learn_lock);
			vfree(tmp);
		}
		if (learn_buffer_user != NULL) {
			vfree(learn_buffer_user);
			learn_buffer_user = NULL;
		}
		learn_buffer_len = 0;
		learn_buffer_user_len = 0;
		gr_learn_attached = 0;
		up(&gr_learn_user_sem);
	}

	return 0;
}
		
struct file_operations grsec_fops = {
	.read		= read_learn,
	.write		= write_grsec_handler,
	.open		= open_learn,
	.release	= close_learn,
	.poll		= poll_learn,
};
