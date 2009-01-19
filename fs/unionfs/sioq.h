#ifndef _SIOQ_H
#define _SIOQ_H

struct deletewh_args {
	struct unionfs_dir_state *namelist;
	struct dentry *dentry;
	int bindex;
};

struct isopaque_args {
	struct dentry *dentry;
};

struct create_args {
	struct inode *parent;
	struct dentry *dentry;
	umode_t mode;
	struct nameidata *nd;
};

struct mkdir_args {
	struct inode *parent;
	struct dentry *dentry;
	umode_t mode;
};

struct mknod_args {
	struct inode *parent;
	struct dentry *dentry;
	umode_t mode;
	dev_t dev;
};

struct symlink_args {
	struct inode *parent;
	struct dentry *dentry;
	char *symbuf;
	umode_t mode;
};

struct unlink_args {
	struct inode *parent;
	struct dentry *dentry;
};


struct sioq_args {

	struct completion comp;
	int err;
	void *ret;

	union {
		struct deletewh_args deletewh;
		struct isopaque_args isopaque;
		struct create_args create;
		struct mkdir_args mkdir;
		struct mknod_args mknod;
		struct symlink_args symlink;
		struct unlink_args unlink;
	}; //} u;
};

extern struct workqueue_struct *sioq;
int __init init_sioq(void);
extern void fin_sioq(void);
extern void run_sioq(void (*func)(void *arg), struct sioq_args *args);

/* Extern definitions for our privledge escalation helpers */
extern void __unionfs_create(void *data);
extern void __unionfs_mkdir(void *data);
extern void __unionfs_mknod(void *data);
extern void __unionfs_symlink(void *data);
extern void __unionfs_unlink(void *data);
extern void __delete_whiteouts(void *data);
extern void __is_opaque_dir(void *data);

#endif /* _SIOQ_H */

