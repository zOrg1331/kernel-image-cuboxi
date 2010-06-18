#undef DEBUG

#include <linux/kernel.h>
#include <linux/string.h>
#include <linux/pci_regs.h>
#include <linux/module.h>
#include <linux/ioport.h>
#include <linux/etherdevice.h>
#include <linux/of_address.h>
#include <asm/prom.h>
#include <asm/pci-bridge.h>

#ifdef CONFIG_PCI
int of_irq_map_pci(struct pci_dev *pdev, struct of_irq *out_irq)
{
	struct device_node *dn, *ppnode;
	struct pci_dev *ppdev;
	u32 lspec;
	u32 laddr[3];
	u8 pin;
	int rc;

	/* Check if we have a device node, if yes, fallback to standard OF
	 * parsing
	 */
	dn = pci_device_to_OF_node(pdev);
	if (dn) {
		rc = of_irq_map_one(dn, 0, out_irq);
		if (!rc)
			return rc;
	}

	/* Ok, we don't, time to have fun. Let's start by building up an
	 * interrupt spec.  we assume #interrupt-cells is 1, which is standard
	 * for PCI. If you do different, then don't use that routine.
	 */
	rc = pci_read_config_byte(pdev, PCI_INTERRUPT_PIN, &pin);
	if (rc != 0)
		return rc;
	/* No pin, exit */
	if (pin == 0)
		return -ENODEV;

	/* Now we walk up the PCI tree */
	lspec = pin;
	for (;;) {
		/* Get the pci_dev of our parent */
		ppdev = pdev->bus->self;

		/* Ouch, it's a host bridge... */
		if (ppdev == NULL) {
#ifdef CONFIG_PPC64
			ppnode = pci_bus_to_OF_node(pdev->bus);
#else
			struct pci_controller *host;
			host = pci_bus_to_host(pdev->bus);
			ppnode = host ? host->dn : NULL;
#endif
			/* No node for host bridge ? give up */
			if (ppnode == NULL)
				return -EINVAL;
		} else
			/* We found a P2P bridge, check if it has a node */
			ppnode = pci_device_to_OF_node(ppdev);

		/* Ok, we have found a parent with a device-node, hand over to
		 * the OF parsing code.
		 * We build a unit address from the linux device to be used for
		 * resolution. Note that we use the linux bus number which may
		 * not match your firmware bus numbering.
		 * Fortunately, in most cases, interrupt-map-mask doesn't include
		 * the bus number as part of the matching.
		 * You should still be careful about that though if you intend
		 * to rely on this function (you ship  a firmware that doesn't
		 * create device nodes for all PCI devices).
		 */
		if (ppnode)
			break;

		/* We can only get here if we hit a P2P bridge with no node,
		 * let's do standard swizzling and try again
		 */
		lspec = pci_swizzle_interrupt_pin(pdev, lspec);
		pdev = ppdev;
	}

	laddr[0] = (pdev->bus->number << 16)
		| (pdev->devfn << 8);
	laddr[1]  = laddr[2] = 0;
	return of_irq_map_raw(ppnode, &lspec, 1, laddr, out_irq);
}
EXPORT_SYMBOL_GPL(of_irq_map_pci);
#endif /* CONFIG_PCI */

void of_parse_dma_window(struct device_node *dn, const void *dma_window_prop,
		unsigned long *busno, unsigned long *phys, unsigned long *size)
{
	const u32 *dma_window;
	u32 cells;
	const unsigned char *prop;

	dma_window = dma_window_prop;

	/* busno is always one cell */
	*busno = *(dma_window++);

	prop = of_get_property(dn, "ibm,#dma-address-cells", NULL);
	if (!prop)
		prop = of_get_property(dn, "#address-cells", NULL);

	cells = prop ? *(u32 *)prop : of_n_addr_cells(dn);
	*phys = of_read_number(dma_window, cells);

	dma_window += cells;

	prop = of_get_property(dn, "ibm,#dma-size-cells", NULL);
	cells = prop ? *(u32 *)prop : of_n_size_cells(dn);
	*size = of_read_number(dma_window, cells);
}

/*
 * Interrupt remapper
 */

static unsigned int of_irq_workarounds;
static struct device_node *of_irq_dflt_pic;

struct device_node *of_irq_find_parent_by_phandle(phandle p)
{
	if (of_irq_workarounds & OF_IMAP_NO_PHANDLE)
		return of_node_get(of_irq_dflt_pic);

	return of_find_node_by_phandle(p);
}

/* This doesn't need to be called if you don't have any special workaround
 * flags to pass
 */
void of_irq_map_init(unsigned int flags)
{
	of_irq_workarounds = flags;

	/* OldWorld, don't bother looking at other things */
	if (flags & OF_IMAP_OLDWORLD_MAC)
		return;

	/* If we don't have phandles, let's try to locate a default interrupt
	 * controller (happens when booting with BootX). We do a first match
	 * here, hopefully, that only ever happens on machines with one
	 * controller.
	 */
	if (flags & OF_IMAP_NO_PHANDLE) {
		struct device_node *np;

		for_each_node_with_property(np, "interrupt-controller") {
			/* Skip /chosen/interrupt-controller */
			if (strcmp(np->name, "chosen") == 0)
				continue;
			/* It seems like at least one person on this planet wants
			 * to use BootX on a machine with an AppleKiwi controller
			 * which happens to pretend to be an interrupt
			 * controller too.
			 */
			if (strcmp(np->name, "AppleKiwi") == 0)
				continue;
			/* I think we found one ! */
			of_irq_dflt_pic = np;
			break;
		}
	}

}

#if defined(CONFIG_PPC_PMAC) && defined(CONFIG_PPC32)
static int of_irq_map_oldworld(struct device_node *device, int index,
			       struct of_irq *out_irq)
{
	const u32 *ints = NULL;
	int intlen;

	/*
	 * Old machines just have a list of interrupt numbers
	 * and no interrupt-controller nodes. We also have dodgy
	 * cases where the APPL,interrupts property is completely
	 * missing behind pci-pci bridges and we have to get it
	 * from the parent (the bridge itself, as apple just wired
	 * everything together on these)
	 */
	while (device) {
		ints = of_get_property(device, "AAPL,interrupts", &intlen);
		if (ints != NULL)
			break;
		device = device->parent;
		if (device && strcmp(device->type, "pci") != 0)
			break;
	}
	if (ints == NULL)
		return -EINVAL;
	intlen /= sizeof(u32);

	if (index >= intlen)
		return -EINVAL;

	out_irq->controller = NULL;
	out_irq->specifier[0] = ints[index];
	out_irq->size = 1;

	return 0;
}
#else /* defined(CONFIG_PPC_PMAC) && defined(CONFIG_PPC32) */
static int of_irq_map_oldworld(struct device_node *device, int index,
			       struct of_irq *out_irq)
{
	return -EINVAL;
}
#endif /* !(defined(CONFIG_PPC_PMAC) && defined(CONFIG_PPC32)) */

int of_irq_map_one(struct device_node *device, int index, struct of_irq *out_irq)
{
	/* OldWorld mac stuff is "special", handle out of line */
	if (of_irq_workarounds & OF_IMAP_OLDWORLD_MAC)
		return of_irq_map_oldworld(device, index, out_irq);

	return __of_irq_map_one(device, index, out_irq);
}
EXPORT_SYMBOL_GPL(of_irq_map_one);

/**
 * Search the device tree for the best MAC address to use.  'mac-address' is
 * checked first, because that is supposed to contain to "most recent" MAC
 * address. If that isn't set, then 'local-mac-address' is checked next,
 * because that is the default address.  If that isn't set, then the obsolete
 * 'address' is checked, just in case we're using an old device tree.
 *
 * Note that the 'address' property is supposed to contain a virtual address of
 * the register set, but some DTS files have redefined that property to be the
 * MAC address.
 *
 * All-zero MAC addresses are rejected, because those could be properties that
 * exist in the device tree, but were not set by U-Boot.  For example, the
 * DTS could define 'mac-address' and 'local-mac-address', with zero MAC
 * addresses.  Some older U-Boots only initialized 'local-mac-address'.  In
 * this case, the real MAC is in 'local-mac-address', and 'mac-address' exists
 * but is all zeros.
*/
const void *of_get_mac_address(struct device_node *np)
{
	struct property *pp;

	pp = of_find_property(np, "mac-address", NULL);
	if (pp && (pp->length == 6) && is_valid_ether_addr(pp->value))
		return pp->value;

	pp = of_find_property(np, "local-mac-address", NULL);
	if (pp && (pp->length == 6) && is_valid_ether_addr(pp->value))
		return pp->value;

	pp = of_find_property(np, "address", NULL);
	if (pp && (pp->length == 6) && is_valid_ether_addr(pp->value))
		return pp->value;

	return NULL;
}
EXPORT_SYMBOL(of_get_mac_address);
