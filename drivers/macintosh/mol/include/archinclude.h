/*
 *   Creation Date: <2002/01/12 22:11:51 samuel>
 *   Time-stamp: <2004/04/10 22:27:41 samuel>
 *
 *	<archinclude.h>
 *
 *
 *
 *   Copyright (C) 2002, 2003, 2004 Samuel Rydh (samuel@ibrium.se)
 *
 *   This program is free software; you can redistribute it and/or
 *   modify it under the terms of the GNU General Public License
 *   as published by the Free Software Foundation
 *
 */

#ifndef _H_ARCHINCLUDE
#define _H_ARCHINCLUDE

//#define PERF_MONITOR
//#define PERFORMANCE_INFO	     	/* collect performance statistics */
//#define PERFORMANCE_INFO_LIGHT	/* sample only the most important counters */

#include "mol_config.h"
#include "kconfig.h"

#include <linux/version.h>

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,18)
#include <linux/utsrelease.h>
#endif

#if LINUX_VERSION_CODE <= KERNEL_VERSION(2,6,18)
#include <linux/config.h>
#else
#include <linux/autoconf.h>
#endif

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,0)
#define LINUX_26
#endif

#ifndef __ASSEMBLY__
#include <linux/kernel.h>
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,26)
#include <linux/semaphore.h>
#endif
#include <asm/atomic.h>
#include <linux/sched.h>	/* needed by <asm/mmu_context.h> */
#include <asm/mmu_context.h>
#include <asm/time.h>

#include "dbg.h"

/* these are declared, but we just want to be sure the definition does not change */
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,0)
extern int flush_hash_pages( unsigned context, unsigned long va, unsigned long pmdval, int count ); /* 2.6 */
#else
extern int flush_hash_page( unsigned context, unsigned long va, pte_t *ptep ); /* 2.5 */
#endif /* Linux 2.6 */

#endif /* __ASSEMBLY__ */

#ifdef LINUX_26
#define compat_flush_hash_pages		flush_hash_pages
#define compat_hash_table_lock		mmu_hash_lock
#else
#define compat_flush_hash_pages		flush_hash_page
#define compat_hash_table_lock		hash_table_lock
#endif


#define	ENOSYS_MOL			ENOSYS
#define EFAULT_MOL			EFAULT

#define IS_LINUX			1
#define IS_DARWIN			0


#endif   /* _H_ARCHINCLUDE */
