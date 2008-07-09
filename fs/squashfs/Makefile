#
# Makefile for the linux squashfs routines.
#

-include /tmp/sqvars.mk

obj-$(CONFIG_SQUASHFS_LZMA) += unlzma.o sqlzma.o
unlzma-y := module.o
sqlzma-y := uncomp.o
obj-$(CONFIG_SQUASHFS) += squashfs.o

ifdef CONFIG_SQUASHFS_LZMA
	squashfs-y += unlzma.o sqlzma.o
endif

squashfs-y += inode.o
squashfs-y += squashfs2_0.o
