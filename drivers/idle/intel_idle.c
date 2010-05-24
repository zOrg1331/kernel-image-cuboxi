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

/* un-comment DEBUG to enable pr_debug() statements */
#define DEBUG

#include <linux/kernel.h>
#include <linux/cpuidle.h>
#include <linux/clockchips.h>
#include <linux/hrtimer.h>	/* ktime_get_real() */
#include <trace/events/power.h>
#include <linux/sched.h>

#define INTEL_IDLE_VERSION "0.1"
#define PREFIX "intel_idle: "

/*
 * intel_idle_load_first exists solely so that acpi_processor can depend on it
 * to guarantee this module to load before that one.
 */
int intel_idle_load_first;
EXPORT_SYMBOL(intel_idle_load_first);

static struct cpuidle_driver intel_idle_driver = {
	.name = "intel_idle",
	.owner = THIS_MODULE,
};
static int ignore_state;
static int disable;

static struct cpuidle_device *intel_idle_cpuidle_devices;
static int intel_idle(struct cpuidle_device *dev, struct cpuidle_state *state);

/*
 * These attributes will be visible to user space under
 * /sys/devices/system/cpu/cpu.../cpuidle/state.../
 *
 * name 
 * 	Hardware name of the state, from datasheet
 * desc
 * 	MWAIT param
 * driver_data
 * 	token passed to intel_idle()
 * flags
 * 	TBD
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

// TBD CPUIDLE_FLAG_TIME_VALID
// TBD CPUIDLE_FLAG_CHECK_BM
//
// TBD BWG BM_STS reference

static struct cpuidle_state all_nehalem_states[] = {

	{ "NHM-C1", "MWAIT 0x00", (void *) 0x00,
		CPUIDLE_FLAG_SHALLOW,
		1, 1000, 1, 0, 0, &intel_idle },
	{ "NHM-C1E", "MWAIT 0x00", (void *) 0x01,
		CPUIDLE_FLAG_SHALLOW,
		3, 1000, 6, 0, 0, &intel_idle },
	{ "NHM-C3", "MWAIT 0x10", (void *) 0x10,
		CPUIDLE_FLAG_BALANCED,
		20, 500, 80, 0, 0, &intel_idle },
	{ "NHM-C6", "MWAIT 0x20", (void *) 0x20,
		CPUIDLE_FLAG_DEEP,
		200, 350, 800, 0, 0, &intel_idle },
	{ "NHM-C7", "MWAIT 0x30", (void *) 0x30,
		CPUIDLE_FLAG_DEEP,
		250, 250, 1000, 0, 0, &intel_idle },
	{ "", "", 0, 0, 0, 0, 0, 0, 0, 0}};

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
	ktime_t kt_before, kt_after;
	s64 usec_delta;
	int cpu = smp_processor_id();

// todo: differentiate between states that stop lapic timer
// 	tbd: if lapic workaround, do we need a c1 bail-out version for suspend?
//
// todo: audit TS_POLLING use in kernel
//
	local_irq_disable();

// tbd: test with lapic timer workaround
// lapic_time_state_broadcast() ?
	clockevents_notify(CLOCK_EVT_NOTIFY_BROADCAST_ENTER, &cpu); 

	kt_before = ktime_get_real();

	stop_critical_timings();
#ifdef notyet
	// not exported to modules
        trace_power_start(POWER_CSTATE, (eax >> 4) + 1);
#endif
        if (!need_resched()) {
                if (cpu_has(&current_cpu_data, X86_FEATURE_CLFLUSH_MONITOR))
                        clflush((void *)&current_thread_info()->flags);

                __monitor((void *)&current_thread_info()->flags, 0, 0);
                smp_mb();
                if (!need_resched())
                        __mwait(eax, ecx);
        }

	start_critical_timings();

	kt_after = ktime_get_real();

	usec_delta = ktime_to_us(ktime_sub(kt_after, kt_before));

	local_irq_enable();
	
	//current_thread_info()->status |= TS_POLLING;	// needed, or redundant?

 	clockevents_notify(CLOCK_EVT_NOTIFY_BROADCAST_EXIT, &cpu); 
	return usec_delta;
}

// TBD hotplug cpu implications

#define MWAIT_SUBSTATE_MASK	(0xf)
#define MWAIT_CSTATE_MASK	(0xf)
#define MWAIT_SUBSTATE_SIZE	(4)
#define CPUID_MWAIT_LEAF (5)
#define CPUID5_ECX_EXTENSIONS_SUPPORTED (0x1)
#define CPUID5_ECX_INTERRUPT_BREAK	(0x2)

/*
 * intel_idle_probe()
 */
static int intel_idle_probe(void)
{
	unsigned int eax, ebx, ecx, edx;
	struct cpuinfo_x86 *c = &cpu_data(0);

	if (disable) {
		pr_debug(PREFIX "disabled\n" );
		return -1;
	}

	if (c->x86_vendor != X86_VENDOR_INTEL)
		return -1;
 
	if (!cpu_has(c, X86_FEATURE_MWAIT))
		return -1;

	if (c->cpuid_level < CPUID_MWAIT_LEAF)
		return -1;

	cpuid(CPUID_MWAIT_LEAF, &eax, &ebx, &ecx, &edx);

	if (!(ecx & CPUID5_ECX_EXTENSIONS_SUPPORTED) ||
		!(ecx & CPUID5_ECX_INTERRUPT_BREAK))
			return -1;

	pr_debug(PREFIX "MWAIT.edx = 0x%x\n", edx);

	if (!cpu_has(c, X86_FEATURE_NONSTOP_TSC))
		//mark_tsc_unstable("TSC halts in idle");
		return -1;

	if (c->x86 != 6)	/* family 6 */
		return 0;

	switch (c->x86_model) {

	case 0x1A:	/* Core i7, Xeon 5500 series */
	case 0x1E:	/* Core i7 and i5 Processor - Lynnfield, Jasper Forest */
	case 0x1F:	/* Core i7 and i5 Processor - Nehalem */
	case 0x25:	/* Westmere */
	case 0x2C:	/* Westmere */
	case 0x2E:	/* Nehalem-EX Xeon */

		pr_debug(PREFIX "v" INTEL_IDLE_VERSION
			" model 0x%X\n", c->x86_model);
		return 0;

	case 0x17:	/* 23 - Core 2 Duo */
	default:
		pr_debug(PREFIX "does not run on family %d model %d\n",
			c->x86, c->x86_model);
		return -1;
	}
}

/*
 * intel_idle_cpuidle_devices_init()
 * allocate, initialize, register cpuidle_devices
 */
static int intel_idle_cpuidle_devices_init(void)
{
	int i;
	struct cpuidle_device *dev;

	intel_idle_cpuidle_devices = alloc_percpu(struct cpuidle_device);
	if (intel_idle_cpuidle_devices == NULL)
		return -1;

// todo probe CPUID.MWAIT to validate each state
// todo: check ignore_state
	for_each_possible_cpu(i) {
		dev = per_cpu_ptr(intel_idle_cpuidle_devices, i);

		dev->states[1] = all_nehalem_states[0]; // hard coded
		dev->states[2] = all_nehalem_states[2]; // hard coded
		dev->states[3] = all_nehalem_states[3]; // hard coded

		dev->state_count = 4; // hard coded

		dev->cpu = i;
		if (cpuidle_register_device(dev)) {
			free_percpu(intel_idle_cpuidle_devices);
			return -EIO;
		}
	}
pr_debug(PREFIX "%d possible cpus\n", i);
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
	intel_idle_load_first = 1;

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
module_param(ignore_state, int, 0444);
module_param(disable, int, 0444);

MODULE_AUTHOR("Len Brown <len.brown@intel.com>");
MODULE_DESCRIPTION("Cpuidle driver for Intel Hardware r" INTEL_IDLE_VERSION);
MODULE_LICENSE("GPL");

