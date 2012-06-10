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

static void cirrus_user_framebuffer_destroy(struct drm_framebuffer *fb)
{
	drm_framebuffer_cleanup(fb);
}

static int cirrus_user_framebuffer_create_handle(struct drm_framebuffer *fb,
						 struct drm_file *file_priv,
						 unsigned int *handle)
{
	return 0;
}

static const struct drm_framebuffer_funcs cirrus_fb_funcs = {
	.destroy = cirrus_user_framebuffer_destroy,
	.create_handle = cirrus_user_framebuffer_create_handle,
};

int cirrus_framebuffer_init(struct drm_device *dev,
			    struct cirrus_framebuffer *gfb,
			    struct drm_mode_fb_cmd *mode_cmd)
{
	int ret = drm_framebuffer_init(dev, &gfb->base, &cirrus_fb_funcs);
	if (ret) {
		CIRRUS_ERROR("drm_framebuffer_init failed: %d\n", ret);
		return ret;
	}
	drm_helper_mode_fill_fb_struct(&gfb->base, mode_cmd);

	return 0;
}
