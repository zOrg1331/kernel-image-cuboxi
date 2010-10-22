/*
 * Hardware error record persistent support
 *
 * Normally, corrected hardware error records will go through the
 * kernel processing and be logged to disk or network finally.  But
 * for uncorrected errors, system may go panic directly for better
 * error containment, disk or network is not usable in this
 * half-working system.  To avoid losing these valuable hardware error
 * records, the error records are saved into some kind of simple
 * persistent storage such as flash before panic, so that they can be
 * read out after system reboot successfully.
 *
 * Copyright 2010 Intel Corp.
 *   Author: Huang Ying <ying.huang@intel.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version
 * 2 as published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/rculist.h>
#include <linux/mutex.h>

#include <linux/herror.h>

#include "herr-internal.h"

/*
 * Simple persistent storage provider list, herr_persists_mutex is
 * used for writer side mutual exclusion, RCU is used to implement
 * lock-less reader side.
 */
static LIST_HEAD(herr_persists);
static DEFINE_MUTEX(herr_persists_mutex);

int herr_persist_register(struct herr_persist *persist)
{
	if (!persist->peek_user)
		return -EINVAL;
	persist->read_done = 0;
	if (mutex_lock_interruptible(&herr_persists_mutex))
		return -EINTR;
	list_add_rcu(&persist->list, &herr_persists);
	mutex_unlock(&herr_persists_mutex);
	/*
	 * There may be hardware error records of previous boot in
	 * persistent storage, notify the user space error daemon to
	 * check.
	 */
	set_bit(HERR_NOTIFY_BIT, &herr_flags);
	herr_notify();
	return 0;
}
EXPORT_SYMBOL_GPL(herr_persist_register);

void herr_persist_unregister(struct herr_persist *persist)
{
	mutex_lock(&herr_persists_mutex);
	list_del_rcu(&persist->list);
	mutex_unlock(&herr_persists_mutex);
	synchronize_rcu();
}
EXPORT_SYMBOL_GPL(herr_persist_unregister);

/* Can be used in atomic context including NMI */
int herr_persist_in(const struct herr_record *ercd)
{
	struct herr_persist *persist;
	int rc = -ENODEV;

	rcu_read_lock();
	list_for_each_entry_rcu(persist, &herr_persists, list) {
		if (!persist->in)
			continue;
		rc = persist->in(ercd);
		if (!rc)
			break;
	}
	rcu_read_unlock();
	return rc;
}
EXPORT_SYMBOL_GPL(herr_persist_in);

int herr_persist_read_done(void)
{
	struct herr_persist *persist;
	int rc = 1;

	rcu_read_lock();
	list_for_each_entry_rcu(persist, &herr_persists, list) {
		if (!persist->read_done) {
			rc = 0;
			break;
		}
	}
	rcu_read_unlock();
	return rc;
}

/* Read next error record from persist storage, don't remove it */
ssize_t herr_persist_peek_user(u64 *record_id, char __user *ercd,
			       size_t bufsiz)
{
	struct herr_persist *persist;
	ssize_t rc = 0;

	if (mutex_lock_interruptible(&herr_persists_mutex))
		return -EINTR;
	list_for_each_entry(persist, &herr_persists, list) {
		if (persist->read_done)
			continue;
		rc = persist->peek_user(record_id, ercd, bufsiz);
		if (rc > 0)
			break;
		else if (rc != -EINTR && rc != -EAGAIN && rc != -EINVAL)
			persist->read_done = 1;
	}
	mutex_unlock(&herr_persists_mutex);
	return rc;
}

/* Clear specified error record from persist storage */
int herr_persist_clear(u64 record_id)
{
	struct herr_persist *persist;
	int rc = -ENOENT;

	if (mutex_lock_interruptible(&herr_persists_mutex))
		return -EINTR;
	list_for_each_entry(persist, &herr_persists, list) {
		if (!persist->clear)
			continue;
		rc = persist->clear(record_id);
		if (!rc)
			break;
		/*
		 * Failed to clear, mark as read_done, because we can
		 * not skip this one
		 */
		else if (rc != -EINTR && rc != -EAGAIN && rc != -ENOENT)
			persist->read_done = 1;
	}
	mutex_unlock(&herr_persists_mutex);
	return rc;
}

static int herr_persist_record(struct herr_record *ercd, void *data)
{
	int *severity = data;

	if (ercd->severity == *severity)
		return herr_persist_in(ercd);
	return 0;
}

void herr_persist_all_records(void)
{
	int severity;

	for (severity = HERR_SEV_FATAL; severity >= HERR_SEV_NONE; severity--)
		herr_for_each_record(herr_persist_record, &severity);
}
EXPORT_SYMBOL_GPL(herr_persist_all_records);
