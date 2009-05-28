#include <linux/kernel.h>
#include <linux/mm.h>
#include <asm/uaccess.h>
#include <asm/errno.h>
#include <asm/mman.h>
#include <net/sock.h>
#include <linux/file.h>
#include <linux/fs.h>
#include <linux/net.h>
#include <linux/in.h>
#include <linux/smp_lock.h>
#include <linux/slab.h>
#include <linux/types.h>
#include <linux/sched.h>
#include <linux/timer.h>
#include <linux/gracl.h>
#include <linux/grsecurity.h>
#include <linux/grinternal.h>

static struct crash_uid *uid_set;
static unsigned short uid_used;
static DEFINE_SPINLOCK(gr_uid_lock);
extern rwlock_t gr_inode_lock;
extern struct acl_subject_label *
	lookup_acl_subj_label(const ino_t inode, const dev_t dev,
			      struct acl_role_label *role);
extern int specific_send_sig_info(int sig, struct siginfo *info, struct task_struct *t);

int
gr_init_uidset(void)
{
	uid_set =
	    kmalloc(GR_UIDTABLE_MAX * sizeof (struct crash_uid), GFP_KERNEL);
	uid_used = 0;

	return uid_set ? 1 : 0;
}

void
gr_free_uidset(void)
{
	if (uid_set)
		kfree(uid_set);

	return;
}

int
gr_find_uid(const uid_t uid)
{
	struct crash_uid *tmp = uid_set;
	uid_t buid;
	int low = 0, high = uid_used - 1, mid;

	while (high >= low) {
		mid = (low + high) >> 1;
		buid = tmp[mid].uid;
		if (buid == uid)
			return mid;
		if (buid > uid)
			high = mid - 1;
		if (buid < uid)
			low = mid + 1;
	}

	return -1;
}

static __inline__ void
gr_insertsort(void)
{
	unsigned short i, j;
	struct crash_uid index;

	for (i = 1; i < uid_used; i++) {
		index = uid_set[i];
		j = i;
		while ((j > 0) && uid_set[j - 1].uid > index.uid) {
			uid_set[j] = uid_set[j - 1];
			j--;
		}
		uid_set[j] = index;
	}

	return;
}

static __inline__ void
gr_insert_uid(const uid_t uid, const unsigned long expires)
{
	int loc;

	if (uid_used == GR_UIDTABLE_MAX)
		return;

	loc = gr_find_uid(uid);

	if (loc >= 0) {
		uid_set[loc].expires = expires;
		return;
	}

	uid_set[uid_used].uid = uid;
	uid_set[uid_used].expires = expires;
	uid_used++;

	gr_insertsort();

	return;
}

void
gr_remove_uid(const unsigned short loc)
{
	unsigned short i;

	for (i = loc + 1; i < uid_used; i++)
		uid_set[i - 1] = uid_set[i];

	uid_used--;

	return;
}

int
gr_check_crash_uid(const uid_t uid)
{
	int loc;
	int ret = 0;

	if (unlikely(!gr_acl_is_enabled()))
		return 0;

	spin_lock(&gr_uid_lock);
	loc = gr_find_uid(uid);

	if (loc < 0)
		goto out_unlock;

	if (time_before_eq(uid_set[loc].expires, get_seconds()))
		gr_remove_uid(loc);
	else
		ret = 1;

out_unlock:
	spin_unlock(&gr_uid_lock);
	return ret;
}

static __inline__ int
proc_is_setxid(const struct task_struct *task)
{
	if (task->uid != task->euid || task->uid != task->suid ||
	    task->uid != task->fsuid)
		return 1;
	if (task->gid != task->egid || task->gid != task->sgid ||
	    task->gid != task->fsgid)
		return 1;

	return 0;
}
static __inline__ int
gr_fake_force_sig(int sig, struct task_struct *t)
{
	unsigned long int flags;
	int ret, blocked, ignored;
	struct k_sigaction *action;

	spin_lock_irqsave(&t->sighand->siglock, flags);
	action = &t->sighand->action[sig-1];
	ignored = action->sa.sa_handler == SIG_IGN;
	blocked = sigismember(&t->blocked, sig);
	if (blocked || ignored) {
		action->sa.sa_handler = SIG_DFL;
		if (blocked) {
			sigdelset(&t->blocked, sig);
			recalc_sigpending_and_wake(t);
		}
	}
	if (action->sa.sa_handler == SIG_DFL)
		t->signal->flags &= ~SIGNAL_UNKILLABLE;
	ret = specific_send_sig_info(sig, SEND_SIG_PRIV, t);

	spin_unlock_irqrestore(&t->sighand->siglock, flags);

	return ret;
}

void
gr_handle_crash(struct task_struct *task, const int sig)
{
	struct acl_subject_label *curr;
	struct acl_subject_label *curr2;
	struct task_struct *tsk, *tsk2;

	if (sig != SIGSEGV && sig != SIGKILL && sig != SIGBUS && sig != SIGILL)
		return;

	if (unlikely(!gr_acl_is_enabled()))
		return;

	curr = task->acl;

	if (!(curr->resmask & (1 << GR_CRASH_RES)))
		return;

	if (time_before_eq(curr->expires, get_seconds())) {
		curr->expires = 0;
		curr->crashes = 0;
	}

	curr->crashes++;

	if (!curr->expires)
		curr->expires = get_seconds() + curr->res[GR_CRASH_RES].rlim_max;

	if ((curr->crashes >= curr->res[GR_CRASH_RES].rlim_cur) &&
	    time_after(curr->expires, get_seconds())) {
		if (task->uid && proc_is_setxid(task)) {
			gr_log_crash1(GR_DONT_AUDIT, GR_SEGVSTART_ACL_MSG, task, curr->res[GR_CRASH_RES].rlim_max);
			spin_lock(&gr_uid_lock);
			gr_insert_uid(task->uid, curr->expires);
			spin_unlock(&gr_uid_lock);
			curr->expires = 0;
			curr->crashes = 0;
			read_lock(&tasklist_lock);
			do_each_thread(tsk2, tsk) {
				if (tsk != task && tsk->uid == task->uid)
					gr_fake_force_sig(SIGKILL, tsk);
			} while_each_thread(tsk2, tsk);
			read_unlock(&tasklist_lock);
		} else {
			gr_log_crash2(GR_DONT_AUDIT, GR_SEGVNOSUID_ACL_MSG, task, curr->res[GR_CRASH_RES].rlim_max);
			read_lock(&tasklist_lock);
			do_each_thread(tsk2, tsk) {
				if (likely(tsk != task)) {
					curr2 = tsk->acl;

					if (curr2->device == curr->device &&
					    curr2->inode == curr->inode)
						gr_fake_force_sig(SIGKILL, tsk);
				}
			} while_each_thread(tsk2, tsk);
			read_unlock(&tasklist_lock);
		}
	}

	return;
}

int
gr_check_crash_exec(const struct file *filp)
{
	struct acl_subject_label *curr;

	if (unlikely(!gr_acl_is_enabled()))
		return 0;

	read_lock(&gr_inode_lock);
	curr = lookup_acl_subj_label(filp->f_path.dentry->d_inode->i_ino,
				     filp->f_path.dentry->d_inode->i_sb->s_dev,
				     current->role);
	read_unlock(&gr_inode_lock);

	if (!curr || !(curr->resmask & (1 << GR_CRASH_RES)) ||
	    (!curr->crashes && !curr->expires))
		return 0;

	if ((curr->crashes >= curr->res[GR_CRASH_RES].rlim_cur) &&
	    time_after(curr->expires, get_seconds()))
		return 1;
	else if (time_before_eq(curr->expires, get_seconds())) {
		curr->crashes = 0;
		curr->expires = 0;
	}

	return 0;
}

void
gr_handle_alertkill(struct task_struct *task)
{
	struct acl_subject_label *curracl;
	__u32 curr_ip;
	struct task_struct *p, *p2;

	if (unlikely(!gr_acl_is_enabled()))
		return;

	curracl = task->acl;
	curr_ip = task->signal->curr_ip;

	if ((curracl->mode & GR_KILLIPPROC) && curr_ip) {
		read_lock(&tasklist_lock);
		do_each_thread(p2, p) {
			if (p->signal->curr_ip == curr_ip)
				gr_fake_force_sig(SIGKILL, p);
		} while_each_thread(p2, p);
		read_unlock(&tasklist_lock);
	} else if (curracl->mode & GR_KILLPROC)
		gr_fake_force_sig(SIGKILL, task);

	return;
}
