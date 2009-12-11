/* ir-register.c - handle IR scancode->keycode tables
 *
 * Copyright (C) 2009 by Mauro Carvalho Chehab <mchehab@redhat.com>
 *
 * This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation version 2 of the License.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 */

int ir_sysfs_setup(void)
{
	int err = 0;
	struct sysdev_class *edac_class;

	debugf1("%s()\n", __func__);

	/* get the /sys/devices/system/edac class reference */
	edac_class = edac_get_edac_class();
	if (edac_class == NULL) {
		debugf1("%s() no edac_class error=%d\n", __func__, err);
		goto fail_out;
	}

	/* Init the MC's kobject */
	mc_kset = kset_create_and_add("mc", NULL, &edac_class->kset.kobj);
	if (!mc_kset) {
		err = -ENOMEM;
		debugf1("%s() Failed to register '.../edac/mc'\n", __func__);
		goto fail_out;
	}

	debugf1("%s() Registered '.../edac/mc' kobject\n", __func__);

	return 0;


	/* error unwind stack */
fail_out:
	return err;
}
