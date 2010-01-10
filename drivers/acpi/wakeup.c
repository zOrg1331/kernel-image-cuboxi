/*
 * wakeup.c - support wakeup devices
 * Copyright (C) 2004 Li Shaohua <shaohua.li@intel.com>
 */

#include <linux/init.h>
#include <linux/acpi.h>
#include <acpi/acpi_drivers.h>
#include <linux/kernel.h>
#include <linux/types.h>

#include "internal.h"
#include "sleep.h"

/*
 * We didn't lock acpi_device_lock in the file, because it invokes oops in
 * suspend/resume and isn't really required as this is called in S-state. At
 * that time, there is no device hotplug
 **/
#define _COMPONENT		ACPI_SYSTEM_COMPONENT
ACPI_MODULE_NAME("wakeup_devices")

/**
 * acpi_enable_wakeup_device_prep - prepare wakeup devices
 *	@sleep_state:	ACPI state
 * Enable all wakup devices power if the devices' wakeup level
 * is higher than requested sleep level
 */

void acpi_enable_wakeup_device_prep(u8 sleep_state)
{
	struct list_head *node, *next;

	list_for_each_safe(node, next, &acpi_wakeup_device_list) {
		struct acpi_device *dev = container_of(node,
						       struct acpi_device,
						       wakeup_list);

		if (!dev->wakeup.flags.valid ||
		    !dev->wakeup.state.enabled ||
		    (sleep_state > (u32) dev->wakeup.sleep_state))
			continue;

		acpi_enable_wakeup_device_power(dev, sleep_state);
	}
}

/**
 * acpi_enable_wakeup_device - enable wakeup devices
 *	@sleep_state:	ACPI state
 * Enable all wakup devices's GPE
 */
void acpi_enable_wakeup_device(u8 sleep_state)
{
	struct list_head *node, *next;

	/* 
	 * Caution: this routine must be invoked when interrupt is disabled 
	 * Refer ACPI2.0: P212
	 */
	list_for_each_safe(node, next, &acpi_wakeup_device_list) {
		struct acpi_device *dev =
			container_of(node, struct acpi_device, wakeup_list);

		if (!dev->wakeup.flags.valid ||
		    !dev->wakeup.prepare_count ||
		    !dev->wakeup.state.enabled ||
		    (sleep_state > (u32) dev->wakeup.sleep_state))
			continue;

		acpi_ref_wakeup_gpe(dev->wakeup.gpe_device,
				    dev->wakeup.gpe_number);
	}
}

/**
 * acpi_disable_wakeup_device - disable devices' wakeup capability
 *	@sleep_state:	ACPI state
 * Disable all wakup devices's GPE and wakeup capability
 */
void acpi_disable_wakeup_device(u8 sleep_state)
{
	struct list_head *node, *next;

	list_for_each_safe(node, next, &acpi_wakeup_device_list) {
		struct acpi_device *dev =
			container_of(node, struct acpi_device, wakeup_list);

		if (dev->wakeup.state.enabled &&
		    dev->wakeup.prepare_count &&
		    sleep_state <= (u32) dev->wakeup.sleep_state)
			acpi_unref_wakeup_gpe(dev->wakeup.gpe_device,
					    dev->wakeup.gpe_number);

		acpi_disable_wakeup_device_power(dev);
	}
}

int __init acpi_wakeup_device_init(void)
{
	struct list_head *node, *next;

	mutex_lock(&acpi_device_lock);
	list_for_each_safe(node, next, &acpi_wakeup_device_list) {
		struct acpi_device *dev = container_of(node,
						       struct acpi_device,
						       wakeup_list);
		/* In case user doesn't load button driver */
		if (!dev->wakeup.flags.run_wake || dev->wakeup.state.enabled)
			continue;
		acpi_ref_wakeup_gpe(dev->wakeup.gpe_device,
				    dev->wakeup.gpe_number);
		dev->wakeup.state.enabled = 1;
	}
	mutex_unlock(&acpi_device_lock);
	return 0;
}
