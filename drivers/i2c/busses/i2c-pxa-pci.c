/*
 * The CE4100's I2C device is more or less the same one as found on PXA.
 * It does not support slave mode, the register slightly moved. This PCI
 * device provides three bars, every contains a single I2C controller.
 */
#include <linux/pci.h>
#include <linux/platform_device.h>
#include <linux/i2c/pxa-i2c.h>
#include <linux/of.h>
#include <linux/of_device.h>
#include <linux/of_address.h>

#define CE4100_PCI_I2C_DEVS	3

struct ce4100_i2c_device {
	struct platform_device pdev;
	struct resource res[2];
	struct i2c_pxa_platform_data pdata;
};

struct ce4100_devices {
	struct ce4100_i2c_device sd[CE4100_PCI_I2C_DEVS];
};

static void plat_dev_release(struct device *dev)
{
	struct ce4100_i2c_device *sd = container_of(dev,
			struct ce4100_i2c_device, pdev.dev);

	of_device_node_put(&sd->pdev.dev);
}
static int add_i2c_device(struct pci_dev *dev, int bar,
		struct ce4100_i2c_device *sd)
{
	struct platform_device *pdev = &sd->pdev;
	struct i2c_pxa_platform_data *pdata = &sd->pdata;
	struct device_node *child;
	int found = 0;
	static int devnum;

	pdev->name = "ce4100-i2c";
	pdev->dev.release = plat_dev_release;
	pdev->dev.parent = &dev->dev;

	pdev->dev.platform_data = pdata;
	pdev->resource = sd->res;

	sd->res[0].flags = IORESOURCE_MEM;
	sd->res[0].start = pci_resource_start(dev, bar);
	sd->res[0].end = pci_resource_end(dev, bar);

	sd->res[1].flags = IORESOURCE_IRQ;
	sd->res[1].start = dev->irq;
	sd->res[1].end = dev->irq;
	pdev->num_resources = 2;

	for_each_child_of_node(dev->dev.of_node, child) {
		const void *prop;
		struct resource r;
		int ret;

		ret = of_address_to_resource(child, 0, &r);
		if (ret < 0)
			continue;
		if (r.start != sd->res[0].start)
			continue;
		if (r.end != sd->res[0].end)
			continue;
		if (r.flags != sd->res[0].flags)
			continue;

		pdev->dev.of_node = child;
		prop = of_get_property(child, "fast-mode", NULL);
		if (prop)
			pdata->fast_mode = 1;

		pdev->id = devnum++;
		found = 1;
		break;
	}

	if (found)
		return platform_device_register(pdev);

	dev_err(&dev->dev, "Missing a DT node at %s for controller bar %d.\n",
			dev->dev.of_node->full_name, bar);
	dev_err(&dev->dev, "Its memory space is 0x%08x - 0x%08x.\n",
			sd->res[0].start, sd->res[0].end);
	return -EINVAL;
}

static int __devinit ce4100_i2c_probe(struct pci_dev *dev,
		const struct pci_device_id *ent)
{
	int ret;
	int i;
	struct ce4100_devices *sds;

	ret = pci_enable_device_mem(dev);
	if (ret)
		return ret;

	if (!dev->dev.of_node) {
		dev_err(&dev->dev, "Missing device tree node.\n");
		return -EINVAL;
	}
	sds = kzalloc(sizeof(*sds), GFP_KERNEL);
	if (!sds)
		goto err_mem;

	pci_set_drvdata(dev, sds);

	for (i = 0; i < ARRAY_SIZE(sds->sd); i++) {
		ret = add_i2c_device(dev, i, &sds->sd[i]);
		if (ret) {
			while (--i >= 0)
				platform_device_unregister(&sds->sd[i].pdev);
			goto err_dev_add;
		}
	}
	return 0;

err_dev_add:
	pci_set_drvdata(dev, NULL);
	kfree(sds);
err_mem:
	pci_disable_device(dev);
	return ret;
}

static void __devexit ce4100_i2c_remove(struct pci_dev *dev)
{
	struct ce4100_devices *sds;
	unsigned int i;

	sds = pci_get_drvdata(dev);
	pci_set_drvdata(dev, NULL);

	for (i = 0; i < ARRAY_SIZE(sds->sd); i++)
		platform_device_unregister(&sds->sd[i].pdev);

	pci_disable_device(dev);
	kfree(sds);
}

static struct pci_device_id ce4100_i2c_devices[] __devinitdata = {
	{ PCI_DEVICE(PCI_VENDOR_ID_INTEL, 0x2e68)},
	{ },
};
MODULE_DEVICE_TABLE(pci, ce4100_i2c_devices);

static struct pci_driver ce4100_i2c_driver = {
	.name           = "ce4100_i2c",
	.id_table       = ce4100_i2c_devices,
	.probe          = ce4100_i2c_probe,
	.remove         = __devexit_p(ce4100_i2c_remove),
};

static int __init ce4100_i2c_init(void)
{
	return pci_register_driver(&ce4100_i2c_driver);
}
module_init(ce4100_i2c_init);

static void __exit ce4100_i2c_exit(void)
{
	pci_unregister_driver(&ce4100_i2c_driver);
}
module_exit(ce4100_i2c_exit);

MODULE_DESCRIPTION("CE4100 PCI-I2C glue code for PXA's driver");
MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("Sebastian Andrzej Siewior <bigeasy@linutronix.de>");
