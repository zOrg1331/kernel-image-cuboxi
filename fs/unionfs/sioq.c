/*
 * Copyright (c) 2003-2006 Erez Zadok
 * Copyright (c) 2003-2006 Charles P. Wright
 * Copyright (c) 2005-2006 Josef 'Jeff' Sipek
 * Copyright (c) 2005-2006 Junjiro Okajima
 * Copyright (c) 2005      Arun M. Krishnakumar
 * Copyright (c) 2004-2006 David P. Quigley
 * Copyright (c) 2003-2004 Mohammad Nayyer Zubair
 * Copyright (c) 2003      Puja Gupta
 * Copyright (c) 2003      Harikesavan Krishnan
 * Copyright (c) 2003-2006 Stony Brook University
 * Copyright (c) 2003-2006 The Research Foundation of State University of New York
 *
 * For specific licensing information, see the COPYING file distributed with
 * this package.
 *
 * This Copyright notice must be kept intact and distributed with all sources.
 */

#include "unionfs.h"

struct workqueue_struct *sioq;

int __init init_sioq(void)
{
	int err;

	sioq = create_workqueue("unionfs_siod");
	if (!IS_ERR(sioq))
		return 0;

	err = PTR_ERR(sioq);
	printk(KERN_ERR "create_workqueue failed %d\n", err);
	sioq = NULL;
	return err;
}

void fin_sioq(void)
{
	if (sioq)
		destroy_workqueue(sioq);
}

void run_sioq(void (*func)(void *arg), struct sioq_args *args)
{
	DECLARE_WORK(wk, func, &args->comp);

	init_completion(&args->comp);
	while (!queue_work(sioq, &wk)) {
		// TODO: do accounting if needed
		schedule();
	}
	wait_for_completion(&args->comp);
}

void __unionfs_create(void *data)
{
	struct sioq_args *args = data;
	struct create_args *c = &args->create;
	args->err = vfs_create(c->parent, c->dentry, c->mode, c->nd);
	complete(&args->comp);
}

void __unionfs_mkdir(void *data)
{
	struct sioq_args *args = data;
	struct mkdir_args *m = &args->mkdir;
	args->err = vfs_mkdir(m->parent, m->dentry, m->mode);
	complete(&args->comp);
}

void __unionfs_mknod(void *data)
{
	struct sioq_args *args = data;
	struct mknod_args *m = &args->mknod;
	args->err = vfs_mknod(m->parent, m->dentry, m->mode, m->dev);
	complete(&args->comp);
}
void __unionfs_symlink(void *data)
{
	struct sioq_args *args = data;
	struct symlink_args *s = &args->symlink;
	args->err = vfs_symlink(s->parent, s->dentry, s->symbuf, s->mode);
	complete(&args->comp);
}

void __unionfs_unlink(void *data)
{
	struct sioq_args *args = data;
	struct unlink_args *u = &args->unlink;
	args->err = vfs_unlink(u->parent, u->dentry);
	complete(&args->comp);
}

void __delete_whiteouts(void *data) {
	struct sioq_args *args = data;
	struct deletewh_args *d = &args->deletewh;
	args->err = delete_whiteouts(d->dentry, d->bindex, d->namelist);
	complete(&args->comp);
}

void __is_opaque_dir(void *data)
{
	struct sioq_args *args = data;

	args->ret = lookup_one_len(UNIONFS_DIR_OPAQUE, args->isopaque.dentry,
				sizeof(UNIONFS_DIR_OPAQUE) - 1);
	complete(&args->comp);
}
