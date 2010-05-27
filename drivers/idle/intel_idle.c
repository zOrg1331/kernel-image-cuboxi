/*
 * intel_idle.c - native hardware idle loop for modern Intel processors
 *
 * Copyright (c) 2010, Intel Corporation.
 * Len Brown <len.brown@intel.com>
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
 */

/*
 * intel_idle is a cpuidle driver that loads on specific Intel processors
 * in lieu of the legacy ACPI processor_idle driver.  The intent is to
 * make Linux more efficient on these processors, as intel_idle knows
 * more than ACPI, as well as make Linux more immune to ACPI BIOS bugs.
 */

/*
 * to test
 * test: build & run with acpi=off
 * test: repeated load/unload
 * test on NHM-EP
 */

/*
 * todo cpuidle
 * 	cpuidle should supply the counters for each driver
 * 	since they are private to cpuidle, not the driver
 */

/*
 * Design Assumptions
 *
 * All CPUs have same idle states as boot cpu
 * Chipset BM_STS (bus master status) bit is a NOP
 * 	for preventing entry into deep C-stats
 */

// TBD hotplug cpu implications
// 	we assume all cpus have same capabilitys as boot cpu
// 	we allocate data structures for all possible cpus
//
// ACPI has a .suspend hack to turn off deep c-statees during suspend
// 	to avoid complications with the lapic timer workaround
// 	will need to address that situation here too.

/* un-comment DEBUG to enable pr_debug() statements */
#define DEBUG

#include <linux/kernel.h>
#include <linux/cpuidle.h>
#include <linux/clockchips.h>
#include <linux/hrtimer.h>	/* ktime_get_real() */
#include <trace/events/power.h>
#include <linux/sched.h>

#define INTEL_IDLE_VERSION "0.2"
#define PREFIX "intel_idle: "

#define MWAIT_SUBSTATE_MASK	(0xf)
#define MWAIT_CSTATE_MASK	(0xf)
#define MWAIT_SUBSTATE_SIZE	(4)
#define CPUID_MWAIT_LEAF (5)
#define CPUID5_ECX_EXTENSIONS_SUPPORTED (0x1)
#define CPUID5_ECX_INTERRUPT_BREAK	(0x2)

#define mwait_hint_to_cstate(hint) ((((hint) >> MWAIT_SUBSTATE_SIZE) & MWAIT_CSTATE_MASK) + 1)
#define lapic_timer_reliable(cstate) (lapic_timer_reliable_states & (1 << (cstate)))

static struct cpuidle_driver intel_idle_driver = {
	.name = "intel_idle",
	.owner = THIS_MODULE,
};
static int max_cstate;
static int disable;
static int power_policy = 7; /* 0 = max perf; 15 = max powersave */

static unsigned int substates;
#define get_num_substates(cstate) ((substates >> ((cstate) * 4)) && 0xF)

/* Reliable LAPIC Timer States, bit 1 for C1 etc.  */
static unsigned int lapic_timer_reliable_states;

static struct cpuidle_device *intel_idle_cpuidle_devices;
static int intel_idle(struct cpuidle_device *dev, struct cpuidle_state *state);

/*
 * These attributes are be visible under
 * /sys/devices/system/cpu/cpu.../cpuidle/state.../
 *
 * name 
 * 	Hardware name of the state, from datasheet
 * desc
 * 	MWAIT param
 * driver_data
 * 	token passed to intel_idle()
 * flags
 * 	CPUIDLE_FLAG_TIME_VALID
 * 		we return valid times in all states
 * 	CPUIDLE_FLAG_SHALLOW
 * 		lapic timer keeps running
 * exit_latency
 * 	[usec]
 * power_usage
 * 	mW (TBD)
 * target_residency
 * 	currently we multiply exit_latency by 4
 * 	[usec]
 * usage
 * 	instance counter
 * time
 * 	residency counter [usec]
 */

static struct cpuidle_state *cpuidle_state_table;

static struct cpuidle_state nehalem_cstates[] = {
	{ "POLL", "", 0, 0, 0, 0, 0, 0, 0, 0},
	{ "NHM-C1", "MWAIT 0x00", (void *) 0x00,
		CPUIDLE_FLAG_TIME_VALID,
		3, 1000, 6, 0, 0, &intel_idle },
	{ "NHM-C3", "MWAIT 0x10", (void *) 0x10,
		CPUIDLE_FLAG_TIME_VALID,
		20, 500, 80, 0, 0, &intel_idle },
	{ "NHM-C6", "MWAIT 0x20", (void *) 0x20,
		CPUIDLE_FLAG_TIME_VALID,
		200, 350, 800, 0, 0, &intel_idle },
	{ "", "", 0, 0, 0, 0, 0, 0, 0, 0}
};

static struct cpuidle_state atom_cstates[] = {
	{ "POLL", "", 0, 0, 0, 0, 0, 0, 0, 0},
	{ "ATM-C1", "MWAIT 0x00", (void *) 0x00,
		CPUIDLE_FLAG_TIME_VALID,
		1, 1000, 4, 0, 0, &intel_idle },
	{ "ATM-C2", "MWAIT 0x10", (void *) 0x10,
		CPUIDLE_FLAG_TIME_VALID,
		20, 500, 80, 0, 0, &intel_idle },
	{ "ATM-C4", "MWAIT 0x30", (void *) 0x30,
		CPUIDLE_FLAG_TIME_VALID,
		100, 250, 400, 0, 0, &intel_idle },
	{ "ATM-C6", "MWAIT 0x40", (void *) 0x40,
		CPUIDLE_FLAG_TIME_VALID,
		200, 150, 800, 0, 0, &intel_idle },
	{ "", "", 0, 0, 0, 0, 0, 0, 0, 0}
};

/*
 * choose_substate()
 *
 * Run-time decision on which C-state substate to invoke
 * If power_policy = 0, choose shallowest substate (0)
 * If power_policy = 15, choose deepest substate
 * If power_policy = middle, choose middle substate etc.
 */
static int choose_substate(int cstate)
{
	unsigned int num_substates;

	power_policy &= 0xF;	/* valid range: 0-15 */
	cstate &= 7;	/* valid range: 0-7 */

	num_substates = get_num_substates(cstate);

	if (num_substates <= 1)
		return 0;
	
	return ((power_policy + (power_policy + 1) * (num_substates - 1)) / 16);
}

/**
 * intel_idle
 * @dev: cpuidle_device
 * @state: cpuidle state
 *
 */
static int
intel_idle(struct cpuidle_device *dev, struct cpuidle_state *state)
{
	unsigned long ecx = 1; /* break on interrupt flag */
	unsigned long eax = (unsigned long)cpuidle_get_statedata(state);
	unsigned int cstate;
	ktime_t kt_before, kt_after;
	s64 usec_delta;
	int cpu = smp_processor_id();

	cstate = mwait_hint_to_cstate(eax);

	eax = eax + choose_substate(cstate);

	local_irq_disable();

	if (!lapic_timer_reliable(cstate))
		clockevents_notify(CLOCK_EVT_NOTIFY_BROADCAST_ENTER, &cpu); 

	kt_before = ktime_get_real();

	stop_critical_timings();
#ifndef MODULE
	trace_power_start(POWER_CSTATE, (eax >> 4) + 1);
#endif
	if (!need_resched()) {

		__monitor((void *)&current_thread_info()->flags, 0, 0);
		smp_mb();
		if (!need_resched())
			__mwait(eax, ecx);
	}

	start_critical_timings();

	kt_after = ktime_get_real();
	usec_delta = ktime_to_us(ktime_sub(kt_after, kt_before));

	local_irq_enable();
	
	if (!lapic_timer_reliable(cstate))
 		clockevents_notify(CLOCK_EVT_NOTIFY_BROADCAST_EXIT, &cpu); 

	return usec_delta;
}


/*
 * intel_idle_probe()
 */
static int intel_idle_probe(void)
{
	unsigned int eax, ebx, ecx, edx;

	if (disable) {
		pr_debug(PREFIX "disabled\n" );
		return -1;
	}

	if (boot_cpu_data.x86_vendor != X86_VENDOR_INTEL)
		return -1;
 
	if (!boot_cpu_has(X86_FEATURE_MWAIT))
		return -1;

	if (boot_cpu_data.cpuid_level < CPUID_MWAIT_LEAF)
		return -1;

	cpuid(CPUID_MWAIT_LEAF, &eax, &ebx, &ecx, &edx);

	if (!(ecx & CPUID5_ECX_EXTENSIONS_SUPPORTED) ||
		!(ecx & CPUID5_ECX_INTERRUPT_BREAK))
			return -1;

	pr_debug(PREFIX "MWAIT substates: 0x%x\n", edx);

	if (substates == 0)
		substates = edx;

	/*
 	 * Bail out if non-stop TSC unavailable.
 	 * Nehalem and newer have it.
 	 *
 	 * Atom and Core2 will will require
 	 * mark_tsc_unstable("TSC halts in idle")
 	 * when have a state deeper than C1
 	 */
	if (!boot_cpu_has(X86_FEATURE_NONSTOP_TSC))
		return -1;

	if (boot_cpu_has(X86_FEATURE_ARAT))	/* Always Reliable APIC Timer */
		lapic_timer_reliable_states = 0xFFFFFFFF;

	if (boot_cpu_data.x86 != 6)	/* family 6 */
		return -1;

	switch (boot_cpu_data.x86_model) {

	case 0x1A:	/* Core i7, Xeon 5500 series */
	case 0x1E:	/* Core i7 and i5 Processor - Lynnfield, Jasper Forest */
	case 0x1F:	/* Core i7 and i5 Processor - Nehalem */
	case 0x2E:	/* Nehalem-EX Xeon */
		lapic_timer_reliable_states = (1 << 1);	 /* C1 */

	case 0x25:	/* Westmere */
	case 0x2C:	/* Westmere */

		cpuidle_state_table = nehalem_cstates;
		break;
#ifdef notyet
	case 0x1C:	/* 28 - Atom Processor */
		cpuidle_state_table = atom_cstates;
		break;
#endif

	case 0x17:	/* 23 - Core 2 Duo */
		lapic_timer_reliable_states = (1 << 2) | (1 << 1); /* C2, C1 */

	default:
		pr_debug(PREFIX "does not run on family %d model %d\n",
			boot_cpu_data.x86, boot_cpu_data.x86_model);
		return -1;
	}

	pr_debug(PREFIX "v" INTEL_IDLE_VERSION
		" model 0x%X\n", boot_cpu_data.x86_model);

pr_debug(PREFIX "lapic_timer_reliable_states 0x%x\n", lapic_timer_reliable_states);
	return 0;
}

/*
 * intel_idle_cpuidle_devices_init()
 * allocate, initialize, register cpuidle_devices
 */
static int intel_idle_cpuidle_devices_init(void)
{
	int i, cstate;
	struct cpuidle_device *dev;

	intel_idle_cpuidle_devices = alloc_percpu(struct cpuidle_device);
	if (intel_idle_cpuidle_devices == NULL)
		return -1;

	for_each_possible_cpu(i) {
		dev = per_cpu_ptr(intel_idle_cpuidle_devices, i);

//#if 0
		/* dev->states[0] is used by cpuidle for the polling state */
		dev->states[1] = nehalem_cstates[1]; // hard coded
		dev->states[2] = nehalem_cstates[2]; // hard coded
		dev->states[3] = nehalem_cstates[3]; // hard coded

		dev->state_count = 4; // hard coded
//#endif
#if 0

		for (cstate = 1; cstate < CPUIDLE_STATE_MAX; ++cstate) {
			if (cstate > max_cstate) {
				printk(PREFIX "max_cstate %d reached", max_cstate);
				break;
			}
			if (get_num_substates(cstate) == 0) {
				pr_debug(PREFIX "no substates for cstate %d\n", cstate);
				break;
			}

			if (cpuidle_state_table[cstate].name == NULL) {
				printk(PREFIX "cstate %d not found\n", cstate);
			} else {
				dev->states[cstate] = cpuidle_state_table[cstate];
				pr_debug(PREFIX "cstate %d found\n", cstate);
			}
		}
		dev->state_count = cstate;
#endif

		pr_debug(PREFIX "state_count %d\n", dev->state_count);

		dev->cpu = i;
		if (cpuidle_register_device(dev)) {
			free_percpu(intel_idle_cpuidle_devices);
			return -EIO;
		}
	}
	return 0;
}

/*
 * intel_idle_cpuidle_devices_uninit()
 * unregister, free cpuidle_devices
 */
static void intel_idle_cpuidle_devices_uninit(void)
{
	int i;
	struct cpuidle_device *dev;

	for_each_possible_cpu(i) {
		dev = per_cpu_ptr(intel_idle_cpuidle_devices, i);
		cpuidle_unregister_device(dev);
	}

	free_percpu(intel_idle_cpuidle_devices);
	return;
}

static int intel_idle_init(void) 
{

	if (intel_idle_probe())
		return -1;

	if (cpuidle_register_driver(&intel_idle_driver)) {
		pr_debug(PREFIX "unable to register with cpuidle due to %s",
			cpuidle_get_driver()->name);
		return -1;
	}

	if (intel_idle_cpuidle_devices_init()) {
		cpuidle_unregister_driver(&intel_idle_driver);
		return -1;
	}

	return 0;	
}

static void __exit intel_idle_exit(void)
{
	intel_idle_cpuidle_devices_uninit();
	cpuidle_unregister_driver(&intel_idle_driver);

	return;
}

module_init(intel_idle_init);
module_exit(intel_idle_exit);
module_param(max_cstate, int, 0444);
module_param(disable, int, 0444);
module_param(substates, int, 0444);
module_param(power_policy, int, 0644);

MODULE_AUTHOR("Len Brown <len.brown@intel.com>");
MODULE_DESCRIPTION("Cpuidle driver for Intel Hardware v" INTEL_IDLE_VERSION);
MODULE_LICENSE("GPL");

