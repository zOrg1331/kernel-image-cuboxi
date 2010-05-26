#ifndef _FS_CEPH_RBD
#define _FS_CEPH_RBD

extern void rbd_set_osdc(struct ceph_osd_client *o);
extern int __init rbd_init(void);
extern void __exit rbd_exit(void);

#endif
