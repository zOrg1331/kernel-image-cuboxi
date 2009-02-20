
# Kconfig
# instead of setting 'n', leave it blank when you disable it.
CONFIG_AUFS_BRANCH_MAX_127 = y
CONFIG_AUFS_BRANCH_MAX_511 =
CONFIG_AUFS_BRANCH_MAX_1023 =
#CONFIG_AUFS_BRANCH_MAX_32767 =
CONFIG_AUFS_HINOTIFY =
CONFIG_AUFS_DEBUG = y
CONFIG_AUFS_MAGIC_SYSRQ =
CONFIG_AUFS_BDEV_LOOP =

########################################

define conf
ifdef $(1)
AUFS_DEF_CONFIG += -D$(1)
endif
endef

$(foreach i, BRANCH_MAX_127 BRANCH_MAX_511 BRANCH_MAX_1023 \
	BRANCH_MAX_32767 \
	HINOTIFY  \
	DEBUG MAGIC_SYSRQ \
	BDEV_LOOP, \
	$(eval $(call conf,CONFIG_AUFS_$(i))))
