################################################################################
#
# Intel PRO/1000 Linux driver
# Copyright(c) 1999 - 2008 Intel Corporation.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
#
# The full GNU General Public License is included in this distribution in
# the file called "COPYING".
#
# Contact Information:
# Linux NICS <linux.nics@intel.com>
# e1000-devel Mailing List <e1000-devel@lists.sourceforge.net>
# Intel Corporation, 5200 N.E. Elam Young Parkway, Hillsboro, OR 97124-6497
#
################################################################################

###########################################################################
# Driver files
FAMILYC = e1000_82540.c e1000_82542.c e1000_82571.c e1000_82541.c \
	  e1000_82543.c e1000_ich8lan.c e1000_80003es2lan.c
FAMILYH = e1000_82571.h e1000_82541.h e1000_82543.h e1000_ich8lan.h \
	  e1000_80003es2lan.h

# core driver files
CFILES = e1000_main.c $(FAMILYC) e1000_mac.c e1000_nvm.c e1000_phy.c \
	 e1000_manage.c e1000_param.c e1000_ethtool.c kcompat.c e1000_api.c
HFILES = e1000.h e1000_hw.h e1000_osdep.h e1000_defines.h e1000_mac.h \
	 e1000_nvm.h e1000_manage.h $(FAMILYH) kcompat.h e1000_regs.h \
	 e1000_api.h

DRIVER_NAME = e1000


#ARCH := $(shell uname -m | sed 's/i.86/i386/')
#ifeq ($(ARCH),alpha)
#  EXTRA_CFLAGS += -ffixed-8 -mno-fp-regs
#endif
#ifeq ($(ARCH),x86_64)
#  EXTRA_CFLAGS += -mcmodel=kernel -mno-red-zone
#endif
#ifeq ($(ARCH),ppc)
#  EXTRA_CFLAGS += -msoft-float
#endif
#ifeq ($(ARCH),ppc64)
#  EXTRA_CFLAGS += -m64 -msoft-float
#  LDFLAGS += -melf64ppc
#endif
#ifneq (,$(findstring NO_82542_SUPPORT, $(CFLAGS_EXTRA)))
#  CFILES := $(filter-out e1000_82542.c, $(CFILES))
#endif

# extra flags for module builds
#EXTRA_CFLAGS += -DDRIVER_$(shell echo $(DRIVER_NAME) | tr '[a-z]' '[A-Z]')
#EXTRA_CFLAGS += -DDRIVER_NAME=$(DRIVER_NAME)
#EXTRA_CFLAGS += -DDRIVER_NAME_CAPS=$(shell echo $(DRIVER_NAME) | tr '[a-z]' '[A-Z]')
# standard flags for module builds
#EXTRA_CFLAGS += -DLINUX -D__KERNEL__ -DMODULE -O2 -pipe -Wall
#EXTRA_CFLAGS += -I$(KSRC)/include -I.
#EXTRA_CFLAGS += $(shell [ -f $(KSRC)/include/linux/modversions.h ] && \
#            echo "-DMODVERSIONS -DEXPORT_SYMTAB \
#                  -include $(KSRC)/include/linux/modversions.h")

#EXTRA_CFLAGS += $(CFLAGS_EXTRA)



# Makefile for 2.6.x kernel
obj-$(CONFIG_E1000) += e1000.o

e1000-objs :  e1000_main.o e1000_82540.o e1000_82542.o e1000_82571.o e1000_82541.o \
	e1000_82543.o e1000_ich8lan.o e1000_80003es2lan.o e1000_mac.o e1000_nvm.o e1000_phy.o \
	 e1000_manage.o e1000_param.o e1000_ethtool.o kcompat.o e1000_api.o
