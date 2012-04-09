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

#include <video/cirrus.h>

#include "cirrus.h"
#include "cirrus_drv.h"
#include "cirrus_mode.h"

static int cirrus_vga_get_modes(struct drm_connector *connector)
{
	/* Just add a static list of modes */
	drm_add_modes_noedid(connector, 640, 480);
	drm_add_modes_noedid(connector, 800, 600);
	drm_add_modes_noedid(connector, 1024, 768);

	return 3;
}

static int cirrus_vga_mode_valid(struct drm_connector *connector,
				 struct drm_display_mode *mode)
{
	/* Any mode we've added is valid */
	return MODE_OK;
}

struct drm_encoder *cirrus_connector_best_encoder(struct drm_connector
						  *connector)
{
	int enc_id = connector->encoder_ids[0];
	struct drm_mode_object *obj;
	struct drm_encoder *encoder;

	/* pick the encoder ids */
	if (enc_id) {
		obj =
		    drm_mode_object_find(connector->dev, enc_id,
					 DRM_MODE_OBJECT_ENCODER);
		if (!obj)
			return NULL;
		encoder = obj_to_encoder(obj);
		return encoder;
	}
	return NULL;
}

static enum drm_connector_status cirrus_vga_detect(struct drm_connector
						   *connector, bool force)
{
	return connector_status_connected;
}

static void cirrus_connector_destroy(struct drm_connector *connector)
{
	drm_connector_cleanup(connector);
	kfree(connector);
}

struct drm_connector_helper_funcs cirrus_vga_connector_helper_funcs = {
	.get_modes = cirrus_vga_get_modes,
	.mode_valid = cirrus_vga_mode_valid,
	.best_encoder = cirrus_connector_best_encoder,
};

struct drm_connector_funcs cirrus_vga_connector_funcs = {
	.dpms = drm_helper_connector_dpms,
	.detect = cirrus_vga_detect,
	.fill_modes = drm_helper_probe_single_connector_modes,
	.destroy = cirrus_connector_destroy,
};

struct drm_connector *cirrus_vga_init(struct drm_device *dev)
{
	struct drm_connector *connector;
	struct cirrus_connector *cirrus_connector;

	cirrus_connector = kzalloc(sizeof(struct cirrus_connector), GFP_KERNEL);
	if (!cirrus_connector)
		return NULL;

	connector = &cirrus_connector->base;

	drm_connector_init(dev, connector,
			   &cirrus_vga_connector_funcs, DRM_MODE_CONNECTOR_VGA);

	drm_connector_helper_add(connector, &cirrus_vga_connector_helper_funcs);

	return connector;
}
