/*
 * linux/include/ve_nfs.h
 *
 * VE context for NFS
 *
 * Copyright (C) 2007 SWsoft
 */

#ifndef __VE_NFS_H__
#define __VE_NFS_H__

#ifdef CONFIG_VE

#include <linux/ve.h>

#define NFS_CTX_FIELD(arg)  (get_exec_env()->_##arg)

#else /* CONFIG_VE */

#define NFS_CTX_FIELD(arg)	_##arg

#endif /* CONFIG_VE */

#define nlmsvc_grace_period	NFS_CTX_FIELD(nlmsvc_grace_period)
#define nlmsvc_timeout		NFS_CTX_FIELD(nlmsvc_timeout)
#define nlmsvc_users		NFS_CTX_FIELD(nlmsvc_users)
#define nlmsvc_task		NFS_CTX_FIELD(nlmsvc_task)
#define nlmsvc_rqst		NFS_CTX_FIELD(nlmsvc_rqst)

#include <linux/nfsd/stats.h>

#define VE_RAPARM_SIZE	2048

struct ve_nfsd_data {
	struct file_system_type *nfsd_fs;
	struct cache_detail *exp_cache;
	struct cache_detail *key_cache;
	struct svc_serv *_nfsd_serv;
	struct nfsd_stats stats;
	struct svc_stat *svc_stat;
	char raparm_mem[VE_RAPARM_SIZE];
};

struct ve_rpc_data {
	struct proc_dir_entry	*_proc_net_rpc;
	struct cache_detail	*_ip_map_cache;
	struct file_system_type	*rpc_pipefs_fstype;
	struct rpc_clnt		*_rpcb_local;
	struct rpc_clnt		*_rpcb_local4;
};

extern int ve_nfs_sync(struct ve_struct *env);
extern void nfs_change_server_params(void *data, int flags, int timeo, int retrans);
extern int is_nfs_automount(struct vfsmount *mnt);

/* This two originaly defined in linux/sunrpc/xprt.h */
#define RPC_MAX_ABORT_TIMEOUT	INT_MAX
extern int xprt_abort_timeout;
 
#endif
