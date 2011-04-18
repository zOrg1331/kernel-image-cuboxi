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
#ifndef __CIRRUS_DRV_H__
#define __CIRRUS_DRV_H__

#include <video/vga.h>

#define DRIVER_AUTHOR		"Matthew Garrett"

#define DRIVER_NAME		"cirrus"
#define DRIVER_DESC		"qemu Cirrus emulation"
#define DRIVER_DATE		"20110418"

#define DRIVER_MAJOR		1
#define DRIVER_MINOR		0
#define DRIVER_PATCHLEVEL	0

#define CIRRUS_INFO(fmt, arg...) DRM_INFO(DRIVER_NAME ": " fmt, ##arg)
#define CIRRUS_ERROR(fmt, arg...) DRM_ERROR(DRIVER_NAME ": " fmt, ##arg)

#define CIRRUSFB_CONN_LIMIT 4

#define RREG8(reg) ioread8(((void __iomem *)cdev->rmmio) + (reg))
#define WREG8(reg, v) iowrite8(v, ((void __iomem *)cdev->rmmio) + (reg))
#define RREG32(reg) ioread32(((void __iomem *)cdev->rmmio) + (reg))
#define WREG32(reg, v) iowrite32(v, ((void __iomem *)cdev->rmmio) + (reg))

#define SEQ_INDEX 4
#define SEQ_DATA 5

#define WREG_SEQ(reg, v)					\
	do {							\
		WREG8(SEQ_INDEX, reg);				\
		WREG8(SEQ_DATA, v);				\
	} while (0)						\

#define CRT_INDEX 0x14
#define CRT_DATA 0x15

#define WREG_CRT(reg, v)					\
	do {							\
		WREG8(CRT_INDEX, reg);				\
		WREG8(CRT_DATA, v);				\
	} while (0)						\

#define GFX_INDEX 0xe
#define GFX_DATA 0xf

#define WREG_GFX(reg, v)					\
	do {							\
		WREG8(GFX_INDEX, reg);				\
		WREG8(GFX_DATA, v);				\
	} while (0)						\

/*
 * Cirrus has a "hidden" DAC register that can be accessed by writing to
 * the pixel mask register to reset the state, then reading from the register
 * four times. The next write will then pass to the DAC
 */
#define WREG_HDR(v)						\
	do {							\
		WREG8(0x6, 0xff);				\
		RREG8(0x6);					\
		RREG8(0x6);					\
		RREG8(0x6);					\
		RREG8(0x6);					\
		WREG8(0x6, v);					\
	} while (0)						\


#include "cirrus.h"

				/* cirrus_crtc.c */
void cirrus_crtc_fb_gamma_set(struct drm_crtc *crtc, u16 red, u16 green,
			     u16 blue, int regno);
void cirrus_crtc_fb_gamma_get(struct drm_crtc *crtc, u16 *red, u16 *green,
			     u16 *blue, int regno);
void cirrus_crtc_init(struct drm_device *dev);

				/* cirrus_encoder.c */
struct drm_encoder *cirrus_encoder_init(struct drm_device *dev);

				/* cirrus_device.c */
int cirrus_device_init(struct cirrus_device *cdev,
		      struct drm_device *ddev,
		      struct pci_dev *pdev,
		      uint32_t flags);
void cirrus_device_fini(struct cirrus_device *cdev);

				/* cirrus_display.c */
int cirrus_modeset_init(struct cirrus_device *cdev);
void cirrus_modeset_fini(struct cirrus_device *cdev);

				/* cirrus_fbdev.c */
int cirrus_fbdev_init(struct cirrus_device *cdev);
void cirrus_fbdev_fini(struct cirrus_device *cdev);

				/* cirrus_framebuffer.c */
int cirrus_framebuffer_init(struct drm_device *dev,
			   struct cirrus_framebuffer *gfb,
			   struct drm_mode_fb_cmd *mode_cmd);

				/* cirrus_irq.c */
void cirrus_driver_irq_preinstall(struct drm_device *dev);
int cirrus_driver_irq_postinstall(struct drm_device *dev);
void cirrus_driver_irq_uninstall(struct drm_device *dev);
irqreturn_t cirrus_driver_irq_handler(DRM_IRQ_ARGS);

				/* cirrus_kms.c */
int cirrus_driver_load(struct drm_device *dev, unsigned long flags);
int cirrus_driver_unload(struct drm_device *dev);
extern struct drm_ioctl_desc cirrus_ioctls[];
extern int cirrus_max_ioctl;

				/* cirrus_vga.c */
struct drm_connector *cirrus_vga_init(struct drm_device *dev);

#endif				/* __CIRRUS_DRV_H__ */
