/*********************************************************************************
 ** Copyright (c) 2011-2012 Petros Koutoupis
 ** All rights reserved.
 **
 ** filename: rxcache.h
 ** description: Device mapper target for block-level disk write-through and
 **     read-ahead caching. This module is based on Flashcache-wt:
 **      Copyright 2010 Facebook, Inc.
 **      Author: Mohan Srinivasan (mohan@facebook.com)
 **
 **     Which in turn was based on DM-Cache:
 **      Copyright (C) International Business Machines Corp., 2006
 **      Author: Ming Zhao (mingzhao@ufl.edu)
 ** 
 ** created: 3Dec11, petros@petroskoutoupis.com
 ** modified:
 **
 ** This file is licensed under GPLv2.
 **
 ** This program is free software; you can redistribute it and/or
 ** modify it under the terms of the GNU General Public License as
 ** published by the Free Software Foundation; either version 2 of the
 ** License, or (at your option) any later version.
 **
 ** This program is distributed in the hope that it will be useful, but
 ** WITHOUT ANY WARRANTY; without even the implied warranty of
 ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 ** General Public License for more details.
 **
 ** You should have received a copy of the GNU General Public License
 ** along with this program; if not, write to the Free Software
 ** Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
 ** USA
 **
 ********************************************************************************/

#include <asm/atomic.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/list.h>
#include <linux/blkdev.h>
#include <linux/bio.h>
#include <linux/vmalloc.h>
#include <linux/slab.h>
#include <linux/hash.h>
#include <linux/spinlock.h>
#include <linux/workqueue.h>
#include <linux/pagemap.h>
#include <linux/random.h>
#include <linux/version.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/hardirq.h>
#include <asm/kmap_types.h>
#include <linux/dm-io.h>
#include <linux/device-mapper.h>
#include <linux/bio.h>
#include "rxcommon.h"

/* Like ASSERT() but always compiled in */

#define VERIFY(x) do { \
    if (unlikely(!(x))) { \
        dump_stack(); \
        panic("VERIFY: assertion (%s) failed at %s (%d)\n", \
        #x,  __FILE__ , __LINE__);		    \
    } \
} while(0)

#define DM_MSG_PREFIX  "rxc"
#define RxPREFIX     "rxc"
#define DRIVER_DESC    "RapidCache (rxc) DM target is a write-through caching target with RapidDisk volumes."

#define READCACHE	1
#define WRITECACHE	2
#define READSOURCE	3
#define WRITESOURCE	4
#define READCACHE_DONE	5

/* Default cache parameters */
#define DEFAULT_CACHE_ASSOC	512
#define DEFAULT_BLOCK_SIZE	8	/* 4 KB */
#define CONSECUTIVE_BLOCKS	512

/* States of a cache block */
#define INVALID		0
#define VALID		1	/* Valid */
#define INPROG		2	/* IO (cache fill) is in progress */
#define CACHEREADINPROG	3	/* cache read in progress, don't recycle */
#define INPROG_INVALID	4	/* Write invalidated during a refill */

#define DEV_PATHLEN	128

#ifndef DM_MAPIO_SUBMITTED
#define DM_MAPIO_SUBMITTED	0
#endif

#define WT_MIN_JOBS 1024
/* Number of pages for I/O */
#if LINUX_VERSION_CODE <= KERNEL_VERSION(2,6,39)
#define COPY_PAGES (1024)
#endif

/* Cache context */
struct cache_c {
    struct dm_target *tgt;
	
    struct dm_dev *disk_dev;        /* Source device */
    struct dm_dev *cache_dev;       /* Cache device */

    spinlock_t	cache_spin_lock;
    struct cacheblock *cache;	    /* Hash table for cache blocks */
    u_int8_t *cache_state;
    u_int32_t*set_lru_next;

    struct dm_io_client *io_client; /* Client memory pool*/
    sector_t size;                  /* Cache size */
    unsigned int assoc;	            /* Cache associativity */
    unsigned int block_size;        /* Cache block size */
    unsigned int block_shift;       /* Cache block size in bits */
    unsigned int block_mask;        /* Cache block mask */
    unsigned int consecutive_shift; /* Consecutive blocks size in bits */

    wait_queue_head_t destroyq;	    /* Wait queue for I/O completion */
    atomic_t nr_jobs;               /* Number of I/O jobs */

    /* Stats */
    unsigned long reads;            /* Number of reads */
    unsigned long writes;           /* Number of writes */
    unsigned long cache_hits;       /* Number of cache hits */
    unsigned long replace;          /* Number of cache replacements */
    unsigned long wr_invalidates;   /* Number of write invalidations */
    unsigned long rd_invalidates;   /* Number of read invalidations */
    unsigned long cached_blocks;    /* Number of cached blocks */
    unsigned long cache_wr_replace;
    unsigned long uncached_reads;
    unsigned long uncached_writes;
    unsigned long cache_reads, cache_writes;
    unsigned long disk_reads, disk_writes;	

    char cache_devname[DEV_PATHLEN];
    char disk_devname[DEV_PATHLEN];
};

/* Cache block metadata structure */
struct cacheblock {
    sector_t dbn;                   /* Sector number of the cached block */
};

/* Structure for a kcached job */
struct kcached_job {
    struct list_head list;
    struct cache_c *dmc;
    struct bio *bio;                /* Original bio */
    struct dm_io_region disk;
    struct dm_io_region cache;
    int index;
    int rw;
    int error;
};

u_int64_t size_hist[33];

static struct workqueue_struct *_kcached_wq;
static struct work_struct _kcached_work;
static struct kmem_cache *_job_cache;
static mempool_t *_job_pool;

static DEFINE_SPINLOCK(_job_lock);

static LIST_HEAD(_complete_jobs);
static LIST_HEAD(_io_jobs);


/*********************************************************************************
 * Function Declarations
 ********************************************************************************/
static void cache_read_miss(struct cache_c *dmc, struct bio* bio, int index);
static void cache_write(struct cache_c *dmc, struct bio* bio);
static int cache_invalidate_blocks(struct cache_c *dmc, struct bio *bio);
static void rxc_uncached_io_callback(unsigned long error, void *context);
static void rxc_start_uncached_io(struct cache_c *dmc, struct bio *bio);


/*********************************************************************************
 * Functions Definitions
 ********************************************************************************/
int
dm_io_async_bvec(unsigned int num_regions, struct dm_io_region *where, 
                        int rw, struct bio_vec *bvec, io_notify_fn fn, void *context){
    struct kcached_job *job = (struct kcached_job *)context;
    struct cache_c *dmc = job->dmc;
    struct dm_io_request iorq;

    iorq.bi_rw = rw;
    iorq.mem.type = DM_IO_BVEC;
    iorq.mem.ptr.bvec = bvec;
    iorq.notify.fn = fn;
    iorq.notify.context = context;
    iorq.client = dmc->io_client;

    return dm_io(&iorq, num_regions, where, NULL);
} // dm_io_async_bvec //

static int 
jobs_init(void){
    _job_cache = kmem_cache_create("kcached-jobs-wt",
        sizeof(struct kcached_job), __alignof__(struct kcached_job), 0, NULL);
    if (!_job_cache)
        return -ENOMEM;

    _job_pool = mempool_create(WT_MIN_JOBS, mempool_alloc_slab,
        mempool_free_slab, _job_cache);
    if (!_job_pool) {
        kmem_cache_destroy(_job_cache);
        return -ENOMEM;
    }

    return 0;
} // jobs_init //

static void 
jobs_exit(void){
    BUG_ON(!list_empty(&_complete_jobs));
    BUG_ON(!list_empty(&_io_jobs));

    mempool_destroy(_job_pool);
    kmem_cache_destroy(_job_cache);
    _job_pool = NULL;
    _job_cache = NULL;
} // jobs_exit //

/* Functions to push and pop a job onto the head of a given job list. */
static inline struct kcached_job *
pop(struct list_head *jobs){
    struct kcached_job *job = NULL;
    unsigned long flags;

    spin_lock_irqsave(&_job_lock, flags);
    if (!list_empty(jobs)) {
        job = list_entry(jobs->next, struct kcached_job, list);
        list_del(&job->list);
    }
    spin_unlock_irqrestore(&_job_lock, flags);
    return job;
} // pop //

static inline void 
push(struct list_head *jobs, struct kcached_job *job){
    unsigned long flags;

    spin_lock_irqsave(&_job_lock, flags);
    list_add_tail(&job->list, jobs);
    spin_unlock_irqrestore(&_job_lock, flags);
} // push //

/* Note : io_callback happens from softirq() and you cannot kick off 
 * new IOs from here. Unfortunately, we have to loop back the calls 
 * to kick off new IOs to the workqueue. */
void 
rxc_io_callback(unsigned long error, void *context){
    struct kcached_job *job = (struct kcached_job *) context;
    struct cache_c *dmc = job->dmc;
    struct bio *bio;
    int invalid = 0;
	
    VERIFY(job != NULL);
    bio = job->bio;
    VERIFY(bio != NULL);
    DPRINTK("%s: %s: %s %llu(%llu->%llu,%llu)", RxPREFIX, __func__,
            (job->rw == READ ? "READ" : "WRITE"), bio->bi_sector,
            job->disk.sector, job->cache.sector, job->disk.count);
    if (error)
        DMERR("%s: io error %ld", __func__, error);
    if (job->rw == READSOURCE || job->rw == WRITESOURCE) {
        spin_lock_bh(&dmc->cache_spin_lock);
        if (dmc->cache_state[job->index] != INPROG) {
            VERIFY(dmc->cache_state[job->index] == INPROG_INVALID);
            invalid++;
        }
        spin_unlock_bh(&dmc->cache_spin_lock);
        if (error || invalid) {
            if (invalid)
                DMERR("%s: cache fill invalidation, sector %lu, size %u",
                        __func__, (unsigned long)bio->bi_sector, bio->bi_size);
                bio_endio(bio, error);
                spin_lock_bh(&dmc->cache_spin_lock);
                dmc->cache_state[job->index] = INVALID;
                spin_unlock_bh(&dmc->cache_spin_lock);
                goto out;
        } else {
            /* Kick off the write to the cache */
            job->rw = WRITECACHE;
            push(&_io_jobs, job);
            queue_work(_kcached_wq, &_kcached_work);
            return;
        }
    } else if (job->rw == READCACHE) {
        spin_lock_bh(&dmc->cache_spin_lock);
        VERIFY(dmc->cache_state[job->index] == INPROG_INVALID ||
            dmc->cache_state[job->index] ==  CACHEREADINPROG);
        if (dmc->cache_state[job->index] == INPROG_INVALID)
            invalid++;
        spin_unlock_bh(&dmc->cache_spin_lock);
        if (!invalid && !error) {
            /* Complete the current IO successfully */
            bio_endio(bio, 0);
            spin_lock_bh(&dmc->cache_spin_lock);
            dmc->cache_state[job->index] = VALID;
            spin_unlock_bh(&dmc->cache_spin_lock);
            goto out;
        }
        /* error || invalid || bounce back to source device */
        job->rw = READCACHE_DONE;
        push(&_complete_jobs, job);
        queue_work(_kcached_wq, &_kcached_work);
        return;
    } else {
        VERIFY(job->rw == WRITECACHE);
        bio_endio(bio, 0);
        spin_lock_bh(&dmc->cache_spin_lock);
        VERIFY((dmc->cache_state[job->index] == INPROG) ||
            (dmc->cache_state[job->index] == INPROG_INVALID));
        if (error || dmc->cache_state[job->index] == INPROG_INVALID) {
            dmc->cache_state[job->index] = INVALID;
        } else {
            dmc->cache_state[job->index] = VALID;
            dmc->cached_blocks++;
        }
        spin_unlock_bh(&dmc->cache_spin_lock);
        DPRINTK("%s: Cache Fill: Block %llu, index = %d: Cache state = %d", RxPREFIX,
                        dmc->cache[job->index].dbn, job->index, dmc->cache_state[job->index]);
    }
out:
    mempool_free(job, _job_pool);
    if (atomic_dec_and_test(&dmc->nr_jobs))
        wake_up(&dmc->destroyq);
} // rxc_io_callback //

static int 
do_io(struct kcached_job *job){
    int r = 0;
    struct cache_c *dmc = job->dmc;
    struct bio *bio = job->bio;

    VERIFY(job->rw == WRITECACHE);
    /* Write to cache device */
    dmc->cache_writes++;
    r = dm_io_async_bvec(1, &job->cache, WRITE, bio->bi_io_vec + bio->bi_idx,
        rxc_io_callback, job);
    VERIFY(r == 0); /* In our case, dm_io_async_bvec() must always return 0 */
    return r;
} // do_io //

int 
rxc_do_complete(struct kcached_job *job){
    struct bio *bio = job->bio;
    struct cache_c *dmc = job->dmc;

    VERIFY(job->rw == READCACHE_DONE);
    DPRINTK("%s: %s: %llu", RxPREFIX, __func__, bio->bi_sector);
    /* error || block invalidated while reading from cache */
    spin_lock_bh(&dmc->cache_spin_lock);
    dmc->cache_state[job->index] = INVALID;
    spin_unlock_bh(&dmc->cache_spin_lock);
    mempool_free(job, _job_pool);
    if (atomic_dec_and_test(&dmc->nr_jobs))
        wake_up(&dmc->destroyq);
    /* Kick this IO back to the source bdev */
    rxc_start_uncached_io(dmc, bio);
    return 0;
} // rxc_do_complete //

static void
process_jobs(struct list_head *jobs, int (*fn) (struct kcached_job *)){
    struct kcached_job *job;

    while ((job = pop(jobs)))
        (void)fn(job);
} // process_jobs //

static void 
do_work(struct work_struct *work){
    process_jobs(&_complete_jobs, rxc_do_complete);
    process_jobs(&_io_jobs, do_io);
} // do_work //

static int 
kcached_init(struct cache_c *dmc){
    init_waitqueue_head(&dmc->destroyq);
    atomic_set(&dmc->nr_jobs, 0);
    return 0;
} // kcached_init //

void 
kcached_client_destroy(struct cache_c *dmc){
    /* Wait for completion of all jobs submitted by this client. */
    wait_event(dmc->destroyq, !atomic_read(&dmc->nr_jobs));
} // kcached_client_detroy //

/* Map a block from the source device to a block in the cache device. */
static unsigned long 
hash_block(struct cache_c *dmc, sector_t dbn){
    unsigned long set_number, value, tmpval;

    value = (unsigned long)
    (dbn >> (dmc->block_shift + dmc->consecutive_shift));
    tmpval = value;
    set_number = do_div(tmpval, (dmc->size >> dmc->consecutive_shift));
    DPRINTK("%s: Hash: %llu(%lu)->%lu", RxPREFIX, dbn, value, set_number);
    return set_number;
} // hash_block //

static int
find_valid_dbn(struct cache_c *dmc, sector_t dbn, int start_index, int *index){
    int i;
    int end_index = start_index + dmc->assoc;

    for (i = start_index ; i < end_index ; i++) {
        if (dbn == dmc->cache[i].dbn && (dmc->cache_state[i] == VALID || 
            dmc->cache_state[i] == CACHEREADINPROG || dmc->cache_state[i] == INPROG)) {
            *index = i;
            return dmc->cache_state[i];
        }
    }
    return -1;
} // find_valid_dbn //

static void
find_invalid_dbn(struct cache_c *dmc, int start_index, int *index){
    int i;
    int end_index = start_index + dmc->assoc;

    /* Find INVALID slot that we can reuse */
    for (i = start_index ; i < end_index ; i++) {
        if (dmc->cache_state[i] == INVALID) {
            *index = i;
            return;
        }
    }
} // find_invalid_dbn //

static void
find_reclaim_dbn(struct cache_c *dmc, int start_index, int *index){
    int i;
    int end_index = start_index + dmc->assoc;
    int set = start_index / dmc->assoc;
    int slots_searched = 0;
	
    /* Find the "oldest" VALID slot to recycle. For each set, we keep
     * track of the next "lru" slot to pick off. Each time we pick off
     * a VALID entry to recycle we advance this pointer. So  we sweep
     * through the set looking for next blocks to recycle. This
     * approximates to FIFO (modulo for blocks written through). */
    i = dmc->set_lru_next[set];
    while (slots_searched < dmc->assoc) {
        VERIFY(i >= start_index);
        VERIFY(i < end_index);
        if (dmc->cache_state[i] == VALID) {
            *index = i;
            break;
        }
        slots_searched++;
        i++;
        if (i == end_index)
        i = start_index;
    }
    i++;
    if (i == end_index)
        i = start_index;
    dmc->set_lru_next[set] = i;
} // find_reclaim_dbn //

/* dbn is the starting sector, io_size is the number of sectors. */
static int 
cache_lookup(struct cache_c *dmc, struct bio *bio, int *index){
    sector_t dbn = bio->bi_sector;
#if defined RxC_DEBUG
    int io_size = to_sector(bio->bi_size);
#endif
    unsigned long set_number = hash_block(dmc, dbn);
    int invalid = -1, oldest_clean = -1;
    int start_index;
    int ret;

    start_index = dmc->assoc * set_number;
    DPRINTK("%s: Cache read lookup : dbn %llu(%lu), set = %d",
            RxPREFIX, dbn, io_size, set_number);
    ret = find_valid_dbn(dmc, dbn, start_index, index);
    if (ret == VALID || ret == INPROG || ret == CACHEREADINPROG) {
        DPRINTK("%s: Cache read lookup: Block %llu(%lu): ret %d VALID/INPROG index %d",
                        RxPREFIX, dbn, io_size, ret, *index);
        /* We found the exact range of blocks we are looking for */
        return ret;
    }
    DPRINTK("%s: Cache read lookup: Block %llu(%lu):%d INVALID", RxPREFIX, dbn, io_size, ret);
    VERIFY(ret == -1);
    find_invalid_dbn(dmc, start_index, &invalid);
    if (invalid == -1) {
        /* We didn't find an invalid entry, search for oldest valid entry */
        find_reclaim_dbn(dmc, start_index, &oldest_clean);
    }
    /* Cache miss : We can't choose an entry marked INPROG, but choose the oldest
     * INVALID or the oldest VALID entry. */
    *index = start_index + dmc->assoc;
    if (invalid != -1) {
        DPRINTK("%s: Cache read lookup MISS (INVALID): dbn %llu(%lu), set = %d, index = %d, start_index = %d",
                        RxPREFIX, dbn, io_size, set_number, invalid, start_index);
            *index = invalid;
    } else if (oldest_clean != -1) {
        DPRINTK("%s: Cache read lookup MISS (VALID): dbn %llu(%lu), set = %d, index = %d, start_index = %d",
                        RxPREFIX, dbn, io_size, set_number, oldest_clean, start_index);
        *index = oldest_clean;
    } else {
        DPRINTK("%s: Cache read lookup MISS (NOROOM): dbn %llu(%lu), set = %d",
                        RxPREFIX, dbn, io_size, set_number);
    }
    if (*index < (start_index + dmc->assoc))
        return INVALID;
    else
        return -1;
} // cache_lookup //

static struct kcached_job *
new_kcached_job(struct cache_c *dmc, struct bio* bio, int index){
    struct kcached_job *job;
	
    job = mempool_alloc(_job_pool, GFP_NOIO);
    if (job == NULL)
        return NULL;
    job->disk.bdev = dmc->disk_dev->bdev;
    job->disk.sector = bio->bi_sector;
    if (index != -1)
        job->disk.count = dmc->block_size;
    else
        job->disk.count = to_sector(bio->bi_size);
    job->cache.bdev = dmc->cache_dev->bdev;
    if (index != -1) {
        job->cache.sector = index << dmc->block_shift;
        job->cache.count = dmc->block_size;
    }
    job->dmc = dmc;
    job->bio = bio;
    job->index = index;
    job->error = 0;
    return job;
} // new_kcached_job //

static void
cache_read_miss(struct cache_c *dmc, struct bio* bio, int index){
    struct kcached_job *job;

    DPRINTK("%s: Cache Read Miss sector %llu %u bytes, index %d)",
                RxPREFIX, bio->bi_sector, bio->bi_size, index);

    job = new_kcached_job(dmc, bio, index);
    if (unlikely(job == NULL)) {
        DMERR("%s: Cannot allocate job\n", __func__);
        spin_lock_bh(&dmc->cache_spin_lock);
        dmc->cache_state[index] = INVALID;
        spin_unlock_bh(&dmc->cache_spin_lock);
        bio_endio(bio, -EIO);
    } else {
        job->rw = READSOURCE; /* Fetch data from the source device */
        DPRINTK("%s: Queue job for %llu", RxPREFIX, bio->bi_sector);
        atomic_inc(&dmc->nr_jobs);
        dmc->disk_reads++;
        dm_io_async_bvec(1, &job->disk, READ,
            bio->bi_io_vec + bio->bi_idx, rxc_io_callback, job);
    }
} // cache_read_miss //

static void
cache_read(struct cache_c *dmc, struct bio *bio){
    int index;
    int res;

    DPRINTK("%s: Got a %s for %llu  %u bytes)", RxPREFIX, (bio_rw(bio) == READ ? "READ":"READA"),
                    bio->bi_sector, bio->bi_size);

    spin_lock_bh(&dmc->cache_spin_lock);
    res = cache_lookup(dmc, bio, &index);
    /* Cache Hit */
    if ((res == VALID) && (dmc->cache[index].dbn == bio->bi_sector)) {
        struct kcached_job *job;

        dmc->cache_state[index] = CACHEREADINPROG;
        dmc->cache_hits++;
        spin_unlock_bh(&dmc->cache_spin_lock);
        DPRINTK("%s: Cache read: Block %llu(%lu), index = %d:%s", RxPREFIX,
                        bio->bi_sector, bio->bi_size, index, "CACHE HIT");
        job = new_kcached_job(dmc, bio, index);
        if (unlikely(job == NULL)) {
            /* Can't allocate job, bounce back error */
            DMERR("cache_read(_hit): Cannot allocate job\n");
            spin_lock_bh(&dmc->cache_spin_lock);
            dmc->cache_state[index] = VALID;
            spin_unlock_bh(&dmc->cache_spin_lock);
            bio_endio(bio, -EIO);
        } else {
            job->rw = READCACHE; /* Fetch data from the source device */
            DPRINTK("%s: Queue job for %llu", RxPREFIX, bio->bi_sector);
            atomic_inc(&dmc->nr_jobs);
            dmc->cache_reads++;
            dm_io_async_bvec(1, &job->cache, READ, bio->bi_io_vec + bio->bi_idx,
            rxc_io_callback, job);
        }
        return;
    }
    /* In all cases except for a cache hit (and VALID), test for potential 
     * invalidations that we need to do. */
    if (cache_invalidate_blocks(dmc, bio) > 0) {
        /* A non zero return indicates an inprog invalidation */
        spin_unlock_bh(&dmc->cache_spin_lock);
        /* Start uncached IO */
        rxc_start_uncached_io(dmc, bio);
        return;
    }
    if (res == -1 || res >= INPROG) {
        /* We either didn't find a cache slot in the set we were looking at or
         * the block we are trying to read is being refilled into cache. */
        spin_unlock_bh(&dmc->cache_spin_lock);
        DPRINTK("%s: Cache read: Block %llu(%lu):%s", RxPREFIX, bio->bi_sector,
                        bio->bi_size, "CACHE MISS & NO ROOM");
        /* Start uncached IO */
        rxc_start_uncached_io(dmc, bio);
        return;
    }
    /* (res == INVALID) Cache Miss And we found cache blocks to replace
     * Claim the cache blocks before giving up the spinlock */
    if (dmc->cache_state[index] == VALID) {
        dmc->cached_blocks--;
        dmc->replace++;
    }
    dmc->cache_state[index] = INPROG;
    dmc->cache[index].dbn = bio->bi_sector;
    spin_unlock_bh(&dmc->cache_spin_lock);

    DPRINTK("%s: Cache read: Block %llu(%lu), index = %d:%s", RxPREFIX, bio->bi_sector,
                    bio->bi_size, index, "CACHE MISS & REPLACE");
    cache_read_miss(dmc, bio, index);
} // cache_read //

static int
cache_invalidate_block_set(struct cache_c *dmc, int set, sector_t io_start, sector_t io_end, 
                            int rw, int *inprog_inval){
    int start_index, end_index, i;
    int invalidations = 0;
	
    start_index = dmc->assoc * set;
    end_index = start_index + dmc->assoc;
    for (i = start_index ; i < end_index ; i++) {
        sector_t start_dbn = dmc->cache[i].dbn;
        sector_t end_dbn = start_dbn + dmc->block_size;
		
        if (dmc->cache_state[i] == INVALID || dmc->cache_state[i] == INPROG_INVALID)
            continue;
        if ((io_start >= start_dbn && io_start < end_dbn) ||
            (io_end >= start_dbn && io_end < end_dbn)) {
            /* We have a match */
            if (rw == WRITE)
                dmc->wr_invalidates++;
            else
                dmc->rd_invalidates++;
            invalidations++;
            if (dmc->cache_state[i] == VALID) {
                dmc->cached_blocks--;			
                dmc->cache_state[i] = INVALID;
                DPRINTK("%s: Cache invalidate: Block %llu VALID", RxPREFIX, start_dbn);
            } else if (dmc->cache_state[i] >= INPROG) {
                (*inprog_inval)++;
                dmc->cache_state[i] = INPROG_INVALID;
                DMERR("%s: sector %lu, size %lu, rw %d", __func__,
                        (unsigned long)io_start, (unsigned long)io_end - (unsigned long)io_start, rw);
                DPRINTK("%s: Cache invalidate: Block %llu INPROG", RxPREFIX, start_dbn);
            }
        }
    }
    return invalidations;
} // cache_invalidate_block_set //

/* Since md will break up IO into blocksize pieces, we only really need to check 
 * the start set and the end set for overlaps. */
static int
cache_invalidate_blocks(struct cache_c *dmc, struct bio *bio){	
    sector_t io_start = bio->bi_sector;
    sector_t io_end = bio->bi_sector + (to_sector(bio->bi_size) - 1);
    int start_set, end_set;
    int inprog_inval_start = 0, inprog_inval_end = 0;
	
    start_set = hash_block(dmc, io_start);
    end_set = hash_block(dmc, io_end);
    (void)cache_invalidate_block_set(dmc, start_set, io_start, io_end,  
        bio_data_dir(bio), &inprog_inval_start);
    if (start_set != end_set)
        cache_invalidate_block_set(dmc, end_set, io_start, io_end,  
            bio_data_dir(bio),  &inprog_inval_end);
    return (inprog_inval_start + inprog_inval_end);
} // cache_invalidate_blocks //

static void
cache_write(struct cache_c *dmc, struct bio* bio){
    int index;
    int res;
    struct kcached_job *job;

    spin_lock_bh(&dmc->cache_spin_lock);
    if (cache_invalidate_blocks(dmc, bio) > 0) {
        /* A non zero return indicates an inprog invalidation */
        spin_unlock_bh(&dmc->cache_spin_lock);
        /* Start uncached IO */
        rxc_start_uncached_io(dmc, bio);
        return;
    }
    res = cache_lookup(dmc, bio, &index);
    VERIFY(res == -1 || res == INVALID);
    if (res == -1) {
        spin_unlock_bh(&dmc->cache_spin_lock);
        /* Start uncached IO */
        rxc_start_uncached_io(dmc, bio);
        return;
    }
    if (dmc->cache_state[index] == VALID) {
        dmc->cached_blocks--;
        dmc->cache_wr_replace++;
    }
    dmc->cache_state[index] = INPROG;
    dmc->cache[index].dbn = bio->bi_sector;
    spin_unlock_bh(&dmc->cache_spin_lock);
    job = new_kcached_job(dmc, bio, index);
    if (unlikely(job == NULL)) {
        DMERR("%s: Cannot allocate job\n", __func__);
        spin_lock_bh(&dmc->cache_spin_lock);
        dmc->cache_state[index] = INVALID;
        spin_unlock_bh(&dmc->cache_spin_lock);
        bio_endio(bio, -EIO);
        return;
    }
    job->rw = WRITESOURCE; /* Write data to the source device */
    DPRINTK("%s: Queue job for %llu", RxPREFIX, bio->bi_sector);
    atomic_inc(&job->dmc->nr_jobs);
    dmc->disk_writes++;
    dm_io_async_bvec(1, &job->disk, WRITE, bio->bi_io_vec + bio->bi_idx,
        rxc_io_callback, job);
    return;
} // cache_write //

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,32)
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,36)
#define bio_barrier(bio)        ((bio)->bi_rw & (1 << BIO_RW_BARRIER))
#else
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,37)
#define bio_barrier(bio)        ((bio)->bi_rw & REQ_HARDBARRIER)
#else
#define bio_barrier(bio)        ((bio)->bi_rw & REQ_FLUSH)
#endif
#endif
#endif

/* Decide the mapping and perform necessary cache operations for a bio request. */
int 
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,8,0)
rxc_map(struct dm_target *ti, struct bio *bio){
#else
rxc_map(struct dm_target *ti, struct bio *bio, union map_info *map_context){
#endif
    struct cache_c *dmc = (struct cache_c *) ti->private;
    int sectors = to_sector(bio->bi_size);

    if (sectors <= 32)
    size_hist[sectors]++;

    DPRINTK("%s: Got a %s for %llu %u bytes)", RxPREFIX, bio_rw(bio) == WRITE ? "WRITE" : (bio_rw(bio) == READ ?
                "READ":"READA"), bio->bi_sector, bio->bi_size);

    if (bio_barrier(bio))
        return -EOPNOTSUPP;

    VERIFY(to_sector(bio->bi_size) <= dmc->block_size);

    if (bio_data_dir(bio) == READ)
        dmc->reads++;
    else
        dmc->writes++;		

    if (to_sector(bio->bi_size) != dmc->block_size) {
        spin_lock_bh(&dmc->cache_spin_lock);
        (void)cache_invalidate_blocks(dmc, bio);
        spin_unlock_bh(&dmc->cache_spin_lock);
        /* Start uncached IO */
        rxc_start_uncached_io(dmc, bio);
    } else {
        if (bio_data_dir(bio) == READ)
            cache_read(dmc, bio);
        else
            cache_write(dmc, bio);
    }
    return DM_MAPIO_SUBMITTED;
} // rxc_map //

static void
rxc_uncached_io_callback(unsigned long error, void *context){
    struct kcached_job *job = (struct kcached_job *) context;
    struct cache_c *dmc = job->dmc;

    spin_lock_bh(&dmc->cache_spin_lock);
    if (bio_data_dir(job->bio) == READ)
        dmc->uncached_reads++;
    else
        dmc->uncached_writes++;		
    (void)cache_invalidate_blocks(dmc, job->bio);
    spin_unlock_bh(&dmc->cache_spin_lock);
    bio_endio(job->bio, error);
    mempool_free(job, _job_pool);
    if (atomic_dec_and_test(&dmc->nr_jobs))
        wake_up(&dmc->destroyq);
} // rxc_uncached_io_callback //

static void
rxc_start_uncached_io(struct cache_c *dmc, struct bio *bio){
    int is_write = (bio_data_dir(bio) == WRITE);
    struct kcached_job *job;
	
    job = new_kcached_job(dmc, bio, -1);
    if (unlikely(job == NULL)) {
        bio_endio(bio, -EIO);
        return;
    }
    atomic_inc(&dmc->nr_jobs);
    if (bio_data_dir(job->bio) == READ)
        dmc->disk_reads++;
    else
        dmc->disk_writes++;			
    dm_io_async_bvec(1, &job->disk, ((is_write) ? WRITE : READ),
        bio->bi_io_vec + bio->bi_idx, rxc_uncached_io_callback, job);
} // rxc_start_uncached_io //

static int inline
rxc_get_dev(struct dm_target *ti, char *pth, struct dm_dev **dmd,
		      char *dmc_dname, sector_t tilen){
    int rc;

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,34)
    rc = dm_get_device(ti, pth, dm_table_get_mode(ti->table), dmd);
#else
#if defined(RHEL_MAJOR) && RHEL_MAJOR == 6
    rc = dm_get_device(ti, pth, dm_table_get_mode(ti->table), dmd);
#else 
    rc = dm_get_device(ti, pth, 0, tilen, dm_table_get_mode(ti->table), dmd);
#endif
#endif
    if (!rc)
        strncpy(dmc_dname, pth, DEV_PATHLEN);
    return rc;
} // rxc_get_dev //

/* Construct a cache mapping.
 *  arg[0]: path to source device
 *  arg[1]: path to cache device
 *  arg[2]: cache block size (in sectors)
 *  arg[3]: cache size (in blocks)
 *  arg[4]: cache associativity */
static int
cache_ctr(struct dm_target *ti, unsigned int argc, char **argv){
    struct cache_c *dmc;
    unsigned int consecutive_blocks;
    sector_t i, order, tmpsize;
    sector_t data_size, dev_size;
    int r = -EINVAL;

    if (argc < 2) {
        ti->error = "rxc: Need at least 2 arguments";
        goto bad;
    }

    dmc = kzalloc(sizeof(*dmc), GFP_KERNEL);
    if (dmc == NULL) {
        ti->error = "rxc: Failed to allocate cache context";
        r = ENOMEM;
        goto bad;
    }

    dmc->tgt = ti;

    if (rxc_get_dev(ti, argv[0], &dmc->disk_dev, dmc->disk_devname, ti->len)) {
        ti->error = "rxc: Disk device lookup failed";
        goto bad1;
    }
    if (strncmp(argv[1], "/dev/rxd", 8) != 0){
        printk(KERN_ERR "%s: %s is not a valid cache device for rxcache.", RxPREFIX, argv[1]);
        ti->error = "rxc: Invalid cache device. Not an rxdsk volume.";
        goto bad2;
    }
    if (rxc_get_dev(ti, argv[1], &dmc->cache_dev, dmc->cache_devname, 0)) {
        ti->error = "rxc: Cache device lookup failed";
        goto bad2;
    }

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,27)
#if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,39)
    dmc->io_client = dm_io_client_create();
#else
    dmc->io_client = dm_io_client_create(COPY_PAGES);
#endif
    if (IS_ERR(dmc->io_client)) {
        r = PTR_ERR(dmc->io_client);
        ti->error = "Failed to create io client\n";
        goto bad2;
    }
#endif

    r = kcached_init(dmc);
    if (r) {
        ti->error = "Failed to initialize kcached";
        goto bad3;
    }
    dmc->assoc = DEFAULT_CACHE_ASSOC;

    if (argc >= 3) {
        if (sscanf(argv[2], "%u", &dmc->block_size) != 1) {
            ti->error = "rxc: Invalid block size";
            r = -EINVAL;
            goto bad4;
        }
        if (!dmc->block_size || (dmc->block_size & (dmc->block_size - 1))) {
            ti->error = "rxc: Invalid block size";
            r = -EINVAL;
            goto bad4;
        }
    } else
        dmc->block_size = DEFAULT_BLOCK_SIZE;

    dmc->block_shift = ffs(dmc->block_size) - 1;
    dmc->block_mask = dmc->block_size - 1;

    /* dmc->size is specified in sectors here, and converted to blocks below */
    if (argc >= 4) {
        if (sscanf(argv[3], "%lu", (unsigned long *)&dmc->size) != 1) {
            ti->error = "rxc: Invalid cache size";
            r = -EINVAL;
            goto bad4;
        }
    } else {
        dmc->size = to_sector(dmc->cache_dev->bdev->bd_inode->i_size);
    }

    if (argc >= 5) {
        if (sscanf(argv[4], "%u", &dmc->assoc) != 1) {
            ti->error = "rxc: Invalid cache associativity";
            r = -EINVAL;
            goto bad4;
        }
        if (!dmc->assoc || (dmc->assoc & (dmc->assoc - 1)) || dmc->size < dmc->assoc) {
           ti->error = "rxc: Invalid cache associativity";
           r = -EINVAL;
           goto bad4;
        }
    } else
        dmc->assoc = DEFAULT_CACHE_ASSOC;

    /* Convert size (in sectors) to blocks. Then round size (in blocks now) down to a
     * multiple of associativity */
    do_div(dmc->size, dmc->block_size);
    tmpsize = dmc->size;
    do_div(tmpsize, dmc->assoc);
    dmc->size = tmpsize * dmc->assoc;

    dev_size = to_sector(dmc->cache_dev->bdev->bd_inode->i_size);
    data_size = dmc->size * dmc->block_size;
    if (data_size > dev_size) {
        DMERR("Requested cache size exeeds the cache device's capacity (%lu>%lu)",
                (unsigned long)data_size, (unsigned long)dev_size);
        ti->error = "rxc: Invalid cache size";
        r = -EINVAL;
        goto bad4;
    }

    consecutive_blocks = dmc->assoc;
    dmc->consecutive_shift = ffs(consecutive_blocks) - 1;

    order = dmc->size * sizeof(struct cacheblock);
#if defined(__x86_64__)
    DMINFO("Allocate %luKB (%luB per) mem for %lu-entry cache" \
            "(capacity:%luMB, associativity:%u, block size:%u sectors(%uKB))",
            (unsigned long)order >> 10, sizeof(struct cacheblock), (unsigned long)dmc->size,
            (unsigned long)data_size >> (20-SECTOR_SHIFT), dmc->assoc, dmc->block_size,
            dmc->block_size >> (10-SECTOR_SHIFT));
#else
    DMINFO("Allocate %luKB (%dB per) mem for %lu-entry cache" \
            "(capacity:%luMB, associativity:%u, block size:%u sectors(%uKB))",
            (unsigned long)order >> 10, sizeof(struct cacheblock), (unsigned long)dmc->size,
            (unsigned long)data_size >> (20-SECTOR_SHIFT), dmc->assoc, dmc->block_size,
            dmc->block_size >> (10-SECTOR_SHIFT));
#endif
    dmc->cache = (struct cacheblock *)vmalloc(order);
    if (!dmc->cache) {
        ti->error = "Unable to allocate memory";
        r = -ENOMEM;
        goto bad4;
    }
    dmc->cache_state = (u_int8_t *)vmalloc(dmc->size);
    if (!dmc->cache_state) {
        ti->error = "Unable to allocate memory";
        r = -ENOMEM;
        vfree((void *)dmc->cache);
        goto bad4;
    }		
	
    order = (dmc->size >> dmc->consecutive_shift) * sizeof(u_int32_t);
    dmc->set_lru_next = (u_int32_t *)vmalloc(order);
    if (!dmc->set_lru_next) {
        ti->error = "Unable to allocate memory";
        r = -ENOMEM;
        vfree((void *)dmc->cache);
        vfree((void *)dmc->cache_state);
        goto bad4;
    }				

    /* Initialize the cache structs */
    for (i = 0; i < dmc->size ; i++) {
        dmc->cache[i].dbn = 0;
        dmc->cache_state[i] = INVALID;
    }

    /* Initialize the point where LRU sweeps begin for each set */
    for (i = 0 ; i < (dmc->size >> dmc->consecutive_shift) ; i++)
        dmc->set_lru_next[i] = i * dmc->assoc;

    spin_lock_init(&dmc->cache_spin_lock);

    dmc->reads = 0;
    dmc->writes = 0;
    dmc->cache_hits = 0;
    dmc->replace = 0;
    dmc->wr_invalidates = 0;
    dmc->rd_invalidates = 0;
    dmc->cached_blocks = 0;
    dmc->cache_wr_replace = 0;

#if LINUX_VERSION_CODE < KERNEL_VERSION(3,6,0)
    ti->split_io = dmc->block_size;
#else
    r = dm_set_target_max_io_len(ti, dmc->block_size);
    if(r)
        goto bad4;
#endif
    ti->private = dmc;

    return 0;

bad4:
    kcached_client_destroy(dmc);
bad3:
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,27)
    dm_io_client_destroy(dmc->io_client);
#endif
    dm_put_device(ti, dmc->cache_dev);
bad2:
    dm_put_device(ti, dmc->disk_dev);
bad1:
    kfree(dmc);
bad:
    return r;
} // cache_ctr //

/* Destroy the cache mapping. */
static void 
cache_dtr(struct dm_target *ti){
    struct cache_c *dmc = (struct cache_c *) ti->private;
    kcached_client_destroy(dmc);

    if (dmc->reads + dmc->writes > 0) {
        DMINFO("stats: \n\treads(%lu), writes(%lu)\n", dmc->reads, dmc->writes);
        DMINFO("\tcache hits(%lu),replacement(%lu), write replacement(%lu)\n" \
                "\tread invalidates(%lu), write invalidates(%lu)\n",
                dmc->cache_hits, dmc->replace, dmc->cache_wr_replace,
                dmc->rd_invalidates, dmc->wr_invalidates);
        DMINFO("conf:\n\tcapacity(%luM), associativity(%u), block size(%uK)\n" \
                "\ttotal blocks(%lu), cached blocks(%lu)\n",
                (unsigned long)dmc->size*dmc->block_size>>11, dmc->assoc,
                dmc->block_size>>(10-SECTOR_SHIFT), 
                (unsigned long)dmc->size, dmc->cached_blocks);
    }

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,27)
    dm_io_client_destroy(dmc->io_client);
#endif
    vfree((void *)dmc->cache);
    vfree((void *)dmc->cache_state);
    vfree((void *)dmc->set_lru_next);

    dm_put_device(ti, dmc->disk_dev);
    dm_put_device(ti, dmc->cache_dev);
    kfree(dmc);
} // cache_dtr //

static void
rxc_status_info(struct cache_c *dmc, status_type_t type, char *result, unsigned int maxlen){
    int sz = 0; /* DMEMIT */

    DMEMIT("stats: \n\treads(%lu), writes(%lu)\n", dmc->reads, dmc->writes);

    DMEMIT("\tcache hits(%lu) replacement(%lu), write replacement(%lu)\n" \
            "\tread invalidates(%lu), write invalidates(%lu)\n" \
            "\tuncached reads(%lu), uncached writes(%lu)\n" \
            "\tdisk reads(%lu), disk writes(%lu)\n"	\
            "\tcache reads(%lu), cache writes(%lu)\n",
            dmc->cache_hits, dmc->replace, dmc->cache_wr_replace,
            dmc->rd_invalidates, dmc->wr_invalidates, 
            dmc->uncached_reads, dmc->uncached_writes,
            dmc->disk_reads, dmc->disk_writes,
            dmc->cache_reads, dmc->cache_writes);
} // rxc_status_info //

static void
rxc_status_table(struct cache_c *dmc, status_type_t type, char *result, unsigned int maxlen){
    int i;
    int sz = 0; /* DMEMIT */

    DMEMIT("conf:\n\trxd dev (%s), disk dev (%s) mode (%s)\n" \
            "\tcapacity(%luM), associativity(%u), block size(%uK)\n" \
            "\ttotal blocks(%lu), cached blocks(%lu)\n",
            dmc->cache_devname, dmc->disk_devname, "WRITETHROUGH",
            (unsigned long)dmc->size*dmc->block_size>>11, dmc->assoc,
            dmc->block_size>>(10-SECTOR_SHIFT), 
            (unsigned long)dmc->size, dmc->cached_blocks);
    DMEMIT(" Size Hist: ");
    for (i = 1 ; i <= 32 ; i++) {
    if (size_hist[i] > 0)
        DMEMIT("%d:%llu ", i*512, size_hist[i]);
    }
} // rxc_status_table //

/* Report cache status:
 *  Output cache stats upon request of device status;
 *  Output cache configuration upon request of table status. */
static int 
#if LINUX_VERSION_CODE < KERNEL_VERSION(3,6,0)
cache_status(struct dm_target *ti, status_type_t type, char *result, unsigned int maxlen){
#else
cache_status(struct dm_target *ti, status_type_t type, unsigned status_flags, char *result,
    unsigned int maxlen){
#endif
    struct cache_c *dmc = (struct cache_c *) ti->private;
	
    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    switch (type) {
        case STATUSTYPE_INFO:
            rxc_status_info(dmc, type, result, maxlen);
            break;
        case STATUSTYPE_TABLE:
            rxc_status_table(dmc, type, result, maxlen);
            break;
    }
    return 0;
} // cache_status //


/****************************************************************************
 *  Functions for manipulating a cache target.
 ****************************************************************************/

static struct target_type cache_target = {
    .name   = "rxcache",
    .version= {2, 0, 0},
    .module = THIS_MODULE,
    .ctr    = cache_ctr,
    .dtr    = cache_dtr,
    .map    = rxc_map,
    .status = cache_status,
};

static int 
rxc_version_show(struct seq_file *seq, void *v){
    seq_printf(seq, "RapidCache Version : %s\n", VERSION_STR);
    return 0;
} // rxc_version_show //

static int 
rxc_version_open(struct inode *inode, struct file *file){
    return single_open(file, &rxc_version_show, NULL);
} // rxc_version_open //

static struct file_operations rxc_version_operations = {
    .open    = rxc_version_open,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = single_release,
};


int __init 
rxc_init(void){
    int r;
    struct proc_dir_entry *entry;

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    r = jobs_init();
    if (r)
        return r;

    _kcached_wq = create_singlethread_workqueue("kcached");
    if (!_kcached_wq) {
        DMERR("failed to start kcached");
        return -ENOMEM;
    }

    INIT_WORK(&_kcached_work, do_work);

    for (r = 0 ; r < 33 ; r++)
        size_hist[r] = 0;
    r = dm_register_target(&cache_target);
    if (r < 0) {
        DMERR("cache: register failed %d", r);
    }

    entry = create_proc_entry("rxc", 0, NULL);
    if (entry)
        entry->proc_fops =  &rxc_version_operations;

    printk(KERN_INFO "%s: Module successfully loaded.\n", RxPREFIX);

    return r;
} // rxc_init //


void 
rxc_exit(void){

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    dm_unregister_target(&cache_target);
    jobs_exit();
    destroy_workqueue(_kcached_wq);
    remove_proc_entry("rxc", NULL);
    printk(KERN_INFO "%s: Module successfully unloaded.\n", RxPREFIX);
} // rxc_exit //


module_init(rxc_init);
module_exit(rxc_exit);

EXPORT_SYMBOL(rxc_io_callback);
EXPORT_SYMBOL(rxc_do_complete);
EXPORT_SYMBOL(rxc_map);

MODULE_LICENSE("GPL");
MODULE_AUTHOR(DRIVER_AUTHOR);
MODULE_DESCRIPTION(DRIVER_DESC);
MODULE_VERSION(VERSION_STR);
MODULE_INFO(Copyright, COPYRIGHT);
