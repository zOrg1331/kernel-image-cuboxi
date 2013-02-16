/*********************************************************************************
 ** Copyright (c) 2011-2012 Petros Koutoupis
 ** All rights reserved.
 **
 ** filename: rxdsk.c
 ** description: RapidDisk is an enhanced Linux RAM disk module to dynamically
 **     create, remove, and resize RAM drives.
 ** created: 1Jun11, petros@petroskoutoupis.com
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

#include <linux/init.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/version.h>
#include <linux/blkdev.h>
#include <linux/bio.h>
#include <linux/hdreg.h>
#include <linux/proc_fs.h>
#include <linux/errno.h>
#include <linux/radix-tree.h>
#include "rxcommon.h"


#define RxPREFIX             "rxd"
#define DRIVER_DESC          "RapidDisk (rxdsk) is an enhanced RAM disk block device driver."
#define DEVICE_NAME          "rxd"
#define PROC_NODE            "rxctl"
#define BYTES_PER_SECTOR     512
#define MAX_RxDISKS          128

#define FREE_BATCH           16
#define SECTOR_SHIFT         9
#define PAGE_SECTORS_SHIFT   (PAGE_SHIFT - SECTOR_SHIFT)
#define PAGE_SECTORS         (1 << PAGE_SECTORS_SHIFT)

/* ioctls */
#define INVALID_CDQUERY_IOCTL   0x5331
#define RXD_GET_STATS           0x0529


static DEFINE_MUTEX(rxproc_mutex);

struct rxdsk_device {
    int rxdsk_number; 
    struct request_queue *rxdsk_queue;
    struct gendisk *rxdsk_disk;
    struct list_head rxdsk_list;
    unsigned long long max_blk_alloc;  /* to keep track of highest sector write */

    /* Backing store of pages and lock to protect it. This is the contents
     * of the block device. */
    spinlock_t rxdsk_lock;
    struct radix_tree_root rxdsk_pages;
};

static int rxdsk_ma_no = 0 /* major */, rxcnt = 0 /* no. of attached devices */;
static int max_rxcnt = MAX_RxDISKS;
struct proc_dir_entry *rx_proc = NULL;
static LIST_HEAD(rxdsk_devices);

/*********************************************************************************
 * Supported insmod params 
 ********************************************************************************/
module_param(max_rxcnt, int, S_IRUGO);
MODULE_PARM_DESC(max_rxcnt, " Total RAM Disk devices available for use. (Default = 128 = MAX)");

/*********************************************************************************
 * Function Declarations
 ********************************************************************************/
static int read_proc(char *, char **, off_t, int, int *, void *);
static int write_proc(struct file *, const char __user *, unsigned long, void *);
static int rxdsk_do_bvec(struct rxdsk_device *, struct page *, unsigned int, unsigned int, int, sector_t);
static int rxdsk_ioctl(struct block_device *, fmode_t, unsigned int, unsigned long);
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,2,0)
static void rxdsk_make_request(struct request_queue *, struct bio *);
#else
static int rxdsk_make_request(struct request_queue *, struct bio *);
#endif
static int attach_device(int, int); /* disk num, disk size */
static int detach_device(int);      /* disk num */
static int resize_device(int, int); /* disk num, disk size */


/*********************************************************************************
 * Functions Definitions
 ********************************************************************************/
static int
write_proc(struct file *file, const char __user *buffer, unsigned long count, void *data){
    int num, size, err = (int)count;
    char *ptr, *buf;

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    mutex_lock(&rxproc_mutex);

    if (!buffer || count > PAGE_SIZE)
        return -EINVAL;

    buf = (char *)__get_free_page(GFP_KERNEL);
    if (!buf)
        return -ENOMEM;

    if(copy_from_user(buf, buffer, count))
        return -EFAULT;
    
    if(!strncmp("rxdsk attach", buffer, 12)) {
        ptr = buf + 13;
        num = simple_strtoul(ptr, &ptr, 0);
        size = simple_strtoul(ptr + 1, &ptr, 0);

        if(attach_device(num, size) != 0){
            printk(KERN_ERR "%s: Unable to attach rxdsk%d\n", RxPREFIX, num);
            err = -EINVAL;
        }
    }else if(!strncmp("rxdsk detach", buffer, 12)) {
        ptr = buf + 13;
        num = simple_strtoul(ptr, &ptr, 0);
        if(detach_device(num) != 0){
            printk(KERN_ERR "%s: Unable to detach rxdsk%d\n", RxPREFIX, num);
            err = -EINVAL;
        }
    }else if(!strncmp("rxdsk resize", buffer, 12)) {
        ptr = buf + 13;
        num = simple_strtoul(ptr, &ptr, 0);
        size = simple_strtoul(ptr + 1, &ptr, 0);

        if(resize_device(num, size) != 0){
            printk(KERN_ERR "%s: Unable to resize rxdsk%d\n", RxPREFIX, num);
            err = -EINVAL;
        }
    }else{
        printk(KERN_ERR "%s: Unsupported command: %s\n", RxPREFIX, buffer);
        err = -EINVAL;
    }

    free_page((unsigned long)buf);
    mutex_unlock(&rxproc_mutex);

    return err;
}  // write_proc //


static int
read_proc(char *page, char **start, off_t off, int count, int *eof, void *data){
    int len;

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    len = sprintf(page, "RapidDisk (rxdsk) %s\n\nMaximum Number of Attachable Devices: %d\nNumber of "
        "Attached Devices: %d\n\n", VERSION_STR, max_rxcnt, rxcnt);
    
    return len;
} // read_proc //


static struct page *
rxdsk_lookup_page(struct rxdsk_device *rxdsk, sector_t sector){
    pgoff_t idx;
    struct page *page;

    /*
     * The page lifetime is protected by the fact that we have opened the
     * device node -- rxdsk pages will never be deleted under us, so we
     * don't need any further locking or refcounting.
     */
    rcu_read_lock();
    idx = sector >> PAGE_SECTORS_SHIFT; /* sector to page index */
    page = radix_tree_lookup(&rxdsk->rxdsk_pages, idx);
    rcu_read_unlock();

    BUG_ON(page && page->index != idx);

    return page;
} // rxdsk_lookup_page //


static struct page *
rxdsk_insert_page(struct rxdsk_device *rxdsk, sector_t sector){
    pgoff_t idx;
    struct page *page;
    gfp_t gfp_flags;

    page = rxdsk_lookup_page(rxdsk, sector);
    if (page)
                return page;

    /*
     * Must use NOIO because we don't want to recurse back into the
     * block or filesystem layers from page reclaim.
     *
     * Cannot support XIP and highmem, because our ->direct_access
     * routine for XIP must return memory that is always addressable.
     * If XIP was reworked to use pfns and kmap throughout, this
     * restriction might be able to be lifted.
     */
    gfp_flags = GFP_NOIO | __GFP_ZERO;
#ifndef CONFIG_BLK_DEV_XIP
    gfp_flags |= __GFP_HIGHMEM;
#endif
    page = alloc_page(gfp_flags);
    if(!page)
        return NULL;

    if(radix_tree_preload(GFP_NOIO)){
        __free_page(page);
        return NULL;
    }

    spin_lock(&rxdsk->rxdsk_lock);
    idx = sector >> PAGE_SECTORS_SHIFT;
    if(radix_tree_insert(&rxdsk->rxdsk_pages, idx, page)){
        __free_page(page);
        page = radix_tree_lookup(&rxdsk->rxdsk_pages, idx);
        BUG_ON(!page);
        BUG_ON(page->index != idx);
    }else
        page->index = idx;
    spin_unlock(&rxdsk->rxdsk_lock);

    radix_tree_preload_end();

    return page;
} // rxdsk_insert_page //


#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,36)
static void
rxdsk_zero_page(struct rxdsk_device *rxdsk, sector_t sector){
    struct page *page;

    page = rxdsk_lookup_page(rxdsk, sector);
    if (page)
        clear_highpage(page);
} // rxdsk_zero_page //
#endif


static void
rxdsk_free_pages(struct rxdsk_device *rxdsk){
    unsigned long pos = 0;
    struct page *pages[FREE_BATCH];
    int nr_pages;

    do{
        int i;

        nr_pages = radix_tree_gang_lookup(&rxdsk->rxdsk_pages, (void **)pages, pos, FREE_BATCH);

        for(i = 0; i < nr_pages; i++){
            void *ret;

            BUG_ON(pages[i]->index < pos);
            pos = pages[i]->index;
            ret = radix_tree_delete(&rxdsk->rxdsk_pages, pos);
            BUG_ON(!ret || ret != pages[i]);
            __free_page(pages[i]);
        }

        pos++;

    /*
     * This assumes radix_tree_gang_lookup always returns as
     * many pages as possible. If the radix-tree code changes,
     * so will this have to.
     */
    }while(nr_pages == FREE_BATCH);
} // rxdsk_free_pages //


static int
copy_to_rxdsk_setup(struct rxdsk_device *rxdsk, sector_t sector, size_t n){
    unsigned int offset = (sector & (PAGE_SECTORS - 1)) << SECTOR_SHIFT;
    size_t copy;

    copy = min_t(size_t, n, PAGE_SIZE - offset);
    if(!rxdsk_insert_page(rxdsk, sector))
        return -ENOMEM;
    if(copy < n){
        sector += copy >> SECTOR_SHIFT;
        if (!rxdsk_insert_page(rxdsk, sector))
            return -ENOMEM;
    }
    return 0;
} // copy_to_rxdsk_setup //


#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,36)
static void
discard_from_rxdsk(struct rxdsk_device *rxdsk, sector_t sector, size_t n){
    while (n >= PAGE_SIZE) {
        rxdsk_zero_page(rxdsk, sector);
        sector += PAGE_SIZE >> SECTOR_SHIFT;
        n -= PAGE_SIZE;
    }
} // discard_from_rxdsk //
#endif

static void
copy_to_rxdsk(struct rxdsk_device *rxdsk, const void *src, sector_t sector, size_t n){
    struct page *page;
    void *dst;
    unsigned int offset = (sector & (PAGE_SECTORS-1)) << SECTOR_SHIFT;
    size_t copy;

    copy = min_t(size_t, n, PAGE_SIZE - offset);
    page = rxdsk_lookup_page(rxdsk, sector);
    BUG_ON(!page);

#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
    dst = kmap_atomic(page);
#else
    dst = kmap_atomic(page, KM_USER1);
#endif
    memcpy(dst + offset, src, copy);
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
    kunmap_atomic(dst);
#else
    kunmap_atomic(dst, KM_USER1);
#endif

    if(copy < n){
        src += copy;
        sector += copy >> SECTOR_SHIFT;
        copy = n - copy;
        page = rxdsk_lookup_page(rxdsk, sector);
        BUG_ON(!page);

#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
        dst = kmap_atomic(page);
#else
        dst = kmap_atomic(page, KM_USER1);
#endif
        memcpy(dst, src, copy);
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
        kunmap_atomic(dst);
#else
        kunmap_atomic(dst, KM_USER1);
#endif
    }

    if((sector + (n / BYTES_PER_SECTOR)) > rxdsk->max_blk_alloc){
        rxdsk->max_blk_alloc = (sector + (n / BYTES_PER_SECTOR));
    }
} // copy_to_rxdsk //


static void
copy_from_rxdsk(void *dst, struct rxdsk_device *rxdsk, sector_t sector, size_t n){
    struct page *page;
    void *src;
    unsigned int offset = (sector & (PAGE_SECTORS-1)) << SECTOR_SHIFT;
    size_t copy;

    copy = min_t(size_t, n, PAGE_SIZE - offset);
    page = rxdsk_lookup_page(rxdsk, sector);

    if(page){
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
        src = kmap_atomic(page);
#else
        src = kmap_atomic(page, KM_USER1);
#endif
        memcpy(dst, src + offset, copy);
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
        kunmap_atomic(src);
#else
        kunmap_atomic(src, KM_USER1);
#endif
    }else
        memset(dst, 0, copy);

    if(copy < n){
        dst += copy;
        sector += copy >> SECTOR_SHIFT;
        copy = n - copy;
        page = rxdsk_lookup_page(rxdsk, sector);
        if(page){
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
            src = kmap_atomic(page);
#else
            src = kmap_atomic(page, KM_USER1);
#endif
            memcpy(dst, src, copy);
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
            kunmap_atomic(src);
#else
            kunmap_atomic(src, KM_USER1);
#endif
        }else
            memset(dst, 0, copy);
    }
} // copy_from_rxdsk //


static int
rxdsk_do_bvec(struct rxdsk_device *rxdsk, struct page *page, unsigned int len,
        unsigned int off, int rw, sector_t sector){

    void *mem;
    int err = 0;

    if(rw != READ){
        err = copy_to_rxdsk_setup(rxdsk, sector, len);
        if(err)
            goto out;
    }

#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
    mem = kmap_atomic(page);
#else
    mem = kmap_atomic(page, KM_USER0);
#endif
    if(rw == READ){
        copy_from_rxdsk(mem + off, rxdsk, sector, len);
        flush_dcache_page(page);
    }else{
        flush_dcache_page(page);
        copy_to_rxdsk(rxdsk, mem + off, sector, len);
    }
#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,4,0)
    kunmap_atomic(mem);
#else
    kunmap_atomic(mem, KM_USER0);
#endif

out:
    return err;
} //rxdsk_do_bvec //


#if LINUX_VERSION_CODE >= KERNEL_VERSION(3,2,0)
static void
#else
static int
#endif
rxdsk_make_request(struct request_queue *q, struct bio *bio){
    struct block_device *bdev = bio->bi_bdev;
    struct rxdsk_device *rxdsk = bdev->bd_disk->private_data;
    int rw;
    struct bio_vec *bvec;
    sector_t sector;
    int i, err = -EIO;

    sector = bio->bi_sector;
    if((sector + bio_sectors(bio)) > get_capacity(bdev->bd_disk))
        goto out;

    err = 0;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,36)
    if (unlikely(bio->bi_rw & REQ_DISCARD)) {
        discard_from_rxdsk(rxdsk, sector, bio->bi_size);
        goto out;
    }
#endif

    rw = bio_rw(bio);
    if (rw == READA)
        rw = READ;

    bio_for_each_segment(bvec, bio, i){
        unsigned int len = bvec->bv_len;

        err = rxdsk_do_bvec(rxdsk, bvec->bv_page, len, bvec->bv_offset, rw, sector);
        if(err)
            break;
        sector += len >> SECTOR_SHIFT;
    }

out:
    set_bit(BIO_UPTODATE, &bio->bi_flags);
    bio_endio(bio, err);

#if LINUX_VERSION_CODE < KERNEL_VERSION(3,2,0)
    return 0;
#endif
} // rxdsk_make_request //


static int
rxdsk_ioctl(struct block_device *bdev, fmode_t mode, unsigned int cmd, unsigned long arg){
    loff_t size;
    struct rxdsk_device *rxdsk = bdev->bd_disk->private_data;

    DPRINTK("%s: debug: entering %s with cmd: %d\n", RxPREFIX, __func__, cmd);

    switch (cmd) {
        case BLKGETSIZE: {
            size = bdev->bd_inode->i_size;
            if ((size >> 9) > ~0UL)
                return -EFBIG;
            return copy_to_user ((void __user *)arg, &size, sizeof(size)) ? -EFAULT : 0;
        }
        case BLKGETSIZE64: {
            return copy_to_user ((void __user *)arg, &bdev->bd_inode->i_size, sizeof(bdev->bd_inode->i_size)) ? -EFAULT : 0;
        }
        case BLKFLSBUF: {
            /* This is for the kernel's pagecache or buffer cache which sits above our block devices */
            mutex_lock(&bdev->bd_mutex);
            sync_blockdev(bdev);
            invalidate_bdev(bdev);
            mutex_unlock(&bdev->bd_mutex);
            return 0;
        }
        case INVALID_CDQUERY_IOCTL: {
            return -EINVAL;
        }
        case RXD_GET_STATS: {
            return copy_to_user ((void __user *)arg, &rxdsk->max_blk_alloc, sizeof(rxdsk->max_blk_alloc)) ? -EFAULT : 0;
        }
        case BLKPBSZGET: 
        case BLKBSZGET: 
        case BLKSSZGET: {
            size = BYTES_PER_SECTOR;
            return copy_to_user ((void __user *)arg, &size, sizeof(size)) ? -EFAULT : 0;
        }
    }

    printk (KERN_WARNING "%s: 0x%x invalid ioctl.\n", RxPREFIX, cmd);
    return -ENOTTY;             /* unknown command */
} // rxdsk_ioctl //


static const struct block_device_operations rxdsk_fops = {
    .owner = THIS_MODULE,
    .ioctl = rxdsk_ioctl,
};


static int
attach_device(int num, int size){
    struct rxdsk_device *rxdsk, *rxtmp;
    struct gendisk *disk;

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    if(rxcnt > max_rxcnt){
        printk(KERN_WARNING "%s: reached maximum number of attached disks. unable to attach more.\n", RxPREFIX);
        goto out;
    }

    list_for_each_entry(rxtmp, &rxdsk_devices, rxdsk_list){
        if(rxtmp->rxdsk_number == num){
            printk(KERN_WARNING "%s: rxdsk device %d already exists.\n", RxPREFIX, num);
            goto out;
        } 
    }

    rxdsk = kzalloc(sizeof(*rxdsk), GFP_KERNEL);
    if(!rxdsk)
        goto out;
    rxdsk->rxdsk_number = num;
    spin_lock_init(&rxdsk->rxdsk_lock);
    INIT_RADIX_TREE(&rxdsk->rxdsk_pages, GFP_ATOMIC);

    rxdsk->rxdsk_queue = blk_alloc_queue(GFP_KERNEL);
    if(!rxdsk->rxdsk_queue)
        goto out_free_dev;
    blk_queue_make_request(rxdsk->rxdsk_queue, rxdsk_make_request);
    blk_queue_logical_block_size (rxdsk->rxdsk_queue, BYTES_PER_SECTOR);
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,37)
    blk_queue_flush(rxdsk->rxdsk_queue, REQ_FLUSH);
#else
    blk_queue_ordered(rxdsk->rxdsk_queue, QUEUE_ORDERED_TAG, NULL);
#endif

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,36)
    rxdsk->rxdsk_queue->limits.discard_granularity = PAGE_SIZE;
    rxdsk->rxdsk_queue->limits.discard_zeroes_data = 1;
    rxdsk->rxdsk_queue->limits.max_discard_sectors = UINT_MAX;
    queue_flag_set_unlocked(QUEUE_FLAG_DISCARD, rxdsk->rxdsk_queue);
#endif

    if (!(disk = rxdsk->rxdsk_disk = alloc_disk (1)))
        goto out_free_queue;
    disk->major = rxdsk_ma_no;
    disk->first_minor = num;
    disk->fops = &rxdsk_fops;
    disk->private_data = rxdsk;
    disk->queue = rxdsk->rxdsk_queue;
    disk->flags |= GENHD_FL_SUPPRESS_PARTITION_INFO;
    sprintf(disk->disk_name, "%s%d", DEVICE_NAME, num);
    set_capacity(disk, size);
    rxdsk->max_blk_alloc = 0;

    add_disk(rxdsk->rxdsk_disk);
    list_add_tail(&rxdsk->rxdsk_list, &rxdsk_devices);
    rxcnt++;
    printk(KERN_INFO "%s: Attached rxd%d of %lu bytes in size.\n", RxPREFIX, num,
        (unsigned long)(size * BYTES_PER_SECTOR));

    return 0;

out_free_queue:
    blk_cleanup_queue(rxdsk->rxdsk_queue); 
out_free_dev:
    kfree(rxdsk);
out:
    return -1;
} // attach_device // 


static int
detach_device(int num){
    struct rxdsk_device *rxdsk;

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    list_for_each_entry(rxdsk, &rxdsk_devices, rxdsk_list)
        if(rxdsk->rxdsk_number == num) break;

    list_del(&rxdsk->rxdsk_list);
    del_gendisk(rxdsk->rxdsk_disk);
    put_disk(rxdsk->rxdsk_disk);
    blk_cleanup_queue(rxdsk->rxdsk_queue);
    rxdsk_free_pages(rxdsk);
    kfree(rxdsk);
    rxcnt--;
    printk(KERN_INFO "%s: Detached rxd%d.\n", RxPREFIX, num);

    return 0;
} // detach_device // 


static int
resize_device(int num, int size){
    struct rxdsk_device *rxdsk;

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    list_for_each_entry(rxdsk, &rxdsk_devices, rxdsk_list)
        if(rxdsk->rxdsk_number == num) break;

    if (size <= get_capacity(rxdsk->rxdsk_disk)){
        printk(KERN_WARNING "%s: Please specify a larger size for resizing.\n", RxPREFIX);
        return -1;
    }
    set_capacity(rxdsk->rxdsk_disk, size);
    printk(KERN_INFO "%s: Resized rxd%d of %lu bytes in size.\n", RxPREFIX, num,
        (unsigned long)(size * BYTES_PER_SECTOR));
    return 0;
} // resize_device // 


static int
__init init_rxd (void){

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    rxdsk_ma_no = register_blkdev (rxdsk_ma_no, DEVICE_NAME);
    if (rxdsk_ma_no < 0){
        printk(KERN_ERR "%s: Failed registering rxdsk, returned %d\n", RxPREFIX, rxdsk_ma_no);
        return rxdsk_ma_no;
    }

    if((rx_proc = create_proc_entry (PROC_NODE, S_IRWXU | S_IRWXG | S_IRWXO, NULL)) == NULL){
        printk(KERN_ERR "%s: Bad create_proc_entry\n", RxPREFIX);
        return -1;
    }

    rx_proc->read_proc = read_proc;
    rx_proc->write_proc = write_proc;

    printk(KERN_INFO "%s: Module successfully loaded.\n", RxPREFIX);

    return 0;

} // init_rxd //


static void
__exit exit_rxd (void){
    struct rxdsk_device *rxdsk, *next;

    DPRINTK("%s: debug: entering %s\n", RxPREFIX, __func__);

    remove_proc_entry(PROC_NODE, NULL);

    list_for_each_entry_safe(rxdsk, next, &rxdsk_devices, rxdsk_list)
        detach_device(rxdsk->rxdsk_number);

    unregister_blkdev (rxdsk_ma_no, DEVICE_NAME);
    printk(KERN_INFO "%s: Module successfully unloaded.\n", RxPREFIX);
} // exit_rxd //

module_init(init_rxd);
module_exit(exit_rxd);

MODULE_LICENSE("GPL");
MODULE_AUTHOR(DRIVER_AUTHOR);
MODULE_DESCRIPTION(DRIVER_DESC);
MODULE_VERSION(VERSION_STR);
MODULE_INFO(Copyright, COPYRIGHT);
