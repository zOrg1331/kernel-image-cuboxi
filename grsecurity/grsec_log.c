#include <linux/kernel.h>
#include <linux/sched.h>
#include <linux/file.h>
#include <linux/tty.h>
#include <linux/fs.h>
#include <linux/grinternal.h>

#define BEGIN_LOCKS(x) \
	read_lock(&tasklist_lock); \
	read_lock(&grsec_exec_file_lock); \
	if (x != GR_DO_AUDIT) \
		spin_lock(&grsec_alert_lock); \
	else \
		spin_lock(&grsec_audit_lock)

#define END_LOCKS(x) \
	if (x != GR_DO_AUDIT) \
		spin_unlock(&grsec_alert_lock); \
	else \
		spin_unlock(&grsec_audit_lock); \
	read_unlock(&grsec_exec_file_lock); \
	read_unlock(&tasklist_lock); \
	if (x == GR_DONT_AUDIT) \
		gr_handle_alertkill(current)

enum {
	FLOODING,
	NO_FLOODING
};

extern char *gr_alert_log_fmt;
extern char *gr_audit_log_fmt;
extern char *gr_alert_log_buf;
extern char *gr_audit_log_buf;

static int gr_log_start(int audit)
{
	char *loglevel = (audit == GR_DO_AUDIT) ? KERN_INFO : KERN_ALERT;
	char *fmt = (audit == GR_DO_AUDIT) ? gr_audit_log_fmt : gr_alert_log_fmt;
	char *buf = (audit == GR_DO_AUDIT) ? gr_audit_log_buf : gr_alert_log_buf;

	if (audit == GR_DO_AUDIT)
		goto set_fmt;

	if (!grsec_alert_wtime || jiffies - grsec_alert_wtime > CONFIG_GRKERNSEC_FLOODTIME * HZ) {
		grsec_alert_wtime = jiffies;
		grsec_alert_fyet = 0;
	} else if ((jiffies - grsec_alert_wtime < CONFIG_GRKERNSEC_FLOODTIME * HZ) && (grsec_alert_fyet < CONFIG_GRKERNSEC_FLOODBURST)) {
		grsec_alert_fyet++;
	} else if (grsec_alert_fyet == CONFIG_GRKERNSEC_FLOODBURST) {
		grsec_alert_wtime = jiffies;
		grsec_alert_fyet++;
		printk(KERN_ALERT "grsec: more alerts, logging disabled for %d seconds\n", CONFIG_GRKERNSEC_FLOODTIME);
		return FLOODING;
	} else return FLOODING;

set_fmt:
	memset(buf, 0, PAGE_SIZE);
	if (current->signal->curr_ip && gr_acl_is_enabled()) {
		sprintf(fmt, "%s%s", loglevel, "grsec: From %u.%u.%u.%u: (%.64s:%c:%.950s) ");
		snprintf(buf, PAGE_SIZE - 1, fmt, NIPQUAD(current->signal->curr_ip), current->role->rolename, gr_roletype_to_char(), current->acl->filename);
	} else if (current->signal->curr_ip) {
		sprintf(fmt, "%s%s", loglevel, "grsec: From %u.%u.%u.%u: ");
		snprintf(buf, PAGE_SIZE - 1, fmt, NIPQUAD(current->signal->curr_ip));
	} else if (gr_acl_is_enabled()) {
		sprintf(fmt, "%s%s", loglevel, "grsec: (%.64s:%c:%.950s) ");
		snprintf(buf, PAGE_SIZE - 1, fmt, current->role->rolename, gr_roletype_to_char(), current->acl->filename);
	} else {
		sprintf(fmt, "%s%s", loglevel, "grsec: ");
		strcpy(buf, fmt);
	}

	return NO_FLOODING;
}

static void gr_log_middle(int audit, const char *msg, va_list ap)
{
	char *buf = (audit == GR_DO_AUDIT) ? gr_audit_log_buf : gr_alert_log_buf;
	unsigned int len = strlen(buf);

	vsnprintf(buf + len, PAGE_SIZE - len - 1, msg, ap);

	return;
}

static void gr_log_middle_varargs(int audit, const char *msg, ...)
{
	char *buf = (audit == GR_DO_AUDIT) ? gr_audit_log_buf : gr_alert_log_buf;
	unsigned int len = strlen(buf);
	va_list ap;

	va_start(ap, msg);
	vsnprintf(buf + len, PAGE_SIZE - len - 1, msg, ap);
	va_end(ap);

	return;
}

static void gr_log_end(int audit)
{
	char *buf = (audit == GR_DO_AUDIT) ? gr_audit_log_buf : gr_alert_log_buf;
	unsigned int len = strlen(buf);

	snprintf(buf + len, PAGE_SIZE - len - 1, DEFAULTSECMSG, DEFAULTSECARGS(current));
	printk("%s\n", buf);

	return;
}

void gr_log_varargs(int audit, const char *msg, int argtypes, ...)
{
	int logtype;
	char *result = (audit == GR_DO_AUDIT) ? "successful" : "denied";
	char *str1, *str2, *str3;
	int num1, num2;
	unsigned long ulong1, ulong2;
	struct dentry *dentry;
	struct vfsmount *mnt;
	struct file *file;
	struct task_struct *task;
	va_list ap;

	BEGIN_LOCKS(audit);
	logtype = gr_log_start(audit);
	if (logtype == FLOODING) {
		END_LOCKS(audit);
		return;
	}
	va_start(ap, argtypes);
	switch (argtypes) {
	case GR_TTYSNIFF:
		task = va_arg(ap, struct task_struct *);
		gr_log_middle_varargs(audit, msg, NIPQUAD(task->signal->curr_ip), gr_task_fullpath0(task), task->comm, task->pid, gr_parent_task_fullpath0(task), task->parent->comm, task->parent->pid);
		break;
	case GR_SYSCTL_HIDDEN:
		str1 = va_arg(ap, char *);
		gr_log_middle_varargs(audit, msg, result, str1);
		break;
	case GR_RBAC:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		gr_log_middle_varargs(audit, msg, result, gr_to_filename(dentry, mnt));
		break;
	case GR_RBAC_STR:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		str1 = va_arg(ap, char *);
		gr_log_middle_varargs(audit, msg, result, gr_to_filename(dentry, mnt), str1);
		break;
	case GR_STR_RBAC:
		str1 = va_arg(ap, char *);
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		gr_log_middle_varargs(audit, msg, result, str1, gr_to_filename(dentry, mnt));
		break;
	case GR_RBAC_MODE2:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		str1 = va_arg(ap, char *);
		str2 = va_arg(ap, char *);
		gr_log_middle_varargs(audit, msg, result, gr_to_filename(dentry, mnt), str1, str2);
		break;
	case GR_RBAC_MODE3:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		str1 = va_arg(ap, char *);
		str2 = va_arg(ap, char *);
		str3 = va_arg(ap, char *);
		gr_log_middle_varargs(audit, msg, result, gr_to_filename(dentry, mnt), str1, str2, str3);
		break;
	case GR_FILENAME:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		gr_log_middle_varargs(audit, msg, gr_to_filename(dentry, mnt));
		break;
	case GR_STR_FILENAME:
		str1 = va_arg(ap, char *);
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		gr_log_middle_varargs(audit, msg, str1, gr_to_filename(dentry, mnt));
		break;
	case GR_FILENAME_STR:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		str1 = va_arg(ap, char *);
		gr_log_middle_varargs(audit, msg, gr_to_filename(dentry, mnt), str1);
		break;
	case GR_FILENAME_TWO_INT:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		num1 = va_arg(ap, int);
		num2 = va_arg(ap, int);
		gr_log_middle_varargs(audit, msg, gr_to_filename(dentry, mnt), num1, num2);
		break;
	case GR_FILENAME_TWO_INT_STR:
		dentry = va_arg(ap, struct dentry *);
		mnt = va_arg(ap, struct vfsmount *);
		num1 = va_arg(ap, int);
		num2 = va_arg(ap, int);
		str1 = va_arg(ap, char *);
		gr_log_middle_varargs(audit, msg, gr_to_filename(dentry, mnt), num1, num2, str1);
		break;
	case GR_TEXTREL:
		file = va_arg(ap, struct file *);
		ulong1 = va_arg(ap, unsigned long);
		ulong2 = va_arg(ap, unsigned long);
		gr_log_middle_varargs(audit, msg, file ? gr_to_filename(file->f_path.dentry, file->f_path.mnt) : "<anonymous mapping>", ulong1, ulong2);
		break;
	case GR_PTRACE:
		task = va_arg(ap, struct task_struct *);
		gr_log_middle_varargs(audit, msg, task->exec_file ? gr_to_filename(task->exec_file->f_path.dentry, task->exec_file->f_path.mnt) : "(none)", task->comm, task->pid);
		break;
	case GR_RESOURCE:
		task = va_arg(ap, struct task_struct *);
		ulong1 = va_arg(ap, unsigned long);
		str1 = va_arg(ap, char *);
		ulong2 = va_arg(ap, unsigned long);
		gr_log_middle_varargs(audit, msg, ulong1, str1, ulong2, gr_task_fullpath(task), task->comm, task->pid, task->uid, task->euid, task->gid, task->egid, gr_parent_task_fullpath(task), task->parent->comm, task->parent->pid, task->parent->uid, task->parent->euid, task->parent->gid, task->parent->egid);
		break;
	case GR_CAP:
		task = va_arg(ap, struct task_struct *);
		str1 = va_arg(ap, char *);
		gr_log_middle_varargs(audit, msg, str1, gr_task_fullpath(task), task->comm, task->pid, task->uid, task->euid, task->gid, task->egid, gr_parent_task_fullpath(task), task->parent->comm, task->parent->pid, task->parent->uid, task->parent->euid, task->parent->gid, task->parent->egid);
		break;
	case GR_SIG:
		task = va_arg(ap, struct task_struct *);
		num1 = va_arg(ap, int);
		gr_log_middle_varargs(audit, msg, num1, gr_task_fullpath0(task), task->comm, task->pid, task->uid, task->euid, task->gid, task->egid, gr_parent_task_fullpath0(task), task->parent->comm, task->parent->pid, task->parent->uid, task->parent->euid, task->parent->gid, task->parent->egid);
		break;
	case GR_CRASH1:
		task = va_arg(ap, struct task_struct *);
		ulong1 = va_arg(ap, unsigned long);
		gr_log_middle_varargs(audit, msg, gr_task_fullpath(task), task->comm, task->pid, task->uid, task->euid, task->gid, task->egid, gr_parent_task_fullpath(task), task->parent->comm, task->parent->pid, task->parent->uid, task->parent->euid, task->parent->gid, task->parent->egid, task->uid, ulong1);
		break;
	case GR_CRASH2:
		task = va_arg(ap, struct task_struct *);
		ulong1 = va_arg(ap, unsigned long);
		gr_log_middle_varargs(audit, msg, gr_task_fullpath(task), task->comm, task->pid, task->uid, task->euid, task->gid, task->egid, gr_parent_task_fullpath(task), task->parent->comm, task->parent->pid, task->parent->uid, task->parent->euid, task->parent->gid, task->parent->egid, ulong1);
		break;
	case GR_PSACCT:
		{
			unsigned int wday, cday;
			__u8 whr, chr;
			__u8 wmin, cmin;
			__u8 wsec, csec;
			char cur_tty[64] = { 0 };
			char parent_tty[64] = { 0 };

			task = va_arg(ap, struct task_struct *);
			wday = va_arg(ap, unsigned int);
			cday = va_arg(ap, unsigned int);
			whr = va_arg(ap, int);
			chr = va_arg(ap, int);
			wmin = va_arg(ap, int);
			cmin = va_arg(ap, int);
			wsec = va_arg(ap, int);
			csec = va_arg(ap, int);
			ulong1 = va_arg(ap, unsigned long);

			gr_log_middle_varargs(audit, msg, gr_task_fullpath(task), task->comm, task->pid, NIPQUAD(task->signal->curr_ip), tty_name(task->signal->tty, cur_tty), task->uid, task->euid, task->gid, task->egid, wday, whr, wmin, wsec, cday, chr, cmin, csec, (task->flags & PF_SIGNALED) ? "killed by signal" : "exited", ulong1, gr_parent_task_fullpath(task), task->parent->comm, task->parent->pid, NIPQUAD(task->parent->signal->curr_ip), tty_name(task->parent->signal->tty, parent_tty), task->parent->uid, task->parent->euid, task->parent->gid, task->parent->egid);
		}
		break;
	default:
		gr_log_middle(audit, msg, ap);
	}
	va_end(ap);
	gr_log_end(audit);
	END_LOCKS(audit);
}
