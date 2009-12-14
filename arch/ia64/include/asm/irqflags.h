#ifndef _ASM_IRQFLAGS_H
#define _ASM_IRQFLAGS_H
#include <asm/kregs.h>
#include <asm/pal.h>
/*
 * The group barrier in front of the rsm & ssm are necessary to ensure
 * that none of the previous instructions in the same group are
 * affected by the rsm/ssm.
 *
 * For spinlocks etc 
 * - clearing psr.i is implicitly serialized (visible by next insn)
 * - setting psr.i requires data serialization
 * - we need a stop-bit before reading PSR because we sometimes
 *   write a floating-point register right before reading the PSR
 *   and that writes to PSR.mfl
 */
#define __local_irq_save(x)			\
do {						\
	ia64_stop();				\
	(x) = ia64_getreg(_IA64_REG_PSR);	\
	ia64_stop();				\
	ia64_rsm(IA64_PSR_I);			\
} while (0)

#define __local_irq_disable()			\
do {						\
	ia64_stop();				\
	ia64_rsm(IA64_PSR_I);			\
} while (0)

#define __local_irq_restore(x)	ia64_intrin_local_irq_restore((x) & IA64_PSR_I)

#ifdef CONFIG_IA64_DEBUG_IRQ

  extern unsigned long last_cli_ip;

# define __save_ip()		last_cli_ip = ia64_getreg(_IA64_REG_IP)

# define raw_local_irq_save(x)					\
do {								\
	unsigned long psr;					\
								\
	__local_irq_save(psr);					\
	if (psr & IA64_PSR_I)					\
		__save_ip();					\
	(x) = psr;						\
} while (0)

# define raw_local_irq_disable()	do { unsigned long x; raw_local_irq_save(x); } while (0)

# define raw_local_irq_restore(x)					\
do {								\
	unsigned long old_psr, psr = (x);			\
								\
	local_save_flags(old_psr);				\
	__local_irq_restore(psr);				\
	if ((old_psr & IA64_PSR_I) && !(psr & IA64_PSR_I))	\
		__save_ip();					\
} while (0)

#else /* !CONFIG_IA64_DEBUG_IRQ */
# define raw_local_irq_save(x)	__local_irq_save(x)
# define raw_local_irq_disable()	__local_irq_disable()
# define raw_local_irq_restore(x)	__local_irq_restore(x)
#endif /* !CONFIG_IA64_DEBUG_IRQ */

#define raw_local_irq_enable()	({ ia64_stop(); ia64_ssm(IA64_PSR_I); ia64_srlz_d(); })
#define raw_local_save_flags(flags)	({ ia64_stop(); (flags) = ia64_getreg(_IA64_REG_PSR); })

#define raw_irqs_disabled()				\
({						\
	unsigned long __ia64_id_flags;		\
	raw_local_save_flags(__ia64_id_flags);	\
	(__ia64_id_flags & IA64_PSR_I) == 0;	\
})

#define raw_safe_halt()         ia64_pal_halt_light()    /* PAL_HALT_LIGHT */
#define raw_irqs_disabled_flags(flags)	\
({						\
	(int)((flags) & IA64_PSR_I) == 0;	\
})
	
#ifdef CONFIG_TRACE_IRQFLAGS
#define TRACE_IRQS_ON br.call.sptk.many b0=trace_hardirqs_on
#define TRACE_IRQS_OFF br.call.sptk.many b0=trace_hardirqs_off
#else
#define TRACE_IRQS_ON
#define TRACE_IRQS_OFF
#endif

#define ARCH_LOCKDEP_SYS_EXIT br.call.sptk.many rp=lockdep_sys_exit

#ifdef CONFIG_DEBUG_LOCK_ALLOC
#define LOCKDEP_SYS_EXIT	ARCH_LOCKDEP_SYS_EXIT
#else
#define LOCKDEP_SYS_EXIT
#endif

#endif


