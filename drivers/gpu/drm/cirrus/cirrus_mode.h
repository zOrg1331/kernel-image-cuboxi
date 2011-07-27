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
#ifndef __CIRRUS_MODE_H__
#define __CIRRUS_MODE_H__

#include "drmP.h"
#include "drm.h"

#define CIRRUS_MAX_FB_HEIGHT 4096
#define CIRRUS_MAX_FB_WIDTH 4096

#define CIRRUS_DPMS_CLEARED (-1)

#define to_cirrus_crtc(x) container_of(x, struct cirrus_crtc, base)
#define to_cirrus_encoder(x) container_of(x, struct cirrus_encoder, base)
#define to_cirrus_framebuffer(x) container_of(x, struct cirrus_framebuffer, base)

struct cirrus_crtc {
	struct drm_crtc			base;
	u8				lut_r[256], lut_g[256], lut_b[256];
	int				last_dpms;
	bool				enabled;
};

struct cirrus_mode_info {
	bool				mode_config_initialized;
	struct cirrus_crtc		*crtc;
	/* pointer to fbdev info structure */
	struct cirrus_fbdev		*gfbdev;
};

struct cirrus_encoder {
	struct drm_encoder		base;
	int				last_dpms;
};

struct cirrus_connector {
	struct drm_connector		base;
};

struct cirrus_framebuffer {
	struct drm_framebuffer		base;
};

#endif				/* __CIRRUS_MODE_H__ */
