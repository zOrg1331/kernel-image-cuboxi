#include <linux/errno.h>
#include <linux/sched.h>
#include <linux/kernel.h>
#include <linux/file.h>
#include <linux/pagemap.h>
#include <linux/kthread.h>

#include <linux/ploop/ploop.h>

static void kaio_queue_fsync_req(struct ploop_request * preq)
{
	struct ploop_device * plo   = preq->plo;
	struct ploop_delta  * delta = ploop_top_delta(plo);
	struct ploop_io     * io    = &delta->io;

	list_add_tail(&preq->list, &io->fsync_queue);
	io->fsync_qlen++;
	if (waitqueue_active(&io->fsync_waitq))
		wake_up_interruptible(&io->fsync_waitq);
}

static void kaio_complete_io_state(struct ploop_request * preq)
{
	struct ploop_device * plo   = preq->plo;
	unsigned long flags;

	if (preq->error || !(preq->req_rw & BIO_FUA)) {
		ploop_complete_io_state(preq);
		return;
	}

	preq->req_rw &= ~BIO_FUA;

	spin_lock_irqsave(&plo->lock, flags);
	kaio_queue_fsync_req(preq);
	plo->st.bio_syncwait++;
	spin_unlock_irqrestore(&plo->lock, flags);
}

static void kaio_complete_io_request(struct ploop_request * preq)
{
	if (atomic_dec_and_test(&preq->io_count))
		kaio_complete_io_state(preq);
}

static void kaio_rw_aio_complete(u64 data, long res)
{
	struct ploop_request * preq = (struct ploop_request *)data;

	if (unlikely(res < 0))
		ploop_set_error(preq, res);

	kaio_complete_io_request(preq);
}

static int kaio_kernel_submit(struct file *file, struct bio *bio, struct ploop_request * preq)
{
	struct kiocb *iocb;
	unsigned short op;
	struct iov_iter iter;
	struct bio_vec *bvec;
	size_t nr_segs;
	loff_t pos = (loff_t) bio->bi_sector << 9;

	iocb = aio_kernel_alloc(GFP_NOIO);
	if (!iocb)
		return -ENOMEM;

	if (bio_rw(bio) & WRITE)
		op = IOCB_CMD_WRITE_ITER;
	else
		op = IOCB_CMD_READ_ITER;

	bvec = bio_iovec_idx(bio, bio->bi_idx);
	nr_segs = bio_segments(bio);
	iov_iter_init_bvec(&iter, bvec, nr_segs, bvec_length(bvec, nr_segs), 0);
	aio_kernel_init_iter(iocb, file, op, &iter, pos);
	aio_kernel_init_callback(iocb, kaio_rw_aio_complete, (u64)preq);

	return aio_kernel_submit(iocb);
}

static void
kaio_submit(struct ploop_io *io, struct ploop_request * preq,
	     unsigned long rw,
	     struct bio_list *sbl, iblock_t iblk, unsigned int size)
{

	struct bio * b;

	if (rw & BIO_FLUSH) {
		spin_lock_irq(&io->plo->lock);
		kaio_queue_fsync_req(preq);
		io->plo->st.bio_syncwait++;
		spin_unlock_irq(&io->plo->lock);
		return;
	}

	ploop_prepare_io_request(preq);

	for (b = sbl->head; b != NULL; b = b->bi_next) {
		int err;

		atomic_inc(&preq->io_count);
		err = kaio_kernel_submit(io->files.file, b, preq);
		if (err) {
			ploop_set_error(preq, err);
			ploop_complete_io_request(preq);
			break;
		}
	}

	kaio_complete_io_request(preq);
}

static void kaio_resubmit(struct ploop_request * preq)
{
	struct ploop_delta * delta = ploop_top_delta(preq->plo);

	switch (preq->eng_state) {
	case PLOOP_E_INDEX_WB:
	case PLOOP_E_DATA_WBI:
		printk("Resubmit: state %lu is not supported yet!\n",
		       preq->eng_state);
		BUG();
		break;
	case PLOOP_E_COMPLETE:
	case PLOOP_E_RELOC_NULLIFY:
		if (preq->aux_bio) {
			struct bio_list tbl;
			tbl.head = tbl.tail = preq->aux_bio;
			kaio_submit(&delta->io, preq, preq->req_rw, &tbl,
				    preq->iblock, 1<<preq->plo->cluster_log);
		} else {
			kaio_submit(&delta->io, preq, preq->req_rw, &preq->bl,
				    preq->iblock, preq->req_size);
		}
		break;
	default:
		printk("Resubmit bad state %lu\n", preq->eng_state);
		BUG();
	}
}

static int kaio_fsync_thread(void * data)
{
	struct ploop_io * io = data;
	struct ploop_device * plo = io->plo;
	struct file *file = io->files.file;

	set_user_nice(current, -20);

	spin_lock_irq(&plo->lock);
	while (!kthread_should_stop() || !list_empty(&io->fsync_queue)) {
		int err;
		struct ploop_request * preq;

		DEFINE_WAIT(_wait);
		for (;;) {
			prepare_to_wait(&io->fsync_waitq, &_wait, TASK_INTERRUPTIBLE);
			if (!list_empty(&io->fsync_queue) ||
			    kthread_should_stop())
				break;

			spin_unlock_irq(&plo->lock);
			schedule();
			spin_lock_irq(&plo->lock);
		}
		finish_wait(&io->fsync_waitq, &_wait);

		if (list_empty(&io->fsync_queue) && kthread_should_stop())
			break;

		preq = list_entry(io->fsync_queue.next, struct ploop_request, list);
		list_del(&preq->list);
		io->fsync_qlen--;
		plo->st.bio_fsync++;
		spin_unlock_irq(&plo->lock);

		err = vfs_fsync(file, file->f_path.dentry, 1);
		if (err) {
			ploop_set_error(preq, -EIO);
		} else if (preq->req_rw & BIO_FLUSH) {
			BUG_ON(!preq->req_size);
			preq->req_rw &= ~BIO_FLUSH;
			kaio_resubmit(preq);
			spin_lock_irq(&plo->lock);
			continue;
		}

		spin_lock_irq(&plo->lock);
		list_add_tail(&preq->list, &plo->ready_queue);

		if (test_bit(PLOOP_S_WAIT_PROCESS, &plo->state))
			wake_up_interruptible(&plo->waitq);
	}
	spin_unlock_irq(&plo->lock);
	return 0;
}

static void
kaio_submit_alloc(struct ploop_io *io, struct ploop_request * preq,
		 struct bio_list * sbl, unsigned int size)
{
	printk("kaio_submit_alloc: UNSUPPORTED !\n");
	ploop_fail_request(preq, -EINVAL);
}

static void
kaio_destroy(struct ploop_io * io)
{
	if (io->files.file) {
		struct file * file;
		struct ploop_delta * delta = container_of(io, struct ploop_delta, io);

		if (io->fsync_thread) {
			kthread_stop(io->fsync_thread);
			io->fsync_thread = NULL;
		}

		file = io->files.file;
		mutex_lock(&delta->plo->sysfs_mutex);
		io->files.file = NULL;
		mutex_unlock(&delta->plo->sysfs_mutex);
		fput(file);
	}
}

static int
kaio_sync(struct ploop_io * io)
{
	struct file *file = io->files.file;

	return vfs_fsync(file, file->f_path.dentry, 0);
}

static int
kaio_stop(struct ploop_io * io)
{
	return 0;
}

static int
kaio_init(struct ploop_io * io)
{
	INIT_LIST_HEAD(&io->fsync_queue);
	init_waitqueue_head(&io->fsync_waitq);

	return 0;
}

static void
kaio_read_page(struct ploop_io * io, struct ploop_request * preq,
		struct page * page, sector_t sec)
{
	printk("kaio_read_page: UNSUPPORTED !\n");
	ploop_fail_request(preq, -EINVAL);
}

static void
kaio_write_page(struct ploop_io * io, struct ploop_request * preq,
		 struct page * page, sector_t sec, int fua)
{
	printk("kaio_write_page: UNSUPPORTED !\n");
	ploop_fail_request(preq, -EINVAL);
}

static int
kaio_sync_readvec(struct ploop_io * io, struct page ** pvec, unsigned int nr,
		   sector_t sec)
{
	return -EINVAL;
}

static int
kaio_sync_writevec(struct ploop_io * io, struct page ** pvec, unsigned int nr,
		    sector_t sec)
{
	return -EINVAL;
}

static int
kaio_sync_read(struct ploop_io * io, struct page * page, unsigned int len,
		unsigned int off, sector_t sec)
{
	printk("kaio_sync_read: UNSUPPORTED !\n");
	return -EINVAL;
}

static int
kaio_sync_write(struct ploop_io * io, struct page * page, unsigned int len,
		 unsigned int off, sector_t sec)
{
	printk("kaio_sync_write: UNSUPPORTED !\n");
	return -EINVAL;
}

static int kaio_alloc_sync(struct ploop_io * io, loff_t pos, loff_t len)
{
	printk("kaio_alloc_sync: UNSUPPORTED !\n");
	return -EINVAL;
}

static int kaio_open(struct ploop_io * io)
{
	struct file * file = io->files.file;
	struct ploop_delta * delta = container_of(io, struct ploop_delta, io);

	if (file == NULL)
		return -EBADF;

	io->files.mapping = file->f_mapping;
	io->files.inode = io->files.mapping->host;
	io->files.bdev = io->files.inode->i_sb->s_bdev;

	if (!(delta->flags & PLOOP_FMT_RDONLY)) {
		io->fsync_thread = kthread_create(kaio_fsync_thread,
						  io, "ploop_fsync%d",
						  delta->plo->index);
		if (io->fsync_thread == NULL)
			return -ENOMEM;

		wake_up_process(io->fsync_thread);
	}

	return 0;
}

static int kaio_prepare_snapshot(struct ploop_io * io, struct ploop_snapdata *sd)
{
	printk("kaio_prepare_snapshot: UNSUPPORTED !\n");
	return -EINVAL;
}

static int kaio_complete_snapshot(struct ploop_io * io, struct ploop_snapdata *sd)
{
	printk("kaio_complete_snapshot: UNSUPPORTED !\n");
	return -EINVAL;
}

static int kaio_prepare_merge(struct ploop_io * io, struct ploop_snapdata *sd)
{
	printk("kaio_prepare_merge: UNSUPPORTED !\n");
	return -EINVAL;
}

static int kaio_start_merge(struct ploop_io * io, struct ploop_snapdata *sd)
{
	printk("kaio_start_merge: UNSUPPORTED !\n");
	return -EINVAL;
}

static int kaio_truncate(struct ploop_io * io, struct file * file,
			  __u32 alloc_head)
{
	printk("kaio_truncate: UNSUPPORTED !\n");
	return -EINVAL;
}

static void kaio_unplug(struct ploop_io * io)
{
	blk_run_address_space(io->files.file->f_mapping);
}

static void kaio_issue_flush(struct ploop_io * io, struct ploop_request *preq)
{
	preq->eng_state = PLOOP_E_COMPLETE;
	preq->req_rw &= ~BIO_FLUSH;

	spin_lock_irq(&io->plo->lock);
	kaio_queue_fsync_req(preq);
	spin_unlock_irq(&io->plo->lock);
}

static struct ploop_io_ops ploop_io_ops_kaio =
{
	.id		=	PLOOP_IO_KAIO,
	.name		=	"kaio",
	.owner		=	THIS_MODULE,

	.unplug		=	kaio_unplug,

	.alloc		=	kaio_alloc_sync,
	.submit		=	kaio_submit,
	.submit_alloc	=	kaio_submit_alloc,
	.read_page	=	kaio_read_page,
	.write_page	=	kaio_write_page,
	.sync_read	=	kaio_sync_read,
	.sync_write	=	kaio_sync_write,
	.sync_readvec	=	kaio_sync_readvec,
	.sync_writevec	=	kaio_sync_writevec,

	.init		=	kaio_init,
	.destroy	=	kaio_destroy,
	.open		=	kaio_open,
	.sync		=	kaio_sync,
	.stop		=	kaio_stop,
	.prepare_snapshot =	kaio_prepare_snapshot,
	.complete_snapshot =	kaio_complete_snapshot,
	.prepare_merge	=	kaio_prepare_merge,
	.start_merge	=	kaio_start_merge,
	.truncate	=	kaio_truncate,

	.issue_flush	=	kaio_issue_flush,

	.i_size_read	=	generic_i_size_read,
	.f_mode		=	generic_f_mode,
};

static int __init pio_kaio_mod_init(void)
{
	return ploop_register_io(&ploop_io_ops_kaio);
}

static void __exit pio_kaio_mod_exit(void)
{
	ploop_unregister_io(&ploop_io_ops_kaio);
}

module_init(pio_kaio_mod_init);
module_exit(pio_kaio_mod_exit);

MODULE_LICENSE("GPL");
