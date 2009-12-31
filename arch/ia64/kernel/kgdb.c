/*
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2, or (at your option) any
 * later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 */

/*
 * Copyright (C) 2004 Amit S. Kale <amitkale@linsyssoft.com>
 * Copyright (C) 2000-2001 VERITAS Software Corporation.
 * Copyright (C) 2002 Andi Kleen, SuSE Labs
 * Copyright (C) 2004 LinSysSoft Technologies Pvt. Ltd.
 * Copyright (C) 2007 MontaVista Software, Inc.
 * Copyright (C) 2007-2008 Jason Wessel, Wind River Systems, Inc.
 */
/****************************************************************************
 *  Contributor:     Lake Stevens Instrument Division$
 *  Written by:      Glenn Engel $
 *  Updated by:	     Amit Kale<akale@veritas.com>
 *  Updated by:	     Tom Rini <trini@kernel.crashing.org>
 *  Updated by:	     Jason Wessel <jason.wessel@windriver.com>
 *  Modified for 386 by Jim Kingdon, Cygnus Support.
 *  Origianl kgdb, compatibility with 2.1.xx kernel by
 *  David Grothe <dave@gcom.com>
 *  Integrated into 2.2.5 kernel by Tigran Aivazian <tigran@sco.com>
 *  X86_64 changes from Andi Kleen's patch merged by Jim Houston
 *  IA64 changes:    Tony Luck
 */
#include <linux/spinlock.h>
#include <linux/kdebug.h>
#include <linux/string.h>
#include <linux/kernel.h>
#include <linux/ptrace.h>
#include <linux/sched.h>
#include <linux/delay.h>
#include <linux/kgdb.h>
#include <linux/init.h>
#include <linux/smp.h>
#include <linux/nmi.h>

#include <asm/break.h>
#include <asm/sections.h>
#include <asm/system.h>
#include <asm/unwind.h>

u64	bkpt_iip;

struct frameinfo {
	unsigned long *gdb_regs;
	unsigned long iip;
};

static void
getframeregs(struct unw_frame_info *info, void *arg)
{
	struct frameinfo *f = arg;
	unsigned long ip, val;

	do {
		unw_get_ip(info, &ip);
		if (ip == 0)
			break;
		if (ip == f->iip) {
			unw_get_cfm(info, &val);
			f->gdb_regs[461] = val;
			unw_get_ar(info, UNW_AR_RSC, &val);
			f->gdb_regs[GDB_ar_rsc] = val;
			unw_get_bsp(info, &val);
			f->gdb_regs[479] = val;
			unw_get_ar(info, UNW_AR_BSPSTORE, &val);
			f->gdb_regs[GDB_ar_bspstore] = val;
			unw_get_ar(info, UNW_AR_PFS, &val);
			f->gdb_regs[GDB_ar_pfs]	= val;
			return;
		}
	} while (unw_unwind(info) >= 0);
}

/**
 *	pt_regs_to_gdb_regs - Convert ptrace regs to GDB regs
 *	@gdb_regs: A pointer to hold the registers in the order GDB wants.
 *	@regs: The &struct pt_regs of the current process.
 *
 *	Convert the pt_regs in @regs into the format for registers that
 *	GDB expects, stored in @gdb_regs.
 */
void pt_regs_to_gdb_regs(unsigned long *gdb_regs, struct pt_regs *regs)
{
	struct frameinfo info;

	info.gdb_regs = gdb_regs;
	info.iip = regs->cr_iip;
	unw_init_running(getframeregs, &info);
	gdb_regs[GDB_r1]	= regs->r1;
	gdb_regs[GDB_r2]	= regs->r2;
	gdb_regs[GDB_r3]	= regs->r3;
	gdb_regs[GDB_r8]	= regs->r8;
	gdb_regs[GDB_r9]	= regs->r9;
	gdb_regs[GDB_r10]	= regs->r10;
	gdb_regs[GDB_r11]	= regs->r11;
	gdb_regs[GDB_r12]	= regs->r12;
	gdb_regs[GDB_r13]	= regs->r13;
	gdb_regs[GDB_r14]	= regs->r14;
	gdb_regs[GDB_r15]	= regs->r15;
	gdb_regs[GDB_r16]	= regs->r16;
	gdb_regs[GDB_r17]	= regs->r17;
	gdb_regs[GDB_r18]	= regs->r18;
	gdb_regs[GDB_r19]	= regs->r19;
	gdb_regs[GDB_r20]	= regs->r20;
	gdb_regs[GDB_r21]	= regs->r21;
	gdb_regs[GDB_r22]	= regs->r22;
	gdb_regs[GDB_r23]	= regs->r23;
	gdb_regs[GDB_r24]	= regs->r24;
	gdb_regs[GDB_r25]	= regs->r25;
	gdb_regs[GDB_r26]	= regs->r26;
	gdb_regs[GDB_r27]	= regs->r27;
	gdb_regs[GDB_r28]	= regs->r28;
	gdb_regs[GDB_r29]	= regs->r29;
	gdb_regs[GDB_r30]	= regs->r30;
	gdb_regs[GDB_r31]	= regs->r31;
	gdb_regs[GDB_f6]	= regs->f6.u.bits[0];
	gdb_regs[GDB_f6+1]	= regs->f6.u.bits[1];
	gdb_regs[GDB_f7]	= regs->f7.u.bits[0];
	gdb_regs[GDB_f7+1]	= regs->f7.u.bits[1];
	gdb_regs[GDB_f8]	= regs->f8.u.bits[0];
	gdb_regs[GDB_f8+1]	= regs->f8.u.bits[1];
	gdb_regs[GDB_f9]	= regs->f9.u.bits[0];
	gdb_regs[GDB_f9+1]	= regs->f9.u.bits[1];
	gdb_regs[GDB_f10]	= regs->f10.u.bits[0];
	gdb_regs[GDB_f10+1]	= regs->f10.u.bits[1];
	gdb_regs[GDB_f11]	= regs->f11.u.bits[0];
	gdb_regs[GDB_f11+1]	= regs->f11.u.bits[1];
	gdb_regs[GDB_b0]	= regs->b0;
	gdb_regs[GDB_b6]	= regs->b6;
	gdb_regs[GDB_b7]	= regs->b7;
	gdb_regs[GDB_pr]	= regs->pr;
	gdb_regs[GDB_cr_iip]	= regs->cr_iip;
	gdb_regs[GDB_cr_ipsr]	= regs->cr_ipsr;
	//gdb_regs[GDB_ar_rsc]	= regs->ar_rsc;
	//gdb_regs[GDB_ar_bspstore] = regs->ar_bspstore;
	gdb_regs[GDB_ar_rnat]	= regs->ar_rnat;
	gdb_regs[GDB_ar_csd]	= regs->ar_csd;
	gdb_regs[GDB_ar_ssd]	= regs->ar_ssd;
	gdb_regs[GDB_ar_ccv]	= regs->ar_ccv;
	gdb_regs[GDB_ar_unat]	= regs->ar_unat;
	gdb_regs[GDB_ar_fpsr]	= regs->ar_fpsr;
	//gdb_regs[GDB_ar_pfs]	= regs->ar_pfs;
}

/**
 *	sleeping_thread_to_gdb_regs - Convert ptrace regs to GDB regs
 *	@gdb_regs: A pointer to hold the registers in the order GDB wants.
 *	@p: The &struct task_struct of the desired process.
 *
 *	Convert the register values of the sleeping process in @p to
 *	the format that GDB expects.
 *	This function is called when kgdb does not have access to the
 *	&struct pt_regs and therefore it should fill the gdb registers
 *	@gdb_regs with what has	been saved in &struct thread_struct
 *	thread field during switch_to.
 */
void sleeping_thread_to_gdb_regs(unsigned long *gdb_regs, struct task_struct *p)
{
	if (!p)
		return;

	pt_regs_to_gdb_regs(gdb_regs, task_pt_regs(p));
}

/**
 *	gdb_regs_to_pt_regs - Convert GDB regs to ptrace regs.
 *	@gdb_regs: A pointer to hold the registers we've received from GDB.
 *	@regs: A pointer to a &struct pt_regs to hold these values in.
 *
 *	Convert the GDB regs in @gdb_regs into the pt_regs, and store them
 *	in @regs.
 */
void gdb_regs_to_pt_regs(unsigned long *gdb_regs, struct pt_regs *regs)
{
	regs->r1		= gdb_regs[GDB_r1];
	regs->r2		= gdb_regs[GDB_r2];
	regs->r3		= gdb_regs[GDB_r3];
	regs->r8		= gdb_regs[GDB_r8];
	regs->r9		= gdb_regs[GDB_r9];
	regs->r10		= gdb_regs[GDB_r10];
	regs->r11		= gdb_regs[GDB_r11];
	regs->r12		= gdb_regs[GDB_r12];
	regs->r13		= gdb_regs[GDB_r13];
	regs->r14		= gdb_regs[GDB_r14];
	regs->r15		= gdb_regs[GDB_r15];
	regs->r16		= gdb_regs[GDB_r16];
	regs->r17		= gdb_regs[GDB_r17];
	regs->r18		= gdb_regs[GDB_r18];
	regs->r19		= gdb_regs[GDB_r19];
	regs->r20		= gdb_regs[GDB_r20];
	regs->r21		= gdb_regs[GDB_r21];
	regs->r22		= gdb_regs[GDB_r22];
	regs->r23		= gdb_regs[GDB_r23];
	regs->r24		= gdb_regs[GDB_r24];
	regs->r25		= gdb_regs[GDB_r25];
	regs->r26		= gdb_regs[GDB_r26];
	regs->r27		= gdb_regs[GDB_r27];
	regs->r28		= gdb_regs[GDB_r28];
	regs->r29		= gdb_regs[GDB_r29];
	regs->r30		= gdb_regs[GDB_r30];
	regs->r31		= gdb_regs[GDB_r31];
	regs->f6.u.bits[0]	= gdb_regs[GDB_f6];
	regs->f6.u.bits[1]	= gdb_regs[GDB_f6+1];
	regs->f7.u.bits[0]	= gdb_regs[GDB_f7];
	regs->f7.u.bits[1]	= gdb_regs[GDB_f7+1];
	regs->f8.u.bits[0]	= gdb_regs[GDB_f8];
	regs->f8.u.bits[1]	= gdb_regs[GDB_f8+1];
	regs->f9.u.bits[0]	= gdb_regs[GDB_f9];
	regs->f9.u.bits[1]	= gdb_regs[GDB_f9+1];
	regs->f10.u.bits[0]	= gdb_regs[GDB_f10];
	regs->f10.u.bits[1]	= gdb_regs[GDB_f10+1];
	regs->f11.u.bits[0]	= gdb_regs[GDB_f11];
	regs->f11.u.bits[1]	= gdb_regs[GDB_f11+1];
	regs->b0		= gdb_regs[GDB_b0];
	regs->b6		= gdb_regs[GDB_b6];
	regs->b7		= gdb_regs[GDB_b7];
	regs->pr		= gdb_regs[GDB_pr];
	regs->cr_iip		= gdb_regs[GDB_cr_iip];
	regs->cr_ipsr		= gdb_regs[GDB_cr_ipsr];
	regs->ar_rsc		= gdb_regs[GDB_ar_rsc];
	regs->ar_bspstore	= gdb_regs[GDB_ar_bspstore];
	regs->ar_rnat		= gdb_regs[GDB_ar_rnat];
	regs->ar_csd		= gdb_regs[GDB_ar_csd];
	regs->ar_ssd		= gdb_regs[GDB_ar_ssd];
	regs->ar_ccv		= gdb_regs[GDB_ar_ccv];
	regs->ar_unat		= gdb_regs[GDB_ar_unat];
	regs->ar_fpsr		= gdb_regs[GDB_ar_fpsr];
	regs->ar_pfs		= gdb_regs[GDB_ar_pfs];
}

#ifdef CONFIG_SMP
static void kgdb_call_nmi_hook(void *ignored)
{
	kgdb_nmicallback(raw_smp_processor_id(), NULL);
}

/**
 *	kgdb_roundup_cpus - Get other CPUs into a holding pattern
 *	@flags: Current IRQ state
 */
void kgdb_roundup_cpus(unsigned long flags)
{
	local_irq_enable();
	smp_call_function(kgdb_call_nmi_hook, NULL, 0);
	local_irq_disable();
}
#endif

/**
 *	kgdb_arch_handle_exception - Handle architecture specific GDB packets.
 *	@vector: The error vector of the exception that happened.
 *	@signo: The signal number of the exception that happened.
 *	@err_code: The error code of the exception that happened.
 *	@remcom_in_buffer: The buffer of the packet we have read.
 *	@remcom_out_buffer: The buffer of %BUFMAX bytes to write a packet into.
 *	@regs: The &struct pt_regs of the current process.
 *
 *	This function MUST handle the 'c' and 's' command packets,
 *	as well packets to set / remove a hardware breakpoint, if used.
 *	If there are additional packets which the hardware needs to handle,
 *	they are handled here.  The code should return -1 if it wants to
 *	process more packets, and a %0 or %1 if it wants to exit from the
 *	kgdb callback.
 */
int kgdb_arch_handle_exception(int e_vector, int signo, int err_code,
			       char *remcomInBuffer, char *remcomOutBuffer,
			       struct pt_regs *linux_regs)
{
	unsigned long addr;
	char *ptr;

	switch (remcomInBuffer[0]) {
	case 'c':
	case 's':
		/* try to read optional parameter, pc unchanged if no parm */
		ptr = &remcomInBuffer[1];
		if (kgdb_hex2long(&ptr, &addr)) {
			linux_regs->cr_iip = addr;
			linux_regs->cr_ipsr &= ~IA64_PSR_RI;
			switch (addr & 0xf) {
			case 0x6:
				linux_regs->cr_ipsr |=
					(__IA64_UL(1) << IA64_PSR_RI_BIT);
				break;
			case 0xc:
				linux_regs->cr_ipsr |=
					(__IA64_UL(2) << IA64_PSR_RI_BIT);
				break;
			}
		}
	case 'D':
	case 'k':
		/*
		 * If we are at the start of arch_kgdb_breakpoint() we must
		 * step to the next instruction in the bundle, otherwise we
		 * would just re-execute the breakpoint.
		 */
		if (linux_regs->cr_iip == bkpt_iip &&
		    (linux_regs->cr_ipsr & IA64_PSR_RI) == 0)
			linux_regs->cr_ipsr |=
				(__IA64_UL(1) << IA64_PSR_RI_BIT);

		/* clear the trace bit */
		linux_regs->cr_ipsr &= ~IA64_PSR_SS;
		atomic_set(&kgdb_cpu_doing_single_step, -1);

		/* set the trace bit if we're stepping */
		if (remcomInBuffer[0] == 's') {
			linux_regs->cr_ipsr |= IA64_PSR_SS;
			kgdb_single_step = 1;
			atomic_set(&kgdb_cpu_doing_single_step,
				   raw_smp_processor_id());
		}

		return 0;
	}

	/* this means that we do not want to exit from the handler: */
	return -1;
}

static inline int
single_step_cont(struct pt_regs *regs, struct die_args *args)
{
	/*
	 * Single step exception from kernel space to user space so
	 * eat the exception and continue the process:
	 */
	printk(KERN_ERR "KGDB: trap/step from kernel to user space, "
			"resuming...\n");
	kgdb_arch_handle_exception(args->trapnr, args->signr,
				   args->err, "c", "", regs);

	return NOTIFY_STOP;
}

static int __kgdb_notify(struct die_args *args, unsigned long cmd)
{
	struct pt_regs *regs = args->regs;

	switch (cmd) {
	case DIE_BREAK:
		/* err is break number from ia64_bad_break() */
		if ((args->err >> 12) != (__IA64_BREAK_KGDB >> 12))
			return NOTIFY_DONE;
	case DIE_FAULT:
		/* err is vector number from ia64_fault() */
		if (args->err == 36)
			/*TODO?: single step */;
		break;
	default:
		if (user_mode(regs))
			return NOTIFY_DONE;
	}

	if (kgdb_handle_exception(args->trapnr, args->signr, args->err, regs))
		return NOTIFY_DONE;

	return NOTIFY_STOP;
}

static int
kgdb_notify(struct notifier_block *self, unsigned long cmd, void *ptr)
{
	unsigned long flags;
	int ret;

	local_irq_save(flags);
	ret = __kgdb_notify(ptr, cmd);
	local_irq_restore(flags);

	return ret;
}

static struct notifier_block kgdb_notifier = {
	.notifier_call	= kgdb_notify,

	/*
	 * Lowest-prio notifier priority, we want to be notified last:
	 */
	.priority	= -INT_MAX,
};

/**
 *	kgdb_arch_init - Perform any architecture specific initalization.
 *
 *	This function will handle the initalization of any architecture
 *	specific callbacks.
 */
int kgdb_arch_init(void)
{
	bkpt_iip = (u64)dereference_function_descriptor(arch_kgdb_breakpoint);
	return register_die_notifier(&kgdb_notifier);
}

/**
 *	kgdb_arch_exit - Perform any architecture specific uninitalization.
 *
 *	This function will handle the uninitalization of any architecture
 *	specific callbacks, for dynamic registration and unregistration.
 */
void kgdb_arch_exit(void)
{
	unregister_die_notifier(&kgdb_notifier);
}

/*
 * Based on ideas from the kprobe code, we reserve 4096 breakpoint values
 * so we can set a breakpoint in slot 1 without having to update across
 * the 64-bit boundary in the middle of the instruction bundle.  For
 * symmetry we do the same even when setting a breakpoint in slot 0
 * or slot 2. This also means we only have to save 23 bits of old
 * instruction information.
 */
static void patch(unsigned long addr, void *instr, void *saved)
{
	u64 *b = __va(ia64_tpa(addr & ~0xful));
	u32 newinst;
	int idx, bit;

	switch (addr & 0xful) {
	case 0x0:
		idx = 0; bit = 23;
		break;
	case 0x6:
		idx = 1; bit = 0;
		break;
	case 0xc:
		idx = 1; bit = 41;
		break;
	default:
		printk("kgdb patch - bad address: %lx\n", addr);
		return;
	}
	if (saved) {
		u32 old = (b[idx] >> bit) & 0x7ffffful;
		memcpy(saved, &old, sizeof(old));
	}
	memcpy(&newinst, instr, sizeof(newinst));
	b[idx] = (b[idx] & ~(0x7ffffful << bit)) | ((u64)newinst << bit);

	ia64_fc(&b[idx]);
	ia64_sync_i();
	ia64_srlz_i();
}

int kgdb_arch_set_breakpoint(unsigned long addr, char *saved_instr)
{
	u32 bkpt = __IA64_BREAK_KGDB >> 12;

	patch(addr, &bkpt, saved_instr);
	return 0;
}

int kgdb_arch_remove_breakpoint(unsigned long addr, char *bundle)
{
	patch(addr, bundle, 0);
	return 0;
}

struct kgdb_arch arch_kgdb_ops = {
	.flags			= 0,
};
