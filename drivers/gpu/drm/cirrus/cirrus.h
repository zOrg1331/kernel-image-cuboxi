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
#ifndef __CIRRUS_H__
#define __CIRRUS_H__

#include "cirrus_mode.h"

struct cirrus_mc {
	resource_size_t			vram_size;
	resource_size_t			vram_base;
};

struct cirrus_device {
	struct device			*dev;
	struct drm_device		*ddev;
	struct pci_dev			*pdev;
	unsigned long			flags;

	resource_size_t			rmmio_base;
	resource_size_t			rmmio_size;
	void __iomem			*rmmio;

	drm_local_map_t			*framebuffer;

	struct cirrus_mc			mc;
	struct cirrus_mode_info		mode_info;

	int				num_crtc;
};

#endif				/* __CIRRUS_H__ */
