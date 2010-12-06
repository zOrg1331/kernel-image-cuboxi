#include <linux/slab.h>
#include <linux/dcache.h>
#include <linux/fs.h>
#include <linux/module.h>
#include <linux/sched.h>

#include <bc/beancounter.h>
#include <bc/dcache.h>

static unsigned int dcache_charge_size(int name_len)
{
	return dentry_cache->objuse + inode_cachep->objuse +
		(name_len > DNAME_INLINE_LEN ? name_len : 0);
}

int ub_dcache_charge(struct user_beancounter *ub, int name_len)
{
	int size, shrink;

	size = dcache_charge_size(name_len);
	do {
		if (!charge_beancounter_fast(ub, UB_DCACHESIZE, size, UB_SOFT | UB_TEST))
			return 0;
		shrink = max(size, ub->ub_parms[UB_DCACHESIZE].max_precharge);
		shrink = DIV_ROUND_UP(shrink, dcache_charge_size(0));
	} while (shrink_dcache_ub(ub, shrink));

	spin_lock_irq(&ub->ub_lock);
	ub->ub_parms[UB_DCACHESIZE].failcnt++;
	spin_unlock_irq(&ub->ub_lock);

	return -ENOMEM;
}

void ub_dcache_uncharge(struct user_beancounter *ub, int name_len)
{
	unsigned int size;

	size = dcache_charge_size(name_len);
	uncharge_beancounter_fast(ub, UB_DCACHESIZE, size);
}

static unsigned long recharge_subtree(struct dentry *d, struct user_beancounter *ub,
		struct user_beancounter *cub)
{
	struct dentry *orig_root;
	unsigned long size = 0;

	orig_root = d;

	while (1) {
		BUG_ON(d->d_ub != cub);
		if (!list_empty(&d->d_lru)) {
			list_move(&d->d_bclru, &ub->ub_dentry_lru);
			cub->ub_dentry_unused--;
			ub->ub_dentry_unused++;
		}

		d->d_ub = ub;
		size += dcache_charge_size(d->d_name.len);

		if (!list_empty(&d->d_subdirs)) {
			d = list_entry(d->d_subdirs.next,
					struct dentry, d_u.d_child);
			continue;
		}
		if (d == orig_root)
			break;
		while (d == list_entry(d->d_parent->d_subdirs.prev,
					struct dentry, d_u.d_child)) {
			d = d->d_parent;
			if (d == orig_root)
				goto out;
		}
		d = list_entry(d->d_u.d_child.next,
				struct dentry, d_u.d_child);
	}
out:
	return size;
}

void ub_dcache_set_owner(struct dentry *root, struct user_beancounter *ub)
{
	struct user_beancounter *cub;
	unsigned long size;

	spin_lock(&dcache_lock);

	cub = root->d_ub;
	if (ub != cub) {
		size = recharge_subtree(root, ub, cub);
		uncharge_beancounter_fast(cub, UB_DCACHESIZE, size);
		charge_beancounter_fast(ub, UB_DCACHESIZE, size, UB_FORCE);
	}

	get_beancounter(ub);
	if (root->d_flags & DCACHE_BCTOP) {
		put_beancounter(cub);
	} else {
		spin_lock(&root->d_lock);
		root->d_flags |= DCACHE_BCTOP;
		spin_unlock(&root->d_lock);
	}

	spin_unlock(&dcache_lock);
}
EXPORT_SYMBOL(ub_dcache_set_owner);
