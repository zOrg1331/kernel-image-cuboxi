
KDIR = /lib/modules/$(shell uname -r)/build
Conf1=${KDIR}/include/config/auto.conf
Conf2=${KDIR}/.config
ifeq "t" "$(shell test -e ${Conf1} && echo t)"
include ${Conf1}
else ifeq "t" "$(shell test -e ${Conf2} && echo t)"
include ${Conf2}
else
$(warning could not find kernel config file. internal auto-config may fail)
endif

CONFIG_AUFS_FS = m
AUFS_DEF_CONFIG = -DCONFIG_AUFS_MODULE -UCONFIG_AUFS
include config.mk

ccflags-y += -I${CURDIR}/include
ccflags-y += ${AUFS_DEF_CONFIG}
export ccflags-y

all: aufs.ko
aufs.ko: fs/aufs/aufs.ko
	ln -f $< $@
fs/aufs/aufs.ko:
	${MAKE} -C ${KDIR} M=${CURDIR}/fs/aufs modules
