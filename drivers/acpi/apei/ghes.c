/*
 * APEI Generic Hardware Error Source support
 *
 * Generic Hardware Error Source provides a way to report platform
 * hardware errors (such as that from chipset). It works in so called
 * "Firmware First" mode, that is, hardware errors are reported to
 * firmware firstly, then reported to Linux by firmware. This way,
 * some non-standard hardware error registers or non-standard hardware
 * link can be checked by firmware to produce more hardware error
 * information for Linux.
 *
 * For more information about Generic Hardware Error Source, please
 * refer to ACPI Specification version 4.0, section 17.3.2.6
 *
 * Copyright 2010 Intel Corp.
 *   Author: Huang Ying <ying.huang@intel.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version
 * 2 as published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/acpi.h>
#include <linux/io.h>
#include <linux/interrupt.h>
#include <linux/timer.h>
#include <linux/cper.h>
#include <linux/kdebug.h>
#include <linux/platform_device.h>
#include <linux/mutex.h>
#include <linux/vmalloc.h>
#include <linux/herror.h>
#include <acpi/apei.h>
#include <acpi/atomicio.h>
#include <acpi/hed.h>
#include <asm/mce.h>
#include <asm/tlbflush.h>

#include "apei-internal.h"

#define GHES_PFX	"GHES: "

#define GHES_ESTATUS_MAX_SIZE		65536

/*
 * One struct ghes is created for each generic hardware error source.
 * It provides the context for APEI hardware error timer/IRQ/SCI/NMI
 * handler.
 *
 * estatus: memory buffer for error status block, allocated during
 * HEST parsing.
 */
#define GHES_TO_CLEAR		0x0001
#define GHES_EXITING		0x0002

struct ghes {
	struct acpi_hest_generic *generic;
	struct acpi_hest_generic_status *estatus;
	u64 buffer_paddr;
	unsigned long flags;
	struct herr_dev *herr_dev;
	union {
		struct list_head list;
		struct timer_list timer;
		unsigned int irq;
	};
};

static int ghes_panic_timeout	__read_mostly = 30;

/*
 * All error sources notified with SCI shares one notifier function,
 * so they need to be linked and checked one by one.  This is applied
 * to NMI too.
 *
 * RCU is used for these lists, so ghes_list_mutex is only used only
 * for list changing, not for traversing.
 *
 * NMI may be triggered on any CPU, so ghes_nmi_lock is used for
 * mutual exclusion of ghest_nmi list.
 */
static LIST_HEAD(ghes_sci);
static LIST_HEAD(ghes_nmi);
static DEFINE_MUTEX(ghes_list_mutex);
static DEFINE_RAW_SPINLOCK(ghes_nmi_lock);

/*
 * Because the memory area used to transfer hardware error information
 * from BIOS to Linux can be determined only in NMI, IRQ or timer
 * handler, but general ioremap can not be used in atomic context, so
 * a special version of atomic ioremap is implemented for that.
 */

/* virtual memory area for atomic ioremap */
static struct vm_struct *ghes_ioremap_area;
/*
 * These 2 spinlock is used to prevent atomic ioremap virtual memory
 * area from being mapped simultaneously.
 */
static DEFINE_RAW_SPINLOCK(ghes_ioremap_lock_nmi);
static DEFINE_SPINLOCK(ghes_ioremap_lock_irq);

static int ghes_ioremap_init(void)
{
	ghes_ioremap_area = __get_vm_area(PAGE_SIZE * 2, VM_IOREMAP,
					  VMALLOC_START, VMALLOC_END);
	if (!ghes_ioremap_area) {
		pr_err(GHES_PFX
		"Failed to allocate virtual memory area for atomic ioremap.\n");
		return -ENOMEM;
	}

	return 0;
}

static void ghes_ioremap_exit(void)
{
	free_vm_area(ghes_ioremap_area);
}

static void *ghes_ioremap_pfn_nmi(u64 pfn)
{
	unsigned long vaddr;

	vaddr = (unsigned long)ghes_ioremap_area->addr;
	ioremap_page_range(vaddr, vaddr + PAGE_SIZE,
			   pfn << PAGE_SHIFT, PAGE_KERNEL);

	return (void *)vaddr;
}

static void *ghes_ioremap_pfn_irq(u64 pfn)
{
	unsigned long vaddr;

	vaddr = (unsigned long)ghes_ioremap_area->addr + PAGE_SIZE;
	ioremap_page_range(vaddr, vaddr + PAGE_SIZE,
			   pfn << PAGE_SHIFT, PAGE_KERNEL);

	return (void *)vaddr;
}

static void ghes_iounmap_nmi(void *vaddr)
{
	BUG_ON(vaddr != ghes_ioremap_area->addr);
	unmap_kernel_range_noflush((unsigned long)vaddr, PAGE_SIZE);
	__flush_tlb_one((unsigned long)vaddr);
}

static void ghes_iounmap_irq(void *vaddr)
{
	BUG_ON(vaddr != ghes_ioremap_area->addr + PAGE_SIZE);
	unmap_kernel_range_noflush((unsigned long)vaddr, PAGE_SIZE);
	__flush_tlb_one((unsigned long)vaddr);
}

static struct ghes *ghes_new(struct acpi_hest_generic *generic)
{
	struct ghes *ghes;
	unsigned int error_block_length;
	int rc;

	ghes = kzalloc(sizeof(*ghes), GFP_KERNEL);
	if (!ghes)
		return ERR_PTR(-ENOMEM);
	ghes->generic = generic;
	rc = acpi_pre_map_gar(&generic->error_status_address);
	if (rc)
		goto err_free;
	error_block_length = generic->error_block_length;
	if (error_block_length > GHES_ESTATUS_MAX_SIZE) {
		pr_warning(FW_WARN GHES_PFX
			   "Error status block length is too long: %u for "
			   "generic hardware error source: %d.\n",
			   error_block_length, generic->header.source_id);
		error_block_length = GHES_ESTATUS_MAX_SIZE;
	}
	ghes->estatus = kmalloc(error_block_length, GFP_KERNEL);
	if (!ghes->estatus) {
		rc = -ENOMEM;
		goto err_unmap;
	}

	return ghes;

err_unmap:
	acpi_post_unmap_gar(&generic->error_status_address);
err_free:
	kfree(ghes);
	return ERR_PTR(rc);
}

static void ghes_fini(struct ghes *ghes)
{
	kfree(ghes->estatus);
	acpi_post_unmap_gar(&ghes->generic->error_status_address);
}

enum {
	GHES_SEV_NO = 0x0,
	GHES_SEV_CORRECTED = 0x1,
	GHES_SEV_RECOVERABLE = 0x2,
	GHES_SEV_PANIC = 0x3,
};

static inline int ghes_severity(int severity)
{
	switch (severity) {
	case CPER_SEV_INFORMATIONAL:
		return GHES_SEV_NO;
	case CPER_SEV_CORRECTED:
		return GHES_SEV_CORRECTED;
	case CPER_SEV_RECOVERABLE:
		return GHES_SEV_RECOVERABLE;
	case CPER_SEV_FATAL:
		return GHES_SEV_PANIC;
	default:
		/* Unkown, go panic */
		return GHES_SEV_PANIC;
	}
}

static void ghes_copy_tofrom_phys(void *buffer, u64 paddr, u32 len,
				  int from_phys)
{
	void *vaddr;
	unsigned long flags = 0;
	int in_nmi = in_nmi();
	u64 offset;
	u32 trunk;

	while (len > 0) {
		offset = paddr - (paddr & PAGE_MASK);
		if (in_nmi) {
			raw_spin_lock(&ghes_ioremap_lock_nmi);
			vaddr = ghes_ioremap_pfn_nmi(paddr >> PAGE_SHIFT);
		} else {
			spin_lock_irqsave(&ghes_ioremap_lock_irq, flags);
			vaddr = ghes_ioremap_pfn_irq(paddr >> PAGE_SHIFT);
		}
		trunk = PAGE_SIZE - offset;
		trunk = min(trunk, len);
		if (from_phys)
			memcpy(buffer, vaddr + offset, trunk);
		else
			memcpy(vaddr + offset, buffer, trunk);
		len -= trunk;
		paddr += trunk;
		buffer += trunk;
		if (in_nmi) {
			ghes_iounmap_nmi(vaddr);
			raw_spin_unlock(&ghes_ioremap_lock_nmi);
		} else {
			ghes_iounmap_irq(vaddr);
			spin_unlock_irqrestore(&ghes_ioremap_lock_irq, flags);
		}
	}
}

static int ghes_read_estatus(struct ghes *ghes, int silent)
{
	struct acpi_hest_generic *g = ghes->generic;
	u64 buf_paddr;
	u32 len;
	int rc;

	rc = acpi_atomic_read(&buf_paddr, &g->error_status_address);
	if (rc) {
		if (!silent && printk_ratelimit())
			pr_warning(FW_WARN GHES_PFX
"Failed to read error status block address for hardware error source: %d.\n",
				   g->header.source_id);
		return -EIO;
	}
	if (!buf_paddr)
		return -ENOENT;

	ghes_copy_tofrom_phys(ghes->estatus, buf_paddr,
			      sizeof(*ghes->estatus), 1);
	if (!ghes->estatus->block_status)
		return -ENOENT;

	ghes->buffer_paddr = buf_paddr;
	ghes->flags |= GHES_TO_CLEAR;

	rc = -EIO;
	len = apei_estatus_len(ghes->estatus);
	if (len < sizeof(*ghes->estatus))
		goto err_read_block;
	if (len > ghes->generic->error_block_length)
		goto err_read_block;
	if (apei_estatus_check_header(ghes->estatus))
		goto err_read_block;
	ghes_copy_tofrom_phys(ghes->estatus + 1,
			      buf_paddr + sizeof(*ghes->estatus),
			      len - sizeof(*ghes->estatus), 1);
	if (apei_estatus_check(ghes->estatus))
		goto err_read_block;
	rc = 0;

err_read_block:
	if (rc && !silent && printk_ratelimit())
		pr_warning(FW_WARN GHES_PFX
			   "Failed to read error status block!\n");
	return rc;
}

static void ghes_clear_estatus(struct ghes *ghes)
{
	ghes->estatus->block_status = 0;
	if (!(ghes->flags & GHES_TO_CLEAR))
		return;
	ghes_copy_tofrom_phys(ghes->estatus, ghes->buffer_paddr,
			      sizeof(ghes->estatus->block_status), 0);
	ghes->flags &= ~GHES_TO_CLEAR;
}

static void ghes_report(struct ghes *ghes)
{
	struct herr_record *ercd;
	struct herr_section *esec;
	struct acpi_hest_generic_status *estatus;
	unsigned int estatus_len, ercd_alloc_flags = 0;
	int ghes_sev;

	ghes_sev = ghes_severity(ghes->estatus->error_severity);
	if (ghes_sev >= GHES_SEV_PANIC)
		ercd_alloc_flags |= HERR_ALLOC_NO_BURST_CONTROL;
	estatus_len = apei_estatus_len(ghes->estatus);
	ercd = herr_record_alloc(HERR_RECORD_LEN_ROUND1(estatus_len),
				 ghes->herr_dev, ercd_alloc_flags);
	if (!ercd)
		return;

	ercd->severity = cper_severity_to_herr(ghes->estatus->error_severity);

	esec = herr_first_sec(ercd);
	esec->length = HERR_SEC_LEN_ROUND(estatus_len);
	esec->flags = 0;
	esec->type = HERR_TYPE_GESR;

	estatus = herr_sec_data(esec);
	memcpy(estatus, ghes->estatus, estatus_len);
	herr_record_report(ercd, ghes->herr_dev);
}

static void ghes_do_proc(struct ghes *ghes)
{
	int sev;
	struct acpi_hest_generic_data *gdata;

	sev = ghes_severity(ghes->estatus->error_severity);
	apei_estatus_for_each_section(ghes->estatus, gdata) {
#ifdef CONFIG_X86_MCE
		if (!uuid_le_cmp(*(uuid_le *)gdata->section_type,
				 CPER_SEC_PLATFORM_MEM)) {
			apei_mce_report_mem_error(
				sev == GHES_SEV_CORRECTED,
				(struct cper_sec_mem_err *)(gdata+1));
		}
#endif
	}
}

static int ghes_proc(struct ghes *ghes)
{
	int rc;

	rc = ghes_read_estatus(ghes, 0);
	if (rc)
		goto out;
	ghes_report(ghes);
	ghes_do_proc(ghes);
	herr_notify();

out:
	ghes_clear_estatus(ghes);
	return 0;
}

static void ghes_add_timer(struct ghes *ghes)
{
	struct acpi_hest_generic *g = ghes->generic;
	unsigned long expire;

	if (!g->notify.poll_interval) {
		pr_warning(FW_WARN GHES_PFX "Poll interval is 0 for "
			   "generaic hardware error source: %d, disabled.",
			   g->header.source_id);
		return;
	}
	expire = jiffies + msecs_to_jiffies(g->notify.poll_interval);
	ghes->timer.expires = round_jiffies_relative(expire);
	add_timer(&ghes->timer);
}

static void ghes_poll_func(unsigned long data)
{
	struct ghes *ghes = (void *)data;

	ghes_proc(ghes);
	if (!(ghes->flags & GHES_EXITING))
		ghes_add_timer(ghes);
}

static irqreturn_t ghes_irq_func(int irq, void *data)
{
	struct ghes *ghes = data;
	int rc;

	rc = ghes_proc(ghes);
	if (rc)
		return IRQ_NONE;

	return IRQ_HANDLED;
}

static int ghes_notify_sci(struct notifier_block *this,
				  unsigned long event, void *data)
{
	struct ghes *ghes;
	int ret = NOTIFY_DONE;

	rcu_read_lock();
	list_for_each_entry_rcu(ghes, &ghes_sci, list) {
		if (!ghes_proc(ghes))
			ret = NOTIFY_OK;
	}
	rcu_read_unlock();

	return ret;
}

static int ghes_notify_nmi(struct notifier_block *this,
				  unsigned long cmd, void *data)
{
	struct ghes *ghes, *ghes_global = NULL;
	int sev, sev_global = -1;
	int ret = NOTIFY_DONE;

	if (cmd != DIE_NMI && cmd != DIE_NMI_IPI)
		return ret;

	raw_spin_lock(&ghes_nmi_lock);
	list_for_each_entry_rcu(ghes, &ghes_nmi, list) {
		if (ghes_read_estatus(ghes, 1)) {
			ghes_clear_estatus(ghes);
			continue;
		}
		ghes_report(ghes);
		sev = ghes_severity(ghes->estatus->error_severity);
		if (sev > sev_global) {
			sev_global = sev;
			ghes_global = ghes;
		}
		ret = NOTIFY_STOP;
	}

	if (ret == NOTIFY_DONE)
		goto out;

	if (sev_global >= GHES_SEV_PANIC) {
		herr_persist_all_records();
		oops_begin();
		/* reboot to log the error! */
		if (panic_timeout == 0)
			panic_timeout = ghes_panic_timeout;
		panic(GHES_PFX "generic hardware fatal error!\n");
	}

	list_for_each_entry_rcu(ghes, &ghes_nmi, list) {
		if (!(ghes->flags & GHES_TO_CLEAR))
			continue;
		ghes_do_proc(ghes);
		ghes_clear_estatus(ghes);
	}

out:
	raw_spin_unlock(&ghes_nmi_lock);
	return ret;
}

static struct notifier_block ghes_notifier_sci = {
	.notifier_call = ghes_notify_sci,
};

static struct notifier_block ghes_notifier_nmi = {
	.notifier_call = ghes_notify_nmi,
};

static int __devinit ghes_probe(struct platform_device *ghes_dev)
{
	struct acpi_hest_generic *generic;
	struct ghes *ghes = NULL;
	int rc;

	rc = -ENODEV;
	generic = *(struct acpi_hest_generic **)ghes_dev->dev.platform_data;
	if (!generic->enabled)
		goto err;

	switch (generic->notify.type) {
	case ACPI_HEST_NOTIFY_POLLED:
	case ACPI_HEST_NOTIFY_EXTERNAL:
	case ACPI_HEST_NOTIFY_SCI:
	case ACPI_HEST_NOTIFY_NMI:
		break;
	case ACPI_HEST_NOTIFY_LOCAL:
		pr_warning(GHES_PFX
"Generic hardware error source: %d notified via local interrupt is not supported!\n",
			   generic->header.source_id);
		goto err;
	default:
		pr_warning(FW_WARN GHES_PFX
"Unknown notification type: %u for generic hardware error source: %d\n",
			   generic->notify.type, generic->header.source_id);
		goto err;
	}

	rc = -EIO;
	if (generic->error_block_length <
	    sizeof(struct acpi_hest_generic_status)) {
		pr_warning(FW_BUG GHES_PFX
"Invalid error block length: %u for generic hardware error source: %d\n",
			   generic->error_block_length,
			   generic->header.source_id);
		goto err;
	}
	ghes = ghes_new(generic);
	if (IS_ERR(ghes)) {
		rc = PTR_ERR(ghes);
		ghes = NULL;
		goto err;
	}
	rc = -ENOMEM;
	ghes->herr_dev = herr_dev_alloc();
	if (!ghes->herr_dev)
		goto err;
	ghes->herr_dev->name = dev_name(&ghes_dev->dev);
	ghes->herr_dev->dev.parent = &ghes_dev->dev;
	rc = herr_dev_register(ghes->herr_dev);
	if (rc) {
		herr_dev_free(ghes->herr_dev);
		goto err;
	}
	switch (generic->notify.type) {
	case ACPI_HEST_NOTIFY_POLLED:
		init_timer(&ghes->timer);
		ghes->timer.function = ghes_poll_func;
		ghes->timer.data = (unsigned long)ghes;
		ghes_add_timer(ghes);
		break;
	case ACPI_HEST_NOTIFY_EXTERNAL:
		/* External interrupt vector is GSI */
		if (acpi_gsi_to_irq(generic->notify.vector, &ghes->irq)) {
			pr_err(GHES_PFX
	"Failed to map GSI to IRQ for generic hardware error source: %d\n",
			       generic->header.source_id);
			goto err_unreg;
		}
		if (request_irq(ghes->irq, ghes_irq_func,
				0, "GHES IRQ", ghes)) {
			pr_err(GHES_PFX
	"Failed to register IRQ for generic hardware error source: %d\n",
			       generic->header.source_id);
			goto err_unreg;
		}
		break;
	case ACPI_HEST_NOTIFY_SCI:
		mutex_lock(&ghes_list_mutex);
		if (list_empty(&ghes_sci))
			register_acpi_hed_notifier(&ghes_notifier_sci);
		list_add_rcu(&ghes->list, &ghes_sci);
		mutex_unlock(&ghes_list_mutex);
		break;
	case ACPI_HEST_NOTIFY_NMI:
		mutex_lock(&ghes_list_mutex);
		if (list_empty(&ghes_nmi))
			register_die_notifier(&ghes_notifier_nmi);
		list_add_rcu(&ghes->list, &ghes_nmi);
		mutex_unlock(&ghes_list_mutex);
		break;
	default:
		BUG();
	}
	platform_set_drvdata(ghes_dev, ghes);

	return 0;
err_unreg:
	herr_dev_unregister(ghes->herr_dev);
err:
	if (ghes) {
		ghes_fini(ghes);
		kfree(ghes);
	}
	return rc;
}

static int __devexit ghes_remove(struct platform_device *ghes_dev)
{
	struct ghes *ghes;
	struct acpi_hest_generic *generic;

	ghes = platform_get_drvdata(ghes_dev);
	generic = ghes->generic;

	ghes->flags |= GHES_EXITING;

	switch (generic->notify.type) {
	case ACPI_HEST_NOTIFY_POLLED:
		del_timer_sync(&ghes->timer);
		break;
	case ACPI_HEST_NOTIFY_EXTERNAL:
		free_irq(ghes->irq, ghes);
		break;
	case ACPI_HEST_NOTIFY_SCI:
		mutex_lock(&ghes_list_mutex);
		list_del_rcu(&ghes->list);
		if (list_empty(&ghes_sci))
			unregister_acpi_hed_notifier(&ghes_notifier_sci);
		mutex_unlock(&ghes_list_mutex);
		synchronize_rcu();
		break;
	case ACPI_HEST_NOTIFY_NMI:
		mutex_lock(&ghes_list_mutex);
		list_del_rcu(&ghes->list);
		if (list_empty(&ghes_nmi))
			unregister_die_notifier(&ghes_notifier_nmi);
		mutex_unlock(&ghes_list_mutex);
		synchronize_rcu();
		break;
	default:
		BUG();
		break;
	}

	herr_dev_unregister(ghes->herr_dev);
	ghes_fini(ghes);
	kfree(ghes);

	platform_set_drvdata(ghes_dev, NULL);

	return 0;
}

static struct platform_driver ghes_platform_driver = {
	.driver		= {
		.name	= "GHES",
		.owner	= THIS_MODULE,
	},
	.probe		= ghes_probe,
	.remove		= ghes_remove,
};

static int __init ghes_init(void)
{
	int rc;

	if (acpi_disabled)
		return -ENODEV;

	if (hest_disable) {
		pr_info(GHES_PFX "HEST is not enabled!\n");
		return -EINVAL;
	}

	rc = ghes_ioremap_init();
	if (rc)
		goto err;

	rc = platform_driver_register(&ghes_platform_driver);
	if (rc)
		goto err_ioremap_exit;

	return 0;
err_ioremap_exit:
	ghes_ioremap_exit();
err:
	return rc;
}

static void __exit ghes_exit(void)
{
	platform_driver_unregister(&ghes_platform_driver);
	ghes_ioremap_exit();
}

module_init(ghes_init);
module_exit(ghes_exit);

MODULE_AUTHOR("Huang Ying");
MODULE_DESCRIPTION("APEI Generic Hardware Error Source support");
MODULE_LICENSE("GPL");
MODULE_ALIAS("platform:GHES");
