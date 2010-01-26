/*
 * to read io range from IOH pci conf, need to do it after mmconfig is there
 */

#include <linux/delay.h>
#include <linux/dmi.h>
#include <linux/pci.h>
#include <linux/init.h>
#include <asm/pci_x86.h>
#include <asm/pci-direct.h>

#include "bus_numa.h"

static int nr_ioh;
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

static void __devinit pci_root_bus_res(struct pci_dev *dev)
{
	u16 word;
	u32 dword;
	struct pci_root_info *info;
	u16 io_base, io_end;
	u32 mmiol_base, mmiol_end;
	u64 mmioh_base, mmioh_end;
	int bus_base, bus_end;

	if (nr_ioh < 2)
		return;

	/* some sys doesn't get mmconf enabled */
	if (dev->cfg_size < 0x120)
		return;

	if (pci_root_num >= PCI_ROOT_NR) {
		printk(KERN_DEBUG "intel_bus.c: PCI_ROOT_NR is too small\n");
		return;
	}

	info = &pci_root_info[pci_root_num];
	pci_root_num++;

	pci_read_config_word(dev, IOH_LCFGBUS, &word);
	bus_base = (word & 0xff);
	bus_end = (word & 0xff00) >> 8;
	sprintf(info->name, "PCI Bus #%02x", bus_base);
	info->bus_min = bus_base;
	info->bus_max = bus_end;

	pci_read_config_word(dev, IOH_LIO, &word);
	io_base = (word & 0xf0) << (12 - 4);
	io_end = (word & 0xf000) | 0xfff;
	update_res(info, io_base, io_end, IORESOURCE_IO, 0);

	pci_read_config_dword(dev, IOH_LMMIOL, &dword);
	mmiol_base = (dword & 0xff00) << (24 - 8);
	mmiol_end = (dword & 0xff000000) | 0xffffff;
	update_res(info, mmiol_base, mmiol_end, IORESOURCE_MEM, 0);

	pci_read_config_dword(dev, IOH_LMMIOH, &dword);
	mmioh_base = ((u64)(dword & 0xfc00)) << (26 - 10);
	mmioh_end = ((u64)(dword & 0xfc000000) | 0x3ffffff);
	pci_read_config_dword(dev, IOH_LMMIOH_BASEU, &dword);
	mmioh_base |= ((u64)(dword & 0x7ffff)) << 32;
	pci_read_config_dword(dev, IOH_LMMIOH_LIMITU, &dword);
	mmioh_end |= ((u64)(dword & 0x7ffff)) << 32;
	update_res(info, mmioh_base, mmioh_end, IORESOURCE_MEM, 0);

	print_ioh_resources(info);
}

/* intel IOH */
DECLARE_PCI_FIXUP_EARLY(PCI_VENDOR_ID_INTEL, 0x342e, pci_root_bus_res);

static void __init count_ioh(int num, int slot, int func)
{
	nr_ioh++;
}

struct pci_check_probe {
	u32 vendor;
	u32 device;
	void (*f)(int num, int slot, int func);
};

static struct pci_check_probe early_qrk[] __initdata = {
	{ PCI_VENDOR_ID_INTEL, 0x342e, count_ioh },
	{}
};

static void __init early_check_pci_dev(int num, int slot, int func)
{
	u16 vendor;
	u16 device;
	int i;

	vendor = read_pci_config_16(num, slot, func, PCI_VENDOR_ID);
	device = read_pci_config_16(num, slot, func, PCI_DEVICE_ID);

	for (i = 0; early_qrk[i].f != NULL; i++) {
		if (((early_qrk[i].vendor == PCI_ANY_ID) ||
			(early_qrk[i].vendor == vendor)) &&
			((early_qrk[i].device == PCI_ANY_ID) ||
			(early_qrk[i].device == device)))
				early_qrk[i].f(num, slot, func);
	}
}

static void __init early_check_pci_devs(void)
{
	unsigned bus, slot, func;

	if (!early_pci_allowed())
		return;

	for (bus = 0; bus < 256; bus++) {
		for (slot = 0; slot < 32; slot++) {
			for (func = 0; func < 8; func++) {
				u32 class;
				u8 type;

				class = read_pci_config(bus, slot, func,
							PCI_CLASS_REVISION);
				if (class == 0xffffffff)
					continue;

				early_check_pci_dev(bus, slot, func);

				if (func == 0) {
					type = read_pci_config_byte(bus, slot,
								    func,
							       PCI_HEADER_TYPE);
					if (!(type & 0x80))
						break;
				}
			}
		}
	}
}

static int __init intel_postcore_init(void)
{
	if (boot_cpu_data.x86_vendor != X86_VENDOR_INTEL)
		return 0;

	early_check_pci_devs();

	if (nr_ioh)
		printk(KERN_DEBUG "pci: found %d IOH\n", nr_ioh);

	return 0;
}
postcore_initcall(intel_postcore_init);

