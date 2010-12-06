#include <linux/sched.h>
#include <linux/vzcalluser.h>

#include "vzpci.h"

static DECLARE_MUTEX(vz_pci_lock);
static LIST_HEAD(vz_pci_devices);

struct ve_pci_dev
{
	struct list_head list;
	struct pci_dev *dev;
	struct sysfs_dirent *sd;
	struct ve_struct *ve;
};

struct ve_pci_dev *ve_add_pci_device(struct pci_dev *dev, struct ve_struct *ve)
{
	struct ve_pci_dev *ve_dev, *tmp;

	down(&vz_pci_lock);
	list_for_each_entry_safe(ve_dev, tmp, &vz_pci_devices, list)
		if (ve_dev->dev == dev) {
			ve_dev = ERR_PTR(-EEXIST);
			goto out_unlock;
		}

	ve_dev = kzalloc(sizeof(struct ve_pci_dev), GFP_KERNEL);
	if (!ve_dev) {
		ve_dev = ERR_PTR(-ENOMEM);
		goto out_unlock;
	}

	ve_dev->dev = dev;
	ve_dev->ve = ve;
	ve_dev->sd = sysfs_create_dirlink(ve->pci_kobj->sd, &ve_dev->dev->dev.kobj);
	if (IS_ERR(ve_dev->sd)) {
		kfree(ve_dev);
		ve_dev = (struct ve_pci_dev *) ve_dev->sd;
		goto out_unlock;
	}

	list_add(&ve_dev->list, &vz_pci_devices);

out_unlock:
	if (IS_ERR(ve_dev))
		pci_dev_put(dev);
	up(&vz_pci_lock);

	return ve_dev;
}

static void ve_del_pci_device(struct ve_pci_dev *dev)
{
	sysfs_remove_dirlink(dev->sd);
	pci_dev_put(dev->dev);
}

int init_ve_sysfs_pci(struct ve_struct *ve)
{
	int ret = -ENOMEM;
	struct ve_struct *old_ve;
	struct kobject *bus_obj, *pci_obj;

	old_ve = set_exec_env(ve);
	bus_obj = kobject_create_and_add("bus", NULL);
	if (!bus_obj)
		goto out;

	pci_obj = kobject_create_and_add("pci", bus_obj);
	kobject_put(bus_obj);
	if (!pci_obj)
		goto out;

	ve->pci_kobj = kobject_create_and_add("devices", pci_obj);
	kobject_put(pci_obj);
	if (!ve->pci_kobj)
		goto out;

	ret = 0;
out:
	set_exec_env(old_ve);
	return ret;
}

void fini_ve_sysfs_pci(struct ve_struct *ve)
{
	struct ve_pci_dev *dev, *tmp;

	down(&vz_pci_lock);
	list_for_each_entry_safe(dev, tmp, &vz_pci_devices, list) {
		if (dev->ve != ve)
			continue;
		list_del(&dev->list);
		ve_del_pci_device(dev);	
	}
	kobject_put(ve->pci_kobj);
	up(&vz_pci_lock);
}

int ve_configure_move_pci_device(struct ve_struct *ve, \
					unsigned int size, char *data)
{
	struct vzctl_ve_pci_dev *dev_id;
	struct pci_dev *dev;
	struct pci_bus *bus;
	struct ve_pci_dev *ve_dev;

	if (size != sizeof(struct vzctl_ve_pci_dev))
		return -EINVAL;
	dev_id = (struct vzctl_ve_pci_dev *) data;

	bus = pci_find_bus(dev_id->domain, dev_id->bus);
	if (bus == NULL)
		return -ENOENT;
	dev = pci_get_slot(bus,	PCI_DEVFN(dev_id->slot, dev_id->func));
	if (dev == NULL)
		return -ENOENT;

	ve_dev = ve_add_pci_device(dev, ve);
	if (IS_ERR(ve_dev))
		return PTR_ERR(ve_dev);

	return 0;
}
