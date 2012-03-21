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

/*
 * The encoder comes after the CRTC in the output pipeline, but before
 * the connector. It's responsible for ensuring that the digital
 * stream is appropriately converted into the output format. Setup is
 * very simple in this case - all we have to do is inform qemu of the
 * colour depth in order to ensure that it displays appropriately
 */

/*
 * These functions are analagous to those in the CRTC code, but are intended
 * to handle any encoder-specific limitations
 */
static bool cirrus_encoder_mode_fixup(struct drm_encoder *encoder,
				  struct drm_display_mode *mode,
				  struct drm_display_mode *adjusted_mode)
{
	return true;
}

static void cirrus_encoder_mode_set(struct drm_encoder *encoder,
				struct drm_display_mode *mode,
				struct drm_display_mode *adjusted_mode)
{
	struct drm_device *dev = encoder->dev;
	struct cirrus_device *cdev = dev->dev_private;

	unsigned char tmp;

	switch (encoder->crtc->fb->bits_per_pixel) {
	case 8:
		tmp = 0x0;
		break;
	case 16:
		/* Enable 16 bit mode */
		WREG_HDR(0x01);
		tmp = 0x6;
		break;
	case 24:
		tmp = 0x4;
		break;
	case 32:
		tmp = 0x8;
		break;
	default:
		return;
	}

	/* Enable packed pixel graphics modes */
	tmp |= 0x1;
	WREG_SEQ(0x7, tmp);

	/* Program the pitch */
	tmp = encoder->crtc->fb->pitches[0] / 8;
	WREG_CRT(VGA_CRTC_OFFSET, tmp);

	/* Enable extended blanking and pitch bits, and enable full memory */
	tmp = 0x22;
	if (encoder->crtc->fb->pitches[0] >= 2048)
		tmp |= 0x10;
	WREG_CRT(0x1b, tmp);

	/* Enable high-colour modes */
	WREG_GFX(VGA_GFX_MODE, 0x40);

	/* And set graphics mode */
	WREG_GFX(VGA_GFX_MISC, 0x01);
}

static void cirrus_encoder_dpms(struct drm_encoder *encoder, int state)
{
	return;
}

static void cirrus_encoder_prepare(struct drm_encoder *encoder)
{
}

static void cirrus_encoder_commit(struct drm_encoder *encoder)
{
}

void cirrus_encoder_destroy(struct drm_encoder *encoder)
{
	struct cirrus_encoder *cirrus_encoder = to_cirrus_encoder(encoder);
	drm_encoder_cleanup(encoder);
	kfree(cirrus_encoder);
}

static const struct drm_encoder_helper_funcs cirrus_encoder_helper_funcs = {
	.dpms = cirrus_encoder_dpms,
	.mode_fixup = cirrus_encoder_mode_fixup,
	.mode_set = cirrus_encoder_mode_set,
	.prepare = cirrus_encoder_prepare,
	.commit = cirrus_encoder_commit,
};

static const struct drm_encoder_funcs cirrus_encoder_encoder_funcs = {
	.destroy = cirrus_encoder_destroy,
};

struct drm_encoder *cirrus_encoder_init(struct drm_device *dev)
{
	struct drm_encoder *encoder;
	struct cirrus_encoder *cirrus_encoder;

	cirrus_encoder = kzalloc(sizeof(struct cirrus_encoder), GFP_KERNEL);
	if (!cirrus_encoder)
		return NULL;

	encoder = &cirrus_encoder->base;
	encoder->possible_crtcs = 0x1;

	drm_encoder_init(dev, encoder, &cirrus_encoder_encoder_funcs,
			 DRM_MODE_ENCODER_DAC);
	drm_encoder_helper_add(encoder, &cirrus_encoder_helper_funcs);

	return encoder;
}
