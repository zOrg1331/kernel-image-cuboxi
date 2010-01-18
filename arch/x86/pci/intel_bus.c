/*
 * to read io range from IOH pci conf, need to do it after mmconfig is there
 */

#include <linux/delay.h>
#include <linux/dmi.h>
#include <linux/pci.h>
#include <linux/init.h>
#include <asm/pci_x86.h>

#include "bus_numa.h"

static inline void print_ioh_resources(struct pci_root_info *info)
{
	int res_num;
	int busnum;
	int i;

	printk(KERN_DEBUG "IOH bus: [%02x, %02x]\n",
			info->bus_min, info->bus_max);
	res_num = info->res_num;
	busnum = info->bus_min;
	for (i = 0; i < res_num; i++) {
		struct resource *res;

		res = &info->res[i];
		printk(KERN_DEBUG "IOH bus: %02x index %x %s: [%llx, %llx]\n",
			busnum, i,
			(res->flags & IORESOURCE_IO) ? "io port" :
							"mmio",
			res->start, res->end);
	}
}

#define IOH_LIO			0x108
#define IOH_LMMIOL		0x10c
#define IOH_LMMIOH		0x110
#define IOH_LMMIOH_BASEU	0x114
#define IOH_LMMIOH_LIMITU	0x118
#define IOH_LCFGBUS		0x11c

#define IOH_VTBAR		0x180
#define IOH_VTSIZE		0x2000	/* Fixed HW size (not programmable) */

static void __devinit pci_root_bus_res(struct pci_dev *dev)
{
	u16 word;
	u32 dword;
	struct pci_root_info tmp, *info = &tmp;
	u16 io_base, io_end;
	u32 mmiol_base, mmiol_end, vtbar;
	u64 mmioh_base, mmioh_end;
	int bus_base, bus_end;

	if (pci_root_num >= PCI_ROOT_NR) {
		printk(KERN_DEBUG "intel_bus.c: PCI_ROOT_NR is too small\n");
		return;
	}

	if (pci_read_config_word(dev, IOH_LCFGBUS, &word))
		return;
	bus_base = (word & 0xff);
	bus_end = (word & 0xff00) >> 8;
	sprintf(info->name, "PCI Bus #%02x", bus_base);
	info->bus_min = bus_base;
	info->bus_max = bus_end;

	if (pci_read_config_word(dev, IOH_LIO, &word))
		return;
	io_base = (word & 0xf0) << (12 - 4);
	io_end = (word & 0xf000) | 0xfff;
	update_res(info, io_base, io_end, IORESOURCE_IO, 0);

	if (pci_read_config_dword(dev, IOH_LMMIOL, &dword))
		return;
	mmiol_base = (dword & 0xff00) << (24 - 8);
	mmiol_end = (dword & 0xff000000) | 0xffffff;
	if (pci_read_config_dword(dev, IOH_VTBAR, &dword))
		return;
	vtbar = dword & 0xfffffffe;
	if (dword & 0x1 &&
		(mmiol_base < vtbar + IOH_VTSIZE - 1 && vtbar < mmiol_end)) {
		/* remove VT-d DRDH from Local MMIOL window */
		if (vtbar <= mmiol_base)
			mmiol_base = vtbar + IOH_VTSIZE;
		else if (mmiol_end <= vtbar + IOH_VTSIZE - 1)
			mmiol_end = vtbar - 1;
		else {
			update_res(info, mmiol_base, vtbar - 1,
				   IORESOURCE_MEM, 0);
			mmiol_base = vtbar + IOH_VTSIZE;
		}
	}
	update_res(info, mmiol_base, mmiol_end, IORESOURCE_MEM, 0);

	if (pci_read_config_dword(dev, IOH_LMMIOH, &dword))
		return;
	mmioh_base = ((u64)(dword & 0xfc00)) << (26 - 10);
	mmioh_end = ((u64)(dword & 0xfc000000) | 0x3ffffff);
	if (pci_read_config_dword(dev, IOH_LMMIOH_BASEU, &dword))
		return;
	mmioh_base |= ((u64)(dword & 0x7ffff)) << 32;
	if (pci_read_config_dword(dev, IOH_LMMIOH_LIMITU, &dword))
		return;
	mmioh_end |= ((u64)(dword & 0x7ffff)) << 32;
	update_res(info, mmioh_base, mmioh_end, IORESOURCE_MEM, 0);

	pci_root_info[pci_root_num++] = *info;
	print_ioh_resources(info);
}

/* intel IOH */
DECLARE_PCI_FIXUP_EARLY(PCI_VENDOR_ID_INTEL, 0x342e, pci_root_bus_res);
