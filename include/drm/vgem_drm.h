/*
 * Copyright 2011 Red Hat, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software")
 * to deal in the software without restriction, including without limitation
 * on the rights to use, copy, modify, merge, publish, distribute, sub
 * license, and/or sell copies of the Software, and to permit persons to whom
 * them Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTIBILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#ifndef VGEM_DRM_H
#define VGEM_DRM_H

/* Bare API largely ripped off from exynos driver */

struct vgem_gem_create {
	unsigned int size;
	unsigned int flags;
	unsigned int handle;
};

struct vgem_gem_mmap {
	unsigned int handle;
	unsigned int size;
	uint64_t mapped;
};

struct vgem_gem_getparam {
#define VGEM_PARAM_IS_VGEM 1
	unsigned int param;
	unsigned int *value;
};

#define DRM_VGEM_GEM_CREATE	0x00
#define DRM_VGEM_GEM_MMAP	0x01
#define DRM_VGEM_GEM_GETPARAM	0x02

#define DRM_IOCTL_VGEM_GEM_CREATE \
		DRM_IOWR(DRM_COMMAND_BASE + DRM_VGEM_GEM_CREATE, \
			 struct vgem_gem_create)

#define DRM_IOCTL_VGEM_GEM_MMAP \
		DRM_IOWR(DRM_COMMAND_BASE + DRM_VGEM_GEM_MMAP, \
			 struct vgem_gem_mmap)

#define DRM_IOCTL_VGEM_GEM_GETPARAM \
		DRM_IOWR(DRM_COMMAND_BASE + DRM_VGEM_GEM_GETPARAM, \
			 struct vgem_gem_getparam)

#endif
