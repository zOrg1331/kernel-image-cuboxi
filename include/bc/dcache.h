#ifndef __UB_DCACHE_H__
#define __UB_DCACHE_H__

#include <bc/decl.h>

UB_DECLARE_FUNC(int, ub_dcache_charge(struct user_beancounter *ub, int name_len))
UB_DECLARE_VOID_FUNC(ub_dcache_uncharge(struct user_beancounter *ub, int name_len))
UB_DECLARE_VOID_FUNC(ub_dcache_newroot(struct dentry *d))

#endif
