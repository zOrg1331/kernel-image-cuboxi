#include <linux/module.h>
#include <linux/bio.h>

#include <linux/ploop/ploop.h>
#include "discard.h"
#include "freeblks.h"

int ploop_discard_init_ioc(struct ploop_device *plo)
{
	struct ploop_freeblks_desc *fbd;
	struct ploop_delta *delta = ploop_top_delta(plo);

	if (delta == NULL)
		return -EINVAL;

	if (plo->maintainance_type != PLOOP_MNTN_OFF)
		return -EBUSY;

	fbd = ploop_fb_init(plo);
	if (!fbd)
		return -ENOMEM;

	ploop_quiesce(plo);

	ploop_fb_set_freezed_level(fbd, delta->level);

	plo->fbd = fbd;

	atomic_set(&plo->maintainance_cnt, 0);
	init_completion(&plo->maintainance_comp);
	plo->maintainance_type = PLOOP_MNTN_DISCARD;
	set_bit(PLOOP_S_DISCARD, &plo->state);

	ploop_relax(plo);

	return 0;
}

int ploop_discard_fini_ioc(struct ploop_device *plo)
{
	int ret = 0;
	struct ploop_request *preq, *tmp;
	LIST_HEAD(drop_list);

	if (!test_and_clear_bit(PLOOP_S_DISCARD, &plo->state))
		return -EINVAL;

	if (plo->maintainance_type != PLOOP_MNTN_DISCARD)
		return -EBUSY;

	ploop_quiesce(plo);

	spin_lock_irq(&plo->lock);
	list_for_each_entry_safe(preq, tmp, &plo->entry_queue, list)
		if (test_bit(PLOOP_REQ_DISCARD, &preq->state)) {
			list_move(&preq->list, &drop_list);
			plo->entry_qlen--;
		}
	spin_unlock_irq(&plo->lock);

	if (!list_empty(&drop_list))
		ploop_preq_drop(plo, &drop_list, 0);

	ploop_fb_fini(plo->fbd, -EOPNOTSUPP);

	clear_bit(PLOOP_S_DISCARD_LOADED, &plo->state);

	plo->maintainance_type = PLOOP_MNTN_OFF;
	complete(&plo->maintainance_comp);

	ploop_relax(plo);

	return ret;
}

int ploop_discard_wait_ioc(struct ploop_device *plo)
{
	int err;

	if (plo->maintainance_type == PLOOP_MNTN_FBLOADED)
		return 0;

	if (plo->maintainance_type != PLOOP_MNTN_DISCARD)
		return -EINVAL;

	err = ploop_maintainance_wait(plo);
	if (err)
		goto out;

	/* maintainance_cnt is zero without discard requests,
	 * in this case ploop_maintainance_wait returns 0
	 * instead of ERESTARTSYS */
	if (signal_pending(current))
		err = -ERESTARTSYS;
out:
	return err;
}
