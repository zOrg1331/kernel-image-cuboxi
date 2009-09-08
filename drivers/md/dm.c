/*
 * Copyright (C) 2001, 2002 Sistina Software (UK) Limited.
 * Copyright (C) 2004-2006 Red Hat, Inc. All rights reserved.
 *
 * This file is released under the GPL.
 */

#include "dm.h"
#include "dm-bio-list.h"
#include "dm-uevent.h"

#include <linux/init.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/moduleparam.h>
#include <linux/blkpg.h>
#include <linux/bio.h>
#include <linux/buffer_head.h>
#include <linux/mempool.h>
#include <linux/slab.h>
#include <linux/idr.h>
#include <linux/hdreg.h>
#include <linux/blktrace_api.h>
#include <linux/smp_lock.h>

#define DM_MSG_PREFIX "core"

static const char *_name = DM_NAME;

static unsigned int major = 0;
static unsigned int _major = 0;

static DEFINE_SPINLOCK(_minor_lock);
/*
 * For bio based dm.
 * One of these is allocated per bio.
 */
struct dm_io {
	struct mapped_device *md;
	int error;
	atomic_t io_count;
	struct bio *bio;
	unsigned long start_time;
};

/*
 * For bio based dm.
 * One of these is allocated per target within a bio.  Hopefully
 * this will be simplified out one day.
 */
struct dm_target_io {
	struct dm_io *io;
	struct dm_target *ti;
	union map_info info;
};

/*
 * For request based dm.
 * One of these is allocated per request.
 *
 * Since assuming "original request : cloned request = 1 : 1" and
 * a counter for number of clones like struct dm_io.io_count isn't needed,
 * struct dm_io and struct target_io can be merged.
 */
struct dm_rq_target_io {
	struct mapped_device *md;
	struct dm_target *ti;
	struct request *orig, clone;
	int error;
	union map_info info;
};

/*
 * For request based dm.
 * One of these is allocated per bio.
 */
struct dm_clone_bio_info {
	struct bio *orig;
	struct request *rq;
};

union map_info *dm_get_mapinfo(struct bio *bio)
{
	if (bio && bio->bi_private)
		return &((struct dm_target_io *)bio->bi_private)->info;
	return NULL;
}

union map_info *dm_get_rq_mapinfo(struct request *rq)
{
	if (rq && rq->end_io_data)
		return &((struct dm_rq_target_io *)rq->end_io_data)->info;
	return NULL;
}
EXPORT_SYMBOL_GPL(dm_get_rq_mapinfo);

#define MINOR_ALLOCED ((void *)-1)

/*
 * Bits for the md->flags field.
 */
#define DMF_BLOCK_IO 0
#define DMF_SUSPENDED 1
#define DMF_FROZEN 2
#define DMF_FREEING 3
#define DMF_DELETING 4
#define DMF_NOFLUSH_SUSPENDING 5

/*
 * Work processed by per-device workqueue.
 */
struct dm_wq_req {
	enum {
		DM_WQ_FLUSH_DEFERRED,
	} type;
	struct work_struct work;
	struct mapped_device *md;
	void *context;
};

struct mapped_device {
	struct rw_semaphore io_lock;
	struct mutex suspend_lock;
	spinlock_t pushback_lock;
	rwlock_t map_lock;
	atomic_t holders;
	atomic_t open_count;

	unsigned long flags;

	struct request_queue *queue;
	struct gendisk *disk;
	char name[16];

	void *interface_ptr;

	/*
	 * A list of ios that arrived while we were suspended.
	 */
	atomic_t pending;
	wait_queue_head_t wait;
	struct bio_list deferred;
	struct bio_list pushback;

	/*
	 * Processing queue (flush/barriers)
	 */
	struct workqueue_struct *wq;

	/*
	 * The current mapping.
	 */
	struct dm_table *map;

	/*
	 * io objects are allocated from here.
	 */
	mempool_t *io_pool;
	mempool_t *tio_pool;

	struct bio_set *bs;

	unsigned int mempool_type; /* Type of mempools above. */

	/*
	 * Event handling.
	 */
	atomic_t event_nr;
	wait_queue_head_t eventq;
	atomic_t uevent_seq;
	struct list_head uevent_list;
	spinlock_t uevent_lock; /* Protect access to uevent_list */

	/*
	 * freeze/thaw support require holding onto a super block
	 */
	struct super_block *frozen_sb;
	struct block_device *suspended_bdev;

	/* forced geometry settings */
	struct hd_geometry geometry;

	/* marker of flush suspend for request-based dm */
	struct request suspend_rq;

	/* For saving the address of __make_request for request based dm */
	make_request_fn *saved_make_request_fn;
};

#define MIN_IOS 256
static struct kmem_cache *_io_cache;
static struct kmem_cache *_tio_cache;
static struct kmem_cache *_rq_tio_cache;
static struct kmem_cache *_bio_info_cache;

static int __init local_init(void)
{
	int r = -ENOMEM;

	/* allocate a slab for the dm_ios */
	_io_cache = KMEM_CACHE(dm_io, 0);
	if (!_io_cache)
		return r;

	/* allocate a slab for the target ios */
	_tio_cache = KMEM_CACHE(dm_target_io, 0);
	if (!_tio_cache)
		goto out_free_io_cache;

	_rq_tio_cache = KMEM_CACHE(dm_rq_target_io, 0);
	if (!_rq_tio_cache)
		goto out_free_tio_cache;

	_bio_info_cache = KMEM_CACHE(dm_clone_bio_info, 0);
	if (!_bio_info_cache)
		goto out_free_rq_tio_cache;

	r = dm_uevent_init();
	if (r)
		goto out_free_bio_info_cache;

	_major = major;
	r = register_blkdev(_major, _name);
	if (r < 0)
		goto out_uevent_exit;

	if (!_major)
		_major = r;

	return 0;

out_uevent_exit:
	dm_uevent_exit();
out_free_bio_info_cache:
	kmem_cache_destroy(_bio_info_cache);
out_free_rq_tio_cache:
	kmem_cache_destroy(_rq_tio_cache);
out_free_tio_cache:
	kmem_cache_destroy(_tio_cache);
out_free_io_cache:
	kmem_cache_destroy(_io_cache);

	return r;
}

static void local_exit(void)
{
	kmem_cache_destroy(_bio_info_cache);
	kmem_cache_destroy(_rq_tio_cache);
	kmem_cache_destroy(_tio_cache);
	kmem_cache_destroy(_io_cache);
	unregister_blkdev(_major, _name);
	dm_uevent_exit();

	_major = 0;

	DMINFO("cleaned up");
}

static int (*_inits[])(void) __initdata = {
	local_init,
	dm_target_init,
	dm_linear_init,
	dm_stripe_init,
	dm_kcopyd_init,
	dm_interface_init,
};

static void (*_exits[])(void) = {
	local_exit,
	dm_target_exit,
	dm_linear_exit,
	dm_stripe_exit,
	dm_kcopyd_exit,
	dm_interface_exit,
};

static int __init dm_init(void)
{
	const int count = ARRAY_SIZE(_inits);

	int r, i;

	for (i = 0; i < count; i++) {
		r = _inits[i]();
		if (r)
			goto bad;
	}

	return 0;

      bad:
	while (i--)
		_exits[i]();

	return r;
}

static void __exit dm_exit(void)
{
	int i = ARRAY_SIZE(_exits);

	while (i--)
		_exits[i]();
}

/*
 * Block device functions
 */
static int dm_blk_open(struct inode *inode, struct file *file)
{
	struct mapped_device *md;
	int retval = 0;

	spin_lock(&_minor_lock);

	md = inode->i_bdev->bd_disk->private_data;
	if (!md) {
		retval = -ENXIO;
		goto out;
	}

	if (test_bit(DMF_FREEING, &md->flags) ||
	    test_bit(DMF_DELETING, &md->flags)) {
		md = NULL;
		retval = -ENXIO;
		goto out;
	}
	if (md->disk->policy && (file->f_mode & FMODE_WRITE)) {
		md = NULL;
		retval = -EROFS;
		goto out;
	}

	dm_get(md);
	atomic_inc(&md->open_count);

out:
	spin_unlock(&_minor_lock);

	return retval;
}

static int dm_blk_close(struct inode *inode, struct file *file)
{
	struct mapped_device *md;

	md = inode->i_bdev->bd_disk->private_data;
	atomic_dec(&md->open_count);
	dm_put(md);
	return 0;
}

int dm_open_count(struct mapped_device *md)
{
	return atomic_read(&md->open_count);
}

/*
 * Guarantees nothing is using the device before it's deleted.
 */
int dm_lock_for_deletion(struct mapped_device *md)
{
	int r = 0;

	spin_lock(&_minor_lock);

	if (dm_open_count(md))
		r = -EBUSY;
	else
		set_bit(DMF_DELETING, &md->flags);

	spin_unlock(&_minor_lock);

	return r;
}

static int dm_blk_getgeo(struct block_device *bdev, struct hd_geometry *geo)
{
	struct mapped_device *md = bdev->bd_disk->private_data;

	return dm_get_geometry(md, geo);
}

static int dm_blk_ioctl(struct inode *inode, struct file *file,
			unsigned int cmd, unsigned long arg)
{
	struct mapped_device *md;
	struct dm_table *map;
	struct dm_target *tgt;
	int r = -ENOTTY;

	/* We don't really need this lock, but we do need 'inode'. */
	unlock_kernel();

	md = inode->i_bdev->bd_disk->private_data;

	map = dm_get_table(md);

	if (!map || !dm_table_get_size(map))
		goto out;

	if (dm_suspended(md)) {
		r = -EAGAIN;
		goto out;
	}

	if (cmd == BLKRRPART) {
		/* Emulate Re-read partitions table */
		kobject_uevent(&md->disk->dev.kobj, KOBJ_CHANGE);
		r = 0;
	} else {
		/* We only support devices that have a single target */
		if (dm_table_get_num_targets(map) != 1)
			goto out;

		tgt = dm_table_get_target(map, 0);

		if (tgt->type->ioctl)
			r = tgt->type->ioctl(tgt, inode, file, cmd, arg);
	}

out:
	dm_table_put(map);

	lock_kernel();
	return r;
}

static struct dm_io *alloc_io(struct mapped_device *md)
{
	return mempool_alloc(md->io_pool, GFP_NOIO);
}

static void free_io(struct mapped_device *md, struct dm_io *io)
{
	mempool_free(io, md->io_pool);
}

static struct dm_target_io *alloc_tio(struct mapped_device *md)
{
	return mempool_alloc(md->tio_pool, GFP_NOIO);
}

static void free_tio(struct mapped_device *md, struct dm_target_io *tio)
{
	mempool_free(tio, md->tio_pool);
}

static inline struct dm_rq_target_io *alloc_rq_tio(struct mapped_device *md)
{
	return mempool_alloc(md->tio_pool, GFP_ATOMIC);
}

static inline void free_rq_tio(struct mapped_device *md,
			       struct dm_rq_target_io *tio)
{
	mempool_free(tio, md->tio_pool);
}

static inline struct dm_clone_bio_info *alloc_bio_info(struct mapped_device *md)
{
	return mempool_alloc(md->io_pool, GFP_ATOMIC);
}

static inline void free_bio_info(struct mapped_device *md,
				 struct dm_clone_bio_info *info)
{
	mempool_free(info, md->io_pool);
}

static void start_io_acct(struct dm_io *io)
{
	struct mapped_device *md = io->md;

	io->start_time = jiffies;

	preempt_disable();
	disk_round_stats(dm_disk(md));
	preempt_enable();
	dm_disk(md)->in_flight = atomic_inc_return(&md->pending);
}

static int end_io_acct(struct dm_io *io)
{
	struct mapped_device *md = io->md;
	struct bio *bio = io->bio;
	unsigned long duration = jiffies - io->start_time;
	int pending;
	int rw = bio_data_dir(bio);

	preempt_disable();
	disk_round_stats(dm_disk(md));
	preempt_enable();
	dm_disk(md)->in_flight = pending = atomic_dec_return(&md->pending);

	disk_stat_add(dm_disk(md), ticks[rw], duration);

	return !pending;
}

/*
 * Add the bio to the list of deferred io.
 */
static int queue_io(struct mapped_device *md, struct bio *bio)
{
	down_write(&md->io_lock);

	if (!test_bit(DMF_BLOCK_IO, &md->flags)) {
		up_write(&md->io_lock);
		return 1;
	}

	bio_list_add(&md->deferred, bio);

	up_write(&md->io_lock);
	return 0;		/* deferred successfully */
}

/*
 * Everyone (including functions in this file), should use this
 * function to access the md->map field, and make sure they call
 * dm_table_put() when finished.
 */
struct dm_table *dm_get_table(struct mapped_device *md)
{
	struct dm_table *t;
	unsigned long flags;

	read_lock_irqsave(&md->map_lock, flags);
	t = md->map;
	if (t)
		dm_table_get(t);
	read_unlock_irqrestore(&md->map_lock, flags);

	return t;
}

/*
 * Get the geometry associated with a dm device
 */
int dm_get_geometry(struct mapped_device *md, struct hd_geometry *geo)
{
	*geo = md->geometry;

	return 0;
}

/*
 * Set the geometry of a device.
 */
int dm_set_geometry(struct mapped_device *md, struct hd_geometry *geo)
{
	sector_t sz = (sector_t)geo->cylinders * geo->heads * geo->sectors;

	if (geo->start > sz) {
		DMWARN("Start sector is beyond the geometry limits.");
		return -EINVAL;
	}

	md->geometry = *geo;

	return 0;
}

/*-----------------------------------------------------------------
 * CRUD START:
 *   A more elegant soln is in the works that uses the queue
 *   merge fn, unfortunately there are a couple of changes to
 *   the block layer that I want to make for this.  So in the
 *   interests of getting something for people to use I give
 *   you this clearly demarcated crap.
 *---------------------------------------------------------------*/

static int __noflush_suspending(struct mapped_device *md)
{
	return test_bit(DMF_NOFLUSH_SUSPENDING, &md->flags);
}

/*
 * Decrements the number of outstanding ios that a bio has been
 * cloned into, completing the original io if necc.
 */
static void dec_pending(struct dm_io *io, int error)
{
	unsigned long flags;

	/* Push-back supersedes any I/O errors */
	if (error && !(io->error > 0 && __noflush_suspending(io->md)))
		io->error = error;

	if (atomic_dec_and_test(&io->io_count)) {
		if (io->error == DM_ENDIO_REQUEUE) {
			/*
			 * Target requested pushing back the I/O.
			 * This must be handled before the sleeper on
			 * suspend queue merges the pushback list.
			 */
			spin_lock_irqsave(&io->md->pushback_lock, flags);
			if (__noflush_suspending(io->md))
				bio_list_add(&io->md->pushback, io->bio);
			else
				/* noflush suspend was interrupted. */
				io->error = -EIO;
			spin_unlock_irqrestore(&io->md->pushback_lock, flags);
		}

		if (end_io_acct(io))
			/* nudge anyone waiting on suspend queue */
			wake_up(&io->md->wait);

		if (io->error != DM_ENDIO_REQUEUE) {
			blk_add_trace_bio(io->md->queue, io->bio,
					  BLK_TA_COMPLETE);

			bio_endio(io->bio, io->error);
		}

		free_io(io->md, io);
	}
}

static void clone_endio(struct bio *bio, int error)
{
	int r = 0;
	struct dm_target_io *tio = bio->bi_private;
	struct mapped_device *md = tio->io->md;
	dm_endio_fn endio = tio->ti->type->end_io;

	if (!bio_flagged(bio, BIO_UPTODATE) && !error)
		error = -EIO;

	if (endio) {
		r = endio(tio->ti, bio, error, &tio->info);
		if (r < 0 || r == DM_ENDIO_REQUEUE)
			/*
			 * error and requeue request are handled
			 * in dec_pending().
			 */
			error = r;
		else if (r == DM_ENDIO_INCOMPLETE)
			/* The target will handle the io */
			return;
		else if (r) {
			DMWARN("unimplemented target endio return value: %d", r);
			BUG();
		}
	}

	dec_pending(tio->io, error);

	/*
	 * Store md for cleanup instead of tio which is about to get freed.
	 */
	bio->bi_private = md->bs;

	bio_put(bio);
	free_tio(md, tio);
}

/*
 * Partial completion handling for request-based dm
 */
static void end_clone_bio(struct bio *clone, int error)
{
	struct dm_clone_bio_info *info = clone->bi_private;
	struct dm_rq_target_io *tio = info->rq->end_io_data;
	struct bio *bio = info->orig;
	unsigned int nr_bytes = info->orig->bi_size;

	free_bio_info(tio->md, info);
	clone->bi_private = tio->md->bs;
	bio_put(clone);

	if (tio->error) {
		/*
		 * An error has already been detected on the request.
		 * Once error occurred, just let clone->end_io() handle
		 * the remainder.
		 */
		return;
	} else if (error) {
		/*
		 * Don't notice the error to the upper layer yet.
		 * The error handling decision is made by the target driver,
		 * when the request is completed.
		 */
		tio->error = error;
		return;
	}

	/*
	 * I/O for the bio successfully completed.
	 * Notice the data completion to the upper layer.
	 */

	/*
	 * bios are processed from the head of the list.
	 * So the completing bio should always be rq->bio.
	 * If it's not, something wrong is happening.
	 */
	if (tio->orig->bio != bio)
		DMERR("bio completion is going in the middle of the request");

	/*
	 * Update the original request.
	 * Do not use blk_end_request() here, because it may complete
	 * the original request before the clone, and break the ordering.
	 */
	blk_update_request(tio->orig, 0, nr_bytes);
}

static void free_bio_clone(struct request *clone, struct mapped_device *md)
{
	struct bio *bio;

	while ((bio = clone->bio) != NULL) {
		clone->bio = bio->bi_next;

		if (bio->bi_private) {
			struct dm_clone_bio_info *info = bio->bi_private;
			free_bio_info(md, info);
		}

		bio->bi_private = md->bs;
		bio_put(bio);
	}
}

static void dec_rq_pending(struct dm_rq_target_io *tio)
{
	if (!atomic_dec_return(&tio->md->pending))
		/* nudge anyone waiting on suspend queue */
		wake_up(&tio->md->wait);
}

static void dm_unprep_request(struct request *rq)
{
	struct request *clone = rq->special;
	struct dm_rq_target_io *tio = clone->end_io_data;

	rq->special = NULL;
	rq->cmd_flags &= ~REQ_DONTPREP;

	free_bio_clone(clone, tio->md);
	dec_rq_pending(tio);
	free_rq_tio(tio->md, tio);
}

/*
 * Requeue the original request of a clone.
 */
void dm_requeue_request(struct request *clone)
{
	struct dm_rq_target_io *tio = clone->end_io_data;
	struct request *rq = tio->orig;
	struct request_queue *q = rq->q;
	unsigned long flags;

	dm_unprep_request(rq);

	spin_lock_irqsave(q->queue_lock, flags);
	if (elv_queue_empty(q))
		blk_plug_device(q);
	blk_requeue_request(q, rq);
	spin_unlock_irqrestore(q->queue_lock, flags);
}
EXPORT_SYMBOL_GPL(dm_requeue_request);

static inline void __stop_queue(struct request_queue *q)
{
	blk_stop_queue(q);
}

static void stop_queue(struct request_queue *q)
{
	unsigned long flags;

	spin_lock_irqsave(q->queue_lock, flags);
	__stop_queue(q);
	spin_unlock_irqrestore(q->queue_lock, flags);
}

static inline void __start_queue(struct request_queue *q)
{
	if (blk_queue_stopped(q))
		blk_start_queue(q);
}

static void start_queue(struct request_queue *q)
{
	unsigned long flags;

	spin_lock_irqsave(q->queue_lock, flags);
	__start_queue(q);
	spin_unlock_irqrestore(q->queue_lock, flags);
}

/*
 * Complete the clone and the original request
 */
static void dm_end_request(struct request *clone, int error)
{
	struct dm_rq_target_io *tio = clone->end_io_data;
	struct request *rq = tio->orig;
	struct request_queue *q = rq->q;
	unsigned int nr_bytes = blk_rq_bytes(rq);

	if (blk_pc_request(rq)) {
		rq->errors = clone->errors;
		rq->data_len = clone->data_len;

		if (rq->sense)
			/*
			 * We are using the sense buffer of the original
			 * request.
			 * So setting the length of the sense data is enough.
			 */
			rq->sense_len = clone->sense_len;
	}

	free_bio_clone(clone, tio->md);
	dec_rq_pending(tio);
	free_rq_tio(tio->md, tio);

	if (unlikely(blk_end_request(rq, error, nr_bytes)))
		BUG();

	blk_run_queue(q);
}

/*
 * Request completion handler for request-based dm
 */
static void dm_softirq_done(struct request *rq)
{
	struct request *clone = rq->completion_data;
	struct dm_rq_target_io *tio = clone->end_io_data;
	dm_request_endio_fn rq_end_io = tio->ti->type->rq_end_io;
	int error = tio->error;
	int r;

	if (rq->cmd_flags & REQ_FAILED)
		goto end_request;

	if (rq_end_io) {
		r = rq_end_io(tio->ti, clone, error, &tio->info);
		if (r <= 0)
			/* The target wants to complete the I/O */
			error = r;
		else if (r == DM_ENDIO_INCOMPLETE)
			/* The target will handle the I/O */
			return;
		else if (r == DM_ENDIO_REQUEUE) {
			/*
			 * The target wants to requeue the I/O.
			 * Don't invoke blk_run_queue() so that the requeued
			 * request won't be dispatched again soon.
			 */
			dm_requeue_request(clone);
			return;
		} else {
			DMWARN("unimplemented target endio return value: %d",
			       r);
			BUG();
		}
	}

end_request:
	dm_end_request(clone, error);
}

/*
 * Called with the queue lock held
 */
static void end_clone_request(struct request *clone, int error)
{
	struct dm_rq_target_io *tio = clone->end_io_data;
	struct request *rq = tio->orig;

	/*
	 * For just cleaning up the information of the queue in which
	 * the clone was dispatched.
	 * The clone is *NOT* freed actually here because it is alloced from
	 * dm own mempool and REQ_ALLOCED isn't set in clone->cmd_flags.
	 */
	__blk_put_request(clone->q, clone);

	/*
	 * Actual request completion is done in a softirq context which doesn't
	 * hold the queue lock.  Otherwise, deadlock could occur because:
	 *     - another request may be submitted by the upper level driver
	 *       of the stacking during the completion
	 *     - the submission which requires queue lock may be done
	 *       against this queue
	 */
	tio->error = error;
	rq->completion_data = clone;
	blk_complete_request(rq);
}

/*
 * Complete the original request of a clone with an error status.
 * Target's rq_end_io() function isn't called.
 * This may be used by target's map_rq() function when the mapping fails.
 */
void dm_kill_request(struct request *clone, int error)
{
	struct dm_rq_target_io *tio = clone->end_io_data;
	struct request *rq = tio->orig;

	tio->error = error;
	/* Avoid printing "I/O error" message, since we didn't I/O actually */
	rq->cmd_flags |= (REQ_FAILED | REQ_QUIET);
	rq->completion_data = clone;
	blk_complete_request(rq);
}
EXPORT_SYMBOL_GPL(dm_kill_request);

static sector_t max_io_len(struct mapped_device *md,
			   sector_t sector, struct dm_target *ti)
{
	sector_t offset = sector - ti->begin;
	sector_t len = ti->len - offset;

	/*
	 * Does the target need to split even further ?
	 */
	if (ti->split_io) {
		sector_t boundary;
		boundary = ((offset + ti->split_io) & ~(ti->split_io - 1))
			   - offset;
		if (len > boundary)
			len = boundary;
	}

	return len;
}

static void __map_bio(struct dm_target *ti, struct bio *clone,
		      struct dm_target_io *tio)
{
	int r;
	sector_t sector;
	struct mapped_device *md;

	/*
	 * Sanity checks.
	 */
	BUG_ON(!clone->bi_size);

	clone->bi_end_io = clone_endio;
	clone->bi_private = tio;

	/*
	 * Map the clone.  If r == 0 we don't need to do
	 * anything, the target has assumed ownership of
	 * this io.
	 */
	atomic_inc(&tio->io->io_count);
	sector = clone->bi_sector;
	r = ti->type->map(ti, clone, &tio->info);
	if (r == DM_MAPIO_REMAPPED) {
		/* the bio has been remapped so dispatch it */

		blk_add_trace_remap(bdev_get_queue(clone->bi_bdev), clone,
				    tio->io->bio->bi_bdev->bd_dev,
				    clone->bi_sector, sector);

		generic_make_request(clone);
	} else if (r < 0 || r == DM_MAPIO_REQUEUE) {
		/* error the io and bail out, or requeue it if needed */
		md = tio->io->md;
		dec_pending(tio->io, r);
		/*
		 * Store bio_set for cleanup.
		 */
		clone->bi_private = md->bs;
		bio_put(clone);
		free_tio(md, tio);
	} else if (r) {
		DMWARN("unimplemented target map return value: %d", r);
		BUG();
	}
}

struct clone_info {
	struct mapped_device *md;
	struct dm_table *map;
	struct bio *bio;
	struct dm_io *io;
	sector_t sector;
	sector_t sector_count;
	unsigned short idx;
};

static void dm_bio_destructor(struct bio *bio)
{
	struct bio_set *bs = bio->bi_private;

	bio_free(bio, bs);
}

/*
 * Creates a little bio that is just does part of a bvec.
 */
static struct bio *split_bvec(struct bio *bio, sector_t sector,
			      unsigned short idx, unsigned int offset,
			      unsigned int len, struct bio_set *bs)
{
	struct bio *clone;
	struct bio_vec *bv = bio->bi_io_vec + idx;

	clone = bio_alloc_bioset(GFP_NOIO, 1, bs);
	clone->bi_destructor = dm_bio_destructor;
	*clone->bi_io_vec = *bv;

	clone->bi_sector = sector;
	clone->bi_bdev = bio->bi_bdev;
	clone->bi_rw = bio->bi_rw;
	clone->bi_vcnt = 1;
	clone->bi_size = to_bytes(len);
	clone->bi_io_vec->bv_offset = offset;
	clone->bi_io_vec->bv_len = clone->bi_size;
	clone->bi_flags |= 1 << BIO_CLONED;

	if (bio_integrity(bio)) {
		bio_integrity_clone(clone, bio, GFP_NOIO, bs);
		bio_integrity_trim(clone,
				   bio_sector_offset(bio, idx, offset), len);
	}

	return clone;
}

/*
 * Creates a bio that consists of range of complete bvecs.
 */
static struct bio *clone_bio(struct bio *bio, sector_t sector,
			     unsigned short idx, unsigned short bv_count,
			     unsigned int len, struct bio_set *bs)
{
	struct bio *clone;

	clone = bio_alloc_bioset(GFP_NOIO, bio->bi_max_vecs, bs);
	__bio_clone(clone, bio);
	clone->bi_destructor = dm_bio_destructor;
	clone->bi_sector = sector;
	clone->bi_idx = idx;
	clone->bi_vcnt = idx + bv_count;
	clone->bi_size = to_bytes(len);
	clone->bi_flags &= ~(1 << BIO_SEG_VALID);

	if (bio_integrity(bio)) {
		bio_integrity_clone(clone, bio, GFP_NOIO, bs);

		if (idx != bio->bi_idx || clone->bi_size < bio->bi_size)
			bio_integrity_trim(clone,
					   bio_sector_offset(bio, idx, 0), len);
	}

	return clone;
}

static int __clone_and_map(struct clone_info *ci)
{
	struct bio *clone, *bio = ci->bio;
	struct dm_target *ti;
	sector_t len = 0, max;
	struct dm_target_io *tio;

	ti = dm_table_find_target(ci->map, ci->sector);
	if (!dm_target_is_valid(ti))
		return -EIO;

	max = max_io_len(ci->md, ci->sector, ti);

	/*
	 * Allocate a target io object.
	 */
	tio = alloc_tio(ci->md);
	tio->io = ci->io;
	tio->ti = ti;
	memset(&tio->info, 0, sizeof(tio->info));

	if (ci->sector_count <= max) {
		/*
		 * Optimise for the simple case where we can do all of
		 * the remaining io with a single clone.
		 */
		clone = clone_bio(bio, ci->sector, ci->idx,
				  bio->bi_vcnt - ci->idx, ci->sector_count,
				  ci->md->bs);
		__map_bio(ti, clone, tio);
		ci->sector_count = 0;

	} else if (to_sector(bio->bi_io_vec[ci->idx].bv_len) <= max) {
		/*
		 * There are some bvecs that don't span targets.
		 * Do as many of these as possible.
		 */
		int i;
		sector_t remaining = max;
		sector_t bv_len;

		for (i = ci->idx; remaining && (i < bio->bi_vcnt); i++) {
			bv_len = to_sector(bio->bi_io_vec[i].bv_len);

			if (bv_len > remaining)
				break;

			remaining -= bv_len;
			len += bv_len;
		}

		clone = clone_bio(bio, ci->sector, ci->idx, i - ci->idx, len,
				  ci->md->bs);
		__map_bio(ti, clone, tio);

		ci->sector += len;
		ci->sector_count -= len;
		ci->idx = i;

	} else {
		/*
		 * Handle a bvec that must be split between two or more targets.
		 */
		struct bio_vec *bv = bio->bi_io_vec + ci->idx;
		sector_t remaining = to_sector(bv->bv_len);
		unsigned int offset = 0;

		do {
			if (offset) {
				ti = dm_table_find_target(ci->map, ci->sector);
				if (!dm_target_is_valid(ti))
					return -EIO;

				max = max_io_len(ci->md, ci->sector, ti);

				tio = alloc_tio(ci->md);
				tio->io = ci->io;
				tio->ti = ti;
				memset(&tio->info, 0, sizeof(tio->info));
			}

			len = min(remaining, max);

			clone = split_bvec(bio, ci->sector, ci->idx,
					   bv->bv_offset + offset, len,
					   ci->md->bs);

			__map_bio(ti, clone, tio);

			ci->sector += len;
			ci->sector_count -= len;
			offset += to_bytes(len);
		} while (remaining -= len);

		ci->idx++;
	}

	return 0;
}

/*
 * Split the bio into several clones.
 */
static int __split_bio(struct mapped_device *md, struct bio *bio)
{
	struct clone_info ci;
	int error = 0;

	ci.map = dm_get_table(md);
	if (unlikely(!ci.map))
		return -EIO;
	if (unlikely(bio_barrier(bio) && !dm_table_barrier_ok(ci.map))) {
		bio_endio(bio, -EOPNOTSUPP);
		dm_table_put(ci.map);
		return 0;
	}
	ci.md = md;
	ci.bio = bio;
	ci.io = alloc_io(md);
	ci.io->error = 0;
	atomic_set(&ci.io->io_count, 1);
	ci.io->bio = bio;
	ci.io->md = md;
	ci.sector = bio->bi_sector;
	ci.sector_count = bio_sectors(bio);
	ci.idx = bio->bi_idx;

	start_io_acct(ci.io);
	while (ci.sector_count && !error)
		error = __clone_and_map(&ci);

	/* drop the extra reference count */
	dec_pending(ci.io, error);
	dm_table_put(ci.map);

	return 0;
}
/*-----------------------------------------------------------------
 * CRUD END
 *---------------------------------------------------------------*/

static int dm_merge_bvec(struct request_queue *q,
			 struct bvec_merge_data *bvm,
			 struct bio_vec *biovec)
{
	struct mapped_device *md = q->queuedata;
	struct dm_table *map = dm_get_table(md);
	struct dm_target *ti;
	sector_t max_sectors;
	int max_size = 0;

	if (unlikely(!map))
		goto out;

	ti = dm_table_find_target(map, bvm->bi_sector);
	if (!dm_target_is_valid(ti))
		goto out_table;

	/*
	 * Find maximum amount of I/O that won't need splitting
	 */
	max_sectors = min(max_io_len(md, bvm->bi_sector, ti),
			  (sector_t) BIO_MAX_SECTORS);
	max_size = (max_sectors << SECTOR_SHIFT) - bvm->bi_size;
	if (max_size < 0)
		max_size = 0;

	/*
	 * merge_bvec_fn() returns number of bytes
	 * it can accept at this offset
	 * max is precomputed maximal io size
	 */
	if (max_size && ti->type->merge)
		max_size = ti->type->merge(ti, bvm, biovec, max_size);

out_table:
	dm_table_put(map);

out:
	/*
	 * Always allow an entire first page
	 */
	if (max_size <= biovec->bv_len && !(bvm->bi_size >> SECTOR_SHIFT))
		max_size = biovec->bv_len;

	return max_size;
}

/*
 * The request function that just remaps the bio built up by
 * dm_merge_bvec.
 */
static int _dm_request(struct request_queue *q, struct bio *bio)
{
	int r = -EIO;
	int rw = bio_data_dir(bio);
	struct mapped_device *md = q->queuedata;

	down_read(&md->io_lock);

	disk_stat_inc(dm_disk(md), ios[rw]);
	disk_stat_add(dm_disk(md), sectors[rw], bio_sectors(bio));

	/*
	 * If we're suspended we have to queue
	 * this io for later.
	 */
	while (test_bit(DMF_BLOCK_IO, &md->flags)) {
		up_read(&md->io_lock);

		if (bio_rw(bio) != READA)
			r = queue_io(md, bio);

		if (r <= 0)
			goto out_req;

		/*
		 * We're in a while loop, because someone could suspend
		 * before we get to the following read lock.
		 */
		down_read(&md->io_lock);
	}

	r = __split_bio(md, bio);
	up_read(&md->io_lock);

out_req:
	if (r < 0)
		bio_io_error(bio);

	return 0;
}

static int dm_make_request(struct request_queue *q, struct bio *bio)
{
	struct mapped_device *md = (struct mapped_device *)q->queuedata;

	if (unlikely(bio_barrier(bio))) {
		bio_endio(bio, -EOPNOTSUPP);
		return 0;
	}

	/*
	 * Submitting to a stopped queue with no map is okay;
	 * might happen during reconfiguration.
	 */
	if (unlikely(!md->map) && !blk_queue_stopped(q)) {
		bio_endio(bio, -EIO);
		return 0;
	}

	return md->saved_make_request_fn(q, bio); /* call __make_request() */
}

static inline int dm_request_based(struct mapped_device *md)
{
	return blk_queue_stackable(md->queue);
}

static int dm_request(struct request_queue *q, struct bio *bio)
{
	struct mapped_device *md = q->queuedata;

	if (dm_request_based(md))
		return dm_make_request(q, bio);

	return _dm_request(q, bio);
}

void dm_dispatch_request(struct request *rq)
{
	int r;

	rq->start_time = jiffies;
	r = blk_insert_cloned_request(rq->q, rq);
	if (r)
		dm_kill_request(rq, r);
}
EXPORT_SYMBOL_GPL(dm_dispatch_request);

static void copy_request_info(struct request *clone, struct request *rq)
{
	clone->cmd_flags = (rq_data_dir(rq) | REQ_NOMERGE);
	clone->cmd_type = rq->cmd_type;
	clone->sector = rq->sector;
	clone->hard_sector = rq->hard_sector;
	clone->nr_sectors = rq->nr_sectors;
	clone->hard_nr_sectors = rq->hard_nr_sectors;
	clone->current_nr_sectors = rq->current_nr_sectors;
	clone->hard_cur_sectors = rq->hard_cur_sectors;
	clone->nr_phys_segments = rq->nr_phys_segments;
	clone->ioprio = rq->ioprio;
	clone->buffer = rq->buffer;
	clone->cmd_len = rq->cmd_len;
	if (rq->cmd_len)
		clone->cmd = rq->cmd;
	clone->data_len = rq->data_len;
	clone->extra_len = rq->extra_len;
	clone->sense_len = rq->sense_len;
	clone->data = rq->data;
	clone->sense = rq->sense;
}

static int clone_request_bios(struct request *clone, struct request *rq,
			      struct mapped_device *md)
{
	struct bio *bio, *clone_bio;
	struct dm_clone_bio_info *info;

	for (bio = rq->bio; bio; bio = bio->bi_next) {
		info = alloc_bio_info(md);
		if (!info)
			goto free_and_out;

		clone_bio = bio_alloc_bioset(GFP_ATOMIC, bio->bi_max_vecs,
					     md->bs);
		if (!clone_bio) {
			free_bio_info(md, info);
			goto free_and_out;
		}

		__bio_clone(clone_bio, bio);
		if (bio_integrity(bio))
			if (bio_integrity_clone(clone_bio, bio, GFP_ATOMIC,
						md->bs) < 0)
				goto free_and_out;

		clone_bio->bi_destructor = dm_bio_destructor;
		clone_bio->bi_end_io = end_clone_bio;
		info->rq = clone;
		info->orig = bio;
		clone_bio->bi_private = info;

		if (clone->bio) {
			clone->biotail->bi_next = clone_bio;
			clone->biotail = clone_bio;
		} else
			clone->bio = clone->biotail = clone_bio;
	}

	return 0;

free_and_out:
	free_bio_clone(clone, md);

	return -ENOMEM;
}

static int setup_clone(struct request *clone, struct request *rq,
		       struct dm_rq_target_io *tio)
{
	int r;

	blk_rq_init(NULL, clone);

	r = clone_request_bios(clone, rq, tio->md);
	if (r)
		return r;

	copy_request_info(clone, rq);
	clone->start_time = jiffies;
	clone->end_io = end_clone_request;
	clone->end_io_data = tio;

	return 0;
}

static inline int dm_flush_suspending(struct mapped_device *md)
{
	return !md->suspend_rq.data;
}

/*
 * Called with the queue lock held.
 */
static int dm_prep_fn(struct request_queue *q, struct request *rq)
{
	struct mapped_device *md = (struct mapped_device *)q->queuedata;
	struct dm_rq_target_io *tio;
	struct request *clone;

	if (unlikely(rq == &md->suspend_rq)) { /* Flush suspend marker */
		if (dm_flush_suspending(md)) {
			if (q->in_flight)
				return BLKPREP_DEFER;
			else {
				/* This device should be quiet now */
				__stop_queue(q);
				smp_mb();
				BUG_ON(atomic_read(&md->pending));
				wake_up(&md->wait);
				return BLKPREP_KILL;
			}
		} else
			/*
			 * The suspend process was interrupted.
			 * So no need to suspend now.
			 */
			return BLKPREP_KILL;
	}

	if (unlikely(rq->special)) {
		DMWARN("Already has something in rq->special.");
		return BLKPREP_KILL;
	}

	if (unlikely(!dm_request_based(md))) {
		DMWARN("Request was queued into bio-based device");
		return BLKPREP_KILL;
	}

	tio = alloc_rq_tio(md); /* Only one for each original request */
	if (!tio)
		/* -ENOMEM */
		return BLKPREP_DEFER;

	tio->md = md;
	tio->ti = NULL;
	tio->orig = rq;
	tio->error = 0;
	memset(&tio->info, 0, sizeof(tio->info));
	memset(&tio->clone, 0, sizeof(tio->clone));

	clone = &tio->clone;
	if (setup_clone(clone, rq, tio)) {
		/* -ENOMEM */
		free_rq_tio(md, tio);
		return BLKPREP_DEFER;
	}

	rq->special = clone;
	rq->cmd_flags |= REQ_DONTPREP;

	return BLKPREP_OK;
}

static void map_request(struct dm_target *ti, struct request *rq,
			struct mapped_device *md)
{
	int r;
	struct request *clone = rq->special;
	struct dm_rq_target_io *tio = clone->end_io_data;

	tio->ti = ti;
	atomic_inc(&md->pending);

#if 0
	/* This might trigger accidentally */

	/*
	 * Although submitted requests to the md->queue are checked against
	 * the table/queue limitations at the submission time, the limitations
	 * may be changed by a table swapping while those already checked
	 * requests are in the md->queue.
	 * If the limitations have been shrunk in such situations, we may be
	 * dispatching requests violating the current limitations here.
	 * Since struct request is a reliable one in the block-layer
	 * and device drivers, dispatching such requests is dangerous.
	 * (e.g. it may cause kernel panic easily.)
	 * Avoid to dispatch such problematic requests in request-based dm.
	 *
	 * Since dm_kill_request() decrements the md->pending, this have to
	 * be done after incrementing the md->pending.
	 */
	r = blk_rq_check_limits(rq->q, rq);
	if (unlikely(r)) {
		DMWARN("violating the queue limitation. the limitation may be"
		       " shrunk while there are some requests in the queue.");
		dm_kill_request(clone, r);
		return;
	}
#endif

	r = ti->type->map_rq(ti, clone, &tio->info);
	switch (r) {
	case DM_MAPIO_SUBMITTED:
		/* The target has taken the I/O to submit by itself later */
		break;
	case DM_MAPIO_REMAPPED:
		/* The target has remapped the I/O so dispatch it */
		dm_dispatch_request(clone);
		break;
	case DM_MAPIO_REQUEUE:
		/* The target wants to requeue the I/O */
		dm_requeue_request(clone);
		break;
	default:
		if (r > 0) {
			DMWARN("unimplemented target map return value: %d", r);
			BUG();
		}

		/* The target wants to complete the I/O */
		dm_kill_request(clone, r);
		break;
	}
}

/*
 * q->request_fn for request-based dm.
 * Called with the queue lock held.
 */
static void dm_request_fn(struct request_queue *q)
{
	struct mapped_device *md = (struct mapped_device *)q->queuedata;
	struct dm_table *map = dm_get_table(md);
	struct dm_target *ti;
	struct request *rq;

	/*
	 * The check for blk_queue_stopped() needs here, because:
	 *     - device suspend uses blk_stop_queue() and expects that
	 *       no I/O will be dispatched any more after the queue stop
	 *     - generic_unplug_device() doesn't call q->request_fn()
	 *       when the queue is stopped, so no problem
	 *     - but underlying device drivers may call q->request_fn()
	 *       without the check through blk_run_queue()
	 */
	while (!blk_queue_plugged(q) && !blk_queue_stopped(q)) {
		rq = elv_next_request(q);
		if (!rq)
			goto plug_and_out;

		ti = dm_table_find_target(map, rq->sector);
		if (ti->type->busy && ti->type->busy(ti))
			goto plug_and_out;

		blkdev_dequeue_request(rq);
		spin_unlock(q->queue_lock);
		map_request(ti, rq, md);
		spin_lock_irq(q->queue_lock);
	}

	goto out;

plug_and_out:
	if (!elv_queue_empty(q))
		/* Some requests still remain, retry later */
		blk_plug_device(q);

out:
	dm_table_put(map);

	return;
}

int dm_underlying_device_busy(struct request_queue *q)
{
	return blk_lld_busy(q);
}
EXPORT_SYMBOL_GPL(dm_underlying_device_busy);

static int dm_lld_busy(struct request_queue *q)
{
	int r;
	struct mapped_device *md = q->queuedata;
	struct dm_table *map = dm_get_table(md);

	if (!map || test_bit(DMF_BLOCK_IO, &md->flags))
		r = 1;
	else
		r = dm_table_any_busy_target(map);

	dm_table_put(map);
	return r;
}

static void dm_unplug_all(struct request_queue *q)
{
	struct mapped_device *md = q->queuedata;
	struct dm_table *map = dm_get_table(md);

	if (map) {
		if (dm_request_based(md))
			generic_unplug_device(q);

		dm_table_unplug_all(map);
		dm_table_put(map);
	}
}

static int dm_any_congested(void *congested_data, int bdi_bits)
{
	int r = bdi_bits;
	struct mapped_device *md = (struct mapped_device *) congested_data;
	struct dm_table *map;

	if (!test_bit(DMF_BLOCK_IO, &md->flags)) {
		map = dm_get_table(md);
		if (map) {
			if (dm_request_based(md))
				/*
				 * Request-based dm cares about only own queue for
				 * the query about congestion status of request_queue
				 */
				r = md->queue->backing_dev_info.state & bdi_bits;
			else
				r = dm_table_any_congested(map, bdi_bits);
			dm_table_put(map);
		}
	}


	return r;
}

/*-----------------------------------------------------------------
 * An IDR is used to keep track of allocated minor numbers.
 *---------------------------------------------------------------*/
static DEFINE_IDR(_minor_idr);

static void free_minor(int minor)
{
	spin_lock(&_minor_lock);
	idr_remove(&_minor_idr, minor);
	spin_unlock(&_minor_lock);
}

/*
 * See if the device with a specific minor # is free.
 */
static int specific_minor(int minor)
{
	int r, m;

	if (minor >= (1 << MINORBITS))
		return -EINVAL;

	r = idr_pre_get(&_minor_idr, GFP_KERNEL);
	if (!r)
		return -ENOMEM;

	spin_lock(&_minor_lock);

	if (idr_find(&_minor_idr, minor)) {
		r = -EBUSY;
		goto out;
	}

	r = idr_get_new_above(&_minor_idr, MINOR_ALLOCED, minor, &m);
	if (r)
		goto out;

	if (m != minor) {
		idr_remove(&_minor_idr, m);
		r = -EBUSY;
		goto out;
	}

out:
	spin_unlock(&_minor_lock);
	return r;
}

static int next_free_minor(int *minor)
{
	int r, m;

	r = idr_pre_get(&_minor_idr, GFP_KERNEL);
	if (!r)
		return -ENOMEM;

	spin_lock(&_minor_lock);

	r = idr_get_new(&_minor_idr, MINOR_ALLOCED, &m);
	if (r)
		goto out;

	if (m >= (1 << MINORBITS)) {
		idr_remove(&_minor_idr, m);
		r = -ENOSPC;
		goto out;
	}

	*minor = m;

out:
	spin_unlock(&_minor_lock);
	return r;
}

static struct block_device_operations dm_blk_dops;

/*
 * Allocate and initialise a blank device with a given minor.
 */
static struct mapped_device *alloc_dev(int minor)
{
	int r;
	struct mapped_device *md = kzalloc(sizeof(*md), GFP_KERNEL);
	void *old_md;

	if (!md) {
		DMWARN("unable to allocate device, out of memory.");
		return NULL;
	}

	if (!try_module_get(THIS_MODULE))
		goto bad_module_get;

	/* get a minor number for the dev */
	if (minor == DM_ANY_MINOR)
		r = next_free_minor(&minor);
	else
		r = specific_minor(minor);
	if (r < 0)
		goto bad_minor;

	init_rwsem(&md->io_lock);
	mutex_init(&md->suspend_lock);
	spin_lock_init(&md->pushback_lock);
	rwlock_init(&md->map_lock);
	atomic_set(&md->holders, 1);
	atomic_set(&md->open_count, 0);
	atomic_set(&md->event_nr, 0);
	atomic_set(&md->uevent_seq, 0);
	INIT_LIST_HEAD(&md->uevent_list);
	spin_lock_init(&md->uevent_lock);

	md->queue = blk_init_queue(dm_request_fn, NULL);
	if (!md->queue)
		goto bad_queue;

	/*
	 * Request-based dm devices cannot be stacked on top of bio-based dm
	 * devices.  The type of this dm device has not been decided yet,
	 * although we initialized the queue using blk_init_queue().
	 * The type is decided at the first table loading time.
	 * To prevent problematic device stacking, clear the queue flag
	 * for request stacking support until then.
	 *
	 * This queue is new, so no concurrency on the queue_flags.
	 */
	queue_flag_clear_unlocked(QUEUE_FLAG_STACKABLE, md->queue);
	md->saved_make_request_fn = md->queue->make_request_fn;
	md->queue->queuedata = md;
	md->queue->backing_dev_info.congested_fn = dm_any_congested;
	md->queue->backing_dev_info.congested_data = md;
	blk_queue_make_request(md->queue, dm_request);
	blk_queue_ordered(md->queue, QUEUE_ORDERED_DRAIN, NULL);
	blk_queue_bounce_limit(md->queue, BLK_BOUNCE_ANY);
	md->queue->unplug_fn = dm_unplug_all;
	blk_queue_merge_bvec(md->queue, dm_merge_bvec);
	blk_queue_softirq_done(md->queue, dm_softirq_done);
	blk_queue_prep_rq(md->queue, dm_prep_fn);
	blk_queue_lld_busy(md->queue, dm_lld_busy);

	md->disk = alloc_disk(1);
	if (!md->disk)
		goto bad_disk;

	atomic_set(&md->pending, 0);
	init_waitqueue_head(&md->wait);
	init_waitqueue_head(&md->eventq);

	md->disk->major = _major;
	md->disk->first_minor = minor;
	md->disk->fops = &dm_blk_dops;
	md->disk->queue = md->queue;
	md->disk->private_data = md;
	sprintf(md->disk->disk_name, "dm-%d", minor);
	add_disk(md->disk);
	format_dev_t(md->name, MKDEV(_major, minor));

	md->wq = create_singlethread_workqueue("kdmflush");
	if (!md->wq)
		goto bad_thread;

	/* Populate the mapping, nobody knows we exist yet */
	spin_lock(&_minor_lock);
	old_md = idr_replace(&_minor_idr, md, minor);
	spin_unlock(&_minor_lock);

	BUG_ON(old_md != MINOR_ALLOCED);

	return md;

bad_thread:
	put_disk(md->disk);
bad_disk:
	blk_cleanup_queue(md->queue);
bad_queue:
	free_minor(minor);
bad_minor:
	module_put(THIS_MODULE);
bad_module_get:
	kfree(md);
	return NULL;
}

static void unlock_fs(struct mapped_device *md);

static void free_dev(struct mapped_device *md)
{
	int minor = md->disk->first_minor;

	if (md->suspended_bdev) {
		unlock_fs(md);
		bdput(md->suspended_bdev);
	}
	destroy_workqueue(md->wq);
	if (md->tio_pool)
		mempool_destroy(md->tio_pool);
	if (md->io_pool)
		mempool_destroy(md->io_pool);
	if (md->bs)
		bioset_free(md->bs);
	blk_integrity_unregister(md->disk);
	del_gendisk(md->disk);
	free_minor(minor);

	spin_lock(&_minor_lock);
	md->disk->private_data = NULL;
	spin_unlock(&_minor_lock);

	put_disk(md->disk);
	blk_cleanup_queue(md->queue);
	module_put(THIS_MODULE);
	kfree(md);
}

/*
 * Bind a table to the device.
 */
static void event_callback(void *context)
{
	unsigned long flags;
	LIST_HEAD(uevents);
	struct mapped_device *md = (struct mapped_device *) context;

	spin_lock_irqsave(&md->uevent_lock, flags);
	list_splice_init(&md->uevent_list, &uevents);
	spin_unlock_irqrestore(&md->uevent_lock, flags);

	dm_send_uevents(&uevents, &md->disk->dev.kobj);

	atomic_inc(&md->event_nr);
	wake_up(&md->eventq);
}

static void __set_size(struct mapped_device *md, sector_t size)
{
	set_capacity(md->disk, size);

	mutex_lock(&md->suspended_bdev->bd_inode->i_mutex);
	i_size_write(md->suspended_bdev->bd_inode, (loff_t)size << SECTOR_SHIFT);
	mutex_unlock(&md->suspended_bdev->bd_inode->i_mutex);
}

static int __bind(struct mapped_device *md, struct dm_table *t)
{
	struct request_queue *q = md->queue;
	sector_t size;
	unsigned long flags;

	size = dm_table_get_size(t);

	/*
	 * Wipe any geometry if the size of the table changed.
	 */
	if (size != get_capacity(md->disk))
		memset(&md->geometry, 0, sizeof(md->geometry));

	if (md->suspended_bdev)
		__set_size(md, size);

	if (!size) {
		dm_table_destroy(t);
		return 0;
	}

	dm_table_event_callback(t, event_callback, md);

	/*
	 * The queue hasn't been stopped yet, if the old table type wasn't
	 * for request-based during suspension.  So stop it to prevent
	 * I/O mapping before resume.
	 * This must be done before setting the queue restrictions,
	 * because request-based dm may be run just after the setting.
	 */
	if (dm_table_request_based(t) && !blk_queue_stopped(q))
		stop_queue(q);

	write_lock_irqsave(&md->map_lock, flags);
	md->map = t;
	dm_table_set_restrictions(t, q);
	dm_table_set_integrity(t, md);
	write_unlock_irqrestore(&md->map_lock, flags);

	dm_get_table(md);
	if (dm_table_get_mode(md->map) & FMODE_WRITE) {
		set_disk_ro(md->disk, 0);
	} else {
		set_disk_ro(md->disk, 1);
	}
	dm_table_put(md->map);

	return 0;
}

static void __unbind(struct mapped_device *md)
{
	struct dm_table *map = md->map;
	unsigned long flags;

	if (!map)
		return;

	dm_table_event_callback(map, NULL, NULL);
	write_lock_irqsave(&md->map_lock, flags);
	md->map = NULL;
	write_unlock_irqrestore(&md->map_lock, flags);
	dm_table_destroy(map);
}

/*
 * Constructor for a new device.
 */
int dm_create(int minor, struct mapped_device **result)
{
	struct mapped_device *md;

	md = alloc_dev(minor);
	if (!md)
		return -ENXIO;

	*result = md;
	return 0;
}

static struct mapped_device *dm_find_md(dev_t dev)
{
	struct mapped_device *md;
	unsigned minor = MINOR(dev);

	if (MAJOR(dev) != _major || minor >= (1 << MINORBITS))
		return NULL;

	spin_lock(&_minor_lock);

	md = idr_find(&_minor_idr, minor);
	if (md && (md == MINOR_ALLOCED ||
		   (dm_disk(md)->first_minor != minor) ||
		   test_bit(DMF_FREEING, &md->flags))) {
		md = NULL;
		goto out;
	}

out:
	spin_unlock(&_minor_lock);

	return md;
}

struct mapped_device *dm_get_md(dev_t dev)
{
	struct mapped_device *md = dm_find_md(dev);

	if (md)
		dm_get(md);

	return md;
}

void *dm_get_mdptr(struct mapped_device *md)
{
	return md->interface_ptr;
}

void dm_set_mdptr(struct mapped_device *md, void *ptr)
{
	md->interface_ptr = ptr;
}

void dm_get(struct mapped_device *md)
{
	atomic_inc(&md->holders);
}

const char *dm_device_name(struct mapped_device *md)
{
	return md->name;
}
EXPORT_SYMBOL_GPL(dm_device_name);

void dm_put(struct mapped_device *md)
{
	struct dm_table *map;

	BUG_ON(test_bit(DMF_FREEING, &md->flags));

	if (atomic_dec_and_lock(&md->holders, &_minor_lock)) {
		map = dm_get_table(md);
		idr_replace(&_minor_idr, MINOR_ALLOCED, dm_disk(md)->first_minor);
		set_bit(DMF_FREEING, &md->flags);
		spin_unlock(&_minor_lock);
		if (!dm_suspended(md)) {
			dm_table_presuspend_targets(map);
			dm_table_postsuspend_targets(map);
		}
		dm_table_put(map);
		__unbind(md);
		free_dev(md);
	}
}
EXPORT_SYMBOL_GPL(dm_put);

static int dm_wait_for_completion(struct mapped_device *md)
{
	int r = 0;

	while (1) {
		set_current_state(TASK_INTERRUPTIBLE);

		smp_mb();
		if (dm_request_based(md)) {
			if (!atomic_read(&md->pending) &&
			    blk_queue_stopped(md->queue))
				break;
		} else if (!atomic_read(&md->pending))
			break;

		if (signal_pending(current)) {
			r = -EINTR;
			break;
		}

		io_schedule();
	}
	set_current_state(TASK_RUNNING);

	return r;
}

/*
 * Process the deferred bios
 */
static void __flush_deferred_io(struct mapped_device *md)
{
	struct bio *c;

	while ((c = bio_list_pop(&md->deferred))) {
		/*
		 * Some bios might have been queued here during suspension
		 * before setting of request-based dm in resume
		 */
		if (dm_request_based(md))
			generic_make_request(c);
		else if (__split_bio(md, c))
			bio_io_error(c);
	}

	clear_bit(DMF_BLOCK_IO, &md->flags);
}

static void __merge_pushback_list(struct mapped_device *md)
{
	unsigned long flags;

	spin_lock_irqsave(&md->pushback_lock, flags);
	clear_bit(DMF_NOFLUSH_SUSPENDING, &md->flags);
	bio_list_merge_head(&md->deferred, &md->pushback);
	bio_list_init(&md->pushback);
	spin_unlock_irqrestore(&md->pushback_lock, flags);
}

static void dm_wq_work(struct work_struct *work)
{
	struct dm_wq_req *req = container_of(work, struct dm_wq_req, work);
	struct mapped_device *md = req->md;

	down_write(&md->io_lock);
	switch (req->type) {
	case DM_WQ_FLUSH_DEFERRED:
		__flush_deferred_io(md);
		break;
	default:
		DMERR("dm_wq_work: unrecognised work type %d", req->type);
		BUG();
	}
	up_write(&md->io_lock);
}

static void dm_wq_queue(struct mapped_device *md, int type, void *context,
			struct dm_wq_req *req)
{
	req->type = type;
	req->md = md;
	req->context = context;
	INIT_WORK(&req->work, dm_wq_work);
	queue_work(md->wq, &req->work);
}

static void dm_queue_flush(struct mapped_device *md, int type, void *context)
{
	struct dm_wq_req req;

	dm_wq_queue(md, type, context, &req);
	flush_workqueue(md->wq);
}

/*
 * Swap in a new table (destroying old one).
 */
int dm_swap_table(struct mapped_device *md, struct dm_table *table)
{
	int r = -EINVAL;

	mutex_lock(&md->suspend_lock);

	/* device must be suspended */
	if (!dm_suspended(md))
		goto out;

	/* without bdev, the device size cannot be changed */
	if (!md->suspended_bdev)
		if (get_capacity(md->disk) != dm_table_get_size(table))
			goto out;

	__unbind(md);
	r = __bind(md, table);

out:
	mutex_unlock(&md->suspend_lock);
	return r;
}

static inline void dm_invalidate_flush_suspend(struct mapped_device *md)
{
	md->suspend_rq.data = (void *)0x1;
}

static void dm_abort_suspend(struct mapped_device *md, int noflush)
{
	struct request_queue *q = md->queue;
	unsigned long flags;

	/*
	 * For flush suspend, invalidation and queue restart must be protected
	 * by a single queue lock to prevent a race with dm_prep_fn().
	 */
	spin_lock_irqsave(q->queue_lock, flags);
	if (!noflush)
		dm_invalidate_flush_suspend(md);
	__start_queue(q);
	spin_unlock_irqrestore(q->queue_lock, flags);
}

/*
 * Additional suspend work for request-based dm.
 *
 * In request-based dm, stopping request_queue prevents mapping.
 * Even after stopping the request_queue, submitted requests from upper-layer
 * can be inserted to the request_queue.  So original (unmapped) requests are
 * kept in the request_queue during suspension.
 */
static void dm_start_suspend(struct mapped_device *md, int noflush)
{
	struct request *rq = &md->suspend_rq;
	struct request_queue *q = md->queue;
	unsigned long flags;

	if (noflush) {
		stop_queue(q);
		return;
	}

	/*
	 * For flush suspend, we need a marker to indicate the border line
	 * between flush needed I/Os and deferred I/Os, since all I/Os are
	 * queued in the request_queue during suspension.
	 *
	 * This marker must be inserted after setting DMF_BLOCK_IO,
	 * because dm_prep_fn() considers no DMF_BLOCK_IO to be
	 * a suspend interruption.
	 */
	spin_lock_irqsave(q->queue_lock, flags);
	if (unlikely(rq->ref_count)) {
		/*
		 * This can happen when the previous suspend was interrupted,
		 * the inserted suspend_rq for the previous suspend has still
		 * been in the queue and this suspend has been invoked.
		 *
		 * We could re-insert the suspend_rq by deleting it from
		 * the queue forcibly using list_del_init(&rq->queuelist).
		 * But it would break the block-layer easily.
		 * So we don't re-insert the suspend_rq again in such a case.
		 * The suspend_rq should be already invalidated during
		 * the previous suspend interruption, so just wait for it
		 * to be completed.
		 *
		 * This suspend will never complete, so warn the user to
		 * interrupt this suspend and retry later.
		 */
		BUG_ON(!rq->data);
		spin_unlock_irqrestore(q->queue_lock, flags);

		DMWARN("Invalidating the previous suspend is still in"
		       " progress.  This suspend will be never done."
		       " Please interrupt this suspend and retry later.");
		return;
	}
	spin_unlock_irqrestore(q->queue_lock, flags);

	/* Now no user of the suspend_rq */
	blk_rq_init(q, rq);
	blk_insert_request(q, rq, 0, NULL);
}

/*
 * Functions to lock and unlock any filesystem running on the
 * device.
 */
static int lock_fs(struct mapped_device *md)
{
	int r;

	WARN_ON(md->frozen_sb);

	md->frozen_sb = freeze_bdev(md->suspended_bdev);
	if (IS_ERR(md->frozen_sb)) {
		r = PTR_ERR(md->frozen_sb);
		md->frozen_sb = NULL;
		return r;
	}

	set_bit(DMF_FROZEN, &md->flags);

	/* don't bdput right now, we don't want the bdev
	 * to go away while it is locked.
	 */
	return 0;
}

static void unlock_fs(struct mapped_device *md)
{
	if (!test_bit(DMF_FROZEN, &md->flags))
		return;

	thaw_bdev(md->suspended_bdev, md->frozen_sb);
	md->frozen_sb = NULL;
	clear_bit(DMF_FROZEN, &md->flags);
}

/*
 * We need to be able to change a mapping table under a mounted
 * filesystem.  For example we might want to move some data in
 * the background.  Before the table can be swapped with
 * dm_bind_table, dm_suspend must be called to flush any in
 * flight bios and ensure that any further io gets deferred.
 */
int dm_suspend(struct mapped_device *md, unsigned suspend_flags)
{
	struct dm_table *map = NULL;
	DECLARE_WAITQUEUE(wait, current);
	int r = 0;
	int do_lockfs = suspend_flags & DM_SUSPEND_LOCKFS_FLAG ? 1 : 0;
	int noflush = suspend_flags & DM_SUSPEND_NOFLUSH_FLAG ? 1 : 0;

	mutex_lock(&md->suspend_lock);

	if (dm_suspended(md)) {
		r = -EINVAL;
		goto out_unlock;
	}

	map = dm_get_table(md);

	/*
	 * DMF_NOFLUSH_SUSPENDING must be set before presuspend.
	 * This flag is cleared before dm_suspend returns.
	 */
	if (noflush)
		set_bit(DMF_NOFLUSH_SUSPENDING, &md->flags);

	/* This does not get reverted if there's an error later. */
	dm_table_presuspend_targets(map);

	/* bdget() can stall if the pending I/Os are not flushed */
	if (!noflush) {
		md->suspended_bdev = bdget_disk(md->disk, 0);
		if (!md->suspended_bdev) {
			DMWARN("bdget failed in dm_suspend");
			r = -ENOMEM;
			goto out;
		}

		/*
		 * Flush I/O to the device. noflush supersedes do_lockfs,
		 * because lock_fs() needs to flush I/Os.
		 */
		if (do_lockfs) {
			r = lock_fs(md);
			if (r)
				goto out;
		}
	}

	/*
	 * First we set the BLOCK_IO flag so no more ios will be mapped.
	 */
	down_write(&md->io_lock);
	set_bit(DMF_BLOCK_IO, &md->flags);

	add_wait_queue(&md->wait, &wait);
	up_write(&md->io_lock);

	if (dm_request_based(md))
		dm_start_suspend(md, noflush);

	/* unplug */
	if (map)
		dm_table_unplug_all(map);

	/*
	 * Wait for the already-mapped ios to complete.
	 */
	r = dm_wait_for_completion(md);

	down_write(&md->io_lock);
	remove_wait_queue(&md->wait, &wait);

	if (noflush) {
		if (dm_request_based(md))
			/* All requeued requests are already in md->queue */
			clear_bit(DMF_NOFLUSH_SUSPENDING, &md->flags);
		else
			__merge_pushback_list(md);
	}
	up_write(&md->io_lock);

	/* were we interrupted ? */
	if (r < 0) {
		dm_queue_flush(md, DM_WQ_FLUSH_DEFERRED, NULL);

		if (dm_request_based(md))
			dm_abort_suspend(md, noflush);

		unlock_fs(md);
		goto out; /* pushback list is already flushed, so skip flush */
	}

	dm_table_postsuspend_targets(map);

	set_bit(DMF_SUSPENDED, &md->flags);

out:
	if (r && md->suspended_bdev) {
		bdput(md->suspended_bdev);
		md->suspended_bdev = NULL;
	}

	dm_table_put(map);

out_unlock:
	mutex_unlock(&md->suspend_lock);
	return r;
}

int dm_resume(struct mapped_device *md)
{
	int r = -EINVAL;
	struct dm_table *map = NULL;

	mutex_lock(&md->suspend_lock);
	if (!dm_suspended(md))
		goto out;

	map = dm_get_table(md);
	if (!map || !dm_table_get_size(map))
		goto out;

	r = dm_table_resume_targets(map);
	if (r)
		goto out;

	dm_queue_flush(md, DM_WQ_FLUSH_DEFERRED, NULL);

	/*
	 * Flushing deferred I/Os must be done after targets are resumed
	 * so that mapping of targets can work correctly.
	 * Request-based dm is queueing the deferred I/Os in its request_queue.
	 */
	if (dm_request_based(md))
		start_queue(md->queue);

	unlock_fs(md);

	if (md->suspended_bdev) {
		bdput(md->suspended_bdev);
		md->suspended_bdev = NULL;
	}

	clear_bit(DMF_SUSPENDED, &md->flags);

	dm_table_unplug_all(map);

	dm_kobject_uevent(md);

	r = 0;

out:
	dm_table_put(map);
	mutex_unlock(&md->suspend_lock);

	return r;
}

/*-----------------------------------------------------------------
 * Event notification.
 *---------------------------------------------------------------*/
void dm_kobject_uevent(struct mapped_device *md)
{
	kobject_uevent(&md->disk->dev.kobj, KOBJ_CHANGE);
}

uint32_t dm_next_uevent_seq(struct mapped_device *md)
{
	return atomic_add_return(1, &md->uevent_seq);
}

uint32_t dm_get_event_nr(struct mapped_device *md)
{
	return atomic_read(&md->event_nr);
}

int dm_wait_event(struct mapped_device *md, int event_nr)
{
	return wait_event_interruptible(md->eventq,
			(event_nr != atomic_read(&md->event_nr)));
}

void dm_uevent_add(struct mapped_device *md, struct list_head *elist)
{
	unsigned long flags;

	spin_lock_irqsave(&md->uevent_lock, flags);
	list_add(elist, &md->uevent_list);
	spin_unlock_irqrestore(&md->uevent_lock, flags);
}

/*
 * The gendisk is only valid as long as you have a reference
 * count on 'md'.
 */
struct gendisk *dm_disk(struct mapped_device *md)
{
	return md->disk;
}
EXPORT_SYMBOL_GPL(dm_disk);

int dm_suspended(struct mapped_device *md)
{
	return test_bit(DMF_SUSPENDED, &md->flags);
}

int dm_noflush_suspending(struct dm_target *ti)
{
	struct mapped_device *md = dm_table_get_md(ti->table);
	int r = __noflush_suspending(md);

	dm_put(md);

	return r;
}
EXPORT_SYMBOL_GPL(dm_noflush_suspending);

int dm_init_md_mempool(struct mapped_device *md, int type)
{
	if (unlikely(type == DM_TYPE_NONE)) {
		DMWARN("no type is specified, can't initialize mempool");
		return -EINVAL;
	}

	if (md->mempool_type == type)
		return 0;

	if (md->map) {
		/* The md has been using, can't change the mempool type */
		DMWARN("can't change mempool type after a table is bound");
		return -EINVAL;
	}

	/* Not using the md yet, we can still change the mempool type */
	if (md->mempool_type != DM_TYPE_NONE) {
		mempool_destroy(md->io_pool);
		md->io_pool = NULL;
		mempool_destroy(md->tio_pool);
		md->tio_pool = NULL;
		bioset_free(md->bs);
		md->bs = NULL;
		md->mempool_type = DM_TYPE_NONE;
	}

	md->io_pool = (type == DM_TYPE_BIO_BASED) ?
		      mempool_create_slab_pool(MIN_IOS, _io_cache) :
		      mempool_create_slab_pool(MIN_IOS, _bio_info_cache);
	if (!md->io_pool)
		return -ENOMEM;

	md->tio_pool = (type == DM_TYPE_BIO_BASED) ?
		       mempool_create_slab_pool(MIN_IOS, _tio_cache) :
		       mempool_create_slab_pool(MIN_IOS, _rq_tio_cache);
	if (!md->tio_pool)
		goto free_io_pool_and_out;

	md->bs = (type == DM_TYPE_BIO_BASED) ?
		 bioset_create(16, 16) : bioset_create(MIN_IOS, MIN_IOS);
	if (!md->bs)
		goto free_tio_pool_and_out;

	md->mempool_type = type;

	return 0;

free_tio_pool_and_out:
	mempool_destroy(md->tio_pool);
	md->tio_pool = NULL;

free_io_pool_and_out:
	mempool_destroy(md->io_pool);
	md->io_pool = NULL;

	return -ENOMEM;
}

static struct block_device_operations dm_blk_dops = {
	.open = dm_blk_open,
	.release = dm_blk_close,
	.ioctl = dm_blk_ioctl,
	.getgeo = dm_blk_getgeo,
	.owner = THIS_MODULE
};

EXPORT_SYMBOL(dm_get_mapinfo);

/*
 * module hooks
 */
module_init(dm_init);
module_exit(dm_exit);

module_param(major, uint, 0);
MODULE_PARM_DESC(major, "The major number of the device mapper");
MODULE_DESCRIPTION(DM_NAME " driver");
MODULE_AUTHOR("Joe Thornber <dm-devel@redhat.com>");
MODULE_LICENSE("GPL");
