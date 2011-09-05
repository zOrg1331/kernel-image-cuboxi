#ifdef CONFIG_BEANCOUNTERS
cpt_object_t *cpt_add_ubc(struct user_beancounter *bc, struct cpt_context *ctx);
__u64 cpt_lookup_ubc(struct user_beancounter *bc, struct cpt_context *ctx);
int cpt_dump_ubc(struct cpt_context *ctx);

struct user_beancounter *rst_lookup_ubc(__u64 pos, struct cpt_context *ctx);
int rst_undump_ubc(struct cpt_context *ctx);

void cpt_finish_ubc(struct cpt_context *ctx);
void rst_finish_ubc(struct cpt_context *ctx);
static inline void copy_one_ubparm(struct ubparm *from,
				   struct ubparm *to,
				   int bc_parm_id)
{
	to[bc_parm_id].barrier = from[bc_parm_id].barrier;
	to[bc_parm_id].limit = from[bc_parm_id].limit;
}
static inline void set_one_ubparm_to_max(struct ubparm *ubprm, int bc_parm_id)
{
	ubprm[bc_parm_id].barrier = UB_MAXVALUE;
	ubprm[bc_parm_id].limit = UB_MAXVALUE;
}
#else
static int inline cpt_dump_ubc(struct cpt_context *ctx)
{ return 0; }
static int inline rst_undump_ubc(struct cpt_context *ctx)
{ return 0; }
static void inline cpt_finish_ubc(struct cpt_context *ctx)
{ return; }
static void inline rst_finish_ubc(struct cpt_context *ctx)
{ return; }
#endif

