%set_verify_elf_skiplist /boot/*
%set_strip_skiplist /boot/*

%define with_doc       0
%define with_headers   1
%define with_openafs   0
%define ovzver 028stab070
%define ovzrel 7

# Whether to apply the Xen patches -- leave this enabled.
%define includexen 1
%define includeovz 1

%define openafs_version 1.4.6

# Versions of various parts

# After branching, please hardcode these values as the
# %%dist and %%rhel tags are not reliable yet
# For example dist -> .el5 and rhel -> 5
%define dist .el5
%define rhel 5

# Values used for RHEL version info in version.h
%define rh_release_major %rhel
%define rh_release_minor 5

# Build options
# You can change compiler version by editing this line:
%define kgcc_version	4.1
%set_gcc_version %kgcc_version

#
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456"
#
%define sublevel 18
%define kversion 2.6.%sublevel
%define krelease alt13.M51.15
%define xen_hv_cset 15502

%define flavour         %( s='%name'; printf %%s "${s#kernel-image-}" )
%define kheaders_dir    %_prefix/include/linux-%kversion-%flavour
%define kbuild_dir      %_prefix/src/linux-%kversion-%flavour-%krelease
%define old_kbuild_dir  %_prefix/src/linux-%kversion-%flavour
%define modules_dir     /lib/modules/%kversion-%flavour-%krelease
%define KVERREL         %kversion-%flavour-%krelease
%define kernel_config kernel-%kversion-%_arch.config.ovz

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp <= 2.3.15, pcmcia-cs <= 3.1.20, isdn4k-utils <= 3.0, mount < 2.10r-5, nfs-utils < 1.0.3, e2fsprogs < 1.29, util-linux < 2.10, jfsutils < 1.0.14, reiserfsprogs < 3.6.3, xfsprogs < 2.1.0, procps < 2.0.9, oprofile < 0.5.3

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts cipe < 1.4.5, tux < 2.1.0, kudzu <= 0.92, dev < 3.2-7, iptables < 1.2.5-3, bcm5820 < 1.81, nvidia-rh72 <= 1.0

Packager: Kernel Maintainers Team <kernel@packages.altlinux.org>
Name: kernel-image-ovz-rhel
Group: System/Kernel and hardware
Summary: Virtuozzo Linux kernel (the core of the Linux operating system)
License: GPLv2
Url: http://www.kernel.org/
Version: %kversion
Release: %krelease
ExclusiveArch: i586 x86_64
ExclusiveOS: Linux
Provides: kernel = %version
Provides: kernel-drm = 4.3.0
Provides: kernel-%_target_cpu = %kversion-%flavour-%krelease
Provides: vzkernel = %KVERREL
Provides: vzquotamod
Provides: alsa = 1.0.14

BuildRequires: kernel-source-%kversion
BuildRequires(pre): rpm-build-kernel
PreReq: coreutils, module-init-tools, mkinitrd
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts

Requires: bootloader-utils >= 0.3-alt1
Requires: module-init-tools >= 3.1
Requires: mkinitrd >= 1:2.9.9-alt1
Requires: startup >= 0.8.3-alt1

# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

#
# List the packages used during the kernel build
#
BuildPreReq: module-init-tools, patch >= 2.5.4, bash >= 2.03, coreutils, tar
BuildPreReq: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils
BuildRequires: binutils >= 2.12
%if %with_headers
BuildRequires: unifdef
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
BuildPreReq: python-modules

Source1: xen-%xen_hv_cset.tar
Source2: Config.mk
%if %with_openafs
Source3: openafs-%openafs_version-src.tar.bz2
%endif

%if %{!?_without_source:0}%{?_without_source:1}
NoSource: 0
%endif

Source10: COPYING.modules
Source11: genkey
Source12: kabitool
Source14: find-provides
Source15: merge.pl
Source16: make_debug_config.sh

Source100: kabi_whitelist_i686
Source101: kabi_whitelist_i686PAE
Source102: kabi_whitelist_i686xen
Source103: kabi_whitelist_ia64
Source104: kabi_whitelist_ia64xen
Source105: kabi_whitelist_ppc64
Source106: kabi_whitelist_ppc64kdump
#Source107: kabi_whitelist_ppc64iseries
#Source108: kabi_whitelist_ppc64iserieskdump
Source109: kabi_whitelist_s390x
Source110: kabi_whitelist_x86_64
Source111: kabi_whitelist_x86_64xen

Source120: Module.kabi_i686
Source121: Module.kabi_i686PAE
Source122: Module.kabi_i686xen
Source123: Module.kabi_ia64
#Source124: Module.kabi_ia64xen
Source125: Module.kabi_ppc64
Source126: Module.kabi_ppc64kdump
Source127: Module.kabi_s390x
Source128: Module.kabi_x86_64
Source129: Module.kabi_x86_64xen

Source130: check-kabi

Source200: kernel-%kversion-i586.config.ovz
Source201: kernel-%kversion-i686-PAE.config.ovz
Source202: kernel-%kversion-i686-ent.config.ovz
Source203: kernel-%kversion-x86_64.config.ovz
Source204: kernel-%kversion-ia64.config.ovz
Source205: kernel-%kversion-ppc64.config.ovz
Source206: kernel-%kversion-i686-xen.config.ovz
Source207: kernel-%kversion-x86_64-xen.config.ovz

#
# Patches 0 through 100 are meant for core subsystem upgrades
#
Patch1: patch-2.6.18.4
#Patch2: patch-2.6.18-rc7-git4.bz2
Patch3: git-geode.patch
Patch4: git-agpgart.patch

# this is for patches we backported the whole fix for later in spec file
# currently just the bcm43xx driver and infiniband stuff
Patch9: stable-patch-reverts.patch

# Patches 10 through 99 are for things that are going upstream really soon.
Patch10: linux-2.6-utrace.patch

# enable sysrq-c on all kernels, not only kexec
Patch20: linux-2.6-sysrq-c.patch
Patch21: linux-2.6-sysrq-w.patch

# Patches 100 through 500 are meant for architecture patches

# 200 - 299   x86(-64)

Patch200: linux-2.6-x86-tune-generic.patch
Patch201: linux-2.6-x86-vga-vidfail.patch
Patch202: linux-2.6-x86-64-edac-support.patch
Patch203: linux-2.6-x86_64-silence-up-apic-errors.patch
Patch207: linux-2.6-x86_64-tif-restore-sigmask.patch
Patch208: linux-2.6-x86_64-add-ppoll-pselect.patch
Patch209: linux-2.6-x86_64-opterons-synchronize-p-state-using-TSC.patch
Patch210: linux-2.6-x86_64-memory-hotplug.patch
Patch211: linux-2.6-x86-relocatable.patch
Patch212: linux-2.6-x86-support-rdtscp-for-gtod.patch
Patch213: linux-2.6-x86-unwinder-fixes.patch
#temp patch for now
Patch214: linux-2.6-x86-disable-mmconfig.patch
Patch215: linux-2.6-x86_64-page-align-e820-area.patch
Patch216: linux-2.6-x86_64-dirty-page-tracking.patch

# 300 - 399   ppc(64)
Patch302: linux-2.6-hvc-console.patch
Patch303: linux-2.6-ppc-rtas-check.patch
Patch304: linux-2.6-ppc64-export-copypage.patch
Patch306: linux-2.6-powerpc-audit.patch
Patch307: linux-2.6-powerpc-seccomp.patch
Patch308: linux-2.6-powerpc-power6-disable-ci_large_page.patch

# 400 - 499   ia64
Patch400: linux-2.6-ia64-futex.patch
Patch401: linux-2.6-ia64-robust-list.patch
Patch402: linux-2.6-ia64-kexec-kdump.patch
Patch404: linux-2.6-ia64-exports-for-xpmem-driver.patch
Patch405: linux-2.6-ia64-kprobes-fixes.patch

# 500 - 599   s390(x)
Patch500: linux-2.6-s390-kprobes.patch
Patch501: linux-2.6-s390-add-uevent-to-ccw.patch
Patch502: linux-2.6-s390-kprobes-fixes.patch
Patch503: linux-2.6-s390-net-ctcmpc-driver.patch

# 600 - 699   sparc(64)

#
# Patches 800 through 899 are reserved for bugfixes to the core system
# and patches related to how RPMs are build
#
Patch800: linux-2.6-build-nonintconfig.patch
Patch801: linux-2.6-build-userspace-headers-warning.patch
Patch802: linux-2.6-build-deprecate-configh-include.patch

# Exec-shield.
Patch810: linux-2.6-execshield.patch
Patch811: linux-2.6-warn-c-p-a.patch

# Module signing infrastructure.
Patch900: linux-2.6-modsign-core.patch
Patch901: linux-2.6-modsign-crypto.patch
Patch902: linux-2.6-modsign-ksign.patch
Patch903: linux-2.6-modsign-mpilib.patch
Patch904: linux-2.6-modsign-script.patch
Patch905: linux-2.6-modsign-include.patch

# Tux http accelerator.
Patch910: linux-2.6-tux.patch

# 950 - 999 Xen
Patch950: linux-2.6-xen.patch
Patch951: linux-2.6-xen-utrace.patch
Patch952: linux-2.6-xen-x86_64-silence-up-apic-errors.patch
Patch953: linux-2.6-xen-x86_64-add-ppoll-pselect.patch
Patch954: linux-2.6-xen-execshield.patch
Patch955: linux-2.6-xen-tux.patch
Patch957: linux-2.6-xen-x86-relocatable.patch
Patch958: linux-2.6-ia64-kexec-kdump-xen-conflict.patch
Patch959: linux-2.6-xen-x86-unwinder.patch
Patch960: linux-2.6-xen-blktap-fixes.patch
Patch961: linux-2.6-xen-pae-handle-64bit-addresses-correctly.patch
Patch962: linux-2.6-xen-remove-bug-from-evtchn-during-retrigger.patch

#
# Patches 1000 to 5000 are reserved for bugfixes to drivers and filesystems
#

Patch1010: linux-2.6-debug-sizeof-structs.patch
Patch1011: linux-2.6-debug-slab-backtrace.patch
Patch1012: linux-2.6-debug-list_head.patch
Patch1013: linux-2.6-debug-taint-vm.patch
Patch1014: linux-2.6-debug-singlebiterror.patch
Patch1015: linux-2.6-debug-spinlock-taint.patch
Patch1016: linux-2.6-debug-Wundef.patch
Patch1017: linux-2.6-debug-disable-builtins.patch
Patch1018: linux-2.6-debug-sleep-in-irq-warning.patch
Patch1019: linux-2.6-debug-must_check.patch
Patch1020: linux-2.6-debug-no-quiet.patch
Patch1021: linux-2.6-debug-boot-delay.patch
Patch1022: linux-2.6-debug-sysfs-crash-debugging.patch
Patch1023: linux-2.6-debug-sysfs-crash-debugging-xen.patch

# Restrict /dev/mem usage.
Patch1050: linux-2.6-devmem.patch
Patch1051: linux-2.6-devmem-xen.patch

# Provide read only /dev/crash driver.
Patch1060: linux-2.6-crash-driver.patch
Patch1061: linux-2.6-crash-driver-xen.patch

Patch1070: linux-2.6-sleepon.patch

# SCSI bits.
Patch1102: linux-2.6-scsi-advansys-pcitable.patch
Patch1103: linux-2.6-iscsi-add-qla4xxx2.patch
Patch1104: linux-2.6-iscsi-update-to-2-6-19-rc1.upstream.patch
Patch1105: linux-2.6-aic9400-adp94xx-updates.patch
Patch1106: linux-2.6-scsi-ipr-supports-sas-attached-sata.patch
Patch1107: linux-2.6-scsi-dont-add-devices-for-pq1-pdt01f.patch
Patch1108: linux-2.6-scsi-remove-userspace-hooks-from-qla4xxx.patch
Patch1109: linux-2.6-scsi-allow-cat-proc-scsi-to-work.patch
Patch1110: linux-2.6-scsi-add-qla3xxx.patch
Patch1111: linux-2.6-scsi-update-blacklist.patch
Patch1112: linux-2.6-iscsi-remove-old-code.patch
Patch1113: linux-2.6-scsi-fix-shared-tag-maps.patch
Patch1114: linux-2.6-scsi-add-promise-stex-driver.patch
Patch1115: linux-2.6-scsi-sg-allow-large-page-sizes.patch
Patch1116: linux-2.6-scsi-qla4xxx-ioctl-hooks.patch
Patch1117: linux-2.6-scsi-update-transport-fc.patch
Patch1118: linux-2.6-scsi-update-emulex-lpfc.patch
Patch1119: linux-2.6-scsi-emulex-ioctl-hooks.patch
Patch1120: linux-2.6-scsi-update-lsi-megaraid.patch
Patch1121: linux-2.6-scsi-ibmvscsi-migration-fix.patch

# NFS bits.
Patch1200: linux-2.6-NFSD-ctlbits.patch
Patch1201: linux-2.6-NFSD-badness.patch

# core networking changes.
Patch1300: linux-2.6-net-ipsec-labelling.patch
Patch1301: linux-2.6-net-netlabel-cipso.patch
Patch1302: linux-2.6-net-netlabel-labeled-network-support.patch
Patch1303: linux-2.6-net-netlabel-audit-config-changes.patch
Patch1304: linux-2.6-net-netlabel-oops-in-cache.patch
Patch1305: linux-2.6-net-netlabel-label-empty-packets-unlabeled.patch
Patch1306: linux-2.6-net-netlabel-fix-ipsec-leak.patch

# Network driver updates
Patch1350: linux-2.6-bcm43xx-periodic-work.patch
Patch1351: linux-2.6-net-e1000-updates.patch

# Filesystem stuff.
# Squashfs
Patch1400: linux-2.6-squashfs.patch
Patch1401: linux-2.6-squashfs-s390-dirty-memory-fix.patch
# GFS/DLM
Patch1410: linux-2.6-gfs2-dlm.patch
Patch1411: linux-2.6-gfs2-tux.patch
Patch1412: linux-2.6-gfs2-locking-exports.patch
Patch1413: linux-2.6-gfs2-move-fs-flags-to-fs_h.patch
Patch1414: linux-2.6-gfs2-dlm-fix-mount-issues.patch
Patch1415: linux-2.6-gfs2-dlm-clear-sbflags-lock-master.patch
Patch1416: linux-2.6-gfs2-dlm-add-tcp-communications.patch
Patch1417: linux-2.6-gfs2-dlm-reset-recover_locks-when-aborted.patch
Patch1418: linux-2.6-gfs2-dlm-fix-incorrect-fs-sync-behaviour.patch
Patch1419: linux-2.6-gfs2-dlm-fix-kref_put-oops.patch

Patch1420: linux-2.6-inode_diet-replace-inodeugeneric_ip-with-inodei_private.patch
Patch1421: linux-2.6-inode-diet-move-i_pipe-into-a-union.patch
Patch1422: linux-2.6-inode-diet-move-i_bdev-into-a-union.patch
Patch1423: linux-2.6-inode-diet-move-i_cdev-into-a-union.patch
Patch1424: linux-2.6-inode-diet-eliminate-i_blksize-and-use-a-per-superblock-default.patch
Patch1425: linux-2.6-inode-diet-squashfs.patch

# NFS superblock sharing
Patch1430: linux-2.6-nfs-unified-sb-os-support.patch
Patch1431: linux-2.6-nfs-unified-sb.patch
# CacheFiles support
Patch1432: linux-2.6-cachefiles-os-support.patch
Patch1433: linux-2.6-cachefiles.patch
# FS-Cache support
Patch1434: linux-2.6-fscache-os-support.patch
Patch1435: linux-2.6-fscache.patch
Patch1436: linux-2.6-fscache-nfs.patch
Patch1437: linux-2.6-fscache-afs.patch

# Various NFS changes.
# double d_drop
Patch1440: linux-2.6-nfs-client-double_d-drop.patch
# NFS uses 64-bit inodes
Patch1441: linux-2.6-nfs-64-bit-inode-support.patch
# Fix NFS/Selinux oops.
Patch1442: linux-2.6-nfs-selinux-oops.patch
Patch1443: linux-2.6-nfs-client-dentry-oops.patch
Patch1444: linux-2.6-nfs-acl-cache-to-nfs-client.patch
Patch1445: linux-2.6-nfs-release-page-fix.patch
Patch1446: linux-2.6-nfs-v4-server-use-after-free.patch
Patch1447: linux-2.6-nfs-handle-rpc-error-properly.patch
Patch1448: linux-2.6-nfs-oops-in-nfs_cancel_commit_list.patch
Patch1449: linux-2.6-nfs-fs-locations-support.patch
Patch1450: linux-2.6-nfs-disassociate-the-fsc-cookie-from-fh.patch

# EXT3 fixes
Patch1460: linux-2.6-ext3-16tb-overflow-fixes.patch
Patch1461: linux-2.6-ext3-check-for-unmapped-buffer.patch
Patch1462: linux-2.6-ext3-handle-directory-corruption-better.patch

# CIFS fixes
Patch1465: linux-2.6-cifs-invalid-readdirs.patch

# VFS fixes
Patch1470: linux-2.6-vfs-dentries-destroy.patch

# AFS fixes
Patch1475: linux-2.6-afs-dentries-refs.patch

# IPV6 routing
Patch1480: linux-2.6-ipv6-multiple-routing-tables-policy.patch
Patch1481: linux-2.6-ipv6-routing-rules-fixes.patch
Patch1482: linux-2.6-ipv6-prohibit-and-blackhole-fixes.patch
Patch1483: linux-2.6-ipv6-init-tb6_lock-through-rwlock_init.patch

# AUTOFS fixes
Patch1490: linux-2.6-autofs4-fixes.patch
Patch1491: linux-2.6-autofs4-cannot-shutdown-when-timeout-zero.patch

# Device mapper / MD layer
Patch1500: linux-2.6-dm-mirroring.patch
Patch1501: linux-2.6-dm-multipath-ioctl-support.patch
Patch1502: linux-2.6-dm-alloc_dev-error-path-fix.patch
Patch1503: linux-2.6-dm-snapshot-invalid-enomem-fix.patch
Patch1504: linux-2.6-dm-snapshot-remove-chunk_size-param.patch
Patch1505: linux-2.6-dm-snapshot-metadata-error-handling.patch
Patch1506: linux-2.6-dm-snapshot-metadata-suspend-fix.patch
Patch1507: linux-2.6-dm-snapshot-removal-seg-fault.patch
Patch1508: linux-2.6-dm-mirror-trailing-space.patch
Patch1509: linux-2.6-dm-add-uevent-change-on-resume.patch
Patch1510: linux-2.6-dm-crypt-clear-key-when-suspend.patch
Patch1511: linux-2.6-dm-use-biosets-to-avoid-deadlock.patch
Patch1512: linux-2.6-dm-add-feature-flags-to-structs.patch
Patch1513: linux-2.6-dm-mpath-fix-io-errors-on-new-path.patch

# Misc bits.
Patch1600: linux-2.6-module_version.patch
Patch1610: linux-2.6-input-kill-stupid-messages.patch
Patch1620: linux-2.6-serial-tickle-nmi.patch
Patch1630: linux-2.6-mm-suspend-improvements.patch
Patch1640: linux-2.6-autofs-revalidate-lookup.patch
Patch1650: linux-2.6-serial-460800.patch
Patch1660: linux-2.6-drm-i965.patch
Patch1670: linux-2.6-softcursor-persistent-alloc.patch
Patch1680: linux-2.6-reiserfs-dentry-ref.patch
Patch1700: linux-2.6-ide-jmicron-fixup.patch
Patch1710: linux-2.6-sched-up-migration-cost.patch
Patch1720: linux-2.6-proc-self-maps-fix.patch
Patch1740: linux-2.6-softlockup-disable.patch
Patch1741: linux-2.6-optimise-spinlock-debug.patch
Patch1742: linux-2.6-ehea-ethernet-driver.patch
Patch1743: linux-2.6-drivers-add-qlogic-firmware.patch
Patch1744: linux-2.6-libertas.diff
Patch1745: linux-2.6-olpc-touchpad.diff
Patch1746: linux-2.6-asix-usbnet-update.patch
Patch1747: linux-2.6-bnep-compat.patch
Patch1748: linux-2.6-hidp-compat.patch
Patch1749: linux-2.6-cmtp-compat.patch
Patch1751: linux-2.6-module-unaligned-access-fix.patch
Patch1753: linux-2.6-poll-einval-conforms-to-posix.patch
Patch1754: linux-2.6-allow-booting-from-raid-partition.patch
Patch1755: linux-2.6-snd-update-sigmatel-codecs.patch
Patch1756: linux-2.6-net-e100-error-recovery-fix.patch
Patch1758: linux-2.6-block-detect-cpqarray.patch
Patch1760: linux-2.6-net-veth-proc-entry-fix.patch
Patch1761: linux-2.6-tty-locking-cleanup.patch
Patch1762: linux-2.6-net-ibmveth-kdump-panic.patch
Patch1763: linux-2.6-mm-dio-prevent-populating-page-cache.patch
Patch1764: linux-2.6-pci-hotplug-p2p-bridge-ioapic-fixes.patch
Patch1765: linux-2.6-fs-bd_mount_mutex-to-sem.patch
Patch1767: linux-2.6-net-ehea-support-64k-pages.patch
Patch1768: linux-2.6-cpu-hotplug-fails-trying-to-bsp-offline.patch
Patch1769: linux-2.6-pci-sort-devices-in-breadth-first-order.patch
Patch1770: linux-2.6-drivers-export-bus-add-remove.patch

# SELinux/audit patches.
Patch1801: linux-2.6-selinux-mprotect-checks.patch
Patch1802: linux-2.6-selinux-support-range-transitions.patch
Patch1803: linux-2.6-audit-code-walking-out-of-bounds.patch
Patch1804: linux-2.6-audit-allow-filtering-by-ppid.patch
Patch1805: linux-2.6-audit-disallow-meaningless-arch-filters.patch

# Warn about usage of various obsolete functionality that may go away.
Patch1900: linux-2.6-obsolete-oss-warning.patch

# no external module should use these symbols.
Patch1910: linux-2.6-unexport-symbols.patch

# VM bits.
Patch2001: linux-2.6-vm-silence-atomic-alloc-failures.patch
Patch2002: linux-2.6-mm-tracking-dirty-pages.patch
Patch2004: linux-2.6-mm-prevent-oom-fixes.patch
Patch2005: linux-2.6-mm-release-page-with-non-zero-gfp-mask.patch

# Tweak some defaults.
Patch2100: linux-2.6-defaults-fat-utf8.patch
Patch2101: linux-2.6-defaults-firmware-loader-timeout.patch
Patch2102: linux-2.6-defaults-phys-start.patch
Patch2103: linux-2.6-defaults-unicode-vt.patch
Patch2104: linux-2.6-defaults-disable-split-ptlock.patch
Patch2105: linux-2.6-panic-on-oops.patch

# SATA Bits
Patch2200: linux-2.6-sata-promise-pata-ports.patch
Patch2201: linux-2.6-sata-ahci-suspend.patch
Patch2202: linux-2.6-sata-sas-adapters-support.patch

# ACPI bits

# Lockdep fixes.
Patch2400: linux-2.6-lockdep-fixes.patch

# Infiniband driver
Patch2600: linux-2.6-openib-sdp.patch
Patch2601: linux-2.6-openib-ehca.patch
Patch2602: linux-2.6-openib-ofed-1_1-update.patch

# kprobes changes.
Patch2700: linux-2.6-kprobes-portable.patch
Patch2701: linux-2.6-kprobes-documentation.patch
Patch2702: linux-2.6-kprobes-add-regs_return_value-helper.patch
Patch2703: linux-2.6-kprobes-deadlock-fixes.patch
Patch2704: linux-2.6-kprobes-opcode-16-byte-alignment.patch

# Wireless driver
Patch2801: linux-2.6-wireless-ipw2200-1_2_0-update.patch

#
# 10000 to 20000 is for stuff that has to come last due to the
# amount of drivers they touch. But only these should go here.
# Not patches you're too lazy for to put in the proper place.
#

Patch10000: linux-2.6-compile-fixes.patch

# Xen hypervisor patches (20000+)
Patch20000: xen-always-inline-memcmp.patch
Patch20001: xen-ia64-domu-panics-by-save-restore.patch
Patch20002: xen-ia64-windows-guest-cannot-boot-with-debug-mode.patch
Patch20003: xen-ia64-fix-for-hang-when-running-gdb.patch
Patch20004: xen-fix-mce-errors-on-amd-v.patch
Patch20005: xen-increase-limits-to-boot-large-ia64-platforms.patch
Patch20006: xen-x86_64-add-stratus-hooks-into-memory.patch
Patch20007: xen-ia64-saner-default-mem-and-cpu-alloc-for-dom0.patch
Patch20008: xen-x86-suppress-bogus-timer-warning.patch
Patch20009: xen-ia64-vulnerability-of-copy_to_user-in-pal-emu.patch
Patch20010: xen-hv-cpu-frequency-scaling.patch
Patch20011: xen-disable-cpu-freq-scaling-when-vcpus-is-small.patch
Patch20012: xen-x86-support-for-architectural-pstate-driver.patch
Patch20013: xen-ia64-hvm-guest-memory-range-checking.patch
Patch20014: xen-enable-nested-paging-by-default-on-amd-v.patch
Patch20015: xen-ia64-running-java-vm-causes-dom0-to-hang.patch
Patch20016: xen-x86-improved-tpr-cr8-virtualization.patch
Patch20017: xen-x86-fix-hp-management-support-on-proliant.patch
Patch20018: xen-x86-vtpr-support-and-upper-address-fix.patch
Patch20019: xen-x86-make-hv-respect-the-e820-map-16m.patch
Patch20020: xen-x86-fix-continuation-translation-for-large-hc.patch
Patch20021: xen-domain-address-size-clamping.patch
Patch20022: xen-improve-checking-in-vcpu_destroy_pagetables.patch
Patch20023: xen-x86-barcelona-hypervisor-fixes.patch
Patch20024: xen-provide-numa-memory-usage-information.patch
Patch20025: xen-export-numa-topology-info-to-domains.patch
Patch20026: xen-ia64-failed-domhvm-creation-causes-hv-hang.patch
Patch20027: xen-ia64-stop-all-cpus-on-hv-panic.patch
Patch20028: xen-ia64-warning-fixes-when-checking-efi-memory.patch
Patch20029: xen-ia64-hv-hangs-on-corrected-platform-errors.patch
Patch20030: xen-incorrect-calculation-leads-to-wrong-nr_cpus.patch
Patch20031: xen-hvm-evtchn-to-fake-pci-interrupt-propagation.patch
Patch20032: xen-hvm-tolerate-intack-completion-failure.patch
Patch20033: xen-move-hvm_maybe_deassert_evtchn_irq-early.patch
Patch20034: xen-virtualize-ibr-dbr-for-pv-domains.patch
Patch20035: xen-domain-debugger-for-vti.patch
Patch20036: xen-x86-more-improved-tpr-cr8-virtualization.patch
Patch20037: xen-x86-pae-support-4gb-memory.patch
Patch20038: xen-x86-pae-support-4gb-memory-ia64-fixes.patch
Patch20039: xen-ia64-create-100gb-mem-guest-fixes.patch
Patch20040: xen-ia64-create-100gb-mem-guest-hv-softlockup.patch
Patch20041: xen-ia64-guest-has-bad-network-performance.patch
Patch20042: xen-ia64-domhvm-with-pagesize-4k-hangs.patch
Patch20043: xen-ia64-stop-all-cpus-on-hv-panic-part2.patch
Patch20044: xen-ia64-domhvm-with-pagesize-4k-hangs-part2.patch
Patch20045: xen-ia64-stop-all-cpus-on-hv-panic-part3.patch
Patch20046: xen-new-vcpu-lock-unlock-helper-functions.patch
Patch20047: xen-resync-tsc-extrapolated-frequency.patch
Patch20048: xen-x86-fix-change-frequency-hypercall.patch
Patch20049: xen-x86-revert-to-default-pit-timer.patch
Patch20050: xen-mprotect-performance-improvements.patch
Patch20051: xen-ia64-fix-kprobes-slowdown-on-single-step.patch
Patch20052: xen-hv-inside-a-fv-guest-crashes-the-host.patch
Patch20053: xen-ia64-fix-kernel-panic-on-systems-w-4gb-ram.patch
Patch20054: xen-ia64-ftp-stress-test-fixes-between-hvm-dom0.patch
Patch20055: xen-ia64-hv-messages-are-not-shown-on-vga-console.patch
Patch20056: xen-oprofile-support-for-penryn-class-processors.patch
Patch20057: xen-hv-ignoring-extended-cpu-model-field.patch
Patch20058: xen-fix-vt-x2-flexpriority.patch
Patch20059: xen-kexec-allocate-correct-memory-reservation.patch
Patch20060: xen-save-phys-addr-for-crash-utility.patch
Patch20061: xen-hv-memory-corruption-with-large-number-of-cpus.patch
Patch20062: xen-x86-new-vcpu_op-call-to-get-physical-cpu-identity.patch
Patch20063: xen-enable-serial-console-for-new-ia64-chip.patch
Patch20064: xen-use-vps-service-to-take-place-of-pal-call.patch
Patch20065: xen-add-vps-sync-read-write-according-to-spec.patch
Patch20066: xen-x86-xenoprof-enable-additional-perf-counters.patch
Patch20067: xen-ia64-smp-unsafe-with-xenmem_add_to_physmap-on-hvm.patch
Patch20068: xen-avoid-dom0-hang-when-tearing-down-domains.patch
Patch20069: xen-automatically-make-heap-larger-on-large-mem-system.patch
Patch20070: xen-limit-dom0-to-32gb-by-default.patch
Patch20071: xen-fix-building-with-max_phys_cpus-128.patch
Patch20072: xen-fix-gdt-allocation-for-128-cpus.patch
Patch20073: xen-x86-make-xenoprof-recognize-other-platforms.patch
Patch20074: xen-ia64-oprofile-recognize-montvale-cpu-as-itanium2.patch
Patch20075: xen-ia64-fixup-physinfo.patch
Patch20076: xen-ia64-fix-xen_sysctl_physinfo-to-handle-numa-info.patch
Patch20077: xen-ia64-quiet-lookup_domain_mpa-when-domain-is-dying.patch
Patch20078: xen-ia64-quieter-xen-boot.patch
Patch20079: xen-ia64-remove-annoying-log-message.patch
Patch20080: xen-ia64-suppress-warning-of-__assign_domain_page.patch
Patch20081: xen-ia64-remove-regnat-fault-message.patch
Patch20082: xen-ia64-don-t-warn-for-eoi-ing-edge-triggered-intr.patch
Patch20083: xen-serialize-scrubbing-pages.patch
Patch20084: xen-page-scrub-serialise-softirq-with-a-new-lock.patch
Patch20085: xen-ia64-fix-ia64_leave_kernel.patch
Patch20086: xen-ia64-turn-off-psr-i-after-pal_halt_light.patch
Patch20087: xen-ia64-fix-and-cleanup-move-to-psr.patch
Patch20088: xen-amd-2mb-backing-pages-support.patch
Patch20089: xen-intel-pre-ept-patch.patch
Patch20090: xen-intel-ept-patch.patch
Patch20091: xen-intel-ept-migration-patch.patch
Patch20092: xen-intel-ept-2mb-patch.patch
Patch20093: xen-x86-fix-building-with-max_phys_cpus-128.patch
Patch20094: xen-ia64-vps-save-restore-patch.patch
Patch20095: xen-hv-ability-to-use-makedumpfile-with-vmcoreinfo.patch
Patch20096: xen-ia64-vt-i2-performance-addendum.patch
Patch20097: xen-allow-guests-to-hide-the-tsc-from-applications.patch
Patch20098: xen-ia64-fix-init-injection.patch
Patch20099: xen-ia64-vt-i2-performance-restoration.patch
Patch20100: xen-ia64-make-viosapic-smp-safe-by-adding-lock-unlock.patch
Patch20101: xen-x86-allow-the-kernel-to-boot-on-pre-64-bit-hw.patch
Patch20102: xen-live-migration-of-pv-guest-fails.patch
Patch20103: xen-limit-node-poking-to-available-nodes.patch
Patch20104: xen-fix-physical-memory-address-overflow.patch
Patch20105: xen-increase-maximum-dma-buffer-size.patch
Patch20106: xen-x86-emulate-movzwl-with-negative-segment-offsets.patch
Patch20107: xen-clear-screen-to-make-luks-passphrase-visible.patch
Patch20108: xen-allow-4gb-ept-guests-on-i386.patch
Patch20109: xen-x86-silence-wrmsr-warnings.patch
Patch20110: xen-x86-fix-dom0-panic-when-using-dom0_max_vcpus.patch
Patch20111: xen-ia64-fix-windows-2003-bsod.patch
Patch20112: xen-improve-handle_fpu_swa.patch
Patch20113: xen-ia64-make-sure-guest-pages-don-t-change.patch
Patch20114: xen-ia64-fix-fp-emulation-in-a-pv-domain.patch
Patch20115: xen-ia64-add-pci-definitions-and-access-functions.patch
Patch20116: xen-add-vt-d-public-header-files.patch
Patch20117: xen-some-system-changes-for-vt-d.patch
Patch20118: xen-add-vt-d-specific-files.patch
Patch20119: xen-x86-irq-injection-changes-for-vt-d.patch
Patch20120: xen-x86-intercept-i-o-for-assigned-device.patch
Patch20121: xen-x86-memory-changes-for-vt-d.patch
Patch20122: xen-x86-add-domctl-interfaces-for-vt-d.patch
Patch20123: xen-x86-fix-ept-for-vt-d.patch
Patch20124: xen-vtd-avoid-redundant-context-mapping.patch
Patch20125: xen-x86-emulate-accesses-to-pci-window-regs-cf8-cfc.patch
Patch20126: xen-vt-d2-support-queue-invalidation.patch
Patch20127: xen-vt-d2-support-interrupt-remapping.patch
Patch20128: xen-sync-vt-d2-code-with-xen-unstable.patch
Patch20129: xen-rename-evtchn_lock-to-event_lock.patch
Patch20130: xen-convert-pirq-to-per-domain.patch
Patch20131: xen-msi-supprt-internal-functions.patch
Patch20132: xen-msi-support-interface.patch
Patch20133: xen-vt-d2-enable-interrupt-remapping-for-msi-msi-x.patch
Patch20134: xen-hvm-msi-passthrough-support.patch
Patch20135: xen-add-hypercall-for-adding-and-removing-pci-devices.patch
Patch20136: xen-ia64-fix-whitespace-error-in-vmx-h.patch
Patch20137: xen-ia64-fix-hvm-guest-kexec.patch
Patch20138: xen-fix-evtchn-exhaustion-with-32-bit-hvm-guest.patch
Patch20139: xen-x86-update-the-earlier-aperf-mperf-patch.patch
Patch20140: xen-fix-32-on-64-pv-oops-in-xen_set_pud.patch
Patch20141: xen-x86-vpid-implement-feature.patch
Patch20142: xen-x86-vpid-free-resources.patch
Patch20143: xen-x86-gdt-replace-single-page-with-one-page-cpu.patch
Patch20144: xen-live-migration-failure-due-to-fragmented-memory.patch
Patch20145: xen-add-amd-iommu-xen-driver.patch
Patch20146: xen-enable-amd-iommu-xen-driver.patch
Patch20147: xen-fix-interrupt-remapping-on-amd-systems.patch
Patch20148: xen-vt-d-enhance-mtrr-pat-virtualization.patch
Patch20149: xen-utilise-the-guest_pat-and-host_pat-vmcs-area.patch
Patch20150: xen-pci-fix-definition-of-pci_pm_ctrl_no_soft_reset.patch
Patch20151: xen-vt-d-workaround-for-mobile-series-4-chipset.patch
Patch20152: xen-enable-systems-without-apic.patch
Patch20153: xen-clear-x86_feature_apic-in-cpuid-when-apic-disabled.patch
Patch20154: xen-x86-fix-msi-eoi-handling-for-hvm-passthru.patch
Patch20155: xen-x86-initialize-vlapic-timer_last_update.patch
Patch20156: xen-x86-misc-fixes-to-the-timer-code.patch
Patch20157: xen-introduce-no-missed-tick-accounting-.patch
Patch20158: xen-x86-fixes-to-the-no-missed-tick-accounting-code.patch
Patch20159: xen-x86-fix-overflow-in-the-hpet-code.patch
Patch20160: xen-x86-explicitly-zero-cr-1-in-getvcpucontext.patch
Patch20161: xen-x86_64-add-1gb-page-table-support.patch
Patch20162: xen-add-credit-scheduler-fairness-and-hard-virt.patch
Patch20163: xen-sched-remove-printk-introduced-with-hard-virt.patch
Patch20165: xen-deadlock-between-libvirt-and-xentop.patch
Patch20166: xen-disable-2mb-support-on-pae-kernels.patch
Patch20167: xen-x86-fix-irq-problem-on-legacy-hardware.patch
Patch20168: xen-allow-msi-reconfigure-for-pt_bind_irq.patch
Patch20169: xen-ia64-add-get-set_address_size-support.patch
Patch20170: xen-hv-remove-high-latency-spin_lock.patch
Patch20171: xen-amd-iommu-crash-with-pass-through-on-large-memory.patch
Patch20172: xen-x86-make-nmi-detection-work.patch
Patch20173: xen-i386-handle-x87-opcodes-in-tls-segment-fixup.patch
Patch20174: xen-x86-fix-wrong-asm.patch
Patch20175: xen-mask-out-more-cpuid-bits-for-pv-guests.patch
Patch20176: xen-allow-booting-with-broken-serial-hardware.patch
Patch20177: xen-mask-out-xsave-for-hvm-guests.patch
Patch20178: xen-panic-in-msi_msg_read_remap_rte-with-acpi-off.patch
Patch20179: xen-ia64-command-line-arg-to-increase-the-heap-size.patch
Patch20180: xen-iommu-move-iommu_setup-to-setup-ioapic-correctly.patch
Patch20181: xen-support-interrupt-remapping-on-m-c.patch
Patch20182: xen-iommu-enable-amd-iommu-debug-at-run-time.patch
Patch20183: xen-iommu-add-passthrough-and-no-intremap-parameters.patch
Patch20184: xen-iommu-amd-extend-loop-ctr-for-polling-completion-wait.patch
Patch20185: xen-fix-crash-with-memory-imbalance.patch
Patch20186: xen-whitespace-fixups-in-xen-scheduler.patch
Patch20187: xen-crank-the-correct-stat-in-the-scheduler.patch
Patch20188: xen-hook-sched-rebalance-logic-to-opt_hardvirt.patch
Patch20189: xen-add-two-hp-proliant-dmi-quirks-to-the-hypervisor.patch
Patch20190: xen-fix-numa-on-magny-cours-systems.patch
Patch20191: xen-mask-extended-topo-cpuid-feature.patch
Patch20192: xen-implement-fully-preemptible-page-table-teardown.patch
Patch20193: xen-fix-srat-check-for-discontiguous-memory.patch
Patch20194: xen-domu-irq-ratelimiting.patch
Patch20195: xen-fix-w-sata-set-to-ide-combined-mode-on-amd.patch
Patch20196: xen-fix-msi-x-table-fixmap-allocation.patch
Patch20197: xen-change-interface-of-hvm_mmio_access.patch
Patch20198: xen-passthrough-msi-x-mask-bit-acceleration.patch
Patch20199: xen-mask-amd-s-node-id-msr.patch
Patch20200: revert-xen-passthrough-msi-x-mask-bit-acceleration.patch
Patch20201: revert-xen-change-interface-of-hvm_mmio_access.patch
Patch20202: revert-xen-fix-msi-x-table-fixmap-allocation.patch
Patch20203: xen-misc-bz-537734-xen-fix-msix-table-fixmap-allocation-v3.patch
Patch20204: xen-misc-bz-537734-xen-change-interface-of-hvm_mmio_access-v3.patch
Patch20205: xen-misc-bz-537734-xen-passthrough-msi-x-mask-bit-acceleration-v3.patch
Patch20206: xen-fix-cpu-frequency-scaling-on-intel-procs.patch
Patch20207: xen-vtd-ignore-unknown-dmar-entries.patch
Patch20208: xen-vtd-fix-ioapic-pin-array.patch
Patch20209: xen-iommu-clear-io-apic-pins-on-boot-and-shutdown.patch
Patch20210: xen-arpl-on-mmio-area-crashes-the-guest.patch
Patch20211: xen-set-hypervisor-present-cpuid-bit.patch
Patch20212: xen-ia64-unset-be-from-the-task-psr.patch
Patch20213: xen-bring-back-vmxe-svme-flags.patch
Patch20214: xen-fix-guest-crash-on-non-ept-machine-may-crash-host.patch
# end of Xen patches

Patch21007: linux-2.6-netlabel-error-checking-cleanups.patch
Patch21008: linux-2.6-xen-fix-spinlock-when-removing-xennet-device.patch
Patch21009: linux-2.6-ia64-fix-panic-in-cpu-hotplug.patch
Patch21010: linux-2.6-acpi-cleanup-output-messages.patch
Patch21011: linux-2.6-xen-privcmd-range-check-hypercall-index.patch
Patch21012: linux-2.6-fs-catch-blocks-beyond-pagecache-limit.patch
Patch21013: linux-2.6-mm-noisy-stack-trace-by-memory-hotplug.patch
Patch21014: linux-2.6-net-compute-checksum-in-netpoll_send_udp.patch
Patch21015: linux-2.6-cifs-explicitly-set-stat-blksize.patch
Patch21016: linux-2.6-configfs-mutex_lock_nested-fix.patch
Patch21017: linux-2.6-openib-ehca-fix-64k-page-table.patch
Patch21018: linux-2.6-dm-sys-block-entries-remain-after-removal.patch
Patch21019: linux-2.6-proc-readdir-race-fix.patch
Patch21021: linux-2.6-sound-hda-fix-typo-in-patch_realtek-c.patch
Patch21022: linux-2.6-net-bnx2-update-firmware-to-correct-rx-problem.patch
Patch21023: linux-2.6-xen-fix-profiling.patch
Patch21024: linux-2.6-xen-netback-reenable-tx-queueing.patch
Patch21025: linux-2.6-x86-remove-microcode-size-check.patch
Patch21026: linux-2.6-s390-add-missing-ctcmpc-target.patch
Patch21027: linux-2.6-xen-avoid-touching-watchdog-when-gone-too-long.patch
Patch21028: linux-2.6-hp-fix-bogus-warning-in-lock_cpu_hotplug.patch
Patch21029: linux-2.6-usb-add-raritan-kvm-usb-dongle-to-usb-blacklist.patch
Patch21030: linux-2.6-x86_64-kdump-mptable-reservation-fix.patch
Patch21031: linux-2.6-dlm-dont-accept-replies-to-old-recovery-messages.patch
Patch21032: linux-2.6-dlm-fix-add_requestqueue-checking-nodes-list.patch
Patch21033: linux-2.6-dlm-fix-size-of-status_reply-message.patch
Patch21034: linux-2.6-net-enable-netpoll-netconsole-for-ibmveth.patch
Patch21035: linux-2.6-net-fix-flowi-clobbering.patch
Patch21036: linux-2.6-xen-iscsi-oops-on-x86_64-xen-domu.patch
Patch21037: linux-2.6-lockdep-ide-proc-interaction-fix.patch
Patch21038: linux-2.6-xen-make-netfront-device-permanent.patch
Patch21039: linux-2.6-x86_64-make-the-boot-gdt-limit-exact.patch
Patch21040: linux-2.6-net-ibmveth-panic-when-buffer-rolls-over.patch
Patch21041: linux-2.6-mm-write-failure-on-swapout-could-corrupt-data.patch
Patch21042: linux-2.6-ppc-update_flash-is-broken.patch
Patch21043: linux-2.6-ppc-power6-illegal-instruction-on-install.patch
Patch21044: linux-2.6-net-e1000-add-device-ids.patch
Patch21045: linux-2.6-ppc-reduce-iommu-page-size-to-4k.patch
Patch21046: linux-2.6-agp-corruption-fixes.patch
Patch21047: linux-2.6-acpi-allow-highest-frequency-if-bios-think-so.patch
Patch21048: linux-2.6-xen-blkback-fix-first_sect-check.patch
Patch21049: linux-2.6-selinux-fix-oops-with-non-mls-policies.patch
Patch21050: linux-2.6-selinux-give-correct-responce-to-get_peercon.patch
Patch21051: linux-2.6-netlabel-send-audit-messages-if-audit-is-on.patch
Patch21052: linux-2.6-dlm-check-for-incompatible-protocol-version.patch
Patch21053: linux-2.6-dlm-resend-lock-during-recovery-if-master-not-ready.patch
Patch21054: linux-2.6-dlm-use-recovery-seq-number-to-discard-old-replies.patch
Patch21056: linux-2.6-xen-fix-2tb-overflow-in-virtual-disk-driver.patch
Patch21057: linux-2.6-hfs-return-error-code-in-case-of-error.patch
Patch21058: linux-2.6-megaraid-initialization-fix-for-kdump.patch
Patch21059: linux-2.6-xen-netback-fix-transmit-credit-scheduler-wrap.patch
Patch21060: linux-2.6-netlabel-disallow-ip-editing-on-cipso-socket.patch
Patch21061: linux-2.6-mm-prevent-hugepages_rsvd-from-going-negative.patch
Patch21062: linux-2.6-net-e1000-reset-all-functions-after-a-pci-error.patch
Patch21063: linux-2.6-sata-ata_piix-map-values.patch
Patch21064: linux-2.6-net-tg3-bcm5752m-crippled-after-reset.patch
Patch21065: linux-2.6-net-tg3-support-broadcom-5756m-5756me-controller.patch
Patch21066: linux-2.6-netlabel-bring-current-with-upstream-bugs.patch
Patch21067: linux-2.6-netlabel-bring-current-with-upstream-performance.patch
Patch21068: linux-2.6-netlabel-bring-current-with-upstream-cleanup-future-work.patch
Patch21069: linux-2.6-xen-blkback-copy-shared-data-before-verification.patch
Patch21070: linux-2.6-xen-blkback-fix-potential-grant-entry-leaks-on-error.patch
Patch21071: linux-2.6-nfs-set-correct-mode-during-create-operation.patch
Patch21072: linux-2.6-char-ipmi-multiple-baseboard-management-centers.patch
Patch21073: linux-2.6-cachefiles-cachefiles_write_page-should-not-error-twice.patch
Patch21074: linux-2.6-pciehp-reenabling-the-slot-disables-the-slot.patch
Patch21075: linux-2.6-pciehp-info-messages-are-confusing.patch
Patch21076: linux-2.6-pciehp-parallel-hotplug-operations-cause-panic.patch
Patch21077: linux-2.6-pciehp-pci_disable_msi-called-to-early.patch
Patch21078: linux-2.6-pciehp-free_irq-called-twice.patch
Patch21079: linux-2.6-shpchp-driver-does-not-work-in-poll-mode.patch
Patch21080: linux-2.6-shpchp-driver-fails-on-system-under-heavy-load.patch
Patch21081: linux-2.6-xen-properly-close-blkfront-on-non-existant-file.patch
Patch21082: linux-2.6-xen-ia64-get-it-working.patch
Patch21083: linux-2.6-xen-ia64-kernel-unaligned-access.patch
Patch21084: linux-2.6-wireless-d80211-kabi-pre-compatibility.patch
Patch21085: linux-2.6-ide-spurious-interrups-from-esb2-in-native-mode.patch
Patch21086: linux-2.6-s390-common-i-o-layer-fixes.patch
Patch21087: linux-2.6-xen-copy-shared-data-before-verification.patch
Patch21088: linux-2.6-dm-mirroring-fix-sync-status-change.patch
Patch21089: linux-2.6-dlm-fix-send_args-lvb-copying.patch
Patch21090: linux-2.6-dlm-fix-receive_request-lvb-copying.patch
Patch21091: linux-2.6-scsi-ide-and-ide-cdrom-module-load-race-fix.patch
Patch21092: linux-2.6-gfs2-fix-bmap-to-map-extents-properly.patch
Patch21093: linux-2.6-gfs2-tidy-up-bmap-and-fix-boundary-bug.patch
Patch21094: linux-2.6-fs-fix-rescan_partitions-to-return-errors-properly.patch
Patch21095: linux-2.6-fs-check_partition-routines-to-continue-on-errors.patch
Patch21096: linux-2.6-gfs2-fix-incorrect-fs-sync-behaviour.patch
Patch21097: linux-2.6-gfs2-simplify-glops-functions.patch
Patch21098: linux-2.6-gfs2-fix-journal-flush-problem.patch
Patch21099: linux-2.6-gfs2-fix-memory-allocation-in-glock-c.patch
Patch21100: linux-2.6-cifs-fix-mount-failure-when-domain-not-specified.patch
Patch21101: linux-2.6-gfs2-fix-recursive-locking-in-gfs2_getattr.patch
Patch21102: linux-2.6-gfs2-fix-recursive-locking-in-gfs2_permission.patch
Patch21103: linux-2.6-scsi-fix-stex_intr-signature.patch
Patch21104: linux-2.6-xen-fix-swiotlb-for-b44-module-kernel-patch.patch
Patch21105: linux-2.6-cramfs-fix-zlib_inflate-oops-with-corrupted-image.patch
Patch21106: linux-2.6-gfs2-fix-mount-failure.patch
Patch21107: linux-2.6-x86_64-fix-time-skew-on-intel-core-2-processors.patch
Patch21109: linux-2.6-x86_64-disable-pci-mmconf-on-hp-xw9300-9400.patch
Patch21110: linux-2.6-gfs2-don-t-flush-everything-on-fdatasync.patch
Patch21111: linux-2.6-gfs2-fix-uninitialised-variable.patch
Patch21112: linux-2.6-xen-make-ballooning-work-right.patch
Patch21113: linux-2.6-selinux-quoted-commas-for-certain-context-mounts.patch
Patch21114: linux-2.6-i386-touch-softdog-during-oops.patch
Patch21115: linux-2.6-connector-exessive-unaligned-access.patch
Patch21116: linux-2.6-cachefiles-handle-enospc-on-create-mkdir-better.patch
Patch21117: linux-2.6-ia64-pal_get_pstate-implementation.patch
Patch21118: linux-2.6-gfs2-fix-size-caclulation-passed-to-the-allocator.patch
Patch21119: linux-2.6-gfs2-dirent-format-compatible-with-gfs1.patch
Patch21121: linux-2.6-gfs2-don-t-try-to-lockfs-after-shutdown.patch
Patch21122: linux-2.6-scsi-fc-transport-removal-of-target-configurable.patch
Patch21123: linux-2.6-mpt-fusion-bugfix-and-maintaince-improvements.patch
Patch21124: linux-2.6-scsi-qla2xxx-add-missing-pci-device-ids.patch
Patch21125: linux-2.6-mm-reject-corrupt-swapfiles-earlier.patch
Patch21126: linux-2.6-mm-gpl-export-truncate_complete_page.patch
Patch21127: linux-2.6-x86_64-enable-nx-bit-support-during-resume.patch
Patch21128: linux-2.6-x86_64-fix-execshield-randomization-for-heap.patch
Patch21129: linux-2.6-net-bonding-don-t-release-slaves-when-master-down.patch
Patch21130: linux-2.6-gfs2-readpages-fix.patch
Patch21131: linux-2.6-gfs2-readpages-fix-2.patch
Patch21132: linux-2.6-gfs2-use-try-locks-in-readpages.patch
Patch21133: linux-2.6-gfs2-fails-back-to-readpage-for-stuffed-files.patch
Patch21134: linux-2.6-cachefiles-improve-fix-reference-counting.patch
Patch21135: linux-2.6-dlm-fix-lost-flags-in-stub-replies.patch
Patch21136: linux-2.6-gfs2-fix-dio-deadlock.patch
Patch21137: linux-2.6-scsi-govault-not-accessible-due-to-software-reset.patch
Patch21138: linux-2.6-nfs-disable-solaris-nfs_acl-version-2.patch
Patch21139: linux-2.6-xen-pvfb.patch
Patch21140: linux-2.6-xen-pvfb-fixes.patch
Patch21141: linux-2.6-scsi-ibmvscsi-empty-hostx-config-file.patch
Patch21142: linux-2.6-ia64-sn_sal_set_cpu_number-called-twice-on-cpu-0.patch
Patch21143: linux-2.6-cciss-bugfixes.patch
Patch21144: linux-2.6-x86_64-create-calgary-boot-knob.patch
Patch21145: linux-2.6-bluetooth-packet-size-checks-for-capi-messages.patch
Patch21146: linux-2.6-scsi-emulex-lpfc-update-to-8-1-10-2.patch
Patch21147: linux-2.6-xen-fix-agp-on-x86_64-under-xen.patch
Patch21148: linux-2.6-scsi-emulex-lpfc-ioctl-on-ppc.patch
Patch21149: linux-2.6-scsi-oops-in-iscsi-packet-transfer-path.patch
Patch21150: linux-2.6-gfs2-change-nlink-panic.patch
Patch21151: linux-2.6-x86-handle-_pss-object-range-speedstep-centrino.patch
Patch21152: linux-2.6-gfs2-initialization-of-security-acls.patch
Patch21153: linux-2.6-misc-export-tasklist_lock.patch
Patch21154: linux-2.6-ia64-hp-zx1-systems-initalize-swiotlb-in-kdump.patch
Patch21155: linux-2.6-ppc64-dlpar-virtual-cpu-removal-failure-cppr-bits.patch
Patch21156: linux-2.6-squashfs-fixup.patch
Patch21157: linux-2.6-scsi-structs-for-future-known-features-and-fixes.patch
Patch21158: linux-2.6-audit-xfrm-config-change-auditing.patch
Patch21159: linux-2.6-scsi-add-qla4032-and-fix-some-bugs.patch
Patch21160: linux-2.6-scsi-fix-bus-reset-in-qla1280-driver.patch
Patch21161: linux-2.6-e1000-truncated-tso-tcp-header-with-82544-workaround.patch
Patch21162: linux-2.6-xen-blktap-fix-potential-grant-entry-leaks-on-error.patch
Patch21163: linux-2.6-splice-must-fully-check-for-fifos.patch
Patch21164: linux-2.6-ia64-kexec-kdump-on-sgi-machines-fixes.patch
Patch21165: linux-2.6-xen-use-swiotlb-mask-for-coherent-mappings-too.patch
Patch21166: linux-2.6-fscache-dueling-read-write-processes-fix.patch
Patch21167: linux-2.6-isdn-ppp-call-init_timer-for-reset-state.patch
Patch21168: linux-2.6-mm-mincore-fix-race-condition.patch
Patch21169: linux-2.6-acpi-increase-acpi_max_reference_count.patch
Patch21170: linux-2.6-net-netfilter-ipv6-ip6tables-vulnerabilities.patch
Patch21171: linux-2.6-nfs-system-stall-under-high-memory-pressure.patch
Patch21172: linux-2.6-audit-add-type-for-3rd-party-emit-key-for-events.patch
Patch21173: linux-2.6-mm-fix-race-in-shared-mmap-ed-page-writeback.patch
Patch21174: linux-2.6-scsi-iscsi-fix-sense-len-handling.patch
Patch21175: linux-2.6-netlabel-stricter-configuration-checking.patch
Patch21176: linux-2.6-x86-remove-unwinder-patches.patch
Patch21177: linux-2.6-ppc64-altivec-avoid-panic-from-userspace.patch
Patch21178: linux-2.6-net-act_gact-division-by-zero.patch
Patch21179: linux-2.6-autofs-fix-panic-on-mount-fail.patch
Patch21180: linux-2.6-net-b44-phy-reset-problem-that-leads-to-link-flap.patch
Patch21181: linux-2.6-net-make-inet-is_icsk-assignment-binary.patch
Patch21182: linux-2.6-cpei-prevent-relocating-hotplug-irqs.patch
Patch21183: linux-2.6-fs-ext2_check_page-denial-of-service.patch
Patch21184: linux-2.6-dlm-disable-debugging-output.patch
Patch21185: linux-2.6-dlm-change-some-log_error-to-log_debug.patch
Patch21186: linux-2.6-x86_64-enabling-lockdep-hangs-the-system.patch
Patch21187: linux-2.6-mm-fix-for-shmem_truncate_range-bug_on.patch
Patch21188: linux-2.6-xen-fix-nosegneg-detection.patch
Patch21189: linux-2.6-gfs2-fix-ordering-of-page-disposal-vs-glock_dq.patch
Patch21190: linux-2.6-gfs2-fix-gfs2_rename-lock-ordering.patch
Patch21191: linux-2.6-netfilter-ip_conntrack-fails-to-unload.patch
Patch21192: linux-2.6-ppc64-kdump-allow-booting-with-maxcpus-1.patch
Patch21193: linux-2.6-x86-add-panic-on-unrecovered-nmi.patch
Patch21194: linux-2.6-s390-inflate-spinlock-kabi.patch
Patch21195: linux-2.6-net-qla3xxx-panics-when-eth1-is-sending-pings.patch
Patch21196: linux-2.6-misc-remove-capability-req-to-read-cap-bound.patch
Patch21197: linux-2.6-cachefs-fix-object-struct-recycling.patch
Patch21198: linux-2.6-fs-listxattr-syscall-corrupt-user-space-programs.patch
Patch21200: linux-2.6-x86_64-clear_kernel_mapping-will-leak-memory.patch
Patch21201: linux-2.6-edac-fix-proc-bus-pci-devices-allow-x-to-start.patch
Patch21202: linux-2.6-xfrm-audit-correct-xfrm-auditing-panic.patch
Patch21203: linux-2.6-net-ipv6-panic-bringing-up-multiple-interfaces.patch
Patch21204: linux-2.6-sound-add-support-for-stac9205-codec.patch
Patch21205: linux-2.6-scsi-prevent-sym53c1510-claiming-wrong-pci-id.patch
Patch21206: linux-2.6-gfs2-return-error-for-null-inode.patch
Patch21207: linux-2.6-ppc64-initialization-of-hotplug-memory-fixes.patch
Patch21208: linux-2.6-xen-add-packet_auxdata-cmsg.patch
Patch21210: linux-2.6-sun-ami-virtual-floppy-issue.patch
Patch21211: linux-2.6-mm-fix-statistics-in-vmscan-c.patch
Patch21212: linux-2.6-netlabel-fix-locking-issues.patch
Patch21213: linux-2.6-netlabel-off-by-one-in-netlbl_cipsov4_add_common.patch
Patch21214: linux-2.6-sata-timeout-boot-message.patch
Patch21215: linux-2.6-misc-fix-vdso-in-core-dumps.patch
Patch21216: linux-2.6-sata-ahci-support-ahci-class-code.patch
Patch21217: linux-2.6-sata-support-legacy-ide-mode-of-sb600-sata.patch
Patch21218: linux-2.6-rng-check-to-see-if-bios-locked-device.patch
Patch21219: linux-2.6-mm-handle-map-of-memory-without-page-backing.patch
Patch21220: linux-2.6-audit-mask-upper-bits-on-32-bit-syscall-on-ppc64.patch
Patch21221: linux-2.6-scsi-fix-panic-on-ex8350-stex-ko.patch
Patch21222: linux-2.6-ipsec-incorrect-return-code-xfrm_policy_lookup.patch
Patch21223: linux-2.6-nfs-unable-to-mount-more-than-1-secure-mount.patch
Patch21224: linux-2.6-ia64-check-for-tio-errors-on-shub2-altix.patch
Patch21225: linux-2.6-x86-proc-mtrr-interface-mtrr-bug-fix.patch
Patch21226: linux-2.6-fs-core-dump-of-read-only-binarys.patch
Patch21227: linux-2.6-security-fix-key-serial-number-collision-problem.patch
Patch21228: linux-2.6-cpufreq-remove-__initdata-from-tscsync.patch
Patch21229: linux-2.6-pcmcia-buffer-overflow-in-omnikey-cardman-driver.patch
Patch21230: linux-2.6-utrace-exploit-and-unkillable-cpu-fixes.patch
Patch21231: linux-2.6-x86-fix-boot_params-and-pci_fixup-warnings.patch
Patch21232: linux-2.6-x86-cpu-hotplug-smpboot-misc-modpost-warning-fixes.patch
Patch21233: linux-2.6-x86-declare-functions-__init-to-avoid-compile-warnings.patch
Patch21234: linux-2.6-init-break-init-two-parts-avoid-modpost-warnings.patch
Patch21235: linux-2.6-serial-change-serial8250_console_setup-to-__init.patch
Patch21236: linux-2.6-x86-fix-apci-related-modpost-warnings.patch
Patch21237: linux-2.6-x86-apic-probe-__init-fixes.patch
Patch21238: linux-2.6-x86-change-__init-to-__cpuinit-data-in-smp-code.patch
Patch21239: linux-2.6-x86-remove-__init-from-efi_get_time.patch
Patch21240: linux-2.6-irq-remove-__init-from-noirqdebug_setup.patch
Patch21241: linux-2.6-x86-remove-__init-from-sysenter_setup.patch
Patch21242: linux-2.6-rtc-__init-to-__devinit-in-drivers-probe-functions.patch
Patch21243: linux-2.6-usb-__init-to-__devinit-in-isp116x_probe.patch
Patch21244: linux-2.6-video-change-nvidiafb_remove-to-__devexit.patch
Patch21245: linux-2.6-atm-fix-__initdata-declarations-in-he-c.patch
Patch21246: linux-2.6-x86-reorganize-smp_alternatives-sections-in-vmlinuz.patch
Patch21247: linux-2.6-video-change-rivafb_remove-to-__deviexit.patch
Patch21248: linux-2.6-net-__devinit-__devexit-cleanups-for-de2104x-driver.patch
Patch21249: linux-2.6-mm-remove-__initdata-from-initkmem_list3.patch
Patch21250: linux-2.6-sound-fix-data-declarations-in-sound-drivers.patch
Patch21251: linux-2.6-x86-fix-various-data-declarations-in-cyrix-c.patch
Patch21252: linux-2.6-nfs-version-2-over-udp-is-not-working-properly.patch
Patch21253: linux-2.6-audit-gfp_kernel-allocation-non-blocking-context.patch
Patch21254: linux-2.6-net-ipv6-security-holes-in-ipv6_sockglue-c-1.patch
Patch21255: linux-2.6-net-ipv6-security-holes-in-ipv6_sockglue-c-2.patch
Patch21256: linux-2.6-mm-gdb-does-not-accurately-output-the-backtrace.patch
Patch21257: linux-2.6-x86_64-dont-leak-nt-bit-into-next-task.patch
Patch21258: linux-2.6-dlm-fix-user-unlocking.patch
Patch21259: linux-2.6-dlm-fix-master-recovery.patch
Patch21260: linux-2.6-dlm-saved-dlm-message-can-be-dropped.patch
Patch21261: linux-2.6-dlm-can-miss-clearing-resend-flag.patch
Patch21262: linux-2.6-dlm-increase-default-lock-limit.patch
Patch21263: linux-2.6-dlm-make-lock_dlm-drop_count-tunable-in-sysfs.patch
Patch21264: linux-2.6-gfs2-fix-missing-unlock_page.patch
Patch21265: linux-2.6-gfs2-fix-list-corruption-in-lops-c.patch
Patch21266: linux-2.6-gfs2-shrink-in-core-inode-size.patch
Patch21267: linux-2.6-gfs2-occasional-panic-in-gfs2_unlink.patch
Patch21268: linux-2.6-gfs2-fix-softlockups.patch
Patch21269: linux-2.6-gfs2-correctly-display-revalidated-directories.patch
Patch21270: linux-2.6-sched-remove-__cpuinitdata-from-cpu_isolated_map.patch
Patch21271: linux-2.6-ppc-reduce-num_pmcs-to-6-for-power6.patch
Patch21272: linux-2.6-s390-page_mkclean-causes-data-corruption.patch
Patch21273: linux-2.6-nfs-fix-disabling-protocols-when-starting-server.patch
Patch21274: linux-2.6-misc-longer-cd-timeout.patch
Patch21275: linux-2.6-kdump-bounds-checking-for-crashkernel-args.patch
Patch21276: linux-2.6-acpi-fix-pci-root-bridge-querying-time.patch
Patch21277: linux-2.6-scsi-missing-pci-device-in-aic79xx-driver.patch
Patch21278: linux-2.6-ext3-return-enoent-from-ext3_link-race-with-unlink.patch
Patch21279: linux-2.6-misc-fix-race-in-efi-variable-delete-code.patch
Patch21280: linux-2.6-usb-airprime-corrupts-ppp-session-for-evdo-card.patch
Patch21281: linux-2.6-scsi-fix-incorrect-last-scatg-length.patch
Patch21282: linux-2.6-ext3-buffer-memorder-fix.patch
Patch21283: linux-2.6-suspend-fix-x86_64-relocatable-kernel-swsusp.patch
Patch21284: linux-2.6-s390-runtime-switch-for-dasd-erp-logging.patch
Patch21285: linux-2.6-cpu-hotplug-make-and-module-insertion-cause-panic.patch
Patch21286: linux-2.6-s390-crypto-support-for-3592-tape-devices.patch
Patch21287: linux-2.6-s390-direct-yield-for-spinlocks.patch
Patch21288: linux-2.6-gfs2-nfs-v2-mount-failure.patch
Patch21289: linux-2.6-gfs2-nfs-causes-recursive-locking.patch
Patch21290: linux-2.6-gfs2-inconsistent-inode-number-lookups.patch
Patch21291: linux-2.6-gfs2-remove-an-incorrect-assert.patch
Patch21292: linux-2.6-scsi-blacklist-touch-up.patch
Patch21293: linux-2.6-edac-add-support-for-revision-f-processors.patch
Patch21294: linux-2.6-s390-kprobes-breaks-bug_on.patch
Patch21295: linux-2.6-ipv6-anycast6-unbalanced-inet6_dev-refcnt.patch
Patch21296: linux-2.6-fs-fix-error-handling-in-check_partition-again.patch
Patch21297: linux-2.6-ext3-handle-orphan-inodes-vs-readonly-snapshots.patch
Patch21298: linux-2.6-pci-include-devices-in-nic-ordering-patch.patch
Patch21299: linux-2.6-s390-dump-on-panic-support.patch
Patch21300: linux-2.6-gfs2-resolve-deadlock-when-write-and-access-file.patch
Patch21301: linux-2.6-gfs2-honor-the-noalloc-flag-during-block-alloc.patch
Patch21303: linux-2.6-s390-pseudo-random-number-generator.patch
Patch21304: linux-2.6-xen-fix-netfront-teardown.patch
Patch21305: linux-2.6-misc-ipc-msgsnd-msgrcv-larger-than-64k-fix.patch
Patch21306: linux-2.6-module-module_firmware-support.patch
Patch21307: linux-2.6-cifs-recognize-when-a-file-is-no-longer-read-only.patch
Patch21308: linux-2.6-tux-date-overflow-fix.patch
Patch21309: linux-2.6-ipv6-fix-routing-regression.patch
Patch21310: linux-2.6-net-clean-up-xfrm_audit_log-interface.patch
Patch21311: linux-2.6-net-wait-for-ipsec-sa-resolution-socket-contexts.patch
Patch21312: linux-2.6-security-invalidate-flow-cache-after-policy-reload.patch
Patch21313: linux-2.6-mm-some-db2-operations-cause-system-to-hang.patch
Patch21314: linux-2.6-x86-ich9-device-ids.patch
Patch21315: linux-2.6-pcie-remove-warning-for-devices-with-no-irq-pin.patch
Patch21316: linux-2.6-scsi-ata_task_ioctl-should-return-ata-registers.patch
Patch21317: linux-2.6-ide-sb600-ide-only-has-one-channel.patch
Patch21318: linux-2.6-net-stop-leak-in-flow-cache-code.patch
Patch21319: linux-2.6-elevator-move-clearing-of-unplug-flag-earlier.patch
Patch21320: linux-2.6-x86-fix-mtrr-modpost-warnings.patch
Patch21321: linux-2.6-net-xfrm_policy-delete-security-check-misplaced.patch
Patch21322: linux-2.6-agp-agpgart-fixes-and-new-pci-ids.patch
Patch21323: linux-2.6-mm-make-do_brk-correctly-return-einval-for-ppc64.patch
Patch21324: linux-2.6-misc-amd-ati-sb600-smbus-support.patch
Patch21325: linux-2.6-dm-stalls-on-resume-if-noflush-is-used.patch
Patch21326: linux-2.6-ppc64-remove-bug_on-in-hugetlb_get_unmapped_area.patch
Patch21327: linux-2.6-fs-make-counters-in-new_inode-and-iunique-32-bits.patch
Patch21328: linux-2.6-xen-better-fix-for-netfront_tx_slot_available.patch
Patch21329: linux-2.6-net-expand-in-kernel-socket-api.patch
Patch21330: linux-2.6-ipc-mqueue-nested-locking-annotation.patch
Patch21331: linux-2.6-nfs-fix-multiple-dentries-point-to-same-dir-inode.patch
Patch21332: linux-2.6-ppc64-allow-vmsplice-to-work-in-32-bit-mode.patch
Patch21333: linux-2.6-nmi-change-watchdog-timeout-to-30-seconds.patch
Patch21334: linux-2.6-s390-crypto-driver-update.patch
Patch21335: linux-2.6-x86-fix-invalid-write-to-nmi-msr.patch
Patch21336: linux-2.6-s390-fix-dasd-reservations.patch
Patch21337: linux-2.6-ppc64-cell-platform-base-kernel-support.patch
Patch21338: linux-2.6-net-ipsec-panic-when-large-sec-context-in-acquire.patch
Patch21339: linux-2.6-gfs2-clean-up-of-glock-code.patch
Patch21340: linux-2.6-gfs2-incorrect-flushing-of-rgrps.patch
Patch21341: linux-2.6-gfs2-hangs-waiting-for-semaphore.patch
Patch21342: linux-2.6-x86-tick-divider.patch
Patch21343: linux-2.6-mm-oom-kills-current-process-on-memoryless-node.patch
Patch21344: linux-2.6-ppc64-handle-power6-partition-modes.patch
Patch21345: linux-2.6-ppc64-handle-power6-partition-modes-2.patch
Patch21346: linux-2.6-dlm-zero-new-user-lvbs.patch
Patch21347: linux-2.6-dlm-overlapping-cancel-and-unlock.patch
Patch21348: linux-2.6-dlm-split-create_message-function.patch
Patch21349: linux-2.6-dlm-add-orphan-purging-code.patch
Patch21350: linux-2.6-dlm-interface-for-purge.patch
Patch21351: linux-2.6-dlm-change-lkid-format.patch
Patch21352: linux-2.6-dlm-fix-mode-munging.patch
Patch21353: linux-2.6-gfs2-use-log_error-before-lm_out_error.patch
Patch21354: linux-2.6-x86_64-fix-misconfigured-k8-north-bridge.patch
Patch21355: linux-2.6-cifs-windows-server-bad-domain-null-terminator.patch
Patch21356: linux-2.6-ia64-fix-stack-layout-issues-when-using-ulimit-s.patch
Patch21357: linux-2.6-mm-unmap-memory-range-disturbs-page-referenced.patch
Patch21358: linux-2.6-net-kernel-headers-missing-include-of-types-h.patch
Patch21359: linux-2.6-gfs2-lockdump-support.patch
Patch21360: linux-2.6-x86_64-calgary-iommu-cleanups-and-fixes.patch
Patch21361: linux-2.6-misc-k8temp.patch
Patch21362: linux-2.6-gfs2_delete_inode-13.patch
Patch21363: linux-2.6-autofs4-fix-race-between-mount-and-expire.patch
Patch21364: linux-2.6-misc-efi-only-warn-on-pre-1-00-version.patch
Patch21365: linux-2.6-net-fix-user-oops-able-bug-in-fib-netlink.patch
Patch21366: linux-2.6-serial-panic-in-check_modem_status-on-8250.patch
Patch21367: linux-2.6-security-supress-selinux-printk-messages.patch
Patch21368: linux-2.6-dm-kmirrord-deadlock-when-dirty-log-on-mirror.patch
Patch21369: linux-2.6-dm-failures-when-creating-many-snapshots.patch
Patch21370: linux-2.6-gfs2-does-a-mutex_lock-instead-of-a-mutex_unlock.patch
Patch21371: linux-2.6-x86_64-gatt-pages-must-be-uncacheable.patch
Patch21372: linux-2.6-ipc-bounds-checking-for-shmmax.patch
Patch21373: linux-2.6-misc-getcpu-system-call.patch
Patch21374: linux-2.6-net-fib_semantics-c-out-of-bounds-check.patch
Patch21375: linux-2.6-net-disallow-rho-by-default.patch
Patch21376: linux-2.6-net-ipv6-fragments-bypass-nf_conntrack-netfilter.patch
Patch21377: linux-2.6-net-null-pointer-dereferences-in-netfilter-code.patch
Patch21378: linux-2.6-mm-null-current-mm-in-grab_swap_token-causes-oops.patch
Patch21379: linux-2.6-dlm-rename-dlm_config_info-fields.patch
Patch21380: linux-2.6-dlm-add-config-entry-to-enable-log_debug.patch
Patch21381: linux-2.6-dlm-expose-dlm_config_info-fields-in-configfs.patch
Patch21382: linux-2.6-net-ipv6_fl_socklist-is-inadvertently-shared.patch
Patch21383: linux-2.6-e1000-fix-watchdog-timeout-panics.patch
Patch21385: linux-2.6-ixgb-fix-early-tso-completion.patch
Patch21386: linux-2.6-intel-rng-fix-deadlock-in-smp_call_function.patch
Patch21387: linux-2.6-x86-greyhound-cpuinfo-output-cleanups.patch
Patch21388: linux-2.6-x86-fix-cpuid-calls-to-support-gh-processors.patch
Patch21389: linux-2.6-x86-fix-to-nmi-to-support-gh-processors.patch
Patch21390: linux-2.6-x86-use-cpuid-calls-to-check-for-mce.patch
Patch21391: linux-2.6-x86-tell-sysrq-m-to-poke-the-nmi-watchdog.patch
Patch21392: linux-2.6-mm-optimize-kill_bdev.patch
Patch21393: linux-2.6-ppc64-eeh-pci-error-recovery-support.patch
Patch21394: linux-2.6-scsi-scsi_transport_spi-sense-buffer-size-error.patch
Patch21395: linux-2.6-fs-stack-overflow-with-non-4k-page-size.patch
Patch21396: linux-2.6-mm-oom-killer-breaks-s390-cmm.patch
Patch21397: linux-2.6-scsi-update-qlogic-qla2xxx-driver-to-8-01-07-k6.patch
Patch21398: linux-2.6-v4l-use-__gfp_dma32-in-videobuf_vm_nopage.patch
Patch21399: linux-2.6-pty-race-could-lead-to-double-idr-index-free.patch
Patch21400: linux-2.6-misc-fix-softlockup-warnings-during-sysrq-t.patch
Patch21401: linux-2.6-gfs2-panic-if-you-try-to-rm-lost-found-directory.patch
Patch21402: linux-2.6-gfs2-deadlock-running-d_rwdirectlarge.patch
Patch21403: linux-2.6-gfs2-mmap-problems-with-distributed-test-cases.patch
Patch21404: linux-2.6-gfs2-flush-the-glock-completely-in-inode_go_sync.patch
Patch21406: linux-2.6-ia64-fpswa-exceptions-take-excessive-system-time.patch
Patch21407: linux-2.6-ia64-mca-init-issues-with-printk-messages-console.patch
Patch21408: linux-2.6-fs-prevent-oops-in-compat-sys-mount.patch
Patch21409: linux-2.6-mm-memory-less-node-support.patch
Patch21410: linux-2.6-misc-lockdep-annotate-declare_wait_queue_head.patch
Patch21411: linux-2.6-mm-vm-scalability-issues.patch
Patch21412: linux-2.6-net-rpc-simplify-data-check-remove-bug_on.patch
Patch21413: linux-2.6-md-dm-multipath-rr-path-order-is-inverted.patch
Patch21414: linux-2.6-md-dm-fix-suspend-error-path.patch
Patch21415: linux-2.6-md-dm-allow-offline-devices-in-table.patch
Patch21416: linux-2.6-scsi-update-for-new-sas-raid.patch
Patch21417: linux-2.6-gfs2-bring-gfs2-uptodate.patch
Patch21418: linux-2.6-misc-xen-fix-microcode-driver-for-new-firmware.patch
Patch21419: linux-2.6-net-high-tcp-latency-with-small-packets.patch
Patch21420: linux-2.6-ia64-platform_kernel_launch_event-is-a-noop.patch
Patch21421: linux-2.6-acpi-_cid-support-for-pci-root-bridge-detection.patch
Patch21422: linux-2.6-scsi-fix-bogus-warnings-from-sb600-dvd-drive.patch
Patch21424: linux-2.6-autofs-fix-panic-on-mount-fail-missing-module.patch
Patch21425: linux-2.6-nfs-add-nordirplus-option-to-nfs-client.patch
Patch21426: linux-2.6-fix-oom-wrongly-kill-processes-through-mpol_bind.patch
Patch21427: linux-2.6-ia64-sn-correctly-update-smp_affinity-mask.patch
Patch21428: linux-2.6-md-dm-crypt-fix-possible-data-corruptions.patch
Patch21429: linux-2.6-ia64-eliminate-deadlock-on-xpc-disconnects.patch
Patch21430: linux-2.6-md-incorrect-param-to-dm_io-causes-read-failures.patch
Patch21431: linux-2.6-nfs-rpc-downsized-response-buffer-checksum.patch
Patch21432: linux-2.6-md-dm-io-fix-panic-on-large-request.patch
Patch21433: linux-2.6-fs-invalid-segmentation-violation-during-exec.patch
Patch21434: linux-2.6-nfs-protocol-v3-write-procedure-patch.patch
Patch21435: linux-2.6-mm-bug_on-in-shmem_writepage-is-triggered.patch
Patch21436: linux-2.6-net-rpc-krb5-memory-leak.patch
Patch21437: linux-2.6-misc-bluetooth-setsockopt-information-leaks.patch
Patch21438: linux-2.6-gfs2-shrink-size-of-struct-gdlm_lock.patch
Patch21439: linux-2.6-gfs2-fixes-related-to-gfs2_grow.patch
Patch21440: linux-2.6-net-fix-dos-in-pppoe.patch
Patch21441: linux-2.6-misc-random-fix-error-in-entropy-extraction.patch
Patch21442: linux-2.6-nfs-nfsv4-referrals-support.patch
Patch21443: linux-2.6-acpi-update-ibm_acpi-module.patch
Patch21444: linux-2.6-misc-xen-kill-sys_lock-unlock-in-microcode-driver.patch
Patch21445: linux-2.6-net-enable-and-update-qla3xxx-networking-driver.patch
Patch21447: linux-2.6-ppc64-support-for-ibm-power-off-ups-rtas-call.patch
Patch21448: linux-2.6-pci-dynamic-add-and-remove-of-pci-e.patch
Patch21449: linux-2.6-ppc64-handle-symbol-lookup-for-kprobes.patch
Patch21450: linux-2.6-x86_64-wall-time-drops-lost-timer-ticks.patch
Patch21451: linux-2.6-mm-reduce-madv_dontneed-contention.patch
Patch21452: linux-2.6-audit-log-targets-of-signals.patch
Patch21453: linux-2.6-ppc64-fix-xmon-off-and-cleanup-xmon-init.patch
Patch21454: linux-2.6-net-ixgb-update-1-0-109-to-add-pci-error-recovery.patch
Patch21455: linux-2.6-ppc64-eeh-is-improperly-enabled-for-power4-system.patch
Patch21456: linux-2.6-nfs-nlm-fix-double-free-in-__nlm_async_call.patch
Patch21457: linux-2.6-dlm-consolidate-transport-protocols.patch
Patch21458: linux-2.6-dlm-block-scand-during-recovery.patch
Patch21459: linux-2.6-dlm-add-lock-timeouts-and-time-warning.patch
Patch21460: linux-2.6-dlm-cancel-in-conversion-deadlock.patch
Patch21461: linux-2.6-dlm-fix-new_lockspace-error-exit.patch
Patch21462: linux-2.6-dlm-wait-for-config-check-during-join.patch
Patch21463: linux-2.6-dlm-canceling-deadlocked-lock.patch
Patch21464: linux-2.6-dlm-dumping-master-locks.patch
Patch21465: linux-2.6-dlm-misc-device-removed-on-lockspace-removal-fail.patch
Patch21466: linux-2.6-dlm-fix-queue_work-oops.patch
Patch21467: linux-2.6-dlm-allow-users-to-create-the-default-lockspace.patch
Patch21468: linux-2.6-scsi-megaraid-update-version-reported-by-megaioc_qdrvrver.patch
Patch21469: linux-2.6-scsi-9650se-not-recognized-by-3w-9xxx-module.patch
Patch21470: linux-2.6-aio-fix-buggy-put_ioctx-call-in-aio_complete.patch
Patch21471: linux-2.6-mm-prevent-oom-kill-of-unkillable-children.patch
Patch21472: linux-2.6-edac-k8_edac-don-t-panic-on-pcc-check.patch
Patch21473: linux-2.6-misc-synclink_gt-fix-init-error-handling.patch
Patch21474: linux-2.6-s390-zfcp-driver-fixes.patch
Patch21475: linux-2.6-scsi-scsi_error-c-fix-lost-eh-commands.patch
Patch21476: linux-2.6-nfs-enable-nosharecache-mounts.patch
Patch21477: linux-2.6-s390-runtime-switch-for-qdio-performance-stats.patch
Patch21478: linux-2.6-scsi-add-kernel-support-for-areca-raid-controller.patch
Patch21479: linux-2.6-sata-move-sata-drivers-to-drivers-ata.patch
Patch21480: linux-2.6-sata-super-jumbo-update.patch
Patch21481: linux-2.6-pci-update-ata-msi-ichx-quirks.patch
Patch21482: linux-2.6-ipmi-update-to-latest.patch
Patch21483: linux-2.6-cpufreq-identifies-num-of-proc-in-powernow-k8.patch
Patch21484: linux-2.6-ppc64-cell-spe-and-performance.patch
Patch21485: linux-2.6-ppc64-spufs-move-to-sdk2-1.patch
Patch21486: linux-2.6-ppc64-update-ehea-driver-to-latest-version.patch
Patch21487: linux-2.6-ppc64-enable-dlpar-support-for-hea.patch
Patch21488: linux-2.6-ppc64-msi-support-for-pci-e.patch
Patch21489: linux-2.6-ppc64-dma-4gb-boundary-protection.patch
Patch21490: linux-2.6-x86_64-fix-a-cast-in-the-lost-ticks-code.patch
Patch21491: linux-2.6-audit-auditing-ptrace.patch
Patch21492: linux-2.6-audit-avc_path-handling.patch
Patch21493: linux-2.6-audit-add-subtrees-support.patch
Patch21494: linux-2.6-dio-clean-up-completion-phase-of-direct_io_worker.patch
Patch21495: linux-2.6-x86-add-greyhound-performance-counter-events.patch
Patch21496: linux-2.6-block-fix-null-bio-crash-in-loop-worker-thread.patch
Patch21497: linux-2.6-audit-pfkey_delete-and-xfrm_del_sa-hooks-wrong.patch
Patch21498: linux-2.6-net-netlabel-verify-level-has-valid-cipso-mapping.patch
Patch21499: linux-2.6-audit-xfrm_add_sa_expire-return-code-error.patch
Patch21500: linux-2.6-audit-init-audit-record-sid-information-to-zero.patch
Patch21501: linux-2.6-audit-collect-inode-info-for-all-f-xattr-cmds.patch
Patch21502: linux-2.6-audit-pfkey_spdget-does-not-audit-xrfm-changes.patch
Patch21503: linux-2.6-audit-match-proto-when-searching-for-larval-sa.patch
Patch21504: linux-2.6-audit-add-space-in-ipv6-xfrm-audit-record.patch
Patch21505: linux-2.6-audit-sad-spd-flush-have-no-security-check.patch
Patch21506: linux-2.6-s390-sclp-race-condition.patch
Patch21507: linux-2.6-s390-ifenslave-c-causes-panic-with-vlan-and-osa.patch
Patch21508: linux-2.6-dasd-prevent-dasd-from-flooding-the-console.patch
Patch21509: linux-2.6-dasd-export-dasd-status-to-userspace.patch
Patch21510: linux-2.6-ide-packet-command-error-when-installing-rpm.patch
Patch21511: linux-2.6-misc-include-taskstats-h-in-kernel-headers-pkg.patch
Patch21512: linux-2.6-nfs-numerous-oops-memory-leaks-and-hangs-upstream.patch
Patch21513: linux-2.6-mm-shared-page-table-for-hugetlb-page.patch
Patch21514: linux-2.6-nfs-fixed-oops-in-symlink-code.patch
Patch21515: linux-2.6-dio-invalidate-clean-pages-before-dio-write.patch
Patch21516: linux-2.6-audit-make-audit-config-immutable-in-kernel.patch
Patch21517: linux-2.6-cifs-update-to-version-1-48arh.patch
Patch21518: linux-2.6-s390-fix-possible-reboot-hang-on-s390.patch
Patch21519: linux-2.6-gfs2-cleanup-inode-number-handling.patch
Patch21520: linux-2.6-gfs2-quotas-non-functional.patch
Patch21521: linux-2.6-gfs2-fix-calc-for-log-blocks-with-small-sizes.patch
Patch21522: linux-2.6-scsi-update-mpt-fusion-to-3-04-04.patch
Patch21523: linux-2.6-scsi-fix-for-slow-dvd-drive.patch
Patch21524: linux-2.6-scsi-mpt-adds-did_bus_busy-status-on-scsi-busy.patch
Patch21525: linux-2.6-gfs2-statfs-sign-problem-and-cleanup-_host-struct.patch
Patch21526: linux-2.6-gfs2-add-nanosecond-timestamp-feature.patch
Patch21527: linux-2.6-md-unconditionalize-log-flush.patch
Patch21528: linux-2.6-md-rh_in_sync-should-be-allowed-to-block.patch
Patch21529: linux-2.6-dlm-fix-debugfs-ref-counting-problem.patch
Patch21530: linux-2.6-scsi-update-iser-driver.patch
Patch21531: linux-2.6-scsi-update-qla4xxx-driver.patch
Patch21532: linux-2.6-ide-serverworks-data-corruptor.patch
Patch21533: linux-2.6-scsi-update-qla2xxx-firmware.patch
Patch21534: linux-2.6-scsi-omnibus-lpfc-driver-update.patch
Patch21535: linux-2.6-pci-i-o-space-mismatch-with-p64h2.patch
Patch21536: linux-2.6-scsi-add-fc-link-speeds.patch
Patch21538: linux-2.6-x86-mce-thermal-throttling.patch
Patch21539: linux-2.6-fs-fix-ext2-overflows-on-filesystems-8t.patch
Patch21540: linux-2.6-scsi-megaraid_sas-update.patch
Patch21541: linux-2.6-x86-rtc-support-for-hpet-legacy-replacement-mode.patch
Patch21542: linux-2.6-x86_64-fix-regression-in-kexec.patch
Patch21543: linux-2.6-scsi-update-iscsi_tcp-driver.patch
Patch21544: linux-2.6-scsi-cciss-ignore-unsent-commands-on-kexec-boot.patch
Patch21545: linux-2.6-scsi-update-aacraid-driver-to-1-1-5-2437.patch
Patch21546: linux-2.6-gfs2-can-t-mount-file-system-on-aoe-device.patch
Patch21547: linux-2.6-gfs2-missing-lost-inode-recovery-code.patch
Patch21548: linux-2.6-ipsec-make-xfrm_acq_expires-proc-tunable.patch
Patch21549: linux-2.6-gfs2-journaled-data-issues.patch
Patch21550: linux-2.6-dlm-variable-allocation-types.patch
Patch21551: linux-2.6-fs-nfs-does-not-support-leases-send-correct-error.patch
Patch21552: linux-2.6-audit-softlockup-messages-loading-selinux-policy.patch
Patch21553: linux-2.6-misc-cpuset-information-leak.patch
Patch21554: linux-2.6-x86_64-disable-mmconf-for-hp-dc5700-microtower.patch
Patch21555: linux-2.6-x86_64-add-l3-cache-support-to-some-processors.patch
Patch21556: linux-2.6-audit-allow-audit-filtering-on-bit-operations.patch
Patch21557: linux-2.6-audit-broken-class-based-syscall-audit.patch
Patch21558: linux-2.6-usb-strange-urbs-and-running-out-iommu.patch
Patch21559: linux-2.6-net-ip_conntrack_sctp-remote-triggerable-panic.patch
Patch21560: linux-2.6-x86_64-sparsemem-memmap-allocation-above-4g.patch
Patch21561: linux-2.6-net-mac80211-inclusion.patch
Patch21562: linux-2.6-audit-0-does-not-disable-all-audit-messages.patch
Patch21563: linux-2.6-audit-when-opening-existing-messege-queue.patch
Patch21564: linux-2.6-scsi-spi-dv-fixup.patch
Patch21565: linux-2.6-ppc64-update-of-spidernet-to-2-0-a-for-cell.patch
Patch21566: linux-2.6-net-tg3-update-to-driver-version-3-76.patch
Patch21567: linux-2.6-net-bonding-update-to-driver-version-3-1-2.patch
Patch21568: linux-2.6-net-forcedeth-update-to-driver-version-0-60.patch
Patch21569: linux-2.6-net-sky2-update-to-version-1-14-from-2-6-21.patch
Patch21571: linux-2.6-net-b44-ethernet-driver-update.patch
Patch21572: linux-2.6-net-ipw200-backports-from-2-6-22-rc1.patch
Patch21573: linux-2.6-net-bnx2-update-to-driver-version-1-5-11.patch
Patch21574: linux-2.6-net-e1000-update-to-driver-version-7-3-20-k2.patch
Patch21575: linux-2.6-net-softmac-updates-from-2-6-21.patch
Patch21576: linux-2.6-net-bcm43xx-backport-from-2-6-22-rc1.patch
Patch21577: linux-2.6-net-allow-packet-drops-during-ipsec-larval-state.patch
Patch21578: linux-2.6-pci-irqbalance-causes-oops-during-pci-removal.patch
Patch21579: linux-2.6-x86_64-fix-tsc-reporting-with-constant-tsc.patch
Patch21581: linux-2.6-acpi-acpi_prt-list-incomplete.patch
Patch21582: linux-2.6-drm-agpgart-and-drm-support-for-bearlake-graphics.patch
Patch21583: linux-2.6-net-cxgb3-initial-support-for-chelsio-t3-card.patch
Patch21584: linux-2.6-net-netxen-initial-support-for-netxen-10gbe-nic.patch
Patch21585: linux-2.6-xen-bimodal-drivers-protocol-header.patch
Patch21586: linux-2.6-xen-bimodal-drivers-pvfb-frontend.patch
Patch21587: linux-2.6-xen-bimodal-drivers-blkfront-driver.patch
Patch21588: linux-2.6-xen-binmodal-drivers-block-backends.patch
Patch21589: linux-2.6-xen-blktap-kill-bogous-flush.patch
Patch21590: linux-2.6-xen-blktap-cleanups.patch
Patch21591: linux-2.6-xen-blktap-race-fix-1.patch
Patch21592: linux-2.6-xen-blktap-race-2.patch
Patch21593: linux-2.6-xen-blkback-blktap-fix-id-type.patch
Patch21594: linux-2.6-xen-save-restore-fix.patch
Patch21595: linux-2.6-xen-ia64-fix-hvm-interrupts-on-ipf.patch
Patch21596: linux-2.6-xen-ia64-fix-xm-mem-set-hypercall-on-ia64.patch
Patch21597: linux-2.6-xen-xen0-can-not-startx-in-tiger4.patch
Patch21598: linux-2.6-xen-ia64-uncorrectable-error-make-hypervisor-hung.patch
Patch21599: linux-2.6-xen-change-to-new-intr-deliver-mechanism.patch
Patch21600: linux-2.6-xen-ia64-changed-foreign-domain-page-map-semantic.patch
Patch21601: linux-2.6-xen-ia64-evtchn_callback-fix-and-clean.patch
Patch21602: linux-2.6-xen-ia64-kernel-panics-when-dom0_mem-is-specified.patch
Patch21603: linux-2.6-xen-ia64-para-domain-vmcore-not-work-under-crash.patch
Patch21604: linux-2.6-xen-ia64-improve-performance-of-system-call.patch
Patch21605: linux-2.6-xen-ia64-set-irq_per_cpu-status-on-percpu-irqs.patch
Patch21606: linux-2.6-xen-ia64-fix-for-irq_desc-missing-in-new-upstream.patch
Patch21607: linux-2.6-xen-support-new-xm-command-xm-trigger.patch
Patch21608: linux-2.6-xen-ia64-cannot-measure-process-time-accurately.patch
Patch21609: linux-2.6-xen-ia64-skip-mca-setup-on-domu.patch
Patch21610: linux-2.6-xen-ia64-xm-save-restore-does-not-work.patch
Patch21611: linux-2.6-xen-ia64-use-generic-swiotlb-h-header.patch
Patch21612: linux-2.6-xen-ia64-fix-pv-on-hvm-driver.patch
Patch21613: linux-2.6-xen-change-interface-version-for-3-1.patch
Patch21614: linux-2.6-xen-expand-vnif-num-per-guest-domain-to-over-four.patch
Patch21615: linux-2.6-xen-x86_64-fix-fs-gs-registers-for-vt-bootup.patch
Patch21616: linux-2.6-net-s2io--native-support-for-pci-error-recovery.patch
Patch21617: linux-2.6-fs-fuse-minor-vfs-change.patch
Patch21618: linux-2.6-md-move-fn-call-that-could-block-outside-spinlock.patch
Patch21619: linux-2.6-scsi-raid1-goes-read-only-after-resync.patch
Patch21620: linux-2.6-ppc64-donate-cycles-from-dedicated-cpu.patch
Patch21622: linux-2.6-openib-kernel-backports-for-ofed-1-2-update.patch
Patch21623: linux-2.6-openib-update-ofed-code-to-1-2.patch
Patch21624: linux-2.6-net-fix-tx_checksum-flag-bug-in-qla3xxx-driver.patch
Patch21625: linux-2.6-s390-qdio-system-hang-with-zfcp-adapter-problems.patch
Patch21626: linux-2.6-input-i8042_interrupt-race-deliver-bytes-swapped.patch
Patch21627: linux-2.6-gfs2-panic-in-unlink.patch
Patch21628: linux-2.6-gfs2-posix-lock-fixes.patch
Patch21629: linux-2.6-misc-disable-pnpacpi-on-ibm-x460.patch
Patch21630: linux-2.6-misc-utrace-update.patch
Patch21631: linux-2.6-net-update-netxen_nic-driver-to-version-3-x-x.patch
Patch21632: linux-2.6-net-ixgb-update-to-driver-version-1-0-126-k2.patch
Patch21633: linux-2.6-ia64-altix-acpi-support.patch
Patch21634: linux-2.6-security-allow-nfs-nohide-and-selinux-to-work.patch
Patch21635: linux-2.6-nfs-closes-and-umounts-are-racing.patch
Patch21636: linux-2.6-x86_64-system-panic-on-boot-up-no-memory-in-node0.patch
Patch21637: linux-2.6-fs-setuid-program-unable-to-read-own-proc-pid-map.patch
Patch21638: linux-2.6-x86_64-fix-casting-issue-in-tick-divider-patch.patch
Patch21639: linux-2.6-sound-alsa-update.patch
Patch21640: linux-2.6-md-add-dm-rdac-hardware-handler.patch
Patch21641: linux-2.6-pata-ide-hotplug-support-promise-pata_pdc2027x.patch
Patch21642: linux-2.6-pci-pci-x-pci-express-read-control-interface.patch
Patch21643: linux-2.6-ide-cannot-find-ide-device-with-ati-amd-sb700.patch
Patch21644: linux-2.6-i2c-smbus-does-not-work-on-ati-amd-sb700-chipset.patch
Patch21645: linux-2.6-x86_64-c-state-divisor-not-functioning-correctly.patch
Patch21646: linux-2.6-agp-fix-amd-64-agp-aperture-validation.patch
Patch21648: linux-2.6-gfs2-assert-fail-writing-to-journaled-file-umount.patch
Patch21649: linux-2.6-xen-kdump-kexec-support.patch
Patch21650: linux-2.6-firewire-new-stack-technology-preview.patch
Patch21651: linux-2.6-sata-combined-mode-regression-fix.patch
Patch21652: linux-2.6-scsi-cciss-driver-updates.patch
Patch21654: linux-2.6-md-fix-eio-on-writes-after-log-failure.patch
Patch21655: linux-2.6-xen-ia64-kernel-panics-when-dom0_mem-is-specified_2.patch
Patch21656: linux-2.6-scsi-update-aic94xx-and-libsas-to-1-0-3.patch
Patch21657: linux-2.6-audit-oops-when-audit-disabled-with-files-watched.patch
Patch21658: linux-2.6-xen-fix-kexec-highmem-failure.patch
Patch21659: linux-2.6-ppc64-data-buffer-miscompare.patch
Patch21660: linux-2.6-audit-subtree-watching-cleanups.patch
Patch21661: linux-2.6-gfs2-igrab-of-inode-in-wrong-state.patch
Patch21663: linux-2.6-gfs2-eio-error-from-gfs2_block_truncate_page.patch
Patch21664: linux-2.6-gfs2-obtaining-no_formal_ino-from-directory-entry.patch
Patch21665: linux-2.6-gfs2-remove-i_mode-pass-from-nfs-file-handle.patch
Patch21666: linux-2.6-gfs2-inode-size-inconsistency.patch
Patch21668: linux-2.6-dm-allow-invalid-snapshots-to-be-activated.patch
Patch21669: linux-2.6-dlm-tcp-connection-to-dlm-port-blocks-operations.patch
Patch21670: linux-2.6-misc-overflow-in-capi-subsystem.patch
Patch21671: linux-2.6-nfs-nfsd-oops-when-exporting-krb5p-mount.patch
Patch21672: linux-2.6-scsi-check-portstates-before-invoking-target-scan.patch
Patch21673: linux-2.6-xen-ia64-enable-blktap-driver.patch
Patch21674: linux-2.6-ppc64-fix-64k-pages-with-kexec-on-hash-table.patch
Patch21675: linux-2.6-ppc64-ehea-driver-cause-panic-on-recv-vlan-packet.patch
Patch21676: linux-2.6-pci-unable-to-reserve-mem-region-on-module-reload.patch
Patch21677: linux-2.6-sata-add-hitachi-to-ncq-blacklist.patch
Patch21678: linux-2.6-gfs2-lockup-detected-in-databuf_lo_before_commit.patch
Patch21679: linux-2.6-gfs2-mounted-file-system-won-t-suspend.patch
Patch21680: linux-2.6-edac-panic-memory-corruption-on-non-kdump-kernels.patch
Patch21681: linux-2.6-wireless-iwlwifi-add-driver.patch
Patch21682: linux-2.6-linux-2.6-dlm-clear-othercon-ptrs-when-connection-closed.patch
Patch21683: linux-2.6-linux-2.6-dlm-fix-null-reference-in-send_ls_not_ready.patch
Patch21684: linux-2.6-linux-2.6-gfs2-soft-lockup-in-rgblk_search.patch
Patch21685: linux-2.6-linux-2.6-xen-fix-time-going-backwards-gettimeofday.patch
Patch21686: linux-2.6-utrace-zombie-to-exit_dead-before-release_task.patch
Patch21687: linux-2.6-sata-regression-in-support-for-third-party-module.patch
Patch21688: linux-2.6-nfs-re-enable-force-umount.patch
Patch21689: linux-2.6-xen-race-load-xenblk-ko-and-scan-lvm-partitions.patch
Patch21690: linux-2.6-gfs2-locksmith-revolver-deadlocks.patch
Patch21691: linux-2.6-gfs2-fix-an-oops-in-the-glock-dumping-code.patch
Patch21692: linux-2.6-scsi-cciss-re-add-missing-kmalloc.patch
Patch21693: linux-2.6-scsi-update-stex-driver.patch
Patch21694: linux-2.6-ppc64-axon-mem-does-not-handle-double-bit-errors.patch
Patch21695: linux-2.6-xen-netloop-do-not-clobber-cloned-skb-page-frags.patch
Patch21696: linux-2.6-cifs-fix-signing-sec-mount-options.patch
Patch21697: linux-2.6-cifs-respect-umask-when-unix-extensions-enabled.patch
Patch21698: linux-2.6-x86-fix-tscsync-frequency-transitions.patch
Patch21699: linux-2.6-ppc-disable-pci-e-compl-timeouts-on-i-o-adapters.patch
Patch21700: linux-2.6-gfs2-bug-relating-to-inherit_jdata-flag-on-inodes.patch
Patch21701: linux-2.6-scsi-adaptec-add-sc-58300-hba-pci-id.patch
Patch21702: linux-2.6-gfs2-reduce-number-of-gfs2_scand-processes-to-one.patch
Patch21703: linux-2.6-ppc-no-boot-hang-response-for-pci-e-errors.patch
Patch21704: linux-2.6-net-e1000e-initial-support.patch
Patch21705: linux-2.6-net-igb-initial-support.patch
Patch21706: linux-2.6-net-e1000-add-support-for-hp-mezzanine-cards.patch
Patch21707: linux-2.6-net-e1000-add-support-for-bolton-nics.patch
Patch21708: linux-2.6-fs-move-msdos-compat-ioctl-to-msdos-dir.patch
Patch21709: linux-2.6-fs-fix-vfat-compat-ioctls-on-64-bit-systems.patch
Patch21710: linux-2.6-ata-add-additional-device-ids-for-sb700.patch
Patch21711: linux-2.6-ppc-pci-host-bridge-i-o-window-not-starting-at-0.patch
Patch21712: linux-2.6-net-tg3-small-update-for-kdump-fix.patch
Patch21713: linux-2.6-ppc-4k-userspace-page-map-support-in-64k-kernels.patch
Patch21714: linux-2.6-net-forcedeth-fix-nic-poll.patch
Patch21715: linux-2.6-scsi-cciss-support-for-p700m.patch
Patch21716: linux-2.6-scsi-pci-shutdown-for-cciss-driver.patch
Patch21717: linux-2.6-dlm-fix-basts-for-granted-pr-waiting-cw.patch
Patch21718: linux-2.6-x86-support-in-fid-did-to-frequency-conversion.patch
Patch21719: linux-2.6-fix-restore-path-for-5-1-pv-guests.patch
Patch21720: linux-2.6-misc-i915_dma-fix-batch-buffer-security-bit.patch
Patch21721: linux-2.6-xen-use-xencons-xvc-by-default-on-non-x86.patch
Patch21722: linux-2.6-gfs2-invalid-metadata-block.patch
Patch21723: linux-2.6-audit-sub-tree-cleanups.patch
Patch21724: linux-2.6-audit-sub-tree-memory-leaks.patch
Patch21725: linux-2.6-sub-tree-signal-handling-fix.patch
Patch21726: linux-2.6-ppc-ehca-driver-use-remap_4k_pfn-in-64k-kernel.patch
Patch21727: linux-2.6-wireless-iwlwifi-update-to-version-1-0-0.patch
Patch21728: linux-2.6-xen-ia64-cannot-use-e100-and-ide-controller.patch
Patch21729: linux-2.6-ppc-dlpar-remove-i-o-resource-failed.patch
Patch21731: linux-2.6-xen-netfront-avoid-deref-skb-after-freed.patch
Patch21732: linux-2.6-misc-workaround-for-qla2xxx-vs-xen-swiotlb.patch
Patch21733: linux-2.6-net-tg3-pci-ids-missed-during-backport.patch
Patch21734: linux-2.6-agp-945-965gme-bridge-id-bug-fix-and-cleanups.patch
Patch21735: linux-2.6-net-forcedeth-optimize-the-tx-data-path.patch
Patch21736: linux-2.6-xen-ia64-allow-guests-to-vga-install.patch
Patch21737: linux-2.6-sound-audio-playback-does-not-work.patch
Patch21738: linux-2.6-scsi-fix-qla4xxx-underrun-and-online-handling.patch
Patch21739: linux-2.6-mm-prevent-the-stack-growth-into-hugetlb-regions.patch
Patch21740: linux-2.6-misc-miss-critical-phys_to_virt-in-lib-swiotlb-c.patch
Patch21741: linux-2.6-x86-blacklist-for-hp-dl585g2-and-hp-dc5700.patch
Patch21742: linux-2.6-ia64-fsys_gettimeofday-leaps-days-with-nojitter.patch
Patch21743: linux-2.6-xen-blktap-tries-to-access-beyond-end-of-disk.patch
Patch21744: linux-2.6-net-s2io-update-to-driver-version-2-0-25-1.patch
Patch21745: linux-2.6-scsi-cciss-increase-max-sectors-to-2048.patch
Patch21746: linux-2.6-misc-fix-broken-altsysrq-f.patch
Patch21747: linux-2.6-mm-separate-mapped-file-and-anon-page-in-show_mem.patch
Patch21748: linux-2.6-sound-fix-panic-in-hda_codec.patch
Patch21749: linux-2.6-misc-cpu-hotplug-notifiers-to-use-raw_notifier.patch
Patch21750: linux-2.6-x86_64-fix-mmio-config-space-quirks.patch
Patch21751: linux-2.6-gfs2-hang-when-using-a-large-sparse-quota-file.patch
Patch21752: linux-2.6-net-fix-dlpar-remove-of-ehea-logical-port.patch
Patch21753: linux-2.6-gfs2-unstuff-quota-inode.patch
Patch21754: linux-2.6-ppc-fix-detection-of-pci-e-based-devices.patch
Patch21755: linux-2.6-scsi-fix-iscsi-write-handling-regression.patch
Patch21756: linux-2.6-sound-support-ad1984-codec.patch
Patch21757: linux-2.6-fs-cifs-fix-deadlock-in-cifs_get_inode_info_unix.patch
Patch21758: linux-2.6-gfs2-panic-after-can-t-parse-mount-arguments.patch
Patch21759: linux-2.6-gfs2-fix-truncate-panic.patch
Patch21760: linux-2.6-scsi-sata-raid-150-4-6-do-not-support-64-bit-dma.patch
Patch21761: linux-2.6-scsi-uninitialized-field-in-gdth-c.patch
Patch21762: linux-2.6-audit-stop-multiple-messages-from-being-printed.patch
Patch21763: linux-2.6-2-scsi-cciss-set-max-command-queue-depth.patch
Patch21764: linux-2.6-ppc-eeh-better-status-string-detection.patch
Patch21765: linux-2.6-dlm-reuse-connections-rather-than-freeing-them.patch
Patch21766: linux-2.6-gfs2-more-problems-unstuffing-journaled-files.patch
Patch21767: linux-2.6-scsi-qla2xxx-disable-msi-x-by-default.patch
Patch21768: linux-2.6-gfs2-glock-dump-dumps-glocks-for-all-file-systems.patch
Patch21769: linux-2.6-misc-microphone-stops-working.patch
Patch21770: linux-2.6-fs-hugetlb-fix-prio_tree-unit.patch
Patch21771: linux-2.6-gfs2-bad-mount-option-causes-panic-null-sb-ptr.patch
Patch21772: linux-2.6-gfs2-fix-inode-meta-data-corruption.patch
Patch21773: linux-2.6-gfs2-distributed-mmap-test-cases-deadlock.patch
Patch21774: linux-2.6-net-tg3-update-to-fix-suspend-resume-problems.patch
Patch21775: linux-2.6-openib-fix-two-ipath-controllers-on-same-subnet.patch
Patch21776: linux-2.6-gfs2-fix-lock-ordering-of-unlink.patch
Patch21777: linux-2.6-nfs-nfs4-closes-and-umounts-are-racing.patch
Patch21778: linux-2.6-autofs-autofs4-fix-race-between-mount-and-expire.patch
Patch21779: linux-2.6-xen-fix-privcmd-to-remove-nopage-handler.patch
Patch21780: linux-2.6-misc-re-export-some-symbols-as-export_symbol_gpl.patch
Patch21781: linux-2.6-mm-madvise-call-to-kernel-loops-forever.patch
Patch21782: linux-2.6-net-igmp-check-null-when-allocate-gfp_atomic-skbs.patch
Patch21783: linux-2.6-net-qla3xxx-read-iscsi-target-disk-fail.patch
Patch21784: linux-2.6-scsi-iscsi-borked-kmalloc.patch
Patch21785: linux-2.6-scsi-qla2xxx-nvram-vpd-upd-produce-soft-lockups.patch
Patch21786: linux-2.6-xen-ia64-alloc-with-gfp_kernel-in-inter-ctxt-fix.patch
Patch21787: linux-2.6-ptrace-null-pointer-dereference-triggered.patch
Patch21788: linux-2.6-xen-allow-32-bit-xen-to-kdump-4g-physical-memory.patch
Patch21789: linux-2.6-s390-hypfs-inode-corruption-due-to-missing-lock.patch
Patch21790: linux-2.6-scsi-megaraid_sas-intercept-cmd-and-throttle-io.patch
Patch21791: linux-2.6-scsi-fusion-allow-vmwares-emulator-to-work-again.patch
Patch21792: linux-2.6-s390-qdio-refresh-buffer-for-iqdio-asynch-out-q.patch
Patch21793: linux-2.6-ppc64-fix-spu-slb-sz-and-invalid-hugepage-faults.patch
Patch21794: linux-2.6-misc-bounds-check-ordering-issue-in-random-driver.patch
Patch21795: linux-2.6-usb-usblcd-locally-triggerable-memory-consumption.patch
Patch21796: linux-2.6-nfs-enable-nosharecache-mounts-fixes.patch
Patch21797: linux-2.6-autofs4-fix-deadlock-during-directory-create.patch
Patch21798: linux-2.6-x86_64-fix-32-bit-ptrace-access-to-debug-regs.patch
Patch21799: linux-2.6-dlm-make-dlm_sendd-cond_resched-more.patch
Patch21800: linux-2.6-gfs2-move-inode-delete-logic-out-of-blocking_cb.patch
Patch21801: linux-2.6-gfs2-mount-hung-after-recovery.patch
Patch21802: linux-2.6-fs-reset-current-pdeath_signal-on-suid-execution.patch
Patch21803: linux-2.6-scsi-qlogic-nvram-vpd-update-memory-corruptions.patch
Patch21804: linux-2.6-gfs2-operations-hang-after-mount-resend.patch
Patch21805: linux-2.6-gfs2-allow-proc-to-handle-multiple-flocks-on-file.patch
Patch21806: linux-2.6-fs-ext3-do_split-leaves-free-space-in-both-blocks.patch
Patch21807: linux-2.6-net-s2io-check-for-error_state-in-isr.patch
Patch21808: linux-2.6-net-cxgb3-backport-fixups-and-sysfs-corrections.patch
Patch21809: linux-2.6-sata-libata-probing-fixes-and-other-cleanups.patch
Patch21810: linux-2.6-net-s2io-check-for-error_state-in-isr-more.patch
Patch21811: linux-2.6-gfs2-deadlock-run-revolver-load-with-lock_nolock.patch
Patch21812: linux-2.6-gfs2-fix-i_cache-stale-entry.patch
Patch21813: linux-2.6-x86_64-syscall-vulnerability.patch
Patch21814: linux-2.6-gfs2-solve-journal-release-invalidate-page-issues.patch
Patch21815: linux-2.6-scsi-aacraid-missing-ioctl-permission-checks.patch
Patch21816: linux-2.6-gfs2-gfs2_writepage-workaround.patch
Patch21817: linux-2.6-gfs2-dlm-schedule-during-recovery-loops.patch
Patch21818: linux-2.6-gfs2-get-super-block-a-different-way.patch
Patch21819: linux-2.6-net-iwlwifi-avoid-bug_on-in-tx-cmd-queue-process.patch
Patch21820: linux-2.6-sound-allow-creation-of-null-parent-devices.patch
Patch21821: linux-2.6-scsi-megaraid_sas-kabi-fix-for-proc-entries.patch
Patch21822: linux-2.6-gfs2-handle-multiple-demote-requests.patch
Patch21823: linux-2.6-net-bnx2-add-phy-workaround-for-5709-a1.patch
Patch21824: linux-2.6-cifs-fix-mem-corruption-due-to-bad-error-handling.patch
Patch21825: linux-2.6-audit-improper-handle-of-audit_log_start-ret-val.patch
Patch21826: linux-2.6-fs-jbd-wait-for-t_sync_datalist-buf-to-complete.patch
Patch21827: linux-2.6-mm-ia64-flush-i-cache-before-set_pte.patch
Patch21828: linux-2.6-x86-fixes-for-the-tick-divider-patch.patch
Patch21829: linux-2.6-alsa-convert-snd-page-alloc-proc-file-to-seq_file.patch
Patch21831: linux-2.6-ppc-kexec-kdump-kernel-hung-on-p5-and-p6.patch
Patch21832: linux-2.6-net-forcedeth-msi-interrupt-bugfix.patch
Patch21833: linux-2.6-net-tg3-fix-performance-regression-on-5705.patch
Patch21834: linux-2.6-nfs4-umounts-oops-in-shrink_dcache_for_umount.patch
Patch21835: linux-2.6-fs-sysfs-store-inode-nrs-in-s_ino.patch
Patch21836: linux-2.6-fs-sysfs-fix-condition-check-in-sysfs_drop_dentry.patch
Patch21837: linux-2.6-fs-sysfs-fix-race-condition-around-sd-s_dentry.patch
Patch21838: linux-2.6-net-ieee80211-off-by-two-integer-underflow.patch
Patch21839: linux-2.6-autofs4-fix-race-between-mount-and-expire-2.patch
Patch21840: linux-2.6-audit-still-alloc-contexts-when-audit-is-disabled.patch
Patch21841: linux-2.6-scsi-ibmvscsi-client-cant-handle-deactive-active.patch
Patch21842: linux-2.6-scsi-ibmvscsi-unable-to-cont-migrating-lpar-error.patch
Patch21843: linux-2.6-ppc-system-cpus-stuck-in-h_join-after-migrating.patch
Patch21844: linux-2.6-fs-missing-dput-in-do_lookup-error-leaks-dentries.patch
Patch21845: linux-2.6-misc-Remove-non-existing-SB600-raid-define.patch
Patch21846: linux-2.6-ia64-misc-DBS-cleanup.patch
Patch21847: linux-2.6-cifs-make-demux-thread-ignore-signals-from-userspa.patch
Patch21848: linux-2.6-net-NetXen-MSI-failed-interrupt-after-fw-enabled.patch
Patch21849: linux-2.6-net-sctp-rewrite-receive-buffer-management-code.patch
Patch21850: linux-2.6-misc-serial-assert-DTR-for-serial-console-devices.patch
Patch21851: linux-2.6-hotplug-acpiphp-cannot-get-bridge-info-with-PCI.patch
Patch21852: linux-2.6-misc-Prevent-NMI-watchdog-triggering-during-sysrq.patch
Patch21853: linux-2.6-usb-Support-for-EPiC-based-io_edgeport-devices.patch
Patch21854: linux-2.6-tux-fix-crashes-during-shutdown.patch
Patch21855: linux-2.6-misc-serial-fix-console-hang-on-HP-Integrity.patch
Patch21856: linux-2.6-net-ipv6-support-RFC4193-local-unicast-addresses.patch
Patch21857: linux-2.6-acpi-sbs-file-permissions-set-incorrectly.patch
Patch21858: linux-2.6-i2c-SB600-700-800-use-same-SMBus-controller-devID.patch
Patch21859: linux-2.6-net-lvs-syncdaemon-causes-high-avg-load-on-system.patch
Patch21860: linux-2.6-x86_64-Switching-to-vsyscall64-causes-oops.patch
Patch21861: linux-2.6-fs-aio-account-for-I-O-wait-properly.patch
Patch21862: linux-2.6-char-tty-set-pending_signal-on-return-ERESTARTSY.patch
Patch21863: linux-2.6-net-fix-race-condition-in-netdev-name-allocation.patch
Patch21864: linux-2.6-net-fail-multicast-with-connection-oriented-socket.patch
Patch21865: linux-2.6-ide-allow-disabling-of-drivers.patch
Patch21866: linux-2.6-fs-Fix-unserialized-task-files-changing.patch
Patch21867: linux-2.6-ia64-remove-stack-hard-limit.patch
Patch21868: linux-2.6-misc-add-vmcoreinfo-support-to-kernel.patch
Patch21869: linux-2.6-scsi-always-update-request-data_len-with-resid.patch
Patch21870: linux-2.6-ext3-orphan-list-check-on-destroy_inode.patch
Patch21871: linux-2.6-scsi-stale-residual-on-write-following-BUSY-retry.patch
Patch21872: linux-2.6-misc-cfq-iosched-fix-deadlock-on-nbd-writes.patch
Patch21873: linux-2.6-audit-collect-events-for-segfaulting-programs.patch
Patch21874: linux-2.6-misc-softirq-remove-spurious-BUG_ON-s.patch
Patch21875: linux-2.6-hotplug-acpiphp-System-error-during-PCI-hotplug.patch
Patch21876: linux-2.6-x86_64-Add-NX-mask-for-PTE-entry.patch
Patch21877: linux-2.6-ppc64-boot-Cell-blades-with-2GB-memory.patch
Patch21878: linux-2.6-ppc64-panic-on-DLPAR-remove-of-eHEA.patch
Patch21879: linux-2.6-ia64-fix-vga-corruption-with-term-blanking-disable.patch
Patch21880: linux-2.6-net-panic-when-mounting-with-insecure-ports.patch
Patch21881: linux-2.6-gfs2-Fix-ordering-of-page-lock-and-transaction-loc.patch
Patch21882: linux-2.6-net-ibmveth-fix-rx-pool-deactivate-oops.patch
Patch21883: linux-2.6-net-ibmveth-h_free_logical_lan-err-on-pool-resize.patch
Patch21884: linux-2.6-net-ibmveth-enable-large-rx-buf-pool-for-large-mt.patch
Patch21885: linux-2.6-ata-SB800-SATA-IDE-LAN-support.patch
Patch21886: linux-2.6-ppc64-eHEA-ibm-loc-code-not-unique.patch
Patch21887: linux-2.6-ia64-add-driver-for-ACPI-methods-to-call-native-fw.patch
Patch21888: linux-2.6-ia64-add-global-ACPI-OpRegion-handler-for-fw-calls.patch
Patch21889: linux-2.6-x86_64-update-IO-APIC-dest-field-to-8-bit-for-xAPI.patch
Patch21890: linux-2.6-GFS2-sysfs-id-file-should-contain-device-id.patch
Patch21891: linux-2.6-ppc64-Remove-WARN_ON-from-disable_msi_mode.patch
Patch21892: linux-2.6-misc-lockdep-fix-seqlock_init.patch
Patch21893: linux-2.6-serial-support-pci-express-icom-devices.patch
Patch21894: linux-2.6-ppc64-kdump-fix-irq-distribution-on-ppc970.patch
Patch21895: linux-2.6-hotplug-slot-poweroff-problem-on-systems-w-o-_ps3.patch
Patch21896: linux-2.6-net-clean-up-in-kernel-socket-api-usage.patch
Patch21897: linux-2.6-net-netxen-allow-module-to-unload.patch
Patch21898: linux-2.6-ia64-kdump-deal-with-empty-image.patch
Patch21899: linux-2.6-ia64-validate-and-remap-mmap-requests.patch
Patch21900: linux-2.6-ia64-ioremap-rename-variables-to-match-i386.patch
Patch21901: linux-2.6-ia64-ioremap-avoid-unsupported-attributes.patch
Patch21902: linux-2.6-ia64-ioremap-allow-cacheable-mmaps-of-legacy_mem.patch
Patch21903: linux-2.6-ia64-ioremap-fail-mmaps-with-incompat-attributes.patch
Patch21904: linux-2.6-net-cipso-packets-generate-kernel-unaligned-access.patch
Patch21905: linux-2.6-ia64-proc-iomem-wiped-out-on-non-acpi-kernel.patch
Patch21906: linux-2.6-x86_64-ide0-noprobe-crashes-the-kernel.patch
Patch21907: linux-2.6-misc-fix-relay-read-start-position.patch
Patch21908: linux-2.6-misc-fix-relay-read-start-in-overwrite-mode.patch
Patch21909: linux-2.6-ia64-enable-kprobe-s-trap-code-on-slot-1.patch
Patch21910: linux-2.6-nfs-nfs_symlink-allocate-page-with-gfp_highuser.patch
Patch21911: linux-2.6-input-psmouse-add-support-to-cortps-protocol.patch
Patch21912: linux-2.6-x86_64-kdump-shutdown-gart-on-k8-systems.patch
Patch21913: linux-2.6-net-kernel-needs-to-support-tcp_rto_min.patch
Patch21914: linux-2.6-misc-proc-pid-environ-stops-at-4k-bytes.patch
Patch21915: linux-2.6-net-labeled-memory-leak-calling-secid_to_secctx.patch
Patch21916: linux-2.6-ppc64-mpstat-reports-wrong-per-processor-stats.patch
Patch21917: linux-2.6-net-ppp_mppe-avoid-using-a-copy-of-interim-key.patch
Patch21918: linux-2.6-ia64-show_mem-printk-cleanup.patch
Patch21919: linux-2.6-ia64-discontig-show_mem-cleanup-output.patch
Patch21920: linux-2.6-ia64-contig-show_mem-cleanup-output.patch
Patch21921: linux-2.6-misc-sched-force-sbin-init-off-isolated-cpus.patch
Patch21922: linux-2.6-misc-allow-a-hyphenated-range-for-isolcpus.patch
Patch21923: linux-2.6-net-ibmveth-checksum-offload-support.patch
Patch21924: linux-2.6-misc-intel-tolapai-sata-and-i2c-support.patch
Patch21925: linux-2.6-scsi-cciss-disable-refetch-on-p600.patch
Patch21926: linux-2.6-edac-fix-return-code-in-e752x_edac-probe-function.patch
Patch21927: linux-2.6-ide-sb700-contains-two-ide-channels.patch
Patch21928: linux-2.6-net-qla3xxx-new-4032-does-not-work-with-vlan.patch
Patch21929: linux-2.6-selinux-don-t-oops-when-using-non-mls-policy.patch
Patch21930: linux-2.6-xen-ia64-fix-free_irq_vector-double-free.patch
Patch21931: linux-2.6-crypto-aes-rename-aes-to-aes-generic.patch
Patch21932: linux-2.6-net-ipv6-backport-optimistic-dad.patch
Patch21933: linux-2.6-mm-xen-memory-tracking-cleanups.patch
Patch21934: linux-2.6-mm-xen-export-xen_create_contiguous_region.patch
Patch21935: linux-2.6-xen-inteface-with-stratus-platform-op.patch
Patch21936: linux-2.6-ia64-bte_unaligned_copy-transfers-extra-cache-line.patch
Patch21937: linux-2.6-xen-ia64-make-ioremapping-work.patch
Patch21938: linux-2.6-fs-proc-add-proc-pid-limits.patch
Patch21939: linux-2.6-nfs-set-attrmask-on-nfs4_create_exclusive-reply.patch
Patch21940: linux-2.6-nfs-reset-any-fields-set-in-attrmask.patch
Patch21941: linux-2.6-x86-add-greyhound-event-based-profiling-support.patch
Patch21942: linux-2.6-ppc64-add-at_null-terminator-to-auxiliary-vector.patch
Patch21943: linux-2.6-ppc64-make-the-vdso-handle-c-unwinding-correctly.patch
Patch21944: linux-2.6-x86-hotplug-pci-memory-resource-mis-allocation.patch
Patch21945: linux-2.6-usb-reset-leds-on-dell-keyboards.patch
Patch21946: linux-2.6-s390-cio-reipl-fails-after-channel-path-reset.patch
Patch21947: linux-2.6-s390-cio-device-status-validity.patch
Patch21948: linux-2.6-s390-cio-fix-memory-leak-when-deactivating.patch
Patch21949: linux-2.6-s390-cio-dynamic-chpid-reconfiguration-via-sclp.patch
Patch21950: linux-2.6-s390-cio-handle-invalid-subchannel-setid-in-stsch.patch
Patch21951: linux-2.6-s390-qeth-use-correct-mac-address-on-recovery.patch
Patch21952: linux-2.6-s390-qeth-up-sequence-number-for-incoming-packets.patch
Patch21954: linux-2.6-s390-qeth-default-performace_stats-attribute-to-0.patch
Patch21955: linux-2.6-s390-qeth-do-not-free-memory-on-failed-init.patch
Patch21956: linux-2.6-s390-panic-with-lcs-interface-as-dhcp-server.patch
Patch21957: linux-2.6-dlm-don-t-overwrite-castparam-if-it-s-null.patch
Patch21958: linux-2.6-nfs-support-32-bit-client-and-64-bit-inode-numbers.patch
Patch21959: linux-2.6-nfs-server-support-32-bit-client-and-64-bit-inodes.patch
Patch21960: linux-2.6-x86-use-pci-bfsort-on-dell-r900.patch
Patch21961: linux-2.6-utrace-s390-regs-fixes.patch
Patch21962: linux-2.6-serial-irq-1-assigned-to-serial-port.patch
Patch21963: linux-2.6-ia64-mm-register-backing-store-bug.patch
Patch21964: linux-2.6-mm-oom-prevent-from-killing-several-processes.patch
Patch21965: linux-2.6-nfs-fix-attr_kill_s-id-handling-on-nfs.patch
Patch21966: linux-2.6-misc-systemtap-uprobes-access_process_vm-export.patch
Patch21967: linux-2.6-x86-change-command-line-size-to-2048.patch
Patch21968: linux-2.6-x86-use-pci-bfsort-for-certain-boxes.patch
Patch21969: linux-2.6-misc-fix-bogus-softlockup-warnings.patch
Patch21970: linux-2.6-misc-pass-regs-struct-to-softlockup_tick.patch
Patch21971: linux-2.6-misc-backport-upstream-softlockup_tick-code.patch
Patch21972: linux-2.6-misc-use-touch_softlockup_watchdog-when-no-nmi-wd.patch
Patch21973: linux-2.6-fs-udf-use-sector_t-and-loff_t-for-file-offsets.patch
Patch21974: linux-2.6-fs-udf-introduce-struct-extent_position.patch
Patch21975: linux-2.6-fs-udf-use-get_bh.patch
Patch21976: linux-2.6-fs-udf-add-assertions.patch
Patch21977: linux-2.6-fs-udf-support-files-larger-than-1g.patch
Patch21978: linux-2.6-fs-udf-fix-possible-data-corruption.patch
Patch21979: linux-2.6-fs-udf-fix-possible-leakage-of-blocks.patch
Patch21980: linux-2.6-md-dm-bd_mount_sem-counter-corruption.patch
Patch21981: linux-2.6-md-dm-panic-on-shrinking-device-size.patch
Patch21982: linux-2.6-fs-dm-crypt-memory-leaks-and-workqueue-exhaustion.patch
Patch21983: linux-2.6-ppc64-fixes-ptrace_set_debugreg-request.patch
Patch21984: linux-2.6-fs-ignore-siocifcount-ioctl-calls.patch
Patch21985: linux-2.6-misc-irqpoll-misrouted-interrupts-deadlocks.patch
Patch21999: linux-2.6-net-sunrpc-fix-hang-due-to-eventd-deadlock.patch
Patch22000: linux-2.6-s390-use-ipl-clear-for-reipl-under-z-vm.patch
Patch22001: linux-2.6-ppc64-cell-support-pinhole-reset-on-blades.patch
Patch22002: linux-2.6-ppc64-export-last_pid.patch
Patch22003: linux-2.6-ppc64-spufs-feature-updates.patch
Patch22004: linux-2.6-ppc64-typo-with-mmio_read_fixup.patch
Patch22005: linux-2.6-ppc64-cbe_cpufreq-fixes-from-2-6-23-rc7.patch
Patch22006: linux-2.6-ppc64-sysfs-support-for-add-remove-cpu-sysfs-attr.patch
Patch22007: linux-2.6-ppc64-spu-add-temperature-and-throttling-support.patch
Patch22008: linux-2.6-ppc64-cell-ddr2-memory-driver-for-axon.patch
Patch22009: linux-2.6-ppc64-cell-enable-rtas-based-ptcal-for-xdr-memory.patch
Patch22010: linux-2.6-ppc64-cell-support-for-msi-on-axon.patch
Patch22011: linux-2.6-xen-avoid-dom0-hang-when-disabling-pirq-s.patch
Patch22012: linux-2.6-nfs-introducde-nfs_removeargs-and-nfs_removeres.patch
Patch22013: linux-2.6-nfs-infrastructure-changes-for-silly-renames.patch
Patch22014: linux-2.6-nfs-clean-up-the-silly-rename-code.patch
Patch22015: linux-2.6-nfs-fix-a-race-in-silly-rename.patch
Patch22016: linux-2.6-nfs-let-rpciod-finish-sillyrename-then-umount.patch
Patch22017: linux-2.6-xen-pvfb-frontend-can-send-bogus-screen-updates.patch
Patch22018: linux-2.6-ppc64-handle-alignment-faults-on-new-fp-load-store.patch
Patch22019: linux-2.6-ppc64-slb-shadow-buffer-support.patch
Patch22020: linux-2.6-x86-report_lost_ticks-fix-up.patch
Patch22021: linux-2.6-gfs2-remove-permission-checks-from-xattr-ops.patch
Patch22022: linux-2.6-dlm-dump-more-lock-values.patch
Patch22023: linux-2.6-dlm-zero-unused-parts-of-sockaddr_storage.patch
Patch22024: linux-2.6-dlm-fix-memory-leak-in-dlm_add_member.patch
Patch22025: linux-2.6-dlm-block-dlm_recv-in-recovery-transition.patch
Patch22026: linux-2.6-dlm-tcp-bind-connections-from-known-local-address.patch
Patch22027: linux-2.6-dlm-don-t-print-common-non-errors.patch
Patch22028: linux-2.6-gfs2-check-kthread_should_stop-when-waiting.patch
Patch22029: linux-2.6-gfs2-recursive-locking-on-rgrp-in-gfs2_rename.patch
Patch22030: linux-2.6-net-backport-of-functions-for-sk_buff-manipulation.patch
Patch22031: linux-2.6-scsi-ipr-add-dual-sas-raid-controller-support.patch
Patch22032: linux-2.6-ppc64-utrace-fix-ptrace_getvrregs-data.patch
Patch22033: linux-2.6-scsi-update-lpfc-driver-to-8-2-0-8.patch
Patch22034: linux-2.6-ppc64-spufs-context-destroy-vs-readdir-race.patch
Patch22035: linux-2.6-cpufreq-rewrite-lock-to-eliminate-hotplug-issues.patch
Patch22036: linux-2.6-cpufreq-ondemand-governor-restructure-the-work-cb.patch
Patch22037: linux-2.6-cpufreq-governor-use-new-rwsem-locking-in-work-cb.patch
Patch22038: linux-2.6-cpufreq-remove-hotplug-cpu-cruft.patch
Patch22039: linux-2.6-cpufreq-don-t-take-sem-in-cpufreq_quick_get.patch
Patch22040: linux-2.6-fs-core-dump-file-ownership.patch
Patch22041: linux-2.6-net-sunrpc-lockd-recovery-is-broken.patch
Patch22042: linux-2.6-ipmi-fix-memory-leak-in-try_init_dmi.patch
Patch22043: linux-2.6-ipmi-do-not-enable-interrupts-too-early.patch
Patch22044: linux-2.6-ipmi-remove-superfluous-semapahore-from-watchdog.patch
Patch22045: linux-2.6-ipmi-add-ppc-si-support.patch
Patch22046: linux-2.6-ipmi-legacy-ioport-setup-changes.patch
Patch22047: linux-2.6-usb-fix-for-error-path-in-rndis.patch
Patch22048: linux-2.6-ppc64-power6-spurr-support.patch
Patch22049: linux-2.6-net-sunhme-fix-failures-on-x86.patch
Patch22050: linux-2.6-x86_64-fix-race-conditions-in-setup_apic_timer.patch
Patch22051: linux-2.6-misc-denial-of-service-with-wedged-processes.patch
Patch22052: linux-2.6-misc-tux-get-rid-of-o_atomiclookup.patch
Patch22053: linux-2.6-xen-fix-behavior-of-invalid-guest-page-mapping.patch
Patch22054: linux-2.6-x86-fix-race-with-endflag-in-nmi-setup-code.patch
Patch22055: linux-2.6-md-dm-mpath-add-hp-handler.patch
Patch22056: linux-2.6-md-dm-mpath-add-retry-pg-init.patch
Patch22057: linux-2.6-md-dm-mpath-hp-retry-if-not-ready.patch
Patch22058: linux-2.6-mm-soft-lockups-when-allocing-mem-on-large-systems.patch
Patch22059: linux-2.6-net-s2io-allow-vlan-creation-on-interfaces.patch
Patch22060: linux-2.6-net-s2io-correct-vlan-frame-reception.patch
Patch22061: linux-2.6-sched-fair-scheduler.patch
Patch22062: linux-2.6-nfs4-client-set-callback-address-properly.patch
Patch22063: linux-2.6-net-cifs-stock-1-50c-import.patch
Patch22064: linux-2.6-fs-cifs-small-fixes-to-make-cifs-1-50c-compile.patch
Patch22065: linux-2.6-fs-cifs-bad-handling-of-eagain-on-kernel_recvmsg.patch
Patch22066: linux-2.6-fs-cifs-fix-spurious-reconnect-on-2nd-peek.patch
Patch22067: linux-2.6-fs-cifs-oops-on-second-mount-to-same-server.patch
Patch22068: linux-2.6-fs-cifs-log-better-errors-on-failed-mounts.patch
Patch22069: linux-2.6-fs-cifs-buffer-overflow-due-to-corrupt-response.patch
Patch22070: linux-2.6-fs-cifs-fix-memory-leak-in-statfs-to-old-servers.patch
Patch22071: linux-2.6-fs-cifs-reduce-corrupt-list-in-find_writable_file.patch
Patch22072: linux-2.6-fs-cifs-shut-down-cifsd-when-signing-mount-fails.patch
Patch22073: linux-2.6-fs-cifs-fix-error-message-about-packet-signing.patch
Patch22074: linux-2.6-fs-cifs-missing-mount-helper-causes-wrong-slash.patch
Patch22075: linux-2.6-fs-cifs-corrupt-data-with-cached-dirty-page-write.patch
Patch22076: linux-2.6-fs-cifs-endian-conversion-problem-in-posix-mkdir.patch
Patch22077: linux-2.6-fs-cifs-update-changes-file-and-version-string.patch
Patch22078: linux-2.6-xen-xenbus-has-use-after-free.patch
Patch22079: linux-2.6-md-dm-crypt-possible-max_phys_segments-violation.patch
Patch22080: linux-2.6-md-dm-snapshot-excessive-memory-usage.patch
Patch22081: linux-2.6-xen-kernel-cpu-frequency-scaling.patch
Patch22082: linux-2.6-net-ixgb-resync-upstream-and-transmit-hang-fixes.patch
Patch22083: linux-2.6-net-fix-refcnt-leak-in-optimistic-dad-handling.patch
Patch22084: linux-2.6-xen-rapid-block-device-plug-unplug-leads-to-crash.patch
Patch22085: linux-2.6-audit-netmask-on-xfrm-policy-configuration-changes.patch
Patch22086: linux-2.6-usb-wacom-fix-side-and-extra-mouse-buttons.patch
Patch22087: linux-2.6-xen-support-for-architectural-pstate-driver.patch
Patch22088: linux-2.6-acpi-docking-undocking-support.patch
Patch22089: linux-2.6-acpi-docking-undocking-add-sysfs-support.patch
Patch22090: linux-2.6-acpi-docking-undocking-error-handling-in-init.patch
Patch22091: linux-2.6-acpi-docking-undocking-check-if-parent-is-on-dock.patch
Patch22092: linux-2.6-acpi-docking-undocking-oops-when-_dck-eval-fails.patch
Patch22093: linux-2.6-md-mirror-presuspend-causing-cluster-mirror-hang.patch
Patch22094: linux-2.6-md-dm-mirror-shedule_timeout-call-causes-slowdown.patch
Patch22095: linux-2.6-md-dm-mirror-write_callback-might-deadlock.patch
Patch22096: linux-2.6-scsi-aacraid-update-to-1-1-5-2453.patch
Patch22097: linux-2.6-net-sunrpc-make-clients-take-ref-to-rpciod-workq.patch
Patch22098: linux-2.6-net-tg3-update-to-upstream-version-3-86.patch
Patch22099: linux-2.6-net-bnx2-update-to-upstream-version-1-6-9.patch
Patch22100: linux-2.6-ia64-utrace-forbid-ptrace-changes-psr-ri-to-3.patch
Patch22101: linux-2.6-ia64-ptrace-access-to-user-register-backing.patch
Patch22102: linux-2.6-misc-utrace-update-for-5-2.patch
Patch22103: linux-2.6-net-bonding-update-to-upstream-version-3-2-2.patch
Patch22104: linux-2.6-net-bonding-documentation-update.patch
Patch22105: linux-2.6-ia64-fix-kernel-warnings-from-rpm-prep-stage.patch
Patch22106: linux-2.6-ppc64-ehea-sync-with-upstream.patch
Patch22107: linux-2.6-scsi-qla2xxx-upstream-improvements-and-cleanups.patch
Patch22108: linux-2.6-scsi-qla2xxx-8-gb-s-support.patch
Patch22109: linux-2.6-scsi-qla2xxx-more-improvements-and-cleanups-part2.patch
Patch22110: linux-2.6-mm-make-compound-page-destructor-handling-explicit.patch
Patch22111: linux-2.6-mm-fix-hugepage-allocation-with-memoryless-nodes.patch
Patch22112: linux-2.6-x86-edac-add-support-for-intel-i3000.patch
Patch22113: linux-2.6-x86_64-nmi-watchdog-incorrect-logic-for-amd-chips.patch
Patch22114: linux-2.6-fs-nfs-byte-range-locking-support-for-cfs.patch
Patch22115: linux-2.6-misc-tlclk-driver-for-telco-blade-systems.patch
Patch22116: linux-2.6-md-fix-bitmap-support.patch
Patch22117: linux-2.6-ppc64-unequal-allocation-of-hugepages.patch
Patch22118: linux-2.6-x86-cpuinfo-list-dynamic-acceleration-technology.patch
Patch22119: linux-2.6-x86_64-calioc2-iommu-support.patch
Patch22120: linux-2.6-scsi-update-megaraid_sas-to-version-3-15.patch
Patch22121: linux-2.6-audit-race-checking-audit_context-and-loginuid.patch
Patch22122: linux-2.6-md-dm-ioctl-fix-32bit-compat-layer.patch
Patch22123: linux-2.6-misc-ioat-dma-support-unisys.patch
Patch22124: linux-2.6-misc-offlining-a-cpu-with-realtime-process-running.patch
Patch22125: linux-2.6-scsi-mpt-fusion-pci-ids-for-version-3-04-05.patch
Patch22126: linux-2.6-scsi-mpt-fusion-add-accessor-for-version-3-04-05.patch
Patch22127: linux-2.6-scsi-mpt-fusion-update-to-version-3-04-05.patch
Patch22128: linux-2.6-misc-revert-add-vmcoreinfo-support-to-kernel.patch
Patch22129: linux-2.6-kexec-fix-vmcoreinfo-patch-that-breaks-kdump.patch
Patch22130: linux-2.6-net-forcedeth-boot-delay-fix.patch
Patch22131: linux-2.6-misc-export-radix-tree-preload.patch
Patch22132: linux-2.6-scsi-mpt-fusion-fix-sas-hotplug.patch
Patch22133: linux-2.6-scsi-qla2xxx-add-support-for-npiv.patch
Patch22134: linux-2.6-scsi-qla2xxx-pci-ee-error-handling-support.patch
Patch22135: linux-2.6-scsi-qla2xxx-add-support-for-npiv-firmware.patch
Patch22136: linux-2.6-misc-enable-s-pdif-in-fila-converse.patch
Patch22137: linux-2.6-x86-add-warning-to-nmi-failure-message.patch
Patch22138: linux-2.6-net-ipv6-ip6_mc_input-sense-of-promiscuous-test.patch
Patch22139: linux-2.6-scsi-qla2xxx-msi-x-hardware-issues-on-platforms.patch
Patch22140: linux-2.6-scsi-stex-use-resid-for-xfer-len-information.patch
Patch22141: linux-2.6-fs-ext3-error-in-ext3_lookup-if-corruption-found.patch
Patch22142: linux-2.6-misc-edac-add-support-for-intel-5000-mchs.patch
Patch22143: linux-2.6-scsi-qla2xxx-rediscovering-luns-takes-5-min.patch
Patch22144: linux-2.6-scsi-lpfc-update-to-version-8-2-0-13.patch
Patch22145: linux-2.6-sched-return-first-time_slice-to-correct-process.patch
Patch22146: linux-2.6-fs-executing-binaries-with-2gb-debug-info.patch
Patch22147: linux-2.6-misc-core-dump-masking-support.patch
Patch22148: linux-2.6-misc-fix-softlockup-warnings-crashes.patch
Patch22149: linux-2.6-audit-log-eintr-not-erestartsys.patch
Patch22150: linux-2.6-net-dod-ipv6-conformance.patch
Patch22151: linux-2.6-xen-save-restore-pv-oops-when-mmap-prot_none.patch
Patch22152: linux-2.6-alsa-support-for-realtek-alc888s.patch
Patch22153: linux-2.6-misc-fix-raw_spinlock_t-vs-lockdep.patch
Patch22154: linux-2.6-lockdep-sanitise-config_prove_locking.patch
Patch22155: linux-2.6-lockdep-lockstat-core-infrastructure.patch
Patch22156: linux-2.6-lockdep-lockstat-human-readability-tweaks.patch
Patch22157: linux-2.6-lockdep-lockstat-hook-into-the-lock-primitives.patch
Patch22158: linux-2.6-lockdep-various-fixes.patch
Patch22159: linux-2.6-lockdep-fixup-sk_callback_lock-annotation.patch
Patch22160: linux-2.6-lockdep-lockstat-measure-lock-bouncing.patch
Patch22161: linux-2.6-lockdep-lockstat-better-class-name-representation.patch
Patch22162: linux-2.6-lockdep-lockstat-documentation.patch
Patch22163: linux-2.6-lockdep-avoid-lockdep-lock_stat-infinite-output.patch
Patch22164: linux-2.6-lockdep-mismatched-lockdep_depth-curr_chain_hash.patch
Patch22165: linux-2.6-lockdep-fixup-mutex-annotations.patch
Patch22166: linux-2.6-lockdep-make-cli-sti-annotation-warnings-clearer.patch
Patch22167: linux-2.6-alsa-disabling-microphone-in-bios-panics-kernel.patch
Patch22168: linux-2.6-aio-account-for-i-o-wait-properly.patch
Patch22169: linux-2.6-scsi-iscsi_tcp-update.patch
Patch22170: linux-2.6-net-null-dereference-in-iwl-driver.patch
Patch22171: linux-2.6-net-infrastructure-updates-to-mac80211-iwl4965.patch
Patch22172: linux-2.6-net-cfg80211-updates-to-support-mac80211-iwl4965.patch
Patch22173: linux-2.6-net-mac80211-updates.patch
Patch22174: linux-2.6-net-iwl4965-updates.patch
Patch22175: linux-2.6-net-ixgbe-support-for-new-intel-10gbe-hardware.patch
Patch22176: linux-2.6-net-bnx2x-support-broadcom-10gbe-hardware.patch
Patch22177: linux-2.6-net-cxgb3-update-to-latest-upstream.patch
Patch22178: linux-2.6-audit-log-uid-auid-and-comm-in-obj_pid-records.patch
Patch22179: linux-2.6-audit-add-session-id-to-easily-correlate-records.patch
Patch22180: linux-2.6-net-r8169-support-realtek-8111c-and-8101e-loms.patch
Patch22181: linux-2.6-cpufreq-fix-non-smp-compile-and-warning.patch
Patch22182: linux-2.6-firewire-fix-uevent-to-handle-hotplug.patch
Patch22183: linux-2.6-fs-ecryptfs-backport-from-2-6-24-rc4.patch
Patch22184: linux-2.6-fs-ecryptfs-stacking-functions-from-upstream-vfs.patch
Patch22185: linux-2.6-fs-ecryptfs-convert-to-vfsmount-dentry.patch
Patch22186: linux-2.6-fs-ecryptfs-backport-f_path-to-f_dentry.patch
Patch22187: linux-2.6-fs-ecryptfs-backport-generic_file_aio_read.patch
Patch22188: linux-2.6-fs-ecryptfs-backport-sysf-api-for-kobjects-ksets.patch
Patch22189: linux-2.6-fs-ecryptfs-backport-to-rhel5-memory-alloc-api.patch
Patch22190: linux-2.6-fs-ecryptfs-convert-to-memclear_highpage_flush.patch
Patch22191: linux-2.6-fs-ecryptfs-un-constify-ops-vectors.patch
Patch22192: linux-2.6-fs-ecryptfs-backport-to-rhel5-cipher-api.patch
Patch22193: linux-2.6-fs-ecryptfs-backport-to-crypto-hash-api.patch
Patch22194: linux-2.6-fs-ecryptfs-backport-to-rhel5-scatterlist-api.patch
Patch22195: linux-2.6-fs-ecryptfs-backport-to-rhel5-netlink-api.patch
Patch22196: linux-2.6-fs-ecryptfs-connect-sendfile-ops.patch
Patch22197: linux-2.6-fs-ecryptfs-upstream-fixes.patch
Patch22198: linux-2.6-fs-ecryptfs-redo-dget-mntget-on-dentry_open-fail.patch
Patch22199: linux-2.6-fs-ecryptfs-check-for-existing-key_tfm-at-mount.patch
Patch22200: linux-2.6-x86-add-pci-quirk-to-ht-enabled-systems.patch
Patch22201: linux-2.6-ia64-altix-acpi-iosapic-warning-cleanup.patch
Patch22202: linux-2.6-xen-ia64-cannot-create-guest-having-100gb-memory.patch
Patch22203: linux-2.6-xen-ia64-fix-ssm_i-emulation-barrier-and-vdso-pv.patch
Patch22204: linux-2.6-crypto-api-add-new-top-level-crypto_api.patch
Patch22205: linux-2.6-crypto-api-add-new-bottom-level-crypto_api.patch
Patch22206: linux-2.6-crypto-api-add-cryptomgr.patch
Patch22207: linux-2.6-crypto-skcipher-add-skcipher-infrastructure.patch
Patch22208: linux-2.6-crypto-chainiv-add-chain-iv-generator.patch
Patch22209: linux-2.6-crypto-eseqiv-add-encrypted-seq-num-iv-generator.patch
Patch22210: linux-2.6-crypto-api-add-aead-crypto-type.patch
Patch22211: linux-2.6-crypto-seqiv-add-seq-num-iv-generator.patch
Patch22212: linux-2.6-crypto-cipher-added-encrypt_one-decrypt_one.patch
Patch22213: linux-2.6-crypto-cipher-added-block-ciphers-for-cbc-ecb.patch
Patch22214: linux-2.6-crypto-digest-added-user-api-for-new-hash-type.patch
Patch22215: linux-2.6-crypto-tcrypt-use-skcipher-interface.patch
Patch22216: linux-2.6-crypto-tcrypt-hmac-template-and-hash-interface.patch
Patch22217: linux-2.6-crypto-hmac-add-crypto-template-implementation.patch
Patch22218: linux-2.6-crypto-ctr-add-ctr-block-cipher-mode.patch
Patch22219: linux-2.6-crypto-tcrypt-add-aead-support.patch
Patch22220: linux-2.6-crypto-ccm-added-ccm-mode.patch
Patch22221: linux-2.6-crypto-xcbc-new-algorithm.patch
Patch22222: linux-2.6-ipsec-add-async-resume-support-on-output.patch
Patch22223: linux-2.6-crypto-aead-add-authenc.patch
Patch22224: linux-2.6-ipsec-add-async-resume-support-on-input.patch
Patch22225: linux-2.6-ipsec-add-new-skcipher-hmac-algorithm-interface.patch
Patch22226: linux-2.6-ipsec-use-crypto_aead-and-authenc-in-esp.patch
Patch22227: linux-2.6-ipsec-allow-async-algorithms.patch
Patch22228: linux-2.6-ipsec-add-support-for-combined-mode-algorithms.patch
Patch22229: linux-2.6-ipv4-esp-discard-dummy-packets-from-rfc4303.patch
Patch22230: linux-2.6-ipv6-esp-discard-dummy-packets-from-rfc4303.patch
Patch22231: linux-2.6-ipsec-make-xfrm_lookup-flags-argument-a-bit-field.patch
Patch22232: linux-2.6-ipsec-added-xfrm-reverse-calls.patch
Patch22233: linux-2.6-ipsec-add-icmp-host-relookup-support.patch
Patch22234: linux-2.6-xfrm-rfc4303-compliant-auditing.patch
Patch22235: linux-2.6-xfrm-drop-pkts-when-replay-counter-would-overflow.patch
Patch22236: linux-2.6-ia64-acpica-allow-load-tables.patch
Patch22237: linux-2.6-misc-net-add-support-for-dm9601.patch
Patch22238: linux-2.6-firewire-limit-logout-messages-in-the-logs.patch
Patch22239: linux-2.6-scsi-areca-driver-update.patch
Patch22240: linux-2.6-scsi-areca-driver-update-rhel-part.patch
Patch22241: linux-2.6-md-dm-auto-loading-of-dm-mirror-log-modules.patch
Patch22242: linux-2.6-sata-rhel5-2-general-kernel-prep.patch
Patch22243: linux-2.6-sata-rhel5-2-driver-update.patch
Patch22244: linux-2.6-md-dm-kobject-backport.patch
Patch22245: linux-2.6-md-dm-export-name-and-uuid.patch
Patch22246: linux-2.6-md-dm-add-uevent-to-core.patch
Patch22247: linux-2.6-md-dm-uevent-generate-events.patch
Patch22248: linux-2.6-md-dm-mpath-send-uevents-for-path-fail-reinstate.patch
Patch22249: linux-2.6-scsi-cciss-version-change.patch
Patch22250: linux-2.6-scsi-cciss-support-new-controllers.patch
Patch22251: linux-2.6-scsi-cciss-update-copyright-information.patch
Patch22252: linux-2.6-scsi-cciss-move-read_ahead-to-block-layer.patch
Patch22253: linux-2.6-net-igb-update-to-actual-upstream-version.patch
Patch22254: linux-2.6-nfs-security-negotiation.patch
Patch22255: linux-2.6-mm-show_mem-include-count-of-pagecache-pages.patch
Patch22256: linux-2.6-x86-fix-build-warning-for-command_line_size.patch
Patch22257: linux-2.6-revert-misc-offlining-a-cpu-with-realtime-process-running.patch
Patch22258: linux-2.6-misc-offline-cpu-with-realtime-process-running-v2.patch
Patch22259: linux-2.6-ia64-proc-cpuinfo-of-montecito.patch
Patch22260: linux-2.6-s390-qeth-skb-sg-support-for-large-incoming-msgs.patch
Patch22261: linux-2.6-s390-cleanup-scsi-dumper-code.patch
Patch22262: linux-2.6-s390-z-vm-unit-record-device-driver.patch
Patch22263: linux-2.6-s390-af_iucv-protocol-support.patch
Patch22264: linux-2.6-s390-cleanup-scsi-dumper-code-part-2.patch
Patch22265: linux-2.6-s390-support-for-z-vm-diag-2fc.patch
Patch22266: linux-2.6-s390-z-vm-monitor-stream-state-2.patch
Patch22267: linux-2.6-char-tpm-cleanups-and-fixes.patch
Patch22268: linux-2.6-s390-qeth-recognize-handle-rc-19-from-hydra-3-osa.patch
Patch22269: linux-2.6-s390-qeth-drop-inbound-pkt-with-unknown-header-id.patch
Patch22270: linux-2.6-s390-zfcp-error-messages-when-lun-0-is-present.patch
Patch22271: linux-2.6-s390-zfcp-remove-scsi-devices-then-adapter.patch
Patch22272: linux-2.6-s390-cio-disable-chan-path-measurements-on-reboot.patch
Patch22273: linux-2.6-s390-qeth-hipersockets-supports-ip-packets-only.patch
Patch22274: linux-2.6-s390-qeth-crash-during-activation-of-osa-cards.patch
Patch22275: linux-2.6-s390-fix-dump-on-panic-for-dasds-under-lpar.patch
Patch22276: linux-2.6-s390-data-corruption-on-dasd-while-toggling-chpids.patch
Patch22277: linux-2.6-s390-crash-placing-a-kprobe-on-bc-instruction.patch
Patch22278: linux-2.6-s390-qdio-time-calculation-is-wrong.patch
Patch22279: linux-2.6-s390-qdio-many-interrupts-on-qdio-driven-devices.patch
Patch22280: linux-2.6-s390-qdio-output-queue-stall-on-fcp-and-net-devs.patch
Patch22281: linux-2.6-s390-pte-type-cleanup.patch
Patch22282: linux-2.6-misc-pci-rom-reduce-number-of-failure-messages.patch
Patch22283: linux-2.6-misc-firewire-latest-upstream.patch
Patch22284: linux-2.6-misc-increase-softlockup-timeout-maximum.patch
Patch22285: linux-2.6-scsi-qla2xxx-fix-for-infinite-login-retry.patch
Patch22286: linux-2.6-scsi-qla2xxx-fix-bad-nvram-kernel-panic.patch
Patch22287: linux-2.6-openib-ofed-1-3-support.patch
Patch22288: linux-2.6-gfs2-permission-denied-on-first-attempt-to-exec.patch
Patch22289: linux-2.6-gfs2-reduce-gfs2-memory-requirements.patch
Patch22290: linux-2.6-fs-corruption-by-unprivileged-user-in-directories.patch
Patch22291: linux-2.6-acpi-support-external-package-objs-as-method-args.patch
Patch22292: linux-2.6-md-avoid-reading-past-end-of-bitmap-file.patch
Patch22293: linux-2.6-xen-export-cpu_llc_id-as-gpl.patch
Patch22294: linux-2.6-ia64-use-thread-on_ustack-to-determine-user-stack.patch
Patch22296: linux-2.6-ide-handle-drac4-hotplug.patch
Patch22297: linux-2.6-mm-make-zonelist-order-selectable-in-numa.patch
Patch22298: linux-2.6-scsi-iscsi-boot-firmware-table-tool-support.patch
Patch22300: linux-2.6-xen-handle-multi-page-segments-in-dma_map_sg.patch
Patch22301: linux-2.6-xen-handle-sync-invocations-on-mapped-subregions.patch
Patch22302: linux-2.6-xen-keep-offset-in-a-page-smaller-than-page_size.patch
Patch22303: linux-2.6-xen-allow-sync-on-offsets-into-dma-mapped-region.patch
Patch22304: linux-2.6-xen-make-dma_addr_to_phys_addr-static.patch
Patch22305: linux-2.6-xen-fixes-a-comment-only.patch
Patch22306: linux-2.6-net-get-minimum-rto-via-tcp_rto_min.patch
Patch22307: linux-2.6-xen-idle-poll-instead-of-hypercall-block.patch
Patch22311: linux-2.6-xen-ia64-access-extended-i-o-spaces-from-dom0.patch
Patch22312: linux-2.6-xen-kdump-fix-dom0-proc-vmcore-layout.patch
Patch22313: linux-2.6-net-fix-missing-defintions-from-rtnetlink-h.patch
Patch22314: linux-2.6-cpufreq-booting-with-maxcpus-1-panics.patch
Patch22315: linux-2.6-misc-enabling-a-non-hotplug-cpu-should-cause-panic.patch
Patch22316: linux-2.6-ia64-xen-fix-bogus-iosapic.patch
Patch22317: linux-2.6-x86-correct-cpu-cache-info-for-tolapai.patch
Patch22318: linux-2.6-char-r500-drm-support.patch
Patch22319: linux-2.6-scsi-cciss-fix-incompatibility-with-hpacucli.patch
Patch22320: linux-2.6-wd-hpwdt-initial-support.patch
Patch22321: linux-2.6-ppc64-oprofile-distinguish-970mp-from-other-970s.patch
Patch22322: linux-2.6-ppc64-oprofile-power5-needs-unique-entry.patch
Patch22323: linux-2.6-misc-ioat-support-for-1-9.patch
Patch22324: linux-2.6-input-enable-hp-ilo2-virtual-remote-mouse.patch
Patch22325: linux-2.6-cpufreq-ondemand-governor-update.patch
Patch22326: linux-2.6-xen-xenoprof-loses-samples-for-passive-domains.patch
Patch22327: linux-2.6-net-e1000e-update-to-latest-upstream.patch
Patch22328: linux-2.6-net-e1000-update-to-lastest-upstream.patch
Patch22329: linux-2.6-acpi-improve-reporting-of-power-states.patch
Patch22330: linux-2.6-fs-hfs-make-robust-to-deal-with-disk-corruption.patch
Patch22331: linux-2.6-x86-mmconfig-remove-platforms-from-the-blacklist.patch
Patch22332: linux-2.6-x86-mmconfig-introduce-pci_using_mmconf-flag.patch
Patch22333: linux-2.6-x86-mmconfig-add-legacy-pci-conf-functions.patch
Patch22334: linux-2.6-x86-mmconfig-init-legacy-pci-conf-functions.patch
Patch22335: linux-2.6-x86-mmconfig-introduce-pcibios_fix_bus_scan.patch
Patch22336: linux-2.6-x86-mmconfig-call-pcibios_fix_bus_scan.patch
Patch22337: linux-2.6-mm-prevent-cpu-lockups-in-invalidate_mapping_pages.patch
Patch22338: linux-2.6-x86-cpufreq-unknown-symbol-fixes.patch
Patch22339: linux-2.6-ide-hotplug-docking-support-for-some-laptops.patch
Patch22340: linux-2.6-nfs-acl-support-broken-due-to-typo.patch
Patch22341: linux-2.6-mm-hugepages-leak-due-to-pagetable-page-sharing.patch
Patch22342: linux-2.6-net-wireless-introduce-wext-scan-capabilities.patch
Patch22343: linux-2.6-sound-enable-hdmi-for-amd-ati-integrated-chipsets.patch
Patch22344: linux-2.6-mm-using-hugepages-panics-the-kernel.patch
Patch22345: linux-2.6-net-ipv6-tahi-rh0-rfc5095-update.patch
Patch22346: linux-2.6-dlm-validate-lock-name-length.patch
Patch22347: linux-2.6-fs-manually-d_move-inside-of-rename.patch
Patch22348: linux-2.6-gfs2-lock-the-page-on-error.patch
Patch22349: linux-2.6-net-ipv6-snmp-counters-fix.patch
Patch22350: linux-2.6-ecryptfs-fix-dentry-handling.patch
Patch22351: linux-2.6-ppc64-backport-pmi-driver-for-cell-blade.patch
Patch22352: linux-2.6-ppc64-cell-support-for-performance-tools-part1.patch
Patch22353: linux-2.6-ppc64-cell-support-for-performance-tools-part2.patch
Patch22354: linux-2.6-ppc64-cell-support-for-performance-tools-part3.patch
Patch22355: linux-2.6-ppc64-cell-support-for-performance-tools-part4.patch
Patch22356: linux-2.6-scsi-aic94xx-version-1-0-2-2.patch
Patch22357: linux-2.6-s390-hipersockets-mac-layer-routing-support.patch
Patch22358: linux-2.6-s390-stsi-change-for-capacity-provisioning.patch
Patch22359: linux-2.6-s390-osa-2-ports-per-chpid-support.patch
Patch22360: linux-2.6-s390-crypto-new-cp-assist-functions.patch
Patch22361: linux-2.6-x86-pci-use-pci-norom-to-disable-p2p-rom-window.patch
Patch22362: linux-2.6-scsi-qla2xxx-fw-driver-doesn-t-login-to-fabric.patch
Patch22363: linux-2.6-audit-break-execve-records-into-smaller-parts.patch
Patch22364: linux-2.6-acpi-backport-video-support-from-upstream.patch
Patch22365: linux-2.6-ia64-xen-create-100gb-mem-guest-fix-softlockup.patch
Patch22366: linux-2.6-ia64-xen-create-100gb-mem-guest-fix-softlockup-2.patch
Patch22367: linux-2.6-usb-sierra-mc8755-increase-hsdpa-performance.patch
Patch22368: linux-2.6-scsi-sym53c8xx-add-pci-error-recovery-callbacks.patch
Patch22369: linux-2.6-misc-support-module-taint-flag-in-proc-modules.patch
Patch22370: linux-2.6-net-udp-new-accounting-interface.patch
Patch22371: linux-2.6-net-udp-add-memory-accounting.patch
Patch22372: linux-2.6-net-udp-update-infiniband-driver.patch
Patch22373: linux-2.6-mm-make-page-private-usable-in-compound-pages.patch
Patch22374: linux-2.6-mm-introduce-more-huge-pte-handling-functions.patch
Patch22375: linux-2.6-s390-system-z-large-page-support.patch
Patch22376: linux-2.6-ia64-enable-cmci-on-hot-plugged-processors.patch
Patch22377: linux-2.6-net-fix-potential-skb-invalid-truesize-bug.patch
Patch22378: linux-2.6-scsi-areca-update-to-latest.patch
Patch22379: linux-2.6-net-ipv6-use-correct-seed-to-compute-ehash-index.patch
Patch22380: linux-2.6-misc-kprobes-make-probe-handler-stack-unwind-correct.patch
Patch22381: linux-2.6-misc-kprobes-support-kretprobe-blacklist.patch
Patch22382: linux-2.6-misc-kprobes-inatomic-__get_user-and-__put_user.patch
Patch22383: linux-2.6-misc-kprobes-fix-reentrancy.patch
Patch22384: linux-2.6-audit-ratelimit-printk-messages.patch
Patch22385: linux-2.6-net-link_watch-always-schedule-urgent-events.patch
Patch22386: linux-2.6-nfs-discard-pagecache-data-for-dirs-on-dentry_iput.patch
Patch22388: linux-2.6-ia64-kdump-slave-cpus-drop-to-pod.patch
Patch22389: linux-2.6-misc-agp-add-e7221-pci-ids.patch
Patch22390: linux-2.6-net-bridge-br_if-fix-oops-in-port_carrier_check.patch
Patch22391: linux-2.6-sata-combined-mode-fix-for-5-2.patch
Patch22392: linux-2.6-selinux-harden-against-null-ptr-dereference-bugs.patch
Patch22393: linux-2.6-scsi-iscsi-set-host-template.patch
Patch22394: linux-2.6-gfs2-install-to-root-volume-should-work.patch
Patch22395: linux-2.6-xen-fix-sbin-init-to-use-cpu_possible.patch
Patch22396: linux-2.6-xen-gnttab-allow-more-than-3-vnifs.patch
Patch22397: linux-2.6-gfs2-speed-up-read-write-performance.patch
Patch22398: linux-2.6-scsi-qla2xxx-updated-firmware-for-25xxx.patch
Patch22399: linux-2.6-scsi-qla25xx-incorrect-firmware-loaded.patch
Patch22400: linux-2.6-firewire-more-upstream-fixes-regarding-rom.patch
Patch22401: linux-2.6-net-e1000e-disable-hw-crc-stripping.patch
Patch22402: linux-2.6-audit-fix-potential-skb-invalid-truesize-bug.patch
Patch22403: linux-2.6-isdn-fix-possible-isdn_net-buffer-overflows.patch
Patch22404: linux-2.6-fs-fix-locking-for-fcntl.patch
Patch22405: linux-2.6-ia64-fix-unaligned-handler-for-fp-instructions.patch
Patch22406: linux-2.6-scsi-qla2xxx-update-rh-version-number.patch
Patch22407: linux-2.6-md-fix-raid1-consistency-check.patch
Patch22408: linux-2.6-ppc-fix-mmap-of-pci-resource-with-hack-for-x.patch
Patch22409: linux-2.6-xen-32-bit-pv-guest-migration-can-fail-under-load.patch
Patch22410: linux-2.6-nfs-reduce-number-of-wire-rpc-ops-increase-perf.patch
Patch22411: linux-2.6-net-icmp-restore-pskb_pull-calls-in-receive-func.patch
Patch22412: linux-2.6-isdn-i4l-fix-memory-overruns.patch
Patch22413: linux-2.6-ide-missing-sb600-sb700-40-pin-cable-support.patch
Patch22414: linux-2.6-scsi-cciss-update-procfs.patch
Patch22415: linux-2.6-s390-dasd-set-online-fails-if-initial-probe-fails.patch
Patch22416: linux-2.6-s390-dasd-fix-loop-in-request-expiration-handling.patch
Patch22417: linux-2.6-ppc-chrp-fix-possible-strncmp-null-pointer-usage.patch
Patch22418: linux-2.6-sched-change-the-interactive-interface.patch
Patch22419: linux-2.6-sched-implement-a-weak-interactivity-mode.patch
Patch22420: linux-2.6-net-e1000e-tweak-irq-allocation-messages.patch
Patch22421: linux-2.6-gfs2-reduce-memory-footprint.patch
Patch22422: linux-2.6-net-bonding-locking-fixes-and-version-3-2-4.patch
Patch22423: linux-2.6-mm-add-sysctl-to-not-flush-mmapped-pages.patch
Patch22424: linux-2.6-ide-ide-io-fail-request-when-device-is-dead.patch
Patch22425: linux-2.6-sound-enable-s-pdif-in-fila-converse-fixlet.patch
Patch22426: linux-2.6-misc-ich10-device-ids.patch
Patch22427: linux-2.6-module-fix-module-loader-race.patch
Patch22428: linux-2.6-net-ipv6-fixes-to-meet-dod-requirements.patch
Patch22429: linux-2.6-net-ipsec-allow-ctr-mode-use-with-aes.patch
Patch22430: linux-2.6-net-sctp-add-bind-hash-locking-to-migrate-code.patch
Patch22431: linux-2.6-fs-check-permissions-in-vmsplice_to_pipe.patch
Patch22432: linux-2.6-libata-sata_nv-may-send-cmds-with-duplicate-tags.patch
Patch22433: linux-2.6-libata-sata_nv-un-blacklist-hitachi-drives.patch
Patch22434: linux-2.6-nfs-interoperability-problem-with-aix-clients.patch
Patch22435: linux-2.6-nfs-potential-file-corruption-issue-when-writing.patch
Patch22436: linux-2.6-gfs2-fix-calling-of-drop_bh.patch
Patch22437: linux-2.6-x86-fix-tsc-feature-flag-check-on-amd.patch
Patch22438: linux-2.6-cpufreq-xen-properly-register-notifier.patch
Patch22439: linux-2.6-audit-fix-bogus-reporting-of-async-signals.patch
Patch22440: linux-2.6-net-ipv6-fix-ipsec-datagram-fragmentation.patch
Patch22441: linux-2.6-net-sctp-socket-initialization-race.patch
Patch22442: linux-2.6-nfs-fslocations-referrals-broken.patch
Patch22443: linux-2.6-net-ixgbe-obtain-correct-protocol-info-on-xmit.patch
Patch22444: linux-2.6-net-remove-ip_tos-setting-privilege-checks.patch
Patch22445: linux-2.6-net-igb-more-5-2-fixes-and-backports.patch
Patch22446: linux-2.6-fs-nlm-fix-refcount-leak-in-nlmsvc_grant_blocked.patch
Patch22447: linux-2.6-x86-mprotect-performance-improvements.patch
Patch22448: linux-2.6-scsi-ibmvscsi-set-command-timeout-to-60-seconds.patch
Patch22449: linux-2.6-sound-add-support-for-ad1882-codec.patch
Patch22450: linux-2.6-x86-blacklist-systems-that-need-nommconf.patch
Patch22451: linux-2.6-video-neofb-avoid-overwriting-fb_info-fields.patch
Patch22452: linux-2.6-x86-add-hp-dl580-g5-to-bfsort-whitelist.patch
Patch22453: linux-2.6-ppc64-iommu-dma-alignment-fix.patch
Patch22454: linux-2.6-net-qla2xxx-wait-for-flash-to-complete-write.patch
Patch22455: linux-2.6-x86-fix-relocate_kernel-to-not-overwrite-pgd.patch
Patch22456: linux-2.6-misc-fix-align-macro.patch
Patch22457: linux-2.6-ppc64-permit-pci-error-state-recovery.patch
Patch22458: linux-2.6-scsi-sym53c8xx-use-proper-struct.patch
Patch22459: linux-2.6-ppc64-fix-xics-set_affinity-code.patch
Patch22460: linux-2.6-ia64-fix-userspace-compile-error-in-gcc_intrin-h.patch
Patch22461: linux-2.6-misc-fix-range-check-in-fault-handlers-with-mremap.patch
Patch22462: linux-2.6-net-cxgb3-rdma-arp-and-loopback-fixes.patch
Patch22463: linux-2.6-misc-fix-memory-leak-in-alloc_disk_node.patch
Patch22464: linux-2.6-crypto-xcbc-fix-ipsec-crash-with-aes-xcbc-mac.patch
Patch22465: linux-2.6-scsi-hptiop-fixes-buffer-overflow-adds-pci-ids.patch
Patch22466: linux-2.6-sound-add-support-for-hp-rp5700-model.patch
Patch22467: linux-2.6-gfs2-remove-assertion-al-al_alloced-failed.patch
Patch22468: linux-2.6-misc-remove-unneeded-export_symbols.patch
Patch22469: linux-2.6-net-e1000e-wake-on-lan-fixes.patch
Patch22470: linux-2.6-firmware-ibft_iscsi-prevent-misconfigured-ibfts.patch
Patch22471: linux-2.6-cpufreq-powernow-blacklist-bad-acpi-tables.patch
Patch22472: linux-2.6-ppc64-broken-msi-on-cell-blades-when-iommu-is-on.patch
Patch22473: linux-2.6-revert-net-sunrpc-fix-hang-due-to-eventd-deadlock.patch
Patch22474: linux-2.6-ppc64-cell-remove-spu_context_switch_active-flag.patch
Patch22475: linux-2.6-ppc64-slb-serialize-invalidation-against-loading.patch
Patch22476: linux-2.6-ppc64-spufs-invalidate-slb-then-add-a-new-entry.patch
Patch22477: linux-2.6-crypto-fix-sa-creation-with-ah.patch
Patch22478: linux-2.6-crypto-fix-sa-creation-with-esp-encryption-only.patch
Patch22479: linux-2.6-gfs2-optimise-loop-in-gfs2_bitfit.patch
Patch22480: linux-2.6-docs-add-oom_adj-and-oom_score-use-to-proc-txt.patch
Patch22481: linux-2.6-gfs2-gfs2_adjust_quota-has-broken-unstuffing-code.patch
Patch22482: linux-2.6-scsi-fusion-1078-corrupts-data-in-36gb-mem-region.patch
Patch22483: linux-2.6-sound-hdmi-device-ids-for-amd-ati-chipsets.patch
Patch22484: linux-2.6-usb-new-iaa-watchdog-timer.patch
Patch22485: linux-2.6-usb-fix-iaa-watchdog-notifications.patch
Patch22486: linux-2.6-x86-clear-df-flag-for-signal-handlers.patch
Patch22487: linux-2.6-xen-add-warning-to-time-went-backwards-message.patch
Patch22488: linux-2.6-scsi-lpfc-update-driver-to-8-2-0-20.patch
Patch22489: linux-2.6-revert-xen-idle-poll-instead-of-hypercall-block.patch
Patch22490: linux-2.6-block-sg-cap-reserved_size-values-at-max_sectors.patch
Patch22491: linux-2.6-scsi-lpfc-update-driver-to-8-2-0-21.patch
Patch22492: linux-2.6-scsi-lpfc-update-driver-to-8-2-0-22.patch
Patch22493: linux-2.6-scsi-qla4xxx-fix-completion-lun-reset-code.patch
Patch22494: linux-2.6-net-qla3xxx-have-link-sm-use-work-threads.patch
Patch22495: linux-2.6-scsi-qla4xxx-negotiation-issues-with-new-switches.patch
Patch22496: linux-2.6-s390-add-missing-tlb-flush-to-hugetlb_cow.patch
Patch22497: linux-2.6-mm-inconsistent-get_user_pages-and-memory-mapped.patch
Patch22498: linux-2.6-ppc64-fixes-removal-of-virtual-cpu-from-dlpar.patch
Patch22499: linux-2.6-x86_64-address-space-randomization.patch
Patch22500: linux-2.6-ppc64-hardware-watchpoints-add-dabrx-definitions.patch
Patch22501: linux-2.6-ppc64-hardware-watchpoints-add-dabrx-init.patch
Patch22502: linux-2.6-openib-remove-xrc-support.patch
Patch22503: linux-2.6-openib-update-ehca-driver-to-version-0-25.patch
Patch22504: linux-2.6-openib-minor-core-updates-between-rc1-and-final.patch
Patch22505: linux-2.6-openib-add-improved-error-handling-in-srp-driver.patch
Patch22506: linux-2.6-openib-sdp-accounting-fixes.patch
Patch22507: linux-2.6-openib-remove-srpt-and-empty-vnic-driver-files.patch
Patch22508: linux-2.6-openib-cleanup-of-the-xrc-patch-removal.patch
Patch22509: linux-2.6-openib-ipoib-updates.patch
Patch22510: linux-2.6-openib-update-the-nes-driver-from-0-4-to-1-0.patch
Patch22511: linux-2.6-openib-update-ipath-driver.patch
Patch22512: linux-2.6-ata-fix-sata-ide-mode-bug-upon-resume.patch
Patch22513: linux-2.6-s390-fix-qeth-scatter-gather.patch
Patch22514: linux-2.6-net-ehea-checksum-error-fix.patch
Patch22515: linux-2.6-audit-fix-panic-regression-netlink-socket-usage.patch
Patch22516: linux-2.6-net-ipv6-fix-default-address-selection-rule-3.patch
Patch22517: linux-2.6-x86-oprofile-support-for-penryn-class-processors.patch
Patch22518: linux-2.6-agp-add-cantiga-ids.patch
Patch22519: linux-2.6-ppc64-oprofile-add-support-for-power5-and-later.patch
Patch22520: linux-2.6-nfs-stop-sillyrenames-and-unmounts-from-racing.patch
Patch22521: linux-2.6-net-ipv6-check-ptr-in-ip6_flush_pending_frames.patch
Patch22522: linux-2.6-s390-fcp-scsi-write-io-stagnates.patch
Patch22523: linux-2.6-x86_64-export-smp_call_function_single.patch
Patch22524: linux-2.6-utrace-race-crash-fixes.patch
Patch22525: linux-2.6-ipsec-use-hmac-instead-of-digest_null.patch
Patch22526: linux-2.6-net-bnx2x-update-5-2-to-support-latest-firmware.patch
Patch22527: linux-2.6-pci-hotplug-pci-express-problems-with-bad-dllps.patch
Patch22528: linux-2.6-sata-sb700-sb800-64bit-dma-support.patch
Patch22529: linux-2.6-x86-fix-4-bit-apicid-assumption.patch
Patch22530: linux-2.6-net-esp-ensure-iv-is-in-linear-part-of-the-skb.patch
Patch22531: linux-2.6-x86-fix-mprotect-on-prot_none-regions.patch
Patch22532: linux-2.6-x86-xen-fix-swiotlb-overflows.patch
Patch22533: linux-2.6-acpi-only-ibm_acpi-c-should-report-bay-events.patch
Patch22534: linux-2.6-scsi-qla4xxx-update-driver-version-number.patch
Patch22535: linux-2.6-x86_64-fix-unprivileged-crash-on-cs-corruption.patch
Patch22536: linux-2.6-sata-sb600-add-255-sector-limit.patch
Patch22537: linux-2.6-xen-check-num-of-segments-in-block-backend-driver.patch
Patch22538: linux-2.6-ppc64-slb-shadow-buffer-error-cause-random-reboots.patch
Patch22539: linux-2.6-nfs-fix-the-fsid-revalidation-in-nfs_update_inode.patch
Patch22540: linux-2.6-x86_64-add-phys_base-to-vmcoreinfo.patch
Patch22541: linux-2.6-s390-cio-chpid-configuration-event-is-ignored.patch
Patch22542: linux-2.6-pci-fix-msi-interrupts-on-ht1000-based-machines.patch
Patch22543: linux-2.6-s390-cio-fix-vary-off-of-paths.patch
Patch22544: linux-2.6-video-pwc-driver-dos.patch
Patch22545: linux-2.6-crytpo-use-scatterwalk_sg_next-for-xcbc.patch
Patch22546: linux-2.6-xen-memory-corruption-due-to-vnif-increase.patch
Patch22547: linux-2.6-ppc64-ehea-fixes-receive-packet-handling.patch
Patch22548: linux-2.6-pci-revert-pci-remove-transparent-bridge-sizing.patch
Patch22549: linux-2.6-revert-scsi-qla2xxx-pci-ee-error-handling-support.patch
Patch22550: linux-2.6-x86_64-32-bit-address-space-randomization.patch
Patch22551: linux-2.6-net-add-aes-ctr-algorithm-to-xfrm_nalgo.patch
Patch22552: linux-2.6-misc-infinite-loop-in-highres-timers.patch
Patch22553: linux-2.6-ia64-kdump-add-save_vmcore_info-to-init-path.patch
Patch22554: linux-2.6-x86_64-page-faults-from-user-mode-are-user-faults.patch
Patch22555: linux-2.6-xen-ia64-set-memory-attribute-in-inline-asm.patch
Patch22556: linux-2.6-scsi-cciss-allow-kexec-to-work.patch
Patch22557: linux-2.6-fs-race-condition-in-dnotify.patch
Patch22558: linux-2.6-misc-add-cpu-hotplug-support-for-relay-functions.patch
Patch22559: linux-2.6-net-32-64-bit-compat-mcast_-sock-options-support.patch
Patch22560: linux-2.6-net-negotiate-all-algorithms-when-id-bit-mask-zero.patch
Patch22561: linux-2.6-net-fix-xfrm-reverse-flow-lookup-for-icmp6.patch
Patch22562: linux-2.6-xen-netfront-send-fake-arp-when-link-gets-carrier.patch
Patch22563: linux-2.6-x86-sanity-checking-for-read_tsc-on-i386.patch
Patch22564: linux-2.6-misc-ttys1-loses-interrupt-and-stops-transmitting.patch
Patch22565: linux-2.6-misc-kernel-crashes-on-futex.patch
Patch22566: linux-2.6-net-fix-recv-return-zero.patch
Patch22567: linux-2.6-sata-update-sata_svw.patch
Patch22568: linux-2.6-i386-Add-check-for-dmi_data-in-powernow_k8-driver.patch
Patch22569: linux-2.6-i386-Add-check-for-supported_cpus-in-powernow_k8.patch
Patch22570: linux-2.6-mm-Make-mmap-with-PROT_WRITE-on-RHEL5.patch
Patch22571: linux-2.6-nfs-address-nfs-rewrite-performance-regression-in.patch
Patch22572: linux-2.6-x86_64-extend-MCE-banks-support-for-Dunnington-N.patch
Patch22573: linux-2.6-net-Fixing-bonding-rtnl_lock-screwups.patch
Patch22574: linux-2.6-x86_64-write-system-call-vulnerability.patch
Patch22575: linux-2.6-misc-buffer-overflow-in-asn-1-parsing-routines.patch
Patch22576: linux-2.6-net-dccp-sanity-check-feature-length.patch
Patch22577: linux-2.6-x86_64-zero-the-output-of-string-inst-on-exception.patch
Patch22578: linux-2.6-net-sit-exploitable-remote-memory-leak.patch
Patch22579: linux-2.6-sys-sys_setrlimit-prevent-setting-rlimit_cpu-to-0.patch
Patch22580: linux-2.6-net-sctp-make-sure-sctp_addr-does-not-overflow.patch
Patch22581: linux-2.6-misc-ttys1-lost-interrupt-stops-transmitting-v2.patch
Patch22582: linux-2.6-tty-add-null-pointer-checks.patch
Patch22583: linux-2.6-net-randomize-udp-port-allocation.patch
Patch22584: linux-2.6-s390-pav-alias-disks-not-detected-on-lpar.patch
Patch22585: linux-2.6-s390-zfcp-deadlock-when-adding-invalid-lun.patch
Patch22586: linux-2.6-s390-zfcp-reduce-flood-on-hba-trace.patch
Patch22587: linux-2.6-s390-zfcp-units-are-reported-as-boxed.patch
Patch22588: linux-2.6-s390-zfcp-zfcp_erp_action_dismiss-will-ignore-actions.patch
Patch22589: linux-2.6-s390-zfcp-imbalance-in-erp_ready_sem-usage.patch
Patch22590: linux-2.6-s390-cio-add-missing-reprobe-loop-end-statement.patch
Patch22591: linux-2.6-s390-zfcp-fix-use-after-free-bug.patch
Patch22592: linux-2.6-s390-cio-sense-id-works-with-partial-hw-response.patch
Patch22593: linux-2.6-s390-cio-introduce-timed-recovery-procedure.patch
Patch22594: linux-2.6-s390-dasd-fix-ifcc-handling.patch
Patch22595: linux-2.6-s390-zfcp-handling-of-boxed-port-after-physical-close.patch
Patch22596: linux-2.6-s390-zfcp-hold-lock-when-checking-port-unit-handle.patch
Patch22597: linux-2.6-s390-zfcp-hold-lock-on-port-unit-handle-for-fcp-cmd.patch
Patch22598: linux-2.6-s390-zfcp-hold-lock-on-port-handle-for-els-command.patch
Patch22599: linux-2.6-s390-zfcp-hold-lock-on-port-unit-handle-for-task-cmd.patch
Patch22600: linux-2.6-s390-zcrypt-disable-ap-polling-thread-per-default.patch
Patch22601: linux-2.6-s390-sclp-prevent-console-lockup-during-se-warmstart.patch
Patch22602: linux-2.6-s390-qeth-ccl-seq-numbers-req-for-protocol-802-2.patch
Patch22603: linux-2.6-s390-dasd-diff-z-vm-minidisks-need-a-unique-uid.patch
Patch22604: linux-2.6-s390-lcs-ccl-seq-numbers-required-for-prot-802-2.patch
Patch22605: linux-2.6-s390-qdio-change-in-timeout-handling-during-establish.patch
Patch22606: linux-2.6-s390-qeth-recovery-problems-with-failing-startlan.patch
Patch22607: linux-2.6-s390-zcrypt-add-support-for-large-random-numbers.patch
Patch22608: linux-2.6-s390-dasd-add-support-for-system-information-messages.patch
Patch22609: linux-2.6-s390-zfcp-enhanced-trace-facility.patch
Patch22610: linux-2.6-fs-fix-bad-unlock_page-in-pip_to_file-error-path.patch
Patch22611: linux-2.6-s390-cio-kernel-panic-in-cm_enable-processing.patch
Patch22612: linux-2.6-s390-qeth-eddp-skb-buff-problem-running-eddp-guestlan.patch
Patch22613: linux-2.6-s390-qdio-missed-inb-traffic-with-online-fcp-devices.patch
Patch22614: linux-2.6-s390-qeth-avoid-inconsistent-lock-state-for-inet6_dev.patch
Patch22615: linux-2.6-s390-cio-avoid-machine-check-vs-not-operational-race.patch
Patch22616: linux-2.6-gfs2-inode-indirect-buffer-corruption.patch
Patch22617: linux-2.6-s390x-cpu-node-affinity.patch
Patch22618: linux-2.6-s390-aes_s390-decrypt-may-produce-wrong-results-in-cbc.patch
Patch22619: linux-2.6-s390-zfcp-fix-check-for-handles-in-abort-handler.patch
Patch22620: linux-2.6-s390-dasd-fix-timeout-handling-in-interrupt-handler.patch
Patch22621: linux-2.6-s390-zfcp-deadlock-in-slave_destroy-handler.patch
Patch22622: linux-2.6-s390-zfcp-out-of-memory-handling-for-status_read-req.patch
Patch22623: linux-2.6-s390-zfcp-memory-handling-for-gid_pn.patch
Patch22624: linux-2.6-dlm-use-dlm-prefix-on-alloc-and-free-functions.patch
Patch22625: linux-2.6-dlm-align-midcomms-message-buffer.patch
Patch22626: linux-2.6-dlm-swap-bytes-for-rcom-lock-reply.patch
Patch22627: linux-2.6-dlm-use-fixed-errno-values-in-messages.patch
Patch22628: linux-2.6-dlm-clear-ast_type-when-removing-from-astqueue.patch
Patch22629: linux-2.6-dlm-recover-locks-waiting-for-overlap-replies.patch
Patch22630: linux-2.6-dlm-call-to-confirm_master-in-receive_request_reply.patch
Patch22631: linux-2.6-dlm-reject-messages-from-non-members.patch
Patch22632: linux-2.6-dlm-validate-messages-before-processing.patch
Patch22633: linux-2.6-dlm-reject-normal-unlock-when-lock-waits-on-lookup.patch
Patch22634: linux-2.6-dlm-limit-dir-lookup-loop.patch
Patch22635: linux-2.6-dlm-fix-possible-use-after-free.patch
Patch22636: linux-2.6-dlm-change-error-message-to-debug.patch
Patch22637: linux-2.6-dlm-keep-cached-master-rsbs-during-recovery.patch
Patch22638: linux-2.6-dlm-save-master-info-after-failed-no-queue-request.patch
Patch22639: linux-2.6-dlm-check-for-null-in-device_write.patch
Patch22640: linux-2.6-dlm-fix-basts-for-granted-cw-waiting-pr-cw.patch
Patch22641: linux-2.6-dlm-move-plock-code-from-gfs2.patch
Patch22642: linux-2.6-tux-crashes-kernel-under-high-load.patch
Patch22643: linux-2.6-gfs2-bad-subtraction-in-while-loop-can-cause-panic.patch
Patch22644: linux-2.6-gfs2-cannot-use-fifo-nodes.patch
Patch22645: linux-2.6-s390-tape-race-condition-in-tape-block-device-driver.patch
Patch22646: linux-2.6-s390-cio-i-o-error-after-cable-pulls.patch
Patch22647: linux-2.6-s390-cio-fix-unusable-zfcp-device-after-vary-off-on.patch
Patch22648: linux-2.6-s390-cio-fix-system-hang-with-reserved-dasd.patch
Patch22649: linux-2.6-s390-fix-race-with-stack-local-wait_queue_head_t.patch
Patch22650: linux-2.6-s390-zfcp-status-read-locking-race.patch
Patch22651: linux-2.6-ia64-properly-unregister-legacy-interrupts.patch
Patch22652: linux-2.6-misc-signaling-msgrvc-should-not-pass-back-error.patch
Patch22653: linux-2.6-ia64-add-tif_restore_sigmask-and-pselect-ppoll-syscall.patch
Patch22654: linux-2.6-edac-k8_edac-add-option-to-report-gart-errors.patch
Patch22655: linux-2.6-misc-allow-hugepage-allocation-to-use-most-of-memory.patch
Patch22656: linux-2.6-ia64-remove-assembler-warnings-on-head-s.patch
Patch22657: linux-2.6-x86_64-gettimeofday-fixes-for-hpet-pmtimer-tsc.patch
Patch22658: linux-2.6-nfs-fix-transposed-deltas-in-nfs-v3.patch
Patch22659: linux-2.6-xen-ia64-add-srlz-instruction-to-asm.patch
Patch22660: linux-2.6-mm-do-not-limit-locked-memory-when-using-rlim_infinity.patch
Patch22661: linux-2.6-nfs-v4-fix-ref-count-and-signal-for-callback-thread.patch
Patch22662: linux-2.6-misc-proc-pid-limits-fix-duplicate-array-entries.patch
Patch22663: linux-2.6-misc-fix-race-in-switch_uid-and-user-signal-accounting.patch
Patch22664: linux-2.6-net-ipv6-no-addrconf-for-bonding-slaves.patch
Patch22665: linux-2.6-fs-ext3-unmount-hang-when-quota-enabled-goes-error-ro.patch
Patch22666: linux-2.6-net-ipv6-don-t-handle-default-routes-specially.patch
Patch22667: linux-2.6-edac-k8_edac-fix-typo-in-user-visible-message.patch
Patch22668: linux-2.6-sched-domain-range-turnable-params-for-wakeup_idle.patch
Patch22669: linux-2.6-openib-small-ipoib-packet-can-cause-an-oops.patch
Patch22670: linux-2.6-fs-jbd-fix-typo-in-recovery-code.patch
Patch22671: linux-2.6-fs-jbd-fix-journal-overflow-issues.patch
Patch22672: linux-2.6-fs-ext3-fix-lock-inversion-in-direct-io.patch
Patch22673: linux-2.6-gfs2-d_doio-stuck-in-readv-waiting-for-pagelock.patch
Patch22674: linux-2.6-nfs-sunrpc-fix-hang-due-to-eventd-deadlock.patch
Patch22675: linux-2.6-nfs-sunrpc-fix-a-race-in-rpciod_down.patch
Patch22676: linux-2.6-x86_64-memmap-flag-results-in-bogus-ram-map-output.patch
Patch22677: linux-2.6-nfs-ensure-that-options-turn-off-attribute-caching.patch
Patch22678: linux-2.6-xen-pvfb-probe-suspend-fixes.patch
Patch22679: linux-2.6-fs-ext3-lighten-up-resize-transaction-requirements.patch
Patch22680: linux-2.6-x86_64-xen-fix-syscall-return-when-tracing.patch
Patch22681: linux-2.6-sound-alsa-hda-driver-update-from-upstream-2008-06-11.patch
Patch22682: linux-2.6-gfs2-lock_dlm-deliver-callbacks-in-the-right-order.patch
Patch22683: linux-2.6-ia64-avoid-unnecessary-tlb-flushes-when-allocating-mem.patch
Patch22684: linux-2.6-gfs2-initial-write-performance-very-slow.patch
Patch22685: linux-2.6-nfs-sunrpc-sleeping-rpc_malloc-might-deadlock.patch
Patch22686: linux-2.6-nfs-remove-error-field-from-nfs_readdir_descriptor_t.patch
Patch22687: linux-2.6-nfs-knfsd-revoke-setuid-setgid-when-uid-gid-changes.patch
Patch22688: linux-2.6-net-sctp-support-remote-address-table-oid.patch
Patch22689: linux-2.6-misc-optional-panic-on-softlockup-warnings.patch
Patch22690: linux-2.6-fs-need-process-map-reporting-for-swapped-pages.patch
Patch22691: linux-2.6-pci-acpiphp_ibm-let-acpi-determine-_cid-buffer-size.patch
Patch22692: linux-2.6-fs-ext3-make-fdatasync-not-sync-metadata.patch
Patch22693: linux-2.6-acpi-remove-processor-module-errors.patch
Patch22694: linux-2.6-fs-debugfs-fix-dentry-reference-count-bug.patch
Patch22695: linux-2.6-net-sunrpc-memory-corruption-from-dead-rpc-client.patch
Patch22696: linux-2.6-nfs-pages-of-a-memory-mapped-file-get-corrupted.patch
Patch22697: linux-2.6-net-fix-the-redirected-packet-if-jiffies-wraps.patch
Patch22698: linux-2.6-fs-cifs-wait-on-kthread_stop-before-thread-exits.patch
Patch22699: linux-2.6-net-ipv6-fix-unbalanced-ref-count-in-ndisc_recv_ns.patch
Patch22700: linux-2.6-scsi-fix-high-i-o-wait-using-3w-9xxx.patch
Patch22701: linux-2.6-x86-brk-fix-rlimit_data-check.patch
Patch22702: linux-2.6-audit-send-eoe-audit-record-at-end-of-syslog-events.patch
Patch22703: linux-2.6-audit-deadlock-under-load-and-auditd-takes-a-signal.patch
Patch22704: linux-2.6-audit-records-sender-of-sigusr2-for-userspace.patch
Patch22705: linux-2.6-net-bnx2x-chip-reset-and-port-type-fixes.patch
Patch22706: linux-2.6-net-ip-tunnel-can-t-be-bound-to-another-device.patch
Patch22707: linux-2.6-dm-snapshot-fix-chunksize-sector-conversion.patch
Patch22708: linux-2.6-dm-snapshot-reduce-default-memory-allocation.patch
Patch22709: linux-2.6-misc-optimize-byte-swapping-fix-pedantic-compile.patch
Patch22710: linux-2.6-x86_64-ia32-syscall-restart-fix.patch
Patch22711: linux-2.6-x86_64-ptrace-sign-extend-orig_rax-to-64-bits.patch
Patch22712: linux-2.6-scsi-update-aacraid-to-1-1-5-2455.patch
Patch22713: linux-2.6-misc-fix-compile-when-selinux-is-disabled.patch
Patch22714: linux-2.6-net-make-udp_encap_rcv-use-pskb_may_pull.patch
Patch22715: linux-2.6-net-s2io-fix-documentation-about-intr_type.patch
Patch22716: linux-2.6-ia64-softlock-prevent-endless-warnings-in-kdump.patch
Patch22717: linux-2.6-misc-fix-up-compile-in-skcipher-h.patch
Patch22718: linux-2.6-mm-dio-fix-cache-invalidation-after-sync-writes.patch
Patch22719: linux-2.6-ppc-use-ibm-slb-size-from-device-tree.patch
Patch22720: linux-2.6-xen-pvfb-frontend-mouse-wheel-support.patch
Patch22721: linux-2.6-fs-missing-check-before-setting-mount-propagation.patch
Patch22722: linux-2.6-acpi-enable-deep-c-states-for-idle-efficiency.patch
Patch22723: linux-2.6-acpi-disable-lapic-timer-on-c2-states.patch
Patch22724: linux-2.6-x86-show-apicid-in-proc-cpuinfo.patch
Patch22725: linux-2.6-x86_64-don-t-call-mp_processor_info-for-disabled-cpu.patch
Patch22726: linux-2.6-x86-don-t-call-mp_processor_info-for-disabled-cpu.patch
Patch22727: linux-2.6-fs-lockd-nlmsvc_lookup_host-called-with-f_sema-held.patch
Patch22728: linux-2.6-fs-potential-race-in-mark_buffer_dirty.patch
Patch22729: linux-2.6-fs-nlm-canceled-inflight-grant_msg-shouldn-t-requeue.patch
Patch22730: linux-2.6-fs-nlm-don-t-reattempt-grant_msg-with-an-inflight-rpc.patch
Patch22731: linux-2.6-fs-nlm-tear-down-rpc-clients-in-nlm_shutdown_hosts.patch
Patch22732: linux-2.6-pci-mmconfig-remove-pci_bios_fix_bus_scan_quirk.patch
Patch22733: linux-2.6-pci-mmconfig-rm-pci_legacy_ops-and-nommconf-blacklist.patch
Patch22734: linux-2.6-pci-mmconfig-use-conf1-for-access-below-256-bytes.patch
Patch22735: linux-2.6-ia64-handle-invalid-acpi-slit-table.patch
Patch22736: linux-2.6-usb-add-ids-for-wwan-cards.patch
Patch22737: linux-2.6-ia64-xen-incompatibility-with-hv-and-userspace-tools.patch
Patch22738: linux-2.6-xen-rename-blktap-kernel-threads-to-blktap-dom-blkname.patch
Patch22739: linux-2.6-xen-blktap-add-statistics.patch
Patch22740: linux-2.6-xen-blktap-stats-error-cleanup.patch
Patch22741: linux-2.6-xen-don-t-try-to-recreate-sysfs-entries.patch
Patch22742: linux-2.6-xen-blktap-modify-sysfs-entries-to-match-blkback.patch
Patch22743: linux-2.6-xen-don-t-collide-symbols-with-blktap.patch
Patch22744: linux-2.6-xen-remove-blktap-sysfs-entries-before-shutdown.patch
Patch22745: linux-2.6-selinux-prevent-illegal-selinux-options-when-mounting.patch
Patch22746: linux-2.6-scsi-ibmvscsi-latest-5-3-fixes-and-enhancements.patch
Patch22747: linux-2.6-misc-irq-reset-stats-when-installing-new-handler.patch
Patch22748: linux-2.6-scsi-ibmvscsi-add-tape-device-support.patch
Patch22749: linux-2.6-gfs2-glock-dumping-missing-out-some-glocks.patch
Patch22750: linux-2.6-ia64-holdoffs-in-sn_ack_irq-when-running-latency-tests.patch
Patch22751: linux-2.6-misc-don-t-randomize-when-no-randomize-personality-set.patch
Patch22752: linux-2.6-fs-vfs-wrong-error-code-on-interrupted-close-syscalls.patch
Patch22753: linux-2.6-mm-xpmem-inhibit-page-swapping-under-heavy-mem-use.patch
Patch22754: linux-2.6-ipmi-restrict-keyboard-i-o-port-reservation.patch
Patch22755: linux-2.6-mm-fix-proc-sys-vm-lowmem_reserve_ratio.patch
Patch22756: linux-2.6-mm-fix-debug-printks-in-page_remove_rmap.patch
Patch22757: linux-2.6-crypto-add-tests-for-cipher-types-to-self-test-module.patch
Patch22758: linux-2.6-video-add-uvcvideo-module.patch
Patch22759: linux-2.6-mm-fix-pae-pmd_bad-bootup-warning.patch
Patch22760: linux-2.6-x86_64-ia32-increase-stack-size.patch
Patch22761: linux-2.6-net-proc-add-unresolved-discards-stat-to-ndisc_cache.patch
Patch22762: linux-2.6-ppc-fast-little-endian-implementation-for-system-p-ave.patch
Patch22763: linux-2.6-ppc-ras-update-for-cell.patch
Patch22764: linux-2.6-ppc-iommu-performance-enhancements.patch
Patch22765: linux-2.6-ppc-event-queue-overflow-on-ehca-adapters.patch
Patch22766: linux-2.6-net-ixgbe-remove-device-id-for-unsupported-device.patch
Patch22767: linux-2.6-mm-numa-system-is-slow-when-over-committing-memory.patch
Patch22768: linux-2.6-net-netxen-driver-update-to-3-4-18.patch
Patch22769: linux-2.6-dlm-fix-a-couple-of-races.patch
Patch22770: linux-2.6-net-slow_start_after_idle-influences-cwnd-validation.patch
Patch22771: linux-2.6-misc-ioc4-fixes-pci_put_dev-printks-mem-resource.patch
Patch22772: linux-2.6-scsi-buslogic-typedef-bool-to-boolean-for-compiler.patch
Patch22773: linux-2.6-net-do-liberal-tracking-for-picked-up-connections.patch
Patch22774: linux-2.6-char-add-hp-ilo-driver.patch
Patch22775: linux-2.6-fs-fix-softlockups-when-repeatedly-dropping-caches.patch
Patch22776: linux-2.6-x86-hugetlb-inconsistent-get_user_pages-x86-piece.patch
Patch22777: linux-2.6-fs-dio-use-kzalloc-to-zero-out-struct-dio.patch
Patch22778: linux-2.6-net-sctp-export-needed-data-to-implement-rfc-3873.patch
Patch22779: linux-2.6-fs-add-le32_add_cpu-and-friends.patch
Patch22780: linux-2.6-fs-add-generic_find_next_le_bit.patch
Patch22781: linux-2.6-fs-introduce-is_owner_or_cap.patch
Patch22782: linux-2.6-fs-add-an-err_cast-function.patch
Patch22783: linux-2.6-fs-i_version-updates.patch
Patch22784: linux-2.6-fs-noinline_for_stack-attribute.patch
Patch22785: linux-2.6-fs-add-buffer_submit_read-and-bh_uptodate_or_lock.patch
Patch22786: linux-2.6-fs-add-clear_nlink-drop_nlink.patch
Patch22787: linux-2.6-block-enhanced-partition-statistics-core-statistics.patch
Patch22788: linux-2.6-block-enhanced-partition-statistics-update-statistics.patch
Patch22789: linux-2.6-block-enhanced-partition-statistics-aoe-fix.patch
Patch22790: linux-2.6-block-enhanced-partition-statistics-cciss-fix.patch
Patch22791: linux-2.6-block-enhanced-partition-statistics-cpqarray-fix.patch
Patch22792: linux-2.6-block-enhanced-partition-statistics-sysfs.patch
Patch22793: linux-2.6-block-enhanced-partition-statistics-procfs.patch
Patch22794: linux-2.6-block-enhanced-partition-statistics-retain-old-stats.patch
Patch22795: linux-2.6-block-enhanced-partition-statistics-documentation.patch
Patch22796: linux-2.6-fs-inotify-previous-event-should-be-last-in-list.patch
Patch22797: linux-2.6-misc-core-dump-remain-dumpable.patch
Patch22798: linux-2.6-xen-expand-scsi-majors-in-blkfront.patch
Patch22799: linux-2.6-xen-fix-blkfront-to-accept-16-devices.patch
Patch22800: linux-2.6-xen-blktap-expand-for-longer-busids.patch
Patch22801: linux-2.6-misc-serial-fix-break-handling-for-i82571-over-lan.patch
Patch22802: linux-2.6-fs-ecryptfs-use-page_alloc-to-get-a-page-of-memory.patch
Patch22803: linux-2.6-misc-fix-wrong-test-in-wait_task_stopped.patch
Patch22804: linux-2.6-pci-fix-problems-with-msi-interrupt-management.patch
Patch22805: linux-2.6-s390-utrace-ptrace_pokeusr_area-corrupts-acr0.patch
Patch22806: linux-2.6-ppc-oprofile-wrong-cpu_type-returned.patch
Patch22807: linux-2.6-ppc-adds-dscr-support-in-sysfs.patch
Patch22808: linux-2.6-xen-event-channel-lock-and-barrier.patch
Patch22809: linux-2.6-fs-add-percpu_counter_add-_sub.patch
Patch22810: linux-2.6-fs-jbd-fix-races-that-lead-to-eio-for-o_direct.patch
Patch22811: linux-2.6-fs-vfs-fix-lookup-on-deleted-directory.patch
Patch22812: linux-2.6-fs-dio-lock-refcount-operations.patch
Patch22813: linux-2.6-scsi-aic94xx-update-to-2-6-25.patch
Patch22814: linux-2.6-mm-tmpfs-restore-missing-clear_highpage.patch
Patch22815: linux-2.6-net-bridge-eliminate-delay-on-carrier-up.patch
Patch22816: linux-2.6-scsi-dlpar-remove-operation-fails-on-lsi-scsi-adapter.patch
Patch22817: linux-2.6-ppc-edac-add-pre-req-support-for-cell-processor.patch
Patch22818: linux-2.6-ppc-edac-add-support-for-cell-processor.patch
Patch22819: linux-2.6-crypto-ipsec-memory-leak.patch
Patch22820: linux-2.6-ia64-use-platform_send_ipi-in-check_sal_cache_flush.patch
Patch22821: linux-2.6-ia64-move-sal_cache_flush-check-later-in-boot.patch
Patch22822: linux-2.6-ia64-fix-boot-failure-on-ia64-sn2.patch
Patch22823: linux-2.6-fs-backport-list_first_entry-helper.patch
Patch22824: linux-2.6-fs-backport-zero_user_segments-and-friends.patch
Patch22825: linux-2.6-xen-pv-shared-use-of-xenbus-netfront-blkfront.patch
Patch22826: linux-2.6-xen-pv-shared-used-header-file-changes.patch
Patch22827: linux-2.6-xen-pv-add-subsystem.patch
Patch22828: linux-2.6-xen-pv-makefile-and-kconfig-additions.patch
Patch22829: linux-2.6-ppc-xmon-setjmp-longjmp-code-generically-available.patch
Patch22830: linux-2.6-ppc-adds-crashdump-shutdown-hooks.patch
Patch22831: linux-2.6-net-adds-inet_lro-module.patch
Patch22832: linux-2.6-net-modifies-inet_lro-for-rhel.patch
Patch22833: linux-2.6-ppc-ehea-update-from-version-0076-05-to-0091-00.patch
Patch22835: linux-2.6-ppc-perr-serr-disabled-after-eeh-error-recovery.patch
Patch22836: linux-2.6-misc-pnp-increase-number-of-devices.patch
Patch22837: linux-2.6-nfs-clean-up-short-packet-handling-for-nfsv3-readdir.patch
Patch22838: linux-2.6-nfs-clean-up-short-packet-handling-for-nfsv2-readdir.patch
Patch22839: linux-2.6-nfs-clean-up-short-packet-handling-for-nfsv4-readdir.patch
Patch22840: linux-2.6-ia64-kdump-implement-greater-than-4g-mem-restriction.patch
Patch22841: linux-2.6-nfs-revert-to-sync-writes-when-background-write-errors.patch
Patch22842: linux-2.6-xen-fix-netloop-restriction.patch
Patch22843: linux-2.6-ia64-add-gate-lds-to-documentation-dontdiff.patch
Patch22844: linux-2.6-misc-batch-kprobe-register-unregister.patch
Patch22845: linux-2.6-ia64-xen-handle-ipi-case-ia64_timer_vector.patch
Patch22846: linux-2.6-alsa-hda-update-to-2008-07-22.patch
Patch22847: linux-2.6-misc-null-pointer-dereference-in-register_kretprobe.patch
Patch22848: linux-2.6-ppc64-cell-spufs-update-for-rhel-5-3.patch
Patch22849: linux-2.6-security-null-ptr-dereference-in-__vm_enough_memory.patch
Patch22850: linux-2.6-net-race-between-neigh_timer_handler-and-neigh_update.patch
Patch22851: linux-2.6-ppc64-missed-hw-breakpoints-across-multiple-threads.patch
Patch22852: linux-2.6-audit-new-filter-type-audit_filetype.patch
Patch22853: linux-2.6-misc-null-pointer-dereference-in-kobject_get_path.patch
Patch22854: linux-2.6-net-h323-fix-panic-in-conntrack-module.patch
Patch22855: linux-2.6-autofs4-check-for-invalid-dentry-in-getpath.patch
Patch22856: linux-2.6-autofs4-sparse-warn-in-waitq-c-autofs4_expire_indirect.patch
Patch22857: linux-2.6-autofs4-bad-return-from-root-c-try_to_fill_dentry.patch
Patch22858: linux-2.6-autofs4-fix-mntput-dput-order-bug.patch
Patch22859: linux-2.6-autofs4-don-t-make-expiring-dentry-negative.patch
Patch22860: linux-2.6-autofs4-use-rehash-list-for-lookups.patch
Patch22861: linux-2.6-autofs4-hold-directory-mutex-if-called-in-oz_mode.patch
Patch22862: linux-2.6-autofs4-use-lookup-intent-flags-to-trigger-mounts.patch
Patch22863: linux-2.6-autofs4-use-struct-qstr-in-waitq-c.patch
Patch22864: linux-2.6-autofs4-fix-pending-mount-race.patch
Patch22865: linux-2.6-autofs4-fix-waitq-locking.patch
Patch22866: linux-2.6-autofs4-check-communication-pipe-is-valid-for-write.patch
Patch22867: linux-2.6-autofs4-fix-waitq-memory-leak.patch
Patch22868: linux-2.6-autofs4-keep-most-direct-and-indirect-dentrys-positive.patch
Patch22869: linux-2.6-autofs4-cleanup-redundant-readdir-code.patch
Patch22870: linux-2.6-autofs4-fix-pending-checks.patch
Patch22871: linux-2.6-autofs4-fix-indirect-mount-pending-expire-race.patch
Patch22872: linux-2.6-autofs4-fix-direct-mount-pending-expire-race.patch
Patch22873: linux-2.6-autofs4-reorganize-expire-pending-wait-function-calls.patch
Patch22874: linux-2.6-autofs4-remove-unused-ioctls.patch
Patch22876: linux-2.6-video-make-v4l2-less-verbose.patch
Patch22877: linux-2.6-ia64-fix-to-check-module_free-parameter.patch
Patch22878: linux-2.6-ppc64-eeh-facilitate-vendor-driver-recovery.patch
Patch22879: linux-2.6-net-pppoe-unshare-skb-before-anything-else.patch
Patch22880: linux-2.6-net-ixgbe-fix-eeh-recovery-time.patch
Patch22881: linux-2.6-nfs-v4-poll-aggressively-when-handling-nfs4err_delay.patch
Patch22882: linux-2.6-net-ipv6-use-timer-pending-to-fix-bridge-ref-count.patch
Patch22883: linux-2.6-net-pppoe-fix-skb_unshare_check-call-position.patch
Patch22884: linux-2.6-ipmi-control-bmc-device-ordering.patch
Patch22885: linux-2.6-mm-add-support-for-fast-get-user-pages.patch
Patch22886: linux-2.6-x86-acpi-prevent-resources-from-corrupting-memory.patch
Patch22887: linux-2.6-xen-pvfb-probe-suspend-fixes-fix.patch
Patch22888: linux-2.6-nfs-v4-credential-ref-leak-in-nfs4_get_state_owner.patch
Patch22889: linux-2.6-nfs-v4-don-t-reuse-expired-nfs4_state_owner-structs.patch
Patch22890: linux-2.6-x86-io_apic-check-timer-with-irq-off.patch
Patch22891: linux-2.6-cpufreq-acpi-boot-crash-due-to-_psd-return-by-ref.patch
Patch22892: linux-2.6-serial-support-for-digi-pci-e-4-8port-async-io-adapter.patch
Patch22893: linux-2.6-dlm-user-c-input-validation-fixes.patch
Patch22894: linux-2.6-xen-x86-fix-endless-loop-when-gpf.patch
Patch22895: linux-2.6-nfs-missing-nfs_fattr_init-in-nfsv3-acl-functions.patch
Patch22896: linux-2.6-usb-removing-bus-with-an-open-file-causes-an-oops.patch
Patch22897: linux-2.6-net-neigh_destroy-call-destructor-before-unloading.patch
Patch22898: linux-2.6-x86-kdump-calgary-iommu-use-boot-kernel-s-tce-tables.patch
Patch22899: linux-2.6-x86_64-resume-from-s3-in-text-mode-with-4gb-of-mem.patch
Patch22900: linux-2.6-revert-misc-mm-add-support-for-fast-get-user-pages.patch
Patch22901: linux-2.6-sound-snd_seq_oss_synth_make_info-info-leak.patch
Patch22903: linux-2.6-gfs2-d_rwdirectempty-fails-with-short-read.patch
Patch22904: linux-2.6-gfs2-rm-on-multiple-nodes-causes-panic.patch
Patch22905: linux-2.6-wireless-update-ieee80211-to-2-6-25.patch
Patch22906: linux-2.6-wireless-update-ipw2x00-driver-to-2-6-25.patch
Patch22907: linux-2.6-wireless-update-bcm43xx-driver-to-2-6-25.patch
Patch22908: linux-2.6-wireless-update-zd1211rw-to-last-non-mac80211-version.patch
Patch22909: linux-2.6-x86-oprofile-enable-additional-perf-counters.patch
Patch22910: linux-2.6-xen-xennet-coordinate-arp-with-backend-network-status.patch
Patch22911: linux-2.6-wireless-infrastructure-changes-for-mac80211-update.patch
Patch22912: linux-2.6-wireless-mac80211-update-to-version-from-2-6-26.patch
Patch22913: linux-2.6-wireless-iwlwifi-update-to-version-from-2-6-26.patch
Patch22914: linux-2.6-wireless-ath5k-add-driver-from-2-6-26.patch
Patch22915: linux-2.6-wireless-rt2x00-add-driver-from-2-6-26.patch
Patch22916: linux-2.6-wireless-rtl818x-add-driver-from-2-6-26.patch
Patch22917: linux-2.6-scsi-cciss-possible-race-condition-during-init.patch
Patch22918: linux-2.6-openib-ehca-handle-two-completions-for-one-work-req.patch
Patch22919: linux-2.6-s390-cio-memory-leak-when-ccw-devices-are-discarded.patch
Patch22920: linux-2.6-sound-hdmi-audio-new-pci-device-id.patch
Patch22921: linux-2.6-gfs2-fix-metafs.patch
Patch22922: linux-2.6-openib-ehca-local-ca-ack-delay-has-an-invalid-value.patch
Patch22923: linux-2.6-scsi-mptscsi-check-for-null-device-in-error-handler.patch
Patch22924: linux-2.6-x86_64-uefi-code-support.patch
Patch22925: linux-2.6-mm-optimize-zero_page-in-get_user_pages-and-fix-xip.patch
Patch22926: linux-2.6-mm-drain_node_page-drain-pages-in-batch-units.patch
Patch22927: linux-2.6-x86_64-nmi-add-perfctr-infrastructure.patch
Patch22928: linux-2.6-x86_64-nmi-introduce-per-cpu-wd_enabled.patch
Patch22929: linux-2.6-x86_64-nmi-introduce-do_nmi_callback.patch
Patch22930: linux-2.6-x86_64-nmi-setup-apic-to-handle-both-io-apic-and-lapic.patch
Patch22931: linux-2.6-x86_64-nmi-update-nmi_watchdog_tick.patch
Patch22932: linux-2.6-x86_64-nmi-change-nmi_active-usage.patch
Patch22933: linux-2.6-x86_64-nmi-use-new-setup-stop-routines-in-suspend-resume.patch
Patch22934: linux-2.6-x86_64-nmi-update-reserve_lapic_nmi.patch
Patch22935: linux-2.6-x86_64-nmi-update-check_nmi_watchdog.patch
Patch22936: linux-2.6-x86_64-nmi-use-perfctr-functions-for-probing.patch
Patch22937: linux-2.6-x86_64-nmi-disable-lapic-io-apic-on-unknown_nmi_panic.patch
Patch22938: linux-2.6-x86_64-nmi-kill-disable_irq-calls.patch
Patch22939: linux-2.6-x86_64-nmi-add-missing-prototypes-in-xen-headers.patch
Patch22940: linux-2.6-x86-nmi-add-perfctr-infrastructure.patch
Patch22941: linux-2.6-x86-nmi-introduce-per-cpu-wd_enabled.patch
Patch22942: linux-2.6-x86-nmi-introduce-do_nmi_callback.patch
Patch22943: linux-2.6-x86-nmi-update-nmi_watchdog_tick.patch
Patch22944: linux-2.6-x86-nmi-change-nmi_active-usage.patch
Patch22945: linux-2.6-x86-nmi-use-setup-stop-routines-in-suspend-resume.patch
Patch22946: linux-2.6-x86-nmi-update-reserve_lapic_nmi.patch
Patch22947: linux-2.6-x86-nmi-update-check_nmi_watchdog.patch
Patch22948: linux-2.6-x86-nmi-use-lapic_adjust_nmi_hz.patch
Patch22949: linux-2.6-x86-nmi-disable-lapic-io-apic-on-unknown_nmi_panic.patch
Patch22950: linux-2.6-x86-nmi-fix-disable-and-enable-_timer_nmi_watchdog.patch
Patch22951: linux-2.6-misc-markers-and-tracepoints-rcu-read-patch.patch
Patch22952: linux-2.6-misc-markers-and-tracepoints-samples-patch.patch
Patch22953: linux-2.6-misc-markers-and-tracepoints-tracepoints.patch
Patch22954: linux-2.6-misc-markers-and-tracepoints-tracepoint-samples.patch
Patch22955: linux-2.6-misc-markers-and-tracepoints-markers.patch
Patch22956: linux-2.6-misc-markers-and-tracepoints-markers-samples.patch
Patch22957: linux-2.6-misc-markers-and-tracepoints-markers-docs.patch
Patch22958: linux-2.6-misc-markers-and-tracepoints-create-module-markers.patch
Patch22959: linux-2.6-misc-markers-and-tracepoints-irq-patch.patch
Patch22960: linux-2.6-misc-markers-and-tracepoints-sched-patch.patch
Patch22961: linux-2.6-misc-markers-and-tracepoints-probes.patch
Patch22962: linux-2.6-misc-markers-and-tracepoints-kabi-fix-up-patch.patch
Patch22963: linux-2.6-utrace-signal-interception-breaks-systemtap-uprobes.patch
Patch22964: linux-2.6-md-fix-crashes-in-iterate_rdev.patch
Patch22965: linux-2.6-acpi-error-attaching-device-data.patch
Patch22966: linux-2.6-ppc-export-lpar-cpu-utilization-stats-for-use-by-hv.patch
Patch22967: linux-2.6-x86-execute-stack-overflow-warning-on-interrupt-stack.patch
Patch22968: linux-2.6-net-dccp_setsockopt_change-integer-overflow.patch
Patch22969: linux-2.6-net-ipv6-drop-outside-of-box-loopback-address-packets.patch
Patch22970: linux-2.6-net-ibmveth-cluster-membership-problems.patch
Patch22971: linux-2.6-alsa-asoc-double-free-and-mem-leak-in-i2c-codec.patch
Patch22972: linux-2.6-gfs2-multiple-writer-performance-issue.patch
Patch22973: linux-2.6-net-udp-possible-recursive-locking.patch
Patch22974: linux-2.6-x86-pci-domain-support.patch
Patch22975: linux-2.6-fs-anon_inodes-implementation.patch
Patch22976: linux-2.6-net-netxen-cleanups-from-upstream-2-6-27.patch
Patch22977: linux-2.6-net-netxen-fixes-from-upstream-2-6-27.patch
Patch22978: linux-2.6-net-netxen-update-to-upstream-2-6-27.patch
Patch22979: linux-2.6-net-netxen-remove-performance-optimization-fix.patch
Patch22980: linux-2.6-ppc64-cell-spufs-update-with-post-2-6-25-patches.patch
Patch22981: linux-2.6-ppc64-cell-spufs-fix-hugetlb.patch
Patch22982: linux-2.6-mm-holdoffs-in-refresh_cpu_vm_stats-using-latency-test.patch
Patch22983: linux-2.6-mm-don-t-use-large-pages-to-map-the-first-2-4mb-of-mem.patch
Patch22984: linux-2.6-openib-race-between-qp-async-handler-and-destroy_qp.patch
Patch22985: linux-2.6-sata-update-driver-to-2-6-26-rc5.patch
Patch22986: linux-2.6-sata-prep-work-for-rhel5-3.patch
Patch22987: linux-2.6-scsi-areca-update-for-rhel-5-3.patch
Patch22988: linux-2.6-x86-make-bare-metal-oprofile-recognize-other-platforms.patch
Patch22989: linux-2.6-block-aoe-use-use-bio-bi_idx-to-avoid-panic.patch
Patch22990: linux-2.6-ia64-oprofile-recognize-montvale-cpu-as-itanium2.patch
Patch22991: linux-2.6-fs-cifs-fix-o_append-on-directio-mounts.patch
Patch22992: linux-2.6-wireless-ath5k-fixup-kconfig-mess-from-update.patch
Patch22993: linux-2.6-wireless-iwlwifi-fix-busted-tkip-encryption.patch
Patch22994: linux-2.6-x86_64-perfctr-dont-use-cccr_ovf_pmi1-on-pentium-4-ds.patch
Patch22995: linux-2.6-misc-cpufreq-fix-format-string-bug.patch
Patch22996: linux-2.6-misc-pipe-support-to-proc-sys-net-core_pattern.patch
Patch22997: linux-2.6-xen-ia64-numa-support.patch
Patch22998: linux-2.6-xen-ia64-kludge-for-xen_guest_handle_64.patch
Patch22999: linux-2.6-xen-numa-extend-physinfo-sysctl-to-export-topo-info.patch
Patch23000: linux-2.6-x86_64-kprobe-kprobe-booster-and-return-probe-booster.patch
Patch23001: linux-2.6-xen-ia64-disable-paravirt-to-remap-dev-mem.patch
Patch23002: linux-2.6-xen-ia64-revert-paravirt-to-ioremap-proc-pci.patch
Patch23003: linux-2.6-xen-ia64-issue-ioremap-hc-in-pci_acpi_scan_root.patch
Patch23004: linux-2.6-xen-ia64-mark-resource-list-functions-__devinit.patch
Patch23005: linux-2.6-x86_64-xen-local-dos-due-to-nt-bit-leakage.patch
Patch23006: linux-2.6-misc-mmtimer-fixes-for-high-resolution-timers.patch
Patch23007: linux-2.6-mm-numa-over-committing-memory-compiler-warnings.patch
Patch23008: linux-2.6-misc-cleanup-header-warnings-and-enable-header-check.patch
Patch23009: linux-2.6-ppc64-spu-add-cpufreq-governor.patch
Patch23010: linux-2.6-xen-disallow-nested-event-delivery.patch
Patch23011: linux-2.6-xen-use-unlocked_ioctl-in-evtchn-gntdev-and-privcmd.patch
Patch23012: linux-2.6-xen-process-event-channel-notifications-in-round-robin.patch
Patch23013: linux-2.6-xen-make-last-processed-event-channel-a-per-cpu-var.patch
Patch23014: linux-2.6-xen-ia64-speed-up-hypercall-for-guest-domain-creation.patch
Patch23015: linux-2.6-fs-relayfs-support-larger-on-memory-buffer.patch
Patch23016: linux-2.6-net-ipv6-configurable-address-selection-policy-table.patch
Patch23017: linux-2.6-firewire-latest-upstream-snapshot-for-rhel-5-3.patch
Patch23018: linux-2.6-x86_64-gart-iommu-alignment-fixes.patch
Patch23019: linux-2.6-x86_64-amd-iommu-driver-support.patch
Patch23020: linux-2.6-misc-fix-kernel-builds-on-modern-userland.patch
Patch23021: linux-2.6-ide-fix-issue-when-appending-data-on-an-existing-dvd.patch
Patch23022: linux-2.6-block-performance-fix-for-too-many-physical-devices.patch
Patch23023: linux-2.6-firmware-fix-ibft-offset-calculation.patch
Patch23024: linux-2.6-openib-lost-interrupt-after-lpar-to-lpar-communication.patch
Patch23025: linux-2.6-x86-hpet-consolidate-assignment-of-hpet_period.patch
Patch23026: linux-2.6-usb-wacom-fix-maximum-distance-values.patch
Patch23027: linux-2.6-usb-wacom-add-support-for-intuos3-4x6.patch
Patch23028: linux-2.6-usb-wacom-add-support-for-cintiq-20wsx.patch
Patch23029: linux-2.6-fs-ext4-new-s390-bitops.patch
Patch23030: linux-2.6-fs-ext4-2-6-27-rc3-upstream-codebase.patch
Patch23031: linux-2.6-fs-ext4-revert-delalloc-upstream-mods.patch
Patch23032: linux-2.6-fs-ext4-fixes-from-upstream-pending-patch-queue.patch
Patch23033: linux-2.6-fs-ext4-kconfig-makefile-config-glue.patch
Patch23034: linux-2.6-fs-ext4-backport-to-rhel5-3-interfaces.patch
Patch23035: linux-2.6-misc-make-printk-more-robust-against-kexec-shutdowns.patch
Patch23036: linux-2.6-x86_64-amd-8-socket-apicid-patches.patch
Patch23037: linux-2.6-usb-work-around-iso-transfers-in-sb700.patch
Patch23038: linux-2.6-net-random32-seeding-improvement.patch
Patch23039: linux-2.6-wireless-iwlwifi-post-2-6-27-rc3-to-support-iwl5x00.patch
Patch23040: linux-2.6-mm-keep-pagefault-from-happening-under-page-lock.patch
Patch23041: linux-2.6-tty-cleanup-release_mem.patch
Patch23042: linux-2.6-tty-add-shutdown-method.patch
Patch23043: linux-2.6-vt-add-shutdown-method.patch
Patch23044: linux-2.6-tty-add-termiox-support.patch
Patch23045: linux-2.6-serial-8250-support-for-dtr-dsr-hardware-flow-control.patch
Patch23046: linux-2.6-wireless-compiler-warning-fixes-for-mac80211-update.patch
Patch23047: linux-2.6-x86_64-use-strncmp-for-memmap-exactmap-boot-argument.patch
Patch23048: linux-2.6-ia64-mca-recovery-montecito-support.patch
Patch23049: linux-2.6-ia64-handle-tlb-errors-from-duplicate-itr-d-dropins.patch
Patch23050: linux-2.6-ia64-cache-error-recovery.patch
Patch23051: linux-2.6-ia64-pal-calls-need-physical-mode-stacked.patch
Patch23052: linux-2.6-ia64-add-dp-bit-to-cache-and-bus-check-structs.patch
Patch23053: linux-2.6-ia64-add-se-bit-to-processor-state-parameter-structure.patch
Patch23054: linux-2.6-ia64-more-itanium-pal-spec-updates.patch
Patch23055: linux-2.6-ia64-update-processor_info-features.patch
Patch23056: linux-2.6-ia64-bte-error-timer-fix.patch
Patch23057: linux-2.6-ia64-fix-altix-bte-error-return-status.patch
Patch23058: linux-2.6-ia64-force-error-to-surface-in-nofault-code.patch
Patch23059: linux-2.6-ia64-cmc-cpe-reverse-fetching-log-and-checking-poll.patch
Patch23060: linux-2.6-ia64-clean-up-cpe-handler-registration.patch
Patch23061: linux-2.6-ia64-remove-needless-delay-in-mca-rendezvous.patch
Patch23062: linux-2.6-ia64-support-multiple-cpus-going-through-os_mca.patch
Patch23063: linux-2.6-ia64-don-t-set-psr-ic-and-psr-i-simultaneously.patch
Patch23064: linux-2.6-ia64-disable-re-enable-cpe-interrupts-on-altix.patch
Patch23065: linux-2.6-ia64-fix-large-mca-bootmem-allocation.patch
Patch23066: linux-2.6-ia64-correct-pernodesize-calculation.patch
Patch23067: linux-2.6-xen-ia64-pv-shared-used-header-file-changes.patch
Patch23068: linux-2.6-xen-ia64-pv-makefile-changes.patch
Patch23069: linux-2.6-xen-ia64-pv-kconfig-additions.patch
Patch23070: linux-2.6-mm-fix-support-for-fast-get-user-pages.patch
Patch23071: linux-2.6-md-dm-mpath-fix-bugs-in-error-paths.patch
Patch23072: linux-2.6-md-dm-crypt-use-cond_resched.patch
Patch23073: linux-2.6-md-dm-snapshots-race-condition-and-data-corruption.patch
Patch23074: linux-2.6-md-dm-snapshot-fix-race-during-exception-creation.patch
Patch23075: linux-2.6-scsi-megaraid_sas-update-to-version-4-01-rh1.patch
Patch23076: linux-2.6-scsi-3w-xxxx-update-to-version-1-26-03-000.patch
Patch23077: linux-2.6-scsi-3w-9xxx-update-to-version-2-26-08-003.patch
Patch23078: linux-2.6-md-dm-reject-barrier-requests.patch
Patch23079: linux-2.6-md-fix-error-propogation-in-raid-arrays.patch
Patch23080: linux-2.6-md-fix-handling-of-sense-buffer-in-eh-commands.patch
Patch23081: linux-2.6-scsi-lpfc-update-to-version-8-2-0-30.patch
Patch23082: linux-2.6-scsi-iscsi-fix-nop-timeout-detection.patch
Patch23083: linux-2.6-net-pppoe-check-packet-length-on-all-receive-paths.patch
Patch23084: linux-2.6-scsi-cciss-support-for-new-controllers.patch
Patch23085: linux-2.6-scsi-cciss-support-for-sg_ioctl.patch
Patch23086: linux-2.6-x86-amd-oprofile-support-instruction-based-sampling.patch
Patch23087: linux-2.6-net-ixgb-hardware-support-and-other-upstream-fixes.patch
Patch23088: linux-2.6-net-bnx2x-update-to-upstream-version-1-45-20.patch
Patch23089: linux-2.6-misc-intel-new-sata-usb-hd-audio-and-i2c-smbus-ids.patch
Patch23090: linux-2.6-net-igb-update-to-upstream-version-1-2-45-k2.patch
Patch23091: linux-2.6-net-tg3-update-to-upstream-version-3-93.patch
Patch23092: linux-2.6-net-e1000e-update-to-upstream-version-0-3-3-3-k2.patch
Patch23093: linux-2.6-net-bnx2-update-to-upstream-version-1-7-9.patch
Patch23094: linux-2.6-net-update-myri10ge-10gbs-ethernet-driver.patch
Patch23095: linux-2.6-net-sky2-re-enable-88e8056-for-most-motherboards.patch
Patch23096: linux-2.6-net-skge-don-t-clear-mc-state-on-link-down.patch
Patch23097: linux-2.6-md-deadlock-with-nested-lvms.patch
Patch23098: linux-2.6-md-dm-kcopyd-private-mempool.patch
Patch23099: linux-2.6-md-dm-snapshot-use-per-device-mempools.patch
Patch23100: linux-2.6-openib-ofed-1-3-2-pre-update.patch
Patch23101: linux-2.6-net-bonding-fix-locking-in-802-3ad-mode.patch
Patch23102: linux-2.6-dlm-fix-address-compare.patch
Patch23103: linux-2.6-net-ixgbe-update-to-version-1-3-18-k4.patch
Patch23104: linux-2.6-scsi-scsi_netlink-transport-lld-receive-event-support.patch
Patch23105: linux-2.6-scsi-scsi_host_lookup-error-returns-and-null-pointers.patch
Patch23106: linux-2.6-net-niu-enable-support-for-sun-neptune-cards.patch
Patch23107: linux-2.6-net-cxgb3-updates-and-lro-fixes.patch
Patch23108: linux-2.6-net-bnx2x-update-to-upstream-version-1-45-21.patch
Patch23109: linux-2.6-nfs-v4-handle-old-format-exports-gracefully.patch
Patch23110: linux-2.6-audit-fix-compile-when-config_auditsyscall-is-disabled.patch
Patch23111: linux-2.6-ia64-kprobes-support-kprobe-booster.patch
Patch23112: linux-2.6-misc-remove-max_arg_pages-limit-independent-stack-top.patch
Patch23113: linux-2.6-misc-remove-max_arg_pages-limit-rework-execve-audit.patch
Patch23114: linux-2.6-misc-remove-max_arg_pages-limit-var-length-argument.patch
Patch23115: linux-2.6-xen-virtio-add-pv-network-and-block-drivers-for-kvm.patch
Patch23116: linux-2.6-scsi-sd-revalidate_disk-wrapper.patch
Patch23117: linux-2.6-fs-wrapper-for-lower-level-revalidate_disk-routines.patch
Patch23118: linux-2.6-fs-adjust-block-device-size-after-an-online-resize.patch
Patch23119: linux-2.6-fs-check-for-device-resize-when-rescanning-partitions.patch
Patch23120: linux-2.6-fs-add-flush_disk-to-flush-out-common-buffer-cache.patch
Patch23121: linux-2.6-fs-call-flush_disk-after-detecting-an-online-resize.patch
Patch23122: linux-2.6-security-key-increase-payload-size-when-instantiating.patch
Patch23123: linux-2.6-security-key-fix-lockdep-warning-when-revoking-auth.patch
Patch23124: linux-2.6-fs-proc-fix-open-less-usage-due-to-proc_fops-flip.patch
Patch23125: linux-2.6-fs-introduce-a-function-to-register-iget-failure.patch
Patch23126: linux-2.6-fs-cifs-latest-upstream-for-rhel-5-3.patch
Patch23127: linux-2.6-md-device-mapper-interface-exposure.patch
Patch23128: linux-2.6-md-dm-log-move-dirty-log-into-separate-module.patch
Patch23129: linux-2.6-md-clean-up-the-dm-io-interface.patch
Patch23130: linux-2.6-md-dm-log-clean-interface.patch
Patch23131: linux-2.6-md-dm-log-move-register-functions.patch
Patch23132: linux-2.6-md-remove-internal-mod-refs-fields-from-interface.patch
Patch23133: linux-2.6-md-expose-dm-h-macros.patch
Patch23134: linux-2.6-md-move-include-files-to-include-linux-for-exposure.patch
Patch23135: linux-2.6-xen-fix-crash-on-irq-exhaustion-and-increase-nr_irqs.patch
Patch23136: linux-2.6-acpi-thinkpad_acpi-update-to-upstream-for-rhel-5-3.patch
Patch23137: linux-2.6-acpi-cpufreq-update-to-upstream-for-rhel-5-3.patch
Patch23138: linux-2.6-acpi-increase-deep-idle-state-residency-on-platforms.patch
Patch23139: linux-2.6-acpi-increase-deep-idle-state-residency-on-platforms-2.patch
Patch23140: linux-2.6-net-tun-add-iff_vnet_hdr-tungetfeatures-tungetiff.patch
Patch23141: linux-2.6-fs-jdb-add-missing-error-checks-for-file-data-writes.patch
Patch23142: linux-2.6-fs-ext3-don-t-read-inode-block-if-buf-has-write-error.patch
Patch23143: linux-2.6-fs-jdb-abort-when-failed-to-log-metadata-buffers.patch
Patch23144: linux-2.6-fs-jbd-don-t-dirty-original-metadata-buffer-on-abort.patch
Patch23145: linux-2.6-fs-jbd-fix-commit-code-to-properly-abort-journal.patch
Patch23146: linux-2.6-fs-ext3-add-checks-for-errors-from-jbd.patch
Patch23147: linux-2.6-fs-jdb-fix-error-handling-for-checkpoint-i-o.patch
Patch23148: linux-2.6-crypto-tcrypt-group-common-speed-templates.patch
Patch23149: linux-2.6-crypto-tcrypt-shrink-speed-templates.patch
Patch23150: linux-2.6-crypto-tcrypt-change-the-usage-of-the-test-vectors.patch
Patch23151: linux-2.6-crypto-tcrypt-aes-cbc-test-vector-from-nist-sp800-38a.patch
Patch23152: linux-2.6-crypto-tcrypt-shrink-the-tcrypt-module.patch
Patch23153: linux-2.6-crypto-tcrypt-catch-cipher-destination-mem-corruption.patch
Patch23154: linux-2.6-crypto-tcrpyt-remove-unnecessary-kmap-kunmap-calls.patch
Patch23155: linux-2.6-crypto-tcrypt-avoid-using-contiguous-pages.patch
Patch23156: linux-2.6-crypto-tcrypt-abort-and-only-log-if-there-is-an-error.patch
Patch23157: linux-2.6-crypto-api-missing-accessors-for-new-crypto_alg-field.patch
Patch23158: linux-2.6-crypto-tcrypt-self-test-for-des3_ebe-cipher.patch
Patch23159: linux-2.6-crypto-tcrypt-add-alg_test-interface.patch
Patch23160: linux-2.6-crypto-cryptomgr-add-test-infrastructure.patch
Patch23161: linux-2.6-crypto-api-use-test-infrastructure.patch
Patch23162: linux-2.6-crypto-cryptomgr-test-ciphers-using-ecb.patch
Patch23163: linux-2.6-crypto-api-add-fips_enable-flag.patch
Patch23164: linux-2.6-crypto-rng-rng-interface-and-implementation.patch
Patch23165: linux-2.6-crypto-skcipher-use-rng-instead-of-get_random_bytes.patch
Patch23166: linux-2.6-crypto-tcrypt-change-the-xtea-test-vectors.patch
Patch23167: linux-2.6-fs-binfmt_misc-avoid-potential-kernel-stack-overflow.patch
Patch23168: linux-2.6-misc-driver-core-port-bus-notifiers.patch
Patch23169: linux-2.6-scsi-add-infrastructure-for-scsi-device-handlers.patch
Patch23170: linux-2.6-md-dm-mpath-use-scsi-device-handler.patch
Patch23171: linux-2.6-scsi-scsi_dh-add-rdac-handler.patch
Patch23172: linux-2.6-scsi-scsi_dh-add-alua-handler.patch
Patch23173: linux-2.6-acpi-add-3-0-_tsd-_tpc-_tss-_ptc-throttling-support.patch
Patch23174: linux-2.6-char-add-range_is_allowed-check-to-mmap_mem.patch
Patch23175: linux-2.6-x86_64-suspend-to-disk-fails-with-4gb-of-ram.patch
Patch23176: linux-2.6-wireless-rt2x00-avoid-null-ptr-deref-when-probe-fails.patch
Patch23177: linux-2.6-fs-jbd-test-bh_write_eio-to-detect-errors-on-metadata.patch
Patch23178: linux-2.6-xen-remove-proc-xen-from-bare-metal-and-fv-guests.patch
Patch23179: linux-2.6-scsi-fix-medium-error-handling-with-bad-devices.patch
Patch23180: linux-2.6-scsi-st-buffer-size-doesn-t-match-block-size-panics.patch
Patch23181: linux-2.6-ia64-multiple-outstanding-ptc-g-instruction-support.patch
Patch23182: linux-2.6-ia64-param-for-max-num-of-concurrent-global-tlb-purges.patch
Patch23183: linux-2.6-ia64-set-default-max_purges-1-regardless-of-pal-return.patch
Patch23184: linux-2.6-scsi-qla2xxx-add-isp84xx-support.patch
Patch23185: linux-2.6-scsi-qla2xxx-add-more-statistics.patch
Patch23186: linux-2.6-scsi-qla2xxx-upstream-changes-from-8-01-07-k7.patch
Patch23187: linux-2.6-scsi-qla2xxx-update-8-02-00-k1-to-8-02-00-k4.patch
Patch23188: linux-2.6-gfs2-nfsv4-delegations-fix-for-cluster-systems.patch
Patch23189: linux-2.6-xen-netfront-xenbus-race.patch
Patch23190: linux-2.6-misc-holdoffs-in-hrtimer_run_queues.patch
Patch23191: linux-2.6-misc-hrtimer-optimize-softirq.patch
Patch23192: linux-2.6-scsi-qla2xxx-mgmt-api-ct-pass-thru.patch
Patch23193: linux-2.6-scsi-qla2xxx-mgmt-api-for-fcoe-netlink.patch
Patch23194: linux-2.6-audit-audit-tty-input.patch
Patch23195: linux-2.6-fs-implement-fallocate-syscall.patch
Patch23196: linux-2.6-scsi-aic79xx-reset-hba-on-kdump-kernel-boot.patch
Patch23197: linux-2.6-xen-kdump-ability-to-use-makedumpfile-with-vmcoreinfo.patch
Patch23198: linux-2.6-md-lvm-raid-1-performance-fixes.patch
Patch23199: linux-2.6-md-lvm-raid-1-performance-fixes-2.patch
Patch23200: linux-2.6-net-r8169-add-support-and-fixes.patch
Patch23201: linux-2.6-fs-ext4-vfs-mm-core-delalloc-support.patch
Patch23202: linux-2.6-scsi-fusion-update-to-version-3-04-07.patch
Patch23203: linux-2.6-misc-preempt-notifiers-implementation.patch
Patch23204: linux-2.6-misc-futex-private-futexes.patch
Patch23205: linux-2.6-misc-hpilo-update-to-upstream-2-6-27.patch
Patch23206: linux-2.6-misc-hpilo-update-driver-to-0-5.patch
Patch23207: linux-2.6-misc-hpilo-cleanup-device_create-for-rhel-5-3.patch
Patch23208: linux-2.6-scsi-qla2xxx-qla84xx-update-to-upstream-for-rhel-5-3.patch
Patch23209: linux-2.6-crypto-fix-panic-in-hmac-self-test.patch
Patch23210: linux-2.6-net-enable-tso-if-supported-by-at-least-one-device.patch
Patch23211: linux-2.6-xen-cpufreq-fix-nehalem-supermicro-systems.patch
Patch23212: linux-2.6-misc-revert-misc-fix-wrong-test-in-wait_task_stopped.patch
Patch23213: linux-2.6-fs-ecryptfs-update-to-2-6-26-codebase.patch
Patch23214: linux-2.6-fs-ecryptfs-propagate-key-errors-up-at-mount-time.patch
Patch23215: linux-2.6-fs-ecryptfs-privileged-kthread-for-lower-file-opens.patch
Patch23216: linux-2.6-fs-ecryptfs-discard-ecryptfsd-registration-messages.patch
Patch23217: linux-2.6-fs-ecryptfs-string-copy-cleanup.patch
Patch23218: linux-2.6-fs-ecryptfs-unaligned-access-helpers.patch
Patch23219: linux-2.6-fs-ecryptfs-delay-lower-file-opens-until-needed.patch
Patch23220: linux-2.6-scsi-qla2xxx-update-8-02-00-k5-to-8-02-00-k6.patch
Patch23221: linux-2.6-md-add-config-option-for-dm-raid4-5-target.patch
Patch23222: linux-2.6-md-add-device-mapper-dirty-region-hash.patch
Patch23223: linux-2.6-md-add-device-mapper-message-parser.patch
Patch23224: linux-2.6-md-add-device-mapper-raid4-5-target.patch
Patch23225: linux-2.6-md-export-dm_disk-and-dm_put.patch
Patch23226: linux-2.6-md-add-device-mapper-object-memory-cache.patch
Patch23227: linux-2.6-md-add-device-mapper-object-memory-cache-interface.patch
Patch23228: linux-2.6-md-add-device-mapper-dirty-region-hash-file.patch
Patch23229: linux-2.6-md-add-device-mapper-raid4-5-stripe-locking-interface.patch
Patch23230: linux-2.6-md-add-device-mapper-message-parser-interface.patch
Patch23231: linux-2.6-fs-ecryptfs-disallow-mounts-on-nfs-cifs-ecryptfs.patch
Patch23232: linux-2.6-ia64-procfs-reduce-the-size-of-page-table-cache.patch
Patch23233: linux-2.6-ia64-procfs-show-the-size-of-page-table-cache.patch
Patch23234: linux-2.6-acpi-correctly-allow-wol-from-s4-state.patch
Patch23235: linux-2.6-nfs-disable-the-fsc-mount-option.patch
Patch23236: linux-2.6-net-ipv6-extra-sysctls-for-additional-tahi-tests.patch
Patch23237: linux-2.6-audit-audit-fork-patch.patch
Patch23238: linux-2.6-scsi-qla2xxx-additional-residual-count-correction.patch
Patch23239: linux-2.6-gfs2-panic-if-you-misspell-any-mount-options.patch
Patch23240: linux-2.6-gfs2-glock-deadlock-in-page-fault-path.patch
Patch23241: linux-2.6-scsi-libiscsi-data-corruption-when-resending-packets.patch
Patch23242: linux-2.6-xen-virtio-include-headers-in-kernel-headers-package.patch
Patch23243: linux-2.6-pci-allow-multiple-calls-to-pcim_enable_device.patch
Patch23244: linux-2.6-openib-add-an-enum-for-future-rds-support.patch
Patch23245: linux-2.6-docs-update-kernel-parameters-with-tick-divider.patch
Patch23246: linux-2.6-revert-mm-numa-system-is-slow-when-over-committing-memory.patch
Patch23247: linux-2.6-scsi-modify-failfast-so-it-does-not-always-fail-fast.patch
Patch23248: linux-2.6-mm-check-physical-address-range-in-ioremap.patch
Patch23249: linux-2.6-x86-mm-fix-endless-page-faults-in-mount_block_root.patch
Patch23250: linux-2.6-x86_64-revert-time-syscall-changes.patch
Patch23251: linux-2.6-scsi-fix-hang-introduced-by-failfast-changes.patch
Patch23252: linux-2.6-scsi-failfast-bit-setting-in-dm-multipath-multipath.patch
Patch23253: linux-2.6-x86_64-nmi-wd-clear-perf-counter-registers-on-p4.patch
Patch23254: linux-2.6-mm-filemap-fix-iov_base-data-corruption.patch
Patch23255: linux-2.6-ppc64-edac-enable-for-cell-platform.patch
Patch23256: linux-2.6-ppc64-subpage-protection-for-pave.patch
Patch23257: linux-2.6-scsi-qla2xxx-support-pci-enhanced-error-recovery.patch
Patch23258: linux-2.6-ata-libata-rmmod-pata_sil680-hangs.patch
Patch23259: linux-2.6-scsi-qla2xxx-use-rport-dev-loss-timeout-consistently.patch
Patch23260: linux-2.6-misc-add-tracepoints-to-activate-deactivate_task.patch
Patch23261: linux-2.6-fs-ecryptfs-off-by-one-writing-null-to-end-of-string.patch
Patch23262: linux-2.6-tty-termiox-support-missing-mutex-lock.patch
Patch23263: linux-2.6-misc-preempt-notifier-fixes.patch
Patch23264: linux-2.6-net-e1000-add-module-param-to-set-tx-descriptor-power.patch
Patch23265: linux-2.6-net-bnx2-fix-problems-with-multiqueue-receive.patch
Patch23266: linux-2.6-scsi-qla2xxx-update-24xx-25xx-firmware-for-rhel-5-3.patch
Patch23267: linux-2.6-net-ipt_clusterip-fix-imbalanced-ref-count.patch
Patch23268: linux-2.6-net-enic-add-new-10gbe-device.patch
Patch23269: linux-2.6-scsi-qla2xxx-use-the-flash-descriptor-table.patch
Patch23270: linux-2.6-scsi-qla2xxx-use-the-flash-layout-table.patch
Patch23271: linux-2.6-scsi-qla2xxx-use-the-npiv-table-to-instantiate-port.patch
Patch23272: linux-2.6-s390-qdio-fix-module-ref-counting-in-qdio_free.patch
Patch23273: linux-2.6-net-e1000e-protect-ichx-nvm-from-malicious-write-erase.patch
Patch23274: linux-2.6-net-correct-mode-setting-for-extended-sysctl-interface.patch
Patch23275: linux-2.6-scsi-scsi_error-retry-cmd-handling-of-transport-error.patch
Patch23276: linux-2.6-ppc64-netboot-image-too-large.patch
Patch23277: linux-2.6-revert-mm-fix-support-for-fast-get-user-pages.patch
Patch23278: linux-2.6-agp-add-support-for-intel-cantiga-and-eaglelake.patch
Patch23279: linux-2.6-drm-support-for-intel-cantiga-and-eaglelake.patch
Patch23280: linux-2.6-scsi-fix-queue_full-retry-handling.patch
Patch23281: linux-2.6-scsi-qla2xxx-new-version-string-defintion.patch
Patch23282: linux-2.6-audit-fix-nul-handling-in-tty-input-auditing.patch
Patch23283: linux-2.6-dlm-add-old-plock-interface.patch
Patch23284: linux-2.6-fs-open-allows-setgid-bit-when-user-is-not-in-group.patch
Patch23285: linux-2.6-fs-remove-suid-when-splicing-into-an-inode.patch
Patch23286: linux-2.6-gfs2-fix-for-noatime-support.patch
Patch23287: linux-2.6-ata-libata-ata_piix-sata-ide-combined-mode-fix.patch
Patch23288: linux-2.6-net-sky2-fix-hang-resulting-from-link-flap.patch
Patch23289: linux-2.6-gfs2-fix-jdata-page-invalidation.patch
Patch23290: linux-2.6-ata-libata-ahci-enclosure-management-support.patch
Patch23291: linux-2.6-misc-posix-timers-event-vs-dequeue_signal-race.patch
Patch23292: linux-2.6-scsi-cciss-the-output-of-lun-size-and-type-wrong.patch
Patch23293: linux-2.6-scsi-aacraid-remove-some-quirk-aac_quirk_scsi_32-bits.patch
Patch23294: linux-2.6-dm-mpath-moving-path-activation-to-workqueue-panics.patch
Patch23295: linux-2.6-scsi-qla2xxx-merge-errors-caused-initialize-failures.patch
Patch23296: linux-2.6-agp-correct-bug-in-stolen-size-calculations.patch
Patch23297: linux-2.6-agp-re-introduce-82g965-graphics-support.patch
Patch23298: linux-2.6-scsi-fix-oops-after-trying-to-removing-rport-twice.patch
Patch23299: linux-2.6-scsi-qla2xxx-prevent-npiv-conf-for-older-hbas.patch
Patch23300: linux-2.6-pci-set-domain-node-to-0-in-pci-bios-enum-code-path.patch
Patch23301: linux-2.6-misc-futex-fixup-futex-compat-for-private-futexes.patch
Patch23302: linux-2.6-ppc64-support-o_nonblock-in-proc-ppc64-rtas-error_log.patch
Patch23303: linux-2.6-crypto-fix-ipsec-crash-with-mac-longer-than-16-bytes.patch
Patch23304: linux-2.6-fs-ext4-fix-warning-on-x86_64-build.patch
Patch23305: linux-2.6-input-atkbd-delay-executing-of-led-switching-request.patch
Patch23306: linux-2.6-nfs-portmap-client-race.patch
Patch23307: linux-2.6-x86-pae-limit-ram-to-64gb-pae36.patch
Patch23308: linux-2.6-openib-ehca-add-flush-cqe-generation.patch
Patch23309: linux-2.6-ppc64-spus-hang-when-run-with-affinity-1.patch
Patch23310: linux-2.6-ppc64-spus-hang-when-run-with-affinity-2.patch
Patch23311: linux-2.6-ppc64-fix-race-for-a-free-spu.patch
Patch23312: linux-2.6-net-sctp-init-ack-indicates-no-auth-peer-support-oops.patch
Patch23313: linux-2.6-ppc64-add-missing-symbols-to-vmcoreinfo.patch
Patch23314: linux-2.6-fs-ext4-add-missing-aops.patch
Patch23315: linux-2.6-fs-don-t-allow-splice-to-files-opened-with-o_append.patch
Patch23316: linux-2.6-openib-ehca-attempt-to-free-srq-when-none-exists.patch
Patch23317: linux-2.6-nfs-remove-recoverable-bug_on.patch
Patch23318: linux-2.6-gfs2-set-gfp-for-data-mappings-to-gfp_nofs.patch
Patch23319: linux-2.6-misc-ptrace-fix-exec-report.patch
Patch23320: linux-2.6-md-random-memory-corruption-in-snapshots.patch
Patch23321: linux-2.6-net-tcp-let-skbs-grow-over-a-page-on-fast-peers.patch
Patch23322: linux-2.6-ia64-fix-ptrace-hangs-when-following-threads.patch
Patch23323: linux-2.6-net-ipv4-fix-byte-value-boundary-check.patch
Patch23324: linux-2.6-xen-fix-crash-on-irq-exhaustion.patch
Patch23325: linux-2.6-xen-fv-fix-lockdep-warnings-when-running-debug-kernel.patch
Patch23326: linux-2.6-net-tun-fix-printk-warning.patch
Patch23327: linux-2.6-drm-i915-driver-arbitrary-ioremap.patch
Patch23328: linux-2.6-x86_64-create-a-fallback-for-ibm-calgary.patch
Patch23329: linux-2.6-ppc64-eeh-pci-e-recovery-fails-e1000-support-msi.patch
Patch23330: linux-2.6-x86-make-halt-f-command-work-correctly.patch
Patch23331: linux-2.6-wireless-iwlwifi-fix-busted-tkip-encryption-_again_.patch
Patch23332: linux-2.6-xen-virtio_net-some-relatively-minor-fixes.patch
Patch23333: linux-2.6-net-e1000e-update-driver-to-support-recovery.patch
Patch23334: linux-2.6-net-allow-rcv-on-inactive-slaves-if-listener-exists.patch
Patch23335: linux-2.6-misc-rtc-disable-sigio-notification-on-close.patch
Patch23336: linux-2.6-fs-ecryptfs-storing-crypto-info-in-xattr-corrupts-mem.patch
Patch23337: linux-2.6-net-ixgbe-bring-up-device-without-crashing-fix.patch
Patch23338: linux-2.6-ppc64-ptcal-has-to-be-disabled-to-use-kexec-on-qs21.patch
Patch23339: linux-2.6-ppc64-kexec-kdump-disable-ptcal-on-qs21.patch
Patch23340: linux-2.6-s390-qdio-speedup-multicast-on-full-hipersocket-queue.patch
Patch23341: linux-2.6-scsi-lpfc-emulex-rhel-5-3-bugfixes.patch
Patch23342: linux-2.6-scsi-qla2xxx-restore-disable-by-default-of-msi-msi-x.patch
Patch23343: linux-2.6-scsi-qla2xxx-84xx-show-fw-ver-and-netlink-code-fixes.patch
Patch23344: linux-2.6-scsi-qla2xxx-correct-atmel-flash-part-handling.patch
Patch23345: linux-2.6-xen-pv-dom0-hang-when-device-re-attached-to-in-guest.patch
Patch23346: linux-2.6-openib-ehca-queue-and-completion-pair-setup-problem.patch
Patch23347: linux-2.6-fs-autofs4-cleanup-autofs-mount-type-usage.patch
Patch23348: linux-2.6-fs-autofs4-correct-offset-mount-expire-check.patch
Patch23349: linux-2.6-fs-ext3-fix-accessing-freed-memory-in-ext3_abort.patch
Patch23350: linux-2.6-fs-ext4-delay-capable-checks-to-avoid-avc-denials.patch
Patch23351: linux-2.6-openib-ppc64-fix-using-sdp-on-64k-page-systems.patch
Patch23352: linux-2.6-scsi-add-libfc-and-software-fcoe-driver.patch
Patch23353: linux-2.6-scsi-add-fnic-driver.patch
Patch23354: linux-2.6-ppc64-clock_gettime-is-not-incrementing-nanoseconds.patch
Patch23355: linux-2.6-scsi-qla2xxx-fix-entries-in-class_device_attributes.patch
Patch23356: linux-2.6-acpi-fix-boot-hang-on-old-systems-without-_cst-methods.patch
Patch23357: linux-2.6-net-bonding-allow-downed-interface-before-mod-remove.patch
Patch23358: linux-2.6-wireless-iwlwifi-avoid-sleep-in-softirq-context.patch
Patch23359: linux-2.6-md-dm-raid45-c-revert-to-rhel5-dm-io-kabi.patch
Patch23360: linux-2.6-md-dm-raid45-c-add-target-to-makefile.patch
Patch23361: linux-2.6-md-dm-stripe-c-raid0-event-handling.patch
Patch23362: linux-2.6-scsi-qla3xxx-qla4xxx-update-use-new-version-format.patch
Patch23363: linux-2.6-acpi-check-common-dmi-tables-on-systems-with-acpi.patch
Patch23364: linux-2.6-x86-vdso-use-install_special_mapping.patch
Patch23365: linux-2.6-ppc64-spufs-missing-context-switch-notification-log-1.patch
Patch23366: linux-2.6-ppc64-spufs-missing-context-switch-notification-log-2.patch
Patch23367: linux-2.6-ppc64-cell-corrupt-spu-coredump-notes.patch
Patch23368: linux-2.6-xen-ia64-backport-check_pages_physically_contiguous.patch
Patch23369: linux-2.6-xen-remove-contiguous_bitmap.patch
Patch23370: linux-2.6-openib-race-in-ipoib_cm_post_receive_nonsrq.patch
Patch23371: linux-2.6-s390-qdio-repair-timeout-handling-for-qdio_shutdown.patch
Patch23372: linux-2.6-md-dm-raid1-support-extended-status-output.patch
Patch23373: linux-2.6-sata-libata-is-broken-with-large-disks.patch
Patch23374: linux-2.6-md-crash-in-device-mapper-if-the-user-removes-snapshot.patch
Patch23375: linux-2.6-nfs-oops-in-direct-i-o-error-handling.patch
Patch23376: linux-2.6-usb-fix-locking-for-input-devices.patch
Patch23377: linux-2.6-openib-ehca-remove-ref-to-qp-if-port-activation-fails.patch
Patch23378: linux-2.6-xen-uninitialized-watch-structure-can-lead-to-crashes.patch
Patch23379: linux-2.6-net-bonding-update-docs-for-arp_ip_target-behavior.patch
Patch23380: linux-2.6-net-bnx2-prevent-ethtool-r-eeh-event.patch
Patch23381: linux-2.6-ppc64-dma-mapping-provide-attributes-on-cell-platform.patch
Patch23382: linux-2.6-openib-ib_core-use-weak-ordering-for-user-memory.patch
Patch23383: linux-2.6-openib-mthca-fix-dma-mapping-leak.patch
Patch23384: linux-2.6-openib-ehca-deadlock-race-when-creating-small-queues.patch
Patch23385: linux-2.6-input-atkbd-cancel-delayed-work-before-freeing-struct.patch
Patch23386: linux-2.6-ppc64-cell-fix-page-fault-error-checking-in-spufs.patch
Patch23387: linux-2.6-wireless-iwlagn-mac80211-ibss-fixes.patch
Patch23388: linux-2.6-acpi-always-use-32-bit-value-for-gpe0-on-hp-xw-boxes.patch
Patch23389: linux-2.6-usb-add-hid_quirk_reset_leds-to-some-keyboards.patch
Patch23390: linux-2.6-video-uvc-buf-overflow-in-format-descriptor-parsing.patch
Patch23391: linux-2.6-s390-cio-fix-double-unregistering-of-subchannels.patch
Patch23392: linux-2.6-s390-cio-reduce-cpu-utilization-during-device-scan.patch
Patch23393: linux-2.6-firewire-various-bug-and-module-unload-hang-fixes.patch
Patch23394: linux-2.6-net-bnx2x-eeh-unload-probe-and-endian-fixes.patch
Patch23395: linux-2.6-acpi-thinkpad-fix-autoloading.patch
Patch23396: linux-2.6-selinux-recognize-addrlabel-netlink-messages.patch
Patch23397: linux-2.6-misc-lots-of-interrupts-with-proc-hz_timer-0.patch
Patch23398: linux-2.6-fs-cifs-corrupt-data-due-to-interleaved-write-calls.patch
Patch23399: linux-2.6-ppc64-spufs-clean-up-page-fault-error-checking.patch
Patch23400: linux-2.6-scsi-qla2xxx-no-npiv-for-loop-connections.patch
Patch23401: linux-2.6-md-dm-mpath-null-ptr-access-in-path-activation-code.patch
Patch23402: linux-2.6-libata-avoid-overflow-in-ata_tf_read_block.patch
Patch23403: linux-2.6-net-ixgbe-add-support-for-82598at.patch
Patch23404: linux-2.6-s390-missing-bits-for-audit-fork.patch
Patch23405: linux-2.6-s390-qeth-eddp-for-large-tso-skb-fragment-list.patch
Patch23406: linux-2.6-libata-force-sb600-700-ide-mode-into-ahci-on-resume.patch
Patch23407: linux-2.6-openib-ipoib-fix-oops-on-fabric-events.patch
Patch23408: linux-2.6-net-bnx2-add-support-for-5716s.patch
Patch23409: linux-2.6-scsi-update-fcoe-drivers.patch
Patch23410: linux-2.6-net-bnx2-fix-oops-on-call-to-poll_controller.patch
Patch23411: linux-2.6-xen-guest-crashes-if-rtl8139-nic-is-only-one-specified.patch
Patch23412: linux-2.6-xen-x86-fix-highmem-xen-c-bug.patch
Patch23413: linux-2.6-dlm-fix-up-memory-allocation-flags.patch
Patch23414: linux-2.6-net-e1000e-enable-ecc-correction-on-82571-silicon.patch
Patch23415: linux-2.6-usb-add-support-for-dell-keyboard-431c-2003.patch
Patch23416: linux-2.6-ia64-replace-printk-with-mprintk-in-mca-init-context.patch
Patch23417: linux-2.6-acpi-add-systems-to-gpe-register-blacklist.patch
Patch23418: linux-2.6-scsi-qla2xx-qla84xx-failure-to-establish-link.patch
Patch23419: linux-2.6-xen-build-xen-platform-pci-as-a-module.patch
Patch23420: linux-2.6-alsa-fix-pcm-write-blocking.patch
Patch23421: linux-2.6-edac-i5000_edac-fix-misc-thermal-error-messages.patch
Patch23422: linux-2.6-agp-use-contiguous-memory-to-support-xen.patch
Patch23423: linux-2.6-net-e1000e-remove-fix-for-eeh-restore-all-registers.patch
Patch23424: linux-2.6-pci-generic-fix-for-eeh-restore-all-registers.patch
Patch23425: linux-2.6-x86-fix-memory-less-numa-node-booting.patch
Patch23426: linux-2.6-scsi-cciss-add-two-new-pci-ids.patch
Patch23427: linux-2.6-misc-fix-check_dead_utrace-vs-do_wait-race.patch
Patch23428: linux-2.6-gfs2-recovery-stuck.patch
Patch23429: linux-2.6-x86-nmi_watchdog-call-do_nmi_callback-from-traps-xen.patch
Patch23430: linux-2.6-net-niu-fix-obscure-64-bit-read-issue.patch
Patch23431: linux-2.6-misc-hugepages-ia64-stack-overflow-and-corrupt-memory.patch
Patch23432: linux-2.6-s390-cio-dasd-device-driver-times-out.patch
Patch23433: linux-2.6-net-mlx4-panic-when-inducing-pci-bus-error.patch
Patch23434: linux-2.6-audit-race-between-inotify-watch-removal-and-unmount.patch
Patch23435: linux-2.6-misc-support-for-intel-s-ibex-peak.patch
Patch23436: linux-2.6-net-cxgb3-eeh-lro-and-multiqueue-fixes.patch
Patch23437: linux-2.6-net-cxgb3-embed-firmware-in-driver.patch
Patch23438: linux-2.6-net-fix-unix-sockets-kernel-panic.patch
Patch23439: linux-2.6-net-tun-jumbo-frame-support.patch
Patch23440: linux-2.6-net-virtio_net-jumbo-frame-support.patch
Patch23441: linux-2.6-net-virtio_net-mergeable-receive-buffers.patch
Patch23442: linux-2.6-misc-utrace-make-ptrace_state-refcountable.patch
Patch23443: linux-2.6-misc-utrace-prevent-ptrace_induce_signal-crash.patch
Patch23444: linux-2.6-misc-fix-add-return-signal-to-ptrace_report_exec.patch
Patch23445: linux-2.6-ata-libata-sata_nv-hard-reset-mcp55.patch
Patch23446: linux-2.6-openib-ehca-fix-generating-flush-work-completions.patch
Patch23447: linux-2.6-acpi-acpi_cpufreq-fix-panic-when-removing-module.patch
Patch23448: linux-2.6-fs-jbd-alter-eio-test-to-avoid-spurious-jbd-aborts.patch
Patch23449: linux-2.6-block-fix-max_segment_size-seg_boundary-mask-setting.patch
Patch23450: linux-2.6-ppc64-fix-system-calls-on-cell-entered-with-xer-so-1.patch
Patch23451: linux-2.6-ata-libata-lba_28_ok-sector-off-by-one.patch
Patch23452: linux-2.6-alsa-select-3stack-dig-model-for-sc-celsius-r670.patch
Patch23453: linux-2.6-x86_64-calgary-iommu-sysdata-fixes.patch
Patch23454: linux-2.6-xen-console-make-luks-passphrase-readable.patch
Patch23455: linux-2.6-x86_64-limit-num-of-mce-sysfs-files-removed-on-suspend.patch
Patch23456: linux-2.6-x86_64-fix-amd-iommu-boot-issue.patch
Patch23457: linux-2.6-wireless-iwlwifi-mac80211-various-small-fixes.patch
Patch23458: linux-2.6-net-cxgb3-fixup-embedded-firmware-problems.patch
Patch23459: linux-2.6-net-cxgb3-eeh-and-eeprom-fixups.patch
Patch23460: linux-2.6-scsi-qla2xx-qla84xx-occasional-panic-on-loading.patch
Patch23461: linux-2.6-scsi-remove-scsi_dh_alua.patch
Patch23462: linux-2.6-net-atm-prevent-local-denial-of-service.patch
Patch23463: linux-2.6-agp-update-the-names-of-some-graphics-drivers.patch
Patch23464: linux-2.6-scsi-qla4xxx-increase-iscsi-session-check-to-3-tuple.patch
Patch23465: linux-2.6-net-enic-update-to-version-1-0-0-648.patch
Patch23466: linux-2.6-misc-revert-mm-keep-pagefault-from-happening-under-pagelock.patch
Patch23467: linux-2.6-x86-disable-hpet-on-machine_crash_shutdown.patch
Patch23468: linux-2.6-scsi-lpfc-fix-cancel_retry_delay.patch
Patch23469: linux-2.6-scsi-fix-error-handler-to-call-scsi_decide_disposition.patch
Patch23470: linux-2.6-scsi-fcoe-update-drivers.patch
Patch23471: linux-2.6-scsi-mpt-fusion-disable-msi-by-default.patch
Patch23472: linux-2.6-net-cxgb3-fixup-embedded-firmware-problems-take-2.patch
Patch23473: linux-2.6-acpi-add-xw8600-and-xw6600-to-gpe0-block-blacklist.patch
Patch23474: linux-2.6-x86_64-proc-export-gart-region-through-proc-iomem.patch
Patch23475: linux-2.6-scsi-ibmvscsi-eh-fails-due-to-insufficient-resources.patch
Patch23476: linux-2.6-revert-x86-disable-hpet-on-machine_crash_shutdown.patch
Patch23477: linux-2.6-scsi-fnic-remove-link-down-count-processing.patch
Patch23478: linux-2.6-openib-fix-ipoib-oops-in-unicast_arp_send.patch
Patch23479: linux-2.6-xen-pv_hvm-guest-hang-on-fv-save-restore.patch
Patch23480: linux-2.6-xen-re-enable-using-xenpv-in-boot-path-for-fv-guests.patch
Patch23481: linux-2.6-revert-i386-check-for-dmi_data-in-powernow_k8-driver.patch
Patch23482: linux-2.6-cifs-cifs_writepages-may-skip-unwritten-pages.patch
Patch23483: linux-2.6-net-netlink-fix-overrun-in-attribute-iteration.patch
Patch23484: linux-2.6-fs-hfs-fix-namelength-memory-corruption.patch
Patch23485: linux-2.6-fs-hfsplus-check-read_mapping_page-return-value.patch
Patch23486: linux-2.6-fs-hfsplus-fix-buffer-overflow-with-a-corrupted-image.patch
Patch23487: linux-2.6-s390-zfcp-fix-hexdump-data-in-s390dbf-traces.patch
Patch23488: linux-2.6-misc-setpgid-returns-esrch-in-some-situations.patch
Patch23489: linux-2.6-x86_64-copy_user_c-assembler-can-leave-garbage-in-rsi.patch
Patch23490: linux-2.6-wireless-iwl-fix-bug_on-in-driver.patch
Patch23491: linux-2.6-net-add-preemption-point-in-qdisc_run.patch
Patch23492: linux-2.6-openib-restore-traffic-in-connected-mode-on-hca.patch
Patch23493: linux-2.6-md-fix-oops-with-device-mapper-mirror-target.patch
Patch23494: linux-2.6-net-sctp-overflow-with-bad-stream-id-in-fwd-tsn-chunk.patch
Patch23495: linux-2.6-net-deadlock-in-hierarchical-token-bucket-scheduler.patch
Patch23496: linux-2.6-nfs-handle-attribute-timeout-and-u32-jiffies-wrap.patch
Patch23497: linux-2.6-nfs-create-rpc-clients-with-proper-auth-flavor.patch
Patch23498: linux-2.6-sched-fix-clock_gettime-monotonicity.patch
Patch23499: linux-2.6-gfs2-mount-attempt-hangs-if-no-more-journals-available.patch
Patch23500: linux-2.6-fs-ext-234-directory-corruption-dos.patch
Patch23501: linux-2.6-x86-kdump-lockup-when-crashing-with-console_sem-held.patch
Patch23502: linux-2.6-crypto-fips-panic-kernel-if-we-fail-crypto-self-tests.patch
Patch23503: linux-2.6-x86_64-incorrect-cpu_khz-calculation-for-amd-processor.patch
Patch23504: linux-2.6-fs-link_path_walk-sanity-stack-usage-optimization.patch
Patch23505: linux-2.6-x86-pci-domain-re-enable-support-on-blacklisted-boxes.patch
Patch23506: linux-2.6-block-enforce-a-minimum-sg_io-timeout.patch
Patch23507: linux-2.6-misc-fix-memory-leak-during-pipe-failure.patch
Patch23508: linux-2.6-net-tcp-lp-prevent-chance-for-oops.patch
Patch23509: linux-2.6-net-ixgbe-frame-reception-and-ring-parameter-issues.patch
Patch23510: linux-2.6-security-keys-introduce-missing-kfree.patch
Patch23511: linux-2.6-crypto-fix-sha384-blocksize-definition.patch
Patch23512: linux-2.6-nfs-knfsd-make-readahead-params-cache-smp-friendly-2.patch
Patch23513: linux-2.6-nfs-knfsd-replace-kmalloc-memset-with-kcalloc-2.patch
Patch23514: linux-2.6-nfs-knfsd-read-ahead-cache-export-table-corruption-2.patch
Patch23515: linux-2.6-nfs-knfsd-alloc-readahead-cache-in-individual-chunks-2.patch
Patch23516: linux-2.6-ppc-don-t-reset-affinity-for-secondary-mpic-on-boot-2.patch
Patch23517: linux-2.6-audit-remove-bogus-newlines-in-execve-audit-records-2.patch
Patch23518: linux-2.6-net-gso-ensure-that-the-packet-is-long-enough-2.patch
Patch23519: linux-2.6-qla2xxx-correct-endianness-during-flash-manipulation-2.patch
Patch23520: linux-2.6-misc-fix-leap-second-hang.patch
Patch23521: linux-2.6-crypto-ccm-fix-handling-of-null-assoc-data.patch
Patch23522: linux-2.6-fs-ecryptfs-readlink-flaw.patch
Patch23523: linux-2.6-scsi-libata-sas_ata-fixup-sas_sata_ops.patch
Patch23524: linux-2.6-snd-fix-snd-sb16-ko-compile.patch
Patch23525: linux-2.6-s390-zfcp-remove-messages-flooding-the-kernel-log.patch
Patch23526: linux-2.6-s390-ipl-file-boot-then-boot-from-alt-dev-won-t-work.patch
Patch23527: linux-2.6-s390-dasd-oops-when-hyper-pav-alias-is-set-online.patch
Patch23528: linux-2.6-s390-lcs-output-request-completion-with-zero-cpa-val.patch
Patch23529: linux-2.6-crypto-export-dsa_verify-as-a-gpl-symbol.patch
Patch23530: linux-2.6-s390-sclp-incorrect-softirq-disable-enable.patch
Patch23531: linux-2.6-s390-qeth-avoid-skb_under_panic-for-bad-inbound-data.patch
Patch23532: linux-2.6-s390-qeth-avoid-problems-after-failing-recovery.patch
Patch23533: linux-2.6-x86-memmap-x-y-does-not-yield-new-map.patch
Patch23534: linux-2.6-fs-need-locking-when-reading-proc-pid-oom_score.patch
Patch23535: linux-2.6-video-avoid-writing-outside-shadow-bytes-array.patch
Patch23536: linux-2.6-fs-proc-proportional-set-size-calculation-and-display.patch
Patch23537: linux-2.6-crypto-ansi_cprng-extra-call-to-_get_more_prng_bytes.patch
Patch23538: linux-2.6-crypto-ansi_cprng-fix-inverted-dt-increment-routine.patch
Patch23539: linux-2.6-nfs-lockd-handle-long-grace-periods-correctly.patch
Patch23540: linux-2.6-nfs-race-with-nfs_access_cache_shrinker-and-umount.patch
Patch23541: linux-2.6-audit-increase-audit_max_key_len.patch
Patch23542: linux-2.6-audit-assorted-audit_filter_task-panics-on-ctx-null.patch
Patch23543: linux-2.6-audit-fix-kstrdup-error-check.patch
Patch23544: linux-2.6-audit-control-character-detection-is-off-by-one.patch
Patch23545: linux-2.6-audit-records-for-descr-created-by-pipe-and-socketpair.patch
Patch23546: linux-2.6-audit-misc-kernel-fixups.patch
Patch23547: linux-2.6-misc-ppc64-large-sends-fail-with-unix-domain-sockets.patch
Patch23548: linux-2.6-fs-inotify-send-in_attrib-event-on-link-count-changes.patch
Patch23549: linux-2.6-misc-futex-h-remove-kernel-bits-for-userspace-header.patch
Patch23550: linux-2.6-net-r8169-disable-the-ability-to-change-mac-address.patch
Patch23551: linux-2.6-ata-jmb361-only-has-one-port.patch
Patch23552: linux-2.6-crypto-des3_ede-permit-weak-keys-unless-req_weak_key.patch
Patch23553: linux-2.6-ppc-msi-interrupts-are-unreliable-on-ibm-qs21-and-qs22.patch
Patch23554: linux-2.6-ppc64-cell-axon-msi-retry-on-missing-interrupt.patch
Patch23555: linux-2.6-powerpc-wait-for-a-panic_timeout-0-before-reboot.patch
Patch23556: linux-2.6-scsi-no-sense-msgs-data-corruption-but-no-i-o-errors.patch
Patch23557: linux-2.6-net-s2io-flush-statistics-when-changing-the-mtu.patch
Patch23558: linux-2.6-xen-fix-disappearing-pci-devices-from-pv-guests.patch
Patch23559: linux-2.6-edac-add-i5400-driver.patch
Patch23560: linux-2.6-ppc-cell-fix-gdb-watchpoints.patch
Patch23561: linux-2.6-net-ipt_reject-properly-handle-ip-options.patch
Patch23562: linux-2.6-pci-msi-set-en-bit-for-devices-on-ht-based-platform.patch
Patch23563: linux-2.6-nfs-fix-hangs-during-heavy-write-workloads.patch
Patch23564: linux-2.6-nfs-memory-corruption-in-nfs3_xdr_setaclargs.patch
Patch23565: linux-2.6-gfs2-panic-in-debugfs_remove-when-unmounting.patch
Patch23566: linux-2.6-misc-backport-rusage_thread-support.patch
Patch23567: linux-2.6-fs-lockd-improve-locking-when-exiting-from-a-process.patch
Patch23568: linux-2.6-firmware-dell_rbu-prevent-oops.patch
Patch23569: linux-2.6-misc-minor-signal-handling-vulnerability.patch
Patch23570: linux-2.6-s390-dasd-dasd_device_from_cdev-called-from-interrupt.patch
Patch23571: linux-2.6-s390-cio-ccwgroup-online-vs-ungroup-race-condition.patch
Patch23572: linux-2.6-s390-qeth-unnecessary-support-ckeck-in-sysfs-route6.patch
Patch23573: linux-2.6-s390-disable-cpu-topology-support-by-default.patch
Patch23574: linux-2.6-s390-qdio-only-1-buffer-in-input_processing-state.patch
Patch23575: linux-2.6-s390-qeth-crash-in-case-of-layer-mismatch-for-vswitch.patch
Patch23576: linux-2.6-s390-qeth-print-hipersocket-version-on-z9-and-later.patch
Patch23577: linux-2.6-xen-irq-remove-superfluous-printk.patch
Patch23578: linux-2.6-misc-ptrace-utrace-fix-blocked-signal-injection.patch
Patch23579: linux-2.6-s390-cio-i-o-error-after-cable-pulls-2.patch
Patch23580: linux-2.6-ppc64-serial_core-define-fixed_port-flag.patch
Patch23581: linux-2.6-ppc-cell-add-support-for-power-button-on-blades.patch
Patch23582: linux-2.6-xen-guest-crash-when-host-has-64g-ram.patch
Patch23583: linux-2.6-scsi-ibmvscsi-n-port-id-support-on-ppc64.patch
Patch23584: linux-2.6-net-fix-icmp_send-and-icmpv6_send-host-re-lookup-code.patch
Patch23585: linux-2.6-net-ehea-improve-behaviour-in-low-mem-conditions.patch
Patch23586: linux-2.6-xen-fbfront-dirty-race.patch
Patch23587: linux-2.6-net-don-t-add-nat-extension-for-confirmed-conntracks.patch
Patch23588: linux-2.6-alt-x86-64-fix-int-0x80-enosys-return.patch
Patch23589: linux-2.6-misc-ia64-s390-add-kernel-version-to-panic-output.patch
Patch23590: linux-2.6-net-improve-udp-port-randomization.patch
Patch23591: linux-2.6-pci-fix-msi-descriptor-leak-during-hot-unplug.patch
Patch23592: linux-2.6-net-ipv6-hop-by-hop-options-header-returned-bad-value.patch
Patch23593: linux-2.6-net-sky2-update-driver-for-rhel-5-4.patch
Patch23594: linux-2.6-net-skbuff-fix-oops-in-skb_seq_read.patch
Patch23595: linux-2.6-scsi-handle-work-queue-and-shost_data-setup-failures.patch
Patch23596: linux-2.6-net-ipv6-check-length-of-users-s-optval-in-setsockopt.patch
Patch23597: linux-2.6-net-ipv6-update-setsockopt-to-support-rfc-3493.patch
Patch23598: linux-2.6-xen-disable-suspend-in-kernel.patch
Patch23599: linux-2.6-wireless-ath5k-update-to-f10-version.patch
Patch23600: linux-2.6-input-wacom-12x12-problem-while-using-lens-cursor.patch
Patch23601: linux-2.6-dlm-fix-plock-notify-callback-to-lockd.patch
Patch23602: linux-2.6-ptrace-correctly-handle-ptrace_update-return-value.patch
Patch23603: linux-2.6-x86-limit-max_cstate-to-use-tsc-on-some-platforms.patch
Patch23604: linux-2.6-ppc64-eeh-disable-enable-lsi-interrupts.patch
Patch23605: linux-2.6-gfs2-parsing-of-remount-arguments-incorrect.patch
Patch23606: linux-2.6-mm-fork-vs-gup-race-fix.patch
Patch23607: linux-2.6-mm-cow-vs-gup-race-fix.patch
Patch23608: linux-2.6-net-enic-upstream-update-to-version-1-0-0-933.patch
Patch23609: linux-2.6-net-memory-disclosure-in-so_bsdcompat-gsopt.patch
Patch23610: linux-2.6-net-skfp_ioctl-inverted-logic-flaw.patch
Patch23611: linux-2.6-ppc64-power7-fix-proc-cpuinfo-cpus-info.patch
Patch23612: linux-2.6-xen-pv-block-remove-anaconda-workaround.patch
Patch23613: linux-2.6-gfs2-make-quota-mount-option-consistent-with-gfs.patch
Patch23614: linux-2.6-usb-sb600-sb700-workaround-for-hang.patch
Patch23615: linux-2.6-serial-8250-fix-boot-hang-when-using-with-sol-port.patch
Patch23616: linux-2.6-net-bonding-fix-arp_validate-3-slaves-behaviour.patch
Patch23617: linux-2.6-net-fix-oops-when-using-openswan.patch
Patch23618: linux-2.6-x86-consistent-time-options-for-x86_64-and-i386.patch
Patch23619: linux-2.6-gfs2-add-uuid-to-gfs2-super-block.patch
Patch23620: linux-2.6-revert-xen-console-make-luks-passphrase-readable.patch
Patch23621: linux-2.6-net-e1000-bnx2-enable-entropy-generation.patch
Patch23622: linux-2.6-ppc64-handle-null-iommu-dma-window-property-correctly.patch
Patch23623: linux-2.6-ppc64-cell-fix-npc-setting-for-nosched-contexts.patch
Patch23624: linux-2.6-ppc64-cell-spufs-update-to-the-upstream-for-rhel-5-4.patch
Patch23625: linux-2.6-net-ipv6-fix-getsockopt-for-sticky-options.patch
Patch23626: linux-2.6-acpi-fix-c-states-less-efficient-on-certain-machines.patch
Patch23627: linux-2.6-x86-tsc-keeps-running-in-c3.patch
Patch23628: linux-2.6-ata-libata-iterate-padded-atapi-scatterlist.patch
Patch23629: linux-2.6-sata-libata-ahci-withdraw-ign_serr_internal-for-sb800.patch
Patch23630: linux-2.6-ia64-use-current_kernel_time-xtime-in-hrtimer_start.patch
Patch23631: linux-2.6-net-fix-a-few-udp-counters.patch
Patch23632: linux-2.6-nfs-fix-hung-clients-from-deadlock-in-flush_workqueue.patch
Patch23633: linux-2.6-x86-reserve-low-64k-of-memory-to-avoid-bios-corruption.patch
Patch23634: linux-2.6-net-ehea-remove-adapter-from-list-in-error-path.patch
Patch23635: linux-2.6-dlm-fix-length-calculation-in-compat-code.patch
Patch23636: linux-2.6-misc-sysrq-t-display-backtrace-for-runnable-processes.patch
Patch23637: linux-2.6-mm-decrement-reclaim_in_progress-after-an-oom-kill.patch
Patch23638: linux-2.6-nfs-lockd-set-svc_serv-sv_maxconn-to-a-better-value.patch
Patch23639: linux-2.6-nfs-sunrpc-add-sv_maxconn-field-to-svc_serv.patch
Patch23640: linux-2.6-misc-make-ioctl-h-compatible-with-userland.patch
Patch23641: linux-2.6-acpi-use-vmalloc-in-acpi_system_read_dsdt.patch
Patch23642: linux-2.6-fs-ext3-handle-collisions-in-htree-dirs.patch
Patch23643: linux-2.6-kexec-add-ability-to-dump-log-from-vmcore-file.patch
Patch23644: linux-2.6-misc-signal-modify-locking-to-handle-large-loads.patch
Patch23645: linux-2.6-net-netxen-rebase-for-rhel-5-4.patch
Patch23646: linux-2.6-acpi-disable-gpes-at-the-start-of-resume.patch
Patch23647: linux-2.6-net-ipv6-check-outgoing-interface-in-all-cases.patch
Patch23648: linux-2.6-net-ipv6-check-hop-limit-setting-in-ancillary-data.patch
Patch23649: linux-2.6-x86_64-fix-gettimeoday-tsc-overflow-issue.patch
Patch23650: linux-2.6-net-put_cmsg-may-cause-application-memory-overflow.patch
Patch23651: linux-2.6-wireless-iwlwifi-booting-with-rf-kill-switch-enabled.patch
Patch23652: linux-2.6-x86_64-mce-do-not-clear-an-unrecoverable-error-status.patch
Patch23653: linux-2.6-ide-increase-timeouts-in-wait_drive_not_busy.patch
Patch23654: linux-2.6-s390-dasd-fix-waitqueue-for-sleep_on_immediatly.patch
Patch23655: linux-2.6-s390-iucv-failing-cpu-hot-remove-for-inactive-iucv.patch
Patch23656: linux-2.6-misc-kernel-headers-add-serial_reg-h.patch
Patch23657: linux-2.6-s390-cio-properly-disable-not-operational-subchannel.patch
Patch23658: linux-2.6-ide-fix-interrupt-flood-at-startup-w-esb2.patch
Patch23659: linux-2.6-net-ipv6-disallow-ipproto_ipv6-level-ipv6_checksum.patch
Patch23660: linux-2.6-xen-fix-blkfront-bug-with-overflowing-ring.patch
Patch23661: linux-2.6-s390-dasd-dasdfmt-not-operating-like-cpfmtxa.patch
Patch23662: linux-2.6-s390-sclp-handle-zero-length-event-buffers.patch
Patch23663: linux-2.6-net-rtnetlink-fix-sending-message-when-replace-route.patch
Patch23664: linux-2.6-net-tulip-mtu-problems-with-802-1q-tagged-frames.patch
Patch23665: linux-2.6-nfs-add-fine-grain-control-for-lookup-cache-in-nfs.patch
Patch23666: linux-2.6-nfs-add-lookupcache-mount-option-for-nfs-shares.patch
Patch23667: linux-2.6-md-dm-check-log-bitmap-will-fit-within-the-log-device.patch
Patch23668: linux-2.6-ptrace-audit_syscall_entry-to-use-right-syscall-number.patch
Patch23669: linux-2.6-revert-x86_64-fix-gettimeoday-tsc-overflow-issue.patch
Patch23671: linux-2.6-usb-net-dm9601-upstream-fixes-for-5-4.patch
Patch23672: linux-2.6-x86-move-pci_video_fixup-to-later-in-boot.patch
Patch23673: linux-2.6-mm-clean-up-pagecache-allocation.patch
Patch23674: linux-2.6-mm-revert-kernel_ds-buffered-write-optimisation.patch
Patch23675: linux-2.6-mm-kill-the-zero-length-iovec-segments-handling.patch
Patch23676: linux-2.6-mm-revert-deadlock-on-vectored-write-fix.patch
Patch23677: linux-2.6-mm-clean-up-buffered-write-code.patch
Patch23678: linux-2.6-mm-cleanup-error-handling.patch
Patch23679: linux-2.6-mm-cleanup-page-caching-stuff.patch
Patch23680: linux-2.6-mm-fix-other-users-of-__grab_cache_page.patch
Patch23681: linux-2.6-mm-write-iovec-cleanup.patch
Patch23682: linux-2.6-mm-fix-pagecache-write-deadlocks.patch
Patch23683: linux-2.6-mm-iov_iter-helper-functions.patch
Patch23684: linux-2.6-gfs2-remove-static-iov-iter-stuff.patch
Patch23685: linux-2.6-fs-splice-don-t-steal-pages.patch
Patch23686: linux-2.6-fs-splice-dont-do-readpage.patch
Patch23687: linux-2.6-mm-introduce-new-aops-write_begin-and-write_end.patch
Patch23688: linux-2.6-fs-new-cont-helpers.patch
Patch23689: linux-2.6-gfs2-remove-generic-aops-stuff.patch
Patch23690: linux-2.6-mm-restore-the-kernel_ds-optimisations.patch
Patch23691: linux-2.6-mm-fix-infinite-loop-with-iov_iter_advance.patch
Patch23692: linux-2.6-mm-iov_iter_advance-fix-don-t-go-off-the-end.patch
Patch23693: linux-2.6-fs-fix-symlink-allocation-context.patch
Patch23694: linux-2.6-mm-make-new-aops-kabi-friendly.patch
Patch23695: linux-2.6-fs-ext3-convert-to-new-aops.patch
Patch23696: linux-2.6-fs-fix-__page_symlink-to-be-kabi-friendly.patch
Patch23697: linux-2.6-net-handle-non-linear-packets-in-skb_checksum_setup.patch
Patch23698: linux-2.6-xen-ia64-fix-bad-mpa-messages.patch
Patch23699: linux-2.6-xen-only-recover-connected-devices-on-resume.patch
Patch23700: linux-2.6-xen-wait-5-minutes-for-device-connection.patch
Patch23701: linux-2.6-xen-xen-reports-bogus-lowtotal.patch
Patch23702: linux-2.6-xen-fix-crash-when-modprobe-xen-vnif-in-a-kvm-guest.patch
Patch23703: linux-2.6-xen-fix-occasional-deadlocks-in-xen-netfront.patch
Patch23704: linux-2.6-xen-silence-mmconfig-warnings.patch
Patch23705: linux-2.6-x86-use-ml-fence-to-synchronize-rdtsc.patch
Patch23706: linux-2.6-s390-dasd-fix-race-in-dasd-timer-handling.patch
Patch23707: linux-2.6-misc-cpuset-attach_task-fixes.patch
Patch23708: linux-2.6-nfs-memory-corruption-in-nfs3_xdr_setaclargs-1.patch
Patch23709: linux-2.6-fs-autofs4-track-uid-and-gid-of-last-mount-requester.patch
Patch23710: linux-2.6-fs-autofs4-devicer-node-ioctl-docoumentation.patch
Patch23711: linux-2.6-fs-autofs4-add-miscelaneous-device-for-ioctls.patch
Patch23712: linux-2.6-fs-autofs4-make-autofs-type-usage-explicit.patch
Patch23713: linux-2.6-fs-autofs4-fix-lookup-deadlock.patch
Patch23714: linux-2.6-alsa-hda-update-for-rhel-5-4.patch
Patch23715: linux-2.6-x86-add-nonstop_tsc-flag-in-proc-cpuinfo.patch
Patch23716: linux-2.6-fs-ecryptfs-fix-memory-leak-into-crypto-headers.patch
Patch23717: linux-2.6-gfs2-use-page_mkwrite-for-mmap.patch
Patch23718: linux-2.6-net-netfilter-nfmark-ipv6-routing-in-output.patch
Patch23719: linux-2.6-docs-document-netdev_budget.patch
Patch23720: linux-2.6-fs-hfs-mount-memory-leak.patch
Patch23721: linux-2.6-x86-fix-calls-to-pci_scan_bus.patch
Patch23722: linux-2.6-x86_64-panic-if-amd-cpu_khz-is-wrong.patch
Patch23723: linux-2.6-fs-add-compat_sys_ustat.patch
Patch23724: linux-2.6-scsi-qla2xxx-production-fcoe-support.patch
Patch23725: linux-2.6-scsi-qla2xxx-production-fcoe-firmware.patch
Patch23726: linux-2.6-crypto-bugfixes-to-ansi_cprng-for-fips-compliance.patch
Patch23727: linux-2.6-acpi-donot-evaluate-_ppc-until-_pss-has-been-evaluated.patch
Patch23728: linux-2.6-s390-kernel-nss-support.patch
Patch23729: linux-2.6-s390-qeth-ipv6-support-for-hiper-socket-layer-3.patch
Patch23730: linux-2.6-s390-provide-service-levels-of-hw-hypervisor.patch
Patch23731: linux-2.6-s390-kernel-shutdown-actions-interface.patch
Patch23732: linux-2.6-s390-kernel-processor-degredation-support.patch
Patch23733: linux-2.6-s390-add-call-home-data.patch
Patch23734: linux-2.6-s390-z90crypt-add-ap-adapter-interrupt-support.patch
Patch23735: linux-2.6-s390-kernel-extra-kernel-parameters-via-vmparm.patch
Patch23736: linux-2.6-s390-extra-kernel-parameters-via-vmparm.patch
Patch23737: linux-2.6-s390-add-fcp-performance-data-collection.patch
Patch23738: linux-2.6-s390-blktrace-add-ioctls-to-scsi-generic-devices.patch
Patch23739: linux-2.6-s390-splice-handle-try_to_release_page-failure.patch
Patch23740: linux-2.6-s390-kernel-shutdown-action-dump_reipl.patch
Patch23741: linux-2.6-s390-set-default-preferred-console-device-ttys.patch
Patch23742: linux-2.6-s390-iucv-locking-free-version-of-iucv_message_.patch
Patch23743: linux-2.6-s390-hvc_console-upgrade-version-of-hvc_console.patch
Patch23744: linux-2.6-s390-hvc_iucv-z-vm-iucv-hypervisor-console-support.patch
Patch23745: linux-2.6-i2c-i2c-piix4-support-for-the-broadcom-ht1100-chipset.patch
Patch23746: linux-2.6-i2c-add-support-for-sb800-smbus.patch
Patch23747: linux-2.6-mm-generic_segment_checks-helper.patch
Patch23748: linux-2.6-fs-block_page_mkwrite-helper.patch
Patch23749: linux-2.6-misc-completion-helpers.patch
Patch23750: linux-2.6-fs-d_add_ci-helper.patch
Patch23751: linux-2.6-fs-d_obtain_alias-helper.patch
Patch23752: linux-2.6-fs-xfs-update-to-2-6-28-6-codebase.patch
Patch23753: linux-2.6-fs-xfs-backport-to-rhel5-4-kernel.patch
Patch23754: linux-2.6-fs-xfs-new-aops-interface.patch
Patch23755: linux-2.6-fs-xfs-fix-compat-ioctls.patch
Patch23756: linux-2.6-fs-xfs-misc-upstream-fixes.patch
Patch23757: linux-2.6-fs-writeback-fix-persistent-inode-dirtied_when-val.patch
Patch23758: linux-2.6-ppc-keyboard-not-recognized-on-bare-metal.patch
Patch23759: linux-2.6-x86-nonstop_tsc-in-tsc-clocksource.patch
Patch23760: linux-2.6-pci-add-pci-_selected_region-pci_enable_device_io-mem.patch
Patch23761: linux-2.6-net-e1000e-make-driver-ioport-free.patch
Patch23762: linux-2.6-net-e1000-make-driver-ioport-free.patch
Patch23763: linux-2.6-net-igb-make-driver-ioport-free.patch
Patch23764: linux-2.6-scsi-lpfc-remove-duplicate-pci-functions-from-driver.patch
Patch23765: linux-2.6-net-skip-redirect-msg-if-target-addr-is-not-link-local.patch
Patch23766: linux-2.6-gfs2-tar-off-gfs2-broken-truncated-symbolic-links.patch
Patch23767: linux-2.6-net-iptables-nat-port-randomisation.patch
Patch23768: linux-2.6-gfs2-fix-uninterruptible-quotad-sleeping.patch
Patch23769: linux-2.6-nfs-remove-bogus-lock-if-signalled-case.patch
Patch23770: linux-2.6-net-allow-for-on-demand-emergency-route-cache-flushing.patch
Patch23771: linux-2.6-nfs-nfsd-ensure-nfsv4-calls-the-fs-on-lockt.patch
Patch23772: linux-2.6-dlm-init-file_lock-before-copying-conflicting-lock.patch
Patch23773: linux-2.6-nfs-only-set-file_lock-fl_lmops-if-stateowner-is-found.patch
Patch23774: linux-2.6-net-netfilter-x_tables-add-connlimit-match.patch
Patch23775: linux-2.6-net-ixgbe-stop-double-counting-frames-and-bytes.patch
Patch23776: linux-2.6-s390-af_iucv-hang-if-recvmsg-is-used-with-msg_peek.patch
Patch23777: linux-2.6-s390-af_iucv-new-error-return-codes-for-connect.patch
Patch23778: linux-2.6-s390-af_iucv-avoid-left-over-iucv-connections.patch
Patch23779: linux-2.6-s390-af_iucv-free-iucv-path-socket-in-path_pending-cb.patch
Patch23780: linux-2.6-s390-af_iucv-broken-send_skb_q-result-in-endless-loop.patch
Patch23781: linux-2.6-s390-af_iucv-error-handling-in-iucv_callback_txdone.patch
Patch23782: linux-2.6-s390-kernel-cpcmd-with-vmalloc-addresses.patch
Patch23783: linux-2.6-fs-lockd-reference-count-leaks-in-async-locking-case.patch
Patch23784: linux-2.6-mm-xen-ptwr_emulate-messages-when-booting-pv-guest.patch
Patch23785: linux-2.6-ppc-msi-return-the-number-of-msi-x-available.patch
Patch23786: linux-2.6-ppc-fix-msi-x-interrupt-querying.patch
Patch23787: linux-2.6-ppc-add-support-for-ibm-req-msi-x.patch
Patch23788: linux-2.6-ppc-check-for-msi-x-also-in-rtas_msi_pci_irq_fixup.patch
Patch23789: linux-2.6-ppc-msi-return-the-number-of-msis-we-could-allocate.patch
Patch23790: linux-2.6-ppc-return-req-msi-x-if-request-is-larger.patch
Patch23791: linux-2.6-ppc-implement-a-quota-system-for-msis.patch
Patch23792: linux-2.6-ppc-reject-discontiguous-msi-x-requests.patch
Patch23793: linux-2.6-net-add-dropmonitor-protocol.patch
Patch23794: linux-2.6-ppc-spufs-check-offset-before-calculating-write-size.patch
Patch23795: linux-2.6-ppc-spufs-fix-incorrect-buffer-offset-in-regs-write.patch
Patch23796: linux-2.6-misc-introduce-list_del_init_rcu.patch
Patch23797: linux-2.6-mm-mmu-notifiers-add-mm_take_all_locks-operation.patch
Patch23798: linux-2.6-mm-mmu-notifier-optimized-ability-to-admin-host-pages.patch
Patch23799: linux-2.6-mm-mmu_notifier-set-config_mmu_notifier-to-y.patch
Patch23800: linux-2.6-mm-mmu_notifier-kabi-workaround-support.patch
Patch23801: linux-2.6-pci-xen-dom0-domu-msi-support-using-phsydev_map_irq.patch
Patch23802: linux-2.6-misc-xen-dom0-add-hypercall-for-add-remove-pci-device.patch
Patch23803: linux-2.6-pci-xen-dom0-hook-pci-probe-and-remove-callbacks.patch
Patch23804: linux-2.6-gfs2-merge-upstream-uevent-patches-into-rhel-5-4.patch
Patch23805: linux-2.6-s390-add-additional-card-ids-to-cex2c-and-cex2a.patch
Patch23806: linux-2.6-misc-printk-add-kern_cont.patch
Patch23807: linux-2.6-x86-fdiv-bug-detection-fix.patch
Patch23808: linux-2.6-x86-hypervisor-detection-and-get-tsc_freq.patch
Patch23809: linux-2.6-x86-add-a-synthetic-tsc_reliable-feature-bit.patch
Patch23810: linux-2.6-x86-xen-changes-timebase-calibration-on-vmware.patch
Patch23811: linux-2.6-x86-xen-add-x86_feature_hypervisor-feature-bit.patch
Patch23812: linux-2.6-x86-vmware-fix-vmware_get_tsc-code.patch
Patch23813: linux-2.6-x86-vmware-look-for-dmi-string-in-product-serial-key.patch
Patch23814: linux-2.6-x86-use-cpu_khz-for-loops_per_jiffy-calculation.patch
Patch23815: linux-2.6-x86_64-xen-implement-a-minimal-tsc-based-clocksource.patch
Patch23816: linux-2.6-x86-xen-improve-kvm-timekeeping.patch
Patch23817: linux-2.6-x86-vmware-lazy-timer-emulation.patch
Patch23818: linux-2.6-x86-vmware-disable-softlock-processing-on-tsc-systems.patch
Patch23819: linux-2.6-x86-use-cpu-feature-bits-to-skip-tsc_unstable-checks.patch
Patch23820: linux-2.6-trace-remove-prototype-from-tracepoint-name.patch
Patch23821: linux-2.6-trace-remove-kernel-trace-c.patch
Patch23822: linux-2.6-trace-use-table_size-macro.patch
Patch23823: linux-2.6-trace-make-tracepoints-use-rcu-sched.patch
Patch23824: linux-2.6-trace-tracepoints-fix-reentrancy.patch
Patch23825: linux-2.6-trace-fix-null-pointer-dereference.patch
Patch23826: linux-2.6-trace-simplify-rcu-usage.patch
Patch23827: linux-2.6-trace-introduce-noupdate-apis.patch
Patch23828: linux-2.6-trace-change-rcu_read_sched-rcu_read.patch
Patch23829: linux-2.6-trace-use-unregister-return-value.patch
Patch23830: linux-2.6-fs-add-fiemap-interface.patch
Patch23831: linux-2.6-fs-generic-block-based-fiemap.patch
Patch23832: linux-2.6-misc-make-sure-fiemap-h-is-installed-in-headers-pkg.patch
Patch23833: linux-2.6-mm-fix-prepare_hugepage_range-to-check-offset.patch
Patch23834: linux-2.6-nfs-v4-client-crash-on-file-lookup-with-long-names.patch
Patch23835: linux-2.6-scsi-aic7xxx-increase-max-io-size.patch
Patch23836: linux-2.6-ata-libata-ahci-enclosure-management-bios-workaround.patch
Patch23837: linux-2.6-scsi-qla2xxx-reduce-did_bus_busy-failover-errors.patch
Patch23838: linux-2.6-x86-xen-crash-when-specifying-mem.patch
Patch23839: linux-2.6-net-fixed-tcp_ack-to-properly-clear-icsk_probes_out.patch
Patch23840: linux-2.6-ata-sata_mv-fix-8-port-timeouts-on-508x-6081-chips.patch
Patch23841: linux-2.6-x86-xen-fix-interaction-between-dom0-and-ntp.patch
Patch23842: linux-2.6-net-sctp-allow-sctp_getladdrs-to-work-for-ipv6.patch
Patch23843: linux-2.6-net-fix-out-of-bound-access-to-hook_entries.patch
Patch23844: linux-2.6-wireless-mac80211-avoid-null-deref.patch
Patch23845: linux-2.6-wireless-iwlagn-make-swcrypto-swcrypto50-1-default.patch
Patch23846: linux-2.6-misc-fork-clone_parent-parent_exec_id-interaction.patch
Patch23847: linux-2.6-misc-keys-key-facility-changes-for-af_rxrpc.patch
Patch23848: linux-2.6-misc-types-add-fmode_t-typedef.patch
Patch23849: linux-2.6-fs-cifs-update-cifs-for-rhel5-4.patch
Patch23850: linux-2.6-fs-nfs-convert-to-new-aops.patch
Patch23851: linux-2.6-net-bonding-clean-up-resources-upon-removing-a-bond.patch
Patch23852: linux-2.6-md-dm-fix-oops-in-mempool_free-when-device-removed.patch
Patch23853: linux-2.6-mm-msync-does-not-sync-data-for-a-long-time.patch
Patch23854: linux-2.6-mm-100-time-spent-under-numa-when-zone_reclaim_mode-1.patch
Patch23855: linux-2.6-net-remove-misleading-skb_truesize_check.patch
Patch23856: linux-2.6-gfs2-blocked-after-recovery.patch
Patch23857: linux-2.6-net-add-dscp-netfilter-target.patch
Patch23858: linux-2.6-fs-xfs-add-fiemap-support.patch
Patch23859: linux-2.6-scsi-ipr-enhance-driver-to-support-msi-x-interrupt.patch
Patch23860: linux-2.6-misc-waitpid-reports-stopped-process-more-than-once.patch
Patch23861: linux-2.6-pci-do-not-clear-prefetch-register.patch
Patch23862: linux-2.6-misc-hpilo-backport-bugfixes-and-updates-for-rhel-5-4.patch
Patch23863: linux-2.6-x86_64-copy_user_c-can-zero-more-data-than-needed.patch
Patch23864: linux-2.6-acpi-add-t-state-notification-support.patch
Patch23865: linux-2.6-misc-hrtimer-check-relative-timeouts-for-overflow.patch
Patch23866: linux-2.6-mm-enable-dumping-of-hugepages-into-core-dumps.patch
Patch23867: linux-2.6-misc-add-hp-xw460c-to-bf-sort-pci-list.patch
Patch23868: linux-2.6-x86-general-pci_scan_bus-fix-for-baremetal-and-xen.patch
Patch23869: linux-2.6-misc-backport-new-ramdisk-driver.patch
Patch23870: linux-2.6-misc-add-sys-bus-driver_probe.patch
Patch23871: linux-2.6-pci-fix-__pci_register_driver-error-handling.patch
Patch23872: linux-2.6-pci-use-proper-call-to-driver_create_file.patch
Patch23873: linux-2.6-pci-add-remove_id-sysfs-entry.patch
Patch23874: linux-2.6-pci-pci-stub-module-to-reserve-pci-device.patch
Patch23875: linux-2.6-misc-xen-change-pvfb-not-to-select-abs-pointer.patch
Patch23876: linux-2.6-net-ehea-mutex_unlock-missing-in-ehea-error-path.patch
Patch23877: linux-2.6-scsi-add-missing-sdev_del-state-if-slave_alloc-fails.patch
Patch23878: linux-2.6-ipmi-allow-shared-interrupts.patch
Patch23879: linux-2.6-ipmi-hold-attn-until-upper-layer-is-ready.patch
Patch23880: linux-2.6-ipmi-fix-some-signedness-issues.patch
Patch23881: linux-2.6-ipmi-fix-platform-crash-on-suspend-resume.patch
Patch23882: linux-2.6-misc-exit_notify-kill-the-wrong-capable-check.patch
Patch23883: linux-2.6-ata-sata_mv-fix-chip-type-for-rocketraid-1740-1742.patch
Patch23884: linux-2.6-agp-add-pci-ids-for-new-video-cards.patch
Patch23885: linux-2.6-fs-ext3-don-t-resize-if-no-reserved-gdt-blocks-left.patch
Patch23886: linux-2.6-fs-ext3-dir_index-error-out-on-corrupt-dx-dirs.patch
Patch23887: linux-2.6-fs-jbd-properly-dispose-of-unmapped-data-buffers.patch
Patch23888: linux-2.6-ppc64-adjust-oprofile_cpu_type.patch
Patch23889: linux-2.6-fs-keep-eventpoll-from-locking-up-the-box.patch
Patch23890: linux-2.6-net-ipv6-assume-loopback-address-in-link-local-scope.patch
Patch23891: linux-2.6-wireless-iwlwifi-problems-switching-b-w-wpa-and-wep.patch
Patch23892: linux-2.6-nfs-large-writes-rejected-when-sec-krb5i-p-specified.patch
Patch23893: linux-2.6-ppc-pseries-set-error_state-to-pci_channel_io_normal.patch
Patch23894: linux-2.6-net-e1000e-fix-false-link-detection.patch
Patch23895: linux-2.6-gfs2-add-fiemap-support.patch
Patch23896: linux-2.6-x86-prevent-boosting-kprobes-on-exception-address.patch
Patch23897: linux-2.6-net-r8169-fix-rxmissed-register-access.patch
Patch23898: linux-2.6-net-r8169-don-t-update-stats-counters-when-if-is-down.patch
Patch23899: linux-2.6-net-forcedeth-update-to-upstream-version-0-62.patch
Patch23900: linux-2.6-net-bnx2-update-to-latest-upstream-1-9-3.patch
Patch23901: linux-2.6-s390-enable-raw-devices.patch
Patch23902: linux-2.6-fs-aio-race-in-aio_complete-leads-to-process-hang.patch
Patch23903: linux-2.6-md-dm-mpath-propagate-ioctl-error-codes.patch
Patch23904: linux-2.6-x86-fix-cpuid-4-instrumentation.patch
Patch23905: linux-2.6-fs-autofs4-fix-incorect-return-in-autofs4_mount_busy.patch
Patch23906: linux-2.6-x86-fix-tick-divider-with-clocksource-pit.patch
Patch23907: linux-2.6-gfs2-remove-scand-glockd-kernel-processes.patch
Patch23908: linux-2.6-gfs2-unaligned-access-in-gfs2_bitfit.patch
Patch23909: linux-2.6-x86_64-more-cpu_khz-to-tsc_khz-conversions.patch
Patch23910: linux-2.6-misc-auxiliary-signal-structure-preparation.patch
Patch23911: linux-2.6-misc-auxiliary-signal-structure-signal_struct_aux.patch
Patch23912: linux-2.6-misc-io-accounting-read-accounting-cifs-fix.patch
Patch23913: linux-2.6-misc-io-accounting-core-statistics.patch
Patch23914: linux-2.6-misc-io-accounting-write-accounting.patch
Patch23915: linux-2.6-misc-io-accounting-account-for-direct-io.patch
Patch23916: linux-2.6-misc-io-accounting-report-in-procfs.patch
Patch23917: linux-2.6-misc-io-accounting-write-cancel-accounting.patch
Patch23918: linux-2.6-misc-io-accounting-read-accounting.patch
Patch23919: linux-2.6-misc-io-accounting-read-accounting-nfs-fix.patch
Patch23920: linux-2.6-misc-io-accounting-tgid-accounting.patch
Patch23921: linux-2.6-x86-powernow-k8-export-module-parameters-via-sysfs.patch
Patch23922: linux-2.6-nfs-memory-leak-when-reading-files-wth-option-noac.patch
Patch23923: linux-2.6-scsi-qla2xxx-updates-and-fixes-from-upstream-part-1.patch
Patch23924: linux-2.6-scsi-qla2xxx-updates-and-fixes-from-upstream-part-2.patch
Patch23925: linux-2.6-scsi-qla2xxx-updates-and-fixes-from-upstream-part-3.patch
Patch23926: linux-2.6-scsi-sym53c8xx_2-fix-up-hotplug-support.patch
Patch23927: linux-2.6-x86-add-map_stack-mmap-flag.patch
Patch23928: linux-2.6-scsi-mpt-fusion-update-to-version-3-04-07rh.patch
Patch23929: linux-2.6-scsi-make-fusion-mpt-driver-legacy-i-o-port-free.patch
Patch23930: linux-2.6-scsi-mpt-fusion-remove-annoying-debug-message.patch
Patch23931: linux-2.6-scsi-qla2xxx-updates-and-fixes-from-upstream-part-4.patch
Patch23932: linux-2.6-fs-export-set_task_ioprio.patch
Patch23933: linux-2.6-fs-update-write_cache_pages.patch
Patch23934: linux-2.6-fs-rebase-ext4-and-jbd2-to-2-6-29-codebase.patch
Patch23935: linux-2.6-fs-backport-patch-for-2-6-29-ext4.patch
Patch23936: linux-2.6-fs-ext4-post-2-6-29-fixes.patch
Patch23937: linux-2.6-nfs-setacl-not-working-over-nfs.patch
Patch23938: linux-2.6-mm-tweak-vm-diry_ratio-to-prevent-stalls-on-some-dbs.patch
Patch23939: linux-2.6-misc-i-o-at-update-include-files.patch
Patch23940: linux-2.6-misc-i-o-at-update-existing-files.patch
Patch23941: linux-2.6-misc-i-o-at-update-network-changes.patch
Patch23942: linux-2.6-misc-i-o-at-add-drivers-dca.patch
Patch23943: linux-2.6-misc-i-o-at-new-include-files.patch
Patch23944: linux-2.6-misc-i-o-at-new-dmaengine_v3-c.patch
Patch23945: linux-2.6-misc-i-o-at-new-ioat-c.patch
Patch23946: linux-2.6-ia64-altix-performance-degradation-in-pci-mode.patch
Patch23947: linux-2.6-alsa-handle-subdevice_mask-in-snd_pci_quirk_lookup.patch
Patch23948: linux-2.6-x86-apic-rollover-in-calibrate_apic_clock.patch
Patch23949: linux-2.6-net-tg3-update-to-version-3-96.patch
Patch23950: linux-2.6-net-e1000-enable-tso6-via-ethtool-with-correct-hw.patch
Patch23951: linux-2.6-agp-zero-pages-before-sending-to-userspace.patch
Patch23952: linux-2.6-mm-vmalloc-don-t-pass-__gfp_zero-to-slab.patch
Patch23953: linux-2.6-net-igb-update-to-upstream-version-1-3-16-k2.patch
Patch23954: linux-2.6-net-ixgbe-update-to-upstream-version-2-0-8-k2.patch
Patch23955: linux-2.6-net-ipv4-remove-uneeded-bh_lock-unlock-from-udp_rcv.patch
Patch23956: linux-2.6-scsi-lpfc-update-to-version-8-2-0-38.patch
Patch23957: linux-2.6-scsi-lpfc-update-to-version-8-2-0-39.patch
Patch23958: linux-2.6-scsi-lpfc-update-to-version-8-2-0-40.patch
Patch23959: linux-2.6-scsi-lpfc-update-to-version-8-2-0-41.patch
Patch23960: linux-2.6-net-provide-a-generic-sioethtool-ethtool_gpermaddr.patch
Patch23961: linux-2.6-acpi-cpu-p-state-limits-ignored-by-os.patch
Patch23962: linux-2.6-scsi-marvell-sas-initial-patch-submission.patch
Patch23963: linux-2.6-scsi-marvell-sas-correct-bit-map-implementation.patch
Patch23964: linux-2.6-scsi-marvell-sas-comment-cleanup.patch
Patch23965: linux-2.6-crypto-fix-rfc4309-deadlocks.patch
Patch23966: linux-2.6-crypto-handle-ccm-dec-test-vectors-expected-to-fail.patch
Patch23967: linux-2.6-crypto-add-self-tests-for-rfc4309.patch
Patch23968: linux-2.6-mm-vmscan-bail-out-of-direct-reclaim-after-max-pages.patch
Patch23969: linux-2.6-fs-cifs-unicode-alignment-and-buffer-sizing-problems.patch
Patch23970: linux-2.6-fs-fix-softlockup-in-posix_locks_deadlock.patch
Patch23971: linux-2.6-video-efifb-driver-update.patch
Patch23972: linux-2.6-scsi-update-libfc-fcoe-for-rhel-5-4.patch
Patch23973: linux-2.6-scsi-update-fnic-fcoe-driver-for-rhel-5-4.patch
Patch23974: linux-2.6-scsi-add-alua-scsi-device-handler.patch
Patch23975: linux-2.6-scsi-stex-support-promise-6gb-sas-raid-controller.patch
Patch23976: linux-2.6-trace-tracepoints-for-network-socket.patch
Patch23977: linux-2.6-trace-tracepoints-for-page-cache.patch
Patch23978: linux-2.6-scsi-add-md3000-and-md3000i-entries-to-rdac_dev_list.patch
Patch23979: linux-2.6-net-bonding-update-to-upstream-version-3-4-0.patch
Patch23980: linux-2.6-net-bonding-support-for-bonding-of-ipoib-interfaces.patch
Patch23981: linux-2.6-scsi-st-option-to-use-sili-in-variable-block-reads.patch
Patch23982: linux-2.6-crypto-fips-panic-box-when-module-validation-fails.patch
Patch23983: linux-2.6-scsi-update-iscsi-layer-and-drivers-for-rhel-5-4.patch
Patch23984: linux-2.6-trace-add-success-to-sched_wakeup-sched_wakeup_new.patch
Patch23985: linux-2.6-mm-allow-tuning-of-max_writeback_pages.patch
Patch23986: linux-2.6-ppc64-set-error_state-to-pci_channel_io_normal.patch
Patch23987: linux-2.6-gfs2-nfsv2-support.patch
Patch23988: linux-2.6-misc-drivers-fix-dma_get_required_mask.patch
Patch23989: linux-2.6-net-ipv6-fix-incoming-packet-length-check.patch
Patch23990: linux-2.6-net-bonding-ignore-updelay-param-when-no-active-slave.patch
Patch23991: linux-2.6-mm-add-tracepoints.patch
Patch23992: linux-2.6-openib-mlx4-update-mlx4_ib-and-mlx4_core-add-mlx4_en.patch
Patch23993: linux-2.6-openib-rmda-update-rdma-headers-to-ofed-1-4-1-rc3.patch
Patch23994: linux-2.6-openib-core-update-core-code-to-ofed-1-4-1-rc3.patch
Patch23995: linux-2.6-openib-core-disable-lock-dep-annotation.patch
Patch23996: linux-2.6-openib-ehca-update-driver-for-rhel-5-4.patch
Patch23997: linux-2.6-openib-ipath-update-driver-to-ofed-1-4-1-rc3.patch
Patch23998: linux-2.6-openib-mthca-update-driver-to-ofed-1-4-1-rc3.patch
Patch23999: linux-2.6-openib-iw_nes-update-nes-iwarp-to-ofed-1-4-1-rc3.patch
Patch24000: linux-2.6-openib-cxgb3-update-driver-to-ofed-1-4-1-rc3.patch
Patch24001: linux-2.6-openib-qlgc_vnic-update-to-ofed-1-4-1-rc3.patch
Patch24002: linux-2.6-openib-sdp-update-to-ofed-1-4-1-rc3.patch
Patch24003: linux-2.6-openib-srp-update-to-ofed-1-4-1-rc3.patch
Patch24004: linux-2.6-openib-ipoib-update-to-ofed-1-4-1-rc3.patch
Patch24005: linux-2.6-openib-rds-add-the-rds-protocol.patch
Patch24006: linux-2.6-openib-add-support-for-xrc-queues.patch
Patch24007: linux-2.6-openib-update-all-the-backports-for-the-code-refresh.patch
Patch24008: linux-2.6-scsi-cciss-changes-in-config-functions.patch
Patch24009: linux-2.6-scsi-cciss-thread-to-detect-config-changes-on-msa2012.patch
Patch24010: linux-2.6-scsi-cciss-version-change-for-rhel-5-4.patch
Patch24011: linux-2.6-scsi-cciss-change-in-discovering-memory-bar.patch
Patch24012: linux-2.6-md-snapshot-store-damage.patch
Patch24013: linux-2.6-md-dm-raid1-mpath-partially-completed-request-crash.patch
Patch24014: linux-2.6-md-dm-raid1-switch-read_record-from-kmalloc-to-slab.patch
Patch24015: linux-2.6-md-race-conditions-in-snapshots.patch
Patch24016: linux-2.6-md-dm-snapshot-refactor-__find_pending_exception.patch
Patch24017: linux-2.6-misc-make-bus_find_device-more-robust-match-upstream.patch
Patch24018: linux-2.6-scsi-qla4xxx-fix-driver-fault-recovery.patch
Patch24019: linux-2.6-openib-ehca-fix-performance-during-creation-of-qps.patch
Patch24020: linux-2.6-revert-scsi-mpt-fusion-remove-annoying-debug-message.patch
Patch24021: linux-2.6-revert-scsi-make-fusion-mpt-driver-legacy-i-o-port-free.patch
Patch24022: linux-2.6-revert-scsi-mpt-fusion-update-to-version-3-04-07rh.patch
Patch24023: linux-2.6-fs-fuse-update-for-rhel-5-4.patch
Patch24024: linux-2.6-misc-fix-blktrace-api-breakage.patch
Patch24025: linux-2.6-block-fix-request-flags.patch
Patch24026: linux-2.6-block-disable-iostat-collection-in-gendisk.patch
Patch24027: linux-2.6-misc-kprobes-fix-deadlock-issue.patch
Patch24028: linux-2.6-scsi-add-mpt2sas-driver.patch
Patch24029: linux-2.6-fs-generic-freeze-ioctl-interface.patch
Patch24030: linux-2.6-md-dm-raid45-corrupt-data-and-premature-end-of-synch.patch
Patch24031: linux-2.6-md-fix-lockup-on-read-error.patch
Patch24032: linux-2.6-md-bitmap-merge-feature.patch
Patch24033: linux-2.6-crypto-add-rng-self-test-infra.patch
Patch24034: linux-2.6-crypto-add-ansi_cprng-test-vectors.patch
Patch24035: linux-2.6-misc-add-some-long-missing-capabilities-to-cap_fs_mask.patch
Patch24036: linux-2.6-scsi-fnic-init-retry-counter.patch
Patch24037: linux-2.6-ia64-xen-switch-from-flipping-to-copying-interface.patch
Patch24038: linux-2.6-nfs-selinux-can-copy-off-the-top-of-the-stack.patch
Patch24039: linux-2.6-ppc64-adjust-oprofile_cpu_type-detail.patch
Patch24040: linux-2.6-fs-ext4-re-fix-warning-on-x86-build.patch
Patch24041: linux-2.6-fs-ecryptfs-remove-ecryptfs_unlink_sigs-warnings.patch
Patch24042: linux-2.6-wireless-mac80211-scanning-related-fixes.patch
Patch24043: linux-2.6-scsi-ibmvscsi-lpar-hang-on-a-multipath-device.patch
Patch24044: linux-2.6-usb-support-huawei-s-mode-switch-in-kernel.patch
Patch24045: linux-2.6-gfs2-fix-glock-ref-count-issue.patch
Patch24046: linux-2.6-trace-sunrpc-adding-trace-points-to-status-routines.patch
Patch24047: linux-2.6-net-af_iucv-race-when-queuing-incoming-iucv-messages.patch
Patch24048: linux-2.6-net-tg3-allow-5785-to-work-when-running-at-10mbps.patch
Patch24049: linux-2.6-fs-vfs-freeze-use-vma-v_file-to-get-to-superblock.patch
Patch24050: linux-2.6-pci-rewrite-pci-bar-reading-code.patch
Patch24051: linux-2.6-pci-handle-64-bit-resources-better-on-32-bit-machines.patch
Patch24052: linux-2.6-pci-fix-64-vbit-prefetchable-memory-resource-bars.patch
Patch24053: linux-2.6-pci-export-__pci_read_base.patch
Patch24054: linux-2.6-pci-support-pcie-ari-capability.patch
Patch24055: linux-2.6-pci-fix-ari-code-to-be-compatible-with-mixed-systems.patch
Patch24056: linux-2.6-pci-enhance-pci_ari_enabled.patch
Patch24057: linux-2.6-pci-allow-pci_alloc_child_bus-to-handle-a-null-bridge.patch
Patch24058: linux-2.6-pci-add-a-new-function-to-map-bar-offsets.patch
Patch24059: linux-2.6-pci-initialize-and-release-sr-iov-capability.patch
Patch24060: linux-2.6-pci-restore-saved-sr-iov-state.patch
Patch24061: linux-2.6-pci-reserve-bus-range-for-sr-iov-device.patch
Patch24062: linux-2.6-pci-centralize-device-setup-code.patch
Patch24063: linux-2.6-pci-add-sr-iov-api-for-physical-function-driver.patch
Patch24064: linux-2.6-pci-restore-pci-e-capability-registers-after-pm-event.patch
Patch24065: linux-2.6-pci-save-and-restore-pcie-2-0-registers.patch
Patch24066: linux-2.6-trace-blk-tracepoints.patch
Patch24067: linux-2.6-misc-vt-d-move-common-msi-defines-to-msi-h.patch
Patch24068: linux-2.6-misc-vt-d-add-pci_find_upstream_pcie_bridge.patch
Patch24069: linux-2.6-misc-vt-d-add-dmar-acpi-table-support.patch
Patch24070: linux-2.6-misc-vt-d-add-dmar-related-timeout-definition.patch
Patch24071: linux-2.6-misc-vt-d-add-clflush_cache_range-function.patch
Patch24072: linux-2.6-misc-vt-d-backport-of-intel-vt-d-support-to-rhel5.patch
Patch24073: linux-2.6-misc-add-amd-iommu-support-to-kvm.patch
Patch24074: linux-2.6-revert-net-forcedeth-power-down-phy-when-if-is-down.patch
Patch24075: linux-2.6-net-r8169-reset-intrstatus-after-chip-reset.patch
Patch24076: linux-2.6-revert-mm-fork-vs-gup-race-fix.patch
Patch24077: linux-2.6-mm-support-for-lockless-get_user_pages.patch
Patch24078: linux-2.6-mm-fork-vs-fast-gup-race-fix.patch
Patch24079: linux-2.6-crypto-print-self-test-success-notices-in-fips-mode.patch
Patch24080: linux-2.6-crypto-add-ctr-test-vectors.patch
Patch24081: linux-2.6-net-tun-add-packet-accounting.patch
Patch24082: linux-2.6-x86_64-clean-up-time-c.patch
Patch24083: linux-2.6-i386-untangle-xtime_lock-vs-update_process_times.patch
Patch24084: linux-2.6-x86-scale-cyc_2_nsec-according-to-cpu-frequency.patch
Patch24085: linux-2.6-sched-rq-clock.patch
Patch24086: linux-2.6-sched-accurate-task-runtime-accounting.patch
Patch24087: linux-2.6-crypto-add-hmac-and-hmac-sha512-test-vectors.patch
Patch24088: linux-2.6-md-s390-i-o-stall-when-performing-random-chpid-off-on.patch
Patch24089: linux-2.6-ia64-fix-regression-in-nanosleep-syscall.patch
Patch24090: linux-2.6-scsi-mpt-fusion-update-version-3-04-07rh-v2.patch
Patch24091: linux-2.6-scsi-mpt-fusion-make-driver-legacy-i-o-port-free-v2.patch
Patch24092: linux-2.6-scsi-mpt-fusion-remove-annoying-debug-message-v2.patch
Patch24093: linux-2.6-cpufreq-xen-powernow-identifies-wrong-number-of-procs.patch
Patch24094: linux-2.6-scsi-lpfc-update-from-version-8-2-0-41-to-8-2-0-43.patch
Patch24095: linux-2.6-fs-cifs-buffer-overruns-when-converting-strings.patch
Patch24096: linux-2.6-x86_64-32-bit-ptrace-emulation-mishandles-6th-arg.patch
Patch24097: linux-2.6-crypto-mark-algs-allowed-in-fips-mode.patch
Patch24098: linux-2.6-crypto-block-use-of-non-fips-algs-in-fips-mode.patch
Patch24099: linux-2.6-crypto-make-tcrypt-stay-loaded-on-success.patch
Patch24100: linux-2.6-misc-lockdep-fix-large-lock-subgraph-traversal.patch
Patch24101: linux-2.6-net-igb-correctly-free-multiqueue-netdevs.patch
Patch24102: linux-2.6-md-dm-raid45-target-doesn-t-create-parity-as-expected.patch
Patch24103: linux-2.6-md-dm-raid45-target-oops-on-mapping-table-reload.patch
Patch24104: linux-2.6-revert-scsi-marvell-sas-comment-cleanup.patch
Patch24105: linux-2.6-revert-scsi-marvell-sas-correct-bit-map-implementation.patch
Patch24106: linux-2.6-revert-scsi-marvell-sas-initial-patch-submission.patch
Patch24107: linux-2.6-revert-mm-fork-vs-fast-gup-race-fix.patch
Patch24108: linux-2.6-s390-appldata-vtimer-bug-with-cpu-hotplug.patch
Patch24109: linux-2.6-net-ehea-fix-circular-locking-problem.patch
Patch24110: linux-2.6-net-igbvf-new-driver-support-82576-virtual-functions.patch
Patch24111: linux-2.6-scsi-force-retry-of-io-when-port-session-is-changing.patch
Patch24112: linux-2.6-scsi-port-upstream-offload-code-to-rhel-5-4.patch
Patch24113: linux-2.6-scsi-add-cxgb3i-iscsi-driver.patch
Patch24114: linux-2.6-net-cxgb3-update-driver-for-rhel-5-4.patch
Patch24115: linux-2.6-md-dm-raid45-don-t-clear-the-suspend-flag-on-recovery.patch
Patch24116: linux-2.6-scsi-aacraid-update-to-1-1-5-2461.patch
Patch24117: linux-2.6-fs-cifs-fix-error-handling-in-parse_dfs_referrals.patch
Patch24118: linux-2.6-fs-cifs-renaming-don-t-try-to-unlink-negative-dentry.patch
Patch24119: linux-2.6-fs-nfs-fix-an-f_mode-f_flags-confusion-in-write-c.patch
Patch24120: linux-2.6-scsi-megaraid-update-megasas-to-4-08-rh1.patch
Patch24121: linux-2.6-misc-iommu-msi-header-cleanup.patch
Patch24122: linux-2.6-pci-missed-fix-to-pci_find_upstream_pcie_bridge.patch
Patch24123: linux-2.6-pci-iommu-phys_addr-cleanup.patch
Patch24124: linux-2.6-pci-remove-pci-stub-driver-from-xen-kernels.patch
Patch24125: linux-2.6-nfs-make-nfsv4recoverydir-proc-file-readable.patch
Patch24126: linux-2.6-mm-fork-o_direct-race-v3.patch
Patch24127: linux-2.6-infiniband-ib_core-use-weak-ordering-for-user-memory.patch
Patch24128: linux-2.6-acpi-updated-dock-driver-for-rhel-5-4.patch
Patch24129: linux-2.6-scsi-retry-mode-select-in-rdac-device-handler.patch
Patch24130: linux-2.6-scsi-make-the-path-state-active-by-default.patch
Patch24131: linux-2.6-scsi-handle-unit-attention-in-mode-select.patch
Patch24132: linux-2.6-scsi-retry-io-on-unit-attention.patch
Patch24133: linux-2.6-scsi-handle-quiescence-in-progress.patch
Patch24134: linux-2.6-scsi-add-lsi-storage-ids.patch
Patch24135: linux-2.6-scsi-fix-compilation-error.patch
Patch24136: linux-2.6-md-handle-multiple-paths-in-pg_init.patch
Patch24137: linux-2.6-scsi-retry-for-not_ready-condition.patch
Patch24138: linux-2.6-md-retry-immediate-in-2-seconds.patch
Patch24139: linux-2.6-misc-random-make-get_random_int-more-random.patch
Patch24140: linux-2.6-trace-sunrpc-adding-trace-points-to-status-routines-v2.patch
Patch24141: linux-2.6-audit-watch-fix-removal-of-audit_dir-rule-on-rmdir.patch
Patch24142: linux-2.6-wireless-mac80211-freeze-when-ath5k-if-brought-down.patch
Patch24143: linux-2.6-dlm-connect-to-nodes-earlier.patch
Patch24144: linux-2.6-dlm-use-more-nofs-allocation.patch
Patch24145: linux-2.6-trace-mm-eliminate-extra-mm-tracepoint-overhead.patch
Patch24146: linux-2.6-misc-compile-add-fwrapv-to-gcc-cflags.patch
Patch24147: linux-2.6-ppc-cell-make-ptcal-more-reliable.patch
Patch24148: linux-2.6-lockdep-don-t-omit-lock_set_subclass.patch
Patch24149: linux-2.6-fs-ext4-corruption-fixes.patch
Patch24150: linux-2.6-fs-cifs-fix-pointer-and-checks-in-cifs_follow_symlink.patch
Patch24151: linux-2.6-x86-remove-xtime_lock-from-time_cpufreq_notifier.patch
Patch24152: linux-2.6-alsa-hda-add-missing-comma-in-ad1884_slave_vols.patch
Patch24153: linux-2.6-revert-sched-accurate-task-runtime-accounting.patch
Patch24154: linux-2.6-net-bnx2x-update-to-1-48-105.patch
Patch24155: linux-2.6-scsi-ibmvfc-wait-on-adapter-init-before-starting-scan.patch
Patch24156: linux-2.6-x86-xen-fix-local-denial-of-service.patch
Patch24157: linux-2.6-net-avoid-extra-wakeups-in-wait_for_packet.patch
Patch24158: linux-2.6-scsi-fnic-compile-on-x86-too.patch
Patch24159: linux-2.6-fs-nfsd-fix-setting-the-nfsv4-acls.patch
Patch24160: linux-2.6-ppc-lpar-hang-on-multipath-device-with-fcs-v2.patch
Patch24161: linux-2.6-alsa-hda-improve-init-for-alc262_hp_bpc-model.patch
Patch24162: linux-2.6-selinux-warn-on-nfs-mounts-with-same-sb-but-diff-opts.patch
Patch24163: linux-2.6-md-dm-i-o-failures-when-running-dm-over-md-with-xen.patch
Patch24164: linux-2.6-net-forcedeth-restore-power-up-snippet.patch
Patch24165: linux-2.6-nfs-v4-client-handling-of-may_exec-in-nfs_permission.patch
Patch24166: linux-2.6-net-sky2-fix-eeprom-reads.patch
Patch24167: linux-2.6-net-backport-csum_unfold-without-sparse-annotations.patch
Patch24168: linux-2.6-net-backport-csum_replace4-csum_replace2.patch
Patch24169: linux-2.6-net-gro-optimise-ethernet-header-comparison.patch
Patch24170: linux-2.6-net-netpoll-backport-netpoll_rx_on.patch
Patch24171: linux-2.6-net-skbuff-add-skb_cow_head.patch
Patch24172: linux-2.6-netfilter-nf_conntrack-add-__nf_copy-to-copy-members.patch
Patch24173: linux-2.6-net-skbuff-merge-code-copy_skb_header-and-skb_clone.patch
Patch24174: linux-2.6-net-skbuff-add-skb_release_head_state.patch
Patch24175: linux-2.6-net-add-frag_list-support-to-skb_segment.patch
Patch24176: linux-2.6-net-add-frag_list-support-to-gso.patch
Patch24177: linux-2.6-net-add-generic-receive-offload-infrastructure.patch
Patch24178: linux-2.6-net-ipv4-add-gro-infrastructure.patch
Patch24179: linux-2.6-net-add-skb_gro_receive.patch
Patch24180: linux-2.6-net-tcp-add-gro-support.patch
Patch24181: linux-2.6-net-ethtool-add-ggro-and-sgro-ops.patch
Patch24182: linux-2.6-net-ipv6-add-gro-support.patch
Patch24183: linux-2.6-net-tcp6-add-gro-support.patch
Patch24184: linux-2.6-net-vlan-add-gro-interfaces.patch
Patch24185: linux-2.6-net-cxgb3-add-gro-suppport.patch
Patch24186: linux-2.6-net-igb-add-gro-suppport.patch
Patch24187: linux-2.6-net-ixgbe-add-gro-suppport.patch
Patch24188: linux-2.6-fs-proc-avoid-info-leaks-to-non-privileged-processes.patch
Patch24189: linux-2.6-powerpc-pass-the-pdn-to-check_msix_entries.patch
Patch24190: linux-2.6-net-add-cnic-support-to-bnx2.patch
Patch24191: linux-2.6-misc-add-uio-framework-from-upstream.patch
Patch24192: linux-2.6-scsi-add-netlink-msg-to-iscsi-if-to-support-offload.patch
Patch24193: linux-2.6-scsi-add-bnx2i-iscsi-driver.patch
Patch24194: linux-2.6-net-add-broadcom-cnic-driver.patch
Patch24195: linux-2.6-scsi-mvsas-initial-patch-submission.patch
Patch24196: linux-2.6-scsi-mvsas-correct-bit-map-implementation.patch
Patch24197: linux-2.6-scsi-mvsas-comment-cleanup.patch
Patch24198: linux-2.6-scsi-mvsas-sync-w-appropriate-upstream-changes.patch
Patch24199: linux-2.6-acpi-check-_pss-frequency-to-prevent-cpufreq-crash.patch
Patch24200: linux-2.6-net-sky2-fix-sky2-stats.patch
Patch24201: linux-2.6-dm-raid45-target-kernel-oops-in-constructor.patch
Patch24202: linux-2.6-x86-nmi-add-intel-cpu-0x6f4-to-perfctr1-workaround.patch
Patch24203: linux-2.6-nfs-v4-r-w-perms-for-user-do-not-work-on-client.patch
Patch24204: linux-2.6-net-netxen-add-gro-support.patch
Patch24205: linux-2.6-revert-net-tun-add-packet-accounting.patch
Patch24206: linux-2.6-fs-vfs-skip-i_clear-state-inodes-in-drop_pagecache_sb.patch
Patch24207: linux-2.6-crypto-testmgr-dynamically-allocate-xbuf-and-axbuf.patch
Patch24208: linux-2.6-net-igb-and-igbvf-return-from-napi-poll-correctly.patch
Patch24209: linux-2.6-crypto-testmgr-check-all-test-vector-lengths.patch
Patch24210: linux-2.6-misc-core-dump-wrong-thread-info-in-core-dump-file.patch
Patch24211: linux-2.6-net-ixgbe-fix-polling-saturates-cpu.patch
Patch24212: linux-2.6-s390-dasd-add-emc-ioctl-to-the-driver.patch
Patch24213: linux-2.6-net-ixgbe-fix-msi-x-allocation-on-8-core-systems.patch
Patch24214: linux-2.6-x86_64-kvm-export-symbols-to-allow-building.patch
Patch24215: linux-2.6-net-e1000-fix-skb_over_panic.patch
Patch24216: linux-2.6-revert-net-avoid-extra-wakeups-in-wait_for_packet.patch
Patch24217: linux-2.6-ata-sata_sx4-fixup-interrupt-and-exception-handling.patch
Patch24218: linux-2.6-sched-fix-cond_resched_softirq-offset.patch
Patch24219: linux-2.6-re-apply-net-tun-add-packet-accounting.patch
Patch24220: linux-2.6-net-tun-only-wake-up-writers.patch
Patch24221: linux-2.6-net-skb_copy_datagram_from_iovec.patch
Patch24222: linux-2.6-tun-use-non-linear-packets-where-possible.patch
Patch24223: linux-2.6-net-gso-stop-fraglists-from-escaping.patch
Patch24224: linux-2.6-ppc64-resolves-issues-with-pcie-save-restore-state.patch
Patch24225: linux-2.6-fs-autofs4-remove-hashed-check-in-validate_wait.patch
Patch24226: linux-2.6-xen-netback-change-back-to-a-flipping-interface.patch
Patch24227: linux-2.6-net-skb_seq_read-wrong-offset-len-for-page-frag-data.patch
Patch24228: linux-2.6-scsi-lpfc-update-to-version-8-2-0-44.patch
Patch24229: linux-2.6-scsi-ipr-adapter-taken-offline-after-first-eeh-error.patch
Patch24230: linux-2.6-scsi-ipr-fix-pci-permanent-error-handler.patch
Patch24231: linux-2.6-ptrace-fix-do_coredump-vs-ptrace_start-deadlock.patch
Patch24232: linux-2.6-gfs2-get-gfs2meta-superblock-correctly.patch
Patch24233: linux-2.6-x86_64-kvm-fix-libvirt-based-device-assignment-issue.patch
Patch24234: linux-2.6-net-qla2xxx-ql8xxx-support-for-10-gige.patch
Patch24235: linux-2.6-scsi-qla4xxx-remove-some-dead-code.patch
Patch24236: linux-2.6-scsi-qla4xxx-extended-sense-data-errors.patch
Patch24237: linux-2.6-pci-fix-sr-iov-regression-with-pci-device-class.patch
Patch24238: linux-2.6-xen-x86-give-dom0-access-to-machine-e820-map.patch
Patch24239: linux-2.6-x86_64-amd-iommu-fix-an-off-by-one-error.patch
Patch24240: linux-2.6-x86_64-iommu-fix-the-handling-of-device-aliases.patch
Patch24241: linux-2.6-x86_64-amd-iommu-fix-flag-masks.patch
Patch24242: linux-2.6-x86_64-iommu-protect-against-broken-ivrs-acpi-table.patch
Patch24243: linux-2.6-x86_64-amd-iommu-fix-spinlock-imbalance.patch
Patch24244: linux-2.6-net-ehea-fix-invalid-pointer-access.patch
Patch24245: linux-2.6-crypto-add-continuous-test-to-hw-rng-in-fips-mode.patch
Patch24246: linux-2.6-net-e1000e-update-to-upstream-version-1-0-2-k2.patch
Patch24247: linux-2.6-char-tpm-get_event_name-stack-corruption.patch
Patch24248: linux-2.6-x86_64-amd-iommu-fix-kdump-unknown-partition-table.patch
Patch24249: linux-2.6-scsi-libsas-use-the-supplied-address-for-sata-devices.patch
Patch24250: linux-2.6-x86_64-amd-iommu-fix-glx-issue-in-bare-metal.patch
Patch24251: linux-2.6-md-increase-pg_init_in_progress-only-if-work-is-queued.patch
Patch24252: linux-2.6-net-ixgbe-backport-fixups-and-bugfixes-for-82599.patch
Patch24253: linux-2.6-net-be2net-add-intial-support.patch
Patch24254: linux-2.6-infiniband-remove-duplicate-definition.patch
Patch24255: linux-2.6-infiniband-mlx4_ib-update-to-ofed-1-4-1-final-bits.patch
Patch24256: linux-2.6-infiniband-iw_cxgb3-update-to-ofed-1-4-1-final-bits.patch
Patch24257: linux-2.6-infiniband-ofed-removes-this-backport-and-all-callers.patch
Patch24258: linux-2.6-infiniband-ofed-fix-broken-switch-statement.patch
Patch24259: linux-2.6-infiniband-iw_nes-update-to-ofed-1-4-1-final-bits.patch
Patch24260: linux-2.6-infiniband-mlx4_en-update-to-ofed-1-4-1-final-bits.patch
Patch24261: linux-2.6-infiniband-ofed-back-out-xrc-patch-not-ready-yet.patch
Patch24262: linux-2.6-infiniband-ipoib-sdp-update-to-ofed-1-4-1-final-bits.patch
Patch24263: linux-2.6-net-cxgb3-support-two-new-phys-and-page-mapping-fix.patch
Patch24264: linux-2.6-infiniband-mthca-update-to-ofed-1-4-1-final-bits.patch
Patch24265: linux-2.6-infiniband-rds-update-to-ofed-1-4-1-final-bits.patch
Patch24266: linux-2.6-infiniband-ofed-backports-from-ofed-1-4-1-final-bits.patch
Patch24267: linux-2.6-infiniband-cxgb3-update-firmware-from-7-1-to-7-4.patch
Patch24268: linux-2.6-infiniband-mlx4_en-hand-remove-xrc-support.patch
Patch24269: linux-2.6-infiniband-iw_cxgb3-add-final-fixups-for-1-4-1.patch
Patch24270: linux-2.6-scsi-ibmvscsi-add-16-byte-cdb-support.patch
Patch24271: linux-2.6-pci-fix-pcie-save-restore-patch.patch
Patch24272: linux-2.6-net-r8169-fix-crash-when-large-packets-are-received.patch
Patch24273: linux-2.6-fs-ext4-fix-prealloc-vs-truncate-corruption.patch
Patch24274: linux-2.6-scsi-lpfc-update-to-version-8-2-0-45.patch
Patch24275: linux-2.6-net-e1000e-stop-unnecessary-polling-when-using-msi-x.patch
Patch24276: linux-2.6-mm-fix-swap-race-condition-in-fork-gup-race-patch.patch
Patch24277: linux-2.6-gfs2-fix-truncate-buffered-direct-i-o-issue.patch
Patch24278: linux-2.6-net-backport-net_rx_action-tracepoint.patch
Patch24279: linux-2.6-misc-hrtimer-fix-a-soft-lockup.patch
Patch24280: linux-2.6-security-drop-mmap_min_addr-to-4096.patch
Patch24281: linux-2.6-scsi-cxgb3i-use-kref-to-track-ddp-support-page-sizes.patch
Patch24282: linux-2.6-gfs2-always-queue-work-after-after-setting-glf_lock.patch
Patch24283: linux-2.6-gfs2-keep-statfs-info-in-sync-on-grows.patch
Patch24284: linux-2.6-mm-prevent-panic-in-copy_hugetlb_page_range.patch
Patch24285: linux-2.6-scsi-lpfc-update-to-version-8-2-0-46.patch
Patch24286: linux-2.6-misc-wacom-reset-state-when-tool-is-not-in-proximity.patch
Patch24287: linux-2.6-ide-enable-vx800-to-use-udma-mode.patch
Patch24288: linux-2.6-misc-kdump-make-mcp55-chips-work.patch
Patch24289: linux-2.6-char-tty-prevent-an-o_ndelay-writer-from-blocking.patch
Patch24290: linux-2.6-scsi-qla4xxx-extended-sense-data-errors-cleanups.patch
Patch24291: linux-2.6-scsi-qla2xxx-updates-25xx-firmware-to-4-04-09.patch
Patch24292: linux-2.6-scsi-qla2xxx-updates-24xx-firmware-to-4-04-09.patch
Patch24293: linux-2.6-scsi-qla2xxx-prevent-i-o-stoppage.patch
Patch24294: linux-2.6-net-sky2-proc-net-dev-statistics-are-broken.patch
Patch24295: linux-2.6-net-iucv-provide-second-per-cpu-cmd-parameter-block.patch
Patch24296: linux-2.6-scsi-ibmvfc-improve-logo-prlo-els-handling.patch
Patch24297: linux-2.6-scsi-ibmvfc-fix-endless-prli-loop-in-discovery.patch
Patch24298: linux-2.6-scsi-ibmvfc-process-async-events-before-cmd-responses.patch
Patch24299: linux-2.6-net-rtnl-assertion-failed-due-to-bonding-notify.patch
Patch24300: linux-2.6-net-be2net-crash-on-ppc-with-lro-and-jumbo-frames.patch
Patch24301: linux-2.6-net-undo-vlan-promiscuity-count-when-unregistered.patch
Patch24302: linux-2.6-pci-quirk-disable-msi-on-via-vt3364-chipsets.patch
Patch24303: linux-2.6-net-rt2x00-use-mac80211-provided-workqueue.patch
Patch24304: linux-2.6-gfs2-fix-panic-in-glock-memory-shrinker.patch
Patch24305: linux-2.6-xen-quiet-printk-on-fv-guest-shutdown.patch
Patch24306: linux-2.6-net-be2net-fix-deadlock-with-bonding.patch
Patch24307: linux-2.6-net-be2net-fix-races-in-napi-and-interrupt-handling.patch
Patch24308: linux-2.6-mm-readv-sometimes-returns-less-than-it-should.patch
Patch24309: linux-2.6-scsi-qla2xxx-rhel-5-4-fixes-and-cleanups.patch
Patch24310: linux-2.6-block-blktrace-fix-recursive-block-remap-tracepoint.patch
Patch24313: linux-2.6-misc-driver-core-add-root_device_register.patch
Patch24314: linux-2.6-xen-virtio-add-pci-device-release-function.patch
Patch24315: linux-2.6-xen-virtio-do-not-statically-allocate-root-device.patch
Patch24316: linux-2.6-pci-intel-iommu-fix-iommu-address-space-allocation.patch
Patch24317: linux-2.6-net-tg3-5785f-and-50160m-support.patch
Patch24318: linux-2.6-net-ipsec-add-missing-braces-to-fix-policy-querying.patch
Patch24319: linux-2.6-mm-fix-re-read-performance-regression.patch
Patch24320: linux-2.6-scsi-lpfc-update-to-version-8-2-0-48.patch
Patch24321: linux-2.6-scsi-lpfc-move-pointer-ref-inside-alloc-check-in.patch
Patch24322: linux-2.6-scsi-lpfc-fix-ctx_idx-increase-and-update-version.patch
Patch24323: linux-2.6-net-qlge-rhel-5-4-cleanups.patch
Patch24324: linux-2.6-x86_64-define-x86_cr4_vmxe.patch
Patch24325: linux-2.6-x86_64-add-efer_svme-define.patch
Patch24326: linux-2.6-x86_64-disable-vmx-and-svm-on-machine_crash_shutdown.patch
Patch24327: linux-2.6-x86_64-add-msr_vm_-defines.patch
Patch24328: linux-2.6-x86_64-import-asm-virtext-h.patch
Patch24329: linux-2.6-x86_64-import-asm-svm-h-and-asm-vmx-h.patch
Patch24330: linux-2.6-net-bnx2i-rhel-5-4-code-cleanups.patch
Patch24331: linux-2.6-scsi-cxgb3i-fix-vlan-support.patch
Patch24332: linux-2.6-mm-prevent-softlockups-in-copy_hugetlb_page_range.patch
Patch24333: linux-2.6-scsi-qla2xxx-prevent-hangs-in-extended-error-handling.patch
Patch24334: linux-2.6-scsi-qla2xxx-npiv-broken-for-ppc-endian-fix.patch
Patch24335: linux-2.6-scsi-cciss-fix-spinlock.patch
Patch24336: linux-2.6-x86-fix-suspend-resume-issue-on-sb800-chipset.patch
Patch24337: linux-2.6-ia64-xen-dom0-get-set_address_size.patch
Patch24338: linux-2.6-net-igb-fix-panic-when-assigning-device-to-guest.patch
Patch24339: linux-2.6-block-protect-the-per-gendisk-partition-array-with-rcu.patch
Patch24340: linux-2.6-gfs2-umount-gfs2-hangs-eating-cpu.patch
Patch24341: linux-2.6-net-be2net-fix-msix-performance-regression.patch
Patch24342: linux-2.6-gfs2-fix-incorrent-statfs_slow-consistency-check.patch
Patch24343: linux-2.6-gfs2-don-t-put-unlikely-reclaim-glocks-on-reclaim-list.patch
Patch24344: linux-2.6-pci-kvm-pci-flr-support-for-device-assignment.patch
Patch24345: linux-2.6-xen-ia64-fix-rmmod-of-pci-devices.patch
Patch24346: linux-2.6-scsi-bnx2i-fix-host-setup-and-libiscsi-abort-locking.patch
Patch24347: linux-2.6-scsi-qla2xxx-provide-reset-capability-for-eeh.patch
Patch24348: linux-2.6-misc-build-with-fno-delete-null-pointer-checks.patch
Patch24349: linux-2.6-misc-personality-handling-fix-per_clear_on_setid.patch
Patch24350: linux-2.6-scsi-stex-minimize-dma-coherent-allocation.patch
Patch24351: linux-2.6-scsi-mptfusion-fix-oops-in-failover-path.patch
Patch24352: linux-2.6-revert-mm-fix-swap-race-in-fork-gup-patch-group.patch
Patch24353: linux-2.6-net-ipv6-add-disable-module-parameter-support.patch
Patch24354: linux-2.6-net-ipv6-fix-bug-when-disabled-module-is-unloaded.patch
Patch24355: linux-2.6-net-ipv6-fix-incorrect-disable_ipv6-behavior.patch
Patch24356: linux-2.6-scsi-cciss-fix-sysfs-broken-symlink-regression.patch
Patch24357: linux-2.6-s390-zcrypt-request-gets-timed-out-under-high-load.patch
Patch24358: linux-2.6-openib-mthca-fix-over-sized-kmalloc-usage.patch
Patch24359: linux-2.6-net-mlx4_en-problem-with-lro-that-segfaults-kvm-host.patch
Patch24360: linux-2.6-net-tun-tap-open-dev-net-tun-and-then-poll-it-fix.patch
Patch24361: linux-2.6-ahci-add-sata-gen3-related-messages.patch
Patch24362: linux-2.6-net-e1000e-igb-make-sure-wol-can-be-configured.patch
Patch24363: linux-2.6-scsi-cciss-add-driver-sysfs-entries.patch
Patch24364: linux-2.6-scsi-cciss-call-bus_unregister-in-cciss_remove_one.patch
Patch24365: linux-2.6-alsa-ibexpeak-related-patches-for-codec-auto-config.patch
Patch24366: linux-2.6-alsa-add-native-support-for-ibexpeak-audio.patch
Patch24367: linux-2.6-gfs2-remove-dcache-entries-for-remote-deleted-inodes.patch
Patch24368: linux-2.6-scsi-lpfc-update-to-8-2-0-48-2p-fix-multiple-panics.patch
Patch24369: linux-2.6-ata-ahci-add-ids-for-ibex-peak-ahci-controllers.patch
Patch24370: linux-2.6-scsi-mptsas-fix-max_id-initialization.patch
Patch24371: linux-2.6-fs-ecryptfs-check-tag-3-packet-encrypted-key-size.patch
Patch24372: linux-2.6-fs-ecryptfs-check-tag-11-packet-data-buffer-size.patch
Patch24373: linux-2.6-fs-__bio_clone-don-t-calculate-hw-phys-segment-counts.patch
Patch24374: linux-2.6-scsi-cxgb3i-fix-skb-allocation.patch
Patch24375: linux-2.6-scsi-megaraid-fix-the-tape-drive-issue.patch
Patch24376: linux-2.6-scsi-alua-send-stpg-if-explicit-and-implicit.patch
Patch24377: linux-2.6-scsi-qla2xxx-unable-to-destroy-npiv-hba-ports.patch
Patch24378: linux-2.6-scsi-bnx2i-fix-conn-disconnection-bugs.patch
Patch24379: linux-2.6-scsi-mptfusion-revert-to-pci_map.patch
Patch24380: linux-2.6-net-tg3-fix-concurrent-migration-of-vm-clients.patch
Patch24381: linux-2.6-dlm-free-socket-in-error-exit-path.patch
Patch24382: linux-2.6-x86_64-intel-iommu-pass-through-support.patch
Patch24383: linux-2.6-net-make-sock_sendpage-use-kernel_sendpage.patch
Patch24384: linux-2.6-net-udp-socket-null-ptr-dereference.patch
Patch24385: linux-2.6-net-igb-set-lan-id-prior-to-configuring-phy.patch
Patch24386: linux-2.6-misc-execve-must-clear-current-clear_child_tid.patch
Patch24387: linux-2.6-misc-information-leak-in-sigaltstack.patch
Patch24388: linux-2.6-x86-pnpacpi-fix-serial-ports-on-ibm-point-of-sale-hw.patch
Patch24389: linux-2.6-fs-cifs-new-opts-to-disable-overriding-of-ownership.patch
Patch24390: linux-2.6-x86-detect-apic-clock-calibration-problems.patch
Patch24391: linux-2.6-x86-export-additional-cpu-flags-in-proc-cpuinfo.patch
Patch24392: linux-2.6-x86-kvm-import-pvclock-c-and-headers.patch
Patch24393: linux-2.6-x86-kvm-import-kvmclock-c.patch
Patch24394: linux-2.6-x86_64-kvm-clocksource-s-implementation.patch
Patch24395: linux-2.6-x86-use-kvm-wallclock.patch
Patch24396: linux-2.6-x86-kvmclock-smp-support.patch
Patch24397: linux-2.6-x86-re-register-clock-area-in-prepare_boot_cpu.patch
Patch24398: linux-2.6-x86-disable-kvmclock-when-shuting-the-machine-down.patch
Patch24399: linux-2.6-x86-disable-kvmclock-by-default.patch
Patch24400: linux-2.6-net-mlx4_core-fails-to-load-on-large-systems.patch
Patch24401: linux-2.6-net-mlx4_en-device-multi-function-patch.patch
Patch24402: linux-2.6-net-mlx4_en-fix-for-vlan-traffic.patch
Patch24403: linux-2.6-scsi-qla2xxx-allow-use-of-msi-when-msi-x-disabled.patch
Patch24404: linux-2.6-net-qlge-fix-hangs-and-read-performance.patch
Patch24405: linux-2.6-net-tg3-refrain-from-touching-mps.patch
Patch24406: linux-2.6-scsi-scsi_transport_fc-fc_user_scan-correction.patch
Patch24407: linux-2.6-selinux-allow-preemption-b-w-transition-perm-checks.patch
Patch24408: linux-2.6-nfs-r-w-i-o-perf-degraded-by-flush_stable-page-flush.patch
Patch24409: linux-2.6-net-bonding-tlb-alb-set-active-slave-when-enslaving.patch
Patch24410: linux-2.6-nfs-nlm_lookup_host-don-t-return-invalidated-nlm_host.patch
Patch24411: linux-2.6-md-prevent-crash-when-accessing-suspend_-sysfs-attr.patch
Patch24412: linux-2.6-x86_64-fix-gettimeoday-tsc-overflow-issue-1.patch
Patch24413: linux-2.6-net-atalk-irda-memory-leak-to-user-in-getname.patch
Patch24414: linux-2.6-net-sky2-revert-some-phy-power-refactoring-changes.patch
Patch24415: linux-2.6-revert-x86_64-fix-gettimeoday-tsc-overflow-issue-1.patch
Patch24416: linux-2.6-revert-net-atalk-irda-memory-leak-to-user-in-getname.patch
Patch24417: linux-2.6-net-bridge-fix-lro-crash-with-tun.patch
Patch24418: linux-2.6-misc-cprng-fix-cont-test-to-be-fips-compliant.patch
Patch24419: linux-2.6-scsi-scsi_dh_rdace-add-more-sun-hardware.patch
Patch24420: linux-2.6-x86-kvmclock-fix-bogus-wallclock-value.patch
Patch24421: linux-2.6-x86_64-kvm-allow-kvmclock-to-be-overwritten.patch
Patch24422: linux-2.6-x86-kvm-mark-kvmclock_init-as-cpuinit.patch
Patch24423: linux-2.6-misc-fix-rng-to-not-use-first-generated-random-block.patch
Patch24424: linux-2.6-x86-kvm-fix-vsyscall-going-backwards.patch
Patch24425: linux-2.6-x86_64-kvm-bound-last_kvm-to-prevent-backwards-time.patch
Patch24426: linux-2.6-net-fix-unbalance-rtnl-locking-in-rt_secret_reschedule.patch
Patch24427: linux-2.6-misc-kthreads-kthread_create-vs-kthread_stop-race.patch
Patch24428: linux-2.6-net-tc-fix-unitialized-kernel-memory-leak.patch
Patch24429: linux-2.6-net-r8169-balance-pci_map-unmap-pair-use-hw-padding.patch
Patch24430: linux-2.6-nfs-knfsd-fix-nfsv4-o_excl-creates.patch
Patch24431: linux-2.6-scsi-st-c-memory-use-after-free-after-mtsetblk-ioctl.patch
Patch24432: linux-2.6-misc-undefined-reference-to-__udivdi3.patch
Patch24433: linux-2.6-net-tcp-do-not-use-tso-gso-when-there-is-urgent-data.patch
Patch24434: linux-2.6-net-tun-allow-group-ownership-of-tun-tap-devices.patch
Patch24435: linux-2.6-net-rtl8139-set-mac-address-on-running-device.patch
Patch24436: linux-2.6-x86-fix-mcp55-apic-routing.patch
Patch24437: linux-2.6-net-bonding-allow-bond-in-mode-balance-alb-to-work.patch
Patch24438: linux-2.6-nfs-fix-stripping-suid-sgid-flags-when-chmod-chgrp-dir.patch
Patch24439: linux-2.6-net-icmp-fix-icmp_errors_use_inbound_ifaddr-sysctl.patch
Patch24440: linux-2.6-gfs2-does-not-update-ctime-mtime-on-the-file.patch
Patch24441: linux-2.6-x86-suspend-resume-work-on-large-logical-cpu-systems.patch
Patch24442: linux-2.6-net-8139too-rtnl-and-flush_scheduled_work-deadlock.patch
Patch24443: linux-2.6-pci-add-pci-express-link-status-register-definitions.patch
Patch24444: linux-2.6-net-vxge-makefile-kconfig-and-config-additions.patch
Patch24445: linux-2.6-net-vxge-new-driver-for-neterion-10gb-ethernet.patch
Patch24446: linux-2.6-net-tcp-do-not-use-tso-gso-when-there-is-urgent-data-2.patch
Patch24447: linux-2.6-audit-correct-the-record-length-of-execve.patch
Patch24448: linux-2.6-block-ll_rw_blk-more-flexable-read_ahead_kb-store.patch
Patch24449: linux-2.6-fs-procfs-fix-fill-all-subdirs-as-dt_unknown.patch
Patch24450: linux-2.6-crypto-s390-permit-weak-keys-unless-req_weak_key-set.patch
Patch24451: linux-2.6-cpufreq-p-state-limit-limit-can-never-be-increased.patch
Patch24452: linux-2.6-net-sunrpc-set-rq_daddr-in-svc_rqst-on-socket-recv.patch
Patch24453: linux-2.6-fs-nlm-track-local-address-and-bind-to-it-for-cbs.patch
Patch24454: linux-2.6-net-sunrpc-client-if-for-binding-to-a-local-address.patch
Patch24455: linux-2.6-misc-cpufreq-don-t-set-policy-for-offline-cpus.patch
Patch24456: linux-2.6-misc-documentation-fix-file-nr-definition-in-fs-txt.patch
Patch24457: linux-2.6-net-igbvf-recognize-failure-to-set-mac-address.patch
Patch24458: linux-2.6-xen-netback-call-netdev_features_changed.patch
Patch24459: linux-2.6-ext3-fix-online-resize-bug.patch
Patch24460: linux-2.6-misc-support-intel-multi-apic-cluster-systems.patch
Patch24461: linux-2.6-ata-ahci-add-device-id-for-82801ji-sata-controller.patch
Patch24462: linux-2.6-net-ipv6-do-not-fwd-pkts-with-the-unspecified-saddr.patch
Patch24463: linux-2.6-char-fix-corrupted-intel_rng-kernel-messages.patch
Patch24464: linux-2.6-fs-sanitize-invalid-partition-table-entries.patch
Patch24465: linux-2.6-nfs-fix-cache-invalidation-problems-in-nfs_readdir.patch
Patch24466: linux-2.6-nfs-fix-regression-in-nfs_open_revalidate.patch
Patch24467: linux-2.6-pci-avoid-disabling-acpi-to-use-non-core-pci-devices.patch
Patch24468: linux-2.6-nfs-statfs-error-handling-fix.patch
Patch24469: linux-2.6-gfs2-gfs2_delete_inode-failing-on-ro-filesystem.patch
Patch24470: linux-2.6-net-fix-drop-monitor-to-not-panic-on-null-dev.patch
Patch24471: linux-2.6-net-ipv4-ip_append_data-handle-null-routing-table.patch
Patch24472: linux-2.6-ia64-fix-ppoll-and-pselect-syscalls.patch
Patch24473: linux-2.6-nfs-nfsd4-idmap-upcalls-should-use-unsigned-uid-gid.patch
Patch24474: linux-2.6-x86-fix-nosmp-option.patch
Patch24475: linux-2.6-s390-af_iucv-sock_seqpacket-support.patch
Patch24476: linux-2.6-acpi-fix-syntax-in-acpi-debug-statement.patch
Patch24477: linux-2.6-net-ipt_recent-sanity-check-hit-count.patch
Patch24478: linux-2.6-x86-xen-add-ida-flag.patch
Patch24479: linux-2.6-scsi-fusion-re-enable-mpt_msi_enable-option.patch
Patch24480: linux-2.6-net-bonding-set-primary-param-via-sysfs.patch
Patch24481: linux-2.6-gfs2-mount-option-o-errors-withdraw-panic.patch
Patch24482: linux-2.6-input-psmouse-reenable-mouse-on-shutdown.patch
Patch24483: linux-2.6-gfs2-smbd-proccess-hangs-with-flock-call.patch
Patch24484: linux-2.6-s390-qeth-improve-no_checksumming-handling-for-layer3.patch
Patch24485: linux-2.6-s390-qeth-handle-vswitch-port-isolation-error-codes.patch
Patch24486: linux-2.6-s390-dasd-dev-attr-to-disable-blocking-on-lost-paths.patch
Patch24487: linux-2.6-net-ixgbe-return-pci_ers_result_disconnect-on-fail.patch
Patch24488: linux-2.6-net-e1000-return-pci_ers_result_disconnect-on-fail.patch
Patch24489: linux-2.6-s390-cio-set-correct-number-of-internal-i-o-retries.patch
Patch24490: linux-2.6-net-r8169-avoid-losing-msi-interrupts.patch
Patch24491: linux-2.6-gfs2-genesis-stuck-writing-to-unlinked-file.patch
Patch24492: linux-2.6-x86-oprofile-utilize-perf-counter-reservation.patch
Patch24493: linux-2.6-x86-oprofile-fix-k8-core2-on-multiple-cpus.patch
Patch24494: linux-2.6-x86-oprofile-support-arch-perfmon.patch
Patch24495: linux-2.6-s390-cio-failing-set-online-offline-processing.patch
Patch24496: linux-2.6-s390-dasd-fail-requests-when-dev-state-is-not-ready.patch
Patch24497: linux-2.6-s390-dasd-add-large-volume-support.patch
Patch24498: linux-2.6-s390-set-preferred-s390-console-based-on-conmode.patch
Patch24499: linux-2.6-s390-iucv-fix-output-register-in-iucv_query_maxconn.patch
Patch24500: linux-2.6-x86-add-smp_call_function_many-single-functions.patch
Patch24501: linux-2.6-s390-cio-boot-through-xautolog-with-conmode-3270.patch
Patch24502: linux-2.6-scsi-scsi_dh_rdac-support-st2500-st2510-and-st2530.patch
Patch24503: linux-2.6-scsi-scsi_dh_rdac-add-support-for-sun-devices.patch
Patch24504: linux-2.6-scsi-scsi_dh_rdac-add-support-for-dell-pv-array.patch
Patch24505: linux-2.6-scsi-scsi_dh_rdac-return-correct-mode-select-cmd-info.patch
Patch24506: linux-2.6-scsi-scsi_dh_rdac-move-init-code-around.patch
Patch24507: linux-2.6-scsi-scsi_dh_rdac-collect-rdac-debug-info-during-init.patch
Patch24508: linux-2.6-scsi-scsi_dh_rdac-changes-for-rdac-debug-logging.patch
Patch24509: linux-2.6-nfs-v4-reclaimer-thread-stuck-in-an-infinite-loop.patch
Patch24510: linux-2.6-fs-ecryptfs-prevent-lower-dentry-from-going-negative.patch
Patch24511: linux-2.6-scsi-export-symbol-scsilun_to_int.patch
Patch24512: linux-2.6-misc-hwmon-update-to-latest-upstream-for-rhel-5-5.patch
Patch24513: linux-2.6-net-netfilter-honour-source-routing-for-lvs-nat.patch
Patch24514: linux-2.6-net-e100-add-support-for-82552.patch
Patch24515: linux-2.6-x86_64-vsmp-fix-bit-wise-operator-and-compile-issue.patch
Patch24516: linux-2.6-net-e1000e-return-pci_ers_result_disconnect-on-fail.patch
Patch24517: linux-2.6-xen-fix-timeout-with-pv-guest-and-physical-cdrom.patch
Patch24518: linux-2.6-xen-blkfront-check-for-out-of-bounds-array-accesses.patch
Patch24519: linux-2.6-net-tcp-add-ipv6-support-to-tcp-syn-cookies.patch
Patch24520: linux-2.6-net-syncookies-support-for-tcp-options-via-timestamps.patch
Patch24521: linux-2.6-pci-pciehp-fix-pcie-hotplug-slot-detection.patch
Patch24522: linux-2.6-x86_64-pci-space-below-4gb-forces-mem-remap-above-1tb.patch
Patch24523: linux-2.6-misc-pipe-fix-fd-leaks.patch
Patch24524: linux-2.6-x86-finish-sysdata-conversion.patch
Patch24525: linux-2.6-fs-file-truncations-when-both-suid-and-write-perms-set.patch
Patch24526: linux-2.6-misc-hotplug-adapt-thermal-throttle-to-cpu_dying.patch
Patch24527: linux-2.6-misc-define-cpu_dying-and-cpu_dying_frozen.patch
Patch24528: linux-2.6-misc-hotplug-use-cpuset-hotplug-callback-to-cpu_dying.patch
Patch24529: linux-2.6-misc-hotplug-add-cpu_dying-notifier.patch
Patch24530: linux-2.6-mm-fix-spinlock-performance-issue-on-large-systems.patch
Patch24531: linux-2.6-audit-dereferencing-krule-as-if-it-were-an-audit_watch.patch
Patch24532: linux-2.6-pci-pci_dev-is_enabled-must-be-set.patch
Patch24533: linux-2.6-net-bnx2-apply-broken_stats-workaround-to-5706-5708.patch
Patch24534: linux-2.6-x86_64-fix-hugepage-memory-tracking.patch
Patch24535: linux-2.6-x86-support-always-running-local-apic.patch
Patch24536: linux-2.6-scsi-cciss-switch-to-using-hlist.patch
Patch24537: linux-2.6-scsi-cciss-version-change-2.patch
Patch24538: linux-2.6-scsi-cciss-ignore-stale-commands-after-reboot.patch
Patch24539: linux-2.6-firewire-fw-ohci-fix-iommu-resource-exhaustion.patch
Patch24540: linux-2.6-block-blkfront-respect-elevator-xyz-cmd-line-option.patch
Patch24541: linux-2.6-nfs-knfsd-query-fs-for-v4-getattr-of-fattr4_maxname.patch
Patch24542: linux-2.6-net-e100-return-pci_ers_result_disconnect-on-failure.patch
Patch24543: linux-2.6-net-igb-return-pci_ers_result_disconnect-on-failure.patch
Patch24544: linux-2.6-net-lvs-fix-sync-protocol-handling-for-timeout-values.patch
Patch24545: linux-2.6-fs-inotify-fix-race.patch
Patch24546: linux-2.6-fs-inotify-remove-debug-code.patch
Patch24547: linux-2.6-net-af_unix-deadlock-on-connecting-to-shutdown-socket.patch
Patch24548: linux-2.6-revert-net-lvs-fix-sync-protocol-handling-for-timeout-values.patch
Patch24549: linux-2.6-net-lvs-adjust-sync-protocol-handling-for-ipvsadm-2.patch
Patch24550: linux-2.6-ata-ahci-add-amd-sb900-controller-device-ids.patch
Patch24551: linux-2.6-security-require-root-for-mmap_min_addr.patch
Patch24552: linux-2.6-net-sunrpc-remove-flush_workqueue-from-xs_connect.patch
Patch24553: linux-2.6-x86-add-ability-to-access-nehalem-uncore-config-space.patch
Patch24554: linux-2.6-scsi-lpfc-update-to-8-2-0-52-fc-fcoe.patch
Patch24555: linux-2.6-scsi-panic-at-ipr_sata_reset-after-device-reset.patch
Patch24556: linux-2.6-scsi-mpt-errata-28-fix-on-lsi53c1030.patch
Patch24557: linux-2.6-serial-power7-support-the-single-port-serial-device.patch
Patch24558: linux-2.6-cifs-libfs-sb-s_maxbytes-casts-to-a-signed-value.patch
Patch24559: linux-2.6-fs-dio-don-t-zero-out-pages-array-inside-struct-dio.patch
Patch24560: linux-2.6-nfs-bring-putpubfh-handling-inline-with-upstream.patch
Patch24561: linux-2.6-s390-ipl-vmhalt-vmpanic-vmpoff-vmreboot-don-t-work.patch
Patch24562: linux-2.6-mm-prevent-hangs-long-pauses-when-zone_reclaim_mode-1.patch
Patch24563: linux-2.6-ipmi-add-hp-message-handling.patch
Patch24564: linux-2.6-scsi-htpiop-rocketraid-driver-update-v1-0-v1-6.patch
Patch24565: linux-2.6-drm-r128-check-for-init-on-all-ioctls-that-require-it.patch
Patch24566: linux-2.6-net-forcedeth-let-phy-power-down-when-if-is-down.patch
Patch24567: linux-2.6-gfs2-improve-statfs-and-quota-usability.patch
Patch24568: linux-2.6-dlm-use-gfp_nofs-on-all-lockspaces.patch
Patch24569: linux-2.6-misc-futex-priority-based-wakeup.patch
Patch24570: linux-2.6-nfs-v4-fix-setting-lock-on-open-file-with-no-state.patch
Patch24571: linux-2.6-scsi-arcmsr-add-missing-parameter.patch
Patch24572: linux-2.6-gfs2-careful-unlinking-inodes.patch
Patch24573: linux-2.6-block-cfq-iosched-development-update.patch
Patch24574: linux-2.6-block-cfq-iosched-add-close-cooperator-code.patch
Patch24575: linux-2.6-block-cfq-iosched-make-seek_mean-converge-more-quick.patch
Patch24576: linux-2.6-block-cfq-iosched-default-seek-when-not-enough-samples.patch
Patch24577: linux-2.6-block-cfq-iosched-fix-aliased-req-cooperation-detect.patch
Patch24578: linux-2.6-block-cfq-iosched-cache-prio_tree-root-in-cfqq-p_root.patch
Patch24579: linux-2.6-block-cfq-calc-seek_mean-per-cfq_queue-not-per-cfq_io_context.patch
Patch24580: linux-2.6-block-cfq-merge-cooperating-cfq_queues.patch
Patch24581: linux-2.6-block-cfq-change-the-meaning-of-the-cfqq_coop-flag.patch
Patch24582: linux-2.6-block-cfq-separate-merged-cfqqs-if-they-stop-cooperating.patch
Patch24583: linux-2.6-block-cfq-iosched-fix-idling-interfering-with-plugging.patch
Patch24584: linux-2.6-block-cfq-iosched-don-t-delay-queue-kick-for-merged-req.patch
Patch24585: linux-2.6-acpi-thinkpad_acpi-disable-ecnvram-brightness-on-some.patch
Patch24586: linux-2.6-mm-don-t-oomkill-when-hugepage-alloc-fails-on-node.patch
Patch24587: linux-2.6-wireless-mac80211-fix-reported-wireless-extensions-version.patch
Patch24588: linux-2.6-misc-saner-fasync-handling-on-file-close.patch
Patch24589: linux-2.6-net-cxgb3-bug-fixes-from-latest-upstream-version.patch
Patch24590: linux-2.6-s390-optimize-storage-key-operations-for-anon-pages.patch
Patch24591: linux-2.6-fs-trim-instantiated-file-blocks-on-write-errors.patch
Patch24592: linux-2.6-x86-amd-fix-cpu-llc_shared_map-information.patch
Patch24593: linux-2.6-x86-fix-up-l3-cache-information-for-amd-magny-cours.patch
Patch24594: linux-2.6-x86-fix-up-threshold_bank4-support-on-amd-magny-cours.patch
Patch24595: linux-2.6-x86-set-cpu_llc_id-on-amd-cpus.patch
Patch24596: linux-2.6-mm-prevent-tmpfs-from-going-readonly-during-oom-kills.patch
Patch24597: linux-2.6-net-netlink-fix-typo-in-initialization.patch
Patch24598: linux-2.6-fs-fix-inode_table-test-in-ext-2-3-_check_descriptors.patch
Patch24599: linux-2.6-net-vlan-silence-multicast-debug-messages.patch
Patch24600: linux-2.6-scsi-qla2xxx-updates-and-fixes-for-rhel-5-5.patch
Patch24601: linux-2.6-cifs-protect-globaloplock_q-with-its-own-spinlock.patch
Patch24602: linux-2.6-cifs-reorganize-get_cifs_acl.patch
Patch24603: linux-2.6-cifs-clean-up-set_cifs_acl-interfaces.patch
Patch24604: linux-2.6-cifs-replace-wrtpending-with-a-real-reference-count.patch
Patch24605: linux-2.6-cifs-remove-cifsinodeinfo-oplockpending-flag.patch
Patch24606: linux-2.6-cifs-take-globalsmbses_lock-as-read-only.patch
Patch24607: linux-2.6-cifs-have-cifsfileinfo-hold-an-extra-inode-reference.patch
Patch24608: linux-2.6-cifs-fix-oplock-request-handling-in-posix-codepath.patch
Patch24609: linux-2.6-cifs-turn-oplock-breaks-into-a-workqueue-job.patch
Patch24610: linux-2.6-kvm-use-upstream-kvm_get_tsc_khz.patch
Patch24611: linux-2.6-pci-aer-base-aer-driver-support.patch
Patch24612: linux-2.6-pci-aer-changes-required-to-compile-in-rhel5.patch
Patch24613: linux-2.6-pci-aer-pcie-support-and-compile-fixes.patch
Patch24614: linux-2.6-pci-aer-backport-acpi-osc-functions.patch
Patch24615: linux-2.6-pci-aer-add-domain-support-to-aer_inject.patch
Patch24616: linux-2.6-pci-aer-fix-null-pointer-in-aer-injection-code.patch
Patch24617: linux-2.6-pci-aer-fix-ppc64-compile-no-msi-support.patch
Patch24618: linux-2.6-apic-fix-server-c1e-spurious-lapic-timer-events.patch
Patch24619: linux-2.6-scsi-qla2xxx-enable-msi-x-correctly-on-qlogic-2xxx-series.patch
Patch24620: linux-2.6-acpi-support-physical-cpu-hotplug-on-x86_64.patch
Patch24621: linux-2.6-cpufreq-add-option-to-avoid-smi-while-calibrating.patch
Patch24622: linux-2.6-acpi-run-events-on-cpu-0.patch
Patch24623: linux-2.6-gfs2-drop-rindex-glock-on-grows.patch
Patch24624: linux-2.6-fs-private-dentry-list-to-avoid-dcache_lock-contention.patch
Patch24626: linux-2.6-pci-fix-sr-iov-function-dependency-link-problem.patch
Patch24627: linux-2.6-x86-mce_amd-fix-up-threshold_bank4-creation.patch
Patch24628: linux-2.6-misc-don-t-call-printk-while-crashing.patch
Patch24629: linux-2.6-x86_64-fix-32-bit-process-register-leak.patch
Patch24630: linux-2.6-s390-do-not-annotate-cmdline-as-__initdata.patch
Patch24631: linux-2.6-acpi-disable-arb_disable-on-platforms-where-not-needed.patch
Patch24632: linux-2.6-x86-amd-fix-hot-plug-cpu-issue-on-32-bit-magny-cours.patch
Patch24633: linux-2.6-x86-fix-l1-cache-by-adding-missing-break.patch
Patch24634: linux-2.6-net-bnx2i-cnic-update-driver-version-for-rhel5-5.patch
Patch24635: linux-2.6-x86_64-amd-iommu-system-management-erratum-63-fix.patch
Patch24636: linux-2.6-acpi-bm_check-and-bm_control-update.patch
Patch24637: linux-2.6-nfsd-don-t-allow-setting-ctime-over-v4.patch
Patch24638: linux-2.6-x86-disable-nmi-watchdog-on-cpu-remove.patch
Patch24639: linux-2.6-x86_64-set-proc-id-and-core-id-before-calling-fixup_dcm.patch
Patch24640: linux-2.6-x86-cpu-upstream-cache-fixes-needed-for-amd-m-c.patch
Patch24641: linux-2.6-x86-support-amd-magny-cours-power-aware-scheduler-fix.patch
Patch24642: linux-2.6-x86-fix-boot-crash-with-8-core-amd-magny-cours-system.patch
Patch24643: linux-2.6-sctp-assign-tsns-earlier-to-avoid-reordering.patch
Patch24644: linux-2.6-kvm-balloon-driver-for-guests.patch
Patch24645: linux-2.6-fs-gfs2-fix-potential-race-in-glock-code.patch
Patch24646: linux-2.6-scsi-ibmvscsi-fcocee-npiv-support.patch
Patch24647: linux-2.6-md-multiple-device-failure-renders-dm-raid1-unfixable.patch
Patch24648: linux-2.6-ppc-fix-compile-warnings-in-eeh-code.patch
Patch24649: linux-2.6-fs-ecryptfs-copy-lower-attrs-before-dentry-instantiate.patch
Patch24650: linux-2.6-mm-conditional-flush-in-flush_all_zero_pkmaps.patch
Patch24651: linux-2.6-acpi-prevent-duplicate-dirs-in-proc-acpi-processor.patch
Patch24652: linux-2.6-net-sched-fix-panic-in-bnx2_poll_work.patch
Patch24653: linux-2.6-net-bnx2x-add-support-for-bcm8727-phy.patch
Patch24654: linux-2.6-fs-skip-inodes-w-o-pages-to-free-in-drop_pagecache_sb.patch
Patch24655: linux-2.6-net-introduce-generic-function-__neigh_notify.patch
Patch24656: linux-2.6-net-use-netlink-notifications-to-track-neighbour-states.patch
Patch24657: linux-2.6-net-bonding-ab_arp-use-std-active-slave-select-code.patch
Patch24658: linux-2.6-net-bonding-introduce-primary_reselect-option.patch
Patch24659: linux-2.6-i2c-include-support-for-hudson-2-smbus-controller.patch
Patch24660: linux-2.6-net-augment-raw_send_hdrinc-to-validate-ihl-in-user-hdr.patch
Patch24661: linux-2.6-net-fix-race-in-data-receive-select.patch
Patch24662: linux-2.6-mm-oom-killer-output-should-display-uid.patch
Patch24663: linux-2.6-powerpc-fix-to-handle-slb-resize-during-migration.patch
Patch24664: linux-2.6-acpi-include-core-wmi-support-and-dell-wmi-driver.patch
Patch24665: linux-2.6-nfs-make-sure-dprintk-macro-works-everywhere.patch
Patch24666: linux-2.6-misc-hibernate-increase-timeout.patch
Patch24667: linux-2.6-net-igb-set-vf-rlpml-must-take-vlan-tag-into-account.patch
Patch24668: linux-2.6-edac-add-amd64_edac-driver.patch
Patch24669: linux-2.6-edac-amd64_edac-add-ddr3-support.patch
Patch24670: linux-2.6-edac-amd64_edac-detect-ddr3-support.patch
Patch24671: linux-2.6-edac-amd64_edac-remove-early-hardware-probe.patch
Patch24672: linux-2.6-misc-hpilo-staging-for-interrupt-handling.patch
Patch24673: linux-2.6-misc-hpilo-add-interrupt-handler.patch
Patch24674: linux-2.6-misc-hpilo-add-polling-mechanism.patch
Patch24675: linux-2.6-net-qlge-fix-crash-with-kvm-guest-device-passthru.patch
Patch24676: linux-2.6-net-igb-fix-kexec-with-igb-controller.patch
Patch24677: linux-2.6-net-qlge-updates-and-fixes-for-rhel-5-5.patch
Patch24678: linux-2.6-x86-kvm-don-t-ask-hv-for-tsc-khz-if-not-using-kvmclock.patch
Patch24679: linux-2.6-ipmi-fix-ipmi_si-modprobe-hang.patch
Patch24680: linux-2.6-scsi-fix-inconsistent-usage-of-max-lun.patch
Patch24681: linux-2.6-s390-zfcp_scsi-dynamic-queue-depth-adjustment-param.patch
Patch24682: linux-2.6-net-igb-add-support-for-82576ns-serdes-adapter.patch
Patch24683: linux-2.6-nfs-nfsd4-do-exact-check-of-attribute-specified.patch
Patch24684: linux-2.6-ia64-kdump-restore-registers-in-the-stack-on-init.patch
Patch24685: linux-2.6-nfs-bring-nfs4acl-into-line-with-mainline-code.patch
Patch24686: linux-2.6-nfs-fix-stale-nfs_fattr-passed-to-nfs_readdir_lookup.patch
Patch24687: linux-2.6-xen-cd-rom-drive-does-not-recognize-new-media.patch
Patch24688: linux-2.6-fs-pipe-c-null-pointer-dereference.patch
Patch24689: linux-2.6-sched-enable-config_detect_hung_task-support.patch
Patch24690: linux-2.6-block-blktrace-correctly-record-block-to-and-from-devs.patch
Patch24691: linux-2.6-cifs-no-cifsgetsrvinodenumber-in-is_path_accessible.patch
Patch24692: linux-2.6-edac-add-upstream-i3200_edac-driver.patch
Patch24693: linux-2.6-edac-i3200_edac-backport-driver-to-rhel-5-5.patch
Patch24694: linux-2.6-cifs-enable-dfs-submounts-to-handle-remote-referrals.patch
Patch24695: linux-2.6-cifs-remote-dfs-root-support.patch
Patch24696: linux-2.6-cifs-fix-build-when-dfs-support-not-enabled.patch
Patch24697: linux-2.6-cifs-fix-some-build-warnings.patch
Patch24698: linux-2.6-cifs-add-loop-check-when-mounting-dfs-tree.patch
Patch24699: linux-2.6-cifs-fix-error-handling-in-mount-time-dfs-referral-code.patch
Patch24700: linux-2.6-cpufreq-x86-change-nr_cpus-arrays-in-powernow-k8.patch
Patch24701: linux-2.6-cpufreq-powernow-k8-get-drv-data-for-correct-cpu.patch
Patch24702: linux-2.6-cpufreq-change-cpu-freq-arrays-to-per_cpu-variables.patch
Patch24703: linux-2.6-cpufreq-avoid-playing-with-cpus_allowed-in-powernow-k8.patch
Patch24704: linux-2.6-scsi-megaraid-fix-sas-permissions-in-sysfs.patch
Patch24705: linux-2.6-cifs-fix-artificial-limit-on-reading-symlinks.patch
Patch24706: linux-2.6-cifs-copy-struct-after-setting-port-not-before.patch
Patch24707: linux-2.6-cifs-add-addr-mount-option-alias-for-ip.patch
Patch24708: linux-2.6-cifs-free-nativefilesystem-before-allocating-new-one.patch
Patch24709: linux-2.6-cifs-fix-read-buffer-overflow.patch
Patch24710: linux-2.6-cifs-fix-potential-null-deref-in-parse_dfs_referrals.patch
Patch24711: linux-2.6-cifs-fix-memory-leak-in-ntlmv2-hash-calculation.patch
Patch24712: linux-2.6-cifs-fix-broken-mounts-when-a-ssh-tunnel-is-used.patch
Patch24713: linux-2.6-cifs-avoid-invalid-kfree-in-cifs_get_tcp_session.patch
Patch24714: linux-2.6-cifs-update-cifs-version-number.patch
Patch24715: linux-2.6-net-call-cond_resched-in-rt_run_flush.patch
Patch24716: linux-2.6-scsi-devinfo-update-for-hitachi-entries-for-rhel5-5.patch
Patch24717: linux-2.6-block-cfq-iosched-get-rid-of-cfqq-hash.patch
Patch24718: linux-2.6-vbd-xen-fix-crash-after-ballooning.patch
Patch24719: linux-2.6-fs-gfs2-fix-glock-ref-count-issues.patch
Patch24720: linux-2.6-s390-kernel-fix-single-stepping-on-svc0.patch
Patch24721: linux-2.6-cifs-duplicate-data-on-appending-to-some-samba-servers.patch
Patch24722: linux-2.6-net-ixgbe-update-to-upstream-version-2-0-44-k2.patch
Patch24723: linux-2.6-net-ixgbe-add-and-enable-config_ixgbe_dca.patch
Patch24724: linux-2.6-scsi-gdth-prevent-negative-offsets-in-ioctl.patch
Patch24725: linux-2.6-net-gro-fix-illegal-merging-of-trailer-trash.patch
Patch24726: linux-2.6-scsi-fusion-update-mpt-driver-to-3-4-13rh.patch
Patch24727: linux-2.6-scsi-disable-state-transition-from-offline-to-running.patch
Patch24728: linux-2.6-fs-ext4-update-to-2-6-32-codebase.patch
Patch24729: linux-2.6-scsi-add-be2iscsi-driver.patch
Patch24730: linux-2.6-scsi-stex-update-driver-for-rhel-5-5.patch
Patch24731: linux-2.6-net-resolve-issues-with-vlan-creation-and-filtering.patch
Patch24732: linux-2.6-fs-ext3-4-free-journal-buffers.patch
Patch24733: linux-2.6-nfs-fix-a-deadlock-with-lazy-umount.patch
Patch24734: linux-2.6-nfs-fix-a-deadlock-with-lazy-umount-2.patch
Patch24735: linux-2.6-nfs-sunrpc-allow-rpc_release-cb-run-on-another-workq.patch
Patch24736: linux-2.6-nfs-nfsiod-ensure-the-asynchronous-rpc-calls-complete.patch
Patch24737: linux-2.6-nfs-add-an-nfsiod-workqueue.patch
Patch24738: linux-2.6-infiniband-init-neigh-dgid-raw-on-bonding-events.patch
Patch24739: linux-2.6-infiniband-null-out-skb-pointers-on-error.patch
Patch24740: linux-2.6-net-mlx4_en-add-a-pci-id-table.patch
Patch24741: linux-2.6-net-cxgb3-correct-hex-decimal-error.patch
Patch24742: linux-2.6-net-cxgb3-fix-port-index-issue.patch
Patch24743: linux-2.6-md-fix-snapshot-crash-on-invalidation.patch
Patch24744: linux-2.6-md-fix-data-corruption-with-different-chunksizes.patch
Patch24745: linux-2.6-mm-call-vfs_check_frozen-after-unlocking-the-spinlock.patch
Patch24746: linux-2.6-x86-fix-stale-data-in-shared_cpu_map-cpumasks.patch
Patch24747: linux-2.6-revert-scsi-fix-inconsistent-usage-of-max_lun.patch
Patch24748: linux-2.6-block-blktrace-only-tear-down-our-own-debug-block.patch
Patch24749: linux-2.6-scsi-mpt2sas-upgrade-to-01-101-06-00.patch
Patch24750: linux-2.6-scsi-mpt2sas-use-selected-regions.patch
Patch24751: linux-2.6-acpi-backport-support-for-acpi-4-0-power-metering.patch
Patch24752: linux-2.6-s390-dasd-fix-diag-access-for-read-only-devices.patch
Patch24753: linux-2.6-hwmon-add-support-for-syleus-chip-to-fschmd-driver.patch
Patch24754: linux-2.6-fs-dlm-fix-connection-close-handling.patch
Patch24755: linux-2.6-net-ipvs-synchronize-closing-of-connections.patch
Patch24756: linux-2.6-scsi-megaraid-upgrade-to-version-4-17-rh1.patch
Patch24757: linux-2.6-scsi-megaraid-make-driver-legacy-i-o-port-free.patch
Patch24758: linux-2.6-net-enic-update-to-upstream-version-1-1-0-100.patch
Patch24759: linux-2.6-fs-jbd-fix-race-in-slab-creation-deletion.patch
Patch24760: linux-2.6-fs-ext2-convert-to-new-aops.patch
Patch24761: linux-2.6-md-raid5-mark-cancelled-readahead-bios-with-eio.patch
Patch24762: linux-2.6-md-fix-deadlock-in-device-mapper-multipath.patch
Patch24763: linux-2.6-md-lock-snapshot-while-reading-status.patch
Patch24764: linux-2.6-md-support-origin-size-chunk-size.patch
Patch24765: linux-2.6-scsi-bfa-brocade-bfa-fibre-channel-fcoe-driver.patch
Patch24766: linux-2.6-scsi-add-pmcraid-driver.patch
Patch24767: linux-2.6-scsi-pmcraid-minor-driver-update-for-rhel5-5.patch
Patch24768: linux-2.6-scsi-lpfc-update-version-from-8-2-0-52-to-8-2-0-55.patch
Patch24769: linux-2.6-scsi-lpfc-update-version-from-8-2-0-55-to-8-2-0-58.patch
Patch24770: linux-2.6-scsi-lpfc-update-version-from-8-2-0-58-to-8-2-0-59.patch
Patch24771: linux-2.6-fuse-prevent-fuse_put_request-on-invalid-pointer.patch
Patch24772: linux-2.6-fs-hfs-fix-a-potential-buffer-overflow.patch
Patch24773: linux-2.6-net-igb-update-igb-driver-to-support-barton-hills.patch
Patch24774: linux-2.6-fbfront-xenfb-don-t-recreate-thread-on-every-restore.patch
Patch24775: linux-2.6-cifs-null-out-pointers-when-chasing-dfs-referrals.patch
Patch24776: linux-2.6-pci-aer-prevent-errors-being-reported-multiple-times.patch
Patch24777: linux-2.6-scsi-st-display-current-settings-of-option-bits.patch
Patch24778: linux-2.6-net-netxen-driver-updates-from-2-6-31.patch
Patch24779: linux-2.6-net-netxen-driver-updates-from-2-6-32.patch
Patch24780: linux-2.6-net-netxen-further-p3-updates-for-rhel5-5.patch
Patch24781: linux-2.6-aio-implement-request-batching.patch
Patch24782: linux-2.6-pci-intel-iommu-iotlb-flushing-mods-atsr-support.patch
Patch24783: linux-2.6-pci-intel-iommu-add-2-6-32-rc4-sw-and-hw-pass-through.patch
Patch24784: linux-2.6-pci-intel-iommu-fix-for-isoch-dmar-w-no-tlb-space.patch
Patch24785: linux-2.6-pci-dmar-check-for-dmar-at-zero-bios-error-earlier.patch
Patch24786: linux-2.6-pci-inte-iommu-alloc_coherent-obey-coherent_dma_mask.patch
Patch24787: linux-2.6-pci-intel-iommu-add-hot-un-plug-support.patch
Patch24788: linux-2.6-pci-dmar-rhsa-entry-decode.patch
Patch24789: linux-2.6-pci-intel-iommu-set-dmar_disabled-when-dmar-at-zero.patch
Patch24790: linux-2.6-pci-intel-iommu-no-pagetable-validate-in-passthru-mode.patch
Patch24791: linux-2.6-misc-sysctl-require-cap_sys_rawio-to-set-mmap_min_addr.patch
Patch24792: linux-2.6-ia64-dma_get_required_mask-altix-workaround.patch
Patch24793: linux-2.6-mm-add-kernel-pagefault-tracepoint-for-x86-x86_64.patch
Patch24794: linux-2.6-usb-add-quirk-for-iso-on-amd-sb800.patch
Patch24795: linux-2.6-gfs2-fix-rename-locking-issue.patch
Patch24796: linux-2.6-gfs2-make-o_append-behave-as-expected.patch
Patch24797: linux-2.6-trace-add-itimer-tracepoints.patch
Patch24798: linux-2.6-trace-add-signal-tracepoints.patch
Patch24799: linux-2.6-trace-add-coredump-tracepoint.patch
Patch24800: linux-2.6-pci-implement-public-pci_ioremap_bar-function.patch
Patch24801: linux-2.6-net-bnx2-fix-frags-index.patch
Patch24802: linux-2.6-fs-xfs-fix-fallocate-error-return-sign.patch
Patch24803: linux-2.6-fs-fix-possible-inode-corruption-on-unlock.patch
Patch24804: linux-2.6-fs-ext4-fix-insufficient-checks-in-ext4_ioc_move_ext.patch
Patch24805: linux-2.6-net-ipv4-fix-an-unexpectedly-freed-skb-in-tcp.patch
Patch24806: linux-2.6-x86-amd-add-node-id-msr-support.patch
Patch24807: linux-2.6-md-raid-deal-with-soft-lockups-during-resync.patch
Patch24808: linux-2.6-net-mlx4-update-to-recent-version-with-sriov-support.patch
Patch24809: linux-2.6-net-e1000-update-to-latest-upstream-for-rhel5-5.patch
Patch24810: linux-2.6-net-e1000e-update-and-fix-wol-issues.patch
Patch24811: linux-2.6-net-benet-update-driver-to-latest-upstream-for-rhel5-5.patch
Patch24812: linux-2.6-net-r8169-update-to-latest-upstream-for-rhel5-5.patch
Patch24813: linux-2.6-fs-add-eventfd-core.patch
Patch24814: linux-2.6-fs-eventfd-wire-up-x86-arches.patch
Patch24815: linux-2.6-fs-aio-kaio-eventfd-support-example.patch
Patch24816: linux-2.6-ia64-wire-up-signal-timer-event-fd-syscalls.patch
Patch24817: linux-2.6-ppc-wire-up-eventfd-syscalls.patch
Patch24818: linux-2.6-fs-eventfd-use-waitqueue-lock.patch
Patch24819: linux-2.6-s390-wire-up-signald-timerfd-and-eventfd-syscalls.patch
Patch24820: linux-2.6-fs-eventfd-clean-compile-when-config_eventfd-n.patch
Patch24821: linux-2.6-fs-eventfd-should-include-linux-syscalls-h.patch
Patch24822: linux-2.6-fs-eventfd-sanitize-anon_inode_getfd.patch
Patch24823: linux-2.6-fs-eventfd-kaio-integration-fix.patch
Patch24824: linux-2.6-fs-eventfd-remove-fput-call-from-possible-irq-context.patch
Patch24825: linux-2.6-mm-srat-and-numa-fixes-for-span-and-or-is-discontig-mem.patch
Patch24826: linux-2.6-pci-add-and-export-pci_clear_master.patch
Patch24827: linux-2.6-net-ethtool-add-more-defines-for-mdio-to-use.patch
Patch24828: linux-2.6-net-mdio-add-mdio-module-from-upstream.patch
Patch24829: linux-2.6-fs-make-nr_open-tunable.patch
Patch24830: linux-2.6-net-bnx2x-update-to-1-52-1.patch
Patch24831: linux-2.6-net-bnx2x-add-firmware-version-5-2-7-0.patch
Patch24832: linux-2.6-net-bnx2x-add-mdio-support.patch
Patch24833: linux-2.6-net-bnx2x-update-to-1-52-1-5.patch
Patch24834: linux-2.6-net-cnic-update-driver-for-rhel5-5.patch
Patch24835: linux-2.6-usb-support-lexar-expresscard.patch
Patch24836: linux-2.6-net-bnx2-update-to-version-2-0-2.patch
Patch24837: linux-2.6-net-wireless-support-updates-from-2-6-32.patch
Patch24838: linux-2.6-net-wireless-updates-of-mac80211-etc-from-2-6-32.patch
Patch24839: linux-2.6-net-ath9k-backport-driver-from-2-6-32.patch
Patch24840: linux-2.6-net-wireless-avoid-deadlock-when-enabling-rfkill.patch
Patch24841: linux-2.6-net-mac80211-avoid-uninit-ptr-deref-in-ieee80211.patch
Patch24842: linux-2.6-net-wireless-kill-some-warning-spam.patch
Patch24843: linux-2.6-net-mac80211-report-correct-signal-for-non-dbm-values.patch
Patch24844: linux-2.6-net-wireless-report-reasonable-bitrate-for-802-11n.patch
Patch24845: linux-2.6-wireless-update-old-static-regulatory-domain-rules.patch
Patch24846: linux-2.6-wireless-use-internal-regulatory-database-infrastructure.patch
Patch24847: linux-2.6-wireless-add-wireless-regulatory-rules-database.patch
Patch24848: linux-2.6-vfs-dio-write-returns-eio-on-try_to_release_page-fail.patch
Patch24849: linux-2.6-scsi-ibmvscsi-upstream-multipath-enhancements-for-5-5.patch
Patch24850: linux-2.6-net-vxge-driver-update-to-2-0-6.patch
Patch24851: linux-2.6-net-sfc-add-the-sfc-solarflare-driver.patch
Patch24852: linux-2.6-net-sfc-additional-fixes-for-rhel5-5.patch
Patch24853: linux-2.6-ia64-export-cpu_core_map-like-i386-and-x86_64.patch
Patch24854: linux-2.6-net-s2io-update-driver-to-current-upstream-version.patch
Patch24855: linux-2.6-scsi-qla2xxx-update-to-8-03-01-04-05-05-k.patch
Patch24856: linux-2.6-scsi-qla2xxx-ct-passthrough-and-link-data-rate-fixes.patch
Patch24857: linux-2.6-infiniband-fix-iser-sg-aligment-handling.patch
Patch24858: linux-2.6-scsi-add-emc-clariion-support-to-scsi_dh-modules.patch
Patch24859: linux-2.6-x86-support-amd-l3-cache-index-disable.patch
Patch24860: linux-2.6-net-ipv4-fix-possible-invalid-memory-access.patch
Patch24861: linux-2.6-misc-timer-add-tracepoints.patch
Patch24862: linux-2.6-md-fix-a-race-in-dm-raid1.patch
Patch24863: linux-2.6-fs-respect-flag-in-do_coredump.patch
Patch24864: linux-2.6-net-bonding-add-debug-module-option.patch
Patch24865: linux-2.6-fs-ext3-replace-lock_super-with-explicit-resize-lock.patch
Patch24866: linux-2.6-x86_64-disable-vsyscall-in-kvm-guests.patch
Patch24867: linux-2.6-misc-intel-agp-drm-add-ironlake-support-to-agp-drm-drivers.patch
Patch24868: linux-2.6-firewire-ohci-handle-receive-packets-with-zero-data.patch
Patch24869: linux-2.6-net-bonding-allow-arp_ip_targets-on-separate-vlan-from-bond-device.patch
Patch24870: linux-2.6-block-iosched-reset-batch-for-ordered-requests.patch
Patch24871: linux-2.6-block-iosched-fix-batching-fairness.patch
Patch24872: linux-2.6-pci-aer-hest-firmware-first-support.patch
Patch24873: linux-2.6-pci-aer-hest-disable-support.patch
Patch24874: linux-2.6-e1000e-support-for-82567v-3-and-mtu-fixes.patch
Patch24875: linux-2.6-pci-enable-acs-p2p-upstream-forwarding.patch
Patch24876: linux-2.6-block-fix-rcu-accesses-in-partition-statistics-code.patch
Patch24877: linux-2.6-net-update-tg3-driver-to-version-3-100.patch
Patch24878: linux-2.6-update-fcoe.patch
Patch24879: linux-2.6-vxge-avoid-netpoll-napi-race.patch
Patch24880: linux-2.6-pci-remove-msi-x-vector-allocation-limitation.patch
Patch24881: linux-2.6-net-wireless-fix-build-when-using-o-objdir.patch
Patch24882: linux-2.6-revert-pci-avoid-disabling-acpi-to-use-non-core-pci.patch
Patch24883: linux-2.6-sound-alsa-hda-driver-update-for-rhel5-5.patch
Patch24884: linux-2.6-misc-do-not-evaluate-warn_on-condition-twice-2.patch
Patch24885: linux-2.6-edac-amd64_edac-fix-access-to-pci-conf-space-type-1-2.patch
Patch24886: linux-2.6-scsi-fix-duplicate-libiscsi-symbol-and-kabi-warnings-2.patch
Patch24887: linux-2.6-oprofile-add-support-for-nehalem-ep-processors.patch
Patch24888: linux-2.6-revert-mm-srat-and-numa-fixes-for-span-and-or-is-disc.patch
Patch24889: linux-2.6-iscsi-fix-install-panic-w-xen-iscsi-boot-device.patch
Patch24890: linux-2.6-net-add-send-receive-tracepoints.patch
Patch24891: linux-2.6-net-virtio_net-fix-tx-wakeup-race-condition.patch
Patch24892: linux-2.6-net-be2net-multiple-bug-fixes.patch
Patch24893: linux-2.6-net-enic-update-to-upstream-version-1-1-0-241a.patch
Patch24894: linux-2.6-net-ixgbe-upstream-update-to-include-82599-kr-support.patch
Patch24895: linux-2.6-net-fixup-problems-with-vlans-and-bonding.patch
Patch24896: linux-2.6-scsi-lpfc-fix-vport-not-logging-out-when-being-deleted.patch
Patch24897: linux-2.6-scsi-lpfc-update-to-8-2-0-60-driver-release.patch
Patch24898: linux-2.6-scsi-lpfc-made-tigershark-set-up-and-use-single-fcp-eq.patch
Patch24899: linux-2.6-scsi-lpfc-blocked-all-scsi-i-o-requests-from-midlayer.patch
Patch24900: linux-2.6-scsi-lpfc-fix-crash-during-unload-and-sli4-abort-cmd.patch
Patch24901: linux-2.6-scsi-lpfc-fix-vport-register-vpi-after-devloss-timeout.patch
Patch24902: linux-2.6-scsi-lpfc-update-to-version-8-2-0-61-driver-release.patch
Patch24903: linux-2.6-scsi-lpfc-fix-adapter-reset-and-off-online-stress-test.patch
Patch24904: linux-2.6-scsi-lpfc-fix-multi-frame-sequence-response-frames.patch
Patch24905: linux-2.6-scsi-lpfc-fix-hbq-buff-adds-to-receive-queue.patch
Patch24906: linux-2.6-scsi-lpfc-fix-hbq-buff-only-for-sli4.patch
Patch24907: linux-2.6-scsi-lpfc-update-to-version-8-2-0-62-driver-release.patch
Patch24908: linux-2.6-scsi-lpfc-fix-fc-header-seq_count-checks.patch
Patch24909: linux-2.6-scsi-lpfc-fix-processing-of-failed-read-fcf-record.patch
Patch24910: linux-2.6-scsi-lpfc-fix-vport-fc_flag-set-outside-of-lock-fail.patch
Patch24911: linux-2.6-scsi-lpfc-fix-dead-fcf-not-triggering-discovery-others.patch
Patch24912: linux-2.6-scsi-lpfc-fix-single-scsi-buffer-not-handled-on-sli4.patch
Patch24913: linux-2.6-scsi-lpfc-update-lpfc-to-version-8-2-0-63-driver-release.patch
Patch24914: linux-2.6-revert-amd64_edac-fix-access-to-pci-conf-space-type-1-2.patch
Patch24915: linux-2.6-net-r8169-improved-frame-length-filtering.patch
Patch24916: linux-2.6-net-e1000-fix-rx-length-check-errors.patch
Patch24917: linux-2.6-net-e1000e-fix-rx-length-check-errors.patch
Patch24918: linux-2.6-r8169-add-missing-hunk-from-frame-length-filtering-fix.patch
Patch24919: linux-2.6-net-e1000e-fix-broken-wol.patch
Patch24920: linux-2.6-ipv6-fix-ipv6_hop_jumbo-remote-system-crash.patch
Patch24921: linux-2.6-qla2xxx-npiv-vport-management-pseudofiles-are-world-writable.patch
Patch24922: linux-2.6-fasync-split-fasync_helper-into-separate-add-remove-functions.patch
Patch24923: linux-2.6-misc-emergency-route-cache-flushing-fixes.patch
Patch24924: linux-2.6-mm-memory-mapped-files-not-updating-timestamps.patch
Patch24925: linux-2.6-x86-relocate-initramfs-so-we-can-increase-vmalloc-space.patch
Patch24926: linux-2.6-scsi-qla2xxx-add-aer-support.patch
Patch24927: linux-2.6-misc-hpilo-fix-build-warning-in-ilo_isr.patch
Patch24928: linux-2.6-scsi-bnx2i-additional-fixes-for-rhel5-5-update.patch
Patch24929: linux-2.6-scsi-stex-don-t-try-to-scan-a-nonexistent-lun.patch
Patch24930: linux-2.6-net-bonding-fix-alb-mode-locking-regression.patch
Patch24931: linux-2.6-net-tg3-update-to-version-3-106-for-57765-asic-support.patch
Patch24932: linux-2.6-alsa-support-creative-x-fi-emu20k1-and-emu20k2-chips.patch
Patch24933: linux-2.6-scsi-scsi_dh-change-scsidh_activate-interface-to-async.patch
Patch24934: linux-2.6-scsi-scsi_dh-make-rdac-hw-handler-s-activate-async.patch
Patch24935: linux-2.6-misc-support-nehalem-ex-processors-in-oprofile.patch
Patch24936: linux-2.6-pci-add-ids-for-intel-b43-graphics-controller.patch
Patch24937: linux-2.6-scsi-be2iscsi-upstream-driver-refresh-for-rhel5-5.patch
Patch24938: linux-2.6-scsi-lpfc-update-driver-to-version-8-2-0-63-1p-fc-fcoe.patch
Patch24939: linux-2.6-scsi-lpfc-update-to-version-8-2-0-63-p2.patch
Patch24940: linux-2.6-scsi-qla2xxx-fix-timeout-value-for-ct-passthru-cmds.patch
Patch24941: linux-2.6-scsi-qla2xxx-fcp2-update-dpc-bug-fast-mailbox-read.patch
Patch24942: linux-2.6-net-igb-update-driver-to-support-end-point-dca.patch
Patch24943: linux-2.6-fs-proc-make-errno-values-consistent-when-race-occurs.patch
Patch24944: linux-2.6-mm-mmap-don-t-enomem-when-mapcount-is-temp-exceeded.patch
Patch24945: linux-2.6-mm-prevent-performance-hit-for-32-bit-apps-on-x86_64.patch
Patch24946: linux-2.6-net-niu-fix-the-driver-to-be-functional-with-vlans.patch
Patch24947: linux-2.6-net-iptables-fix-routing-of-reject-target-packets.patch
Patch24948: linux-2.6-fs-proc-make-smaps-readable-even-after-setuid.patch
Patch24949: linux-2.6-x86_64-export-additional-features-in-cpuinfo-for-xen.patch
Patch24950: linux-2.6-kvm-kvmclock-won-t-restore-properly-after-resume.patch
Patch24951: linux-2.6-acpi-fix-null-pointer-panic-in-acpi_run_os.patch
Patch24952: linux-2.6-pci-vf-can-t-be-enabled-in-dom0.patch
Patch24953: linux-2.6-md-fix-deadlock-at-suspending-mirror-device.patch
Patch24954: linux-2.6-md-fix-kernel-panic-releasing-bio-after-recovery-failed.patch
Patch24955: linux-2.6-kvm-pvclock-on-i386-suffers-from-double-registering.patch
Patch24956: linux-2.6-x86-fix-amd-m-c-boot-inside-xen-on-pre-5-5-hypervisor.patch
Patch24957: linux-2.6-usb-support-more-huawei-modems.patch
Patch24958: linux-2.6-mm-prevent-hangs-during-memory-reclaim-on-large-systems.patch
Patch24959: linux-2.6-misc-audit-fix-breakage-and-leaks-in-audit_tree-c.patch
Patch24960: linux-2.6-misc-edac-driver-fix-for-non-mmconfig-systems.patch
Patch24961: linux-2.6-block-loop-fix-aops-check-for-gfs.patch
Patch24962: linux-2.6-misc-khungtaskd-set-pf_nofreeze-flag-to-fix-suspend.patch
Patch24963: linux-2.6-net-ipv6-fix-oops-in-ip6_dst_lookup_tail.patch
Patch24964: linux-2.6-fs-gfs2-don-t-withdraw-on-partial-rindex-entries.patch
Patch24965: linux-2.6-misc-fix-kernel-info-leak-with-print-fatal-signals-1.patch
Patch24966: linux-2.6-net-netfilter-enforce-cap_net_admin-in-ebtables.patch
Patch24967: linux-2.6-x86_64-wire-up-compat-sched_rr_get_interval.patch
Patch24968: linux-2.6-net-sky2-fix-initial-link-state-errors.patch
Patch24969: linux-2.6-fs-aio-fix-5-oltp-perf-regression-from-eventfd.patch
Patch24970: linux-2.6-mm-fix-sys_move_pages-infoleak.patch
Patch24971: linux-2.6-misc-fix-apic-and-tsc-reads-for-guests.patch
Patch24972: linux-2.6-scsi-megaraid-fix-32-bit-apps-on-64-bit-kernel.patch
Patch24973: linux-2.6-misc-ptrace-ptrace_kill-hangs-in-100-cpu-loop.patch
Patch24974: linux-2.6-cpufreq-powernow-k8-fix-crash-on-amd-family-0x11-procs.patch
Patch24975: linux-2.6-x86-xen-invalidate-dom0-pages-before-starting-guest.patch
Patch24976: linux-2.6-net-niu-fix-deadlock-when-using-bonding.patch
Patch24977: linux-2.6-net-igb-fix-msix_other-interrupt-masking.patch
Patch24978: linux-2.6-fs-nfsv4-distinguish-expired-from-stale-stateid.patch
Patch24979: linux-2.6-net-cxgb3-add-memory-barriers.patch
Patch24980: linux-2.6-net-cnic-additional-fixes-for-rhel5-5-update.patch
Patch24981: linux-2.6-char-ipmi-fix-ipmi_watchdog-deadlock.patch
Patch24982: linux-2.6-infiniband-fix-issue-w-sleep-in-interrupt-ehca-handler.patch
Patch24983: linux-2.6-infiniband-fix-bitmask-handling-from-qp-control-block.patch
Patch24984: linux-2.6-net-be2net-latest-bugfixes-from-upstream-for-rhel5.5.patch
Patch24985: linux-2.6-net-wireless-fixes-from-2-6-32-2.patch
Patch24986: linux-2.6-net-wireless-fixes-through-2-6-32-3.patch
Patch24987: linux-2.6-net-wireless-fixes-from-2-6-32-4.patch
Patch24988: linux-2.6-net-wireless-fixes-from-2-6-32-7.patch
Patch24989: linux-2.6-s390-clear-high-order-bits-after-switch-to-64-bit-mode.patch
Patch24990: linux-2.6-misc-rwsem-fix-a-bug-in-rwsem_is_locked.patch
Patch24991: linux-2.6-net-e1000e-fix-deadlock-unloading-module-on-some-ich8.patch
Patch24992: linux-2.6-s390-qeth-set-default-blkt-settings-by-osa-hw-level.patch
Patch24993: linux-2.6-pci-aer-disable-advanced-error-reporting-by-default.patch
Patch24994: linux-2.6-ppc-fix-sched-while-atomic-error-in-alignment-handler.patch
Patch24995: linux-2.6-mm-i386-fix-iounmap-s-use-of-vm_struct-s-size-field.patch
Patch24996: linux-2.6-net-netfilter-allow-changing-queue-length-via-netlink.patch
Patch24997: linux-2.6-net-forcedeth-fix-putting-system-into-s4.patch
Patch24998: linux-2.6-base-make-platform_device_add_data-accept-const-pointer.patch
Patch24999: linux-2.6-hwmon-f71805f-fix-sio_data-to-platform_device_add_data.patch
Patch25000: linux-2.6-hwmon-it87-fix-sio_data-to-platform_device_add_data.patch
Patch25001: linux-2.6-hwmon-smsc47m1-fix-data-to-platform_device_add_data.patch
Patch25002: linux-2.6-hwmon-w83627hf-fix-data-to-platform_device_add_data.patch
Patch25003: linux-2.6-mm-xen-make-mmap-with-prot_write.patch
Patch25004: linux-2.6-virtio-fix-module-loading-for-virtio-balloon-module.patch
Patch25005: linux-2.6-scsi-qla2xxx-return-failed-if-abort-command-fails.patch
Patch25006: linux-2.6-fs-ecryptfs-fix-metadata-in-xattr-feature-regression.patch
Patch25007: linux-2.6-nfs-bug-548846-deadlock-in-the-sunrpc-code.patch
Patch25008: linux-2.6-lpfc-add-support-for-pci-bar-region-0-if-bar0-is-a-64-bit-register.patch
Patch25009: linux-2.6-lpfc-add-support-for-new-sli-features.patch
Patch25010: linux-2.6-lpfc-fix-a-merge-issue.patch
Patch25011: linux-2.6-lpfc-implement-the-port_capabities-mailbox-command.patch
Patch25012: linux-2.6-lpfc-relax-event-queue-field-checking-to-allow-non-zero-minor-codes.patch
Patch25013: linux-2.6-lpfc-fix-driver-build-issues-with-the-new-rhel5-5-kernel-sources.patch
Patch25014: linux-2.6-lpfc-update-lpfc-version-for-8-2-0-63-3p-driver-release.patch
Patch25015: linux-2.6-fs-gfs2-use-correct-gfp-for-alloc-page-on-write.patch
Patch25016: linux-2.6-net-tg3-fix-race-condition-with-57765-devices.patch
Patch25017: linux-2.6-net-tg3-fix-57765-led.patch
Patch25018: linux-2.6-scsi-fix-bugs-in-fnic-and-libfc.patch
Patch25019: linux-2.6-fs-fix-randasys-crashes-x86_64-systems-regression.patch
Patch25020: linux-2.6-net-ixgbe-prevent-speculatively-processing-descriptors.patch
Patch25021: linux-2.6-misc-hvc_iucv-alloc-send-receive-buffers-in-dma-zone.patch
Patch25022: linux-2.6-net-bnx2x-update-to-1-52-1-6.patch
Patch25023: linux-2.6-net-bnx2x-update-to-1-52-1-6-firmware.patch
Patch25024: linux-2.6-fs-ext4-avoid-divide-by-0-when-mounting-corrupted-fs.patch
Patch25025: linux-2.6-net-ixgbe-initial-support-of-ixgbe-pf-and-vf-drivers.patch
Patch25026: linux-2.6-scsi-be2iscsi-fix-eh-bugs-and-enable-new-hw-support.patch
Patch25027: linux-2.6-misc-wacom-add-intuos4-support.patch
Patch25028: linux-2.6-scsi-device_handler-add-netapp-to-alua-dev-list.patch
Patch25029: linux-2.6-x86_64-mce-avoid-deadlocks-during-mce-broadcasts.patch
Patch25030: linux-2.6-net-cxgb3-memory-barrier-addition-fixup.patch
Patch25031: linux-2.6-mm-prevent-severe-performance-degradation-hang-fix.patch
Patch25032: linux-2.6-dm-raid45-constructor-error-path-oops-fix.patch
Patch25033: linux-2.6-ia64-kdump-fix-a-deadlock-while-redezvousing.patch
Patch25034: linux-2.6-x86_64-k8-do-not-mark-early_is_k8_nb-as-__init.patch
Patch25035: linux-2.6-i386-mce-avoid-deadlocks-during-mce-broadcasts.patch
Patch25036: linux-2.6-scsi-mpt2sas-fix-missing-initialization.patch
Patch25037: linux-2.6-misc-usb-serial-add-support-for-qualcomm-modems.patch
Patch25038: linux-2.6-s390-zcrypt-do-not-remove-coprocessor-on-error-8-72.patch
Patch25039: linux-2.6-x86_64-fix-missing-32-bit-syscalls-on-64-bit.patch
Patch25040: linux-2.6-net-mlx4-pass-eth-attributes-down-to-vlan-interfaces.patch
Patch25041: linux-2.6-net-mlx4-fix-broken-sriov-code.patch
Patch25042: linux-2.6-net-bnx2-update-firmware-and-version-to-2-0-8.patch
Patch25043: linux-2.6-net-e1000e-disable-nfs-filtering-capabilites-in-ich-hw.patch
Patch25044: linux-2.6-net-ixgbe-stop-unmapping-dma-buffers-too-early.patch
Patch25045: linux-2.6-net-s2io-restore-ability-to-tx-rx-vlan-traffic.patch
Patch25046: linux-2.6-net-igb-fix-warning-in-igb_ethtool-c.patch
Patch25047: linux-2.6-net-igb-fix-wol-initialization-when-disabled-in-eeprom.patch
Patch25048: linux-2.6-net-bnx2x-use-single-tx-queue.patch
Patch25049: linux-2.6-net-tg3-fix-5717-and-57765-asic-revs-panic-under-load.patch
Patch25050: linux-2.6-net-be2net-critical-bugfix-from-upstream.patch
Patch25051: linux-2.6-wireless-iwlwifi-fix-dual-band-n-only-use-on-5x00.patch
Patch25052: linux-2.6-net-sctp-backport-cleanups-for-ootb-handling.patch
Patch25053: linux-2.6-fs-gfs2-fix-kernel-bug-when-using-fiemap.patch
Patch25054: linux-2.6-x86_64-xen-fix-missing-32-bit-syscalls-on-64-bit-xen.patch
Patch25055: linux-2.6-fs-cifs-fix-len-for-converted-unicode-readdir-names.patch
Patch25056: linux-2.6-fs-cifs-fix-dentry-hash-for-case-insensitive-mounts.patch
Patch25057: linux-2.6-fs-cifs-cifs-shouldn-t-make-mountpoints-shrinkable.patch
Patch25058: linux-2.6-fs-cifs-max-username-len-check-in-setup-does-not-match.patch
Patch25059: linux-2.6-block-cfq-kick-busy-queues-w-o-waiting-for-merged-req.patch
Patch25060: linux-2.6-revert-ia64-kdump-fix-a-deadlock-while-redezvousing.patch
Patch25061: linux-2.6-net-igb-fix-dca-support-for-82580-nics.patch
Patch25062: linux-2.6-wireless-rt2x00-fix-work-cancel-race-conditions.patch
Patch25063: linux-2.6-misc-backport-upstream-strict_strto-functions.patch
Patch25064: linux-2.6-cpu-fix-amd-l3-cache-disable-functionality.patch
Patch25065: linux-2.6-net-virtio_net-refill-rx-buffer-on-out-of-memory.patch
Patch25066: linux-2.6-net-r8169-fix-assignments-in-backported-net_device_ops.patch
Patch25067: linux-2.6-acpi-power_meter-avoid-oops-on-driver-load.patch
Patch25068: linux-2.6-fs-gfs2-locking-fix-for-potential-dos.patch
Patch25069: linux-2.6-block-cfq-iosched-fix-sequential-read-perf-regression.patch
Patch25070: linux-2.6-net-mlx4-pass-attributes-down-to-vlan-interfaces.patch
Patch25071: linux-2.6-s390-kernel-correct-tlb-flush-of-page-table-entries.patch
Patch25072: linux-2.6-mm-don-t-let-reserved-memory-overlap-bootmem_map.patch
Patch25073: linux-2.6-x86_64-fix-floating-point-state-corruption-after-signal.patch
Patch25074: linux-2.6-edac-fix-internal-error-message-in-amd64_edac-driver.patch
Patch25075: linux-2.6-fusion-mptsas-fix-event_data-alignment.patch
Patch25076: linux-2.6-scsi-fnic-fix-tx-queue-handling.patch
Patch25077: linux-2.6-dvb-fix-endless-loop-when-decoding-ule-at-dvb-core.patch
Patch25078: linux-2.6-sound-hda_intel-avoid-divide-by-zero-in-azx-devices.patch
Patch25079: linux-2.6-netlink-connector-delete-buggy-notification-code.patch
Patch25080: linux-2.6-misc-kernel-fix-elf-load-dos-on-x86_64.patch
Patch25081: linux-2.6-iscsi-fix-slow-failover-times.patch
Patch25082: linux-2.6-net-bnx2-avoid-restarting-cnic-in-some-contexts.patch
Patch25083: linux-2.6-mm-fix-boot-on-s390x-after-bootmem-overlap-patch.patch
Patch25084: linux-2.6-cpu-fix-boot-crash-in-32-bit-install-on-amd-cpus.patch
Patch25085: linux-2.6-net-bnx2-fix-lost-msi-x-problem-on-5709-nics.patch
Patch25086: linux-2.6-fs-fix-kernel-oops-while-copying-from-ext3-to-gfs2.patch
Patch25087: linux-2.6-nfs-fix-an-oops-when-truncating-a-file.patch
Patch25088: linux-2.6-fs-vfs-fix-lookup_follow-on-automount-symlinks.patch
Patch25089: linux-2.6-block-introduce-the-rq_is_sync-macro.patch
Patch25090: linux-2.6-block-cfq-iosched-propagate-down-request-sync-flag.patch
Patch25091: linux-2.6-block-cfq-iosched-fix-async-queue-behaviour.patch
Patch25092: linux-2.6-block-cfq-iosched-async-queue-allocation-per-priority.patch
Patch25093: linux-2.6-block-cfq-iosched-fix-ioprio_class_idle-accounting.patch
Patch25094: linux-2.6-net-tipc-fix-various-oopses-in-uninitialized-code.patch
Patch25095: linux-2.6-acpi-warn-on-hot-add-of-memory-exceeding-4g-boundary.patch
Patch25096: linux-2.6-mm-move-locating-vma-code-and-checks-on-it.patch
Patch25097: linux-2.6-mm-move-mremap_fixed-into-its-own-header.patch
Patch25098: linux-2.6-mm-add-new-vma_expandable-helper-function.patch
Patch25099: linux-2.6-mm-fix-checks-for-expand-in-place-mremap.patch
Patch25100: linux-2.6-mm-fix-the-arch-checks-in-mremap_fixed-case.patch
Patch25101: linux-2.6-mm-fix-pgoff-in-have-to-relocate-case-of-mremap.patch
Patch25102: linux-2.6-mm-kill-ancient-cruft-in-s390-compat-mmap.patch
Patch25103: linux-2.6-mm-unify-sys_mmap-functions.patch
Patch25104: linux-2.6-mm-get-rid-of-open-coding-in-ia64_brk.patch
Patch25105: linux-2.6-mm-take-arch_mmap_check-into-get_unmapped_area.patch
Patch25106: linux-2.6-mm-switch-do_brk-to-get_unmapped_area.patch
Patch25107: linux-2.6-mm-keep-get_unmapped_area_prot-functional.patch
Patch25108: linux-2.6-acpi-fix-warn-on-unregister-in-power-meter-driver.patch
Patch25109: linux-2.6-net-sctp-fix-skb_over_panic-w-too-many-unknown-params.patch
Patch25110: linux-2.6-virtio-fix-gfp-flags-passed-by-virtio-balloon-driver.patch
Patch25111: linux-2.6-net-e1000-fix-wol-init-when-wol-disabled-in-eeprom.patch
Patch25112: linux-2.6-misc-futex-fix-fault-handling-in-futex_lock_pi.patch
Patch25113: linux-2.6-misc-futex-handle-user-space-corruption-gracefully.patch
Patch25114: linux-2.6-misc-futex-handle-futex-value-corruption-gracefully.patch
Patch25115: linux-2.6-nfs-revert-retcode-check-in-nfs_revalidate_mapping.patch
Patch25116: linux-2.6-net-sched-fix-sfq-qdisc-crash-w-limit-of-2-packets.patch
Patch25117: linux-2.6-net-tg3-fix-intx-fallback-when-msi-fails.patch
Patch25118: linux-2.6-net-bonding-fix-broken-multicast-with-round-robin-mode.patch
Patch25119: linux-2.6-fs-remove-unneccessary-f_ep_lock-from-fasync_helper.patch
Patch25120: linux-2.6-nfs-don-t-unhash-dentry-in-nfs_lookup_revalidate.patch
Patch25121: linux-2.6-mm-fix-hugepage-corruption-using-vm-drop_caches.patch
Patch25122: linux-2.6-net-neigh-fix-state-transitions-via-netlink-request.patch
Patch25123: linux-2.6-x86_64-fix-time-drift-due-to-faulty-lost-tick-tracking.patch
Patch25124: linux-2.6-net-implement-dev_disable_lro-api-for-rhel5.patch
Patch25125: linux-2.6-net-bxn2x-add-dynamic-lro-disable-support.patch
Patch25126: linux-2.6-net-cnic-fix-crash-during-bnx2x-mtu-change.patch
Patch25127: linux-2.6-net-e1000-e1000e-implement-simple-interrupt-moderation.patch
Patch25128: linux-2.6-net-tg3-fix-panic-in-tg3_interrupt.patch
Patch25129: linux-2.6-net-sctp-file-must-be-valid-before-setting-timeout.patch
Patch25130: linux-2.6-misc-keys-do-not-find-already-freed-keyrings.patch
Patch25131: linux-2.6-mm-clear-page-errors-when-issuing-a-fresh-read-of-page.patch
Patch25132: linux-2.6-fs-gfs2-fix-permissions-checking-for-setflags-ioctl.patch
Patch25133: linux-2.6-x86-grab-atomic64-types-from-upstream.patch
Patch25134: linux-2.6-misc-add-atomic64_cmpxcgh-to-x86_64-include-files.patch
Patch25135: linux-2.6-virt-enable-pvclock-flags-in-vcpu_time_info-structure.patch
Patch25136: linux-2.6-virt-add-a-global-synchronization-point-for-pvclock.patch
Patch25137: linux-2.6-virt-don-t-compute-pvclock-adjustments-if-we-trust-tsc.patch
Patch25138: linux-2.6-net-cnic-fix-bnx2x-panic-w-multiple-interfaces-enabled.patch
Patch25139: linux-2.6-pci-acpiphp-fix-missing-acpiphp_glue_exit.patch
Patch25140: linux-2.6-fs-ext4-move_ext-can-t-overwrite-append-only-files.patch
Patch25141: linux-2.6-net-cnic-fix-panic-when-nl-msg-rcvd-when-device-down.patch
Patch25142: linux-2.6-net-tcp-fix-rcv-mss-estimate-for-lro.patch
Patch25143: linux-2.6-net-bluetooth-fix-possible-bad-memory-access-via-sysfs.patch
Patch25144: linux-2.6-fs-cifs-fix-kernel-bug-with-remote-os-2-server.patch
Patch25145: linux-2.6-block-cfq-iosched-kill-cfq_exit_lock.patch
Patch25146: linux-2.6-block-cfq-iosched-fix-bad-locking-in-changed_ioprio.patch
Patch25147: linux-2.6-message-mptsas-fix-disk-add-failing-due-to-timeout.patch
Patch25148: linux-2.6-security-keys-new-key-flag-for-add_key-from-userspace.patch
Patch25149: linux-2.6-fs-cifs-reject-dns-upcall-add_key-req-from-userspace.patch
Patch25150: linux-2.6-fs-nfs-fix-bug-in-nfsd4-read_buf.patch
Patch25151: linux-2.6-fs-xfs-don-t-let-swapext-operate-on-write-only-files.patch
Patch25152: linux-2.6-scsi-qla2xxx-update-firmware-to-version-5-03-02.patch
Patch25153: linux-2.6-fs-gfs2-fix-rename-causing-kernel-oops.patch
Patch25154: linux-2.6-scsi-ips-driver-sleeps-while-holding-spin_lock.patch
Patch25155: linux-2.6-fs-ecryptfs-fix-ecryptfs_uid_hash-buffer-overflow.patch
Patch25156: linux-2.6-pci-msi-add-option-for-lockless-interrupt-mode.patch
Patch25157: linux-2.6-mm-keep-a-guard-page-below-a-grow-down-stack-segment.patch
Patch25158: linux-2.6-mm-fix-missing-unmap-for-stack-guard-page-failure-case.patch
Patch25159: linux-2.6-mm-fix-page-table-unmap-for-stack-guard-page-properly.patch
Patch25160: linux-2.6-mm-fix-up-some-user-visible-effects-of-stack-guard-page.patch
Patch25161: linux-2.6-mm-pass-correct-mm-when-growing-stack.patch
Patch25162: linux-2.6-mm-accept-an-abutting-stack-segment.patch
Patch25163: linux-2.6-net-sctp-fix-length-checks.patch
Patch25164: linux-2.6-net-bonding-check-if-clients-mac-addr-has-changed.patch
Patch25165: linux-2.6-mm-add-option-to-skip-zero_page-mmap-of-dev-zero.patch
Patch25166: linux-2.6-fs-ext4-consolidate-in_range-definitions.patch
Patch25167: linux-2.6-fs-xfs-always-use-iget-in-bulkstat.patch
Patch25168: linux-2.6-fs-xfs-validate-untrusted-inode-numbers-during-lookup.patch
Patch25169: linux-2.6-fs-xfs-rename-xfs_iget_bulkstat-to-xfs_iget_untrusted.patch
Patch25170: linux-2.6-usb-fix-usbfs-information-leak.patch
Patch25171: linux-2.6-net-sched-fix-some-kernel-memory-leaks.patch
Patch25172: linux-2.6-fs-xfs-fix-untrusted-inode-number-lookup.patch
Patch25173: linux-2.6-s390-dasd-allocate-fallback-cqr-for-reserve-release.patch
Patch25174: linux-2.6-s390-dasd-force-online-does-not-work.patch
Patch25175: linux-2.6-net-cxgb3-add-define-for-fatal-parity-error-bit.patch
Patch25176: linux-2.6-net-cxgb3-clear-fatal-parity-error-register-on-init.patch
Patch25177: linux-2.6-net-cxgb3-get-fatal-parity-error-status-on-interrupt.patch
Patch25178: linux-2.6-net-cxgb3-don-t-flush-workqueue-if-called-from-wq.patch
Patch25179: linux-2.6-fs-xfs-fix-missing-untrusted-inode-lookup-tag.patch
Patch25180: linux-2.6-misc-make-compat_alloc_user_space-incorporate-the-access_ok.patch

Patch30000: diff-xen-smpboot-ifdef-hotplug-20090306
Patch30001: diff-ocfs2-drop-duplicate-functions-20090306

# Start VZ patches
Patch50000: patch-%ovzver-core

# Hot fixes
Patch60001: diff-i2o-msgleak-10070423
Patch60002: diff-i2o-msgget-errh-10070423
Patch60003: diff-i2o-cfg-passthru-20070423
Patch60004: diff-i2o-proc-perms-20060304
Patch60005: diff-i2o-procread-20070509
# alread in RHEL5 .53el5
# Patch60006: diff-megaraid-64bit-dma-20070716
Patch60007: diff-i2o-iosched-fix-20070806
Patch60008: diff-ms-splice-access-20080211
Patch60009: diff-tossing-headers-around

Patch70003: diff-scsi-add-modalias-mainstream

# DRBD
Patch90000: patch-linux-2.6.18-rhel5-drbd-8.3.4
Patch90001: diff-drbd-compilation
Patch90002: diff-drbd-dont-use-connector

# Areca
# replaced with linux-2.6-scsi-add-kernel-support-for-areca-raid-controller.patch
# Patch90200: linux-2.6.18-arcmsr-1.20.0X.14.devel.patch

# 3ware

Patch90210: linux-2.6.18-atl1-1.0.41.0.patch
Patch90211: diff-backport-dm-delay-20070716
Patch90212: diff-dm-limits-bounce_pfn-20071029
# Patch90213: diff-forcedeth-fix-timeout-20071129
# Patch90214: linux-2.6.18-r8169-2.2LK-NAPI-ms-2.6.24-rc3.patch
# this patch doesn't fully help, see bug #95898. simply disabled CONFIG_FB_INTEL
# Patch90215: diff-intelfb-noregister-workaround-20071212
Patch90216: diff-snd-hda-intel
Patch90217: diff-drv-e1000-depends-e1000e-20080718
Patch90220: diff-drv-e1000-select-e1000e

# GFSv1
Patch90300: diff-gfs-kmod-0.1.31_3.el5
Patch90301: diff-gfs-kmod-1.31.1-1.34.2

Patch90401: diff-gfs-kconfig
Patch90402: diff-gfs-vz-fixes-20070514
Patch90403: diff-gfs-aops-fix-20070516
Patch90404: diff-gfs-vzquota-20070521
Patch90406: diff-gfs-debug-bugs-20070521
Patch90407: diff-gfs-setattr-multiple-20070606
Patch90408: diff-gfs-bh-leak-fix-20070716
Patch90409: diff-gfs-dread-oops-20070718
Patch90410: diff-gfs-rm-warn-20070720
Patch90411: diff-gfs-rm-lockfs-support-20071129
Patch90412: diff-gfs-force-localfloks-20080226
Patch90413: diff-gfs-shut-up-debug-20080821
Patch90414: diff-gfs-aio-pops

# Patch90340: diff-dlm-fix-user-unlocking-20070829
# Patch90341: diff-dlm-can-miss-clearing-resend-flag-20070829
# Patch90342: diff-dlm-overlapping-cancel-and-unlock-20070829
# imho this one should be redone on RHEL5.1
# Patch90343: diff-dlm-lowcomms-stop-clean-conn-20070926

# Zaptel/Asterisk modules
Patch90400: linux-2.6.18-asterisk-1.4.7.1.patch

# OpenAFS
Patch90500: diff-openafs-for_each_process
Patch90501: diff-openafs-find_task_by_pid
Patch90502: diff-openafs-exec-context
Patch90503: diff-openafs-configure-no-mod-check

# mix
Patch91002: linux-hp-dmi-info-correct.patch
Patch91003: diff-nfs-rpcsaddr

# Bells and whistles
Patch100000: diff-fs-fsync-enable-rh5-20080131
Patch100001: diff-ms-devleak-dstdebug-20080504
Patch100002: diff-ipv4-dumpbaddst-20080929
Patch100003: diff-ipv4-reliable-dst-garbage-20080929
Patch100004: diff-ve-moreleaks-20090829
Patch100010: diff-ms-nfssync-20081118
Patch100014: diff-ms-devleaktime-20081111
Patch100016: diff-rh-cifs-disable-posix-extensons-by-default-20090304
Patch100017: diff-ms-32bitHW-kernel-panic-string
Patch100018: diff-ms-mmap-min-addr
Patch100020: linux-2.6.18-128.1.1.el5.028stab062.3-build-fixes.diff
Patch100024: diff-make-sysrq-mask-affect-proc-sysrq-trigger-20090826
Patch100025: diff-ms-alow-ve0-exceed-threads-max
Patch100026: diff-ms-ext4-nodelalloc-by-default
Patch100027: diff-rh-hung-task-tunes-and-fixes
Patch100028: diff-rh-bond802.3ad-slave-speed-20100421
Patch100029: diff-vmalloc-supress-passing-gfp-dma32-to-slab
Patch100030: diff-cfq-iosched-zero-async-queue-after-put-20100817
Patch100032: diff-bc-cfq-fix-preemption-logic
Patch100033: diff-ve-net-ipforward-lro-fix-oops
Patch100034: diff-venet-stat-tx_dropped-account-20100910
Patch100035: diff-ve-vzevent-fix-reboot-detection

# MAC HW hacks
Patch101000: diff-mac-acpi-scan-rsdp-bit-lower-20090811
Patch101001: diff-mac-cpufreq-bug-on-apple-xserve-20090811
Patch101007: diff-ms-reboot-via-pci-port-cf9-20090922

# NBD
Patch110001: diff-nbd-from-current
Patch110002: diff-nbd-compile-fixes
Patch110003: diff-nbd-umount-after-connection-lost
Patch110005: diff-nbd-spinlock-usage-fix
Patch110006: diff-nbd-xmit-timeout
Patch110007: diff-nbd-remove-truncate-at-disconnect-20090529
Patch110008: diff-nbd-forbid-socket-clear-without-disconnect-20090529
Patch110009: diff-nbd-pid_show-args-number-20090916

# End VZ patches

# adds rhel version info to version.h
Patch99990: linux-2.6-rhel-version-h.patch
# empty final patch file to facilitate testing of kernel patches
Patch99999: linux-kernel-test.patch

# ALT-specific patches
Patch200000: our_kernel.patch

Patch200100: linux-2.6-scsi-3w-9xxx-update-to-version-2-26-08-006.patch

# END OF PATCH DEFINITIONS

# Override find_provides to use a script that provides "kernel(symbol) = hash".
# Pass path of the RPM temp dir containing kabideps to find-provides script.
%global _use_internal_dependency_generator 0
%define __find_provides %_sourcedir/find-provides %_tmppath
%define __find_requires /usr/lib/rpm/find-requires kernel

%ifarch x86_64
Obsoletes: kernel-smp
%endif
Obsoletes: kernel-modules-rhel5-0
Obsoletes: kernel-modules-rhel5-1
Obsoletes: kernel-modules-rhel5-2

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

%package -n kernel-headers-modules-%flavour
Summary: Headers and other files needed for building kernel modules
Group: Development/Kernel
Requires: gcc%kgcc_version
# ??? Requires: kernel-headers-alsa

%description -n kernel-headers-modules-%flavour
This package contains header files, Makefiles and other parts of the
Linux kernel build system which are needed to build kernel modules for
the Linux kernel package %name-%version-%release.

If you need to compile a third-party kernel module for the Linux
kernel package %name-%version-%release, install this package
and specify %kbuild_dir as the kernel source
directory.

%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation

%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.

%package -n kernel-headers-%flavour
Summary: Header files for the Linux kernel
Group: Development/Kernel
Requires: kernel-headers-common >= 1.1.5
Provides: kernel-headers = %version

%description -n kernel-headers-%flavour
This package makes Linux kernel headers corresponding to the Linux
kernel package %name-%version-%release available for building
userspace programs (if this version of headers is selected by
adjust_kernel_headers).

Since Linux 2.6.18 the kernel build system supports creation of
sanitized kernel headers for use in userspace (by deleting headers
which are not usable in userspace and removing #ifdef __KERNEL__
blocks from installed headers).  This package contains sanitized
headers instead of raw kernel headers which were present in some
previous versions of similar packages.

If possible, try to use glibc-kernheaders instead of this package.

%prep
%setup -T -q -n %name-%version -c
tar -xf /usr/src/kernel/sources/kernel-source-%kversion.tar.bz2
mv kernel-source-%kversion linux-%kversion.%_target_cpu

cd linux-%kversion.%_target_cpu

# this file should be usable both with make and sh (for broken modules
# which do not use the kernel makefile system)
echo 'export GCC_VERSION=%kgcc_version' > gcc_version.inc

# Update to latest upstream.
%patch1 -p1
#%patch2 -p1
%patch3 -p1
%patch4 -p1

# we really want the backported patch and not the stable one
%patch9 -p1 -R

# Patches 10 through 100 are meant for core subsystem upgrades

# Rolands utrace ptrace replacement.
%patch10 -p1

# sysrq works always
%patch20 -p1
%patch21 -p1

# Architecture patches

#
# x86(-64)
#
# Compile 686 kernels tuned for Pentium4.
%patch200 -p1
# add vidfail capability;
# without this patch specifying a framebuffer on the kernel prompt would
# make the boot stop if there's no supported framebuffer device; this is bad
# for the installer cd that wants to automatically fall back to textmode
# in that case
%patch201 -p1
# EDAC support for K8
%patch202 -p1
# Suppress APIC errors on UP x86-64.
%patch203 -p1
# Support TIF_RESTORE_SIGMASK on x86_64
%patch207 -p1
# Add ppoll and pselect syscalls
%patch208 -p1
# fix opteron timer scaling
%patch209 -p1
# add support for x86_64 memory hotplug
%patch210 -p1
# add support for rdtscp in gtod
%patch212 -p1
# unwinder fixes
%patch213 -p1
# temp patch for now
%patch214 -p1
%patch215 -p1
%patch216 -p1

#
# PowerPC
#
# Make HVC console generic; support simulator console device using it.
#%patch302 -p1
# Check properly for successful RTAS instantiation
%patch303 -p1
# Export copy_4K_page for ppc64
%patch304 -p1
# Fix checking for syscall success/failure
%patch306 -p1
# Fix SECCOMP for ppc32
%patch307 -p1
%patch308 -p1

# ia64 futex and [gs]et_robust_list
%patch400 -p1
%patch401 -p1
# ia64 kexec/kdump
%patch402 -p1
%patch404 -p1
%patch405 -p1

# S390
# Kprobes.
%patch500 -p1
%patch501 -p1
%patch502 -p1
%patch503 -p1

#
# Patches 800 through 899 are reserved for bugfixes to the core system
# and patches related to how RPMs are build
#

# This patch adds a "make nonint_oldconfig" which is non-interactive and
# also gives a list of missing options at the end. Useful for automated
# builds (as used in the buildsystem).
%patch800 -p1
# Warn if someone tries to build userspace using kernel headers
%patch801 -p1
# Warn if someone #include's <linux/config.h>
%patch802 -p1

# Exec shield
%patch810 -p1
#%patch811 -p1

#
# GPG signed kernel modules
#
%patch900 -p1
%patch901 -p1
%patch902 -p1
%patch903 -p1
%patch904 -p1
%patch905 -p1

# Tux
%patch910 -p1

#
# Xen
#
%if %includexen
#
# Apply the main xen patch...
#%patch951 -p1
%patch950 -p1 -b .p.xen
#
# ... and back out all the tpm additions, they need fixing
#
for f in `find drivers/char/tpm -type f -name "*.p.xen"` ; do \
    g=`dirname $f`/`basename $f .p.xen`; \
    mv "$f" "$g"; \
    if [ ! -s "$g" ] ; then rm -f "$g" ; fi; \
done
# Delete the rest of the backup files, they just confuse the build later
find -name "*.p.xen" | xargs rm -f

# utrace
%patch951 -p1
%patch952 -p1
%patch953 -p1
# Xen exec-shield bits
%patch954 -p1
%patch955 -p1
# ia64 xen cleanups for kexec/kdump
%patch958 -p1
# xen x86 unwinder fixes
%patch959 -p1

# xen blktap fixes
%patch960 -p1
# The blktap patch needs to rename a file.  For now, that is far more easily
# done in the spec file than in the patch itself.
mv drivers/xen/blktap/blktap.c drivers/xen/blktap/blktapmain.c

%patch961 -p1
%patch962 -p1

%endif

#
# Patches 1000 to 5000 are reserved for bugfixes to drivers and filesystems
#

# Various low-impact patches to aid debugging.
%patch1010 -p1
%patch1011 -p1
%patch1012 -p1
%patch1013 -p1
%patch1014 -p1
%patch1015 -p1
%patch1016 -p1
%patch1017 -p1
%patch1018 -p1
%patch1019 -p1
# Disable the 'quiet' boot switch for better bug reports.
#%patch1020 -p1
%patch1021 -p1
%patch1022 -p1
%if %includexen
%patch1023 -p1
%endif

#
# Make /dev/mem a need-to-know function
#
%patch1050 -p1
%if %includexen
%patch1051 -p1
%endif

#
# /dev/crash driver for the crashdump analysis tool
#
%patch1060 -p1
%if %includexen
%patch1061 -p1
%endif

#
# Most^WAll users of sleep_on are broken; fix a bunch
#
%patch1070 -p1

#
# SCSI Bits.
#
# Add a pci table to advansys driver.
%patch1102 -p1
# add support for qla4xxx
%patch1103 -p1
# iscsi update for 2.6.19-rc1
%patch1104 -p1
# aic9400/adp94xx updates
%patch1105 -p1
# support for ipr to use sas attached sata
%patch1106 -p1
# don't add scsi devices for special targets
%patch1107 -p1
%patch1108 -p1
%patch1109 -p1
# qla3xxx driver
%patch1110 -p1
# scsi blacklist
%patch1111 -p1
%patch1112 -p1
%patch1113 -p1
%patch1114 -p1
%patch1115 -p1
%patch1116 -p1
%patch1117 -p1
%patch1118 -p1
%patch1119 -p1
%patch1120 -p1
%patch1121 -p1

#
# Various NFS/NFSD fixes.
#
# kNFSD: fixed '-p port' arg to rpc.nfsd and enables the defining proto versions and transports
%patch1200 -p1
# Fix badness.
%patch1201 -p1

# core networking changes.
%patch1300 -p1
%patch1301 -p1
%patch1302 -p1
%patch1303 -p1
# netlabel fixes
%patch1304 -p1
%patch1305 -p1
%patch1306 -p1

# NIC driver fixes
%patch1350 -p1 -E
%patch1351 -p1

# Filesystem patches.
# Squashfs
%patch1400 -p1
%patch1401 -p1
# GFS2/DLM
%patch1410 -p1
%patch1411 -p1
%patch1412 -p1
%patch1413 -p1
%patch1414 -p1
%patch1415 -p1
%patch1416 -p1
%patch1417 -p1
%patch1418 -p1
%patch1419 -p1
# Ted's inode diet work.
%patch1420 -p1
%patch1421 -p1
%patch1422 -p1
%patch1423 -p1
%patch1424 -p1
%patch1425 -p1

#nfs sharing
%patch1430 -p1
%patch1431 -p1
# CacheFiles
%patch1432 -p1
%patch1433 -p1
# FS-Cache
%patch1434 -p1
%patch1435 -p1
%patch1436 -p1
%patch1437 -p1

# NFS
# double d_drop
%patch1440 -p1
# NFS supports 64-bit inodes
%patch1441 -p1
# Fix NFS/Selinux oops. (#204848)
%patch1442 -p1
# Fix nfs client dentry oops
%patch1443 -p1
# add ACL cache to NFS client
%patch1444 -p1
%patch1445 -p1
%patch1446 -p1
%patch1447 -p1
%patch1448 -p1
%patch1449 -p1
%patch1450 -p1

# EXT3
# overflows at 16tb fix
%patch1460 -p1
%patch1461 -p1
%patch1462 -p1

# CIFS fixes
%patch1465 -p1

# VFS fixes
# destroy the dentries via umounts
%patch1470 -p1

# AFS fixes
# ensure dentries refs when killed
%patch1475 -p1

# IPV6 routing policy
%patch1480 -p1
%patch1481 -p1
%patch1482 -p1
%patch1483 -p1

# AUTOFS fixes
%patch1490 -p1
%patch1491 -p1

# Device mapper / MD layer
# dm mirroring
%patch1500 -p1
%patch1501 -p1
%patch1502 -p1
%patch1503 -p1
%patch1504 -p1
%patch1505 -p1
%patch1506 -p1
%patch1507 -p1
%patch1508 -p1
%patch1509 -p1
%patch1510 -p1
%patch1511 -p1
%patch1512 -p1
%patch1513 -p1

# Misc fixes
# Add missing MODULE_VERSION tags to some modules.
%patch1600 -p1
# The input layer spews crap no-one cares about.
%patch1610 -p1
# Tickle the NMI whilst doing serial writes.
%patch1620 -p1
# Numerous patches to improve software suspend.
%patch1630 -p1
# Enable autofs4 to return fail for revalidate during lookup
%patch1640 -p1
# Allow to use 480600 baud on 16C950 UARTs
%patch1650 -p1
# Intel i965 DRM support.
%patch1660 -p1
# Use persistent allocation in softcursor
%patch1670 -p1
# reiserfs-make-sure-all-dentries-refs-are-released-before-calling-kill_block_super-try-2.patch
%patch1680 -p1
# Only print migration info on SMP
%patch1710 -p1
# setuid /proc/self/maps fix.
%patch1720 -p1
# Add a safety net to softlockup so that it doesn't prevent installs.
%patch1740 -p1
# Speed up spinlock debug.
%patch1741 -p1
# support EHEA ethernet driver
%patch1742 -p1
# qlogic firmware
%patch1743 -p1

# OLPC specific patches
%if 0%{?olpc}
# Marvell Libertas wireless driver
%patch1744 -p1
# OLPC touchpad
%patch1745 -p1
%endif
# Fixes for DUB-E100 vB1 usb ethernet
%patch1746 -p1
# Fix various Bluetooth compat ioctls
%patch1747 -p1
%patch1748 -p1
%patch1749 -p1
# fix unaligned access on module loading for ia64
%patch1751 -p1
%patch1753 -p1
%patch1754 -p1
%patch1755 -p1
%patch1756 -p1
%patch1758 -p1
%patch1760 -p1
%patch1761 -p1
%patch1762 -p1
%patch1763 -p1
%patch1764 -p1
%patch1765 -p1
%patch1767 -p1
%patch1768 -p1
%patch1769 -p1
%patch1770 -p1

# Fix the SELinux mprotect checks on executable mappings
%patch1801 -p1
# Add support for SELinux range transitions
%patch1802 -p1
%patch1803 -p1
%patch1804 -p1
%patch1805 -p1

# Warn about obsolete functionality usage.
%patch1900 -p1
# Remove kernel-internal functionality that nothing external should use.
%patch1910 -p1

#
# VM related fixes.
#
# Silence GFP_ATOMIC failures.
%patch2001 -p1
# track dirty pages
%patch2002 -p1
# prevent oom kills
%patch2004 -p1
%patch2005 -p1

# Changes to upstream defaults.
# Use UTF-8 by default on VFAT.
%patch2100 -p1
# Increase timeout on firmware loader.
%patch2101 -p1
# Change PHYSICAL_START
%if 0%{?rhel}
#%patch2102 -p1
%else
%patch2102 -p1
%endif

# Use unicode VT's by default.
%patch2103 -p1
# Disable split page table lock
%patch2104 -p1
# panic on oops
%patch2105 -p1

# Enable PATA ports on Promise SATA.
%patch2200 -p1
# Fix AHCI Suspend.
%patch2201 -p1
# add the sas parts
%patch2202 -p1

# ACPI patches

# Lockdep fixes
%patch2400 -p1

# Infiniband driver
%patch2600 -p1
%patch2601 -p1
%patch2602 -p1

# kprobe changes
%patch2700 -p1
%patch2701 -p1
%patch2702 -p1
#%patch2703 -p1
%patch2704 -p1

# wireless driver
%patch2801 -p1 -E

#
# Patches 5000 to 6000 are reserved for new drivers that are about to
# be merged upstream
#

#
# final stuff
#

#
# misc small stuff to make things compile or otherwise improve performance
#
%patch10000 -p1

%if 0%{?rhel}
#add in support for x86 and x86_64 relocatable kernels
%patch211 -p1
#xen fix for x86 relocatable support
%patch957 -p1
%endif

%patch21007 -p1
%patch21008 -p1
%patch21009 -p1
%patch21010 -p1
%patch21011 -p1
%patch21012 -p1
%patch21013 -p1
%patch21014 -p1
%patch21015 -p1
%patch21016 -p1
%patch21017 -p1
%patch21018 -p1
%patch21019 -p1
%patch21021 -p1
%patch21022 -p1
%patch21023 -p1
%patch21024 -p1
%patch21025 -p1
%patch21026 -p1
%patch21027 -p1
%patch21028 -p1
%patch21029 -p1
%patch21030 -p1
%patch21031 -p1
%patch21032 -p1
%patch21033 -p1
%patch21034 -p1
%patch21035 -p1
%patch21036 -p1
%patch21037 -p1
%patch21038 -p1
%patch21039 -p1
%patch21040 -p1
%patch21041 -p1
%patch21042 -p1
%patch21043 -p1
%patch21044 -p1
%patch21045 -p1
%patch21046 -p1
%patch21047 -p1
%patch21048 -p1
%patch21049 -p1
%patch21050 -p1
%patch21051 -p1
%patch21052 -p1
%patch21053 -p1
%patch21054 -p1
%patch21056 -p1
%patch21057 -p1
%patch21058 -p1
%patch21059 -p1
%patch21060 -p1
%patch21061 -p1
%patch21062 -p1
%patch21063 -p1
%patch21064 -p1
%patch21065 -p1
%patch21066 -p1
%patch21067 -p1
%patch21068 -p1
%patch21069 -p1
%patch21070 -p1
%patch21071 -p1
%patch21072 -p1
%patch21073 -p1
%patch21074 -p1
%patch21075 -p1
%patch21076 -p1
%patch21077 -p1
%patch21078 -p1
%patch21079 -p1
%patch21080 -p1
%patch21081 -p1
%patch21082 -p1
%patch21083 -p1
%patch21084 -p1
%patch21085 -p1
%patch21086 -p1
%patch21087 -p1
%patch21088 -p1
%patch21089 -p1
%patch21090 -p1
%patch21091 -p1
%patch21092 -p1
%patch21093 -p1
%patch21094 -p1
%patch21095 -p1
%patch21096 -p1
%patch21097 -p1
%patch21098 -p1
%patch21099 -p1
%patch21100 -p1
%patch21101 -p1
%patch21102 -p1
%patch21103 -p1
%patch21104 -p1
%patch21105 -p1
%patch21106 -p1
%patch21107 -p1
%patch21109 -p1
%patch21110 -p1
%patch21111 -p1
%patch21112 -p1
%patch21113 -p1
%patch21114 -p1
%patch21115 -p1
%patch21116 -p1
%patch21117 -p1
%patch21118 -p1
%patch21119 -p1
%patch21121 -p1
%patch21122 -p1
%patch21123 -p1
%patch21124 -p1
%patch21125 -p1
%patch21126 -p1
%patch21127 -p1
%patch21128 -p1
%patch21129 -p1
%patch21130 -p1
%patch21131 -p1
%patch21132 -p1
%patch21133 -p1
%patch21134 -p1
%patch21135 -p1
%patch21136 -p1
%patch21137 -p1
%patch21138 -p1
%patch21139 -p1
%patch21140 -p1
%patch21141 -p1
%patch21142 -p1
%patch21143 -p1
%patch21144 -p1
%patch21145 -p1
%patch21146 -p1
%patch21147 -p1
%patch21148 -p1
%patch21149 -p1
%patch21150 -p1
%patch21151 -p1
%patch21152 -p1
%patch21153 -p1
%patch21154 -p1
%patch21155 -p1
%patch21156 -p1
%patch21157 -p1
%patch21158 -p1
%patch21159 -p1
%patch21160 -p1
%patch21161 -p1
%patch21162 -p1
%patch21163 -p1
%patch21164 -p1
%patch21165 -p1
%patch21166 -p1
%patch21167 -p1
%patch21168 -p1
%patch21169 -p1
%patch21170 -p1
%patch21171 -p1
%patch21172 -p1
%patch21173 -p1
%patch21174 -p1
%patch21175 -p1
%patch21176 -p1
%patch21177 -p1
%patch21178 -p1
%patch21179 -p1
%patch21180 -p1
%patch21181 -p1
%patch21182 -p1
%patch21183 -p1
%patch21184 -p1
%patch21185 -p1
%patch21186 -p1
%patch21187 -p1
%patch21188 -p1
%patch21189 -p1
%patch21190 -p1
%patch21191 -p1
%patch21192 -p1
%patch21193 -p1
%patch21194 -p1
%patch21195 -p1
%patch21196 -p1
%patch21197 -p1
%patch21198 -p1
%patch21200 -p1
%patch21201 -p1
%patch21202 -p1
%patch21203 -p1
%patch21204 -p1
%patch21205 -p1
%patch21206 -p1
%patch21207 -p1
%patch21208 -p1
%patch21210 -p1
%patch21211 -p1
%patch21212 -p1
%patch21213 -p1
%patch21214 -p1
%patch21215 -p1
%patch21216 -p1
%patch21217 -p1
%patch21218 -p1
%patch21219 -p1
%patch21220 -p1
%patch21221 -p1
%patch21222 -p1
%patch21223 -p1
%patch21224 -p1
%patch21225 -p1
%patch21226 -p1
%patch21227 -p1
%patch21228 -p1
%patch21229 -p1
%patch21230 -p1
%patch21231 -p1
%patch21232 -p1
%patch21233 -p1
%patch21234 -p1
%patch21235 -p1
%patch21236 -p1
%patch21237 -p1
%patch21238 -p1
%patch21239 -p1
%patch21240 -p1
%patch21241 -p1
%patch21242 -p1
%patch21243 -p1
%patch21244 -p1
%patch21245 -p1
%patch21246 -p1
%patch21247 -p1
%patch21248 -p1
%patch21249 -p1
%patch21250 -p1
%patch21251 -p1
%patch21252 -p1
%patch21253 -p1
%patch21254 -p1
%patch21255 -p1
%patch21256 -p1
%patch21257 -p1
%patch21258 -p1
%patch21259 -p1
%patch21260 -p1
%patch21261 -p1
%patch21262 -p1
%patch21263 -p1
%patch21264 -p1
%patch21265 -p1
%patch21266 -p1
%patch21267 -p1
%patch21268 -p1
%patch21269 -p1
%patch21270 -p1
%patch21271 -p1
%patch21272 -p1
%patch21273 -p1
%patch21274 -p1
%patch21275 -p1
%patch21276 -p1
%patch21277 -p1
%patch21278 -p1
%patch21279 -p1
%patch21280 -p1
%patch21281 -p1
%patch21282 -p1
%patch21283 -p1
%patch21284 -p1
%patch21285 -p1
%patch21286 -p1
%patch21287 -p1
%patch21288 -p1
%patch21289 -p1
%patch21290 -p1
%patch21291 -p1
%patch21292 -p1
%patch21293 -p1
%patch21294 -p1
%patch21295 -p1
%patch21296 -p1
%patch21297 -p1
%patch21298 -p1
%patch21299 -p1
%patch21300 -p1
%patch21301 -p1
%patch21303 -p1
%patch21304 -p1
%patch21305 -p1
%patch21306 -p1
%patch21307 -p1
%patch21308 -p1
%patch21309 -p1
%patch21310 -p1
%patch21311 -p1
%patch21312 -p1
%patch21313 -p1
%patch21314 -p1
%patch21315 -p1
%patch21316 -p1
%patch21317 -p1
%patch21318 -p1
%patch21319 -p1
%patch21320 -p1
%patch21321 -p1
%patch21322 -p1
%patch21323 -p1
%patch21324 -p1
%patch21325 -p1
%patch21326 -p1
%patch21327 -p1
%patch21328 -p1
%patch21329 -p1
%patch21330 -p1
%patch21331 -p1
%patch21332 -p1
%patch21333 -p1
%patch21334 -p1
%patch21335 -p1
%patch21336 -p1
%patch21337 -p1
%patch21338 -p1
%patch21339 -p1
%patch21340 -p1
%patch21341 -p1
%patch21342 -p1
%patch21343 -p1
%patch21344 -p1
%patch21345 -p1
%patch21346 -p1
%patch21347 -p1
%patch21348 -p1
%patch21349 -p1
%patch21350 -p1
%patch21351 -p1
%patch21352 -p1
%patch21353 -p1
%patch21354 -p1
%patch21355 -p1
%patch21356 -p1
%patch21357 -p1
%patch21358 -p1
%patch21359 -p1
%patch21360 -p1
%patch21361 -p1
%patch21362 -p1
%patch21363 -p1
%patch21364 -p1
%patch21365 -p1
%patch21366 -p1
%patch21367 -p1
%patch21368 -p1
%patch21369 -p1
%patch21370 -p1
%patch21371 -p1
%patch21372 -p1
%patch21373 -p1
%patch21374 -p1
%patch21375 -p1
%patch21376 -p1
%patch21377 -p1
%patch21378 -p1
%patch21379 -p1
%patch21380 -p1
%patch21381 -p1
%patch21382 -p1
%patch21383 -p1
%patch21385 -p1
%patch21386 -p1
%patch21387 -p1
%patch21388 -p1
%patch21389 -p1
%patch21390 -p1
%patch21391 -p1
%patch21392 -p1
%patch21393 -p1
%patch21394 -p1
%patch21395 -p1
%patch21396 -p1
%patch21397 -p1
%patch21398 -p1
%patch21399 -p1
%patch21400 -p1
%patch21401 -p1
%patch21402 -p1
%patch21403 -p1
%patch21404 -p1
%patch21406 -p1
%patch21407 -p1
%patch21408 -p1
%patch21409 -p1
%patch21410 -p1
%patch21411 -p1
%patch21412 -p1
%patch21413 -p1
%patch21414 -p1
%patch21415 -p1
%patch21416 -p1
%patch21417 -p1
%patch21418 -p1
%patch21419 -p1
%patch21420 -p1
%patch21421 -p1
%patch21422 -p1
%patch21424 -p1
%patch21425 -p1
%patch21426 -p1
%patch21427 -p1
%patch21428 -p1
%patch21429 -p1
%patch21430 -p1
%patch21431 -p1
%patch21432 -p1
%patch21433 -p1
%patch21434 -p1
%patch21435 -p1
%patch21436 -p1
%patch21437 -p1
%patch21438 -p1
%patch21439 -p1
%patch21440 -p1
%patch21441 -p1
%patch21442 -p1
%patch21443 -p1
%patch21444 -p1
%patch21445 -p1
%patch21447 -p1
%patch21448 -p1
%patch21449 -p1
%patch21450 -p1
%patch21451 -p1
%patch21452 -p1
%patch21453 -p1
%patch21454 -p1
%patch21455 -p1
%patch21456 -p1
%patch21457 -p1
%patch21458 -p1
%patch21459 -p1
%patch21460 -p1
%patch21461 -p1
%patch21462 -p1
%patch21463 -p1
%patch21464 -p1
%patch21465 -p1
%patch21466 -p1
%patch21467 -p1
%patch21468 -p1
%patch21469 -p1
%patch21470 -p1
%patch21471 -p1
%patch21472 -p1
%patch21473 -p1
%patch21474 -p1
%patch21475 -p1
%patch21476 -p1
%patch21477 -p1
%patch21478 -p1
%patch21479 -p1
%patch21480 -p1
%patch21481 -p1
%patch21482 -p1
%patch21483 -p1
%patch21484 -p1
%patch21485 -p1
%patch21486 -p1
%patch21487 -p1
%patch21488 -p1
%patch21489 -p1
%patch21490 -p1
%patch21491 -p1
%patch21492 -p1
%patch21493 -p1
%patch21494 -p1
%patch21495 -p1
%patch21496 -p1
%patch21497 -p1
%patch21498 -p1
%patch21499 -p1
%patch21500 -p1
%patch21501 -p1
%patch21502 -p1
%patch21503 -p1
%patch21504 -p1
%patch21505 -p1
%patch21506 -p1
%patch21507 -p1
%patch21508 -p1
%patch21509 -p1
%patch21510 -p1
%patch21511 -p1
%patch21512 -p1
%patch21513 -p1
%patch21514 -p1
%patch21515 -p1
%patch21516 -p1
%patch21517 -p1
%patch21518 -p1
%patch21519 -p1
%patch21520 -p1
%patch21521 -p1
%patch21522 -p1
%patch21523 -p1
%patch21524 -p1
%patch21525 -p1
%patch21526 -p1
%patch21527 -p1
%patch21528 -p1
%patch21529 -p1
%patch21530 -p1
%patch21531 -p1
%patch21532 -p1
%patch21533 -p1
%patch21534 -p1
%patch21535 -p1
%patch21536 -p1
%patch21538 -p1
%patch21539 -p1
%patch21540 -p1
%patch21541 -p1
%patch21542 -p1
%patch21543 -p1
%patch21544 -p1
%patch21545 -p1
%patch21546 -p1
%patch21547 -p1
%patch21548 -p1
%patch21549 -p1
%patch21550 -p1
%patch21551 -p1
%patch21552 -p1
%patch21553 -p1
%patch21554 -p1
%patch21555 -p1
%patch21556 -p1
%patch21557 -p1
%patch21558 -p1
%patch21559 -p1
%patch21560 -p1
%patch21561 -p1 -E
%patch21562 -p1
%patch21563 -p1
%patch21564 -p1
%patch21565 -p1
%patch21566 -p1
%patch21567 -p1
%patch21568 -p1
%patch21569 -p1
%patch21571 -p1
%patch21572 -p1 -E
%patch21573 -p1
%patch21574 -p1
%patch21575 -p1
%patch21576 -p1 -E
%patch21577 -p1
%patch21578 -p1
%patch21579 -p1
%patch21581 -p1
%patch21582 -p1
%patch21583 -p1
%patch21584 -p1
%patch21585 -p1
%patch21586 -p1
%patch21587 -p1
%patch21588 -p1
%patch21589 -p1
%patch21590 -p1
%patch21591 -p1
%patch21592 -p1
%patch21593 -p1
%patch21594 -p1
%patch21595 -p1
%patch21596 -p1
%patch21597 -p1
%patch21598 -p1
%patch21599 -p1
%patch21600 -p1
%patch21601 -p1
%patch21602 -p1
%patch21603 -p1
%patch21604 -p1
%patch21605 -p1
%patch21606 -p1
%patch21607 -p1
%patch21608 -p1
%patch21609 -p1
%patch21610 -p1
%patch21611 -p1
%patch21612 -p1
%patch21613 -p1
%patch21614 -p1
%patch21615 -p1
%patch21616 -p1
%patch21617 -p1
%patch21618 -p1
%patch21619 -p1
%patch21620 -p1
%patch21622 -p1
%patch21623 -p1
%patch21624 -p1
%patch21625 -p1
%patch21626 -p1
%patch21627 -p1
%patch21628 -p1
%patch21629 -p1
%patch21630 -p1
%patch21631 -p1
%patch21632 -p1
%patch21633 -p1
%patch21634 -p1
%patch21635 -p1
%patch21636 -p1
%patch21637 -p1
%patch21638 -p1
%patch21639 -p1
%patch21640 -p1
%patch21641 -p1
%patch21642 -p1
%patch21643 -p1
%patch21644 -p1
%patch21645 -p1
%patch21646 -p1
%patch21648 -p1
%patch21649 -p1
%patch21650 -p1
%patch21651 -p1
%patch21652 -p1
%patch21654 -p1
%patch21655 -p1
%patch21656 -p1
%patch21657 -p1
%patch21658 -p1
%patch21659 -p1
%patch21660 -p1
%patch21661 -p1
%patch21663 -p1
%patch21664 -p1
%patch21665 -p1
%patch21666 -p1
%patch21668 -p1
%patch21669 -p1
%patch21670 -p1
%patch21671 -p1
%patch21672 -p1
%patch21673 -p1
%patch21674 -p1
%patch21675 -p1
%patch21676 -p1
%patch21677 -p1
%patch21678 -p1
%patch21679 -p1
%patch21680 -p1
%patch21681 -p1 -E
%patch21682 -p1
%patch21683 -p1
%patch21684 -p1
%patch21685 -p1
%patch21686 -p1
%patch21687 -p1
%patch21688 -p1
%patch21689 -p1
%patch21690 -p1
%patch21691 -p1
%patch21692 -p1
%patch21693 -p1
%patch21694 -p1
%patch21695 -p1
%patch21696 -p1
%patch21697 -p1
%patch21698 -p1
%patch21699 -p1
%patch21700 -p1
%patch21701 -p1
%patch21702 -p1
%patch21703 -p1
%patch21704 -p1
%patch21705 -p1
%patch21706 -p1
%patch21707 -p1
%patch21708 -p1
%patch21709 -p1
%patch21710 -p1
%patch21711 -p1
%patch21712 -p1
%patch21713 -p1
%patch21714 -p1
%patch21715 -p1
%patch21716 -p1
%patch21717 -p1
%patch21718 -p1
%patch21719 -p1
%patch21720 -p1
%patch21721 -p1
%patch21722 -p1
%patch21723 -p1
%patch21724 -p1
%patch21725 -p1
%patch21726 -p1
%patch21727 -p1 -E
%patch21728 -p1
%patch21729 -p1
%patch21731 -p1
%patch21732 -p1
%patch21733 -p1
%patch21734 -p1
%patch21735 -p1
%patch21736 -p1
%patch21737 -p1
%patch21738 -p1
%patch21739 -p1
%patch21740 -p1
%patch21741 -p1
%patch21742 -p1
%patch21743 -p1
%patch21744 -p1
%patch21745 -p1
%patch21746 -p1
%patch21747 -p1
%patch21748 -p1
%patch21749 -p1
%patch21750 -p1
%patch21751 -p1
%patch21752 -p1
%patch21753 -p1
%patch21754 -p1
%patch21755 -p1
%patch21756 -p1
%patch21757 -p1
%patch21758 -p1
%patch21759 -p1
%patch21760 -p1
%patch21761 -p1
%patch21762 -p1
%patch21763 -p1
%patch21764 -p1
%patch21765 -p1
%patch21766 -p1
%patch21767 -p1
%patch21768 -p1
%patch21769 -p1
%patch21770 -p1
%patch21771 -p1
%patch21772 -p1
%patch21773 -p1
%patch21774 -p1
%patch21775 -p1
%patch21776 -p1
%patch21777 -p1
%patch21778 -p1
%patch21779 -p1
%patch21780 -p1
%patch21781 -p1
%patch21782 -p1
%patch21783 -p1
%patch21784 -p1
%patch21785 -p1
%patch21786 -p1
%patch21787 -p1
%patch21788 -p1
%patch21789 -p1
%patch21790 -p1
%patch21791 -p1
%patch21792 -p1
%patch21793 -p1
%patch21794 -p1
%patch21795 -p1
%patch21796 -p1
%patch21797 -p1
%patch21798 -p1
%patch21799 -p1
%patch21800 -p1
%patch21801 -p1
%patch21802 -p1
%patch21803 -p1
%patch21804 -p1
%patch21805 -p1
%patch21806 -p1
%patch21807 -p1
%patch21808 -p1
%patch21809 -p1
%patch21810 -p1
%patch21811 -p1
%patch21812 -p1
%patch21813 -p1
%patch21814 -p1
%patch21815 -p1
%patch21816 -p1
%patch21817 -p1
%patch21818 -p1
%patch21819 -p1 -E
%patch21820 -p1
%patch21821 -p1
%patch21822 -p1
%patch21823 -p1
%patch21824 -p1
%patch21825 -p1
%patch21826 -p1
%patch21827 -p1
%patch21828 -p1
%patch21829 -p1
%patch21831 -p1
%patch21832 -p1
%patch21833 -p1
%patch21834 -p1
%patch21835 -p1
%patch21836 -p1
%patch21837 -p1
%patch21838 -p1
%patch21839 -p1
%patch21840 -p1
%patch21841 -p1
%patch21842 -p1
%patch21843 -p1
%patch21844 -p1
%patch21845 -p1
%patch21846 -p1
%patch21847 -p1
%patch21848 -p1
%patch21849 -p1
%patch21850 -p1
%patch21851 -p1
%patch21852 -p1
%patch21853 -p1
%patch21854 -p1
%patch21855 -p1
%patch21856 -p1
%patch21857 -p1
%patch21858 -p1
%patch21859 -p1
%patch21860 -p1
%patch21861 -p1
%patch21862 -p1
%patch21863 -p1
%patch21864 -p1
%patch21865 -p1
%patch21866 -p1
%patch21867 -p1
%patch21868 -p1
%patch21869 -p1
%patch21870 -p1
%patch21871 -p1
%patch21872 -p1
%patch21873 -p1
%patch21874 -p1
%patch21875 -p1
%patch21876 -p1
%patch21877 -p1
%patch21878 -p1
%patch21879 -p1
%patch21880 -p1
%patch21881 -p1
%patch21882 -p1
%patch21883 -p1
%patch21884 -p1
%patch21885 -p1
%patch21886 -p1
%patch21887 -p1
%patch21888 -p1
%patch21889 -p1
%patch21890 -p1
%patch21891 -p1
%patch21892 -p1
%patch21893 -p1
%patch21894 -p1
%patch21895 -p1
%patch21896 -p1
%patch21897 -p1
%patch21898 -p1
%patch21899 -p1
%patch21900 -p1
%patch21901 -p1
%patch21902 -p1
%patch21903 -p1
%patch21904 -p1
%patch21905 -p1
%patch21906 -p1
%patch21907 -p1
%patch21908 -p1
%patch21909 -p1
%patch21910 -p1
%patch21911 -p1
%patch21912 -p1
%patch21913 -p1
%patch21914 -p1
%patch21915 -p1
%patch21916 -p1
%patch21917 -p1
%patch21918 -p1
%patch21919 -p1
%patch21920 -p1
%patch21921 -p1
%patch21922 -p1
%patch21923 -p1
%patch21924 -p1
%patch21925 -p1
%patch21926 -p1
%patch21927 -p1
%patch21928 -p1
%patch21929 -p1
%patch21930 -p1
%patch21931 -p1
%patch21932 -p1
%patch21933 -p1
%patch21934 -p1
%patch21935 -p1
%patch21936 -p1
%patch21937 -p1
%patch21938 -p1
%patch21939 -p1
%patch21940 -p1
%patch21941 -p1
%patch21942 -p1
%patch21943 -p1
%patch21944 -p1
%patch21945 -p1
%patch21946 -p1
%patch21947 -p1
%patch21948 -p1
%patch21949 -p1
%patch21950 -p1
%patch21951 -p1
%patch21952 -p1
%patch21954 -p1
%patch21955 -p1
%patch21956 -p1
%patch21957 -p1
%patch21958 -p1
%patch21959 -p1
%patch21960 -p1
%patch21961 -p1
%patch21962 -p1
%patch21963 -p1
%patch21964 -p1
%patch21965 -p1
%patch21966 -p1
%patch21967 -p1
%patch21968 -p1
%patch21969 -p1
%patch21970 -p1
%patch21971 -p1
%patch21972 -p1
%patch21973 -p1
%patch21974 -p1
%patch21975 -p1
%patch21976 -p1
%patch21977 -p1
%patch21978 -p1
%patch21979 -p1
%patch21980 -p1
%patch21981 -p1
%patch21982 -p1
%patch21983 -p1
%patch21984 -p1
%patch21985 -p1
%patch21999 -p1
%patch22000 -p1
%patch22001 -p1
%patch22002 -p1
%patch22003 -p1
%patch22004 -p1
%patch22005 -p1
%patch22006 -p1
%patch22007 -p1
%patch22008 -p1
%patch22009 -p1
%patch22010 -p1
%patch22011 -p1
%patch22012 -p1
%patch22013 -p1
%patch22014 -p1
%patch22015 -p1
%patch22016 -p1
%patch22017 -p1
%patch22018 -p1
%patch22019 -p1
%patch22020 -p1
%patch22021 -p1
%patch22022 -p1
%patch22023 -p1
%patch22024 -p1
%patch22025 -p1
%patch22026 -p1
%patch22027 -p1
%patch22028 -p1
%patch22029 -p1
%patch22030 -p1
%patch22031 -p1
%patch22032 -p1
%patch22033 -p1
%patch22034 -p1
%patch22035 -p1
%patch22036 -p1
%patch22037 -p1
%patch22038 -p1
%patch22039 -p1
%patch22040 -p1
%patch22041 -p1
%patch22042 -p1
%patch22043 -p1
%patch22044 -p1
%patch22045 -p1
%patch22046 -p1
%patch22047 -p1
%patch22048 -p1
%patch22049 -p1
%patch22050 -p1
%patch22051 -p1
%patch22052 -p1
%patch22053 -p1
%patch22054 -p1
%patch22055 -p1
%patch22056 -p1
%patch22057 -p1
%patch22058 -p1
%patch22059 -p1
%patch22060 -p1
%patch22061 -p1
%patch22062 -p1
%patch22063 -p1
%patch22064 -p1
%patch22065 -p1
%patch22066 -p1
%patch22067 -p1
%patch22068 -p1
%patch22069 -p1
%patch22070 -p1
%patch22071 -p1
%patch22072 -p1
%patch22073 -p1
%patch22074 -p1
%patch22075 -p1
%patch22076 -p1
%patch22077 -p1
%patch22078 -p1
%patch22079 -p1
%patch22080 -p1
%patch22081 -p1
%patch22082 -p1
%patch22083 -p1
%patch22084 -p1
%patch22085 -p1
%patch22086 -p1
%patch22087 -p1
%patch22088 -p1
%patch22089 -p1
%patch22090 -p1
%patch22091 -p1
%patch22092 -p1
%patch22093 -p1
%patch22094 -p1
%patch22095 -p1
%patch22096 -p1
%patch22097 -p1
%patch22098 -p1
%patch22099 -p1
%patch22100 -p1
%patch22101 -p1
%patch22102 -p1
%patch22103 -p1
%patch22104 -p1
%patch22105 -p1
%patch22106 -p1
%patch22107 -p1
%patch22108 -p1
%patch22109 -p1
%patch22110 -p1
%patch22111 -p1
%patch22112 -p1
%patch22113 -p1
%patch22114 -p1
%patch22115 -p1
%patch22116 -p1
%patch22117 -p1
%patch22118 -p1
%patch22119 -p1
%patch22120 -p1
%patch22121 -p1
%patch22122 -p1
%patch22123 -p1
%patch22124 -p1
%patch22125 -p1
%patch22126 -p1
%patch22127 -p1
%patch22128 -p1
%patch22129 -p1
%patch22130 -p1
%patch22131 -p1
%patch22132 -p1
%patch22133 -p1
%patch22134 -p1
%patch22135 -p1
%patch22136 -p1
%patch22137 -p1
%patch22138 -p1
%patch22139 -p1
%patch22140 -p1
%patch22141 -p1
%patch22142 -p1
%patch22143 -p1
%patch22144 -p1
%patch22145 -p1
%patch22146 -p1
%patch22147 -p1
%patch22148 -p1
%patch22149 -p1
%patch22150 -p1
%patch22151 -p1
%patch22152 -p1
%patch22153 -p1
%patch22154 -p1
%patch22155 -p1
%patch22156 -p1
%patch22157 -p1
%patch22158 -p1
%patch22159 -p1
%patch22160 -p1
%patch22161 -p1
%patch22162 -p1
%patch22163 -p1
%patch22164 -p1
%patch22165 -p1
%patch22166 -p1
%patch22167 -p1
%patch22168 -p1
%patch22169 -p1
%patch22170 -p1 -E
%patch22171 -p1
%patch22172 -p1 -E
%patch22173 -p1 -E
%patch22174 -p1 -E
%patch22175 -p1
%patch22176 -p1
%patch22177 -p1
%patch22178 -p1
%patch22179 -p1
%patch22180 -p1
%patch22181 -p1
%patch22182 -p1
%patch22183 -p1
%patch22184 -p1
%patch22185 -p1
%patch22186 -p1
%patch22187 -p1
%patch22188 -p1
%patch22189 -p1
%patch22190 -p1
%patch22191 -p1
%patch22192 -p1
%patch22193 -p1
%patch22194 -p1
%patch22195 -p1
%patch22196 -p1
%patch22197 -p1
%patch22198 -p1
%patch22199 -p1
%patch22200 -p1
%patch22201 -p1
%patch22202 -p1
%patch22203 -p1
%patch22204 -p1
%patch22205 -p1
%patch22206 -p1
%patch22207 -p1
%patch22208 -p1
%patch22209 -p1
%patch22210 -p1
%patch22211 -p1
%patch22212 -p1
%patch22213 -p1
%patch22214 -p1
%patch22215 -p1
%patch22216 -p1
%patch22217 -p1
%patch22218 -p1
%patch22219 -p1
%patch22220 -p1
%patch22221 -p1
%patch22222 -p1
%patch22223 -p1
%patch22224 -p1
%patch22225 -p1
%patch22226 -p1
%patch22227 -p1
%patch22228 -p1
%patch22229 -p1
%patch22230 -p1
%patch22231 -p1
%patch22232 -p1
%patch22233 -p1
%patch22234 -p1
%patch22235 -p1
%patch22236 -p1
%patch22237 -p1
%patch22238 -p1
%patch22239 -p1
%patch22240 -p1
%patch22241 -p1
%patch22242 -p1
%patch22243 -p1
%patch22244 -p1
%patch22245 -p1
%patch22246 -p1
%patch22247 -p1
%patch22248 -p1
%patch22249 -p1
%patch22250 -p1
%patch22251 -p1
%patch22252 -p1
%patch22253 -p1
%patch22254 -p1
%patch22255 -p1
%patch22256 -p1
%patch22257 -p1
%patch22258 -p1
%patch22259 -p1
%patch22260 -p1
%patch22261 -p1
%patch22262 -p1
%patch22263 -p1
%patch22264 -p1
%patch22265 -p1
%patch22266 -p1
%patch22267 -p1
%patch22268 -p1
%patch22269 -p1
%patch22270 -p1
%patch22271 -p1
%patch22272 -p1
%patch22273 -p1
%patch22274 -p1
%patch22275 -p1
%patch22276 -p1
%patch22277 -p1
%patch22278 -p1
%patch22279 -p1
%patch22280 -p1
%patch22281 -p1
%patch22282 -p1
%patch22283 -p1
%patch22284 -p1
%patch22285 -p1
%patch22286 -p1
%patch22287 -p1
%patch22288 -p1
%patch22289 -p1
%patch22290 -p1
%patch22291 -p1
%patch22292 -p1
%patch22293 -p1
%patch22294 -p1
%patch22296 -p1
%patch22297 -p1
%patch22298 -p1
%patch22300 -p1
%patch22301 -p1
%patch22302 -p1
%patch22303 -p1
%patch22304 -p1
%patch22305 -p1
%patch22306 -p1
%patch22307 -p1
%patch22311 -p1
%patch22312 -p1
%patch22313 -p1
%patch22314 -p1
%patch22315 -p1
%patch22316 -p1
%patch22317 -p1
%patch22318 -p1
%patch22319 -p1
%patch22320 -p1
%patch22321 -p1
%patch22322 -p1
%patch22323 -p1
%patch22324 -p1
%patch22325 -p1
%patch22326 -p1
%patch22327 -p1
%patch22328 -p1
%patch22329 -p1
%patch22330 -p1
%patch22331 -p1
%patch22332 -p1
%patch22333 -p1
%patch22334 -p1
%patch22335 -p1
%patch22336 -p1
%patch22337 -p1
%patch22338 -p1
%patch22339 -p1
%patch22340 -p1
%patch22341 -p1
%patch22342 -p1 -E
%patch22343 -p1
%patch22344 -p1
%patch22345 -p1
%patch22346 -p1
%patch22347 -p1
%patch22348 -p1
%patch22349 -p1
%patch22350 -p1
%patch22351 -p1
%patch22352 -p1
%patch22353 -p1
%patch22354 -p1
%patch22355 -p1
%patch22356 -p1
%patch22357 -p1
%patch22358 -p1
%patch22359 -p1
%patch22360 -p1
%patch22361 -p1
%patch22362 -p1
%patch22363 -p1
%patch22364 -p1
%patch22365 -p1
%patch22366 -p1
%patch22367 -p1
%patch22368 -p1
%patch22369 -p1
%patch22370 -p1
%patch22371 -p1
%patch22372 -p1
%patch22373 -p1
%patch22374 -p1
%patch22375 -p1
%patch22376 -p1
%patch22377 -p1
%patch22378 -p1
%patch22379 -p1
%patch22380 -p1
%patch22381 -p1
%patch22382 -p1
%patch22383 -p1
%patch22384 -p1
%patch22385 -p1
%patch22386 -p1
%patch22388 -p1
%patch22389 -p1
%patch22390 -p1
%patch22391 -p1
%patch22392 -p1
%patch22393 -p1
%patch22394 -p1
%patch22395 -p1
%patch22396 -p1
%patch22397 -p1
%patch22398 -p1
%patch22399 -p1
%patch22400 -p1
%patch22401 -p1
%patch22402 -p1
%patch22403 -p1
%patch22404 -p1
%patch22405 -p1
%patch22406 -p1
%patch22407 -p1
%patch22408 -p1
%patch22409 -p1
%patch22410 -p1
%patch22411 -p1
%patch22412 -p1
%patch22413 -p1
%patch22414 -p1
%patch22415 -p1
%patch22416 -p1
%patch22417 -p1
%patch22418 -p1
%patch22419 -p1
%patch22420 -p1
%patch22421 -p1
%patch22422 -p1
%patch22423 -p1
%patch22424 -p1
%patch22425 -p1
%patch22426 -p1
%patch22427 -p1
%patch22428 -p1
%patch22429 -p1
%patch22430 -p1
%patch22431 -p1
%patch22432 -p1
%patch22433 -p1
%patch22434 -p1
%patch22435 -p1
%patch22436 -p1
%patch22437 -p1
%patch22438 -p1
%patch22439 -p1
%patch22440 -p1
%patch22441 -p1
%patch22442 -p1
%patch22443 -p1
%patch22444 -p1
%patch22445 -p1
%patch22446 -p1
%patch22447 -p1
%patch22448 -p1
%patch22449 -p1
%patch22450 -p1
%patch22451 -p1
%patch22452 -p1
%patch22453 -p1
%patch22454 -p1
%patch22455 -p1
%patch22456 -p1
%patch22457 -p1
%patch22458 -p1
%patch22459 -p1
%patch22460 -p1
%patch22461 -p1
%patch22462 -p1
%patch22463 -p1
%patch22464 -p1
%patch22465 -p1
%patch22466 -p1
%patch22467 -p1
%patch22468 -p1
%patch22469 -p1
%patch22470 -p1
%patch22471 -p1
%patch22472 -p1
%patch22473 -p1
%patch22474 -p1
%patch22475 -p1
%patch22476 -p1
%patch22477 -p1
%patch22478 -p1
%patch22479 -p1
%patch22480 -p1
%patch22481 -p1
%patch22482 -p1
%patch22483 -p1
%patch22484 -p1
%patch22485 -p1
%patch22486 -p1
%patch22487 -p1
%patch22488 -p1
%patch22489 -p1
%patch22490 -p1
%patch22491 -p1
%patch22492 -p1
%patch22493 -p1
%patch22494 -p1
%patch22495 -p1
%patch22496 -p1
%patch22497 -p1
%patch22498 -p1
%patch22499 -p1
%patch22500 -p1
%patch22501 -p1
%patch22502 -p1
%patch22503 -p1
%patch22504 -p1
%patch22505 -p1
%patch22506 -p1
%patch22507 -p1
%patch22508 -p1
%patch22509 -p1
%patch22510 -p1
%patch22511 -p1
%patch22512 -p1
%patch22513 -p1
%patch22514 -p1
%patch22515 -p1
%patch22516 -p1
%patch22517 -p1
%patch22518 -p1
%patch22519 -p1
%patch22520 -p1
%patch22521 -p1
%patch22522 -p1
%patch22523 -p1
%patch22524 -p1
%patch22525 -p1
%patch22526 -p1
%patch22527 -p1
%patch22528 -p1
%patch22529 -p1
%patch22530 -p1
%patch22531 -p1
%patch22532 -p1
%patch22533 -p1
%patch22534 -p1
%patch22535 -p1
%patch22536 -p1
%patch22537 -p1
%patch22538 -p1
%patch22539 -p1
%patch22540 -p1
%patch22541 -p1
%patch22542 -p1
%patch22543 -p1
%patch22544 -p1
%patch22545 -p1
%patch22546 -p1
%patch22547 -p1
%patch22548 -p1
%patch22549 -p1
%patch22550 -p1
%patch22551 -p1
%patch22552 -p1
%patch22553 -p1
%patch22554 -p1
%patch22555 -p1
%patch22556 -p1
%patch22557 -p1
%patch22558 -p1
%patch22559 -p1
%patch22560 -p1
%patch22561 -p1
%patch22562 -p1
%patch22563 -p1
%patch22564 -p1
%patch22565 -p1
%patch22566 -p1
%patch22567 -p1
%patch22568 -p1
%patch22569 -p1
%patch22570 -p1
%patch22571 -p1
%patch22572 -p1
%patch22573 -p1
%patch22574 -p1
%patch22575 -p1
%patch22576 -p1
%patch22577 -p1
%patch22578 -p1
%patch22579 -p1
%patch22580 -p1
%patch22581 -p1
%patch22582 -p1
%patch22583 -p1
%patch22584 -p1
%patch22585 -p1
%patch22586 -p1
%patch22587 -p1
%patch22588 -p1
%patch22589 -p1
%patch22590 -p1
%patch22591 -p1
%patch22592 -p1
%patch22593 -p1
%patch22594 -p1
%patch22595 -p1
%patch22596 -p1
%patch22597 -p1
%patch22598 -p1
%patch22599 -p1
%patch22600 -p1
%patch22601 -p1
%patch22602 -p1
%patch22603 -p1
%patch22604 -p1
%patch22605 -p1
%patch22606 -p1
%patch22607 -p1
%patch22608 -p1
%patch22609 -p1
%patch22610 -p1
%patch22611 -p1
%patch22612 -p1
%patch22613 -p1
%patch22614 -p1
%patch22615 -p1
%patch22616 -p1
%patch22617 -p1
%patch22618 -p1
%patch22619 -p1
%patch22620 -p1
%patch22621 -p1
%patch22622 -p1
%patch22623 -p1
%patch22624 -p1
%patch22625 -p1
%patch22626 -p1
%patch22627 -p1
%patch22628 -p1
%patch22629 -p1
%patch22630 -p1
%patch22631 -p1
%patch22632 -p1
%patch22633 -p1
%patch22634 -p1
%patch22635 -p1
%patch22636 -p1
%patch22637 -p1
%patch22638 -p1
%patch22639 -p1
%patch22640 -p1
%patch22641 -p1
%patch22642 -p1
%patch22643 -p1
%patch22644 -p1
%patch22645 -p1
%patch22646 -p1
%patch22647 -p1
%patch22648 -p1
%patch22649 -p1
%patch22650 -p1
%patch22651 -p1
%patch22652 -p1
%patch22653 -p1
%patch22654 -p1
%patch22655 -p1
%patch22656 -p1
%patch22657 -p1
%patch22658 -p1
%patch22659 -p1
%patch22660 -p1
%patch22661 -p1
%patch22662 -p1
%patch22663 -p1
%patch22664 -p1
%patch22665 -p1
%patch22666 -p1
%patch22667 -p1
%patch22668 -p1
%patch22669 -p1
%patch22670 -p1
%patch22671 -p1
%patch22672 -p1
%patch22673 -p1
%patch22674 -p1
%patch22675 -p1
%patch22676 -p1
%patch22677 -p1
%patch22678 -p1
%patch22679 -p1
%patch22680 -p1
%patch22681 -p1
%patch22682 -p1
%patch22683 -p1
%patch22684 -p1
%patch22685 -p1
%patch22686 -p1
%patch22687 -p1
%patch22688 -p1
%patch22689 -p1
%patch22690 -p1
%patch22691 -p1
%patch22692 -p1
%patch22693 -p1
%patch22694 -p1
%patch22695 -p1
%patch22696 -p1
%patch22697 -p1
%patch22698 -p1
%patch22699 -p1
%patch22700 -p1
%patch22701 -p1
%patch22702 -p1
%patch22703 -p1
%patch22704 -p1
%patch22705 -p1
%patch22706 -p1
%patch22707 -p1
%patch22708 -p1
%patch22709 -p1
%patch22710 -p1
%patch22711 -p1
%patch22712 -p1
%patch22713 -p1
%patch22714 -p1
%patch22715 -p1
%patch22716 -p1
%patch22717 -p1
%patch22718 -p1
%patch22719 -p1
%patch22720 -p1
%patch22721 -p1
%patch22722 -p1
%patch22723 -p1
%patch22724 -p1
%patch22725 -p1
%patch22726 -p1
%patch22727 -p1
%patch22728 -p1
%patch22729 -p1
%patch22730 -p1
%patch22731 -p1
%patch22732 -p1
%patch22733 -p1
%patch22734 -p1
%patch22735 -p1
%patch22736 -p1
%patch22737 -p1
%patch22738 -p1
%patch22739 -p1
%patch22740 -p1
%patch22741 -p1
%patch22742 -p1
%patch22743 -p1
%patch22744 -p1
%patch22745 -p1
%patch22746 -p1
%patch22747 -p1
%patch22748 -p1
%patch22749 -p1
%patch22750 -p1
%patch22751 -p1
%patch22752 -p1
%patch22753 -p1
%patch22754 -p1
%patch22755 -p1
%patch22756 -p1
%patch22757 -p1
%patch22758 -p1
%patch22759 -p1
%patch22760 -p1
%patch22761 -p1
%patch22762 -p1
%patch22763 -p1
%patch22764 -p1
%patch22765 -p1
%patch22766 -p1
%patch22767 -p1
%patch22768 -p1
%patch22769 -p1
%patch22770 -p1
%patch22771 -p1
%patch22772 -p1
%patch22773 -p1
%patch22774 -p1
%patch22775 -p1
%patch22776 -p1
%patch22777 -p1
%patch22778 -p1
%patch22779 -p1
%patch22780 -p1
%patch22781 -p1
%patch22782 -p1
%patch22783 -p1
%patch22784 -p1
%patch22785 -p1
%patch22786 -p1
%patch22787 -p1
%patch22788 -p1
%patch22789 -p1
%patch22790 -p1
%patch22791 -p1
%patch22792 -p1
%patch22793 -p1
%patch22794 -p1
%patch22795 -p1
%patch22796 -p1
%patch22797 -p1
%patch22798 -p1
%patch22799 -p1
%patch22800 -p1
%patch22801 -p1
%patch22802 -p1
%patch22803 -p1
%patch22804 -p1
%patch22805 -p1
%patch22806 -p1
%patch22807 -p1
%patch22808 -p1
%patch22809 -p1
%patch22810 -p1
%patch22811 -p1
%patch22812 -p1
%patch22813 -p1
%patch22814 -p1
%patch22815 -p1
%patch22816 -p1
%patch22817 -p1
%patch22818 -p1
%patch22819 -p1
%patch22820 -p1
%patch22821 -p1
%patch22822 -p1
%patch22823 -p1
%patch22824 -p1
%patch22825 -p1
%patch22826 -p1
%patch22827 -p1
%patch22828 -p1
%patch22829 -p1
%patch22830 -p1
%patch22831 -p1
%patch22832 -p1
%patch22833 -p1
%patch22835 -p1
%patch22836 -p1
%patch22837 -p1
%patch22838 -p1
%patch22839 -p1
%patch22840 -p1
%patch22841 -p1
%patch22842 -p1
%patch22843 -p1
%patch22844 -p1
%patch22845 -p1
%patch22846 -p1
%patch22847 -p1
%patch22848 -p1
%patch22849 -p1
%patch22850 -p1
%patch22851 -p1
%patch22852 -p1
%patch22853 -p1
%patch22854 -p1
%patch22855 -p1
%patch22856 -p1
%patch22857 -p1
%patch22858 -p1
%patch22859 -p1
%patch22860 -p1
%patch22861 -p1
%patch22862 -p1
%patch22863 -p1
%patch22864 -p1
%patch22865 -p1
%patch22866 -p1
%patch22867 -p1
%patch22868 -p1
%patch22869 -p1
%patch22870 -p1
%patch22871 -p1
%patch22872 -p1
%patch22873 -p1
%patch22874 -p1
%patch22876 -p1
%patch22877 -p1
%patch22878 -p1
%patch22879 -p1
%patch22880 -p1
%patch22881 -p1
%patch22882 -p1
%patch22883 -p1
%patch22884 -p1
%patch22885 -p1
%patch22886 -p1
%patch22887 -p1
%patch22888 -p1
%patch22889 -p1
%patch22890 -p1
%patch22891 -p1
%patch22892 -p1
%patch22893 -p1
%patch22894 -p1
%patch22895 -p1
%patch22896 -p1
%patch22897 -p1
%patch22898 -p1
%patch22899 -p1
%patch22900 -p1
%patch22901 -p1
%patch22903 -p1
%patch22904 -p1
%patch22905 -p1
%patch22906 -p1 -E
%patch22907 -p1 -E
%patch22908 -p1 -E
%patch22909 -p1
%patch22910 -p1
%patch22911 -p1
%patch22912 -p1 -E
%patch22913 -p1 -E
%patch22914 -p1 -E
%patch22915 -p1 -E
%patch22916 -p1 -E
%patch22917 -p1
%patch22918 -p1
%patch22919 -p1
%patch22920 -p1
%patch22921 -p1
%patch22922 -p1
%patch22923 -p1
%patch22924 -p1
%patch22925 -p1
%patch22926 -p1
%patch22927 -p1
%patch22928 -p1
%patch22929 -p1
%patch22930 -p1
%patch22931 -p1
%patch22932 -p1
%patch22933 -p1
%patch22934 -p1
%patch22935 -p1
%patch22936 -p1
%patch22937 -p1
%patch22938 -p1
%patch22939 -p1
%patch22940 -p1
%patch22941 -p1
%patch22942 -p1
%patch22943 -p1
%patch22944 -p1
%patch22945 -p1
%patch22946 -p1
%patch22947 -p1
%patch22948 -p1
%patch22949 -p1
%patch22950 -p1
%patch22951 -p1
%patch22952 -p1
%patch22953 -p1
%patch22954 -p1
%patch22955 -p1
%patch22956 -p1
%patch22957 -p1
%patch22958 -p1
%patch22959 -p1
%patch22960 -p1
%patch22961 -p1
%patch22962 -p1
%patch22963 -p1
%patch22964 -p1
%patch22965 -p1
%patch22966 -p1
%patch22967 -p1
%patch22968 -p1
%patch22969 -p1
%patch22970 -p1
%patch22971 -p1
%patch22972 -p1
%patch22973 -p1
%patch22974 -p1
%patch22975 -p1
%patch22976 -p1
%patch22977 -p1
%patch22978 -p1
%patch22979 -p1
%patch22980 -p1
%patch22981 -p1
%patch22982 -p1
%patch22983 -p1
%patch22984 -p1
%patch22985 -p1
%patch22986 -p1
%patch22987 -p1
%patch22988 -p1
%patch22989 -p1
%patch22990 -p1
%patch22991 -p1
%patch22992 -p1 -E
%patch22993 -p1 -E
%patch22994 -p1
%patch22995 -p1
%patch22996 -p1
%patch22997 -p1
%patch22998 -p1
%patch22999 -p1
%patch23000 -p1
%patch23001 -p1
%patch23002 -p1
%patch23003 -p1
%patch23004 -p1
%patch23005 -p1
%patch23006 -p1
%patch23007 -p1
%patch23008 -p1
%patch23009 -p1
%patch23010 -p1
%patch23011 -p1
%patch23012 -p1
%patch23013 -p1
%patch23014 -p1
%patch23015 -p1
%patch23016 -p1
%patch23017 -p1
%patch23018 -p1
%patch23019 -p1
%patch23020 -p1
%patch23021 -p1
%patch23022 -p1
%patch23023 -p1
%patch23024 -p1
%patch23025 -p1
%patch23026 -p1
%patch23027 -p1
%patch23028 -p1
%patch23029 -p1
%patch23030 -p1
%patch23031 -p1
%patch23032 -p1
%patch23033 -p1
%patch23034 -p1
%patch23035 -p1
%patch23036 -p1
%patch23037 -p1
%patch23038 -p1
%patch23039 -p1 -E
%patch23040 -p1
%patch23041 -p1
%patch23042 -p1
%patch23043 -p1
%patch23044 -p1
%patch23045 -p1
%patch23046 -p1
%patch23047 -p1
%patch23048 -p1
%patch23049 -p1
%patch23050 -p1
%patch23051 -p1
%patch23052 -p1
%patch23053 -p1
%patch23054 -p1
%patch23055 -p1
%patch23056 -p1
%patch23057 -p1
%patch23058 -p1
%patch23059 -p1
%patch23060 -p1
%patch23061 -p1
%patch23062 -p1
%patch23063 -p1
%patch23064 -p1
%patch23065 -p1
%patch23066 -p1
%patch23067 -p1
%patch23068 -p1
%patch23069 -p1
%patch23070 -p1
%patch23071 -p1
%patch23072 -p1
%patch23073 -p1
%patch23074 -p1
%patch23075 -p1
%patch23076 -p1
%patch23077 -p1
%patch23078 -p1
%patch23079 -p1
%patch23080 -p1
%patch23081 -p1
%patch23082 -p1
%patch23083 -p1
%patch23084 -p1
%patch23085 -p1
%patch23086 -p1
%patch23087 -p1
%patch23088 -p1
%patch23089 -p1
%patch23090 -p1
%patch23091 -p1
%patch23092 -p1
%patch23093 -p1
%patch23094 -p1
%patch23095 -p1
%patch23096 -p1
%patch23097 -p1
%patch23098 -p1
%patch23099 -p1
%patch23100 -p1
%patch23101 -p1
%patch23102 -p1
%patch23103 -p1
%patch23104 -p1
%patch23105 -p1
%patch23106 -p1
%patch23107 -p1
%patch23108 -p1
%patch23109 -p1
%patch23110 -p1
%patch23111 -p1
%patch23112 -p1
%patch23113 -p1
%patch23114 -p1
%patch23115 -p1
%patch23116 -p1
%patch23117 -p1
%patch23118 -p1
%patch23119 -p1
%patch23120 -p1
%patch23121 -p1
%patch23122 -p1
%patch23123 -p1
%patch23124 -p1
%patch23125 -p1
%patch23126 -p1
%patch23127 -p1
%patch23128 -p1
%patch23129 -p1
%patch23130 -p1
%patch23131 -p1
%patch23132 -p1
%patch23133 -p1
%patch23134 -p1
%patch23135 -p1
%patch23136 -p1
%patch23137 -p1
%patch23138 -p1
%patch23139 -p1
%patch23140 -p1
%patch23141 -p1
%patch23142 -p1
%patch23143 -p1
%patch23144 -p1
%patch23145 -p1
%patch23146 -p1
%patch23147 -p1
%patch23148 -p1
%patch23149 -p1
%patch23150 -p1
%patch23151 -p1
%patch23152 -p1
%patch23153 -p1
%patch23154 -p1
%patch23155 -p1
%patch23156 -p1
%patch23157 -p1
%patch23158 -p1
%patch23159 -p1
%patch23160 -p1
%patch23161 -p1
%patch23162 -p1
%patch23163 -p1
%patch23164 -p1
%patch23165 -p1
%patch23166 -p1
%patch23167 -p1
%patch23168 -p1
%patch23169 -p1
%patch23170 -p1
%patch23171 -p1
%patch23172 -p1
%patch23173 -p1
%patch23174 -p1
%patch23175 -p1
%patch23176 -p1 -E
%patch23177 -p1
%patch23178 -p1
%patch23179 -p1
%patch23180 -p1
%patch23181 -p1
%patch23182 -p1
%patch23183 -p1
%patch23184 -p1
%patch23185 -p1
%patch23186 -p1
%patch23187 -p1
%patch23188 -p1
%patch23189 -p1
%patch23190 -p1
%patch23191 -p1
%patch23192 -p1
%patch23193 -p1
%patch23194 -p1
%patch23195 -p1
%patch23196 -p1
%patch23197 -p1
%patch23198 -p1
%patch23199 -p1
%patch23200 -p1
%patch23201 -p1
%patch23202 -p1
%patch23203 -p1
%patch23204 -p1
%patch23205 -p1
%patch23206 -p1
%patch23207 -p1
%patch23208 -p1
%patch23209 -p1
%patch23210 -p1
%patch23211 -p1
%patch23212 -p1
%patch23213 -p1
%patch23214 -p1
%patch23215 -p1
%patch23216 -p1
%patch23217 -p1
%patch23218 -p1
%patch23219 -p1
%patch23220 -p1
%patch23221 -p1
%patch23222 -p1
%patch23223 -p1
%patch23224 -p1
%patch23225 -p1
%patch23226 -p1
%patch23227 -p1
%patch23228 -p1
%patch23229 -p1
%patch23230 -p1
%patch23231 -p1
%patch23232 -p1
%patch23233 -p1
%patch23234 -p1
%patch23235 -p1
%patch23236 -p1
%patch23237 -p1
%patch23238 -p1
%patch23239 -p1
%patch23240 -p1
%patch23241 -p1
%patch23242 -p1
%patch23243 -p1
%patch23244 -p1
%patch23245 -p1
%patch23246 -p1
%patch23247 -p1
%patch23248 -p1
%patch23249 -p1
%patch23250 -p1
%patch23251 -p1
%patch23252 -p1
%patch23253 -p1
%patch23254 -p1
%patch23255 -p1
%patch23256 -p1
%patch23257 -p1
%patch23258 -p1
%patch23259 -p1
%patch23260 -p1
%patch23261 -p1
%patch23262 -p1
%patch23263 -p1
%patch23264 -p1
%patch23265 -p1
%patch23266 -p1
%patch23267 -p1
%patch23268 -p1
%patch23269 -p1
%patch23270 -p1
%patch23271 -p1
%patch23272 -p1
%patch23273 -p1
%patch23274 -p1
%patch23275 -p1
%patch23276 -p1
%patch23277 -p1
%patch23278 -p1
%patch23279 -p1
%patch23280 -p1
%patch23281 -p1
%patch23282 -p1
%patch23283 -p1
%patch23284 -p1
%patch23285 -p1
%patch23286 -p1
%patch23287 -p1
%patch23288 -p1
%patch23289 -p1
%patch23290 -p1
%patch23291 -p1
%patch23292 -p1
%patch23293 -p1
%patch23294 -p1
%patch23295 -p1
%patch23296 -p1
%patch23297 -p1
%patch23298 -p1
%patch23299 -p1
%patch23300 -p1
%patch23301 -p1
%patch23302 -p1
%patch23303 -p1
%patch23304 -p1
%patch23305 -p1
%patch23306 -p1
%patch23307 -p1
%patch23308 -p1
%patch23309 -p1
%patch23310 -p1
%patch23311 -p1
%patch23312 -p1
%patch23313 -p1
%patch23314 -p1
%patch23315 -p1
%patch23316 -p1
%patch23317 -p1
%patch23318 -p1
%patch23319 -p1
%patch23320 -p1
%patch23321 -p1
%patch23322 -p1
%patch23323 -p1
%patch23324 -p1
%patch23325 -p1
%patch23326 -p1
%patch23327 -p1
%patch23328 -p1
%patch23329 -p1
%patch23330 -p1
%patch23331 -p1 -E
%patch23332 -p1
%patch23333 -p1
%patch23334 -p1
%patch23335 -p1
%patch23336 -p1
%patch23337 -p1
%patch23338 -p1
%patch23339 -p1
%patch23340 -p1
%patch23341 -p1
%patch23342 -p1
%patch23343 -p1
%patch23344 -p1
%patch23345 -p1
%patch23346 -p1
%patch23347 -p1
%patch23348 -p1
%patch23349 -p1
%patch23350 -p1
%patch23351 -p1
%patch23352 -p1
%patch23353 -p1
%patch23354 -p1
%patch23355 -p1
%patch23356 -p1
%patch23357 -p1
%patch23358 -p1 -E
%patch23359 -p1
%patch23360 -p1
%patch23361 -p1
%patch23362 -p1
%patch23363 -p1
%patch23364 -p1
%patch23365 -p1
%patch23366 -p1
%patch23367 -p1
%patch23368 -p1
%patch23369 -p1
%patch23370 -p1
%patch23371 -p1
%patch23372 -p1
%patch23373 -p1
%patch23374 -p1
%patch23375 -p1
%patch23376 -p1
%patch23377 -p1
%patch23378 -p1
%patch23379 -p1
%patch23380 -p1
%patch23381 -p1
%patch23382 -p1
%patch23383 -p1
%patch23384 -p1
%patch23385 -p1
%patch23386 -p1
%patch23387 -p1 -E
%patch23388 -p1
%patch23389 -p1
%patch23390 -p1
%patch23391 -p1
%patch23392 -p1
%patch23393 -p1
%patch23394 -p1
%patch23395 -p1
%patch23396 -p1
%patch23397 -p1
%patch23398 -p1
%patch23399 -p1
%patch23400 -p1
%patch23401 -p1
%patch23402 -p1
%patch23403 -p1
%patch23404 -p1
%patch23405 -p1
%patch23406 -p1
%patch23407 -p1
%patch23408 -p1
%patch23409 -p1
%patch23410 -p1
%patch23411 -p1
%patch23412 -p1
%patch23413 -p1
%patch23414 -p1
%patch23415 -p1
%patch23416 -p1
%patch23417 -p1
%patch23418 -p1
%patch23419 -p1
%patch23420 -p1
%patch23421 -p1
%patch23422 -p1
%patch23423 -p1
%patch23424 -p1
%patch23425 -p1
%patch23426 -p1
%patch23427 -p1
%patch23428 -p1
%patch23429 -p1
%patch23430 -p1
%patch23431 -p1
%patch23432 -p1
%patch23433 -p1
%patch23434 -p1
%patch23435 -p1
%patch23436 -p1
%patch23437 -p1
%patch23438 -p1
%patch23439 -p1
%patch23440 -p1
%patch23441 -p1
%patch23442 -p1
%patch23443 -p1
%patch23444 -p1
%patch23445 -p1
%patch23446 -p1
%patch23447 -p1
%patch23448 -p1
%patch23449 -p1
%patch23450 -p1
%patch23451 -p1
%patch23452 -p1
%patch23453 -p1
%patch23454 -p1
%patch23455 -p1
%patch23456 -p1
%patch23457 -p1 -E
%patch23458 -p1
%patch23459 -p1
%patch23460 -p1
%patch23461 -p1
%patch23462 -p1
%patch23463 -p1
%patch23464 -p1
%patch23465 -p1
%patch23466 -p1
%patch23467 -p1
%patch23468 -p1
%patch23469 -p1
%patch23470 -p1
%patch23471 -p1
%patch23472 -p1
%patch23473 -p1
%patch23474 -p1
%patch23475 -p1
%patch23476 -p1
%patch23477 -p1
%patch23478 -p1
%patch23479 -p1
%patch23480 -p1
%patch23481 -p1
%patch23482 -p1
%patch23483 -p1
%patch23484 -p1
%patch23485 -p1
%patch23486 -p1
%patch23487 -p1
%patch23488 -p1
%patch23489 -p1
%patch23490 -p1 -E
%patch23491 -p1
%patch23492 -p1
%patch23493 -p1
%patch23494 -p1
%patch23495 -p1
%patch23496 -p1
%patch23497 -p1
%patch23498 -p1
%patch23499 -p1
%patch23500 -p1
%patch23501 -p1
%patch23502 -p1
%patch23503 -p1
%patch23504 -p1
%patch23505 -p1
%patch23506 -p1
%patch23507 -p1
%patch23508 -p1
%patch23509 -p1
%patch23510 -p1
%patch23511 -p1
%patch23512 -p1
%patch23513 -p1
%patch23514 -p1
%patch23515 -p1
%patch23516 -p1
%patch23517 -p1
%patch23518 -p1
%patch23519 -p1
%patch23520 -p1
%patch23521 -p1
%patch23522 -p1
%patch23523 -p1
%patch23524 -p1
%patch23525 -p1
%patch23526 -p1
%patch23527 -p1
%patch23528 -p1
%patch23529 -p1
%patch23530 -p1
%patch23531 -p1
%patch23532 -p1
%patch23533 -p1
%patch23534 -p1
%patch23535 -p1
%patch23536 -p1
%patch23537 -p1
%patch23538 -p1
%patch23539 -p1
%patch23540 -p1
%patch23541 -p1
%patch23542 -p1
%patch23543 -p1
%patch23544 -p1
%patch23545 -p1
%patch23546 -p1
%patch23547 -p1
%patch23548 -p1
%patch23549 -p1
%patch23550 -p1
%patch23551 -p1
%patch23552 -p1
%patch23553 -p1
%patch23554 -p1
%patch23555 -p1
%patch23556 -p1
%patch23557 -p1
%patch23558 -p1
%patch23559 -p1
%patch23560 -p1
%patch23561 -p1
%patch23562 -p1
%patch23563 -p1
%patch23564 -p1
%patch23565 -p1
%patch23566 -p1
%patch23567 -p1
%patch23568 -p1
%patch23569 -p1
%patch23570 -p1
%patch23571 -p1
%patch23572 -p1
%patch23573 -p1
%patch23574 -p1
%patch23575 -p1
%patch23576 -p1
%patch23577 -p1
%patch23578 -p1
%patch23579 -p1
%patch23580 -p1
%patch23581 -p1
%patch23582 -p1
%patch23583 -p1
%patch23584 -p1
%patch23585 -p1
%patch23586 -p1
%patch23587 -p1
%patch23588 -p1
%patch23589 -p1
%patch23590 -p1
%patch23591 -p1
%patch23592 -p1
%patch23593 -p1
%patch23594 -p1
%patch23595 -p1
%patch23596 -p1
%patch23597 -p1
%patch23598 -p1
%patch23599 -p1 -E
%patch23600 -p1
%patch23601 -p1
%patch23602 -p1
%patch23603 -p1
%patch23604 -p1
%patch23605 -p1
%patch23606 -p1
%patch23607 -p1
%patch23608 -p1
%patch23609 -p1
%patch23610 -p1
%patch23611 -p1
%patch23612 -p1
%patch23613 -p1
%patch23614 -p1
%patch23615 -p1
%patch23616 -p1
%patch23617 -p1
%patch23618 -p1
%patch23619 -p1
%patch23620 -p1
%patch23621 -p1
%patch23622 -p1
%patch23623 -p1
%patch23624 -p1
%patch23625 -p1
%patch23626 -p1
%patch23627 -p1
%patch23628 -p1
%patch23629 -p1
%patch23630 -p1
%patch23631 -p1
%patch23632 -p1
%patch23633 -p1
%patch23634 -p1
%patch23635 -p1
%patch23636 -p1
%patch23637 -p1
%patch23638 -p1
%patch23639 -p1
%patch23640 -p1
%patch23641 -p1
%patch23642 -p1
%patch23643 -p1
%patch23644 -p1
%patch23645 -p1
%patch23646 -p1
%patch23647 -p1
%patch23648 -p1
%patch23649 -p1
%patch23650 -p1
%patch23651 -p1 -E
%patch23652 -p1
%patch23653 -p1
%patch23654 -p1
%patch23655 -p1
%patch23656 -p1
%patch23657 -p1
%patch23658 -p1
%patch23659 -p1
%patch23660 -p1
%patch23661 -p1
%patch23662 -p1
%patch23663 -p1
%patch23664 -p1
%patch23665 -p1
%patch23666 -p1
%patch23667 -p1
%patch23668 -p1
%patch23669 -p1
%patch23671 -p1
%patch23672 -p1
%patch23673 -p1
%patch23674 -p1
%patch23675 -p1
%patch23676 -p1
%patch23677 -p1
%patch23678 -p1
%patch23679 -p1
%patch23680 -p1
%patch23681 -p1
%patch23682 -p1
%patch23683 -p1
%patch23684 -p1
%patch23685 -p1
%patch23686 -p1
%patch23687 -p1
%patch23688 -p1
%patch23689 -p1
%patch23690 -p1
%patch23691 -p1
%patch23692 -p1
%patch23693 -p1
%patch23694 -p1
%patch23695 -p1
%patch23696 -p1
%patch23697 -p1
%patch23698 -p1
%patch23699 -p1
%patch23700 -p1
%patch23701 -p1
%patch23702 -p1
%patch23703 -p1
%patch23704 -p1
%patch23705 -p1
%patch23706 -p1
%patch23707 -p1
%patch23708 -p1
%patch23709 -p1
%patch23710 -p1
%patch23711 -p1
%patch23712 -p1
%patch23713 -p1
%patch23714 -p1
%patch23715 -p1
%patch23716 -p1
%patch23717 -p1
%patch23718 -p1
%patch23719 -p1
%patch23720 -p1
%patch23721 -p1
%patch23722 -p1
%patch23723 -p1
%patch23724 -p1
%patch23725 -p1
%patch23726 -p1
%patch23727 -p1
%patch23728 -p1
%patch23729 -p1
%patch23730 -p1
%patch23731 -p1
%patch23732 -p1
%patch23733 -p1
%patch23734 -p1
%patch23735 -p1
%patch23736 -p1
%patch23737 -p1
%patch23738 -p1
%patch23739 -p1
%patch23740 -p1
%patch23741 -p1
%patch23742 -p1
%patch23743 -p1
%patch23744 -p1
%patch23745 -p1
%patch23746 -p1
%patch23747 -p1
%patch23748 -p1
%patch23749 -p1
%patch23750 -p1
%patch23751 -p1
%patch23752 -p1
%patch23753 -p1
%patch23754 -p1
%patch23755 -p1
%patch23756 -p1
%patch23757 -p1
%patch23758 -p1
%patch23759 -p1
%patch23760 -p1
%patch23761 -p1
%patch23762 -p1
%patch23763 -p1
%patch23764 -p1
%patch23765 -p1
%patch23766 -p1
%patch23767 -p1
%patch23768 -p1
%patch23769 -p1
%patch23770 -p1
%patch23771 -p1
%patch23772 -p1
%patch23773 -p1
%patch23774 -p1
%patch23775 -p1
%patch23776 -p1
%patch23777 -p1
%patch23778 -p1
%patch23779 -p1
%patch23780 -p1
%patch23781 -p1
%patch23782 -p1
%patch23783 -p1
%patch23784 -p1
%patch23785 -p1
%patch23786 -p1
%patch23787 -p1
%patch23788 -p1
%patch23789 -p1
%patch23790 -p1
%patch23791 -p1
%patch23792 -p1
%patch23793 -p1
%patch23794 -p1
%patch23795 -p1
%patch23796 -p1
%patch23797 -p1
%patch23798 -p1
%patch23799 -p1
%patch23800 -p1
%patch23801 -p1
%patch23802 -p1
%patch23803 -p1
%patch23804 -p1
%patch23805 -p1
%patch23806 -p1
%patch23807 -p1
%patch23808 -p1
%patch23809 -p1
%patch23810 -p1
%patch23811 -p1
%patch23812 -p1
%patch23813 -p1
%patch23814 -p1
%patch23815 -p1
%patch23816 -p1
%patch23817 -p1
%patch23818 -p1
%patch23819 -p1
%patch23820 -p1
%patch23821 -p1
%patch23822 -p1
%patch23823 -p1
%patch23824 -p1
%patch23825 -p1
%patch23826 -p1
%patch23827 -p1
%patch23828 -p1
%patch23829 -p1
%patch23830 -p1
%patch23831 -p1
%patch23832 -p1
%patch23833 -p1
%patch23834 -p1
%patch23835 -p1
%patch23836 -p1
%patch23837 -p1
%patch23838 -p1
%patch23839 -p1
%patch23840 -p1
%patch23841 -p1
%patch23842 -p1
%patch23843 -p1
%patch23844 -p1 -E
%patch23845 -p1 -E
%patch23846 -p1
%patch23847 -p1
%patch23848 -p1
%patch23849 -p1
%patch23850 -p1
%patch23851 -p1
%patch23852 -p1
%patch23853 -p1
%patch23854 -p1
%patch23855 -p1
%patch23856 -p1
%patch23857 -p1
%patch23858 -p1
%patch23859 -p1
%patch23860 -p1
%patch23861 -p1
%patch23862 -p1
%patch23863 -p1
%patch23864 -p1
%patch23865 -p1
%patch23866 -p1
%patch23867 -p1
%patch23868 -p1
%patch23869 -p1
%patch23870 -p1
%patch23871 -p1
%patch23872 -p1
%patch23873 -p1
%patch23874 -p1
%patch23875 -p1
%patch23876 -p1
%patch23877 -p1
%patch23878 -p1
%patch23879 -p1
%patch23880 -p1
%patch23881 -p1
%patch23882 -p1
%patch23883 -p1
%patch23884 -p1
%patch23885 -p1
%patch23886 -p1
%patch23887 -p1
%patch23888 -p1
%patch23889 -p1
%patch23890 -p1
%patch23891 -p1 -E
%patch23892 -p1
%patch23893 -p1
%patch23894 -p1
%patch23895 -p1
%patch23896 -p1
%patch23897 -p1
%patch23898 -p1
%patch23899 -p1
%patch23900 -p1
%patch23901 -p1
%patch23902 -p1
%patch23903 -p1
%patch23904 -p1
%patch23905 -p1
%patch23906 -p1
%patch23907 -p1
%patch23908 -p1
%patch23909 -p1
%patch23910 -p1
%patch23911 -p1
%patch23912 -p1
%patch23913 -p1
%patch23914 -p1
%patch23915 -p1
%patch23916 -p1
%patch23917 -p1
%patch23918 -p1
%patch23919 -p1
%patch23920 -p1
%patch23921 -p1
%patch23922 -p1
%patch23923 -p1
%patch23924 -p1
%patch23925 -p1
%patch23926 -p1
%patch23927 -p1
%patch23928 -p1
%patch23929 -p1
%patch23930 -p1
%patch23931 -p1
%patch23932 -p1
%patch23933 -p1
%patch23934 -p1
%patch23935 -p1
%patch23936 -p1
%patch23937 -p1
%patch23938 -p1
%patch23939 -p1
%patch23940 -p1
%patch23941 -p1
%patch23942 -p1
%patch23943 -p1
%patch23944 -p1
%patch23945 -p1
%patch23946 -p1
%patch23947 -p1
%patch23948 -p1
%patch23949 -p1
%patch23950 -p1
%patch23951 -p1
%patch23952 -p1
%patch23953 -p1
%patch23954 -p1
%patch23955 -p1
%patch23956 -p1
%patch23957 -p1
%patch23958 -p1
%patch23959 -p1
%patch23960 -p1
%patch23961 -p1
%patch23962 -p1
%patch23963 -p1
%patch23964 -p1
%patch23965 -p1
%patch23966 -p1
%patch23967 -p1
%patch23968 -p1
%patch23969 -p1
%patch23970 -p1
%patch23971 -p1
%patch23972 -p1
%patch23973 -p1
%patch23974 -p1
%patch23975 -p1
%patch23976 -p1
%patch23977 -p1
%patch23978 -p1
%patch23979 -p1
%patch23980 -p1
%patch23981 -p1
%patch23982 -p1
%patch23983 -p1
%patch23984 -p1
%patch23985 -p1
%patch23986 -p1
%patch23987 -p1
%patch23988 -p1
%patch23989 -p1
%patch23990 -p1
%patch23991 -p1
%patch23992 -p1
%patch23993 -p1
%patch23994 -p1
%patch23995 -p1
%patch23996 -p1
%patch23997 -p1
%patch23998 -p1
%patch23999 -p1
%patch24000 -p1
%patch24001 -p1
%patch24002 -p1
%patch24003 -p1
%patch24004 -p1
%patch24005 -p1
%patch24006 -p1
%patch24007 -p1
%patch24008 -p1
%patch24009 -p1
%patch24010 -p1
%patch24011 -p1
%patch24012 -p1
%patch24013 -p1
%patch24014 -p1
%patch24015 -p1
%patch24016 -p1
%patch24017 -p1
%patch24018 -p1
%patch24019 -p1
%patch24020 -p1
%patch24021 -p1
%patch24022 -p1
%patch24023 -p1
%patch24024 -p1
%patch24025 -p1
%patch24026 -p1
%patch24027 -p1
%patch24028 -p1
%patch24029 -p1
%patch24030 -p1
%patch24031 -p1
%patch24032 -p1
%patch24033 -p1
%patch24034 -p1
%patch24035 -p1
%patch24036 -p1
%patch24037 -p1
%patch24038 -p1
%patch24039 -p1
%patch24040 -p1
%patch24041 -p1
%patch24042 -p1 -E
%patch24043 -p1
%patch24044 -p1
%patch24045 -p1
%patch24046 -p1
%patch24047 -p1
%patch24048 -p1
%patch24049 -p1
%patch24050 -p1
%patch24051 -p1
%patch24052 -p1
%patch24053 -p1
%patch24054 -p1
%patch24055 -p1
%patch24056 -p1
%patch24057 -p1
%patch24058 -p1
%patch24059 -p1
%patch24060 -p1
%patch24061 -p1
%patch24062 -p1
%patch24063 -p1
%patch24064 -p1
%patch24065 -p1
%patch24066 -p1
%patch24067 -p1
%patch24068 -p1
%patch24069 -p1
%patch24070 -p1
%patch24071 -p1
%patch24072 -p1
%patch24073 -p1
%patch24074 -p1
%patch24075 -p1
%patch24076 -p1
%patch24077 -p1
%patch24078 -p1
%patch24079 -p1
%patch24080 -p1
%patch24081 -p1
%patch24082 -p1
%patch24083 -p1
%patch24084 -p1
%patch24085 -p1
%patch24086 -p1
%patch24087 -p1
%patch24088 -p1
%patch24089 -p1
%patch24090 -p1
%patch24091 -p1
%patch24092 -p1
%patch24093 -p1
%patch24094 -p1
%patch24095 -p1
%patch24096 -p1
%patch24097 -p1
%patch24098 -p1
%patch24099 -p1
%patch24100 -p1
%patch24101 -p1
%patch24102 -p1
%patch24103 -p1
%patch24104 -p1
%patch24105 -p1
%patch24106 -p1
%patch24107 -p1
%patch24108 -p1
%patch24109 -p1
%patch24110 -p1
%patch24111 -p1
%patch24112 -p1
%patch24113 -p1
%patch24114 -p1
%patch24115 -p1
%patch24116 -p1
%patch24117 -p1
%patch24118 -p1
%patch24119 -p1
%patch24120 -p1
%patch24121 -p1
%patch24122 -p1
%patch24123 -p1
%patch24124 -p1
%patch24125 -p1
%patch24126 -p1
%patch24127 -p1
%patch24128 -p1
%patch24129 -p1
%patch24130 -p1
%patch24131 -p1
%patch24132 -p1
%patch24133 -p1
%patch24134 -p1
%patch24135 -p1
%patch24136 -p1
%patch24137 -p1
%patch24138 -p1
%patch24139 -p1
%patch24140 -p1
%patch24141 -p1
%patch24142 -p1 -E
%patch24143 -p1
%patch24144 -p1
%patch24145 -p1
%patch24146 -p1
%patch24147 -p1
%patch24148 -p1
%patch24149 -p1
%patch24150 -p1
%patch24151 -p1
%patch24152 -p1
%patch24153 -p1
%patch24154 -p1
%patch24155 -p1
%patch24156 -p1
%patch24157 -p1
%patch24158 -p1
%patch24159 -p1
%patch24160 -p1
%patch24161 -p1
%patch24162 -p1
%patch24163 -p1
%patch24164 -p1
%patch24165 -p1
%patch24166 -p1
%patch24167 -p1
%patch24168 -p1
%patch24169 -p1
%patch24170 -p1
%patch24171 -p1
%patch24172 -p1
%patch24173 -p1
%patch24174 -p1
%patch24175 -p1
%patch24176 -p1
%patch24177 -p1
%patch24178 -p1
%patch24179 -p1
%patch24180 -p1
%patch24181 -p1
%patch24182 -p1
%patch24183 -p1
%patch24184 -p1
%patch24185 -p1
%patch24186 -p1
%patch24187 -p1
%patch24188 -p1
%patch24189 -p1
%patch24190 -p1
%patch24191 -p1
%patch24192 -p1
%patch24193 -p1
%patch24194 -p1
%patch24195 -p1
%patch24196 -p1
%patch24197 -p1
%patch24198 -p1
%patch24199 -p1
%patch24200 -p1
%patch24201 -p1
%patch24202 -p1
%patch24203 -p1
%patch24204 -p1
%patch24205 -p1
%patch24206 -p1
%patch24207 -p1
%patch24208 -p1
%patch24209 -p1
%patch24210 -p1
%patch24211 -p1
%patch24212 -p1
%patch24213 -p1
%patch24214 -p1
%patch24215 -p1
%patch24216 -p1
%patch24217 -p1
%patch24218 -p1
%patch24219 -p1
%patch24220 -p1
%patch24221 -p1
%patch24222 -p1
%patch24223 -p1
%patch24224 -p1
%patch24225 -p1
%patch24226 -p1
%patch24227 -p1
%patch24228 -p1
%patch24229 -p1
%patch24230 -p1
%patch24231 -p1
%patch24232 -p1
%patch24233 -p1
%patch24234 -p1
%patch24235 -p1
%patch24236 -p1
%patch24237 -p1
%patch24238 -p1
%patch24239 -p1
%patch24240 -p1
%patch24241 -p1
%patch24242 -p1
%patch24243 -p1
%patch24244 -p1
%patch24245 -p1
%patch24246 -p1
%patch24247 -p1
%patch24248 -p1
%patch24249 -p1
%patch24250 -p1
%patch24251 -p1
%patch24252 -p1
%patch24253 -p1
%patch24254 -p1
%patch24255 -p1
%patch24256 -p1
%patch24257 -p1
%patch24258 -p1
%patch24259 -p1
%patch24260 -p1
%patch24261 -p1
%patch24262 -p1
%patch24263 -p1
%patch24264 -p1
%patch24265 -p1
%patch24266 -p1
%patch24267 -p1
%patch24268 -p1
%patch24269 -p1
%patch24270 -p1
%patch24271 -p1
%patch24272 -p1
%patch24273 -p1
%patch24274 -p1
%patch24275 -p1
%patch24276 -p1
%patch24277 -p1
%patch24278 -p1
%patch24279 -p1
%patch24280 -p1
%patch24281 -p1
%patch24282 -p1
%patch24283 -p1
%patch24284 -p1
%patch24285 -p1
%patch24286 -p1
%patch24287 -p1
%patch24288 -p1
%patch24289 -p1
%patch24290 -p1
%patch24291 -p1
%patch24292 -p1
%patch24293 -p1
%patch24294 -p1
%patch24295 -p1
%patch24296 -p1
%patch24297 -p1
%patch24298 -p1
%patch24299 -p1
%patch24300 -p1
%patch24301 -p1
%patch24302 -p1
%patch24303 -p1 -E
%patch24304 -p1
%patch24305 -p1
%patch24306 -p1
%patch24307 -p1
%patch24308 -p1
%patch24309 -p1
%patch24310 -p1
%patch24313 -p1
%patch24314 -p1
%patch24315 -p1
%patch24316 -p1
%patch24317 -p1
%patch24318 -p1
%patch24319 -p1
%patch24320 -p1
%patch24321 -p1
%patch24322 -p1
%patch24323 -p1
%patch24324 -p1
%patch24325 -p1
%patch24326 -p1
%patch24327 -p1
%patch24328 -p1
%patch24329 -p1
%patch24330 -p1
%patch24331 -p1
%patch24332 -p1
%patch24333 -p1
%patch24334 -p1
%patch24335 -p1
%patch24336 -p1
%patch24337 -p1
%patch24338 -p1
%patch24339 -p1
%patch24340 -p1
%patch24341 -p1
%patch24342 -p1
%patch24343 -p1
%patch24344 -p1
%patch24345 -p1
%patch24346 -p1
%patch24347 -p1
%patch24348 -p1
%patch24349 -p1
%patch24350 -p1
%patch24351 -p1
%patch24352 -p1
%patch24353 -p1
%patch24354 -p1
%patch24355 -p1
%patch24356 -p1
%patch24357 -p1
%patch24358 -p1
%patch24359 -p1
%patch24360 -p1
%patch24361 -p1
%patch24362 -p1
%patch24363 -p1
%patch24364 -p1
%patch24365 -p1
%patch24366 -p1
%patch24367 -p1
%patch24368 -p1
%patch24369 -p1
%patch24370 -p1
%patch24371 -p1
%patch24372 -p1
%patch24373 -p1
%patch24374 -p1
%patch24375 -p1
%patch24376 -p1
%patch24377 -p1
%patch24378 -p1
%patch24379 -p1
%patch24380 -p1
%patch24381 -p1
%patch24382 -p1
%patch24383 -p1
%patch24384 -p1
%patch24385 -p1
%patch24386 -p1
%patch24387 -p1
%patch24388 -p1
%patch24389 -p1
%patch24390 -p1
%patch24391 -p1
%patch24392 -p1
%patch24393 -p1
%patch24394 -p1
%patch24395 -p1
%patch24396 -p1
%patch24397 -p1
%patch24398 -p1
%patch24399 -p1
%patch24400 -p1
%patch24401 -p1
%patch24402 -p1
%patch24403 -p1
%patch24404 -p1
%patch24405 -p1
%patch24406 -p1
%patch24407 -p1
%patch24408 -p1
%patch24409 -p1
%patch24410 -p1
%patch24411 -p1
%patch24412 -p1
%patch24413 -p1
%patch24414 -p1
%patch24415 -p1
%patch24416 -p1
%patch24417 -p1
%patch24418 -p1
%patch24419 -p1
%patch24420 -p1
%patch24421 -p1
%patch24422 -p1
%patch24423 -p1
%patch24424 -p1
%patch24425 -p1
%patch24426 -p1
%patch24427 -p1
%patch24428 -p1
%patch24429 -p1
%patch24430 -p1
%patch24431 -p1
%patch24432 -p1
%patch24433 -p1
%patch24434 -p1
%patch24435 -p1
%patch24436 -p1
%patch24437 -p1
%patch24438 -p1
%patch24439 -p1
%patch24440 -p1
%patch24441 -p1
%patch24442 -p1
%patch24443 -p1
%patch24444 -p1
%patch24445 -p1
%patch24446 -p1
%patch24447 -p1
%patch24448 -p1
%patch24449 -p1
%patch24450 -p1
%patch24451 -p1
%patch24452 -p1
%patch24453 -p1
%patch24454 -p1
%patch24455 -p1
%patch24456 -p1
%patch24457 -p1
%patch24458 -p1
%patch24459 -p1
%patch24460 -p1
%patch24461 -p1
%patch24462 -p1
%patch24463 -p1
%patch24464 -p1
%patch24465 -p1
%patch24466 -p1
%patch24467 -p1
%patch24468 -p1
%patch24469 -p1
%patch24470 -p1
%patch24471 -p1
%patch24472 -p1
%patch24473 -p1
%patch24474 -p1
%patch24475 -p1
%patch24476 -p1
%patch24477 -p1
%patch24478 -p1
%patch24479 -p1
%patch24480 -p1
%patch24481 -p1
%patch24482 -p1
%patch24483 -p1
%patch24484 -p1
%patch24485 -p1
%patch24486 -p1
%patch24487 -p1
%patch24488 -p1
%patch24489 -p1
%patch24490 -p1
%patch24491 -p1
%patch24492 -p1
%patch24493 -p1
%patch24494 -p1
%patch24495 -p1
%patch24496 -p1
%patch24497 -p1
%patch24498 -p1
%patch24499 -p1
%patch24500 -p1
%patch24501 -p1
%patch24502 -p1
%patch24503 -p1
%patch24504 -p1
%patch24505 -p1
%patch24506 -p1
%patch24507 -p1
%patch24508 -p1
%patch24509 -p1
%patch24510 -p1
%patch24511 -p1
%patch24512 -p1
%patch24513 -p1
%patch24514 -p1
%patch24515 -p1
%patch24516 -p1
%patch24517 -p1
%patch24518 -p1
%patch24519 -p1
%patch24520 -p1
%patch24521 -p1
%patch24522 -p1
%patch24523 -p1
%patch24524 -p1
%patch24525 -p1
%patch24526 -p1
%patch24527 -p1
%patch24528 -p1
%patch24529 -p1
%patch24530 -p1
%patch24531 -p1
%patch24532 -p1
%patch24533 -p1
%patch24534 -p1
%patch24535 -p1
%patch24536 -p1
%patch24537 -p1
%patch24538 -p1
%patch24539 -p1
%patch24540 -p1
%patch24541 -p1
%patch24542 -p1
%patch24543 -p1
%patch24544 -p1
%patch24545 -p1
%patch24546 -p1
%patch24547 -p1
%patch24548 -p1
%patch24549 -p1
%patch24550 -p1
%patch24551 -p1
%patch24552 -p1
%patch24553 -p1
%patch24554 -p1
%patch24555 -p1
%patch24556 -p1
%patch24557 -p1
%patch24558 -p1
%patch24559 -p1
%patch24560 -p1
%patch24561 -p1
%patch24562 -p1
%patch24563 -p1
%patch24564 -p1
%patch24565 -p1
%patch24566 -p1
%patch24567 -p1
%patch24568 -p1
%patch24569 -p1
%patch24570 -p1
%patch24571 -p1
%patch24572 -p1
%patch24573 -p1
%patch24574 -p1
%patch24575 -p1
%patch24576 -p1
%patch24577 -p1
%patch24578 -p1
%patch24579 -p1
%patch24580 -p1
%patch24581 -p1
%patch24582 -p1
%patch24583 -p1
%patch24584 -p1
%patch24585 -p1
%patch24586 -p1
%patch24587 -p1
%patch24588 -p1
%patch24589 -p1
%patch24590 -p1
%patch24591 -p1
%patch24592 -p1
%patch24593 -p1
%patch24594 -p1
%patch24595 -p1
%patch24596 -p1
%patch24597 -p1
%patch24598 -p1
%patch24599 -p1
%patch24600 -p1
%patch24601 -p1
%patch24602 -p1
%patch24603 -p1
%patch24604 -p1
%patch24605 -p1
%patch24606 -p1
%patch24607 -p1
%patch24608 -p1
%patch24609 -p1
%patch24610 -p1
%patch24611 -p1
%patch24612 -p1
%patch24613 -p1
%patch24614 -p1
%patch24615 -p1
%patch24616 -p1
%patch24617 -p1
%patch24618 -p1
%patch24619 -p1
%patch24620 -p1
%patch24621 -p1
%patch24622 -p1
%patch24623 -p1
%patch24624 -p1
%patch24626 -p1
%patch24627 -p1
%patch24628 -p1
%patch24629 -p1
%patch24630 -p1
%patch24631 -p1
%patch24632 -p1
%patch24633 -p1
%patch24634 -p1
%patch24635 -p1
%patch24636 -p1
%patch24637 -p1
%patch24638 -p1
%patch24639 -p1
%patch24640 -p1
%patch24641 -p1
%patch24642 -p1
%patch24643 -p1
%patch24644 -p1
%patch24645 -p1
%patch24646 -p1
%patch24647 -p1
%patch24648 -p1
%patch24649 -p1
%patch24650 -p1
%patch24651 -p1
%patch24652 -p1
%patch24653 -p1
%patch24654 -p1
%patch24655 -p1
%patch24656 -p1
%patch24657 -p1
%patch24658 -p1
%patch24659 -p1
%patch24660 -p1
%patch24661 -p1
%patch24662 -p1
%patch24663 -p1
%patch24664 -p1
%patch24665 -p1
%patch24666 -p1
%patch24667 -p1
%patch24668 -p1
%patch24669 -p1
%patch24670 -p1
%patch24671 -p1
%patch24672 -p1
%patch24673 -p1
%patch24674 -p1
%patch24675 -p1
%patch24676 -p1
%patch24677 -p1
%patch24678 -p1
%patch24679 -p1
%patch24680 -p1
%patch24681 -p1
%patch24682 -p1
%patch24683 -p1
%patch24684 -p1
%patch24685 -p1
%patch24686 -p1
%patch24687 -p1
%patch24688 -p1
%patch24689 -p1
%patch24690 -p1
%patch24691 -p1
%patch24692 -p1
%patch24693 -p1
%patch24694 -p1
%patch24695 -p1
%patch24696 -p1
%patch24697 -p1
%patch24698 -p1
%patch24699 -p1
%patch24700 -p1
%patch24701 -p1
%patch24702 -p1
%patch24703 -p1
%patch24704 -p1
%patch24705 -p1
%patch24706 -p1
%patch24707 -p1
%patch24708 -p1
%patch24709 -p1
%patch24710 -p1
%patch24711 -p1
%patch24712 -p1
%patch24713 -p1
%patch24714 -p1
%patch24715 -p1
%patch24716 -p1
%patch24717 -p1
%patch24718 -p1
%patch24719 -p1
%patch24720 -p1
%patch24721 -p1
%patch24722 -p1
%patch24723 -p1
%patch24724 -p1
%patch24725 -p1
%patch24726 -p1
%patch24727 -p1
%patch24728 -p1
%patch24729 -p1
%patch24730 -p1
%patch24731 -p1
%patch24732 -p1
%patch24733 -p1
%patch24734 -p1
%patch24735 -p1
%patch24736 -p1
%patch24737 -p1
%patch24738 -p1
%patch24739 -p1
%patch24740 -p1
%patch24741 -p1
%patch24742 -p1
%patch24743 -p1
%patch24744 -p1
%patch24745 -p1
%patch24746 -p1
%patch24747 -p1
%patch24748 -p1
%patch24749 -p1
%patch24750 -p1
%patch24751 -p1
%patch24752 -p1
%patch24753 -p1
%patch24754 -p1
%patch24755 -p1
%patch24756 -p1
%patch24757 -p1
%patch24758 -p1
%patch24759 -p1
%patch24760 -p1
%patch24761 -p1
%patch24762 -p1
%patch24763 -p1
%patch24764 -p1
%patch24765 -p1
%patch24766 -p1
%patch24767 -p1
%patch24768 -p1
%patch24769 -p1
%patch24770 -p1
%patch24771 -p1
%patch24772 -p1
%patch24773 -p1
%patch24774 -p1
%patch24775 -p1
%patch24776 -p1
%patch24777 -p1
%patch24778 -p1
%patch24779 -p1
%patch24780 -p1
%patch24781 -p1
%patch24782 -p1
%patch24783 -p1
%patch24784 -p1
%patch24785 -p1
%patch24786 -p1
%patch24787 -p1
%patch24788 -p1
%patch24789 -p1
%patch24790 -p1
%patch24791 -p1
%patch24792 -p1
%patch24793 -p1
%patch24794 -p1
%patch24795 -p1
%patch24796 -p1
%patch24797 -p1
%patch24798 -p1
%patch24799 -p1
%patch24800 -p1
%patch24801 -p1
%patch24802 -p1
%patch24803 -p1
%patch24804 -p1
%patch24805 -p1
%patch24806 -p1
%patch24807 -p1
%patch24808 -p1
%patch24809 -p1
%patch24810 -p1
%patch24811 -p1
%patch24812 -p1
%patch24813 -p1
%patch24814 -p1
%patch24815 -p1
%patch24816 -p1
%patch24817 -p1
%patch24818 -p1
%patch24819 -p1
%patch24820 -p1
%patch24821 -p1
%patch24822 -p1
%patch24823 -p1
%patch24824 -p1
%patch24825 -p1
%patch24826 -p1
%patch24827 -p1
%patch24828 -p1
%patch24829 -p1
%patch24830 -p1
%patch24831 -p1
%patch24832 -p1
%patch24833 -p1
%patch24834 -p1
%patch24835 -p1
%patch24836 -p1
%patch24837 -p1
%patch24838 -p1
%patch24839 -p1
%patch24840 -p1
%patch24841 -p1
%patch24842 -p1
%patch24843 -p1
%patch24844 -p1
%patch24845 -p1
%patch24846 -p1
%patch24847 -p1
%patch24848 -p1
%patch24849 -p1
%patch24850 -p1
%patch24851 -p1
%patch24852 -p1
%patch24853 -p1
%patch24854 -p1
%patch24855 -p1
%patch24856 -p1
%patch24857 -p1
%patch24858 -p1
%patch24859 -p1
%patch24860 -p1
%patch24861 -p1
%patch24862 -p1
%patch24863 -p1
%patch24864 -p1
%patch24865 -p1
%patch24866 -p1
%patch24867 -p1
%patch24868 -p1
%patch24869 -p1
%patch24870 -p1
%patch24871 -p1
%patch24872 -p1
%patch24873 -p1
%patch24874 -p1
%patch24875 -p1
%patch24876 -p1
%patch24877 -p1
%patch24878 -p1
%patch24879 -p1
%patch24880 -p1
%patch24881 -p1
%patch24882 -p1
%patch24883 -p1
%patch24884 -p1
%patch24885 -p1
%patch24886 -p1
%patch24887 -p1
%patch24888 -p1
%patch24889 -p1
%patch24890 -p1
%patch24891 -p1
%patch24892 -p1
%patch24893 -p1
%patch24894 -p1
%patch24895 -p1
%patch24896 -p1
%patch24897 -p1
%patch24898 -p1
%patch24899 -p1
%patch24900 -p1
%patch24901 -p1
%patch24902 -p1
%patch24903 -p1
%patch24904 -p1
%patch24905 -p1
%patch24906 -p1
%patch24907 -p1
%patch24908 -p1
%patch24909 -p1
%patch24910 -p1
%patch24911 -p1
%patch24912 -p1
%patch24913 -p1
%patch24914 -p1
%patch24915 -p1
%patch24916 -p1
%patch24917 -p1
%patch24918 -p1
%patch24919 -p1
%patch24920 -p1
%patch24921 -p1
%patch24922 -p1
%patch24923 -p1
%patch24924 -p1
%patch24925 -p1
%patch24926 -p1
%patch24927 -p1
%patch24928 -p1
%patch24929 -p1
%patch24930 -p1
%patch24931 -p1
%patch24932 -p1
%patch24933 -p1
%patch24934 -p1
%patch24935 -p1
%patch24936 -p1
%patch24937 -p1
%patch24938 -p1
%patch24939 -p1
%patch24940 -p1
%patch24941 -p1
%patch24942 -p1
%patch24943 -p1
%patch24944 -p1
%patch24945 -p1
%patch24946 -p1
%patch24947 -p1
%patch24948 -p1
%patch24949 -p1
%patch24950 -p1
%patch24951 -p1
%patch24952 -p1
%patch24953 -p1
%patch24954 -p1
%patch24955 -p1
%patch24956 -p1
%patch24957 -p1
%patch24958 -p1
%patch24959 -p1
%patch24960 -p1
%patch24961 -p1
%patch24962 -p1
%patch24963 -p1
%patch24964 -p1
%patch24965 -p1
%patch24966 -p1
%patch24967 -p1
%patch24968 -p1
%patch24969 -p1
%patch24970 -p1
%patch24971 -p1
%patch24972 -p1
%patch24973 -p1
%patch24974 -p1
%patch24975 -p1
%patch24976 -p1
%patch24977 -p1
%patch24978 -p1
%patch24979 -p1
%patch24980 -p1
%patch24981 -p1
%patch24982 -p1
%patch24983 -p1
%patch24984 -p1
%patch24985 -p1
%patch24986 -p1
%patch24987 -p1
%patch24988 -p1
%patch24989 -p1
%patch24990 -p1
%patch24991 -p1
%patch24992 -p1
%patch24993 -p1
%patch24994 -p1
%patch24995 -p1
%patch24996 -p1
%patch24997 -p1
%patch24998 -p1
%patch24999 -p1
%patch25000 -p1
%patch25001 -p1
%patch25002 -p1
%patch25003 -p1
%patch25004 -p1
%patch25005 -p1
%patch25006 -p1
%patch25007 -p1
%patch25008 -p1
%patch25009 -p1
%patch25010 -p1
%patch25011 -p1
%patch25012 -p1
%patch25013 -p1
%patch25014 -p1
%patch25015 -p1
%patch25016 -p1
%patch25017 -p1
%patch25018 -p1
%patch25019 -p1
%patch25020 -p1
%patch25021 -p1
%patch25022 -p1
%patch25023 -p1
%patch25024 -p1
%patch25025 -p1
%patch25026 -p1
%patch25027 -p1
%patch25028 -p1
%patch25029 -p1
%patch25030 -p1
%patch25031 -p1
%patch25032 -p1
%patch25033 -p1
%patch25034 -p1
%patch25035 -p1
%patch25036 -p1
%patch25037 -p1
%patch25038 -p1
%patch25039 -p1
%patch25040 -p1
%patch25041 -p1
%patch25042 -p1
%patch25043 -p1
%patch25044 -p1
%patch25045 -p1
%patch25046 -p1
%patch25047 -p1
%patch25048 -p1
%patch25049 -p1
%patch25050 -p1
%patch25051 -p1
%patch25052 -p1
%patch25053 -p1
%patch25054 -p1
%patch25055 -p1
%patch25056 -p1
%patch25057 -p1
%patch25058 -p1
%patch25059 -p1
%patch25060 -p1
%patch25061 -p1
%patch25062 -p1
%patch25063 -p1
%patch25064 -p1
%patch25065 -p1
%patch25066 -p1
%patch25067 -p1
%patch25068 -p1
%patch25069 -p1
%patch25070 -p1
%patch25071 -p1
%patch25072 -p1
%patch25073 -p1
%patch25074 -p1
%patch25075 -p1
%patch25076 -p1
%patch25077 -p1
%patch25078 -p1
%patch25079 -p1
%patch25080 -p1
%patch25081 -p1
%patch25082 -p1
%patch25083 -p1
%patch25084 -p1
%patch25085 -p1
%patch25086 -p1
%patch25087 -p1
%patch25088 -p1
%patch25089 -p1
%patch25090 -p1
%patch25091 -p1
%patch25092 -p1
%patch25093 -p1
%patch25094 -p1
%patch25095 -p1
%patch25096 -p1
%patch25097 -p1
%patch25098 -p1
%patch25099 -p1
%patch25100 -p1
%patch25101 -p1
%patch25102 -p1
%patch25103 -p1
%patch25104 -p1
%patch25105 -p1
%patch25106 -p1
%patch25107 -p1
%patch25108 -p1
%patch25109 -p1
%patch25110 -p1
%patch25111 -p1
%patch25112 -p1
%patch25113 -p1
%patch25114 -p1
%patch25115 -p1
%patch25116 -p1
%patch25117 -p1
%patch25118 -p1
%patch25119 -p1
%patch25120 -p1
%patch25121 -p1
%patch25122 -p1
%patch25123 -p1
%patch25124 -p1
%patch25125 -p1
%patch25126 -p1
%patch25127 -p1
%patch25128 -p1
%patch25129 -p1
%patch25130 -p1
%patch25131 -p1
%patch25132 -p1
%patch25133 -p1
%patch25134 -p1
%patch25135 -p1
%patch25136 -p1
%patch25137 -p1
%patch25138 -p1
%patch25139 -p1
%patch25140 -p1
%patch25141 -p1
%patch25142 -p1
%patch25143 -p1
%patch25144 -p1
%patch25145 -p1
%patch25146 -p1
%patch25147 -p1
%patch25148 -p1
%patch25149 -p1
%patch25150 -p1
%patch25151 -p1
%patch25152 -p1
%patch25153 -p1
%patch25154 -p1
%patch25155 -p1
%patch25156 -p1
%patch25157 -p1
%patch25158 -p1
%patch25159 -p1
%patch25160 -p1
%patch25161 -p1
%patch25162 -p1
%patch25163 -p1
%patch25164 -p1
%patch25165 -p1
%patch25166 -p1
%patch25167 -p1
%patch25168 -p1
%patch25169 -p1
%patch25170 -p1
%patch25171 -p1
%patch25172 -p1
%patch25173 -p1
%patch25174 -p1
%patch25175 -p1
%patch25176 -p1
%patch25177 -p1
%patch25178 -p1
%patch25179 -p1
%patch25180 -p1

%patch30000 -p1
%patch30001 -p1

%if %includeovz
%patch50000 -p1

%patch60001 -p1
%patch60002 -p1
%patch60003 -p1
%patch60004 -p1
%patch60005 -p1
#%patch60006 -p1
%patch60007 -p1
%patch60008 -p1
%patch60009 -p1

%patch70003 -p1

%patch90000 -p1
%patch90001 -p1
%patch90002 -p1

%patch90210 -p1
%patch90211 -p1
%patch90212 -p1
# %patch90213 -p1 obsoleted by linux-2.6-net-forcedeth-boot-delay-fix.patch
# %patch90214 -p1 obsoleted by linux-2.6-net-r8169-support-realtek-8111c-and-8101e-loms.patch
#%patch90215 -p1
%patch90216 -p1
%patch90217 -p1
%patch90220 -p1

%patch90300 -p1
%patch90301 -p1

%patch90401 -p1
%patch90402 -p1
%patch90403 -p1
%patch90404 -p1
%patch90406 -p1
%patch90407 -p1
%patch90408 -p1
%patch90409 -p1
%patch90410 -p1
%patch90411 -p1
%patch90412 -p1
%patch90413 -p1
%patch90414 -p1

# %patch90340 -p1
# %patch90341 -p1
# %patch90342 -p1
# %patch90343 -p1

%patch90400 -p1

%patch91002 -p1
%patch91003 -p1

%patch100000 -p1
%patch100001 -p1
%patch100002 -p1
%patch100003 -p1
%patch100004 -p1
%patch100010 -p1
%patch100014 -p1
%patch100016 -p1
%patch100017 -p1
%patch100018 -p1
%patch100020 -p1
%patch100024 -p1
%patch100025 -p1
%patch100026 -p1
%patch100027 -p1
%patch100028 -p1
%patch100029 -p1
%patch100030 -p1
%patch100032 -p1
%patch100033 -p1
%patch100034 -p1
%patch100035 -p1

%patch101000 -p1
%patch101001 -p1
%patch101007 -p1

%patch110001 -p1
%patch110002 -p1
%patch110003 -p1
%patch110005 -p1
%patch110006 -p1

%patch110007 -p1
%patch110008 -p1
%patch110009 -p1

%endif

# correction of SUBLEVEL/EXTRAVERSION in top-level source tree Makefile
# patch the Makefile to include rhel version info
%patch99990 -p1
perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %sublevel/" Makefile
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -prep/" Makefile
perl -p -i -e "s/^VZVERSION.*/VZVERSION = %ovzver.%ovzrel/" Makefile
perl -p -i -e "s/^RHEL_MAJOR.*/RHEL_MAJOR = %rh_release_major/" Makefile
perl -p -i -e "s/^RHEL_MINOR.*/RHEL_MINOR = %rh_release_minor/" Makefile

# conditionally applied test patch for debugging convenience
%if %([ -s %PATCH99999 ] && echo 1 || echo 0)
%patch99999 -p1
%endif

# ALT-specific patch
%patch200000 -p1
%patch200100 -p1

# %patch210000 -p1
# %patch210001 -p1
# %patch210002 -p1
# %patch210003 -p1
# %patch210004 -p1
# %patch210005 -p1
# %patch210006 -p1
# %patch210007 -p1
# %patch210008 -p1

# END OF PATCH APPLICATIONS

cp %SOURCE10 Documentation/

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# Unpack the Xen tarball.
%if %includexen
cp %SOURCE2 .
if [ -d xen ]; then
  rm -rf xen
fi
%setup -D -T -q -n %name-%version -a1
cd xen
# Any necessary hypervisor patches go here
%patch20001 -p1
%patch20002 -p1
%patch20003 -p1
%patch20004 -p1
%patch20005 -p1
%patch20006 -p1
%patch20007 -p1
%patch20008 -p1
%patch20009 -p1
%patch20010 -p1
%patch20011 -p1
%patch20012 -p1
%patch20013 -p1
%patch20014 -p1
%patch20015 -p1
%patch20016 -p1
%patch20017 -p1
%patch20018 -p1
%patch20019 -p1
%patch20020 -p1
%patch20021 -p1
%patch20022 -p1
%patch20023 -p1
%patch20024 -p1
%patch20025 -p1
%patch20026 -p1
%patch20027 -p1
%patch20028 -p1
%patch20029 -p1
%patch20030 -p1
%patch20031 -p1
%patch20032 -p1
%patch20033 -p1
%patch20034 -p1
%patch20035 -p1
%patch20036 -p1
%patch20037 -p1
%patch20038 -p1
%patch20039 -p1
%patch20040 -p1
%patch20041 -p1
%patch20042 -p1
%patch20043 -p1
%patch20044 -p1
%patch20045 -p1
%patch20046 -p1
%patch20047 -p1
%patch20048 -p1
%patch20049 -p1
%patch20050 -p1
%patch20051 -p1
%patch20052 -p1
%patch20053 -p1
%patch20054 -p1
%patch20055 -p1
%patch20056 -p1
%patch20057 -p1
%patch20058 -p1
%patch20059 -p1
%patch20060 -p1
%patch20061 -p1
%patch20062 -p1
%patch20063 -p1
%patch20064 -p1
%patch20065 -p1
%patch20066 -p1
%patch20067 -p1
%patch20068 -p1
%patch20069 -p1
%patch20070 -p1
%patch20071 -p1
%patch20072 -p1
%patch20073 -p1
%patch20074 -p1
%patch20075 -p1
%patch20076 -p1
%patch20077 -p1
%patch20078 -p1
%patch20079 -p1
%patch20080 -p1
%patch20081 -p1
%patch20082 -p1
%patch20083 -p1
%patch20084 -p1
%patch20085 -p1
%patch20086 -p1
%patch20087 -p1
%patch20088 -p1
%patch20089 -p1
%patch20090 -p1
%patch20091 -p1
%patch20092 -p1
%patch20093 -p1
%patch20094 -p1
%patch20095 -p1
%patch20096 -p1
%patch20097 -p1
%patch20098 -p1
%patch20099 -p1
%patch20100 -p1
%patch20101 -p1
%patch20102 -p1
%patch20103 -p1
%patch20104 -p1
%patch20105 -p1
%patch20106 -p1
%patch20107 -p1
%patch20108 -p1
%patch20109 -p1
%patch20110 -p1
%patch20111 -p1
%patch20112 -p1
%patch20113 -p1
%patch20114 -p1
%patch20115 -p1
%patch20116 -p1
%patch20117 -p1
%patch20118 -p1
%patch20119 -p1
%patch20120 -p1
%patch20121 -p1
%patch20122 -p1
%patch20123 -p1
%patch20124 -p1
%patch20125 -p1
%patch20126 -p1
%patch20127 -p1
%patch20128 -p1
%patch20129 -p1
%patch20130 -p1
%patch20131 -p1
%patch20132 -p1
%patch20133 -p1
%patch20134 -p1
%patch20135 -p1
%patch20136 -p1
%patch20137 -p1
%patch20138 -p1
%patch20139 -p1
%patch20140 -p1
%patch20141 -p1
%patch20142 -p1
%patch20143 -p1
%patch20144 -p1
%patch20145 -p1
%patch20146 -p1
%patch20147 -p1
%patch20148 -p1
%patch20149 -p1
%patch20150 -p1
%patch20151 -p1
%patch20152 -p1
%patch20153 -p1
%patch20154 -p1
%patch20155 -p1
%patch20156 -p1
%patch20157 -p1
%patch20158 -p1
%patch20159 -p1
%patch20160 -p1
%patch20161 -p1
%patch20162 -p1
%patch20163 -p1
%patch20165 -p1
%patch20166 -p1
%patch20167 -p1
%patch20168 -p1
%patch20169 -p1
%patch20170 -p1
%patch20171 -p1
%patch20172 -p1
%patch20173 -p1
%patch20174 -p1
%patch20175 -p1
%patch20176 -p1
%patch20177 -p1
%patch20178 -p1
%patch20179 -p1
%patch20180 -p1
%patch20181 -p1
%patch20182 -p1
%patch20183 -p1
%patch20184 -p1
%patch20185 -p1
%patch20186 -p1
%patch20187 -p1
%patch20188 -p1
%patch20189 -p1
%patch20190 -p1
%patch20191 -p1
%patch20192 -p1
%patch20193 -p1
%patch20194 -p1
%patch20195 -p1
%patch20196 -p1
%patch20197 -p1
%patch20198 -p1
%patch20199 -p1
%patch20200 -p1
%patch20201 -p1
%patch20202 -p1
%patch20203 -p1
%patch20204 -p1
%patch20205 -p1
%patch20206 -p1
%patch20207 -p1
%patch20208 -p1
%patch20209 -p1
%patch20210 -p1
%patch20211 -p1
%patch20212 -p1
%patch20213 -p1
%patch20214 -p1
# end of necessary hypervisor patches
%endif

%if %with_openafs
  echo Prepare openafs...
  cd  %_builddir/%name-%version
  tar xjf %SOURCE3
  cd openafs-%openafs_version
%patch90500 -p1
%patch90501 -p1
%patch90502 -p1
%patch90503 -p1
%endif

%build
export ARCH=%base_arch
cd linux-%kversion.%_target_cpu

echo BUILDING A KERNEL FOR %_target_cpu...

# make sure EXTRAVERSION says what we want it to say
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%flavour-%release/" Makefile

%make_build -s mrproper
cp %_sourcedir/%kernel_config . && cp %kernel_config .config

%make_build -s nonint_oldconfig > /dev/null
%make_build -s %{?_smp_mflags} bzImage
%make_build -s %{?_smp_mflags} modules || exit 1

%if %with_openafs
    echo Building openafs...
    OpenAfsDir=%_builddir/%name-%version/openafs-%openafs_version
    KernelSrcDir=%_builddir/%name-%version/linux-%kversion.%_target_cpu
    pushd $OpenAfsDir
    [ -f Makefile ] && make distclean
    ./configure --with-linux-kernel-headers=$KernelSrcDir
    %make_build -s libafs
    popd
%endif

%install
export ARCH=%base_arch

cd linux-%kversion.%_target_cpu

mkdir -p %buildroot/boot
install -m 644 .config %buildroot/boot/config-%KVERREL
install -m 644 System.map %buildroot/boot/System.map-%KVERREL
touch %buildroot/boot/initrd-%KVERREL.img

cp arch/$ARCH/boot/bzImage %buildroot/boot/vmlinuz-%KVERREL
if [ -f arch/$ARCH/boot/zImage.stub ]; then
  cp arch/$ARCH/boot/zImage.stub %buildroot/boot/zImage.stub-%KVERREL || :
fi

%if %includeovz
cp vmlinux %buildroot/boot/vmlinux-%KVERREL
chmod 600 %buildroot/boot/vmlinux-%KVERREL
%endif

mkdir -p %buildroot/%modules_dir
make -s INSTALL_MOD_PATH=%buildroot modules_install KERNELRELEASE=%KVERREL

# Create the kABI metadata for use in packaging
echo "**** GENERATING kernel ABI metadata ****"
gzip -c9 < Module.symvers > %buildroot/boot/symvers-%KVERREL.gz
chmod 0755 %_sourcedir/kabitool
if [ ! -e %buildroot/kabi_whitelist_%_target_cpu ]; then
    echo "**** No KABI whitelist was available during build ****"
    %_sourcedir/kabitool -b %buildroot%kbuild_dir -k %KVERREL -l %buildroot/kabi_whitelist
else
cp %buildroot/kabi_whitelist_%_target_cpu %buildroot/kabi_whitelist
fi
rm -f %_tmppath/kernel-%KVERREL-kabideps
%_sourcedir/kabitool -b . -d %_tmppath/kernel-%KVERREL-kabideps -k %KVERREL -w %buildroot/kabi_whitelist

# And save the headers/makefiles etc for building modules against
#
# This all looks scary, but the end result is supposed to be:
# * all arch relevant include/ files
# * all Makefile/Kconfig files
# * all script/ files

rm -f %buildroot%modules_dir/{build,source}
mkdir -p %buildroot%modules_dir/build
(cd %buildroot%modules_dir ; ln -s build source)
# dirs for additional modules per module-init-tools, kbuild/modules.txt
mkdir -p %buildroot%modules_dir/{extra,updates,weak-updates}
%if %with_openafs
find $OpenAfsDir -name libafs.ko -execdir cp '{}' %buildroot%modules_dir/extra/openafs.ko \;
%endif
# first copy everything
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %buildroot%modules_dir/build
cp Module.symvers %buildroot%modules_dir/build
mv %buildroot/kabi_whitelist %buildroot%modules_dir/build
if [ -e %buildroot/Module.kabi ]; then
mv %buildroot/Module.kabi %buildroot%modules_dir/build
fi
cp symsets-%KVERREL.tar.gz %buildroot%modules_dir/build
# then drop all but the needed Makefiles/Kconfig files
rm -rf %buildroot%modules_dir/build/{Documentation,scripts,include}
cp .config %buildroot%modules_dir/build
cp -a scripts %buildroot%modules_dir/build
if [ -d arch/%_arch/scripts ]; then
  cp -a arch/%_arch/scripts %buildroot%modules_dir/build/arch/%_arch || :
fi
if [ -f arch/%_arch/*lds ]; then
  cp -a arch/%_arch/*lds %buildroot%modules_dir/build/arch/%_arch/ || :
fi
rm -f %buildroot%modules_dir/build/scripts/*.o
rm -f %buildroot%modules_dir/build/scripts/*/*.o
rm -rf %buildroot%modules_dir/build/scripts/rt-tester/
rm -rf %buildroot%modules_dir/build/scripts/bloat-o-meter
rm -rf %buildroot%modules_dir/build/scripts/show_delta
mkdir -p %buildroot%modules_dir/build/include
pushd include
cp -a acpi config keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound video asm asm-generic ub %buildroot%modules_dir/build/include
cp -a `readlink asm` %buildroot%modules_dir/build/include
if [ "$ARCH" = "x86_64" ]; then
  cp -a asm-i386 %buildroot%modules_dir/build/include
fi

# Make sure the Makefile and version.h have a matching timestamp so that
# external modules can be built
touch -r %buildroot%modules_dir/build/Makefile %buildroot%modules_dir/build/include/linux/version.h
touch -r %buildroot%modules_dir/build/.config %buildroot%modules_dir/build/include/linux/autoconf.h
# Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
cp %buildroot%modules_dir/build/.config %buildroot%modules_dir/build/include/config/auto.conf
popd

#
# save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
#

find %buildroot%modules_dir -name "*.ko" -type f >modnames

# mark modules executable so that strip-to-file can strip them
for i in `cat modnames`
do
  chmod u+x $i
done

# detect missing or incorrect license tags
for i in `cat modnames`
do
  echo -n "$i "
  /sbin/modinfo -l $i >> modinfo
done
cat modinfo |\
%if %with_openafs
  grep -v "http://www.openafs.org/dl/license10.html" |
%endif
  grep -v "^GPL" |
  grep -v "^Dual BSD/GPL" |\
  grep -v "^Dual MPL/GPL" |\
  grep -v "^GPL and additional rights" |\
  grep -v "^GPL v2" && exit 1
rm -f modinfo modnames
# remove files that will be auto generated by depmod at rpm -i time
rm -f %buildroot%modules_dir/modules.*

# Move the devel headers out of the root file system
mkdir -p %buildroot/usr/src/kernels
mv %buildroot%modules_dir/build %buildroot%kbuild_dir
ln -sf %kbuild_dir %buildroot%modules_dir/build

	# Temporary fix for upstream "make prepare" bug.
#	pushd $RPM_BUILD_ROOT/%%kbuild_dir > /dev/null
#	if [ -f Makefile ]; then
#		make prepare
#	fi
#	popd > /dev/null

# EOoldBuildKernel
mkdir -p %buildroot/etc/modprobe.d
cat > %buildroot/etc/modprobe.d/blacklist-firewire << \EOF
# Comment out the next line to enable the firewire drivers
blacklist firewire-ohci
EOF

%if %with_doc
mkdir -p %buildroot/usr/share/doc/kernel-doc-%kversion/Documentation

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a+r *
# copy the source over
tar cf - Documentation | tar xf - -C %buildroot/usr/share/doc/kernel-doc-%kversion
%endif

%if %with_headers
# Install kernel headers
make INSTALL_HDR_PATH=%buildroot%kheaders_dir headers_install

# Manually go through the 'headers_check' process for every file, but
# don't die if it fails
chmod +x scripts/hdrcheck.sh
echo -e '*****\n*****\nHEADER EXPORT WARNINGS:\n*****' > hdrwarnings.txt
for FILE in `find %buildroot%kheaders_dir/include` ; do
    scripts/hdrcheck.sh %buildroot%kheaders_dir/include $FILE >> hdrwarnings.txt || :
done
echo -e '*****\n*****' >> hdrwarnings.txt
if grep -q exist hdrwarnings.txt; then
   sed s:^%buildroot%kheaders_dir/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   exit 1
fi

# glibc provides scsi headers for itself, for now
rm -rf %buildroot%kheaders_dir/include/scsi
rm -f %buildroot%kheaders_dir/include/asm*/{atomic,io,irq}.h
%endif

# drivers-headers install
install -d %buildroot%kbuild_dir/drivers/scsi
install -d %buildroot%kbuild_dir/drivers/char/drm
install -d %buildroot%kbuild_dir/drivers/md
install -d %buildroot%kbuild_dir/drivers/usb/core
install -d %buildroot%kbuild_dir/drivers/net/wireless
install -d %buildroot%kbuild_dir/net/mac80211
install -d %buildroot%kbuild_dir/kernel
install -d %buildroot%kbuild_dir/lib
cp -a drivers/scsi/{{scsi,scsi_typedefs}.h,scsi_module.c} \
	%buildroot%kbuild_dir/drivers/scsi/
cp -a drivers/char/drm/{drm,drm_os_linux,drmP}.h \
	%buildroot%kbuild_dir/drivers/char/drm/
cp -a drivers/md/dm*.h \
	%buildroot%kbuild_dir/drivers/md/
cp -a drivers/usb/core/*.h \
	%buildroot%kbuild_dir/drivers/usb/core/
cp -a drivers/net/wireless/Kconfig \
	%buildroot%kbuild_dir/drivers/net/wireless/
cp -a lib/hexdump.c %buildroot%kbuild_dir/lib/
cp -a kernel/workqueue.c %buildroot%kbuild_dir/kernel/
cp -a net/mac80211/ieee80211_i.h \
	%buildroot%kbuild_dir/net/mac80211/
cp -a net/mac80211/key.h \
	%buildroot%kbuild_dir/net/mac80211/
cp -a net/mac80211/rate.h \
	%buildroot%kbuild_dir/net/mac80211/
cp -a net/mac80211/sta_info.h \
	%buildroot%kbuild_dir/net/mac80211/

# Install files required for building external modules (in addition to headers)
KbuildFiles="
	Makefile
	Module.symvers
	arch/x86/Makefile
	arch/x86/Makefile_32
	arch/x86/Makefile_32.cpu
%ifarch x86_64
	arch/x86/Makefile_64
%endif

	scripts/pnmtologo
	scripts/mod/modpost
	scripts/mkmakefile
	scripts/mkversion
	scripts/mod/mk_elfconfig
	scripts/kconfig/conf
	scripts/mkcompile_h
	scripts/makelst
	scripts/Makefile.modpost
	scripts/Makefile.modinst
	scripts/Makefile.lib
	scripts/Makefile.host
	scripts/Makefile.clean
	scripts/Makefile.build
	scripts/Makefile
	scripts/Kbuild.include
	scripts/kallsyms
	scripts/genksyms/genksyms
	scripts/basic/fixdep
	scripts/extract-ikconfig
	scripts/conmakehash
	scripts/checkversion.pl
	scripts/checkincludes.pl
	scripts/checkconfig.pl
	scripts/bin2c
	scripts/gcc-version.sh

	.config
	.kernelrelease
	gcc_version.inc
"
for f in $KbuildFiles; do
	[ -e "$f" ] || continue
	[ -x "$f" ] && mode=755 || mode=644
	install -Dp -m$mode "$f" %buildroot%kbuild_dir/"$f"
done

# Fix symlinks to kernel sources in /lib/modules
rm -f %buildroot%modules_dir/{build,source}
ln -s %kbuild_dir %buildroot%modules_dir/build

# Provide kbuild directory with old name (without %%krelease)
ln -s "$(relative %kbuild_dir %old_kbuild_dir)" %buildroot%old_kbuild_dir

###
### scripts
###

%post
%post_kernel_image %KVERREL

%preun
%preun_kernel_image %KVERREL

###
### file lists
###

%files
/boot/vmlinuz-%KVERREL
/boot/System.map-%KVERREL
/boot/symvers-%KVERREL.gz
/boot/config-%KVERREL
%modules_dir
%exclude %modules_dir/build
%ghost /boot/initrd-%KVERREL.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files -n kernel-headers-modules-%flavour
%kbuild_dir
%old_kbuild_dir
%dir %modules_dir
%modules_dir/build

%if %with_headers
%files -n kernel-headers-%flavour
%kheaders_dir
%endif

# only some architecture builds need kernel-doc
%if %with_doc
%files doc
%doc %_docdir/kernel-doc-%kversion
%endif

%changelog
* Tue Oct 05 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.15
- Release of 2.6.18-194.17.1.el5 028stab070.7

* Thu Sep 30 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.14
- Update 3w-9xxx to 26-08-006 (ALT #24189)

* Wed Sep 22 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.13
- Fix CVE-2010-3081

* Mon Sep 06 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.12
- Release of 2.6.18-194.11.3.el5 028stab071.4

* Wed Sep 01 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.11
- Release of 2.6.18-194.11.3.el5 028stab071.3
- CVE-2010-2240: keep a guard page below a grow-down stack segment

* Tue Aug 31 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.10
- Release of 2.6.18-194.11.1.el5 028stab071.2
- RHSA-2010-0610:
 * CVE-2010-1084: kernel: bluetooth: potential bad memory access with
   sysfs files
 * CVE-2010-2066: kernel: ext4: Make sure the MOVE_EXT ioctl can't
   overwrite append-only files
 * CVE-2010-2070: /kernel/security/CVE-2006-0742 test cause kernel-xen
   panic on ia64
 * CVE-2010-2226: kernel: xfs swapext ioctl minor security issue
 * CVE-2010-2248: kernel: cifs: Fix a kernel BUG with remote OS/2 server
 * CVE-2010-2521: kernel: nfsd4: bug in read_buf
 * CVE-2010-2524: kernel: dns_resolver upcall security issue

* Sat Jul 24 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.9
- Release of 2.6.18-194.8.1.el5 028stab070.2

* Mon May 31 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.8
- Release of 2.6.18-194.3.1.el5 028stab069.6

* Tue May 25 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.7
- Release of 2.6.18-194.3.1.el5 028stab069.5

* Fri Apr 02 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.6
- Release of 2.6.18-164.15.1.el5 028stab068.9

* Sun Mar 21 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.5
- Release of 2.6.18-164.11.1.el5 028stab068.5

* Wed Mar 17 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.4
- Fix openvz bug #1449 (strange load values)

* Sat Feb 20 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.3
- Release of 2.6.18-164.11.1.el5.028stab068.3
- Enable CONFIG_PRINTK_TIME

* Fri Jan 29 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.2
- Release of 2.6.18-164.10.1.el5.028stab067.4

* Tue Dec 22 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.1
- Switch to Branch 5.1

* Tue Dec 22 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt14
- Release of 2.6.18-164.2.1.el5.028stab066.10

* Mon Dec 21 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13
- Release of 2.6.18-164.2.1.el5 028stab066.7 (SA)

* Sun Nov 08 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt12
- Release of 2.6.18-128.2.1.el5 028stab064.8 (SA)
- remove make-sock_sendpage-use-kernel_sendpage.patch
- remove udp-fix-MSG_PROBE-crash.patch
- remove zaptel from modules.build

* Thu Sep 03 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt11
- Don't build wanrouter.ko

* Thu Aug 20 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt10
- CVE-2009-2698: fix MSG_PROBE crash

* Mon Aug 17 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt9
- CVE-2009-2692: uninit op in SOCKOPS_WRAP() leads to privesc
- Add patches from Solar Designer

* Mon Aug 10 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt8
- Release of 2.6.18-128.2.1.el5 028stab064.4

* Wed Jun 17 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt7
- Apply patch from Cyrill Gorcunov (fix getcpu syscall, upstream#1149)

* Wed May 20 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt6
- Compile processor.ko into kernel
- Don't build ntfs.ko
- Release of 2.6.18-128.1.1.el5.028stab062.3

* Mon Apr 20 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt5
- Disable CONFIG_KEYS (ALT #17478)

* Mon Apr 13 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt4
- Disable IPv6 support

* Thu Feb 26 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt3
- Build for Sisyhpus

* Tue Feb 24 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt1.M50.1
- Build for M50

* Fri Jan 30 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt2.M40.2
- Build on i586 instead of i686

* Thu Jan 29 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt2.M40.1
- Build for branch-4.0

* Mon Jan 26 2009 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt2
- release of 2.6.18-92.1.18.el5.028stab060.2

* Thu Dec 11 2008 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt1
- Intermediate release

* Sun Dec 07 2008 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt1.92.1.13.el5.028stab059.6
- Build with more or less adecuate konfig
- Build with sisyphus check

* Wed Nov 26 2008 Anton Protopopov <aspsk@altlinux.org> 2.6.18-92.1.13.el5.028stab059.6.alt1
- Build for ALT

* Thu Sep 4 2008 Jiri Pirko <jpirko@redhat.com> [2.6.18-92.1.13.el5]
- [md] fix crashes in iterate_rdev (Doug Ledford ) [460128 455471]
- [sound] snd_seq_oss_synth_make_info info leak (Eugene Teo ) [458000 458001] {CVE-2008-3272}
- [ipmi] control BMC device ordering (peterm@redhat.com ) [459071 430157]
- [ia64] fix to check module_free parameter (Masami Hiramatsu ) [460639 457961]
-  [misc] NULL pointer dereference in kobject_get_path (Jiri Pirko ) [459776 455460]
- [xen] ia64: SMP-unsafe with XENMEM_add_to_physmap on HVM (Tetsu Yamamoto ) [459780 457137]
- [net] bridge: eliminate delay on carrier up (Herbert Xu ) [458783 453526]
- [fs] dio: lock refcount operations (Jeff Moyer ) [459082 455750]
- [misc]  serial: fix break handling for i82571 over LAN (Aristeu Rozanski ) [460509 440018]
- [fs] dio: use kzalloc to zero out struct dio (Jeff Moyer ) [461091 439918]
- [fs] lockd: nlmsvc_lookup_host called with f_sema held (Jeff Layton ) [459083 453094]
- [net] bnx2x: chip reset and port type fixes (Andy Gospodarek ) [441259 442026]

* Wed Aug 27 2008 Jiri Pirko <jpirko@redhat.com> [2.6.18-92.1.12.el5]
- [mm] tmpfs: restore missing clear_highpage (Eugene Teo ) [426082 426083]{CVE-2007-6417}
- [fs] vfs: fix lookup on deleted directory (Eugene Teo ) [457865 457866]{CVE-2008-3275}
- [net] ixgbe: remove device ID for unsupported device (Andy Gospodarek ) [457484 454910]
- [ppc] Event Queue overflow on eHCA adapters (Brad Peters ) [458779 446713]

* Fri Aug 1 2008 Jiri Pirko <jpirko@redhat.com> [2.6.18-92.1.11.el5]
- [mm] xpmem: inhibit page swapping under heavy mem use (George Beshers ) [456946 456574]
- [xen] HV: memory corruption with large number of cpus (Chris Lalancette ) [455768 449945]
- [fs] missing check before setting mount propagation (Eugene Teo ) [454392 454393]
- [openib] small ipoib packet can cause an oops (Doug Ledford ) [447913 445731]
- [misc] fix race in switch_uid and user signal accounting (Vince Worthington ) [456235 441762 440830]

* Thu May 22 2008 Anton Arapov <aarapov@redhat.com> [2.6.18-92.1.1.el5]
- [xen] netfront: send fake arp when link gets carrier (Herbert Xu ) [447684 441716]
- [net] fix xfrm reverse flow lookup for icmp6 (Neil Horman ) [447688 446250]
- [net] negotiate all algorithms when id bit mask zero (Neil Horman ) [447685 442820]
- [net] 32/64 bit compat MCAST_ sock options support (Neil Horman ) [447687 444582]
- [misc] add CPU hotplug support for relay functions (Kei Tokunaga ) [447522 441523]

* Thu Sep 14 2006 David Woodhouse <dwmw2@redhat.com>
- 2.6.18rc7-git1
- header file fixups
- use correct arch for 'make headers_install' when cross-building

* Wed Sep 13 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc7

* Tue Sep 12 2006 David Woodhouse <dwmw2@redhat.com>
- Export <linux/netfilter/xt_{CONN,}SECMARK.h> (#205612)

* Tue Sep 12 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git4
- Enable IFB driver. (#204552)
- Export copy_4K_page for ppc64

* Tue Sep 12 2006 David Woodhouse <dwmw2@redhat.com>
- GFS2 update

* Mon Sep 11 2006 Roland McGrath <roland@redhat.com>
- s390 single-step fix

* Mon Sep 11 2006 Dave Jones <davej@redhat.com>
- Add a PCI ID to sata_via
- Intel i965 DRM support.
- Fix NFS/Selinux oops. (#204848)

* Sat Sep  9 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git3

* Fri Sep  8 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git2

* Thu Sep  7 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6-git1
- GFS2/DLM updates.

* Wed Sep  6 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: fix 32-bit PTRACE_PEEKUSR for FP regs on ppc64. (#205179)

* Wed Sep  6 2006 Juan Quintela <quintela@redhat.com>
- Undo rhel5 xen patch for relocatable.

* Wed Sep  6 2006 Dave Jones <davej@redhat.com>
- AGP support for Intel I965

* Tue Sep  5 2006 Jeremy Katz <katzj@redhat.com>
- Update xenfb based on upstream review

* Tue Sep  5 2006 Dave Jones <davej@redhat.com>
- Numerous sparse fixes to Tux.

* Tue Sep  5 2006 Mike Christie <mchristi@redhat.com>
- update iscsi layer to what will be in 2.6.19-rc1

* Tue Sep  5 2006 Dave Jones <davej@redhat.com>
- NFS lockdep fixes.
- Make ia64 Altix IDE driver built-in instead of modular. (#205282)

* Mon Sep  4 2006 Juan Quintela <quintela@redhat.com>
- xenoprof upstream fix.
- update xen HV to cset 11394.
- xen update (3hypercall incompatibility included)
- linux-2.6 changeset: 34073:b1d36669f98d
- linux-2.6-xen-fedora changeset: 35901:b7112196674e
- xen-unstable changeset: 11204:5fc1fe79083517824d89309cc618f21302724e29
- fix ia64 (xen & net xen).

* Mon Sep  4 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc6
- Drop recent NFS changes completely.

* Sun Sep  3 2006 Dave Jones <davej@redhat.com>
- Fix bogus -EIO's over NFS (#204859)
- Enable ptrace in olpc kernels. (#204958)

* Sun Sep  3 2006 Marcelo Tosatti <mtosatti@redhat.com>
- Remove PAE, xen and kdump configs for olpc case

* Sun Sep  3 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc5-git7

* Sat Sep  2 2006 Dave Jones <davej@redhat.com>
- Fix up typo in tux.patch
- 2.6.18rc5-git6

* Wed Aug 30 2006 Juan Quintela <quintela@redhat.com>
- update xen-hv to cset 11256 (pre 3 hypercall breakage).
- remove debug=y from HV compilation.
- xen update (pre 3 hypercall breakage)
  * linux-2.6 changeset: 33957:421a6d428e95
  * linux-2.6-xen-fedora changeset: 35756:78332fcbe5b0
  * xen-unstable changeset: 11251:5fc1fe79083517824d89309cc618f21302724e29
  * get new irqflags code from linux-2.6.tip-xen.

* Wed Aug 30 2006 Jeremy Katz <katzj@redhat.com>
- Fix up DEFAULTKERNEL for kernel-xen[0U]->kernel-xen change

* Wed Aug 30 2006 Marcelo Tosatti <mtosatti@redhat.com>
- Fixes for DUB-E100 vB1 usb ethernet (backported from James M.)

* Tue Aug 29 2006 Jarod Wilson <jwilson@redhat.com>
- 2.6.18-rc5-git1

* Tue Aug 29 2006 Jeremy Katz <katzj@redhat.com>
- Fix serial console with xen dom0

* Tue Aug 29 2006 Don Zickus <dzickus@redhat.com>
- enabled EHEA driver
- x86 relocatable fixes
- audit code fixes for cachefs

* Mon Aug 28 2006 Jeremy Katz <katzj@redhat.com>
- Add updated pv framebuffer patch for Xen and re-enable the config options

* Mon Aug 28 2006 Juan Quintela <quintela@redhat.com>
- ia64 xen fixing.

* Sun Aug 27 2006 David Woodhouse <dwmw2@redhat.com>
- Fix V4L1 stuff in <linux/videodev.h> (#204225)

* Fri Aug 25 2006 Juan Quintela <quintela@redhat.com>
- update xen HV to xen-unstable cset 11251.
- fix ia64 xen HV compilation.
- linux xen kernel update:
  * linux-2.6 changeset: 33681:2695586981b9
  * linux-2.6-xen-fedora changeset: 35458:b1b8e00e7a17
  * linux-2.6-xen changeset: 22861:0b726fcb6780
  * xen-unstable changeset: 11204:5fc1fe79083517824d89309cc618f21302724e29

* Fri Aug 25 2006 Don Zickus <dzickus@redhat.com>
- build fix for ia64 kdump

* Fri Aug 25 2006 Don Zickus <dzickus@redhat.com>
- update utrace
- more gfs2-dlm fixes
- fix xen-devel build directory issue
- add x86, x86_64 relocatable kernel patch for rhel only (davej, forgive my sins)
  - applied xen relocatable cleanup on top of it
- add ia64 kexec/kdump pieces

* Fri Aug 25 2006 Jesse Keating <jkeating@redhat.com>
- Enable i386 for olpc so that kernel-headers is built

* Thu Aug 24 2006 David Woodhouse <dwmw2@redhat.com>
- Update GFS2 patch (from swhiteho)
- Enable kernel-headers build
- Enable i386 build _only_ for kernel-headers

* Tue Aug 22 2006 Don Zickus <dzickus@redhat.com>
- Another lockdep-fix
- NFS fix for the connectathon test
- Enable mmtimer for ia64
- Add support for iscsi qla4xxx

* Tue Aug 22 2006 Marcelo Tosatti <mtosatti@redhat.com>
- Add Libertas wireless driver

* Mon Aug 21 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: experimental support for ia64, sparc64.

* Sun Aug 20 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc4-git1

* Sat Aug 19 2006 Dave Jones <davej@redhat.com>
- Update to latest upstream from GregKH's git tree.

* Sat Aug 19 2006 Juan Quintela <quintela@redhat.com>
- xen kernel update.
  * linux-2.6 changeset: 33525:dcc321d1340a
  * linux-2.6-xen-fedora changeset: 35247:400b0cf28ee4
  * linux-2.6-xen changeset: 22813:80c2ccf5c330
  * xen-unstable changeset: 11069:0340e579f06544431e915d17596ac144145a077e
- xen big config update.  Every config option is the same than normal kernel
  except MICROCODE, TCG_TPM & CONFIG_DEBUG_SLAB.
- disable XEN_FRAMEBUFFER & XEN_KEYBOARD.
- make sysrq c to "crash" all kernels.

* Thu Aug 17 2006 Don Zickus <dzickus@redhat.com>
- NFS 64-bit inode support
- QLogic firmware
- SELinux support for range transitions
- EHEA ethernet driver
- ppc irq mapping fix

* Wed Aug 16 2006 Roland McGrath <roland@redhat.com>
- New utrace patch:
  - Fix s390 single-step for real this time.
  - Revamp how arch code defines ptrace compatibility.

* Wed Aug 16 2006 Dave Jones <davej@redhat.com>
- Update to latest GregKH tree.
- Reenable debug.

* Tue Aug 15 2006 Don Zickus <dzickus@redhat.com>
- cleanup config-rhel-generic to compile again
- removed useless options in config-rhel-generic

* Tue Aug 15 2006 Don Zickus <dzickus@redhat.com>
- ppc64 spec cleanups

* Mon Aug 14 2006 Dave Jones <davej@redhat.com>
- Update to squashfs 3.1 which should fix stack overflows seen
  during installation.
- Merge framebuffer driver for OLPC.

* Sun Aug 13 2006 Juan Quintela <quintela@redhat.com>
- enable ia64 xen again.
- xen kernel-update linux-2.6-xen-fedora cset 35236:70890e6e4a72.
  * fix ia64 compilation problems.

* Sat Aug 12 2006 Juan Quintela <quintela@redhat.com>
- disable ia64 xen, it doesn't compile.
- xen HV update cset 11057:4ee64035c0a3
  (newer than that don't compile on ia64).
- update linux-2.6-xen patch to fix sort_regions on ia64.
- fix %%setup for xen HV to work at xen HV upgrades.

* Fri Aug 11 2006 Juan Quintela <quintela@redhat.com>
- xen HV update cset 11061:80f364a5662f.
- xen kernel update
  * linux-2.6-xen-fedora cset
  * linux-2.6-xen cset 22809:d4b3aba8876df169ffd9fac1d17bd88d87eb67c5.
  * xen-unstable 11060:323eb29083e6d596800875cafe6f843b5627d77b
  * Integrate xen virtual frame buffer patch.
  * Enable CONFIG_CRASH on xen.

* Fri Aug 11 2006 Dave Jones <davej@redhat.com>
- Yet more lockdep fixes.
- Update to GregKH's daily tree.
- GFS2/DLM locking bugfix

* Thu Aug 10 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: fix ptrace synchronization issues.

* Thu Aug 10 2006 Dave Jones <davej@redhat.com>
- GFS2/DLM update.
- Daily GregKH updates
- More lockdep fixes.

* Wed Aug  9 2006 Roland McGrath <roland@redhat.com>
- Fix utrace_regset nits breaking s390.

* Wed Aug  9 2006 Dave Jones <davej@redhat.com>
- Another lockdep fix for networking.
- Change some hotplug PCI options.
- Daily update from GregKH's git tree.
- Unbreak SMP locking in oprofile.
- Fix hotplug CPU locking in workqueue creation.
- K8 EDAC support.
- IPsec labelling enhancements for MLS
- Netlabel: CIPSO labeled networking

* Tue Aug  8 2006 Roland McGrath <roland@redhat.com>
- Fix utrace/ptrace interactions with SELinux.

* Tue Aug  8 2006 Dave Jones <davej@redhat.com>
- Pull post-rc4 fixes from GregKH's git tree.

* Mon Aug  7 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc4

* Sun Aug  6 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git7

* Fri Aug  4 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git6
- Return of signed modules.

* Thu Aug  3 2006 Roland McGrath <roland@redhat.com>
- New utrace patch:
  - fix s390 single-step
  - first third of ia64 support, enable CONFIG_UTRACE (no ptrace yet)

* Fri Aug  3 2006 Juan Quintela <quintela@anano.mitica>
- Update linux-2.6-xen patch.
  * linux-2.6-xen-fedora cset 34931:a3fda906fb82
  * linux-2.6-xen cset 22777:158b51d317b76ebc94d61c25ad6a01d121dff750
  * xen-unstable cset  10866:4833dc75ce4d08e2adc4c5866b945c930a96f225

* Thu Aug  3 2006 Juan Quintela <quintela@redhat.com>
- xen hv compiled with -O2 through Config.mk
- Update xen HV cset 10294.

* Thu Aug  3 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git3
- Fix PCI ID clash between ipr and dac960

* Thu Aug  3 2006 Jon Masters <jcm@redhat.com>
- Copy .config to include/config/auto.conf to avoid unnecessary "make prepare".
- This should finally fix #197220.
- Pulled in patch-2.6.18-rc3-git2.bz2.sign to fix SRPM build failure.

* Wed Aug  2 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git2
- Readd patch to allow 460800 baud on 16C950 UARTs.
- Fix backtracing for interrupt stacks

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com>
- add necessary ia64 hv fixes (#201040)

* Wed Aug  2 2006 Dave Jones <davej@redhat.com>
- More GFS2 bugfixing.

* Tue Aug  1 2006 Dave Jones <davej@redhat.com>
- s390 kprobes support.
- Fix oops in libata ata_device_add()
- Yet more fixes for lockdep triggered bugs.
- Merge numerous patches from -mm to improve software suspend.
- Fix incorrect section usage in MCE code that blew up on resume.

* Tue Aug  1 2006 Roland McGrath <roland@redhat.com>
- fix bogus BUG_ON in ptrace_do_wait

* Tue Aug  1 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3-git1

* Tue Aug  1 2006 Juan Quintela <quintela@redhat.com>
- disable CONFIG_DEBUG_SLAB for xen (should fix #200127).

* Mon Jul 31 2006 Roland McGrath <roland@redhat.com>
- New utrace patch:
  - fix ptrace_do_wait deadlock (#200822, #200605)
  - arch cleanups

* Mon Jul 31 2006 Juan Quintela <quintela@redhat.com>
- disable blktap for xen-ia64 (don't compile).
- enable ia64-xen (it compiles, but still don't boot).

* Mon Jul 31 2006 Juan Quintela <quintela@redhat.com>
- Fix dlm s/u.generic_ip/i_private/.

* Mon Jul 31 2006 Don Zickus <dzickus@redhat.com>
- IA64 compile fixes

* Mon Jul 31 2006 Juan Quintela <quintela@redhat.com>
- Update xen patch to linux-2.6-xen-fedora cset 34801.
	* linux-2.6 cset 33175
	* no linux-2.6-xen updates.
- Remove xen x86_64 8 cpu limit.

* Mon Jul 31 2006 Dave Jones <davej@redhat.com>
- Numerous GFS2/DLM fixes.

* Mon Jul 31 2006 Jeremy Katz <katzj@redhat.com>
- new ahci suspend patch

* Mon Jul 31 2006 Dave Jones <davej@redhat.com>
- VFS: Destroy the dentries contributed by a superblock on unmounting [try #2]

* Sun Jul 30 2006 Jon Masters <jcm@redhat.com>
- Wasn't calling weak-modules properly.
- kabitool not being picked up (weird).

* Sun Jul 30 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc3

* Sat Jul 29 2006 Dave Jones <davej@redhat.com>
- lockdep fix: ipv6
- 2.6.18rc2-git7

* Fri Jul 28 2006 Don Zickus <dzickus@redhat.com>
- Refreshed NFS caching patches
- tweaked some ppc64 kdump config options

* Fri Jul 28 2006 Jon Masters <jcm@redhat.com>
- Remove make-symsets and built-in-where as now handled by kabitool

* Fri Jul 28 2006 Dave Jones <davej@redhat.com>
- Update futex-death patch.

* Thu Jul 27 2006 Roland McGrath <roland@redhat.com>
- s390 utrace fix

* Thu Jul 27 2006 Don Zickus <dzickus@redhat.com>
- Enable kdump on ppc64iseries.  yeah more rpms..

* Thu Jul 27 2006 Dave Jones <davej@redhat.com>
- Add missing export for ia64 (#200396)

* Thu Jul 27 2006 Juan Quintela <quintela@redhat.com>
- review all xen related patches.
- x86_64 dom0, x86_64 domU and i386 domU should work.
- fix xen i386 dom0 boot (#200382).

* Thu Jul 27 2006 Rik van Riel <riel@redhat.com>
- reduce hypervisor stack use with -O2, this really fixes bug (#198932)

* Wed Jul 26 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc2-git6

* Wed Jul 26 2006 Roland McGrath <roland@redhat.com>
- New utrace patch: unsafe_exec fix; s390 build enabled (but non-working).

* Wed Jul 26 2006 Juan Quintela <quintela@redhat.com>
- new xen patch based on linux-2.6-xen cset 22749.
  and linux-2.6 cset 33089.

* Wed Jul 26 2006 Dave Jones <davej@redhat.com>
- Enable sparsemem on ia64. (#108848)

* Wed Jul 26 2006 Juan Quintela <quintela@redhat.com>
- update xen-hv to 10730 cset, should really fix huge timeout problems.

* Wed Jul 26 2006 Juan Quintela <quintela@redhat.com>
- Workaround the huge timeouts problems on xen HV x86.
- xen update and cleanup/reorgatization of xen patches.

* Tue Jul 25 2006 Rik van Riel <riel@redhat.com>
- disable debug=y hypervisor build option because of stack overflow (#198932)

* Tue Jul 25 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc2-git4 & git5

* Tue Jul 25 2006 Jon Masters <jcm@redhat.com>
- Fix kabitool provided find-provides once again.

* Tue Jul 25 2006 Juan Quintela <quintela@redhat.com>
- Use cset number instead of date for xen hypervisor.
- Update xen hypervisor to cset 10712.

* Mon Jul 24 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc2-git2 & git3
- Fix PI Futex exit crash.
- Fix an inotify locking bug.
- Add device mapper mirroring patches.

* Mon Jul 24 2006 Jon Masters <jcm@redhat.com>
- Change kabideps location.

* Mon Jul 24 2006 Juan Quintela <quintela@redhat.com>
- New xen patch, fixes gso, xenoprof, vDSO.

* Sat Jul 22 2006 Dave Jones <davej@redhat.com>
- Enable connector proc events.
- Enable PPC64 memory hotplug.
- 2.6.18rc2-git1

* Sat Jul 22 2006 Juan Quintela <quintela@redhat.com>
- addia64-xen support, not enabled by default.
- add ia64-xen config

* Fri Jul 21 2006 Jeremy Katz <katzj@redhat.com>
- Patch from jakub to use sysv style hash for VDSO to fix booting
  on ia64 (#199634, #199595)
- Fix e1000 crc calculation for things to work with xen
- Update gfs2 patchset

* Thu Jul 20 2006 Roland McGrath <roland@redhat.com>
- Clean up spec changes for debuginfo generation to cover Xen case.
- New version of utrace patch, fixes /proc permissions. (#199014)

* Thu Jul 20 2006 Juan Quintela <quintela@anano.mitica>
- remove xenPAE option, as now the i686 xen kernel is PAE.

* Thu Jul 20 2006 Juan Quintela <quintela@redhat.com>
- Fix to get xen debug info files in the right position.

* Thu Jul 20 2006 Don Zickus <dzickus@redhat.com>
- apparently I was wrong and was fixed already

* Thu Jul 20 2006 Don Zickus <dzickus@redhat.com>
- fixed build_debuginfo to not collect a stripped kernel

* Wed Jul 19 2006 Don Zickus <dzickus@redhat.com>
- Add in support for nfs superblock sharing and cachefs
  patches from David Howells
- Disable 'make prepare' hack as it is breaking ppc symlinks
- Added tracking dirty pages patch from Peter Zijlstra
- Fix for Opteron timer scaling
- Fix for Calgary pci hang

* Wed Jul 19 2006 Juan Quintela <quintela@redhat>
- big xen patch.
- enable xen again.
- redo xen config.
- i686 kernel for xen uses PAE now.
- new xen Hypervisor cset 10711.

* Wed Jul 19 2006 Roland McGrath <roland@redhat.com>
- New version of utrace patch, might fix #198780.

* Wed Jul 19 2006 Jon Masters <jcm@redhat.com>
- Workaround upstream "make prepare" bug by adding an additional prepare stage.
- Fix kabideps

* Tue Jul 18 2006 Jon Masters <jcm@redhat.com>
- Check in new version of kabitool for kernel deps.
- Fix kabitool for correct location of symvers.
- Various other fixes when things broke.

* Sun Jul 16 2006 Dave Jones <davej@redhat.com>
- Support up to 4GB in the 586 kernel again.
- Drop the FPU optimisation, it may be the reason for
  strange SIGFPE warnings various apps have been getting.

* Sat Jul 15 2006 Dave Jones <davej@redhat.com>
- Cleaned up a bunch of bogons in the config files.
- 2.6.18-rc1-git9,git10 & 2.6.18-rc2
- improvements to linked list debugging.

* Fri Jul 14 2006 Don Zickus <dzickus@redhat.com>
- remove the ppc kdump patches

* Fri Jul 14 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git8

* Thu Jul 13 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git7
- More lockdep fixes.
- Fix slab corruption issue.

* Thu Jul 13 2006 Mike Christie <mchristi@redhat.com>
- Add iscsi update being sent upstream for 2.6.18-rc2

* Thu Jul 13 2006 Roland McGrath <roland@redhat.com>
- Fix spec typo that swallowed kdump subpackage.

* Thu Jul 13 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git6

* Wed Jul 12 2006 Roland McGrath <roland@redhat.com>
- Build separate debuginfo subpackages instead of a single one.

* Wed Jul 12 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git5
- Make serial console installs on ia64 work again.
- Shrink struct inode.

* Wed Jul 12 2006 David Woodhouse <dwmw2@redhat.com>
- Temporarily disable -headers subpackage until the problems which
  arise from brew not using older package are dealt with.

* Wed Jul 12 2006 David Woodhouse <dwmw2@redhat.com>
- No headers subpackage for noarch build
- Fix PI-futexes to be properly unlocked on unexpected exit

* Wed Jul 12 2006 Dave Jones <davej@redhat.com>
- Add sleazy fpu optimisation.   Apps that heavily
  use floating point in theory should get faster.

* Tue Jul 11 2006 Dave Jones <davej@redhat.com>
- Add utrace. (ptrace replacement).

* Tue Jul 11 2006 David Woodhouse <dwmw2@redhat.com>
- Build iSeries again
- Minor GFS2 update
- Enable kernel-headers subpackage

* Tue Jul 11 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git4

* Mon Jul 10 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git3
- Big bunch o' lockdep patches from Arjan.

* Sun Jul  9 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1-git2

* Fri Jul  7 2006 Don Zickus <dzickus@redhat.com>
- Unified rhel and fedora srpm

* Fri Jul  7 2006 Dave Jones <davej@redhat.com>
- Add lockdep annotate for bdev warning.
- Enable autofs4 to return fail for revalidate during lookup

* Thu Jul  6 2006 Dave Jones <davej@redhat.com>
- 2.6.18-rc1
- Disable RT_MUTEX_TESTER

* Wed Jul  5 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git25

* Wed Jul  5 2006 Dave Jones <davej@redhat.com>
- Try out sparsemem experiment on x86-64.

* Wed Jul  5 2006 David Woodhouse <dwmw2@redhat.com>
- Fix asm-powerpc/cputime.h for new cputime64_t stuff
- Update GFS2

* Wed Jul  5 2006 Dave Jones <davej@redhat.com>
- Further lockdep improvements.

* Wed Jul  5 2006 David Woodhouse <dwmw2@redhat.com>
- 2.6.17-git24 (yay, headers_install)

* Tue Jul  4 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git21, git22 & git23

* Sun Jul  2 2006 David Woodhouse <dwmw2@redhat.com>
- Add ppoll() and pselect() on x86_64 again

* Sat Jul  1 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git19

* Fri Jun 30 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git16 & git17

* Fri Jun 30 2006 Jeremy Katz <katzj@redhat.com>
- really fix up squashfs

* Thu Jun 29 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git13, git14 & git15
- Hopefully fix up squashfs & gfs2

* Tue Jun 27 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git12
- Disable the signed module patches for now, they need love.

* Mon Jun 26 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git10 & git11
- Enable fake PCI hotplug driver. (#190437)
- Remove lots of 'modprobe loop's from specfile.

* Sun Jun 25 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git8 & git9

* Sat Jun 24 2006 Dave Jones <davej@redhat.com>
- Enable profiling for 586 kernels.
- 2.6.17-git6 & git7
  This required lots of rediffing. SATA suspend, Promise PATA-on-SATA,
  Xen, exec-shield, and more.  Tread carefully, harmful if swallowed etc.

* Fri Jun 23 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git5

* Fri Jun 23 2006 Jeremy Katz <katzj@redhat.com>
- update to squashfs 3.0

* Thu Jun 22 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git4
- Update sysconfig/kernel on x86 %%post - Robert Scheck (#196307)

* Thu Jun 22 2006 David Woodhouse <dwmw2@redhat.com>
- MTD update

* Thu Jun 22 2006 David Woodhouse <dwmw2@redhat.com>
- Update GFS2 patch
- Apply 'make headers_install' unconditionally now Linus has the cleanups

* Wed Jun 21 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git3

* Tue Jun 20 2006 David Woodhouse <dwmw2@redhat.com>
- Update MTD tree, Update and re-enable Geode tree
- Remove AC97 patch obsoleted by Geode tree

* Tue Jun 20 2006 Dave Jones <davej@redhat.com>
- 2.6.17-git1

* Sun Jun 18 2006 Dave Jones <davej@redhat.com>
- 2.6.17

* Sat Jun 17 2006 David Woodhouse <dwmw2@redhat.com>
- Add Geode and MTD git trees (for OLPC)

* Thu Jun 15 2006 Don Zickus <dzickus@redhat.com>
- rhelbuild clean ups
- add back in support for iSeries and s390 (needed internally only)

* Thu Jun 15 2006 Jeremy Katz <katzj@redhat.com>
- fix installation of -xen kernel on baremetal to be dom0 grub config

* Wed Jun 14 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git7
- Console fixes for suspend/resume
- Drop support for PPC iseries & 31bit s390.

* Wed Jun 14 2006 Juan Quintela <quintela@redhat.com>
- remove xen0/xenU/xen0-PAE/xenU-PAE packages
- disable xen PAE kernel for i386 for now
- create xen-PAE kernel
- remove %%requires xen from xen kernels

* Wed Jun 14 2006 Juan Quintela <quintela@redhat.com>
- rename xen0 & xenU to single xen kernels.

* Tue Jun 13 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git5
- serial/tty resume fixing.

* Mon Jun 12 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git3
- autofs4 - need to invalidate children on tree mount expire

* Sun Jun 11 2006 Dave Jones <davej@redhat.com>
- 2.6.17-rc6-git2
- Add MyMusix PD-205 to the unusual USB quirk list.
- Silence noisy unimplemented 32bit syscalls on x86-64.

* Sat Jun 10 2006 Juan Quintela <quintela@redhat.com>
- rebase xen to linux-2.6 cset 27412
- rebase xen to linux-2.6-xen cset 22608
- rebase HV cset 10314

* Fri Jun  9 2006 David Woodhouse <dwmw2@redhat.com>
- Update GFS2 patch, export GFS2 and DLM headers

* Fri Jun  9 2006 Dave Jones <davej@redhat.com>
- Disable KGDB again, it broke serial console :(
- 2.6.17-rc6-git1

* Wed Jun  7 2006 Dave Jones <davej@redhat.com>
- Experiment: Add KGDB.
- AC97 fix for OLPC.

* Tue Jun  6 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc6. Special 6/6/6 edition, what could go wrong?
- Add a kdump kernel for PPC64 (Don Zickus)
- Enable SCHED_STATS

* Mon Jun  5 2006 Dave Jones <davej@redhat.com>
- Do PCI config space restore on resume in reverse.
- Make Powernow-k7 work again.
- Fix the setuid /proc/self/maps fix (#165351, #190128)

* Sun Jun  4 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5-git11

* Fri Jun  2 2006 Dave Jones <davej@redhat.com>
- Drop previous autofs4 patch, it was broken.

* Fri Jun  2 2006 Juan Quintela <quintela@redhat.com>
- disable PAE for now
- update xen HV to xen-unstable cset 10243
- rebase xen-patch to linux-2.6-xen cset 22568
- rebase xen-patch to linux-2.6 cset 27329

* Thu Jun  1 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5-git8

* Wed May 31 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5-git7
- Ressurect V4L1, too much still depends on it.

* Tue May 30 2006 Dave Jones <davej@redhat.com>
- Fix up CFQ locking bug.
- 2.6.17rc5-git6
- Update iscsi to what will be pushed for 2.6.18

* Tue May 30 2006 Jon Masters <jcm@redhat.com>
- Add KMP enablers to kernel spec file.

* Mon May 29 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5-git5
- autofs4: spoof negative dentries from mount fails on browseable
  indirect map mount points
- Make acpi-cpufreq sticky.

* Sun May 28 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5-git4

* Sat May 27 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5-git2 & git3

* Fri May 26 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5-git1

* Thu May 25 2006 Juan Quintela <quintela@redhat.com>
- enable xen PAE kernels for testing.
- rebase xen patch (linux-2.6-xen cset 22558, linux-2.6 cset 27227)

* Thu May 25 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc5
- Merge GFS2/DLM (Steven Whitehouse)
- Remove .orig's during rpmbuild. (#192982)

* Wed May 24 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4-git13

* Wed May 24 2006 Juan Quintela <quintela@redhat.com>
- remove xen-irq-patch included upstream.
- rebase xen hipervisor to xen-unstable cset 10140.
- rebase xen patch linux-2.6-xen cset 22552.

* Tue May 23 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4-git11

* Mon May 22 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4-git10

* Sat May 20 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4-git9

* Thu May 18 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4-git6

* Wed May 17 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4-git5

* Tue May 16 2006 Juan Quintela <quintela@redhat.com>
- rebase xen to cset 28078.

* Sun May 16 2006 David Woodhouse <dwmw2@redhat.com>
- 2.6.17rc4-git3

* Sun May 14 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4-git2

* Thu May 11 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc4

* Tue May  9 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git17

* Mon May  8 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git15

* Sat May  6 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git12

* Fri May  5 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git11

* Fri May  5 2006 David Woodhouse <dwmw2@redhat.com>
- Fix #190776 by rediffing the patch so it actually gets applied properly
- Fix the machine check too.

* Fri May  5 2006 David Woodhouse <dwmw2@redhat.com>
- Remove bcm43xx-assoc-on-startup patch. I don't think the original
  problem is fixed upstream yet, but this patch causes BZ #190776.

* Fri May  5 2006 Juan Quintela <quintela@redhat.com>
- fix irq handling on xen Hypervisor.
- rebase to linux-2.6-xen-fedora cset 27866

* Thu May  4 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git10

* Thu May  4 2006 Jeremy Katz <katzj@redhat.com>
- improved ahci suspend patch from Forrest Zhao

* Wed May  3 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git8

* Wed May  3 2006 Juan Quintela <quintela@redhat.com>
- rebase xen-unstable HV 9920"

* Tue May  2 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git6

* Tue May  2 2006 Juan Quintela <quintela@redhat.com>
- rebase on linux-2.6 & linux-2.6-xen as of May,1st.
- new HV from xen-unstable as of 20060428.
- fixed the binaries included on xen tarball :p

* Mon May  1 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git4

* Sun Apr 30 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git3

* Fri Apr 28 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3-git2

* Fri Apr 28 2006 David Woodhouse <dwmw2@redhat.com>
- Disable Xen on the basis that it doesn't build
- Check for Xen tarball being unclean, abort early even on i386.

* Thu Apr 27 2006 Juan Quintela <quintela@redhat.com>
- Remove figlet by hand again.
- Enable xen again
- rebase linux-2.6-xen linux-2.6-xen
- fix & enable xenoprof

* Wed Apr 26 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc3
- 2.6.17rc2-git8

* Wed Apr 26 2006 David Woodhouse <dwmw2@redhat.com>
- Don't include /usr/include/scsi in kernel-headers for now, because
  glibc ships those for itself. Update header cleanup patches so that
  glibc actually builds against the resulting headers

* Wed Apr 26 2006 Juan Quintela <quintela@redhat.com>
- Delete figlet form xen hypervisor.

* Wed Apr 26 2006 David Woodhouse <dwmw2@redhat.com>
- Include kernel-headers subpackage, conditionally (and off for now)

* Wed Apr 26 2006 Juan Quintela <quintela@redhat.com>
- rebase with last linux-2.6-xen.
- enable xen again.

* Tue Apr 25 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc2-git7

* Tue Apr 25 2006 David Woodhouse <dwmw2@redhat.com>
- Drop the last remnants of the 'make bzImage on all arches' silliness

* Sun Apr 23 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc2-git5

* Sat Apr 22 2006 Dave Jones <davej@redhat.com>
- Ugly SATA suspend/resume hack de jour.

* Sat Apr 22 2006 Juan Quintela <quintela@redhat.com>
- rebase xen.
- fix x86_64 xen (thanks chris).
- enable xen again.

* Fri Apr 21 2006 Dave Jones <davej@redhat.com>
- Make Promise PATA on SATA work again (thanks Jim Bevier)
- 2.6.17rc2-git4

* Thu Apr 20 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc2-git3
- Make AHCI suspend/resume work.

* Wed Apr 19 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc2-git1
- Use unicode VTs by default.

* Tue Apr 18 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc2
- 2.6.17rc1-git13
- Enable DECNET to keep both users happy. (#120628)
- Enable TPM modules. (#189020)
- Enable some SGI specific ia64 options. (#188915)
- Add missing -kdump %%preuninstall (#189100)

* Mon Apr 17 2006 Juan Quintela <quintela@redhat.com>
- enable xen again.

* Sun Apr 16 2006 Dave Jones <davej@redhat.com>
- Big rebase to 2.6.17-rc1-git12

* Fri Apr 14 2006 Juan Quintela <quintela@redhat.com>
- Enable xen again.
- Update xen hypervisor to cset 9638.
- Update xen patch to linux-2.6.tip-xen.hg cset 26602.
- Remove/rediff lots of patches.
- x86_64 xen don't work, fixing that.

* Wed Apr 12 2006 David Woodhouse <dwmw2@redhat.com>
- Add include/{mtd,rdma,keys} directories to kernel-devel package

* Tue Apr 11 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc1-git4

* Mon Apr 10 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc1-git2 & git3
- Enable SMP on all x86 kernels.
  SMP_ALTERNATIVES disables the spinlocks etc at runtime.
- setuid /proc/self/maps fix (#165351)

* Thu Apr  6 2006 Dave Jones <davej@redhat.com>
- Rebuild without a zillion warnings.

* Tue Apr  4 2006 Dave Jones <davej@redhat.com>
- Reenable non-standard serial ports. (#187466)
- Reenable snd-es18xx for x86-32 (#187733)
- Map x86 kernel to 4MB physical address.

* Mon Apr  3 2006 Dave Jones <davej@redhat.com>
- Disable 'quiet' mode.

* Sun Apr  2 2006 Dave Jones <davej@redhat.com>
- 2.6.17rc1

* Sun Apr  2 2006 James Morris <jmorris@redhat.com>
- Rework dom0 sedf scheduler defaults patch, bz # 181856

* Sat Apr  1 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git20

* Fri Mar 31 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git19

* Fri Mar 31 2006 David Woodhouse <dwmw2@redhat.com>
- Send standard WEXT events on softmac assoc/disassociation.
- OFFB udpate

* Thu Mar 30 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git18
- Reenable CONFIG_PCI_MSI

* Wed Mar 29 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git16 & git17

* Tue Mar 28 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git14 & git15
- reenable sky2.

* Mon Mar 27 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git13
- Fix broken x86-64 32bit vDSO (#186924)

* Sat Mar 25 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git10

* Fri Mar 24 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git9

* Fri Mar 24 2006 David Woodhouse <dwmw2@redhat.com>
- Fix lockup when someone takes the bcm43xx device down while it's
  scanning (#180953)

* Thu Mar 23 2006 Juan Quintela <quintela@redhat.com>
- disable sky2 (as it is broken upstream)

* Thu Mar 23 2006 Juan Quintela <quintela@redhat.com>
- fix xen to compile with 2.6.16-git6.

* Thu Mar 23 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git6

* Wed Mar 22 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git5

* Wed Mar 22 2006 David Woodhouse <dwmw2@redhat.com>
- Update the bcm43xx driver to make it work nicely with initscripts
  and NetworkManager without user intervention.
- Fix Tux build

* Tue Mar 21 2006 Dave Jones <davej@redhat.com>
- 2.6.16-git3
- Improve spinlock scalability on big machines.

* Tue Mar 21 2006 Juan Quintela <quintela@redhat.com>
- rebase to xen unstable cset 9334.

* Tue Mar 21 2006 Juan Quintela <quintela@redhat.com>
- buildxen again.

* Mon Mar 20 2006 Juan Quintela <quintela@redhat.com>
- fix xen vmx in 64 bits.

* Mon Mar 20 2006 Dave Jones <davej@redhat.com>
- 2.6.16 & 2.6.16-git1
- Tux 2.6.16-A0 (Just rediffing)
- Update Ingo's latency tracer patch.
- Update exec-shield to Ingo's latest.
  (Incorporates John Reiser's "map the vDSO intelligently" patch
   which increases the efficiency of prelinking - #162797).
- ACPI ecdt uid hack. (#185947)

* Sun Mar 19 2006 Dave Jones <davej@redhat.com>
- 2.6.16rc6-git12
- Enable EFI on x86.

* Sat Mar 18 2006 Dave Jones <davej@redhat.com>
- 2.6.16rc6-git10 & git11

* Fri Mar 17 2006 Dave Jones <davej@redhat.com>
- 2.6.16rc6-git8 & git9

* Thu Mar 16 2006 Dave Jones <davej@redhat.com>
- 2.6.16rc6-git7

* Wed Mar 15 2006 Dave Jones <davej@redhat.com>
- 2.6.16rc6-git5
- Unmark 'print_tainted' as a GPL symbol.

* Tue Mar 14 2006 Dave Jones <davej@redhat.com>
- FC5 final kernel
- 2.6.16-rc6-git3
