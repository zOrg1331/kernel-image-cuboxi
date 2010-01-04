#ifndef _ASM_IA64_KGDB_H
#define _ASM_IA64_KGDB_H

/*
 * Copyright (C) 2001-2004 Amit S. Kale
 * Copyright (C) 2008 Wind River Systems, Inc.
 */

/*
 * BUFMAX defines the maximum number of characters in inbound/outbound
 * buffers at least NUMREGBYTES*2 are needed for register packets
 * Longer buffer is needed to list all threads
 */
#define BUFMAX			8192

/*
 *  Note that this register image is in a different order than
 *  the register image that Linux produces at interrupt time.
 *
 *  Linux's register image is defined by struct pt_regs in ptrace.h.
 *  Just why GDB uses a different order is a historical mystery.
 */
enum regnames64 {
	GDB_r1 = 1,
	GDB_r2,
	GDB_r3,
	GDB_r8 = 8,
	GDB_r9,
	GDB_r10,
	GDB_r11,
	GDB_r12,
	GDB_r13,
	GDB_r14,
	GDB_r15,
	GDB_r16,
	GDB_r17,
	GDB_r18,
	GDB_r19,
	GDB_r20,
	GDB_r21,
	GDB_r22,
	GDB_r23,
	GDB_r24,
	GDB_r25,
	GDB_r26,
	GDB_r27,
	GDB_r28,
	GDB_r29,
	GDB_r30,
	GDB_r31,
	GDB_f6 = 140,
	GDB_f7,
	GDB_f8,
	GDB_f9,
	GDB_f10,
	GDB_f11,
	GDB_b0 = 448,
	GDB_b6 = 454,
	GDB_b7,
	GDB_pr = 458,
	GDB_cr_iip,
	GDB_cr_ipsr,
	GDB_ar_rsc = 478,
	GDB_ar_bspstore = 480,
	GDB_ar_rnat,
	GDB_ar_csd = 487,
	GDB_ar_ssd,
	GDB_ar_ccv = 494,
	GDB_ar_unat = 498,
	GDB_ar_fpsr = 502,
	GDB_ar_pfs = 526,
/* These are in pt_regs, but gdb doesn't have slots for them
	GDB_cr_ifs,
	GDB_loadrs,
*/
};

#define NUMREGBYTES		((GDB_ar_pfs+1)*8)

extern void arch_kgdb_breakpoint(void);

#define BREAK_INSTR_SIZE	4
#define CACHE_FLUSH_IS_SAFE	1

#endif /* _ASM_IA64_KGDB_H */
