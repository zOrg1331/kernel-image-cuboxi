/*
 *	Xen SMP booting functions
 *
 *	See arch/i386/kernel/smpboot.c for copyright and credits for derived
 *	portions of this file.
 */

#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/mm.h>
#include <linux/sched.h>
#include <linux/kernel_stat.h>
#include <linux/smp_lock.h>
#include <linux/irq.h>
#include <linux/bootmem.h>
#include <linux/notifier.h>
#include <linux/cpu.h>
#include <linux/percpu.h>
#include <asm/desc.h>
#include <asm/arch_hooks.h>
#include <asm/pgalloc.h>
#include <xen/evtchn.h>
#include <xen/interface/vcpu.h>
#include <xen/cpu_hotplug.h>
#include <xen/xenbus.h>

extern irqreturn_t smp_reschedule_interrupt(int, void *);
extern irqreturn_t smp_call_function_interrupt(int, void *);
extern irqreturn_t smp_call_function_single_interrupt(int, void *);

extern int local_setup_timer(unsigned int cpu);
extern void local_teardown_timer(unsigned int cpu);

extern void hypervisor_callback(void);
extern void failsafe_callback(void);
extern void system_call(void);
extern void smp_trap_init(trap_info_t *);

/* Number of siblings per CPU package */
int smp_num_siblings = 1;

cpumask_t cpu_online_map;
EXPORT_SYMBOL(cpu_online_map);
cpumask_t cpu_possible_map;
EXPORT_SYMBOL(cpu_possible_map);
cpumask_t cpu_initialized_map;

DEFINE_PER_CPU(struct cpuinfo_x86, cpu_info);
EXPORT_PER_CPU_SYMBOL(cpu_info);

static int __read_mostly resched_irq = -1;
static int __read_mostly callfunc_irq = -1;
static int __read_mostly call1func_irq = -1;

#ifdef CONFIG_X86_LOCAL_APIC
#define set_cpu_to_apicid(cpu, apicid) (per_cpu(x86_cpu_to_apicid, cpu) = (apicid))
#else
#define set_cpu_to_apicid(cpu, apicid)
#endif

DEFINE_PER_CPU(cpumask_t, cpu_sibling_map);
DEFINE_PER_CPU(cpumask_t, cpu_core_map);
EXPORT_PER_CPU_SYMBOL(cpu_core_map);

void __init prefill_possible_map(void)
{
	int i, rc;

	for_each_possible_cpu(i)
	    if (i != smp_processor_id())
		return;

	for (i = 0; i < NR_CPUS; i++) {
		rc = HYPERVISOR_vcpu_op(VCPUOP_is_up, i, NULL);
		if (rc >= 0) {
			cpu_set(i, cpu_possible_map);
			nr_cpu_ids = i + 1;
		}
	}
}

static inline void
set_cpu_sibling_map(unsigned int cpu)
{
	cpu_data(cpu).phys_proc_id = cpu;
	cpu_data(cpu).cpu_core_id  = 0;

	per_cpu(cpu_sibling_map, cpu) = cpumask_of_cpu(cpu);
	per_cpu(cpu_core_map, cpu) = cpumask_of_cpu(cpu);

	cpu_data(cpu).booted_cores = 1;
}

static void
remove_siblinginfo(unsigned int cpu)
{
	cpu_data(cpu).phys_proc_id = BAD_APICID;
	cpu_data(cpu).cpu_core_id  = BAD_APICID;

	cpus_clear(per_cpu(cpu_sibling_map, cpu));
	cpus_clear(per_cpu(cpu_core_map, cpu));

	cpu_data(cpu).booted_cores = 0;
}

static int __cpuinit xen_smp_intr_init(unsigned int cpu)
{
	static struct irqaction resched_action = {
		.handler = smp_reschedule_interrupt,
		.flags   = IRQF_DISABLED,
		.name    = "resched"
	}, callfunc_action = {
		.handler = smp_call_function_interrupt,
		.flags   = IRQF_DISABLED,
		.name    = "callfunc"
	}, call1func_action = {
		.handler = smp_call_function_single_interrupt,
		.flags   = IRQF_DISABLED,
		.name    = "call1func"
	};
	int rc;

	rc = bind_ipi_to_irqaction(RESCHEDULE_VECTOR,
				   cpu,
				   &resched_action);
	if (rc < 0)
		return rc;
	if (resched_irq < 0)
		resched_irq = rc;
	else
		BUG_ON(resched_irq != rc);

	rc = bind_ipi_to_irqaction(CALL_FUNCTION_VECTOR,
				   cpu,
				   &callfunc_action);
	if (rc < 0)
		goto unbind_resched;
	if (callfunc_irq < 0)
		callfunc_irq = rc;
	else
		BUG_ON(callfunc_irq != rc);

	rc = bind_ipi_to_irqaction(CALL_FUNC_SINGLE_VECTOR,
				   cpu,
				   &call1func_action);
	if (rc < 0)
		goto unbind_call;
	if (call1func_irq < 0)
		call1func_irq = rc;
	else
		BUG_ON(call1func_irq != rc);

	rc = xen_spinlock_init(cpu);
	if (rc < 0)
		goto unbind_call1;

	if ((cpu != 0) && ((rc = local_setup_timer(cpu)) != 0))
		goto fail;

	return 0;

 fail:
	xen_spinlock_cleanup(cpu);
 unbind_call1:
	unbind_from_per_cpu_irq(call1func_irq, cpu, NULL);
 unbind_call:
	unbind_from_per_cpu_irq(callfunc_irq, cpu, NULL);
 unbind_resched:
	unbind_from_per_cpu_irq(resched_irq, cpu, NULL);
	return rc;
}

#ifdef CONFIG_HOTPLUG_CPU
static void __cpuinit xen_smp_intr_exit(unsigned int cpu)
{
	if (cpu != 0)
		local_teardown_timer(cpu);

	unbind_from_per_cpu_irq(resched_irq, cpu, NULL);
	unbind_from_per_cpu_irq(callfunc_irq, cpu, NULL);
	unbind_from_per_cpu_irq(call1func_irq, cpu, NULL);
	xen_spinlock_cleanup(cpu);
}
#endif

void __cpuinit cpu_bringup(void)
{
	cpu_init();
	identify_secondary_cpu(&current_cpu_data);
	touch_softlockup_watchdog();
	preempt_disable();
	local_irq_enable();
}

static void __cpuinit cpu_bringup_and_idle(void)
{
	cpu_bringup();
	cpu_idle();
}

static void __cpuinit cpu_initialize_context(unsigned int cpu)
{
	/* vcpu_guest_context_t is too large to allocate on the stack.
	 * Hence we allocate statically and protect it with a lock */
	static vcpu_guest_context_t ctxt;
	static DEFINE_SPINLOCK(ctxt_lock);

	struct task_struct *idle = idle_task(cpu);

	if (cpu_test_and_set(cpu, cpu_initialized_map))
		return;

	spin_lock(&ctxt_lock);

	memset(&ctxt, 0, sizeof(ctxt));

	ctxt.flags = VGCF_IN_KERNEL;
	ctxt.user_regs.ds = __USER_DS;
	ctxt.user_regs.es = __USER_DS;
	ctxt.user_regs.fs = 0;
	ctxt.user_regs.gs = 0;
	ctxt.user_regs.ss = __KERNEL_DS;
	ctxt.user_regs.eip = (unsigned long)cpu_bringup_and_idle;
	ctxt.user_regs.eflags = X86_EFLAGS_IF | 0x1000; /* IOPL_RING1 */

	memset(&ctxt.fpu_ctxt, 0, sizeof(ctxt.fpu_ctxt));

	smp_trap_init(ctxt.trap_ctxt);

	ctxt.ldt_ents = 0;
	ctxt.gdt_frames[0] = virt_to_mfn(get_cpu_gdt_table(cpu));
	ctxt.gdt_ents = GDT_SIZE / 8;

	ctxt.user_regs.cs = __KERNEL_CS;
	ctxt.user_regs.esp = idle->thread.sp0 - sizeof(struct pt_regs);

	ctxt.kernel_ss = __KERNEL_DS;
	ctxt.kernel_sp = idle->thread.sp0;

	ctxt.event_callback_eip    = (unsigned long)hypervisor_callback;
	ctxt.failsafe_callback_eip = (unsigned long)failsafe_callback;
#ifdef __i386__
	ctxt.event_callback_cs     = __KERNEL_CS;
	ctxt.failsafe_callback_cs  = __KERNEL_CS;

	ctxt.ctrlreg[3] = xen_pfn_to_cr3(virt_to_mfn(swapper_pg_dir));

	ctxt.user_regs.fs = __KERNEL_PERCPU;
#else /* __x86_64__ */
	ctxt.syscall_callback_eip  = (unsigned long)system_call;

	ctxt.ctrlreg[3] = xen_pfn_to_cr3(virt_to_mfn(init_level4_pgt));

	ctxt.gs_base_kernel = (unsigned long)(cpu_pda(cpu));
#endif

	if (HYPERVISOR_vcpu_op(VCPUOP_initialise, cpu, &ctxt))
		BUG();

	spin_unlock(&ctxt_lock);
}

void __init smp_prepare_cpus(unsigned int max_cpus)
{
	unsigned int cpu;
	struct task_struct *idle;
	int apicid;
	struct vcpu_get_physid cpu_id;
	void *gdt_addr;

	apicid = 0;
	if (HYPERVISOR_vcpu_op(VCPUOP_get_physid, 0, &cpu_id) == 0)
		apicid = xen_vcpu_physid_to_x86_apicid(cpu_id.phys_id);
	boot_cpu_data.apicid = apicid;
	cpu_data(0) = boot_cpu_data;

	set_cpu_to_apicid(0, apicid);

	current_thread_info()->cpu = 0;

	for_each_possible_cpu (cpu) {
		cpus_clear(per_cpu(cpu_sibling_map, cpu));
		cpus_clear(per_cpu(cpu_core_map, cpu));
	}

	set_cpu_sibling_map(0);

	if (xen_smp_intr_init(0))
		BUG();

	cpu_initialized_map = cpumask_of_cpu(0);

	/* Restrict the possible_map according to max_cpus. */
	while ((num_possible_cpus() > 1) && (num_possible_cpus() > max_cpus)) {
		for (cpu = NR_CPUS-1; !cpu_isset(cpu, cpu_possible_map); cpu--)
			continue;
		cpu_clear(cpu, cpu_possible_map);
	}

	for_each_possible_cpu (cpu) {
		if (cpu == 0)
			continue;

		idle = fork_idle(cpu);
		if (IS_ERR(idle))
			panic("failed fork for CPU %d", cpu);

#ifdef __i386__
		init_gdt(cpu);
#endif
		gdt_addr = get_cpu_gdt_table(cpu);
		make_page_readonly(gdt_addr, XENFEAT_writable_descriptor_tables);

		apicid = cpu;
		if (HYPERVISOR_vcpu_op(VCPUOP_get_physid, cpu, &cpu_id) == 0)
			apicid = xen_vcpu_physid_to_x86_apicid(cpu_id.phys_id);
		cpu_data(cpu) = boot_cpu_data;
		cpu_data(cpu).cpu_index = cpu;
		cpu_data(cpu).apicid = apicid;

		set_cpu_to_apicid(cpu, apicid);

#ifdef __x86_64__
		cpu_pda(cpu)->pcurrent = idle;
		cpu_pda(cpu)->cpunumber = cpu;
		clear_ti_thread_flag(task_thread_info(idle), TIF_FORK);
#else
	 	per_cpu(current_task, cpu) = idle;
#endif

		irq_ctx_init(cpu);

#ifdef CONFIG_HOTPLUG_CPU
		if (is_initial_xendomain())
			cpu_set(cpu, cpu_present_map);
#else
		cpu_set(cpu, cpu_present_map);
#endif
	}

	init_xenbus_allowed_cpumask();

#ifdef CONFIG_X86_IO_APIC
	/*
	 * Here we can be sure that there is an IO-APIC in the system. Let's
	 * go and set it up:
	 */
	if (cpu_has_apic && !skip_ioapic_setup && nr_ioapics)
		setup_IO_APIC();
#endif
}

void __init smp_prepare_boot_cpu(void)
{
#ifdef __i386__
	init_gdt(smp_processor_id());
#endif
	switch_to_new_gdt();
	prefill_possible_map();
}

#ifdef CONFIG_HOTPLUG_CPU

/*
 * Initialize cpu_present_map late to skip SMP boot code in init/main.c.
 * But do it early enough to catch critical for_each_present_cpu() loops
 * in i386-specific code.
 */
static int __init initialize_cpu_present_map(void)
{
	cpu_present_map = cpu_possible_map;
	return 0;
}
core_initcall(initialize_cpu_present_map);

int __cpuexit __cpu_disable(void)
{
	cpumask_t map = cpu_online_map;
	unsigned int cpu = smp_processor_id();

	if (cpu == 0)
		return -EBUSY;

	remove_siblinginfo(cpu);

	cpu_clear(cpu, map);
	fixup_irqs(map);
	cpu_clear(cpu, cpu_online_map);

	return 0;
}

void __cpuinit __cpu_die(unsigned int cpu)
{
	while (HYPERVISOR_vcpu_op(VCPUOP_is_up, cpu, NULL)) {
		current->state = TASK_UNINTERRUPTIBLE;
		schedule_timeout(HZ/10);
	}

	xen_smp_intr_exit(cpu);

	if (num_online_cpus() == 1)
		alternatives_smp_switch(0);
}

#endif /* CONFIG_HOTPLUG_CPU */

int __cpuinit __cpu_up(unsigned int cpu)
{
	int rc;

	rc = cpu_up_check(cpu);
	if (rc)
		return rc;

	cpu_initialize_context(cpu);

	if (num_online_cpus() == 1)
		alternatives_smp_switch(1);

	/* This must be done before setting cpu_online_map */
	set_cpu_sibling_map(cpu);
	wmb();

	rc = xen_smp_intr_init(cpu);
	if (rc) {
		remove_siblinginfo(cpu);
		return rc;
	}

	cpu_set(cpu, cpu_online_map);

	rc = HYPERVISOR_vcpu_op(VCPUOP_up, cpu, NULL);
	BUG_ON(rc);

	return 0;
}

void __init smp_cpus_done(unsigned int max_cpus)
{
}

#ifndef CONFIG_X86_LOCAL_APIC
int setup_profiling_timer(unsigned int multiplier)
{
	return -EINVAL;
}
#endif
