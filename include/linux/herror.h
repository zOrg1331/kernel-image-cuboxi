#ifndef LINUX_HERROR_H
#define LINUX_HERROR_H

#include <linux/ioctl.h>
#include <linux/herror_record.h>

struct herr_persist_buffer {
	void __user *buf;
	unsigned int buf_size;
};

#define HERR_PERSIST_PEEK	_IOW('H', 1, struct herr_persist_buffer)
#define HERR_PERSIST_CLEAR	_IOW('H', 2, u64)

#ifdef __KERNEL__

#include <linux/types.h>
#include <linux/list.h>
#include <linux/device.h>

/*
 * Hardware error reporting
 */

#define HERR_ALLOC_NO_BURST_CONTROL	0x0001

struct herr_dev;

/* allocate a herr_record lock-lessly */
struct herr_record *herr_record_alloc(unsigned int len,
				      struct herr_dev *edev,
				      unsigned int flags);
void herr_record_init(struct herr_record *ercd);
/* report error via error record */
int herr_record_report(struct herr_record *ercd, struct herr_dev *edev);
/* free the herr_record allocated before */
void herr_record_free(struct herr_record *ercd);
/*
 * Notify waited user space hardware error daemon for the new error
 * record, can not be used in NMI context
 */
void herr_notify(void);

/* Traverse all error records not consumed by user space */
typedef int (*herr_traverse_func_t)(struct herr_record *ercd, void *data);
int herr_for_each_record(herr_traverse_func_t func, void *data);


/*
 * Hardware Error Reporting Device Management
 */
extern struct class herr_class;

struct herr_dev {
	const char *name;
	atomic_t overflows;
	atomic_t logs;
	atomic_t bursts;
	struct device dev;
	struct list_head list;
	atomic64_t timestamp;
};
#define to_herr_dev(d)	container_of(d, struct herr_dev, dev)

struct herr_dev *herr_dev_alloc(void);
void herr_dev_free(struct herr_dev *dev);

static inline struct herr_dev *herr_dev_get(struct herr_dev *dev)
{
	return dev ? to_herr_dev(get_device(&dev->dev)) : NULL;
}

static inline void herr_dev_put(struct herr_dev *dev)
{
	if (dev)
		put_device(&dev->dev);
}

int herr_dev_register(struct herr_dev *dev);
void herr_dev_unregister(struct herr_dev *dev);


/*
 * Simple Persistent Storage
 */

struct herr_persist;
/* Put an error record into simple persistent storage */
int herr_persist_in(const struct herr_record *ercd);
/* Save all error records not yet consumed in persistent storage */
void herr_persist_all_records(void);

/*
 * Simple Persistent Storage Provider Management
 */
struct herr_persist {
	struct list_head list;
	char *name;
	unsigned int read_done:1;
	/* Put an error record into storage, must be NMI-safe */
	int (*in)(const struct herr_record *ercd);
	/*
	 * Read out an error record from storage to user space, don't
	 * remove it, the HERR_RCD_PERSIST must be set in record flags
	 */
	ssize_t (*peek_user)(u64 *record_id, char __user *ubuf, size_t usize);
	/* Clear an error record */
	int (*clear)(u64 record_id);
};

/* Register (un-register) simple persistent storage provider */
int herr_persist_register(struct herr_persist *persist);
void herr_persist_unregister(struct herr_persist *persist);
#endif
#endif
