#include <linux/ioport.h>
#include <asm/e820.h>

void arch_remove_reservations(struct resource *avail)
{
	/*
	 * Trim out the area reserved for BIOS (low 1MB).  We could also remove
	 * E820 "reserved" areas here.
	 */
	if (avail->flags & IORESOURCE_MEM) {
		if (avail->start < BIOS_END)
			avail->start = BIOS_END;
	}
}
