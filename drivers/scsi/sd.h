#ifndef _SCSI_DISK_H
#define _SCSI_DISK_H

/*
 * More than enough for everybody ;)  The huge number of majors
 * is a leftover from 16bit dev_t days, we don't really need that
 * much numberspace.
 */
#define SD_MAJORS	16

/*
 * This is limited by the naming scheme enforced in sd_probe,
 * add another character to it if you really need more disks.
 */
#define SD_MAX_DISKS	(((26 * 26) + 26 + 1) * 26)

/*
 * Time out in seconds for disks and Magneto-opticals (which are slower).
 */
#define SD_TIMEOUT		(30 * HZ)
#define SD_MOD_TIMEOUT		(75 * HZ)

/*
 * Number of allowed retries
 */
#define SD_MAX_RETRIES		5
#define SD_PASSTHROUGH_RETRIES	1

/*
 * Size of the initial data buffer for mode and read capacity data
 */
#define SD_BUF_SIZE		512

/*
 * Number of sectors at the end of the device to avoid multi-sector
 * accesses to in the case of last_sector_bug
 */
#define SD_LAST_BUGGY_SECTORS	8

#if (defined(CONFIG_SD_IOSTATS) && defined(CONFIG_PROC_FS))
typedef struct {
	unsigned long long iostat_size;
	unsigned long long iostat_count;
} iostat_counter_t;

#define IOSTAT_NCOUNTERS 16
typedef struct {
	iostat_counter_t	iostat_read_histogram[IOSTAT_NCOUNTERS];
	iostat_counter_t	iostat_write_histogram[IOSTAT_NCOUNTERS];
	struct timeval		iostat_timeval;

	/* queue depth: how well the pipe is filled up */
	unsigned long long	iostat_queue_ticks[IOSTAT_NCOUNTERS];
	unsigned long long	iostat_queue_ticks_sum;
	unsigned long		iostat_queue_depth;
	unsigned long		iostat_queue_stamp;

	/* seeks: how linear the traffic is */
	unsigned long long	iostat_next_sector;
	unsigned long long	iostat_seek_sectors;
	unsigned long long	iostat_seeks;
	unsigned long long	iostat_sectors;
	unsigned long long	iostat_reqs;
	unsigned long		iostat_read_reqs;
	unsigned long		iostat_write_reqs;

	/* process time: how long it takes to process requests */
	unsigned long		iostat_rtime[IOSTAT_NCOUNTERS];
	unsigned long		iostat_wtime[IOSTAT_NCOUNTERS];

	/* queue time: how long process spent in elevator's queue */
	unsigned long		iostat_rtime_in_queue[IOSTAT_NCOUNTERS];
	unsigned long		iostat_wtime_in_queue[IOSTAT_NCOUNTERS];

	/* must be the last field, as it's used to know size to be memset'ed */
	spinlock_t		iostat_lock;
} ____cacheline_aligned_in_smp iostat_stats_t;
#endif

struct scsi_disk {
	struct scsi_driver *driver;	/* always &sd_template */
	struct scsi_device *device;
	struct device	dev;
	struct gendisk	*disk;
	unsigned int	openers;	/* protected by BKL for now, yuck */
	sector_t	capacity;	/* size in 512-byte sectors */
	u32		index;
	u8		media_present;
	u8		write_prot;
	u8		protection_type;/* Data Integrity Field */
	unsigned	previous_state : 1;
	unsigned	ATO : 1;	/* state of disk ATO bit */
	unsigned	WCE : 1;	/* state of disk WCE bit */
	unsigned	RCD : 1;	/* state of disk RCD bit, unused */
	unsigned	DPOFUA : 1;	/* state of disk DPOFUA bit */
#if (defined(CONFIG_SD_IOSTATS) && defined(CONFIG_PROC_FS))
	iostat_stats_t	*stats;		/* scsi disk statistics */
#endif
};
#define to_scsi_disk(obj) container_of(obj,struct scsi_disk,dev)

static inline struct scsi_disk *scsi_disk(struct gendisk *disk)
{
	return container_of(disk->private_data, struct scsi_disk, driver);
}

#define sd_printk(prefix, sdsk, fmt, a...)				\
        (sdsk)->disk ?							\
	sdev_printk(prefix, (sdsk)->device, "[%s] " fmt,		\
		    (sdsk)->disk->disk_name, ##a) :			\
	sdev_printk(prefix, (sdsk)->device, fmt, ##a)

/*
 * A DIF-capable target device can be formatted with different
 * protection schemes.  Currently 0 through 3 are defined:
 *
 * Type 0 is regular (unprotected) I/O
 *
 * Type 1 defines the contents of the guard and reference tags
 *
 * Type 2 defines the contents of the guard and reference tags and
 * uses 32-byte commands to seed the latter
 *
 * Type 3 defines the contents of the guard tag only
 */

enum sd_dif_target_protection_types {
	SD_DIF_TYPE0_PROTECTION = 0x0,
	SD_DIF_TYPE1_PROTECTION = 0x1,
	SD_DIF_TYPE2_PROTECTION = 0x2,
	SD_DIF_TYPE3_PROTECTION = 0x3,
};

/*
 * Data Integrity Field tuple.
 */
struct sd_dif_tuple {
       __be16 guard_tag;	/* Checksum */
       __be16 app_tag;		/* Opaque storage */
       __be32 ref_tag;		/* Target LBA or indirect LBA */
};

#if defined(CONFIG_BLK_DEV_INTEGRITY)

extern void sd_dif_op(struct scsi_cmnd *, unsigned int, unsigned int);
extern void sd_dif_config_host(struct scsi_disk *);
extern int sd_dif_prepare(struct request *rq, sector_t, unsigned int);
extern void sd_dif_complete(struct scsi_cmnd *, unsigned int);

#else /* CONFIG_BLK_DEV_INTEGRITY */

#define sd_dif_op(a, b, c)			do { } while (0)
#define sd_dif_config_host(a)			do { } while (0)
#define sd_dif_prepare(a, b, c)			(0)
#define sd_dif_complete(a, b)			(0)

#endif /* CONFIG_BLK_DEV_INTEGRITY */

#endif /* _SCSI_DISK_H */
