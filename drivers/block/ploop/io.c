#include <linux/fs.h>
#include <linux/file.h>

#include <linux/ploop/ploop.h>
#include <linux/ploop/ploop_if.h>

/* Generic IO routines. */

static LIST_HEAD(ploop_ios);
static DEFINE_MUTEX(ploop_ios_mutex);

int ploop_register_io(struct ploop_io_ops * ops)
{
	mutex_lock(&ploop_ios_mutex);
	list_add(&ops->list, &ploop_ios);
	mutex_unlock(&ploop_ios_mutex);
	return 0;
}
EXPORT_SYMBOL(ploop_register_io);

void ploop_unregister_io(struct ploop_io_ops * ops)
{
	mutex_lock(&ploop_ios_mutex);
	list_del(&ops->list);
	mutex_unlock(&ploop_ios_mutex);
}
EXPORT_SYMBOL(ploop_unregister_io);

struct ploop_io_ops * ploop_io_get(unsigned int id)
{
	struct ploop_io_ops * ops;

	mutex_lock(&ploop_ios_mutex);
	list_for_each_entry(ops, &ploop_ios, list) {
		if (ops->id == id && try_module_get(ops->owner)) {
			mutex_unlock(&ploop_ios_mutex);
			return ops;
		}
	}
	mutex_unlock(&ploop_ios_mutex);
	return NULL;
}

void ploop_io_put(struct ploop_io_ops * ops)
{
	module_put(ops->owner);
}


int
ploop_io_init(struct ploop_delta * delta, int nchunks, struct ploop_ctl_chunk * pc)
{
	int err;
	struct ploop_io_ops * ops;

	if (nchunks != 1)
		return -EINVAL;

	if (pc[0].pctl_offset ||
	    pc[0].pctl_start ||
	    pc[0].pctl_len)
		return -EINVAL;

	ops = ploop_io_get(pc[0].pctl_type);
	if (ops == NULL)
		return -EINVAL;

	memset(&delta->io, 0, sizeof(struct ploop_io));
	delta->io.plo = delta->plo;
	delta->io.n_chunks = 1;
	delta->io.ops = ops;

	err = -EBADF;
	delta->io.files.file = fget(pc[0].pctl_fd);
	if (!delta->io.files.file)
		goto out_err;

	err = ops->init(&delta->io);
	if (err)
		goto out_err;

	return 0;

out_err:
	if (delta->io.files.file)
		fput(delta->io.files.file);
	delta->io.files.file = NULL;
	ploop_io_put(ops);
	delta->io.ops = NULL;
	return err;
}
EXPORT_SYMBOL(ploop_io_init);

int ploop_io_open(struct ploop_io * io)
{
	struct file * file;
	struct ploop_delta * delta = container_of(io, struct ploop_delta, io);

	if ((file = io->files.file) == NULL)
		return -EBADF;

	if ((delta->flags & PLOOP_FMT_RDONLY) &&
	    (io->ops->f_mode(io) & FMODE_WRITE))
		return -EINVAL;

	if (!(delta->flags & PLOOP_FMT_RDONLY) &&
	    !(io->ops->f_mode(io) & FMODE_WRITE))
		return -EINVAL;

	return io->ops->open(io);
}
EXPORT_SYMBOL(ploop_io_open);

void ploop_io_destroy(struct ploop_io * io)
{
	if (io->ops) {
		io->ops->destroy(io);
		ploop_io_put(io->ops);
		io->ops = NULL;
	}
}
EXPORT_SYMBOL(ploop_io_destroy);

