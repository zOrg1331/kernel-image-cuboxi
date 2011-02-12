/*
 *  include/bc/vmpages.h
 *
 *  Copyright (C) 2005  SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 */

#ifndef __UB_PAGES_H_
#define __UB_PAGES_H_

#include <linux/linkage.h>
#include <bc/beancounter.h>
#include <bc/decl.h>

/*
 * Check whether vma has private or copy-on-write mapping.
 */
#define VM_UB_PRIVATE(__flags, __file)					\
		( ((__flags) & VM_WRITE) ?				\
			(__file) == NULL || !((__flags) & VM_SHARED) :	\
			0						\
		)

UB_DECLARE_FUNC(int, ub_memory_charge(struct mm_struct *mm,
			unsigned long size,
			unsigned vm_flags,
			struct file *vm_file,
			int strict))
UB_DECLARE_VOID_FUNC(ub_memory_uncharge(struct mm_struct *mm,
			unsigned long size,
			unsigned vm_flags,
			struct file *vm_file))

struct shmem_inode_info;
UB_DECLARE_FUNC(int, ub_shmpages_charge(struct shmem_inode_info *i,
			unsigned long sz))
UB_DECLARE_VOID_FUNC(ub_shmpages_uncharge(struct shmem_inode_info *i,
			unsigned long sz))
UB_DECLARE_VOID_FUNC(ub_tmpfs_respages_inc(struct shmem_inode_info *shi))
UB_DECLARE_VOID_FUNC(ub_tmpfs_respages_sub(struct shmem_inode_info *shi,
			unsigned long size))
#define ub_tmpfs_respages_dec(shi)	ub_tmpfs_respages_sub(shi, 1)

#ifdef CONFIG_BEANCOUNTERS
#define shmi_ub_set(shi, ub)	do {			\
		(shi)->shmi_ub = get_beancounter(ub);	\
	} while (0)
#define shmi_ub_put(shi)	do {			\
		put_beancounter((shi)->shmi_ub);	\
		(shi)->shmi_ub = NULL;			\
	} while (0)
#else
#define shmi_ub_set(shi, ub)	do { } while (0)
#define shmi_ub_put(shi)	do { } while (0)
#endif

UB_DECLARE_FUNC(int, ub_locked_charge(struct mm_struct *mm,
			unsigned long size))
UB_DECLARE_VOID_FUNC(ub_locked_uncharge(struct mm_struct *mm,
			unsigned long size))
UB_DECLARE_FUNC(int, ub_lockedshm_charge(struct shmem_inode_info *shi,
			unsigned long size))
UB_DECLARE_VOID_FUNC(ub_lockedshm_uncharge(struct shmem_inode_info *shi,
			unsigned long size))

extern void __ub_update_oomguarpages(struct user_beancounter *ub);
static inline unsigned long ub_mapped_pages(struct user_beancounter *ub)
{
	return ub_stat_get(ub, mapped_file_pages) +
		ub_stat_get(ub, anonymous_pages);
}

#ifdef CONFIG_BC_SWAP_ACCOUNTING
#define SWP_DECLARE_FUNC(ret, decl)	UB_DECLARE_FUNC(ret, decl)
#define SWP_DECLARE_VOID_FUNC(decl)	UB_DECLARE_VOID_FUNC(decl)
#else
#define SWP_DECLARE_FUNC(ret, decl)	static inline ret decl {return (ret)0;}
#define SWP_DECLARE_VOID_FUNC(decl)	static inline void decl { }
#endif

struct swap_info_struct;
SWP_DECLARE_FUNC(int, ub_swap_init(struct swap_info_struct *si, pgoff_t n))
SWP_DECLARE_VOID_FUNC(ub_swap_fini(struct swap_info_struct *si))
SWP_DECLARE_VOID_FUNC(ub_swapentry_inc(struct swap_info_struct *si, pgoff_t n,
			struct user_beancounter *ub))
SWP_DECLARE_VOID_FUNC(ub_swapentry_dec(struct swap_info_struct *si, pgoff_t n))

extern int ub_check_ram_limits(struct user_beancounter *ub, gfp_t gfp_mask);

#endif /* __UB_PAGES_H_ */
