/*
 * This file contains miscellaneous low-level functions for PPC 44x.
 *    Copyright 2007 David Gibson <dwg@au1.ibm.com>, IBM Corporation.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version
 * 2 of the License, or (at your option) any later version.
 *
 */

#include <asm/mmu.h>
#include <asm/reg.h>
#include <asm/ppc_asm.h>

	.text

#ifdef CONFIG_PPC_47x

#define LOAD_CLEAR_CCR2_DSTI(REG1, REG2)	\
BEGIN_MMU_FTR_SECTION				\
	mfspr REG1,SPRN_CCR2_476;		\
	rlwinm	REG2,REG1,0,~CCR2_476_DSTI;	\
	mtspr	SPRN_CCR2_476,REG2;		\
END_MMU_FTR_SECTION_IFSET(MMU_FTR_TYPE_47x)

#define RESTORE_CCR2_DSTI(REG)			\
BEGIN_MMU_FTR_SECTION				\
	mtspr	SPRN_CCR2_476,REG;		\
END_MMU_FTR_SECTION_IFSET(MMU_FTR_TYPE_47x)

#else	/* CONFIG_PPC_47x */

#define LOAD_CLEAR_CCR2_DSTI(REG1, REG2)
#define RESTORE_CCR2_DSTI(REG)

#endif	/* CONFIG_PPC_47x */

/*
 * Do an IO access in AS1
 */
_GLOBAL(as1_readb)
	LOAD_CLEAR_CCR2_DSTI(r8, r9)
	mfmsr	r7
	ori	r0,r7,MSR_DS
	sync
	mtmsr	r0
	sync
	isync
	lbz	r3,0(r3)
	sync
	mtmsr	r7
	sync
	isync
	RESTORE_CCR2_DSTI(r8)
	blr

_GLOBAL(as1_writeb)
	LOAD_CLEAR_CCR2_DSTI(r8, r9)
	mfmsr	r7
	ori	r0,r7,MSR_DS
	sync
	mtmsr	r0
	sync
	isync
	stb	r3,0(r4)
	sync
	mtmsr	r7
	sync
	isync
	RESTORE_CCR2_DSTI(r8)
	blr
