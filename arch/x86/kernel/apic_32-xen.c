/*
 *	Local APIC handling stubs
 */

#include <linux/init.h>
#include <linux/interrupt.h>

#include <asm/smp.h>

/*
 * Debug level, exported for io_apic.c
 */
unsigned int apic_verbosity;

/* Have we found an MP table */
int smp_found_config;

static int __init apic_set_verbosity(char *str)
{
	if (strcmp("debug", str) == 0)
		apic_verbosity = APIC_DEBUG;
	else if (strcmp("verbose", str) == 0)
		apic_verbosity = APIC_VERBOSE;
	return 1;
}

__setup("apic=", apic_set_verbosity);

int setup_profiling_timer(unsigned int multiplier)
{
	return -EINVAL;
}

#ifndef CONFIG_SMP
/*
 * This initializes the IO-APIC and APIC hardware if this is
 * a UP kernel.
 */
int __init APIC_init_uniprocessor(void)
{
	if (!cpu_has_apic)
		return -1;

#ifdef CONFIG_X86_IO_APIC
	if (smp_found_config)
		if (!skip_ioapic_setup && nr_ioapics)
			setup_IO_APIC();
#endif

	return 0;
}
#endif
