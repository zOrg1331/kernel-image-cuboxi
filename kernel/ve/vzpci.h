#include <linux/ve.h>
#include <linux/pci.h>

#ifdef CONFIG_VZ_PCI
int init_ve_sysfs_pci(struct ve_struct *ve);
void fini_ve_sysfs_pci(struct ve_struct *ve);
int ve_configure_move_pci_device(struct ve_struct *ve,
					unsigned int size, char *data);
#else
inline int init_ve_sysfs_pci(struct ve_struct *ve) { return 0; }
inline void fini_ve_sysfs_pci(struct ve_struct *ve) {}
inline int ve_configure_move_pci_device(struct ve_struct *ve,
					unsigned int size, char *data)
{
	return -ENOSYS;
}
#endif
