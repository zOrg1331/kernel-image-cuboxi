/*
 * Copyright 2010 Matt Turner.
 * Copyright 2011 Red Hat <mjg@redhat.com>
 *
 * This file is subject to the terms and conditions of the GNU General
 * Public License version 2. See the file COPYING in the main
 * directory of this archive for more details.
 *
 * Authors: Matthew Garrett
 *			Matt Turner
 */
#include "drmP.h"
#include "drm.h"
#include "drm_crtc_helper.h"

#include "cirrus.h"
#include "cirrus_drv.h"

/*
 * This file contains simple functions for initialising the driver
 */

int cirrus_modeset_init(struct cirrus_device *cdev)
{
	struct drm_encoder *encoder;
	struct drm_connector *connector;
	int ret;

	drm_mode_config_init(cdev->ddev);
	cdev->mode_info.mode_config_initialized = true;

	cdev->ddev->mode_config.max_width = CIRRUS_MAX_FB_WIDTH;
	cdev->ddev->mode_config.max_height = CIRRUS_MAX_FB_HEIGHT;

	cdev->ddev->mode_config.fb_base = cdev->mc.vram_base;

	cirrus_crtc_init(cdev->ddev);

	encoder = cirrus_encoder_init(cdev->ddev);
	if (!encoder) {
		CIRRUS_ERROR("cirrus_encoder_init failed\n");
		return -1;
	}

	connector = cirrus_vga_init(cdev->ddev);
	if (!connector) {
		CIRRUS_ERROR("cirrus_vga_init failed\n");
		return -1;
	}

	drm_mode_connector_attach_encoder(connector, encoder);

	ret = cirrus_fbdev_init(cdev);
	if (ret) {
		CIRRUS_ERROR("cirrus_fbdev_init failed\n");
		return ret;
	}

	return 0;
}

void cirrus_modeset_fini(struct cirrus_device *cdev)
{
	cirrus_fbdev_fini(cdev);

	if (cdev->mode_info.mode_config_initialized) {
		drm_mode_config_cleanup(cdev->ddev);
		cdev->mode_info.mode_config_initialized = false;
	}
}
