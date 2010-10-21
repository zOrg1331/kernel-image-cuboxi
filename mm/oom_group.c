#include <linux/module.h>
#include <linux/sched.h>
#include <linux/proc_fs.h>
#include <asm/uaccess.h>
#include <linux/seq_file.h>
#include <linux/ctype.h>

static LIST_HEAD(oom_group_list_head);
static DEFINE_RWLOCK(oom_group_lock);

struct oom_group_pattern {
	char comm[TASK_COMM_LEN], pcomm[TASK_COMM_LEN];
	uid_t uid;
	int oom_group;
	struct list_head group_list;
};

int get_oom_group(struct task_struct *t)
{
	struct oom_group_pattern *gp;

	read_lock(&oom_group_lock);
	list_for_each_entry(gp, &oom_group_list_head, group_list) {
		if (strncmp(gp->comm, t->comm, strlen(gp->comm)))
			continue;
		if (strncmp(gp->pcomm, t->parent->comm, strlen(gp->pcomm)))
			continue;
		if (gp->uid != (uid_t)-1LL && gp->uid != task_uid(t))
			continue;
		read_unlock(&oom_group_lock);
		return gp->oom_group;
	}
	read_unlock(&oom_group_lock);
	return 0;
}

static int __oom_group_del_entry(struct oom_group_pattern *g)
{
	struct oom_group_pattern *tmp;

	list_for_each_entry(tmp, &oom_group_list_head, group_list) {
		if (strcmp(tmp->comm, g->comm))
			continue;
		if (strcmp(tmp->pcomm, g->pcomm))
			continue;
		if (tmp->uid != g->uid)
			continue;

		list_del(&tmp->group_list);
		kfree(tmp);
		return 0;
	}
	return -ENOENT;
}

static int oom_group_del_entry(struct oom_group_pattern *g)
{
	int ret;

	write_lock(&oom_group_lock);
	ret = __oom_group_del_entry(g);
	write_unlock(&oom_group_lock);
	return ret;
}

static void oom_group_add_entry(struct oom_group_pattern *g)
{
	write_lock(&oom_group_lock);
	__oom_group_del_entry(g);
	list_add(&g->group_list, &oom_group_list_head);
	write_unlock(&oom_group_lock);
}

static char *nextline(char *s)
{
	while(*s && *s != '\n') s++;
	while(*s && *s == '\n') s++;
	return s;
}

static int commcpy(char *comm, char **str)
{
	char *s = *str;
	int width = TASK_COMM_LEN - 1;

	while (*s && isspace(*s) && *s != '\n')
		s++;
	if (!*s || *s == '\n')
		return -EINVAL;

	*str = s;
	while (*s && !isspace(*s) && *s != '\n' && width--)
		*comm++ = *s++;

	if (s - *str == 1 && *(comm - 1) == '*')
		comm--;
	*comm = '\0';
	*str = s;
	if (width < 0)
		return -EINVAL;
	return 0;
}

static int str_to_pattern(struct oom_group_pattern *g, char *str, int add)
{
	int err;
	char *end;

	err = commcpy(g->comm, &str);
	if (err)
		return err;
	err = commcpy(g->pcomm, &str);
	if (err)
		return err;

	while (isspace(*str))
		str++;

	g->uid = simple_strtoll(str, &end, 0);
	if (end == str)
		return -EINVAL;
	str = end;
	while (isspace(*str))
		str++;

	g->oom_group = simple_strtol(str, &end, 0);
	if (add && end == str)
		return -EINVAL;

	while (isspace(*end))
		end++;
	if (*end != '\0' && *end != '\n')
		return -EINVAL;
	return 0;
}

static int oom_group_parse_line(char *line)
{
	int err, add;
	struct oom_group_pattern *g;

	if (*line == '+')
		add = 1;
	else if (*line == '-')
		add = 0;
	else
		return -EINVAL;

	g = kmalloc(sizeof(struct oom_group_pattern), GFP_KERNEL);
	if (g == NULL)
		return -ENOMEM;

	err = str_to_pattern(g, line + 1, add);
	if (err)
		goto free;

	if (add) {
		oom_group_add_entry(g);
		g = NULL;
	} else
		err = oom_group_del_entry(g);

free:
	kfree(g);
	return err;
}

static ssize_t oom_group_write(struct file * file, const char __user *buf,
				size_t count, loff_t *ppos)
{
	char *s, *page;
	int err;
	int offset;

	page = (unsigned char *)__get_free_page(GFP_KERNEL);
	if (!page)
		return -ENOMEM;

	if (count > (PAGE_SIZE - 1))
		count = (PAGE_SIZE - 1);

	err = copy_from_user(page, buf, count);
	if (err)
		goto err;

	s = page;
	s[count] = '\0';

	while (*s) {
		err = oom_group_parse_line(s);
		if (err)
			break;

		s = nextline(s);
	}

	offset = s - page;
	if (offset > 0)
		err = offset;
err:
	free_page((unsigned long)page);
	return err;
}

static void *oom_group_seq_start(struct seq_file *seq, loff_t *pos)
{
	unsigned int n = *pos;
	struct list_head *entry;

	n = *pos;
	read_lock(&oom_group_lock);
	list_for_each(entry, &oom_group_list_head)
		if (n-- == 0)
			return entry;
	return NULL;
}
static void oom_group_seq_stop(struct seq_file *s, void *v)
{
	read_unlock(&oom_group_lock);
}

#define COMM_TO_STR(s) (*s == '\0' ? "*" : s)

static int oom_group_seq_show(struct seq_file *s, void *v)
{
	struct list_head *entry = v;
	struct oom_group_pattern *p;

	p = list_entry(entry, struct oom_group_pattern, group_list);
	seq_printf(s, "%s %s %d %d\n",
		COMM_TO_STR(p->comm), COMM_TO_STR(p->pcomm),
		(int)p->uid, p->oom_group);
	return 0;
}

static void *oom_group_seq_next(struct seq_file *seq, void *v, loff_t *pos)
{
	struct list_head *entry;

	entry = (struct list_head *)v;
	(*pos)++;
	return entry->next == &oom_group_list_head ? NULL : entry->next;
}

static struct seq_operations oom_group_seq_ops = {
	.start = oom_group_seq_start,
	.next  = oom_group_seq_next,
	.stop  = oom_group_seq_stop,
	.show  = oom_group_seq_show,
};

static int oom_group_seq_open(struct inode *inode, struct file *file)
{
	return seq_open(file, &oom_group_seq_ops);
}

static struct file_operations proc_oom_group_ops = {
	.owner   = THIS_MODULE,
	.open    = oom_group_seq_open,
	.read    = seq_read,
	.llseek  = seq_lseek,
	.release = seq_release,
	.write   = oom_group_write,
};

static int __init oom_group_init(void) {
	struct proc_dir_entry *proc;

	proc = proc_create("oom_groups", 0660, NULL, &proc_oom_group_ops);
	if (!proc)
		return -ENOMEM;
	return 0;
}

module_init(oom_group_init);
