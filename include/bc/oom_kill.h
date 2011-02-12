#include <bc/decl.h>
#include <bc/task.h>
#include <bc/beancounter.h>

#define get_exec_oom_ctrl()		(&current->task_bc.exec_ub->oom_ctrl)
#define active_oom_ctrl()		(current->task_bc.oom_ctrl)

UB_DECLARE_FUNC(int, ub_oom_lock(void))
UB_DECLARE_FUNC(struct user_beancounter *, ub_oom_select_worst(void))
UB_DECLARE_VOID_FUNC(ub_oom_mm_killed(struct user_beancounter *ub))
UB_DECLARE_VOID_FUNC(ub_oom_unlock(void))
UB_DECLARE_VOID_FUNC(ub_oom_task_dead(struct mm_struct *mm))
UB_DECLARE_FUNC(int, ub_oom_task_skip(struct user_beancounter *ub,
			struct task_struct *tsk))
UB_DECLARE_FUNC(int, out_of_memory_in_ub(struct user_beancounter *ub,
					gfp_t gfp_mask))
UB_DECLARE_VOID_FUNC(ub_oom_start(struct oom_control *oom_ctrl))
UB_DECLARE_VOID_FUNC(ub_oom_task_killed(struct task_struct *tsk))

#ifdef CONFIG_BEANCOUNTERS
#endif
