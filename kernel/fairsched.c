/*
 * Fair Scheduler
 *
 * Copyright (C) 2000-2008  SWsoft
 * All rights reserved.
 *
 * Licensing governed by "linux/COPYING.SWsoft" file.
 *
 */

#include <linux/module.h>
#include <linux/sched.h>
#include <linux/err.h>
#include <linux/mount.h>
#include <linux/cgroup.h>
#include <linux/pid_namespace.h>
#include <linux/syscalls.h>
#include <linux/fairsched.h>

static struct cgroup *fairsched_root;

SYSCALL_DEFINE3(fairsched_mknod, unsigned int, parent, unsigned int, weight,
				 unsigned int, newid)
{
	struct cgroup *node;
	int retval;
	char name[16];

	if (!capable_setveid())
		return -EPERM;

	retval = -EINVAL;
	if (weight < 1 || weight > FSCHWEIGHT_MAX)
		goto out;
	if (newid < 0 || newid > INT_MAX)
		goto out;

	snprintf(name, sizeof(name), "%d", newid);
	node = cgroup_kernel_open(fairsched_root, CGRP_CREAT|CGRP_EXCL, name);
	if (IS_ERR(node))
		return PTR_ERR(node);
	cgroup_kernel_close(node);
	retval = newid;
out:
	return retval;
}

SYSCALL_DEFINE1(fairsched_rmnod, unsigned int, id)
{
	char name[16];

	if (!capable_setveid())
		return -EPERM;

	snprintf(name, sizeof(name), "%d", id);
	return cgroup_kernel_remove(fairsched_root, name);
}

SYSCALL_DEFINE2(fairsched_chwt, unsigned int, id, unsigned, weight)
{
	struct cgroup *cgrp;
	char name[16];

	if (!capable_setveid())
		return -EPERM;

	if (id == 0)
		return -EINVAL;
	if (weight < 1 || weight > FSCHWEIGHT_MAX)
		return -EINVAL;

	snprintf(name, sizeof(name), "%d", id);
	cgrp = cgroup_kernel_open(fairsched_root, 0, name);
	if (IS_ERR(cgrp))
		return PTR_ERR(cgrp);
	if (cgrp == NULL)
		return -ENOENT;

	sched_cgroup_set_shares(cgrp, FSCHWEIGHT_BASE / weight);
	cgroup_kernel_close(cgrp);

	return 0;
}

SYSCALL_DEFINE2(fairsched_vcpus, unsigned int, id, unsigned int, vcpus)
{
	struct cgroup *cgrp;
	char name[16];

	if (!capable_setveid())
		return -EPERM;

	if (id == 0)
		return -EINVAL;

	snprintf(name, sizeof(name), "%d", id);
	cgrp = cgroup_kernel_open(fairsched_root, 0, name);
	if (IS_ERR(cgrp))
		return PTR_ERR(cgrp);
	if (cgrp == NULL)
		return -ENOENT;
	cgroup_kernel_close(cgrp);

	return 0;
}

SYSCALL_DEFINE3(fairsched_rate, unsigned int, id, int, op, unsigned, rate)
{
	struct cgroup *cgrp;
	char name[16];
	long ret;

	if (!capable_setveid())
		return -EPERM;

	if (id == 0)
		return -EINVAL;
	if (op == FAIRSCHED_SET_RATE && (rate < 1 || rate >= (1UL << 31)))
		return -EINVAL;


	snprintf(name, sizeof(name), "%d", id);
	cgrp = cgroup_kernel_open(fairsched_root, 0, name);
	if (IS_ERR(cgrp))
		return PTR_ERR(cgrp);
	if (cgrp == NULL)
		return -ENOENT;

	switch (op) {
		case FAIRSCHED_SET_RATE:
			ret = rate;
			break;
		case FAIRSCHED_DROP_RATE:
			ret = 0;
			break;
		case FAIRSCHED_GET_RATE:
			ret = -ENODATA;
			break;
		default:
			ret = -EINVAL;
			break;
	}
	cgroup_kernel_close(cgrp);

	return ret;
}

SYSCALL_DEFINE2(fairsched_mvpr, pid_t, pid, unsigned int, id)
{
	struct cgroup *cgrp;
	struct task_struct *tsk;
	char name[16];

	if (!capable_setveid())
		return -EPERM;

	snprintf(name, sizeof(name), "%d", id);
	cgrp = cgroup_kernel_open(fairsched_root, 0, name);
	if (IS_ERR(cgrp))
		return PTR_ERR(cgrp);
	if (cgrp == NULL)
		return -ENOENT;

	write_lock_irq(&tasklist_lock);
	tsk = find_task_by_vpid(pid);
	if (tsk == NULL) {
		write_unlock_irq(&tasklist_lock);
		cgroup_kernel_close(cgrp);
		return -ESRCH;
	}
	get_task_struct(tsk);
	write_unlock_irq(&tasklist_lock);

	cgroup_lock();
	cgroup_attach_task(cgrp, tsk);
	cgroup_unlock();

	cgroup_kernel_close(cgrp);
	put_task_struct(tsk);

	return 0;
}

int fairsched_new_node(int id, unsigned int vcpus)
{
	struct cgroup *cgrp;
	int err;
	char name[16];

	snprintf(name, sizeof(name), "%d", id);
	cgrp = cgroup_kernel_open(fairsched_root, CGRP_CREAT, name);
	err = PTR_ERR(cgrp);
	if (IS_ERR(cgrp)) {
		printk(KERN_WARNING "Can't create fairsched node %d\n", id);
		goto out;
	}

#if 0
	err = do_fairsched_vcpus(id, vcpus);
	if (err) {
		printk(KERN_WARNING "Can't set sched vcpus on node %d\n", id);
		goto cleanup;
	}
#endif

	cgroup_lock();
	err = cgroup_attach_task(cgrp, current);
	cgroup_unlock();
	cgroup_kernel_close(cgrp);
	if (err) {
		printk(KERN_WARNING "Can't switch to fairsched node %d\n", id);
		goto cleanup;
	}

	return 0;

cleanup:
	if (cgroup_kernel_remove(fairsched_root, name))
		printk(KERN_ERR "Can't clean fairsched node %d\n", id);
out:
	return err;
}
EXPORT_SYMBOL(fairsched_new_node);

void fairsched_drop_node(int id)
{
	char name[16];

	snprintf(name, sizeof(name), "%d", id);
	if (cgroup_kernel_remove(fairsched_root, name))
		printk(KERN_ERR "Can't remove fairsched node %d\n", id);
}
EXPORT_SYMBOL(fairsched_drop_node);

int fairsched_move_task(int id, struct task_struct *tsk)
{
	struct cgroup *cgrp;
	char name[16];

	snprintf(name, sizeof(name), "%d", id);
	cgrp = cgroup_kernel_open(fairsched_root, 0, name);
	if (IS_ERR(cgrp))
		return PTR_ERR(cgrp);
	if (cgrp == NULL)
		return -ENOENT;

	cgroup_lock();
	cgroup_attach_task(cgrp, tsk);
	cgroup_unlock();

	cgroup_kernel_close(cgrp);

	return 0;
}
EXPORT_SYMBOL(fairsched_move_task);

#ifdef CONFIG_PROC_FS

/*********************************************************************/
/*
 * proc interface
 */
/*********************************************************************/

#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/vmalloc.h>

struct fairsched_node_dump {
	int id;
	unsigned weight;
	unsigned rate;
	int nr_pcpu;
	int nr_tasks, nr_runtasks;
};

struct fairsched_dump {
	int len;
	struct fairsched_node_dump nodes[0];
};

static struct fairsched_dump *fairsched_do_dump(int compat)
{
	struct fairsched_dump *dump;
	struct fairsched_node_dump *p;
	int nr_nodes;
	struct dentry *root, *dentry;
	struct cgroup *cgrp;
	unsigned long id;
	char *endp;

	root = fairsched_root->dentry;
	mutex_lock(&root->d_inode->i_mutex);

	spin_lock(&dcache_lock);
	nr_nodes = 0;
	list_for_each_entry(dentry, &root->d_subdirs, d_u.d_child) {
		if (d_unhashed(dentry) || !dentry->d_inode ||
				!S_ISDIR(dentry->d_inode->i_mode))
			continue;
		nr_nodes++;
	}
	spin_unlock(&dcache_lock);

	nr_nodes = ve_is_super(get_exec_env()) ? nr_nodes + 16 : 1;

	dump = ub_vmalloc(sizeof(*dump) + nr_nodes * sizeof(dump->nodes[0]));
	if (dump == NULL)
		goto out;

	spin_lock(&dcache_lock);

	p = dump->nodes;
	list_for_each_entry(dentry, &root->d_subdirs, d_u.d_child) {
		if (d_unhashed(dentry) || !dentry->d_inode ||
				!S_ISDIR(dentry->d_inode->i_mode))
			continue;
		id = simple_strtoul(dentry->d_name.name, &endp, 10);
		if (*endp || id > INT_MAX)
			continue;
		if (!ve_accessible_veid(id, get_exec_env()->veid))
			continue;
		cgrp = dentry->d_fsdata; /* __d_cgrp */
		p->id = id;
		p->nr_tasks = cgroup_task_count(cgrp);
		p->nr_runtasks = sched_cgroup_get_nr_running(cgrp);
		p->weight = FSCHWEIGHT_BASE / sched_cgroup_get_shares(cgrp);
		p->nr_pcpu = num_online_cpus();
		p->rate = 0;
		p++;
		if (!--nr_nodes)
			break;
	}
	dump->len = p - dump->nodes;

	spin_unlock(&dcache_lock);
out:
	mutex_unlock(&root->d_inode->i_mutex);
	return dump;
}

#define FAIRSCHED_PROC_HEADLINES 2

#define FAIRSHED_DEBUG          " debug"

#ifdef CONFIG_VE
/*
 * File format is dictated by compatibility reasons.
 */
static int fairsched_seq_show(struct seq_file *m, void *v)
{
	struct fairsched_dump *dump;
	struct fairsched_node_dump *p;
	unsigned vid, nid, pid, r;

	dump = m->private;
	p = (struct fairsched_node_dump *)((unsigned long)v & ~3UL);
	if (p - dump->nodes < FAIRSCHED_PROC_HEADLINES) {
		if (p == dump->nodes)
			seq_printf(m, "Version: 2.6 debug\n");
		else if (p == dump->nodes + 1)
			seq_printf(m,
				       "      veid "
				       "        id "
				       "    parent "
				       "weight "
				       " rate "
				       "tasks "
				       "  run "
				       "cpus"
				       " "
				       "flg "
				       "ready "
				       "           start_tag "
				       "               value "
				       "               delay"
				       "\n");
	} else {
		p -= FAIRSCHED_PROC_HEADLINES;
		vid = nid = pid = 0;
		r = (unsigned long)v & 3;
		if (p == dump->nodes) {
			if (r == 2)
				nid = p->id;
		} else {
			if (!r)
				nid = p->id;
			else if (r == 1)
				vid = pid = p->id;
			else
				vid = p->id, nid = 1;
		}
		seq_printf(m,
			       "%10u "
			       "%10u %10u %6u %5u %5u %5u %4u"
			       " "
			       " %c%c %5u %20Lu %20Lu %20Lu"
			       "\n",
			       vid,
			       nid,
			       pid,
			       p->weight,
			       p->rate,
			       p->nr_tasks,
			       p->nr_runtasks,
			       p->nr_pcpu,
			       p->rate ? 'L' : '.',
			       '.',
			       p->nr_runtasks,
			       0ll, 0ll, 0ll);
	}

	return 0;
}

static void *fairsched_seq_start(struct seq_file *m, loff_t *pos)
{
	struct fairsched_dump *dump;
	unsigned long l;

	dump = m->private;
	if (*pos >= dump->len * 3 - 1 + FAIRSCHED_PROC_HEADLINES)
		return NULL;
	if (*pos < FAIRSCHED_PROC_HEADLINES)
		return dump->nodes + *pos;
	/* guess why... */
	l = (unsigned long)(dump->nodes +
		((unsigned long)*pos + FAIRSCHED_PROC_HEADLINES * 2 + 1) / 3);
	l |= ((unsigned long)*pos + FAIRSCHED_PROC_HEADLINES * 2 + 1) % 3;
	return (void *)l;
}
static void *fairsched_seq_next(struct seq_file *m, void *v, loff_t *pos)
{
	++*pos;
	return fairsched_seq_start(m, pos);
}
#endif /* CONFIG_VE */

static int fairsched2_seq_show(struct seq_file *m, void *v)
{
	struct fairsched_dump *dump;
	struct fairsched_node_dump *p;

	dump = m->private;
	p = v;
	if (p - dump->nodes < FAIRSCHED_PROC_HEADLINES) {
		if (p == dump->nodes)
			seq_printf(m, "Version: 2.7" FAIRSHED_DEBUG "\n");
		else if (p == dump->nodes + 1)
			seq_printf(m,
				       "        id "
				       "weight "
				       " rate "
				       "  run "
				       "cpus"
#ifdef FAIRSHED_DEBUG
				       " "
				       "flg "
				       "ready "
				       "           start_tag "
				       "               value "
				       "               delay"
#endif
				       "\n");
	} else {
		p -= FAIRSCHED_PROC_HEADLINES;
		seq_printf(m,
			       "%10u %6u %5u %5u %4u"
#ifdef FAIRSHED_DEBUG
			       " "
			       " %c%c %5u %20Lu %20Lu %20Lu"
#endif
			       "\n",
			       p->id,
			       p->weight,
			       p->rate,
			       p->nr_runtasks,
			       p->nr_pcpu
#ifdef FAIRSHED_DEBUG
			       ,
			       p->rate ? 'L' : '.',
			       '.',
			       p->nr_runtasks,
			       0ll, 0ll, 0ll
#endif
			       );
	}

	return 0;
}

static void *fairsched2_seq_start(struct seq_file *m, loff_t *pos)
{
	struct fairsched_dump *dump;

	dump = m->private;
	if (*pos >= dump->len + FAIRSCHED_PROC_HEADLINES)
		return NULL;
	return dump->nodes + *pos;
}
static void *fairsched2_seq_next(struct seq_file *m, void *v, loff_t *pos)
{
	++*pos;
	return fairsched2_seq_start(m, pos);
}
static void fairsched2_seq_stop(struct seq_file *m, void *v)
{
}

#ifdef CONFIG_VE
static struct seq_operations fairsched_seq_op = {
	.start		= fairsched_seq_start,
	.next		= fairsched_seq_next,
	.stop		= fairsched2_seq_stop,
	.show		= fairsched_seq_show
};
#endif
static struct seq_operations fairsched2_seq_op = {
	.start		= fairsched2_seq_start,
	.next		= fairsched2_seq_next,
	.stop		= fairsched2_seq_stop,
	.show		= fairsched2_seq_show
};
static int fairsched_seq_open(struct inode *inode, struct file *file)
{
	int ret;
	struct seq_file *m;
	int compat;

#ifdef CONFIG_VE
	compat = (file->f_dentry->d_name.len == sizeof("fairsched") - 1);
	ret = seq_open(file, compat ? &fairsched_seq_op : &fairsched2_seq_op);
#else
	compat = 0;
	ret = seq_open(file, &fairsched2_seq_op);
#endif
	if (ret)
		return ret;
	m = file->private_data;
	m->private = fairsched_do_dump(compat);
	if (m->private == NULL) {
		seq_release(inode, file);
		ret = -ENOMEM;
	}
	return ret;
}
static int fairsched_seq_release(struct inode *inode, struct file *file)
{
	struct seq_file *m;
	struct fairsched_dump *dump;

	m = file->private_data;
	dump = m->private;
	m->private = NULL;
	vfree(dump);
	seq_release(inode, file);
	return 0;
}
static struct file_operations proc_fairsched_operations = {
	.open		= fairsched_seq_open,
	.read		= seq_read,
	.llseek		= seq_lseek,
	.release	= fairsched_seq_release
};

#endif /* CONFIG_PROC_FS */

int __init fairsched_init(void)
{
	struct vfsmount *mnt;
	struct cgroup *cgrp;
	int ret;
	struct cgroup_sb_opts opts = {
		.subsys_bits	= 1ul << cpu_cgroup_subsys_id,
	};

	mnt = cgroup_kernel_mount(&opts);
	if (IS_ERR(mnt))
		return PTR_ERR(mnt);
	fairsched_root = cgroup_get_root(mnt);

	/* fairsched node INT_MAX for ve0 tasks */
	cgrp = cgroup_kernel_open(fairsched_root, CGRP_CREAT, "2147483647");
	if (IS_ERR(cgrp))
		return PTR_ERR(cgrp);
	ret = cgroup_kernel_attach(cgrp, init_pid_ns.child_reaper);
	if (ret)
		return ret;

#ifdef CONFIG_PROC_FS
	proc_create("fairsched", S_IRUGO, &glob_proc_root,
			&proc_fairsched_operations);
	proc_create("fairsched2", S_IRUGO, &glob_proc_root,
			&proc_fairsched_operations);
#endif /* CONFIG_PROC_FS */
	return 0;
}
late_initcall(fairsched_init);
