/*
 *   Creation Date: <2003/06/06 20:00:52 samuel>
 *   Time-stamp: <2004/03/06 13:54:26 samuel>
 *
 *	<misc.c>
 *
 *	Miscellaneous
 *
 *   Copyright (C) 2003, 2004 Samuel Rydh (samuel@ibrium.se)
 *
 *   This program is free software; you can redistribute it and/or
 *   modify it under the terms of the GNU General Public License
 *   version 2
 *
 */

#include "archinclude.h"
#include "mol-ioctl.h"
#include "mmu.h"
#include "mtable.h"
#include "constants.h"
#include "asmfuncs.h"
#include "performance.h"
#include "misc.h"
#include "emu.h"
#include "alloc.h"
#include "uaccess.h"


/************************************************************************/
/*	Performance Info						*/
/************************************************************************/

#ifdef PERFORMANCE_INFO

static void
clear_performance_info( kernel_vars_t *kv )
{
	perf_info_t *p = g_perf_info_table;
	int i;

	for( ; p->name ; p++ )
		*p->ctrptr = 0;
	for( i=0; i<NUM_ASM_BUMP_CNTRS; i++ )
		kv->asm_bump_cntr[i] = 0;
	kv->num_acntrs = 0;
}

static int
get_performance_info( kernel_vars_t *kv, uint ind, perf_ctr_t *r )
{
	perf_info_t *p;
	int len;
	char *name;

	for( p=g_perf_info_table; p->name && ind; p++, ind-- )
		;
	if( !p->name ) {
		extern int __start_bumptable[], __end_bumptable[];
		if( ind >= __end_bumptable - __start_bumptable )
			return 1;
		name = (char*)__start_bumptable + __start_bumptable[ind];
		r->ctr = kv->asm_bump_cntr[ind];
	} else {
		name = p->name;
		r->ctr = *p->ctrptr;
	}

	if( (len=strlen(name)+1) > sizeof(r->name) )
		len = sizeof(r->name);
	memcpy( r->name, name, len );
	return 0;
}

#else /* PERFORMANCE_INFO */

static void
clear_performance_info( kernel_vars_t *kv )
{
}

static int
get_performance_info( kernel_vars_t *kv, uint ind, perf_ctr_t *r )
{
	return 1;
}

#endif /* PERFORMANCE_INFO */



/************************************************************************/
/*	misc								*/
/************************************************************************/

int
do_debugger_op( kernel_vars_t *kv, dbg_op_params_t *pb )
{
	int ret = 0;

	switch( pb->operation ) {
	case DBG_OP_EMULATE_TLBIE:
		flush_ea_range( kv, (pb->ea & ~0xf0000000), 0x1000 );
		break;

	case DBG_OP_EMULATE_TLBIA:
		clear_all_vsids( kv );
		break;

	case DBG_OP_GET_PTE:
		ret = dbg_get_PTE( kv, pb->context, pb->ea, &pb->ret.pte );
		break;

	case DBG_OP_BREAKPOINT_FLAGS:
		kv->break_flags = pb->param;
		kv->mregs.flag_bits &= ~fb_DbgTrace;
		kv->mregs.flag_bits |= (pb->param & BREAK_SINGLE_STEP)? fb_DbgTrace : 0;
		msr_altered( kv );
		break;

	case DBG_OP_TRANSLATE_EA:
		/* param == is_data_access */
		ret = dbg_translate_ea( kv, pb->context, pb->ea, &pb->ret.phys, pb->param );
		break;

	default:
		printk("Unimplemended debugger operation %d\n", pb->operation );
		ret = -ENOSYS_MOL;
		break;
	}
	return ret;
}

static void
tune_spr( kernel_vars_t *kv, uint spr, int action )
{
	extern int r__spr_illegal[], r__spr_read_only[], r__spr_read_write[];
	int hook, newhook=0;

	if( spr >= 1024 )
		return;

	hook = kv->_bp.spr_hooks[spr];

	/* LSB of hook specifies whether the SPR is privileged */
	switch( action ) {
	case kTuneSPR_Illegal:
		newhook = (int)r__spr_illegal;
		hook &= ~1;
		break;

	case kTuneSPR_Privileged:
		hook |= 1;
		break;

	case kTuneSPR_Unprivileged:
		hook &= ~1;
		break;

	case kTuneSPR_ReadWrite:
		newhook = (int)r__spr_read_write;
		break;

	case kTuneSPR_ReadOnly:
		newhook = (int)r__spr_read_only;
		break;
	}
	if( newhook )
		hook = (hook & 1) | tophys_mol( (char*)reloc_ptr(newhook) );
	kv->_bp.spr_hooks[spr] = hook;
}

/* return value: <0: system error, >=0: ret value */
int
handle_ioctl( kernel_vars_t *kv, int cmd, int arg1, int arg2, int arg3 )
{
	struct mmu_mapping map;
	perf_ctr_t pctr;
	int ret = 0;

	switch( cmd ) {
	case MOL_IOCTL_GET_SESSION_MAGIC:
		ret = get_session_magic( arg1 );
		break;

	case MOL_IOCTL_IDLE_RECLAIM_MEMORY:
		mtable_reclaim( kv );
		break;

	case MOL_IOCTL_SPR_CHANGED:
		msr_altered(kv);
		mmu_altered(kv);
		break;

	case MOL_IOCTL_ADD_IORANGE: /* void ( ulong mbase, int size, void *usr_data )*/
		add_io_trans( kv, arg1, arg2, (void*)arg3 );
		break;
	case MOL_IOCTL_REMOVE_IORANGE:	/* void ( ulong mbase, int size ) */
		remove_io_trans( kv, arg1, arg2 );
		break;

	case MOL_IOCTL_ALLOC_EMUACCEL_SLOT: /* EMULATE_xxx, param, ret_addr -- mphys */
		ret = alloc_emuaccel_slot( kv, arg1, arg2, arg3 );
		break;
	case MOL_IOCTL_MAPIN_EMUACCEL_PAGE: /* arg1 = mphys */
		ret = mapin_emuaccel_page( kv, arg1 );
		break;

	case MOL_IOCTL_SETUP_FBACCEL: /* lvbase, bytes_per_row, height */
		setup_fb_acceleration( kv, (char*)arg1, arg2, arg3 );
		break;
	case MOL_IOCTL_TUNE_SPR: /* spr#, action */
		tune_spr( kv, arg1, arg2 );
		break;

	case MOL_IOCTL_MMU_MAP: /* arg1=struct mmu_mapping *m, arg2=map/unmap */
		if( copy_from_user_mol(&map, (struct mmu_mapping*)arg1, sizeof(map)) )
			break;
		if( arg2 )
			mmu_add_map( kv, &map );
		else
			mmu_remove_map( kv, &map );
		if( copy_to_user_mol((struct mmu_mapping*)arg1, &map, sizeof(map)) )
			ret = -EFAULT_MOL;
		break;

	case MOL_IOCTL_GET_PERF_INFO:
		ret = get_performance_info( kv, arg1, &pctr );
		if( copy_to_user_mol((perf_ctr_t*)arg2, &pctr, sizeof(pctr)) )
			ret = -EFAULT_MOL;
		break;

#if 0
	case MOL_IOCTL_TRACK_DIRTY_RAM:
		ret = track_lvrange( kv );
		break;
	case MOL_IOCTL_GET_DIRTY_RAM:
		ret = get_track_buffer( kv, (char*)arg1 );
		break;
	case MOL_IOCTL_SET_DIRTY_RAM:
		set_track_buffer( kv, (char*)arg1 );
		break;
#endif
	/* ---------------- performance statistics ------------------ */

	case MOL_IOCTL_CLEAR_PERF_INFO:
		clear_performance_info( kv );
		break;

	default:
		printk("unsupported MOL ioctl %d\n", cmd );
		ret = -ENOSYS_MOL;
	}
	return ret;
}
