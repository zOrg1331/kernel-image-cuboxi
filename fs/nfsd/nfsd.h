static inline int nfsd_v4client(struct svc_rqst *rq)
{
	return rq->rq_prog == NFS_PROGRAM && rq->rq_vers == 4;
}
