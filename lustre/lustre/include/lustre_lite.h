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
 */

#ifndef _LL_H
#define _LL_H

#if defined(__linux__)
#include <linux/lustre_lite.h>
#elif defined(__APPLE__)
#include <darwin/lustre_lite.h>
#elif defined(__WINNT__)
#include <winnt/lustre_lite.h>
#else
#error Unsupported operating system.
#endif

#include <obd_class.h>
#include <obd_ost.h>
#include <lustre_net.h>
#include <lustre_mds.h>
#include <lustre_ha.h>

#ifdef __KERNEL__

/* careful, this is easy to screw up */
#define PAGE_CACHE_MAXBYTES ((__u64)(~0UL) << CFS_PAGE_SHIFT)

#endif

#define LLAP_FROM_COOKIE(c)                                                    \
        (LASSERT(((struct ll_async_page *)(c))->llap_magic == LLAP_MAGIC),     \
         (struct ll_async_page *)(c))

// 4*1024*1024
#define LL_MAX_BLKSIZE_BITS     (22)
#define LL_MAX_BLKSIZE          (1UL<<LL_MAX_BLKSIZE_BITS)

#include <lustre/lustre_user.h>


struct lustre_rw_params {
        int                lrp_lock_mode;
        ldlm_policy_data_t lrp_policy;
        obd_flag           lrp_brw_flags;
        int                lrp_ast_flags;
};

/*
 * XXX nikita: this function lives in the header because it is used by both
 * llite kernel module and liblustre library, and there is no (?) better place
 * to put it in.
 */
static inline void lustre_build_lock_params(int cmd, unsigned long open_flags,
                                            __u64 connect_flags,
                                            loff_t pos, ssize_t len,
                                            struct lustre_rw_params *params)
{
        params->lrp_lock_mode = (cmd == OBD_BRW_READ) ? LCK_PR : LCK_PW;
        params->lrp_brw_flags = 0;

        params->lrp_policy.l_extent.start = pos;
        params->lrp_policy.l_extent.end = pos + len - 1;
        /*
         * for now O_APPEND always takes local locks.
         */
        if (cmd == OBD_BRW_WRITE && (open_flags & O_APPEND)) {
                params->lrp_policy.l_extent.start = 0;
                params->lrp_policy.l_extent.end   = OBD_OBJECT_EOF;
        } else if (LIBLUSTRE_CLIENT && (connect_flags & OBD_CONNECT_SRVLOCK)) {
                /*
                 * liblustre: OST-side locking for all non-O_APPEND
                 * reads/writes.
                 */
                params->lrp_lock_mode = LCK_NL;
                params->lrp_brw_flags = OBD_BRW_SRVLOCK;
        } else {
                /*
                 * nothing special for the kernel. In the future llite may use
                 * OST-side locks for small writes into highly contended
                 * files.
                 */
        }
        params->lrp_ast_flags = (open_flags & O_NONBLOCK) ?
                LDLM_FL_BLOCK_NOWAIT : 0;
}

/*
 * This is embedded into liblustre and llite super-blocks to keep track of
 * connect flags (capabilities) supported by all imports given mount is
 * connected to.
 */
struct lustre_client_ocd {
        /*
         * This is conjunction of connect_flags across all imports (LOVs) this
         * mount is connected to. This field is updated by ll_ocd_update()
         * under ->lco_lock.
         */
        __u64      lco_flags;
        struct semaphore   lco_lock;
        struct obd_export *lco_mdc_exp;
        struct obd_export *lco_osc_exp;
};

/*
 * This function is used as an upcall-callback hooked by liblustre and llite
 * clients into obd_notify() listeners chain to handle notifications about
 * change of import connect_flags. See llu_fsswop_mount() and
 * lustre_common_fill_super().
 *
 * Again, it is dumped into this header for the lack of a better place.
 */
static inline int ll_ocd_update(struct obd_device *host,
                                struct obd_device *watched,
                                enum obd_notify_event ev, void *owner)
{
        struct lustre_client_ocd *lco;
        struct client_obd        *cli;
        __u64 flags;
        int   result;

        ENTRY;
        if (!strcmp(watched->obd_type->typ_name, LUSTRE_OSC_NAME)) {
                cli = &watched->u.cli;
                lco = owner;
                flags = cli->cl_import->imp_connect_data.ocd_connect_flags;
                CDEBUG(D_SUPER, "Changing connect_flags: "LPX64" -> "LPX64"\n",
                       lco->lco_flags, flags);
                mutex_down(&lco->lco_lock);
                lco->lco_flags &= flags;
                /* for each osc event update ea size */
                if (lco->lco_osc_exp)
                        mdc_init_ea_size(lco->lco_mdc_exp, lco->lco_osc_exp);
                mutex_up(&lco->lco_lock);

                result = 0;
        } else {
                CERROR("unexpected notification from %s %s!\n",
                       watched->obd_type->typ_name,
                       watched->obd_name);
                result = -EINVAL;
        }
        RETURN(result);
}

#endif
