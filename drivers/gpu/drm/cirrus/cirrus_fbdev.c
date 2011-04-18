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
#include "drm_fb_helper.h"

#include <linux/fb.h>

#include "cirrus.h"
#include "cirrus_drv.h"

struct cirrus_fbdev {
	struct drm_fb_helper helper;
	struct cirrus_framebuffer gfb;
	struct list_head fbdev_list;
	struct cirrus_device *cdev;
};

static struct fb_ops cirrusfb_ops = {
	.owner = THIS_MODULE,
	.fb_check_var = drm_fb_helper_check_var,
	.fb_set_par = drm_fb_helper_set_par,
	.fb_fillrect = cfb_fillrect,
	.fb_copyarea = cfb_copyarea,
	.fb_imageblit = cfb_imageblit,
	.fb_pan_display = drm_fb_helper_pan_display,
	.fb_blank = drm_fb_helper_blank,
	.fb_setcmap = drm_fb_helper_setcmap,
};

static int cirrusfb_create(struct cirrus_fbdev *gfbdev,
			   struct drm_fb_helper_surface_size *sizes)
{
	struct cirrus_device *cdev = gfbdev->cdev;
	struct fb_info *info;
	struct drm_framebuffer *fb;
	struct drm_map_list *r_list, *list_t;
	struct drm_local_map *map = NULL;
	struct drm_mode_fb_cmd mode_cmd;
	struct device *device = &cdev->pdev->dev;
	int ret;

	mode_cmd.width = sizes->surface_width;
	mode_cmd.height = sizes->surface_height;
	mode_cmd.bpp = sizes->surface_bpp;
	mode_cmd.depth = sizes->surface_depth;
	mode_cmd.pitch = mode_cmd.width * ((mode_cmd.bpp + 7) / 8);

	info = framebuffer_alloc(0, device);
	if (info == NULL)
		return -ENOMEM;

	info->par = gfbdev;

	ret = cirrus_framebuffer_init(cdev->ddev, &gfbdev->gfb, &mode_cmd);
	if (ret)
		return ret;

	fb = &gfbdev->gfb.base;
	if (!fb) {
		CIRRUS_INFO("fb is NULL\n");
		return -EINVAL;
	}

	/* setup helper */
	gfbdev->helper.fb = fb;
	gfbdev->helper.fbdev = info;

	strcpy(info->fix.id, "cirrusdrmfb");

	drm_fb_helper_fill_fix(info, fb->pitch, fb->depth);

	info->flags = FBINFO_DEFAULT;
	info->fbops = &cirrusfb_ops;

	drm_fb_helper_fill_var(info, &gfbdev->helper, sizes->fb_width,
			       sizes->fb_height);

	/* setup aperture base/size for vesafb takeover */
	info->apertures = alloc_apertures(1);
	if (!info->apertures) {
		ret = -ENOMEM;
		goto out_iounmap;
	}
	info->apertures->ranges[0].base = cdev->ddev->mode_config.fb_base;
	info->apertures->ranges[0].size = cdev->mc.vram_size;

	list_for_each_entry_safe(r_list, list_t, &cdev->ddev->maplist, head) {
		map = r_list->map;
		if (map->type == _DRM_FRAME_BUFFER) {
			map->handle = ioremap_nocache(map->offset, map->size);
			if (!map->handle) {
				CIRRUS_ERROR("fb: can't remap framebuffer\n");
				return -1;
			}
			break;
		}
	}

	info->fix.smem_start = map->offset;
	info->fix.smem_len = map->size;
	if (!info->fix.smem_len) {
		CIRRUS_ERROR("%s: can't count memory\n", info->fix.id);
		goto out_iounmap;
	}
	info->screen_base = map->handle;
	if (!info->screen_base) {
		CIRRUS_ERROR("%s: can't remap framebuffer\n", info->fix.id);
		goto out_iounmap;
	}

	info->fix.mmio_start = 0;
	info->fix.mmio_len = 0;

	ret = fb_alloc_cmap(&info->cmap, 256, 0);
	if (ret) {
		CIRRUS_ERROR("%s: can't allocate color map\n", info->fix.id);
		ret = -ENOMEM;
		goto out_iounmap;
	}

	return 0;
out_iounmap:
	iounmap(map->handle);
	return ret;
}

static int cirrus_fb_find_or_create_single(struct drm_fb_helper *helper,
					   struct drm_fb_helper_surface_size
					   *sizes)
{
	struct cirrus_fbdev *gfbdev = (struct cirrus_fbdev *)helper;
	int new_fb = 0;
	int ret;

	if (!helper->fb) {
		ret = cirrusfb_create(gfbdev, sizes);
		if (ret)
			return ret;
		new_fb = 1;
	}
	return new_fb;
}

static int cirrus_fbdev_destroy(struct drm_device *dev,
				struct cirrus_fbdev *gfbdev)
{
	struct fb_info *info;
	struct cirrus_framebuffer *gfb = &gfbdev->gfb;

	if (gfbdev->helper.fbdev) {
		info = gfbdev->helper.fbdev;

		unregister_framebuffer(info);
		if (info->cmap.len)
			fb_dealloc_cmap(&info->cmap);
		framebuffer_release(info);
	}

	drm_fb_helper_fini(&gfbdev->helper);
	drm_framebuffer_cleanup(&gfb->base);

	return 0;
}

static struct drm_fb_helper_funcs cirrus_fb_helper_funcs = {
	.gamma_set = cirrus_crtc_fb_gamma_set,
	.gamma_get = cirrus_crtc_fb_gamma_get,
	.fb_probe = cirrus_fb_find_or_create_single,
};

int cirrus_fbdev_init(struct cirrus_device *cdev)
{
	struct cirrus_fbdev *gfbdev;
	int ret;

	gfbdev = kzalloc(sizeof(struct cirrus_fbdev), GFP_KERNEL);
	if (!gfbdev)
		return -ENOMEM;

	gfbdev->cdev = cdev;
	cdev->mode_info.gfbdev = gfbdev;
	gfbdev->helper.funcs = &cirrus_fb_helper_funcs;

	ret = drm_fb_helper_init(cdev->ddev, &gfbdev->helper,
				 cdev->num_crtc, CIRRUSFB_CONN_LIMIT);
	if (ret) {
		kfree(gfbdev);
		return ret;
	}
	drm_fb_helper_single_add_all_connectors(&gfbdev->helper);
	drm_fb_helper_initial_config(&gfbdev->helper, 24);

	return 0;
}

void cirrus_fbdev_fini(struct cirrus_device *cdev)
{
	if (!cdev->mode_info.gfbdev)
		return;

	cirrus_fbdev_destroy(cdev->ddev, cdev->mode_info.gfbdev);
	kfree(cdev->mode_info.gfbdev);
	cdev->mode_info.gfbdev = NULL;
}
