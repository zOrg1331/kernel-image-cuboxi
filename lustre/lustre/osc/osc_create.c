/* -*- mode: c; c-basic-offset: 8; indent-tabs-mode: nil; -*-
 * vim:expandtab:shiftwidth=8:tabstop=8:
 *
 * GPL HEADER START
 *
 * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 only,
 * as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License version 2 for more details (a copy is included
 * in the LICENSE file that accompanied this code).
 *
 * You should have received a copy of the GNU General Public License
 * version 2 along with this program; If not, see
 * http://www.sun.com/software/products/lustre/docs/GPLv2.pdf
 *
 * Please contact Sun Microsystems, Inc., 4150 Network Circle, Santa Clara,
 * CA 95054 USA or visit www.sun.com if you need additional information or
 * have any questions.
 *
 * GPL HEADER END
 */
/*
 * Copyright  2008 Sun Microsystems, Inc. All rights reserved
 * Use is subject to license terms.
 */
/*
 * This file is part of Lustre, http://www.lustre.org/
 * Lustre is a trademark of Sun Microsystems, Inc.
 *
 * lustre/osc/osc_create.c
 * For testing and management it is treated as an obd_device,
 * although * it does not export a full OBD method table (the
 * requests are coming * in over the wire, so object target modules
 * do not have a full * method table.)
 *
 * Author: Peter Braam <braam@clusterfs.com>
 */

#ifndef EXPORT_SYMTAB
# define EXPORT_SYMTAB
#endif
#define DEBUG_SUBSYSTEM S_OSC

#ifdef __KERNEL__
# include <libcfs/libcfs.h>
#else /* __KERNEL__ */
# include <liblustre.h>
#endif

#ifdef  __CYGWIN__
# include <ctype.h>
#endif

# include <lustre_dlm.h>
#include <obd_class.h>
#include "osc_internal.h"

static int osc_interpret_create(struct ptlrpc_request *req, void *data, int rc)
{
        struct osc_creator *oscc;
        struct ost_body *body = NULL;
        ENTRY;

        if (req->rq_repmsg) {
                body = lustre_swab_repbuf(req, REPLY_REC_OFF, sizeof(*body),
                                          lustre_swab_ost_body);
                if (body == NULL && rc == 0)
                        rc = -EPROTO;
        }

        oscc = req->rq_async_args.pointer_arg[0];
        LASSERT(oscc && (oscc->oscc_obd != LP_POISON));

        spin_lock(&oscc->oscc_lock);
        oscc->oscc_flags &= ~OSCC_FLAG_CREATING;
        switch (rc) {
        case 0: {
                if (body) {
                        int diff = body->oa.o_id - oscc->oscc_last_id;

                        /* oscc_internal_create() stores the original value of
                         * grow_count in rq_async_args.space[0].
                         * We can't compare against oscc_grow_count directly,
                         * because it may have been increased while the RPC
                         * is in flight, so we would always find ourselves
                         * having created fewer objects and decreasing the
                         * precreate request size.  b=18577 */
                        if (diff < (int) req->rq_async_args.space[0]) {
                                /* the OST has not managed to create all the
                                 * objects we asked for */
                                oscc->oscc_grow_count = max(diff,
                                                            OST_MIN_PRECREATE);
                                /* don't bump grow_count next time */
                                oscc->oscc_flags |= OSCC_FLAG_LOW;
                        } else {
                                /* the OST is able to keep up with the work,
                                 * we could consider increasing grow_count
                                 * next time if needed */
                                oscc->oscc_flags &= ~OSCC_FLAG_LOW;
                        }
                        oscc->oscc_last_id = body->oa.o_id;
                }
                spin_unlock(&oscc->oscc_lock);
                break;
        }
        case -EAGAIN:
                /* valid race delorphan vs create, or somthing after resend */
                spin_unlock(&oscc->oscc_lock);
                DEBUG_REQ(D_INODE, req, "Got EGAIN - resend \n");
                break;
        case -ENOSPC:
        case -EROFS: 
        case -EFBIG: {
                oscc->oscc_flags |= OSCC_FLAG_NOSPC;
                if (body && rc == -ENOSPC) {
                        oscc->oscc_grow_count = OST_MIN_PRECREATE;
                        oscc->oscc_last_id = body->oa.o_id;
                }
                spin_unlock(&oscc->oscc_lock);
                DEBUG_REQ(D_INODE, req, "OST out of space, flagging");
                break;
        }
        case -EIO: {
                /* filter always set body->oa.o_id as the last_id 
                 * of filter (see filter_handle_precreate for detail)*/
                if (body && body->oa.o_id > oscc->oscc_last_id)
                        oscc->oscc_last_id = body->oa.o_id;
                spin_unlock(&oscc->oscc_lock);
                break;
        }
        default: {
                oscc->oscc_flags |= OSCC_FLAG_RECOVERING;
                oscc->oscc_grow_count = OST_MIN_PRECREATE;
                spin_unlock(&oscc->oscc_lock);
                DEBUG_REQ(D_ERROR, req,
                          "unknown rc %d from async create: failing oscc", rc);
                ptlrpc_fail_import(req->rq_import,
                                   lustre_msg_get_conn_cnt(req->rq_reqmsg));
        }
        }

        CDEBUG(D_RPCTRACE, "prealloc through id "LPU64", next to use "LPU64"\n",
               oscc->oscc_last_id, oscc->oscc_next_id);

        cfs_waitq_signal(&oscc->oscc_waitq);
        RETURN(rc);
}

static int oscc_internal_create(struct osc_creator *oscc)
{
        struct ptlrpc_request *request;
        struct ost_body *body;
        __u32 size[] = { sizeof(struct ptlrpc_body), sizeof(*body) };
        ENTRY;

        LASSERT_SPIN_LOCKED(&oscc->oscc_lock);

        if (oscc->oscc_flags & OSCC_FLAG_CREATING ||
            oscc->oscc_flags & OSCC_FLAG_RECOVERING) {
                spin_unlock(&oscc->oscc_lock);
                RETURN(0);
        }

        if (oscc->oscc_grow_count < oscc->oscc_max_grow_count &&
            ((oscc->oscc_flags & OSCC_FLAG_LOW) == 0) &&
            (__s64)(oscc->oscc_last_id - oscc->oscc_next_id) <=
                   (oscc->oscc_grow_count / 4 + 1)) {
                oscc->oscc_flags |= OSCC_FLAG_LOW;
                oscc->oscc_grow_count *= 2;
        }

        if (oscc->oscc_grow_count > oscc->oscc_max_grow_count / 2)
                oscc->oscc_grow_count = oscc->oscc_max_grow_count / 2;

        oscc->oscc_flags |= OSCC_FLAG_CREATING;
        spin_unlock(&oscc->oscc_lock);

        request = ptlrpc_prep_req(oscc->oscc_obd->u.cli.cl_import,
                                  LUSTRE_OST_VERSION, OST_CREATE, 2,
                                  size, NULL);
        if (request == NULL) {
                spin_lock(&oscc->oscc_lock);
                oscc->oscc_flags &= ~OSCC_FLAG_CREATING;
                spin_unlock(&oscc->oscc_lock);
                RETURN(-ENOMEM);
        }

        request->rq_request_portal = OST_CREATE_PORTAL;
        ptlrpc_at_set_req_timeout(request);
        body = lustre_msg_buf(request->rq_reqmsg, REQ_REC_OFF, sizeof(*body));

        spin_lock(&oscc->oscc_lock);
        body->oa.o_id = oscc->oscc_last_id + oscc->oscc_grow_count;
        body->oa.o_gr = 0;
        body->oa.o_valid |= OBD_MD_FLID | OBD_MD_FLGROUP;
        request->rq_async_args.space[0] = oscc->oscc_grow_count;
        spin_unlock(&oscc->oscc_lock);
        CDEBUG(D_RPCTRACE, "prealloc through id "LPU64" (last seen "LPU64")\n",
               body->oa.o_id, oscc->oscc_last_id);

        ptlrpc_req_set_repsize(request, 2, size);

        request->rq_async_args.pointer_arg[0] = oscc;
        request->rq_interpret_reply = osc_interpret_create;
        ptlrpcd_add_req(request);

        RETURN(0);
}

static int oscc_has_objects(struct osc_creator *oscc, int count)
{
        int have_objs;
        spin_lock(&oscc->oscc_lock);
        have_objs = ((__s64)(oscc->oscc_last_id - oscc->oscc_next_id) >= count);

        if (!have_objs) {
                oscc_internal_create(oscc);
        } else {
                spin_unlock(&oscc->oscc_lock);
        }

        return have_objs;
}

static int oscc_wait_for_objects(struct osc_creator *oscc, int count)
{
        int have_objs;
        int ost_full;
        int osc_invalid;

        have_objs = oscc_has_objects(oscc, count);

        spin_lock(&oscc->oscc_lock);
        ost_full = (oscc->oscc_flags & OSCC_FLAG_NOSPC);
        spin_unlock(&oscc->oscc_lock);

        osc_invalid = oscc->oscc_obd->u.cli.cl_import->imp_invalid;

        return have_objs || ost_full || osc_invalid;
}

static int oscc_precreate(struct osc_creator *oscc, int wait)
{
        struct l_wait_info lwi = { 0 };
        int rc = 0;
        ENTRY;

        if (oscc_has_objects(oscc, oscc->oscc_grow_count / 2))
                RETURN(0);

        if (!wait)
                RETURN(0);

        /* no rc check -- a no-INTR, no-TIMEOUT wait can't fail */
        l_wait_event(oscc->oscc_waitq, oscc_wait_for_objects(oscc, 1), &lwi);

        if (!oscc_has_objects(oscc, 1) && (oscc->oscc_flags & OSCC_FLAG_NOSPC))
                rc = -ENOSPC;

        if (oscc->oscc_obd->u.cli.cl_import->imp_invalid)
                rc = -EIO;

        RETURN(rc);
}

int oscc_recovering(struct osc_creator *oscc)
{
        int recov = 0;

        spin_lock(&oscc->oscc_lock);
        recov = oscc->oscc_flags & OSCC_FLAG_RECOVERING;
        spin_unlock(&oscc->oscc_lock);

        return recov;
}

/* decide if the OST has remaining object, return value :
        0 : the OST has remaining object, and don't need to do precreate.
        1 : the OST has no remaining object, and will send a RPC for precreate.
        2 : the OST has no remaining object, and will not get any for
            a potentially very long time
     1000 : unusable
 */
int osc_precreate(struct obd_export *exp)
{
        struct osc_creator *oscc = &exp->exp_obd->u.cli.cl_oscc;
        struct obd_import *imp = exp->exp_imp_reverse;
        ENTRY;

        LASSERT(oscc != NULL);
        if (imp != NULL && imp->imp_deactive)
                RETURN(1000);

        if (oscc_recovering(oscc))
                RETURN(2);

        if (oscc->oscc_flags & OSCC_FLAG_NOSPC)
                RETURN(1000);

        if (oscc->oscc_last_id < oscc->oscc_next_id) {
                if (oscc->oscc_flags & OSCC_FLAG_SYNC_IN_PROGRESS)
                        RETURN(1);

                spin_lock(&oscc->oscc_lock);
                if (oscc->oscc_flags & OSCC_FLAG_CREATING) {
                        spin_unlock(&oscc->oscc_lock);
                        RETURN(1);
                }

                oscc_internal_create(oscc);
                RETURN(1);
        }
        RETURN(0);
}

int osc_create(struct obd_export *exp, struct obdo *oa,
               struct lov_stripe_md **ea, struct obd_trans_info *oti)
{
        struct lov_stripe_md *lsm;
        struct osc_creator *oscc = &exp->exp_obd->u.cli.cl_oscc;
        struct obd_import  *imp  = exp->exp_obd->u.cli.cl_import;
        int try_again = 1, rc = 0;
        ENTRY;
        LASSERT(oa);
        LASSERT(ea);

        if ((oa->o_valid & OBD_MD_FLGROUP) && (oa->o_gr != 0))
                RETURN(osc_real_create(exp, oa, ea, oti));

        if ((oa->o_valid & OBD_MD_FLFLAGS) &&
            oa->o_flags == OBD_FL_RECREATE_OBJS) {
                RETURN(osc_real_create(exp, oa, ea, oti));
        }

        /* this is the special case where create removes orphans */
        if ((oa->o_valid & OBD_MD_FLFLAGS) &&
            oa->o_flags == OBD_FL_DELORPHAN) {
                spin_lock(&oscc->oscc_lock);
                if (oscc->oscc_flags & OSCC_FLAG_SYNC_IN_PROGRESS) {
                        spin_unlock(&oscc->oscc_lock);
                        RETURN(-EBUSY);
                }
                if (!(oscc->oscc_flags & OSCC_FLAG_RECOVERING)) {
                        spin_unlock(&oscc->oscc_lock);
                        RETURN(0);
                }
                oscc->oscc_flags |= OSCC_FLAG_SYNC_IN_PROGRESS;
                /* seting flag LOW we prevent extra grow precreate size
                 * and enforce use last assigned size */
                oscc->oscc_flags |= OSCC_FLAG_LOW;
                spin_unlock(&oscc->oscc_lock);
                CDEBUG(D_HA, "%s: oscc recovery started - delete to "LPU64"\n",
                       oscc->oscc_obd->obd_name, oscc->oscc_next_id - 1);

                /* delete from next_id on up */
                oa->o_valid |= OBD_MD_FLID | OBD_MD_FLGROUP;
                oa->o_id = oscc->oscc_next_id - 1;
                oa->o_gr = 0;

                rc = osc_real_create(exp, oa, ea, NULL);

                spin_lock(&oscc->oscc_lock);
                oscc->oscc_flags &= ~OSCC_FLAG_SYNC_IN_PROGRESS;
                if (rc == 0 || rc == -ENOSPC) {
                        struct obd_connect_data *ocd;

                        if (rc == -ENOSPC)
                                oscc->oscc_flags |= OSCC_FLAG_NOSPC;
                        oscc->oscc_flags &= ~OSCC_FLAG_RECOVERING;
                        oscc->oscc_last_id = oa->o_id;
                        ocd = &imp->imp_connect_data;
                        if (ocd->ocd_connect_flags & OBD_CONNECT_SKIP_ORPHAN) {
                                CDEBUG(D_HA, "%s: Skip orphan set, reset last "
                                       "objid\n", oscc->oscc_obd->obd_name);
                                oscc->oscc_next_id = oa->o_id + 1;
                        }

                        CDEBUG(D_HA, "%s: oscc recovery finished, last_id: "
                               LPU64", rc: %d\n", oscc->oscc_obd->obd_name,
                               oscc->oscc_last_id, rc);
                        cfs_waitq_signal(&oscc->oscc_waitq);
                } else {
                        CDEBUG(D_ERROR, "%s: oscc recovery failed: %d\n",
                               oscc->oscc_obd->obd_name, rc);
                }
                spin_unlock(&oscc->oscc_lock);


                RETURN(rc);
        }

        lsm = *ea;
        if (lsm == NULL) {
                rc = obd_alloc_memmd(exp, &lsm);
                if (rc < 0)
                        RETURN(rc);
        }

        while (try_again) {
                /* If orphans are being recovered, then we must wait until
                   it is finished before we can continue with create. */
                if (oscc_recovering(oscc)) {
                        struct l_wait_info lwi;

                        CDEBUG(D_HA,"%s: oscc recovery in progress, waiting\n",
                               oscc->oscc_obd->obd_name);

                        lwi = LWI_TIMEOUT(cfs_timeout_cap(cfs_time_seconds(
                                obd_timeout / 4)), NULL, NULL);
                        rc = l_wait_event(oscc->oscc_waitq,
                                          !oscc_recovering(oscc), &lwi);
                        LASSERT(rc == 0 || rc == -ETIMEDOUT);
                        if (rc == -ETIMEDOUT) {
                                CDEBUG(D_HA,"%s: timeout waiting on recovery\n",
                                       oscc->oscc_obd->obd_name);
                                RETURN(rc);
                        }
                        CDEBUG(D_HA, "%s: oscc recovery over, waking up\n",
                               oscc->oscc_obd->obd_name);
                }

                spin_lock(&oscc->oscc_lock);
                if (oscc->oscc_flags & OSCC_FLAG_EXITING) {
                        spin_unlock(&oscc->oscc_lock);
                        break;
                }

                if (oscc->oscc_last_id >= oscc->oscc_next_id) {
                        memcpy(oa, &oscc->oscc_oa, sizeof(*oa));
                        oa->o_id = oscc->oscc_next_id;
                        lsm->lsm_object_id = oscc->oscc_next_id;
                        *ea = lsm;
                        oscc->oscc_next_id++;
                        try_again = 0;

                        CDEBUG(D_RPCTRACE, "%s: set oscc_next_id = "LPU64"\n",
                               exp->exp_obd->obd_name, oscc->oscc_next_id);
                } else if (oscc->oscc_flags & OSCC_FLAG_NOSPC) {
                        rc = -ENOSPC;
                        spin_unlock(&oscc->oscc_lock);
                        break;
                }
                spin_unlock(&oscc->oscc_lock);
                rc = oscc_precreate(oscc, try_again);
                if (rc)
                        break;
        }

        if (rc == 0)
                CDEBUG(D_INFO, "%s: returning objid "LPU64"\n",
                       obd2cli_tgt(oscc->oscc_obd), lsm->lsm_object_id);
        else if (*ea == NULL)
                obd_free_memmd(exp, &lsm);
        RETURN(rc);
}

void oscc_init(struct obd_device *obd)
{
        struct osc_creator *oscc;

        if (obd == NULL)
                return;

        oscc = &obd->u.cli.cl_oscc;

        memset(oscc, 0, sizeof(*oscc));
        CFS_INIT_LIST_HEAD(&oscc->oscc_list);
        cfs_waitq_init(&oscc->oscc_waitq);
        spin_lock_init(&oscc->oscc_lock);
        oscc->oscc_obd = obd;
        oscc->oscc_grow_count = OST_MIN_PRECREATE;
        oscc->oscc_max_grow_count = OST_MAX_PRECREATE;

        oscc->oscc_next_id = 2;
        oscc->oscc_last_id = 1;
        oscc->oscc_flags |= OSCC_FLAG_RECOVERING;
        /* XXX the export handle should give the oscc the last object */
        /* oed->oed_oscc.oscc_last_id = exph->....; */
}
