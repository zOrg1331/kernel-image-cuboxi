%set_verify_elf_skiplist /boot/*
%set_strip_skiplist /boot/*

%define with_doc       0
%define with_headers   1
%define with_openafs   0

%define ovzver 028stab059

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
%define rh_release_minor 2

# Build options
# You can change compiler version by editing this line:
%define kgcc_version	4.1

#
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456"
#
%define sublevel 18
%define kversion 2.6.%sublevel
%define krelease alt1
%define xen_hv_cset 15502

%define hdrarch %_target_cpu

%define flavour         %( s='%name'; printf %%s "${s#kernel-image-}" )
%define kheaders_dir    %_prefix/include/linux-%kversion-%flavour
%define kbuild_dir      %_prefix/src/linux-%kversion-%flavour-%krelease
%define old_kbuild_dir  %_prefix/src/linux-%kversion-%flavour
%define modules_dir     /lib/modules/%kversion-%flavour-%krelease
%define KVERREL         %kversion-%flavour-%krelease

# Overrides for generic default options

# Per-arch tweaks
%ifarch i686
%define all_arch_configs kernel-%kversion-i686.config.ovz
%define hdrarch i386
# we build always xen i686 HV with pae
%endif

%ifarch x86_64
%define all_arch_configs kernel-%kversion-x86_64*.config.ovz
%endif

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

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
%if 0%{?olpc}
ExclusiveArch: i386 i586
%else
ExclusiveArch: i686 x86_64
%endif
ExclusiveOS: Linux
Provides: kernel = %version
Provides: kernel-drm = 4.3.0
Provides: kernel-%_target_cpu = %kversion-%release
Provides: vzkernel = %KVERREL
Provides: vzquotamod
Provides: alsa = 1.0.14

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
BuildRequires: gcc >= 3.4.2, binutils >= 2.12
%if %with_headers
BuildRequires: unifdef
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
BuildPreReq: python-modules

Source0: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/linux-%kversion.tar.bz2
Source1: xen-%xen_hv_cset.tar.bz2
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

Source200: kernel-%kversion-i686.config.ovz
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
Patch1: patch-2.6.18.4.bz2
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
Patch20059: xen-hv-memory-corruption-with-large-number-of-cpus.patch
Patch20060: xen-ia64-smp-unsafe-with-xenmem_add_to_physmap-on-hvm.patch
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
Patch22563: linux-2.6-misc-possible-buffer-overflow-in-asn1-parsing-routines.patch
Patch22564: linux-2.6-net-dccp-sanity-check-feature-length.patch
Patch22566: linux-2.6-x86_64-fix-copy_from_user-data-leaks.patch
Patch22567: linux-2.6-x86_64-copy_user_generic-does-not-zero-bytes.patch
Patch22568: linux-2.6-x86-sanity-checking-for-read_tsc-on-i386.patch
Patch22569: linux-2.6-net-Fixing-bonding-rtnl_lock-screwups.patch
Patch22570: linux-2.6-misc-kernel-crashes-on-futex.patch
Patch22571: linux-2.6-net-fix-recv-return-zero.patch
Patch22572: linux-2.6-i386-Add-check-for-dmi_data-in-powernow_k8-driver.patch
Patch22573: linux-2.6-i386-Add-check-for-supported_cpus-in-powernow_k8.patch
Patch22574: linux-2.6-mm-Make-mmap-with-PROT_WRITE-on-RHEL5.patch
Patch22575: linux-2.6-nfs-address-nfs-rewrite-performance-regression-in.patch
Patch22576: linux-2.6-x86_64-extend-MCE-banks-support-for-Dunnington-N.patch
Patch22577: linux-2.6-misc-ttys1-loses-interrupt-and-stops-transmitting.patch
Patch22578: linux-2.6-misc-ttys1-lost-interrupt-stops-transmitting-v2.patch
Patch22579: linux-2.6-net-sit-exploitable-remote-memory-leak.patch
Patch22580: linux-2.6-sys-sys_setrlimit-prevent-setting-rlimit_cpu-to-0.patch
Patch22581: linux-2.6-net-sctp-make-sure-sctp_addr-does-not-overflow.patch
Patch22582: linux-2.6-tty-add-null-pointer-checks.patch
Patch22583: linux-2.6-net-randomize-udp-port-allocation.patch
Patch22584: linux-2.6-ia64-properly-unregister-legacy-interrupts.patch
Patch22585: linux-2.6-misc-signaling-msgrvc-should-not-pass-back-error.patch
Patch22586: linux-2.6-ia64-softlock-prevent-endless-warnings-in-kdump.patch
Patch22587: linux-2.6-misc-fix-race-in-switch_uid-and-user-signal-accounting.patch
Patch22588: linux-2.6-openib-small-ipoib-packet-can-cause-an-oops.patch
Patch22589: linux-2.6-fs-missing-check-before-setting-mount-propagation.patch
Patch22590: linux-2.6-mm-xpmem-inhibit-page-swapping-under-heavy-mem-use.patch
Patch22591: linux-2.6-ppc-event-queue-overflow-on-ehca-adapters.patch
Patch22592: linux-2.6-net-ixgbe-remove-device-id-for-unsupported-device.patch
Patch22593: linux-2.6-fs-vfs-fix-lookup-on-deleted-directory.patch
Patch22594: linux-2.6-mm-tmpfs-restore-missing-clear_highpage.patch
Patch22595: linux-2.6-net-bnx2x-chip-reset-and-port-type-fixes.patch
Patch22596: linux-2.6-fs-lockd-nlmsvc_lookup_host-called-with-f_sema-held.patch
Patch22597: linux-2.6-fs-dio-use-kzalloc-to-zero-out-struct-dio.patch
Patch22598: linux-2.6-misc-serial-fix-break-handling-for-i82571-over-lan.patch
Patch22599: linux-2.6-fs-dio-lock-refcount-operations.patch
Patch22600: linux-2.6-net-bridge-eliminate-delay-on-carrier-up.patch
Patch22601: linux-2.6-misc-null-pointer-dereference-in-kobject_get_path.patch
Patch22602: linux-2.6-ia64-fix-to-check-module_free-parameter.patch
Patch22603: linux-2.6-ipmi-control-bmc-device-ordering.patch
Patch22604: linux-2.6-sound-snd_seq_oss_synth_make_info-info-leak.patch
Patch22605: linux-2.6-md-fix-crashes-in-iterate_rdev.patch

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
Patch60012: diff-tossing-headers-around

# cciss SG_IO ioctls (Bug #114972)
Patch70000: diff-cciss-reformat-error-handling
Patch70001: diff-cciss-add-sg-io-ioctl
Patch70002: diff-cciss-printk-creq-flags

Patch70003: diff-scsi-add-modalias-mainstream

# DRBD
Patch90000: patch-linux-2.6.18-rhel5-drbd-8.2.6

# Areca
# replaced with linux-2.6-scsi-add-kernel-support-for-areca-raid-controller.patch
# Patch90200: linux-2.6.18-arcmsr-1.20.0X.14.devel.patch

# 3ware
# RHEL5.1 adds exactly this patch: linux-2.6-scsi-9650se-not-recognized-by-3w-9xxx-module.patch
# but changes version to 2.26.02.008, instead of 2.26.06.001
# Patch90201: linux-2.6.18-3w_9xxx-2.26.06.001-2.6.18.patch
Patch90201: linux-2.6.18-3w-xxxx-1.26.02.001-03.000.patch
Patch90202: linux-2.6.18-3w_9xxx-2.26.02.008-08.003.patch

Patch90210: linux-2.6.18-atl1-1.0.41.0.patch
Patch90211: diff-backport-dm-delay-20070716
Patch90212: diff-dm-limits-bounce_pfn-20071029
# Patch90213: diff-forcedeth-fix-timeout-20071129
# Patch90214: linux-2.6.18-r8169-2.2LK-NAPI-ms-2.6.24-rc3.patch
# this patch doesn't fully help, see bug #95898. simply disabled CONFIG_FB_INTEL
# Patch90215: diff-intelfb-noregister-workaround-20071212
Patch90216: diff-snd-hda-intel
Patch90217: diff-drv-e1000-depends-e1000e-20080718
Patch90218: diff-rh-9w-try-set-mwi
Patch90219: diff-drv-arcmsr-alloc-atomic-20080821
Patch90220: diff-drv-e1000-select-e1000e

# GFSv1
Patch90300: diff-gfs-kmod-0.1.23-5.el5_2.2
Patch90301: diff-gfs-kconfig
Patch90302: diff-gfs-vz-fixes-20070514
Patch90303: diff-gfs-aops-fix-20070516
Patch90304: diff-gfs-vzquota-20070521
Patch90306: diff-gfs-debug-bugs-20070521
Patch90307: diff-gfs-setattr-multiple-20070606
Patch90308: diff-gfs-bh-leak-fix-20070716
Patch90309: diff-gfs-dread-oops-20070718
Patch90310: diff-gfs-rm-warn-20070720
Patch90311: diff-gfs-rm-lockfs-support-20071129
Patch90312: diff-gfs-force-localfloks-20080226
Patch90313: diff-gfs-shut-up-debug-20080821
Patch90314: diff-gfs-fix-proc-entry-20081024

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
Patch91001: diff-ms-tcp-slow-start-20080306
Patch91002: linux-hp-dmi-info-correct.patch
Patch91003: diff-nfs-rpcsaddr
Patch91004: diff-ms-rtnlcompat-20081010

# Bells and whistles
Patch100000: diff-fs-fsync-enable-rh5-20080131
Patch100001: diff-ms-devleak-dstdebug-20080504
Patch100002: diff-ipv4-dumpbaddst-20080929
Patch100003: diff-ipv4-reliable-dst-garbage-20080929
Patch100004: diff-ve-moreleaks-20090829
Patch100005: diff-ms-__scm_destroy-recursion-20081113
Patch100006: diff-ms-AF_UNIX-garbage-20081113
Patch100007: diff-ms-AF_UNIX-garbage-inflight-20081113
# Patch100002: diff-ms-dnotify-race

# End VZ patches

# adds rhel version info to version.h
Patch99990: linux-2.6-rhel-version-h.patch
# empty final patch file to facilitate testing of kernel patches
Patch99999: linux-kernel-test.patch

# END OF PATCH DEFINITIONS

# Override find_provides to use a script that provides "kernel(symbol) = hash".
# Pass path of the RPM temp dir containing kabideps to find-provides script.
%global _use_internal_dependency_generator 0
%define __find_provides %_sourcedir/find-provides %_tmppath
%define __find_requires /usr/lib/rpm/find-requires kernel

%ifarch x86_64
Obsoletes: kernel-smp
%endif

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

%package -n kernel-headers-modules-%flavour
Summary: Headers and other files needed for building kernel modules
Group: System/Kernel and hardware
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
Group: System/Kernel and hardware
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
# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.
if [ ! -d %name-%kversion/vanilla ]; then
  # Ok, first time we do a make prep.
  rm -f pax_global_header
%setup -q -n %name-%version -c
  mv linux-%kversion vanilla
else
  # We already have a vanilla dir.
  cd %name-%kversion
  if [ -d linux-%kversion.%_target_cpu ]; then
     # Just in case we ctrl-c'd a prep already
     rm -rf deleteme
     # Move away the stale away, and delete in background.
     mv linux-%kversion.%_target_cpu deleteme
     rm -rf deleteme &
  fi
fi
cp -rl vanilla linux-%kversion.%_target_cpu

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
%patch1350 -p1
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
%patch2801 -p1

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
%patch21561 -p1
%patch21562 -p1
%patch21563 -p1
%patch21564 -p1
%patch21565 -p1
%patch21566 -p1
%patch21567 -p1
%patch21568 -p1
%patch21569 -p1
%patch21571 -p1
%patch21572 -p1
%patch21573 -p1
%patch21574 -p1
%patch21575 -p1
%patch21576 -p1
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
%patch21681 -p1
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
%patch21727 -p1
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
%patch21819 -p1
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
%patch22170 -p1
%patch22171 -p1
%patch22172 -p1
%patch22173 -p1
%patch22174 -p1
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
%patch22342 -p1
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
%patch60012 -p1

%patch70000 -p1
%patch70001 -p1
%patch70002 -p1
%patch70003 -p1

%patch90000 -p1

#%patch90200 -p1
%patch90201 -p1
%patch90202 -p1
%patch90210 -p1
%patch90211 -p1
%patch90212 -p1
# %patch90213 -p1 obsoleted by linux-2.6-net-forcedeth-boot-delay-fix.patch
# %patch90214 -p1 obsoleted by linux-2.6-net-r8169-support-realtek-8111c-and-8101e-loms.patch
#%patch90215 -p1
%patch90216 -p1
%patch90217 -p1
%patch90218 -p1
%patch90219 -p1
%patch90220 -p1

%patch90300 -p1
%patch90301 -p1
%patch90302 -p1
%patch90303 -p1
%patch90304 -p1
%patch90306 -p1
%patch90307 -p1
%patch90308 -p1
%patch90309 -p1
%patch90310 -p1
%patch90311 -p1
%patch90312 -p1
%patch90313 -p1
%patch90314 -p1

# %patch90340 -p1
# %patch90341 -p1
# %patch90342 -p1
# %patch90343 -p1

%patch90400 -p1

%patch91001 -p1
%patch91002 -p1
%patch91003 -p1
%patch91004 -p1

%patch100000 -p1
%patch100001 -p1
%patch100002 -p1
%patch100003 -p1
%patch100004 -p1
%patch100005 -p1
%patch100006 -p1
%patch100007 -p1
# %patch100002 -p1 obsoleted by linux-2.6-fs-race-condition-in-dnotify.patch

%endif

# correction of SUBLEVEL/EXTRAVERSION in top-level source tree Makefile
# patch the Makefile to include rhel version info
%patch99990 -p1
perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %sublevel/" Makefile
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -prep/" Makefile
perl -p -i -e "s/^RHEL_MAJOR.*/RHEL_MAJOR = %rh_release_major/" Makefile
perl -p -i -e "s/^RHEL_MINOR.*/RHEL_MINOR = %rh_release_minor/" Makefile

# conditionally applied test patch for debugging convenience
%if %([ -s %PATCH99999 ] && echo 1 || echo 0)
%patch99999 -p1
%endif

# END OF PATCH APPLICATIONS

cp %SOURCE10 Documentation/

mkdir configs

for cfg in %all_arch_configs; do
  cp -f %_sourcedir/$cfg .
done

#if a olpc kernel, apply the olpc config options
%if 0%{?olpc}
  for i in %all_arch_configs
  do
    mv $i $i.tmp
    %_sourcedir/merge.pl %_sourcedir/config-olpc-generic $i.tmp > $i
    rm $i.tmp
  done
%endif

%if 0%{?rhel}
# don't need these for relocatable kernels
rm -f kernel-%kversion-{i686,x86_64}-kdump.config
# don't need these in general
rm -f kernel-%kversion-i586.config
%endif

%if 0%{?olpc}
# don't need these for OLPC
rm -f kernel-%kversion-*PAE*.config
rm -f kernel-%kversion-*ent*.config
rm -f kernel-%kversion-*xen*.config
rm -f kernel-%kversion-*kdump*.config
%endif

rm -f kernel-%kversion-*-debug.config

# now run oldconfig over all the config files
for i in *.config.ovz
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch nonint_oldconfig > /dev/null
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done

# If we don't have many patches to apply, sometimes the deleteme
# trick still hasn't completed, and things go bang at this point
# when find traverses into directories that get deleted.
# So we serialise until the dir has gone away.
cd ..
while [ -d deleteme ];
do
	sleep 1
done

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

###
### build
###
%build
# prepare directories

cd linux-%kversion.%_target_cpu

# Pick the right config file for the kernel we're building
Config=kernel-%kversion-%_target_cpu.config.ovz

echo BUILDING A KERNEL FOR %_target_cpu...

# make sure EXTRAVERSION says what we want it to say
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%release/" Makefile

# and now to start the build process

%make_build -s mrproper
cp configs/$Config .config

Arch=`head -1 .config | cut -b 3-`
echo USING ARCH=$Arch
echo "$Arch" > .buildarch

%make_build -s ARCH=$Arch nonint_oldconfig > /dev/null
%make_build -s ARCH=$Arch %{?_smp_mflags} bzImage
%make_build -s ARCH=$Arch %{?_smp_mflags} modules || exit 1

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

###
### install
###

%install
cd linux-%kversion.%_target_cpu
# Start installing the results

Arch=`cat .buildarch`

mkdir -p %buildroot/boot
install -m 644 .config %buildroot/boot/config-%KVERREL
install -m 644 System.map %buildroot/boot/System.map-%KVERREL
touch %buildroot/boot/initrd-%KVERREL.img

cp arch/$Arch/boot/bzImage %buildroot/boot/vmlinuz-%KVERREL
if [ -f arch/$Arch/boot/zImage.stub ]; then
  cp arch/$Arch/boot/zImage.stub %buildroot/boot/zImage.stub-%KVERREL || :
fi

%if %includeovz
cp vmlinux %buildroot/boot/vmlinux-%KVERREL
chmod 600 %buildroot/boot/vmlinux-%KVERREL
%endif

mkdir -p %buildroot/%modules_dir
make -s ARCH=$Arch INSTALL_MOD_PATH=%buildroot modules_install KERNELRELEASE=%KVERREL

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
mkdir -p %buildroot%modules_dir/build/include
pushd include
cp -a acpi config keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound video asm asm-generic ub %buildroot%modules_dir/build/include
cp -a `readlink asm` %buildroot%modules_dir/build/include
if [ "$Arch" = "x86_64" ]; then
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
make ARCH=%hdrarch INSTALL_HDR_PATH=%buildroot%kheaders_dir headers_install

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
   # exit 1
fi

# glibc provides scsi headers for itself, for now
rm -rf %buildroot%kheaders_dir/include/scsi
rm -f %buildroot%kheaders_dir/include/asm*/{atomic,io,irq}.h
%endif

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

* Tue Apr 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-92.el5]
- [fs] race condition in dnotify (Alexander Viro ) [443440 439759] {CVE-2008-1669 CVE-2008-1375}

* Tue Apr 22 2008 Don Zickus <dzickus@redhat.com> [2.6.18-91.el5]
- [scsi] cciss: allow kexec to work (Chip Coldwell ) [230717]
- [xen] ia64: set memory attribute in inline asm (Tetsu Yamamoto ) [426015]
- [xen] fix VT-x2 FlexPriority (Bill Burns ) [252236]

* Tue Apr 15 2008 Don Zickus <dzickus@redhat.com> [2.6.18-90.el5]
- [x86_64] page faults from user mode are user faults (Dave Anderson ) [442101]
- [ia64] kdump: add save_vmcore_info to INIT path (Neil Horman ) [442368]
- [misc] infinite loop in highres timers (Michal Schmidt ) [440002]
- [net] add aes-ctr algorithm to xfrm_nalgo (Neil Horman ) [441425]
- [x86_64] 32-bit address space randomization (Peter Zijlstra ) [213483]
- Revert: [scsi] qla2xxx: pci ee error handling support (Marcus Barrow ) [441779]
- [pci] revert 'PCI: remove transparent bridge sizing' (Ed Pollard ) [252260]
- [ppc64] eHEA: fixes receive packet handling (Brad Peters ) [441364]

* Tue Apr 08 2008 Don Zickus <dzickus@redhat.com> [2.6.18-89.el5]
- [xen] memory corruption due to VNIF increase (Tetsu Yamamoto ) [441390]
- [crytpo] use scatterwalk_sg_next for xcbc (Thomas Graf ) [439874]
- [video] PWC driver DoS (Pete Zaitcev ) [308531]
- [s390] cio: fix vary off of paths (Hans-Joachim Picht ) [436106]
- [pci] fix MSI interrupts on HT1000 based machines (Doug Ledford ) [438776]
- [s390] cio: CHPID configuration event is ignored (Hans-Joachim Picht ) [431858]
- [x86_64] add phys_base to vmcoreinfo (Muuhh IKEDA ) [439304]
- [wd] disable hpwdt due to nmi problems (Prarit Bhargava ) [438741]
- [nfs] fix the fsid revalidation in nfs_update_inode (Steve Dickson ) [431166]
- [ppc64] SLB shadow buffer error cause random reboots (Brad Peters ) [440085]
- [xen] check num of segments in block backend driver (Bill Burns ) [378291]
- [sata] SB600: add 255-sector limit (Bhavana Nagendra ) [434741]
- [x86_64] fix unprivileged crash on %%cs corruption (Jarod Wilson ) [439788]
- [scsi] qla4xxx: update driver version number (Marcus Barrow ) [439316]
- [acpi] only ibm_acpi.c should report bay events (Prarit Bhargava ) [439380]
- [x86] xen: fix SWIOTLB overflows (Stephen C. Tweedie ) [433554]
- [x86] fix mprotect on PROT_NONE regions (Stephen C. Tweedie ) [437412]
- [net] ESP: ensure IV is in linear part of the skb (Thomas Graf ) [427248]
- [x86] fix 4 bit apicid assumption (Geoff Gustafson ) [437820]
- [sata] SB700/SB800 64bit DMA support (Bhavana Nagendra ) [434741]

* Tue Apr 01 2008 Don Zickus <dzickus@redhat.com> [2.6.18-88.el5]
- [pci] hotplug: PCI Express problems with bad DLLPs (Kei Tokunaga ) [433355]
- [net] bnx2x: update 5.2 to support latest firmware (Andy Gospodarek ) [435261]
- [ipsec] use hmac instead of digest_null (Herbert Xu ) [436267]
- [utrace] race crash fixes (Roland McGrath ) [428693 245429 245735 312961]
- [x86_64] EXPORT smp_call_function_single (George Beshers ) [438720]
- [s390] FCP/SCSI write IO stagnates (Jan Glauber ) [437099]
- [net] ipv6: check ptr in ip6_flush_pending_frames (Neil Horman ) [439059]
- [nfs] stop sillyrenames and unmounts from racing (Steve Dickson ) [437302]
- [ppc64] oprofile: add support for Power5+ and later (Brad Peters ) [244719]
- [agp] add cantiga ids (Geoff Gustafson ) [438919]
- [x86] oprofile: support for Penryn-class processors (Geoff Gustafson ) [253056]
- [net] ipv6: fix default address selection rule 3 (Neil Horman ) [438429]
- [audit] fix panic, regression, netlink socket usage (Eric Paris ) [434158]
- [net] eHEA: checksum error fix (Brad Peters ) [438212]
- [s390] fix qeth scatter-gather (Jan Glauber ) [438180]
- [ata] fix SATA IDE mode bug upon resume (Bhavana Nagendra ) [432652]
- [openib] update ipath driver (Doug Ledford ) [253023]
- [openib] update the nes driver from 0.4 to 1.0 (Doug Ledford ) [253023]
- [openib] IPoIB updates (Doug Ledford ) [253023]
- [openib] cleanup of the xrc patch removal (Doug Ledford ) [253023]
- [openib] remove srpt and empty vnic driver files (Doug Ledford ) [253023]
- [openib] enable IPoIB connect mode support (Doug Ledford ) [253023]
- [openib] SDP accounting fixes (Doug Ledford ) [253023]
- [openib] add improved error handling in srp driver (Doug Ledford ) [253023]
- [openib] minor core updates between rc1 and final (Doug Ledford ) [253023]
- [openib] update ehca driver to version 0.25 (Doug Ledford ) [253023]
- [openib] remove xrc support (Doug Ledford ) [253023]
- [ppc64] hardware watchpoints: add DABRX init (Brad Peters ) [438259]
- [ppc64] hardware watchpoints: add DABRX definitions (Brad Peters ) [438259]
- [x86_64] address space randomization (Peter Zijlstra ) [222473]
- [ppc64] fixes removal of virtual cpu from dlpar (Brad Peters ) [432846]
- [mm] inconsistent get_user_pages and memory mapped (Brad Peters ) [408781]
- [s390] add missing TLB flush to hugetlb_cow (Hans-Joachim Picht ) [433799]
- [xen] HV ignoring extended cpu model field (Geoff Gustafson ) [439254]
- [xen] oprofile: support for Penryn-class processors (Geoff Gustafson ) [253056]
- [xen] ia64: HV messages are not shown on VGA console (Tetsu Yamamoto ) [438789]
- [xen] ia64: ftp stress test fixes between HVM/Dom0 (Tetsu Yamamoto ) [426015]
- [xen] ia64: fix kernel panic on systems w/<=4GB RAM (Jarod Wilson ) [431001]

* Tue Mar 25 2008 Don Zickus <dzickus@redhat.com> [2.6.18-87.el5]
- [scsi] qla4xxx: negotiation issues with new switches (Marcus Barrow ) [438032]
- [net] qla3xxx: have link SM use work threads (Marcus Barrow ) [409171]
- [scsi] qla4xxx: fix completion, lun reset code (Marcus Barrow ) [438214]
- [scsi] lpfc: update driver to 8.2.0.22 (Chip Coldwell ) [437050]
- [scsi] lpfc: update driver to 8.2.0.21 (Chip Coldwell ) [437050]
- [block] sg: cap reserved_size values at max_sectors (David Milburn ) [433481]
- Revert: [xen] idle=poll instead of hypercall block (Bill Burns ) [437252]
- [scsi] lpfc: update driver to 8.2.0.20 (Chip Coldwell ) [430600]
- [xen] add warning to 'time went backwards' message (Prarit Bhargava ) [436775]
- [x86] clear df flag for signal handlers (Jason Baron ) [436131]
- [usb] fix iaa watchdog notifications (Bhavana Nagendra ) [435670]
- [usb] new iaa watchdog timer (Bhavana Nagendra ) [435670]

* Tue Mar 18 2008 Don Zickus <dzickus@redhat.com> [2.6.18-86.el5]
- [sound] HDMI device IDs for AMD ATI chipsets (Bhavana Nagendra ) [435658]
- [scsi] fusion: 1078 corrupts data in 36GB mem region (Chip Coldwell ) [436210]
- [GFS2] gfs2_adjust_quota has broken unstuffing code (Abhijith Das ) [434736]
- [docs] add oom_adj and oom_score use to proc.txt (Larry Woodman ) [277151]
- [GFS2] optimise loop in gfs2_bitfit (Bob Peterson ) [435456]
- [crypto] fix SA creation with ESP encryption-only (Thomas Graf ) [436267]
- [crypto] fix SA creation with AH (Thomas Graf ) [435243]
- [ppc64] spufs: invalidate SLB then add a new entry (Brad Peters ) [436336]
- [ppc64] SLB: serialize invalidation against loading (Brad Peters ) [436336]
- [ppc64] cell: remove SPU_CONTEXT_SWITCH_ACTIVE flag (Brad Peters ) [434155]
- Revert: [net] sunrpc: fix hang due to eventd deadlock (Jeff Layton ) [438044]
- [ppc64] broken MSI on cell blades when IOMMU is on (Brad Peters ) [430949]
- [cpufreq] powernow: blacklist bad acpi tables (Chris Lalancette ) [430947]
- [firmware] ibft_iscsi: prevent misconfigured iBFTs (Konrad Rzeszutek ) [430297]
- [xen] HV inside a FV guest, crashes the host (Bill Burns ) [436351]

* Tue Mar 11 2008 Don Zickus <dzickus@redhat.com> [2.6.18-85.el5]
- [xen] ia64: fix kprobes slowdown on single step (Tetsu Yamamoto ) [434558]
- [xen] mprotect performance improvements (Rik van Riel ) [412731]
- [GFS2] remove assertion 'al->al_alloced' failed (Abhijith Das ) [432824]
- [misc] remove unneeded EXPORT_SYMBOLS (Don Zickus ) [295491]
- [net] e1000e: wake on lan fixes (Andy Gospodarek ) [432343]
- [sound] add support for HP-RP5700 model (Jaroslav Kysela ) [433593]
- [scsi] hptiop: fixes buffer overflow, adds pci-ids (Chip Coldwell ) [430662]
- [crypto] xcbc: fix IPsec crash with aes-xcbc-mac (Herbert Xu ) [435377]
- [misc] fix memory leak in alloc_disk_node (Jerome Marchand ) [395871]
- [net] cxgb3: rdma arp and loopback fixes (Andy Gospodarek ) [253449]
- [misc] fix range check in fault handlers with mremap (Vitaly Mayatskikh ) [428971]
- [ia64] fix userspace compile error in gcc_intrin.h (Doug Chapman ) [429074]
- [ppc64] fix xics set_affinity code (Brad Peters ) [435126]
- [scsi] sym53c8xx: use proper struct (Brad Peters ) [434857]
- [ppc64] permit pci error state recovery (Brad Peters ) [434857]
- [misc] fix ALIGN macro (Thomas Graf ) [434940]
- [x86] fix relocate_kernel to not overwrite pgd (Neil Horman ) [346431]
- [net] qla2xxx: wait for flash to complete write (Marcus Barrow ) [434992]
- [ppc64] iommu DMA alignment fix (Brad Peters ) [426875]
- [x86] add HP DL580 G5 to bfsort whitelist (Tony Camuso ) [434792]
- [video] neofb: avoid overwriting fb_info fields (Anton Arapov ) [430254]
- [x86] blacklist systems that need nommconf (Prarit Bhargava ) [433671]
- [sound] add support for AD1882 codec (Jaroslav Kysela ) [429073]
- [scsi] ibmvscsi: set command timeout to 60 seconds (Brad Peters ) [354611]
- [x86] mprotect performance improvements (Rik van Riel ) [412731]
- [fs] nlm: fix refcount leak in nlmsvc_grant_blocked (Jeff Layton ) [432626]
- [net] igb: more 5.2 fixes and backports (Andy Gospodarek ) [252004]
- [net] remove IP_TOS setting privilege checks (Thomas Graf ) [431074]
- [net] ixgbe: obtain correct protocol info on xmit (Andy Gospodarek ) [428230]
- [nfs] fslocations/referrals broken (Brad Peters ) [432690]
- [net] sctp: socket initialization race (Neil Horman ) [426234]
- [net] ipv6: fix IPsec datagram fragmentation (Herbert Xu ) [432314]
- [audit] fix bogus reporting of async signals (Alexander Viro ) [432400]
- [cpufreq] xen: properly register notifier (Bhavana Nagendra ) [430940]
- [x86] fix TSC feature flag check on AMD (Bhavana Nagendra ) [428479]

* Fri Feb 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-84.el5]
- [xen] x86: revert to default PIT timer (Bill Burns ) [428710]

* Thu Feb 21 2008 Don Zickus <dzickus@redhat.com> [2.6.18-83.el5]
- [xen] x86: fix change frequency hypercall (Bhavana Nagendra ) [430938]
- [xen] resync TSC extrapolated frequency (Bhavana Nagendra ) [430938]
- [xen] new vcpu lock/unlock helper functions (Bhavana Nagendra ) [430938]

* Tue Feb 19 2008 Don Zickus <dzickus@redhat.com> [2.6.18-82.el5]
- [ppc64] X fails to start (Don Zickus ) [433038]

* Tue Feb 12 2008 Don Zickus <dzickus@redhat.com> [2.6.18-81.el5]
- [gfs2] fix calling of drop_bh (Steven Whitehouse ) [432370]
- [nfs] potential file corruption issue when writing (Jeff Layton ) [429755]
- [nfs] interoperability problem with AIX clients (Steve Dickson ) [426804]
- [libata] sata_nv: un-blacklist hitachi drives (David Milburn ) [426044]
- [libata] sata_nv: may send cmds with duplicate tags (David Milburn ) [426044]

* Sun Feb 10 2008 Don Zickus <dzickus@redhat.com> [2.6.18-80.el5]
- [fs] check permissions in vmsplice_to_pipe (Alexander Viro ) [432253] {CVE-2008-0600}

* Fri Feb 08 2008 Don Zickus <dzickus@redhat.com> [2.6.18-79.el5]
- [net] sctp: add bind hash locking to migrate code (Aristeu Rozanski ) [426234]
- [net] ipsec: allow CTR mode use with AES (Aristeu Rozanski ) [430164]
- [net] ipv6: fixes to meet DoD requirements (Thomas Graf ) [431718]
- [module] fix module loader race (Jan Glauber ) [429909]
- [misc] ICH10 device IDs (Geoff Gustafson ) [251083]
- [sound] enable S/PDIF in Fila/Converse - fixlet (John Feeney ) [240783]
- [ide] ide-io: fail request when device is dead (Aristeu Rozanski ) [354461]
- [mm] add sysctl to not flush mmapped pages (Larry Woodman ) [431180]
- [net] bonding: locking fixes and version 3.2.4 (Andy Gospodarek ) [268001]
- [gfs2] reduce memory footprint (Bob Peterson ) [349271]
- [net] e1000e: tweak irq allocation messages (Andy Gospodarek ) [431004]
- [sched] implement a weak interactivity mode (Peter Zijlstra ) [250589]
- [sched] change the interactive interface (Peter Zijlstra ) [250589]
- [ppc] chrp: fix possible strncmp NULL pointer usage (Vitaly Mayatskikh ) [396831]
- [s390] dasd: fix loop in request expiration handling (Hans-Joachim Picht ) [430592]
- [s390] dasd: set online fails if initial probe fails (Hans-Joachim Picht ) [429583]
- [scsi] cciss: update procfs (Tomas Henzl ) [423871]
- [Xen] ia64: stop all CPUs on HV panic part3 (Tetsu Yamamoto ) [426129]

* Tue Feb 05 2008 Don Zickus <dzickus@redhat.com> [2.6.18-78.el5]
- [misc] enable i2c-piix4 (Bhavana Nagendra ) [424531]
- [ide] missing SB600/SB700 40-pin cable support (Bhavana Nagendra ) [431437]
- [isdn] i4l: fix memory overruns (Vitaly Mayatskikh ) [425181]
- [net] icmp: restore pskb_pull calls in receive func (Herbert Xu ) [431293]
- [nfs] reduce number of wire RPC ops, increase perf (Peter Staubach ) [321111]
- [xen] 32-bit pv guest migration can fail under load (Don Dutile ) [425471]
- [ppc] fix mmap of PCI resource with hack for X (Scott Moser ) [229594]
- [md] fix raid1 consistency check (Doug Ledford ) [429747]

* Thu Jan 31 2008 Don Zickus <dzickus@redhat.com> [2.6.18-77.el5]
- [xen] ia64: domHVM with pagesize 4k hangs part2 (Tetsu Yamamoto ) [428124]
- [scsi] qla2xxx: update RH version number (Marcus Barrow ) [431052]
- [ia64] fix unaligned handler for FP instructions (Luming Yu ) [428920]
- [fs] fix locking for fcntl (Ed Pollard ) [430596]
- [isdn] fix possible isdn_net buffer overflows (Aristeu Rozanski ) [392161] {CVE-2007-6063}
- [audit] fix potential SKB invalid truesize bug (Hideo AOKI ) [429417]
- [net] e1000e: disable hw crc stripping (Andy Gospodarek ) [430722]
- [firewire] more upstream fixes regarding rom (Jay Fenlason ) [370421]
- [scsi] qla25xx: incorrect firmware loaded (Marcus Barrow ) [430725]
- [scsi] qla2xxx: updated firmware for 25xxx (Marcus Barrow ) [430729]
- [gfs2] speed up read/write performance (Bob Peterson ) [253990]

* Tue Jan 29 2008 Don Zickus <dzickus@redhat.com> [2.6.18-76.el5]
- [Xen] gnttab: allow more than 3 VNIFs (Tetsu Yamamoto ) [297331]
- [xen] fix /sbin/init to use cpu_possible (Chris Lalancette ) [430310]
- [GFS2] install to root volume should work (Abhijith Das ) [220052]
- [scsi] iscsi: set host template (Mike Christie ) [430130]
- [selinux] harden against null ptr dereference bugs (Eric Paris ) [233021]

* Thu Jan 24 2008 Don Zickus <dzickus@redhat.com> [2.6.18-75.el5]
- [xen] ia64: stop all cpus on hv panic part2 (Tetsu Yamamoto ) [426129]
- [sata] combined mode fix for 5.2 (Peter Martuccelli ) [428945 428708]
- [net] bridge br_if: fix oops in port_carrier_check (Herbert Xu ) [408791]
- [misc] agp: add E7221 pci ids (Dave Airlie ) [216722]
- [ia64] kdump: slave CPUs drop to POD (Jonathan Lim ) [429956]

* Wed Jan 23 2008 Don Zickus <dzickus@redhat.com> [2.6.18-74.el5]
- Revert: [s390] qeth: create copy of skb for modification (Hans-Joachim Picht ) [354861]
- Revert: [xen] allow more than 3 VNIFs (Tetsu Yamamoto ) [297331]
- [nfs] discard pagecache data for dirs on dentry_iput (Jeff Layton ) [364351]
- [net] link_watch: always schedule urgent events (Herbert Xu ) [251527]
- [audit] ratelimit printk messages (Eric Paris ) [428701]
- [misc] kprobes: fix reentrancy (Dave Anderson ) [232489]
- [misc] kprobes: inatomic __get_user and __put_user (Dave Anderson ) [232489]
- [misc] kprobes: support kretprobe blacklist (Dave Anderson ) [232489]
- [misc] kprobes: make probe handler stack unwind correct (Dave Anderson ) [232489]
- [net] ipv6: use correct seed to compute ehash index (Neil Horman ) [248052]
- [scsi] areca: update to latest (Tomas Henzl ) [429877]
- [net] fix potential SKB invalid truesize bug (Hideo AOKI ) [429417]
- [ia64] enable CMCI on hot-plugged processors (Fabio Olive Leite ) [426793]
- [s390] system z large page support (Hans-Joachim Picht ) [318951]
- [mm] introduce more huge pte handling functions (Jan Glauber ) [318951]
- [mm] make page->private usable in compound pages (Jan Glauber ) [318951]
- [net] udp: update infiniband driver (Hideo AOKI ) [223593]
- [net] udp: add memory accounting (Hideo AOKI ) [223593]
- [net] udp: new accounting interface (Hideo AOKI ) [223593]
- [misc] support module taint flag in /proc/modules (Jon Masters ) [253476]
- [scsi] sym53c8xx: add PCI error recovery callbacks (Ed Pollard ) [207977]
- [usb] sierra MC8755: increase HSDPA performance (Ivan Vecera ) [232885]

* Wed Jan 23 2008 Don Zickus <dzickus@redhat.com> [2.6.18-73.el5]
- [xen] ia64: domHVM with pagesize 4k hangs (Tetsu Yamamoto ) [428124]
- [xen] ia64: guest has bad network performance (Tetsu Yamamoto ) [272201]
- [xen] ia64: create 100GB mem guest, HV softlockup (Tetsu Yamamoto ) [251353]
- [xen] ia64: create 100GB mem guest fixes (Tetsu Yamamoto ) [251353]
- [xen] x86-pae: support >4GB memory ia64 fixes (Bhavana Nagendra ) [316371]
- [xen] x86-pae: support >4GB memory (Bhavana Nagendra ) [316371]
- [kABI] RHEL-5.2 updates (Jon Masters ) [282881 284231 252994 371971 403821 264701 422321]
- [ia64] xen: create 100GB mem guest, fix softlockup#2 (Tetsu Yamamoto ) [251353]
- [ia64] xen: create 100GB mem guest, fix softlockup (Tetsu Yamamoto ) [251353]
- [acpi] backport video support from upstream (Dave Airlie ) [428326]
- [audit] break execve records into smaller parts (Eric Paris ) [429692]
- [scsi] qla2xxx fw: driver doesn't login to fabric (Marcus Barrow ) [253477]
- [x86] pci: use pci=norom to disable p2p rom window (Konrad Rzeszutek ) [426033]
- [s390] crypto: new CP assist functions (Hans-Joachim Picht ) [318961]
- [s390] OSA 2 Ports per CHPID support (Hans-Joachim Picht ) [318981]
- [s390] STSI change for capacity provisioning (Hans-Joachim Picht ) [318991]
- [s390] HiperSockets MAC layer routing support (Hans-Joachim Picht ) [319001]
- [scsi] aic94xx: version 1.0.2-2 (Konrad Rzeszutek ) [253301]
- [ppc64] cell: support for Performance Tools part4 (Scott Moser ) [253211]
- [ppc64] cell: support for Performance Tools part3 (Brad Peters ) [253211]
- [ppc64] cell: support for Performance Tools part2 (Scott Moser ) [253211]
- [ppc64] cell: support for Performance Tools part1 (Brad Peters ) [253211]

* Mon Jan 21 2008 Don Zickus <dzickus@redhat.com> [2.6.18-72.el5]
- [ppc64] backport PMI driver for cell blade (Scott Moser ) [279171]
- [fs] ecryptfs: fix dentry handling (Eric Sandeen ) [228341]
- [net] IPV6 SNMP counters fix (Ed Pollard ) [421401]
- [gfs2] lock the page on error (Bob Peterson ) [429168]
- [fs] manually d_move inside of rename() (Peter Staubach ) [427472]
- [dlm] validate lock name length (Patrick Caulfeld ) [409221]
- [net] IPv6 TAHI RH0 RFC5095 update (Thomas Graf ) [426904]
- [mm] using hugepages panics the kernel (Larry Woodman ) [429205]
- [sound] enable HDMI for AMD/ATI integrated chipsets (Bhavana Nagendra ) [428963]
- [net] wireless: introduce WEXT scan capabilities (John W. Linville ) [427528]
- [mm] hugepages: leak due to pagetable page sharing (Larry Woodman ) [428612]
- [nfs] acl support broken due to typo (Steve Dickson ) [429109]
- [ide] hotplug docking support for some laptops (Alan Cox ) [230541]
- [x86] cpufreq: unknown symbol fixes (Rik van Riel ) [427368]
- [mm] prevent cpu lockups in invalidate_mapping_pages (Larry Woodman ) [427798]
- [x86] mmconfig: call pcibios_fix_bus_scan (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: introduce pcibios_fix_bus_scan (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: init legacy pci conf functions (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: add legacy pci conf functions (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: introduce PCI_USING_MMCONF flag (tcamuso@redhat.com ) [408551]
- [x86] mmconfig: remove platforms from the blacklist (tcamuso@redhat.com ) [239673 253288 408551]
- [fs] hfs: make robust to deal with disk corruption (Eric Sandeen ) [213773]
- [acpi] improve reporting of power states (Brian Maly ) [210716]
- [net] e1000: update to lastest upstream (Andy Gospodarek ) [253128]
- [net] e1000e: update to latest upstream (Andy Gospodarek ) [252003]
- [xen] xenoprof: loses samples for passive domains (Markus Armbruster ) [426200]
- [cpufreq] ondemand governor update (Brian Maly ) [309311]
- [input] enable HP iLO2 virtual remote mouse (Alex Chiang ) [250288]
- [misc] ioat: support for 1.9 (John Feeney ) [209411]
- [ppc64] oprofile: power5+ needs unique entry (Scott Moser ) [244719]
- [ppc64] oprofile: distinguish 970MP from other 970s (Scott Moser ) [216458]
- [wd] hpwdt: initial support (pschoell ) [251063]
- [xen] x86: more improved TPR/CR8 virtualization (Bhavana Nagendra ) [251985]
- [xen] domain debugger for VTi (Tetsu Yamamoto ) [426362]
- [xen] virtualize ibr/dbr for PV domains (Tetsu Yamamoto ) [426362]

* Sat Jan 19 2008 Don Zickus <dzickus@redhat.com> [2.6.18-71.el5]
- [scsi] cciss: fix incompatibility with hpacucli (Tomas Henzl ) [426873]
- Revert: [net] udp: update infiniband driver (Hideo AOKI ) [223593]
- Revert: [net] udp: add memory accounting (Hideo AOKI ) [223593]
- Revert: [net] udp: new accounting interface (Hideo AOKI ) [223593]
- Revert: [misc] add a new /proc/modules_taint interface (Jon Masters ) [253476]

* Thu Jan 17 2008 Don Zickus <dzickus@redhat.com> [2.6.18-70.el5]
- [xen] move hvm_maybe_deassert_evtchn_irq early (Don Dutile ) [412721]
- [xen] hvm: tolerate intack completion failure (Don Dutile ) [412721]
- [xen] hvm: evtchn to fake pci interrupt propagation (Don Dutile ) [412721]
- [char] R500 drm support (Dave Airlie ) [429012]
- [x86] correct cpu cache info for Tolapai (Geoff Gustafson ) [426172]
- [ia64] xen: fix bogus IOSAPIC (Doug Chapman ) [246130]
- [misc] enabling a non-hotplug cpu should cause panic (Kei Tokunaga ) [426508]
- [cpufreq] booting with maxcpus=1 panics (Doug Chapman ) [428331]
- [net] fix missing defintions from rtnetlink.h (Neil Horman ) [428143]
- [xen] kdump: fix dom0 /proc/vmcore layout (Neil Horman ) [423731]
- [xen] ia64: access extended I/O spaces from dom0 (Jarod Wilson ) [249629]
- [net] udp: update infiniband driver (Hideo AOKI ) [223593]
- [net] udp: add memory accounting (Hideo AOKI ) [223593]
- [net] udp: new accounting interface (Hideo AOKI ) [223593]
- [xen] idle=poll instead of hypercall block (Markus Armbruster ) [416141]
- [net] get minimum RTO via tcp_rto_min (Anton Arapov ) [427205]
- [xen] fixes a comment only (Bill Burns ) [328321]
- [xen] make dma_addr_to_phys_addr static (Bill Burns ) [328321]
- [xen] allow sync on offsets into dma-mapped region (Bill Burns ) [328321]
- [xen] keep offset in a page smaller than PAGE_SIZE (Bill Burns ) [328321]
- [xen] handle sync invocations on mapped subregions (Bill Burns ) [328321]
- [xen] handle multi-page segments in dma_map_sg (Bill Burns ) [328321]
- [misc] add a new /proc/modules_taint interface (Jon Masters ) [253476]
- [scsi] iscsi: Boot Firmware Table tool support (Konrad Rzeszutek ) [307781]
- [mm] make zonelist order selectable in NUMA (Kei Tokunaga ) [251111]
- [ide] handle DRAC4 hotplug (John Feeney ) [212391]
- [xen] allow more than 3 VNIFs (Tetsu Yamamoto ) [297331]
- [misc] enable support for CONFIG_SUNDANCE (Andy Gospodarek ) [252074]
- [ia64] use thread.on_ustack to determine user stack (Luming Yu ) [253548]
- [xen] export cpu_llc_id as gpl (Rik van Riel ) [429004]
- [md] avoid reading past end of bitmap file (Ivan Vecera ) [237326]
- [acpi] Support external package objs as method args (Luming Yu ) [241899]

* Wed Jan 16 2008 Don Zickus <dzickus@redhat.com> [2.6.18-69.el5]
- [xen] incorrect calculation leads to wrong nr_cpus (Daniel P. Berrange ) [336011]
- [xen] ia64: hv hangs on Corrected Platform Errors (Tetsu Yamamoto ) [371671]
- [xen] ia64: warning fixes when checking EFI memory (Tetsu Yamamoto ) [245566]
- [Xen] ia64: stop all CPUs on HV panic (Tetsu Yamamoto ) [426129]
- [Xen] ia64: failed domHVM creation causes HV hang (Tetsu Yamamoto ) [279831]
- [xen] export NUMA topology info to domains (Bill Burns ) [235848]
- [xen] provide NUMA memory usage information (Bill Burns ) [235850]
- [xen] x86: barcelona hypervisor fixes (Bhavana Nagendra ) [421021]
- [xen] improve checking in vcpu_destroy_pagetables (Bill Burns ) [227614]
- [xen] domain address-size clamping (Bill Burns ) [227614]
- [xen] x86: fix continuation translation for large HC (Bill Burns ) [227614]
- [xen] x86: make HV respect the e820 map < 16M (Chris Lalancette ) [410811]
- [xen] x86: vTPR support and upper address fix (Bill Burns ) [252236]
- [xen] x86: fix hp management support on proliant (Bill Burns ) [415691]
- [xen] x86: improved TPR/CR8 virtualization (Bhavana Nagendra ) [251985]
- [xen] ia64: running java-vm causes dom0 to hang (Tetsu Yamamoto ) [317301]
- [xen] enable nested paging by default on amd-v (Bhavana Nagendra ) [247190]
- [fs] corruption by unprivileged user in directories (Vitaly Mayatskikh ) [428797] {CVE-2008-0001}
- [gfs2] Reduce gfs2 memory requirements (Bob Peterson ) [428291]
- [gfs2] permission denied on first attempt to exec (Abhijith Das ) [422681]
- [openib] OFED 1.3 support (Doug Ledford ) [253023 254027 284861]
- [scsi] qla2xxx: fix bad nvram kernel panic (Marcus Barrow ) [367201]
- [scsi] qla2xxx: fix for infinite-login-retry (Marcus Barrow ) [426327]
- [misc] increase softlockup timeout maximum (George Beshers ) [253124]
- [misc] firewire: latest upstream (Jay Fenlason ) [370421]
- [misc] pci rom: reduce number of failure messages (Jun'ichi "Nick" Nomura ) [217698]
- [s390] pte type cleanup (Hans-Joachim Picht ) [360701]
- [s390] qdio: output queue stall on FCP and net devs (Hans-Joachim Picht ) [354871]
- [s390] qdio: many interrupts on qdio-driven devices (Hans-Joachim Picht ) [360821]
- [s390] qdio: time calculation is wrong (Hans-Joachim Picht ) [360631]
- [s390] crash placing a kprobe on  instruction (Hans-Joachim Picht ) [253275]
- [s390] data corruption on DASD while toggling CHPIDs (Hans-Joachim Picht ) [360611]
- [s390] fix dump on panic for DASDs under LPAR (Hans-Joachim Picht ) [250352]
- [s390] qeth: crash during activation of OSA-cards (Hans-Joachim Picht ) [380981]
- [s390] qeth: hipersockets supports IP packets only (Hans-Joachim Picht ) [329991]
- [s390] cio: Disable chan path measurements on reboot (Hans-Joachim Picht ) [354801]
- [s390] zfcp: remove SCSI devices then adapter (Hans-Joachim Picht ) [382841]
- [s390] zfcp: error messages when LUN 0 is present (Jan Glauber ) [354811]
- [s390] qeth: drop inbound pkt with unknown header id (Hans-Joachim Picht ) [360591]
- [s390] qeth: recognize/handle RC=19 from Hydra 3 OSA (Hans-Joachim Picht ) [354891]
- [char] tpm: cleanups and fixes (Konrad Rzeszutek ) [184784]
- [s390] z/VM monitor stream state 2 (Hans-Joachim Picht ) [253026]
- [s390] support for z/VM DIAG 2FC (Hans-Joachim Picht ) [253034]
- [s390] Cleanup SCSI dumper code part 2 (Hans-Joachim Picht ) [253104]
- [s390] AF_IUCV Protocol support (Jan Glauber ) [228117]
- [s390] z/VM unit-record device driver (Hans-Joachim Picht ) [253121]
- [s390] cleanup SCSI dumper code (Hans-Joachim Picht ) [253104]
- [s390] qeth: skb sg support for large incoming msgs (Hans-Joachim Picht ) [253119]
- [ia64] /proc/cpuinfo of Montecito (Luming Yu ) [251089]

* Sun Jan 13 2008 Don Zickus <dzickus@redhat.com> [2.6.18-68.el5]
- [misc] offline CPU with realtime process running v2 (Michal Schmidt ) [240232]
- Revert: [misc] offlining a CPU with realtime process running (Don Zickus ) [240232]
- [x86] fix build warning for command_line_size (Prarit Bhargava ) [427423]
- [mm] show_mem: include count of pagecache pages (Larry Woodman ) [428094]
- [nfs] Security Negotiation (Steve Dickson ) [253019]
- [net] igb: update to actual upstream version (Andy Gospodarek ) [252004]
- [scsi] cciss: move READ_AHEAD to block layer (Tomas Henzl ) [424371]
- [scsi] cciss: update copyright information (Tomas Henzl ) [423841]
- [scsi] cciss: support new controllers (Tomas Henzl ) [423851]
- [scsi] cciss version change (Tomas Henzl ) [423831]
- [md] dm-mpath: send uevents for path fail/reinstate (dwysocha@redhat.com ) [184778]
- [md] dm-uevent: generate events (Dave Wysochanski ) [184778]
- [md] dm: add uevent to core (dwysocha@redhat.com ) [184778]
- [md] dm: export name and uuid (dwysocha@redhat.com ) [184778]
- [md] dm: kobject backport (Dave Wysochanski ) [184778]
- [sata] rhel5.2 driver update (Jeff Garzik ) [184884 307911]
- [sata] rhel5.2 general kernel prep (Jeff Garzik ) [184884 307911]
- [md] dm: auto loading of dm-mirror log modules (Jonathan Brassow ) [388661]
- [scsi] areca driver update rhel part (Tomas Henzl ) [363961]
- [scsi] areca driver update (Tomas Henzl ) [363961]
- [firewire] limit logout messages in the logs (Jay Fenlason ) [304981]
- - [net] add support for dm9601 (Ivan Vecera ) [251994]
- [ia64] ACPICA: allow Load tables (Luming Yu ) [247596]

* Fri Jan 11 2008 Don Zickus <dzickus@redhat.com> [2.6.18-67.el5]
- [xfrm] drop pkts when replay counter would overflow (Herbert Xu ) [427877]
- [xfrm] rfc4303 compliant auditing (Herbert Xu ) [427877]
- [ipsec] add ICMP host relookup support (Herbert Xu ) [427876]
- [ipsec] added xfrm reverse calls (Herbert Xu ) [427876]
- [ipsec] make xfrm_lookup flags argument a bit-field (Herbert Xu ) [427876]
- [ipv6] esp: discard dummy packets from rfc4303 (Herbert Xu ) [427872]
- [ipv4] esp: discard dummy packets from rfc4303 (Herbert Xu ) [427872]
- [ipsec] add support for combined mode algorithms (Herbert Xu ) [253051]
- [ipsec] allow async algorithms (Herbert Xu ) [253051]
- [ipsec] use crypto_aead and authenc in ESP (Herbert Xu ) [253051]
- [ipsec] add new skcipher/hmac algorithm interface (Herbert Xu ) [253051]
- [ipsec] add async resume support on input (Herbert Xu ) [253051]
- [crypto] aead: add authenc (Herbert Xu ) [253051]
- [ipsec] add async resume support on output (Herbert Xu ) [253051]
- [crypto] xcbc: new algorithm (Herbert Xu ) [253051]
- [crypto] ccm: added CCM mode (Herbert Xu ) [253051]
- [crypto] tcrypt: add aead support (Herbert Xu ) [253051]
- [crypto] ctr: add CTR  block cipher mode (Herbert Xu ) [253051]
- [crypto] hmac: add crypto template implementation (Herbert Xu ) [253051]
- [crypto] tcrypt: hmac template and hash interface (Herbert Xu ) [253051]
- [crypto] tcrypt: use skcipher interface (Herbert Xu ) [253051]
- [crypto] digest: added user api for new hash type (Herbert Xu ) [253051]
- [crypto] cipher: added block ciphers for CBC/ECB (Herbert Xu ) [253051]
- [crypto] cipher: added encrypt_one/decrypt_one (Herbert Xu ) [253051]
- [crypto] seqiv: add seq num IV generator (Herbert Xu ) [253051]
- [crypto] api: add aead crypto type (Herbert Xu ) [253051]
- [crypto] eseqiv: add encrypted seq num IV generator (Herbert Xu ) [253051]
- [crypto] chainiv: add chain IV generator (Herbert Xu ) [253051]
- [crypto] skcipher: add skcipher infrastructure (Herbert Xu ) [253051]
- [crypto] api: add cryptomgr (Herbert Xu ) [253051]
- [crypto] api: add new bottom-level crypto_api (Herbert Xu ) [253051]
- [crypto] api: add new top-level crypto_api (Herbert Xu ) [253051]
- [scsi] mpt fusion: set config_fusion_max=128 (Chip Coldwell ) [426533]
- [xen] ia64: fix ssm_i emulation barrier and vdso pv (Tetsu Yamamoto ) [426015]
- [xen] ia64: cannot create guest having 100GB memory (Tetsu Yamamoto ) [251353]
- [ia64] altix acpi iosapic warning cleanup (George Beshers ) [246130]
- [x86] add pci quirk to HT enabled systems (Neil Horman ) [336371]
- [fs] ecryptfs: check for existing key_tfm at mount (Eric Sandeen ) [228341]
- [fs] ecryptfs: redo dget,mntget on dentry_open fail (Eric Sandeen ) [228341]
- [fs] ecryptfs: upstream fixes (Eric Sandeen ) [228341]
- [fs] ecryptfs: connect sendfile ops (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 netlink api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 scatterlist api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to crypto hash api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 cipher api (Eric Sandeen ) [228341]
- [fs] ecryptfs: un-constify ops vectors (Eric Sandeen ) [228341]
- [fs] ecryptfs: convert to memclear_highpage_flush (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport to rhel5 memory alloc api (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport sysf API for kobjects/ksets (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport generic_file_aio_read (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport f_path to f_dentry (Eric Sandeen ) [228341]
- [fs] ecryptfs: convert to vfsmount/dentry (Eric Sandeen ) [228341]
- [fs] ecryptfs: stacking functions from upstream vfs (Eric Sandeen ) [228341]
- [fs] ecryptfs: backport from 2.6.24-rc4 (Eric Sandeen ) [228341]
- [firewire] fix uevent to handle hotplug (Jay Fenlason ) [302981]
- [cpufreq] fix non-smp compile and warning (Prarit Bhargava ) [413941]
- [net] r8169: support realtek 8111c and 8101e loms (Ivan Vecera ) [276421 251259 248534 247142 238187]
- specfile: xen - see more than 32 vpcus on x86_64 (Bill Burns) [228572]
- specfile: cleanups, add new build options (Jarod Wilson) [248753 232602 247118]

* Wed Jan 09 2008 Don Zickus <dzickus@redhat.com> [2.6.18-66.el5]
- Fixes: [lockdep] lockstat: core infrastructure (Peter Zijlstra ) [193729]

* Wed Jan 09 2008 Don Zickus <dzickus@redhat.com> [2.6.18-65.el5]
- [audit] add session id to easily correlate records (Eric Paris ) [242813]
- [audit] log uid, auid, and comm in obj_pid records (Eric Paris ) [284531]
- [net] cxgb3: update to latest upstream (Andy Gospodarek ) [253195]
- [net] bnx2x: support Broadcom 10GbE Hardware (Andy Gospodarek ) [253346]
- [misc] enable i2c-piix4 (Bhavana Nagendra ) [424531]
- [net] ixgbe: support for new Intel 10GbE Hardware (Andy Gospodarek ) [252005]
- [net] iwl4965 updates (John W. Linville ) [252981]
- [net] mac80211 updates (John W. Linville ) [253015]
- [net] cfg80211 updates to support mac80211/iwl4965 (John W. Linville ) [252981]
- [net] infrastructure updates to mac80211/iwl4965 (John W. Linville ) [252981 253015 253027 256001]
- [net] NULL dereference in iwl driver (Vitaly Mayatskikh ) [401431] {CVE-2007-5938}
- [scsi] iscsi_tcp update (Mike Christie ) [253989 245823]
- [aio] account for I/O wait properly (Jeff Moyer ) [253337]
- [alsa] disabling microphone in bios panics kernel (John Feeney ) [240783]
- [lockdep] make cli/sti annotation warnings clearer (Peter Zijlstra ) [193729]
- [lockdep] fixup mutex annotations (Peter Zijlstra ) [193729]
- [lockdep] mismatched lockdep_depth/curr_chain_hash (Peter Zijlstra ) [193729]
- [lockdep] avoid lockdep & lock_stat infinite output (Peter Zijlstra ) [193729]
- [lockdep] lockstat: documentation (Peter Zijlstra ) [193729]
- [lockdep] lockstat: better class name representation (Peter Zijlstra ) [193729]
- [lockdep] lockstat: measure lock bouncing (Peter Zijlstra ) [193729]
- [lockdep] fixup sk_callback_lock annotation (Peter Zijlstra ) [193729]
- [lockdep] various fixes (Peter Zijlstra ) [193729]
- [lockdep] lockstat: hook into the lock primitives (Peter Zijlstra ) [193729]
- [lockdep] lockstat: human readability tweaks (Peter Zijlstra ) [193729]
- [lockdep] lockstat: core infrastructure (Peter Zijlstra ) [193729]
- [lockdep] sanitise CONFIG_PROVE_LOCKING (Peter Zijlstra ) [193729]
- [misc] fix raw_spinlock_t vs lockdep (Peter Zijlstra ) [193729]
- [alsa] support for realtek alc888s (Brian Maly ) [251253]
- [xen] save/restore: pv oops when mmap prot_none (Chris Lalancette ) [294811]
- [net] dod ipv6 conformance (Neil Horman ) [253278]
- [audit] log eintr, not erestartsys (Eric Paris ) [234426]
- [misc] ipmi: panic handling enhancement (Geoff Gustafson ) [277121]
- [misc] fix softlockup warnings/crashes (Chris Lalancette ) [250994]
- [misc] core dump masking support (Takahiro Yasui ) [223616]
- [fs] executing binaries with >2GB debug info (Dave Anderson ) [224679]
- [sched] return first time_slice to correct process (Vitaly Mayatskikh ) [238035]

* Tue Jan 08 2008 Don Zickus <dzickus@redhat.com> [2.6.18-64.el5]
- Fixes: [kexec] fix vmcoreinfo patch that breaks kdump (Neil Horman ) [424511]
- Fixes: [fs] nfs: byte-range locking support for cfs (Konrad Rzeszutek ) [196318]

* Mon Jan 07 2008 Don Zickus <dzickus@redhat.com> [2.6.18-63.el5]
- [scsi] lpfc:  update to version 8.2.0.13 (Chip Coldwell ) [426281]
- [scsi] qla2xxx: rediscovering luns takes 5 min (Marcus Barrow ) [413211]
- [misc] edac: add support for intel 5000 mchs (Aristeu Rozanski ) [249335]
- [fs] ext3: error in ext3_lookup if corruption found (Eric Sandeen ) [181662]
- [scsi] stex: use resid for xfer len information (Prarit Bhargava ) [251557]
- [scsi] qla2xxx: msi-x hardware issues on platforms (Marcus Barrow ) [253629]
- [net] ipv6: ip6_mc_input: sense of promiscuous test (Neil Horman ) [390071]
- [x86] Add warning to nmi failure message (Prarit Bhargava ) [401631]
- [misc] enable s/pdif in fila/converse (John Feeney ) [240783]
- [scsi] qla2xxx: add support for npiv - firmware (Marcus Barrow ) [249618]
- [scsi] qla2xxx: pci ee error handling support (Marcus Barrow ) [253267]
- [scsi] qla2xxx: add support for npiv (Marcus Barrow ) [249618]
- [scsi] mpt fusion: fix sas hotplug (Chip Coldwell ) [253122]
- [misc] export radix-tree-preload (George Beshers ) [422321]
- [net] forcedeth: boot delay fix (Andy Gospodarek ) [405521]
- [kexec] fix vmcoreinfo patch that breaks kdump (Neil Horman ) [424511]
- Revert: [misc] add vmcoreinfo support to kernel (Neil Horman ) [253850]
- [scsi] mpt fusion: update to version 3.04.05+ (Chip Coldwell ) [253122]
- [scsi] mpt fusion: add accessor for version 3.04.05+ (Chip Coldwell ) [253122]
- [scsi] mpt fusion: pci ids for version 3.04.05+ (Chip Coldwell ) [253122]
- [misc] offlining a CPU with realtime process running (Michal Schmidt ) [240232]
- [misc] ioat dma: support unisys (Ivan Vecera ) [248767]
- [md] dm ioctl: fix 32bit compat layer (Milan Broz ) [360441]
- [ppc64] enable CONFIG_FB_RADEON (Scott Moser ) [281141]
- [audit] race checking audit_context and loginuid (Eric Paris ) [241728]
- [scsi] update megaraid_sas to version 3.15 (Tomas Henzl ) [243154]
- [x86_64] calioc2 iommu support (Konrad Rzeszutek ) [253302]
- [x86] cpuinfo: list dynamic acceleration technology (Geoff Gustafson ) [252229]
- [ppc64] unequal allocation of hugepages (Scott Moser ) [239790]
- [md] fix bitmap support (Doug Ledford ) [210178]
- [misc] tlclk driver for telco blade systems (Geoff Gustafson ) [233512]
- [fs] nfs: byte-range locking support for cfs (Konrad Rzeszutek ) [196318]
- [x86_64] nmi watchdog: incorrect logic for amd chips (Prarit Bhargava ) [391741]
- [x86] edac: add support for Intel i3000 (Aristeu Rozanski ) [295501]
- [mm] fix hugepage allocation with memoryless nodes (Scott Moser ) [239790]
- [mm] make compound page destructor handling explicit (Scott Moser ) [239790]
- [scsi] qla2xxx: more improvements and cleanups part2 (Marcus Barrow ) [253272]
- [scsi] qla2xxx: 8 GB/S support (Marcus Barrow ) [249796]
- [scsi] qla2xxx: upstream improvements and cleanups (Marcus Barrow ) [253272]
- [ppc64] ehea: sync with upstream (Scott Moser ) [253414]
- [ia64] fix kernel warnings from rpm prep stage (Luming Yu ) [208271]

* Thu Dec 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-62.el5]
- [xen] ia64: hvm guest memory range checking (Jarod Wilson ) [408711]
- [xen] x86: support for architectural pstate driver (Bhavana Nagendra ) [419171]
- [xen] disable cpu freq scaling when vcpus is small (Rik van Riel ) [251969]
- [xen] hv: cpu frequency scaling (Rik van Riel ) [251969]
- [xen] ia64: vulnerability of copy_to_user in PAL emu (Jarod Wilson ) [425939]
- [net] bonding: documentation update (Andy Gospodarek ) [235711]
- [net] bonding: update to upstream version 3.2.2 (Andy Gospodarek ) [251902 236750 268001]
- [misc] utrace: update for 5.2 (Roland McGrath ) [299941 309461 309551 309761]
- [ia64] ptrace: access to user register backing (Roland McGrath ) [237749]
- [ia64] utrace: forbid ptrace changes psr.ri to 3 (Roland McGrath ) [247174]
- [net] bnx2: update to upstream version 1.6.9 (Andy Gospodarek ) [251109]
- [net] tg3: update to upstream version 3.86 (Andy Gospodarek ) [253344]
- [net] sunrpc: make clients take ref to rpciod workq (Jeff Layton ) [246642]
- [scsi] aacraid: update to 1.1.5-2453 (Chip Coldwell ) [364371]
- [md] dm-mirror: write_callback might deadlock (Jonathan Brassow ) [247877]
- [md] dm-mirror: shedule_timeout call causes slowdown (Jonathan Brassow ) [358881]
- [md] mirror presuspend causing cluster mirror hang (Jonathan Brassow ) [358871]
- [acpi] docking/undocking: oops when _DCK eval fails (John Feeney ) [252214]
- [acpi] docking/undocking: check if parent is on dock (John Feeney ) [252214]
- [acpi] docking/undocking: error handling in init (John Feeney ) [252214]
- [acpi] docking/undocking: add sysfs support (John Feeney ) [252214]
- [acpi] docking/undocking support (John Feeney ) [252214]
- [xen] support for architectural pstate driver (Bhavana Nagendra ) [419171]
- [usb] wacom: fix 'side' and 'extra' mouse buttons (Aristeu Rozanski ) [249415]
- [audit] netmask on xfrm policy configuration changes (Eric Paris ) [410531]
- [xen] rapid block device plug/unplug leads to crash (Don Dutile ) [308971]
- [net] fix refcnt leak in optimistic dad handling (Neil Horman ) [423791]
- [net] ixgb: resync upstream and transmit hang fixes (Andy Gospodarek ) [252002]
- [xen] kernel: cpu frequency scaling (Rik van Riel ) [251969]
- [md] dm snapshot: excessive memory usage (Milan Broz ) [421451]
- [md] dm-crypt: possible max_phys_segments violation (Milan Broz ) [421441]
- [xen] xenbus has use-after-free (Don Dutile ) [249728]
- [fs] cifs: update CHANGES file and version string (Jeff Layton ) [417961]
- [fs] cifs: endian conversion problem in posix mkdir (Jeff Layton ) [417961]
- [fs] cifs: corrupt data with cached dirty page write (Jeff Layton ) [329431]
- [fs] cifs: missing mount helper causes wrong slash (Jeff Layton ) [417961]
- [fs] cifs: fix error message about packet signing (Jeff Layton ) [417961]
- [fs] cifs: shut down cifsd when signing mount fails (Jeff Layton ) [417961]
- [fs] cifs: reduce corrupt list in find_writable_file (Jeff Layton ) [417961]
- [fs] cifs: fix memory leak in statfs to old servers (Jeff Layton ) [417961]
- [fs] cifs: buffer overflow due to corrupt response (Jeff Layton ) [373001]
- [fs] cifs: log better errors on failed mounts (Jeff Layton ) [417961]
- [fs] cifs: oops on second mount to same server (Jeff Layton ) [373741]
- [fs] cifs: fix spurious reconnect on 2nd peek (Jeff Layton ) [417961]
- [fs] cifs: bad handling of EAGAIN on kernel_recvmsg (Jeff Layton ) [336501]
- [fs] cifs: small fixes to make cifs-1.50c compile (Jeff Layton ) [417961]
- [net] cifs: stock 1.50c import (Jeff Layton ) [417961]
- [nfs4] client: set callback address properly (Steve Dickson ) [264721]
- [sched] fair scheduler (Peter Zijlstra ) [250589]
- [net] s2io: correct VLAN frame reception (Andy Gospodarek ) [354451]
- [net] s2io: allow VLAN creation on interfaces (Andy Gospodarek ) [354451]
- [mm] soft lockups when allocing mem on large systems (Doug Chapman ) [281381]
- [md] dm mpath: hp retry if not ready (Dave Wysochanski ) [208261]
- [md] dm mpath: add retry pg init (Dave Wysochanski ) [208261]
- [md] dm mpath: add hp handler (Dave Wysochanski ) [208261]
- [x86] fix race with 'endflag' in NMI setup code (Prarit Bhargava ) [357391]
- [xen] fix behavior of invalid guest page mapping (Markus Armbruster ) [254208]
- [misc] tux: get rid of O_ATOMICLOOKUP (Michal Schmidt ) [358661]
- [misc] Denial of service with wedged processes (Jerome Marchand ) [229882]
- [x86_64] fix race conditions in setup_APIC_timer (Geoff Gustafson ) [251869]

* Sat Dec 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-61.el5]
- [net] sunhme: fix failures on x86 (John W. Linville ) [254234]
- [ppc64] power6 SPURR support (Scott Moser ) [253114]
- [usb] fix for error path in rndis (Pete Zaitcev ) [236719]
- [ipmi] legacy ioport setup changes (Peter Martuccelli ) [279191]
- [ipmi] add PPC SI support (Peter Martuccelli ) [279191]
- [ipmi] remove superfluous semapahore from watchdog (Peter Martuccelli ) [279191]
- [ipmi] do not enable interrupts too early (Peter Martuccelli ) [279191]
- [ipmi] fix memory leak in try_init_dmi (Peter Martuccelli ) [279191]
- [net] sunrpc: lockd recovery is broken (Steve Dickson ) [240976]
- [fs] core dump file ownership (Don Howard ) [397001]
- [cpufreq] don't take sem in cpufreq_quick_get (Doug Chapman ) [253416]
- [cpufreq] remove hotplug cpu cruft (Doug Chapman ) [253416]
- [cpufreq] governor: use new rwsem locking in work cb (Doug Chapman ) [253416]
- [cpufreq] ondemand governor restructure the work cb (Doug Chapman ) [253416]
- [cpufreq] rewrite lock to eliminate hotplug issues (Doug Chapman ) [253416]
- [ppc64] spufs: context destroy vs readdir race (Scott Moser ) [387841]
- [scsi] update lpfc driver to 8.2.0.8 (Chip Coldwell ) [252989]
- [ppc64] utrace: fix PTRACE_GETVRREGS data (Roland McGrath ) [367221]
- [scsi] ipr: add dual SAS RAID controller support (Scott Moser ) [253398]
- [net] backport of functions for sk_buff manipulation (Andy Gospodarek ) [385681]
- [gfs2] recursive locking on rgrp in gfs2_rename (Abhijith Das ) [404711]
- [gfs2] check kthread_should_stop when waiting (David Teigland ) [404571]
- [dlm] don't print common non-errors (David Teigland ) [404561]
- [dlm] tcp: bind connections from known local address (David Teigland ) [358841]
- [dlm] block dlm_recv in recovery transition (David Teigland ) [358821]
- [dlm] fix memory leak in dlm_add_member (David Teigland ) [358791]
- [dlm] zero unused parts of sockaddr_storage (David Teigland ) [358771]
- [dlm] dump more lock values (David Teigland ) [358751]
- [gfs2] remove permission checks from xattr ops (Ryan O'Hara ) [307431]
- [x86] report_lost_ticks fix up (Prarit Bhargava ) [394581]
- [ppc64] SLB shadow buffer support (Scott Moser ) [253112]
- [ppc64] handle alignment faults on new FP load/store (Scott Moser ) [253111]
- [xen] PVFB frontend can send bogus screen updates (Markus Armbruster ) [370341]
- [nfs] let rpciod finish sillyrename then umount (Steve Dickson ) [253663]
- [nfs] fix a race in silly rename (Steve Dickson ) [253663]
- [nfs] clean up the silly rename code (Steve Dickson ) [253663]
- [nfs] infrastructure changes for silly renames (Steve Dickson ) [253663]
- [nfs] introducde nfs_removeargs and nfs_removeres (Steve Dickson ) [253663]
- [xen] avoid dom0 hang when disabling pirq's (Chris Lalancette ) [372741]
- [ppc64] cell: support for msi on axon (Scott Moser ) [253212]
- [ppc64] cell: enable rtas-based ptcal for xdr memory (Scott Moser ) [253212]
- [ppc64] cell: ddr2 memory driver for axon (Scott Moser ) [253212]
- [ppc64] spu: add temperature and throttling support (Scott Moser ) [279171]
- [ppc64] sysfs: support for add/remove cpu sysfs attr (Scott Moser ) [279171]
- [ppc64] cbe_cpufreq: fixes from 2.6.23-rc7 (Scott Moser ) [279171]
- [ppc64] typo with mmio_read_fixup (Scott Moser ) [253208]
- [ppc64] spufs: feature updates (Scott Moser ) [253208]
- [ppc64] export last_pid (Scott Moser ) [253208]
- [ppc64] cell: support pinhole-reset on blades (Scott Moser ) [253208]
- [s390] use IPL CLEAR for reipl under z/VM (Hans-Joachim Picht ) [386991]
- [net] sunrpc: fix hang due to eventd deadlock (Jeff Layton ) [246642]
- [misc] : misrouted interrupts deadlocks (Dave Anderson ) [247379]
- [fs] ignore SIOCIFCOUNT ioctl calls (Josef Bacik ) [310011]
- [ppc64] fixes PTRACE_SET_DEBUGREG request (Roland McGrath ) [253117]
- [fs] dm crypt: memory leaks and workqueue exhaustion (Milan Broz ) [360621]
- [md] dm: panic on shrinking device size (Milan Broz ) [360151]
- [md] dm: bd_mount_sem counter corruption (Milan Broz ) [360571]
- [fs] udf: fix possible leakage of blocks (Eric Sandeen ) [221282]
- [fs] udf: Fix possible data corruption (Eric Sandeen ) [221282]
- [fs] udf: support files larger than 1G (Eric Sandeen ) [221282]
- [fs] udf: add assertions (Eric Sandeen ) [221282]
- [fs] udf: use get_bh (Eric Sandeen ) [221282]
- [fs] udf: introduce struct extent_position (Eric Sandeen ) [221282]
- [fs] udf: use sector_t and loff_t for file offsets (Eric Sandeen ) [221282]
- [misc] use touch_softlockup_watchdog when no nmi wd (Prarit Bhargava ) [367251]
- [misc] backport upstream softlockup_tick code (Prarit Bhargava ) [367251]
- [misc] pass regs struct to softlockup_tick (Prarit Bhargava ) [336541]
- [misc] fix bogus softlockup warnings (Prarit Bhargava ) [252360]
- [x86] use pci=bfsort for certain boxes (Michal Schmidt ) [242990]
- [x86] Change command line size to 2048 (Prarit Bhargava ) [247477]
- [misc] systemtap uprobes: access_process_vm export (Frank Ch. Eigler ) [424991]
- [nfs] fix ATTR_KILL_S*ID handling on NFS (Jeff Layton ) [222330]
- [mm] oom: prevent from killing several processes (Larry Woodman ) [392351]

* Fri Dec 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-60.el5]
- [xen] x86: suppress bogus timer warning (Chris Lalancette ) [317201]
- [xen] ia64: saner default mem and cpu alloc for dom0 (Jarod Wilson ) [248967]
- [xen] x86_64: add stratus hooks into memory (Kimball Murray ) [247833]
- [ia64] mm: register backing store bug (Luming Yu ) [310801]
- [serial] irq -1 assigned to serial port (Luming Yu ) [227728]
- [utrace] s390 regs fixes (Roland McGrath ) [325451]
- [x86] use pci=bfsort on Dell R900 (Michal Schmidt ) [242990]
- [nfs] server support 32-bit client and 64-bit inodes (Peter Staubach ) [253589]
- [nfs] support 32-bit client and 64-bit inode numbers (Peter Staubach ) [253589]
- [dlm] Don't overwrite castparam if it's NULL (Patrick Caulfield ) [318061]
- [s390] panic with lcs interface as dhcp server (Hans-Joachim Picht ) [350861]
- [s390] qeth: do not free memory on failed init (Hans-Joachim Picht ) [330211]
- [s390] qeth: default performace_stats attribute to 0 (Hans-Joachim Picht ) [248897]
- [s390] qeth: create copy of skb for modification (Hans-Joachim Picht ) [354861]
- [s390] qeth: up sequence number for incoming packets (Hans-Joachim Picht ) [354851]
- [s390] qeth: use correct MAC address on recovery (Hans-Joachim Picht ) [241276]
- [s390] cio: handle invalid subchannel setid in stsch (Hans-Joachim Picht ) [354831]
- [s390] cio: Dynamic CHPID reconfiguration via SCLP (Hans-Joachim Picht ) [253120]
- [s390] cio: fix memory leak when deactivating (Hans-Joachim Picht ) [213272]
- [s390] cio: Device status validity (Hans-Joachim Picht ) [354821]
- [s390] cio: reipl fails after channel path reset (Hans-Joachim Picht ) [231306]
- [usb] reset LEDs on Dell keyboards (Pete Zaitcev ) [228674]
- [x86] hotplug: PCI memory resource mis-allocation (Konrad Rzeszutek ) [252260]
- [ppc64] Make the vDSO handle C++ unwinding correctly (David Howells ) [420551]
- [ppc64] add AT_NULL terminator to auxiliary vector (Vitaly Mayatskikh ) [231442]
- [x86] Add Greyhound Event based Profiling support (Bhavana Nagendra ) [314611]
- [nfs] reset any fields set in attrmask (Jeff Layton ) [242482]
- [nfs] Set attrmask on NFS4_CREATE_EXCLUSIVE reply (Jeff Layton ) [242482]
- [fs] proc: add /proc/<pid>/limits (Neil Horman ) [253762]
- [xen] ia64: make ioremapping work (Jarod Wilson ) [240006]
- [ia64] bte_unaligned_copy transfers extra cache line (Luming Yu ) [218298]
- [xen] inteface with stratus platform op (Kimball Murray ) [247841]
- [mm] xen: export xen_create_contiguous_region (Kimball Murray ) [247839]
- [mm] xen: memory tracking cleanups (Kimball Murray ) [242514]

* Tue Dec 11 2007 Don Zickus <dzickus@redhat.com> [2.6.18-59.el5]
- [net] ipv6: backport optimistic DAD (Neil Horman ) [246723]
- [crypto] aes: Rename aes to aes-generic (Herbert Xu ) [245954]
- [xen] ia64: fix free_irq_vector: double free (Aron Griffis ) [208599]
- [selinux] don't oops when using non-MLS policy (Eric Paris ) [223827]
- [net] qla3xxx: new 4032 does not work with VLAN (Marcus Barrow ) [253785]
- [ide] SB700 contains two IDE channels (Bhavana Nagendra ) [314571]
- [edac] fix return code in e752x_edac probe function (Aristeu Rozanski ) [231608]
- [scsi] cciss: disable refetch on P600 (Aron Griffis ) [251563]
- [misc] Intel Tolapai SATA and I2C support (Ivan Vecera ) [251086]
- [net] ibmveth: Checksum offload support (Scott Moser ) [254035]
- [misc] Allow a hyphenated range for isolcpus (Jonathan Lim ) [328151]
- [misc] sched: force /sbin/init off isolated cpus (Jonathan Lim ) [328091]
- [ia64] contig: show_mem cleanup output (George Beshers ) [221612]
- [ia64] discontig: show_mem cleanup output (George Beshers ) [221612]
- [ia64] show_mem printk cleanup (George Beshers ) [221612]
- [net] ppp_mppe: avoid using a copy of interim key (Michal Schmidt ) [248716]
- [ppc64] mpstat reports wrong per-processor stats (Scott Moser ) [212234]
- [net] labeled: memory leak calling secid_to_secctx (Eric Paris ) [250442]
- [misc] /proc/<pid>/environ stops at 4k bytes (Anton Arapov ) [308391]
- [net] kernel needs to support TCP_RTO_MIN (Anton Arapov ) [303011]
- [x86_64] kdump: shutdown gart on k8 systems (Prarit Bhargava ) [264601]
- [input] psmouse: add support to 'cortps' protocol (Aristeu Rozanski ) [248759]
- [nfs] nfs_symlink: allocate page with GFP_HIGHUSER (Jeff Layton ) [245042]
- [ia64] enable kprobe's trap code on slot 1 (Masami Hiramatsu ) [207107]
- [misc] Fix relay read start in overwrite mode (Masami Hiramatsu ) [250706]
- [misc] Fix relay read start position (Masami Hiramatsu ) [250706]
- [x86_64] 'ide0=noprobe' crashes the kernel (Michal Schmidt ) [241338]
- [ia64] proc/iomem wiped out on non ACPI kernel (George Beshers ) [257001]
- [net] CIPSO packets generate kernel unaligned access (Luming Yu ) [242955]
- [ia64] ioremap: fail mmaps with incompat attributes (Jarod Wilson ) [240006]
- [ia64] ioremap: allow cacheable mmaps of legacy_mem (Jarod Wilson ) [240006]
- [ia64] ioremap: avoid unsupported attributes (Jarod Wilson ) [240006]
- [ia64] ioremap: rename variables to match i386 (Jarod Wilson ) [240006]
- [ia64] validate and remap mmap requests (Jarod Wilson ) [240006]
- [ia64] kdump: deal with empty image (Doug Chapman ) [249724]
- [net] NetXen: allow module to unload (Konrad Rzeszutek ) [245751]
- [net] clean up in-kernel socket api usage (Neil Horman ) [246851]
- [hotplug] slot poweroff problem on systems w/o _PS3 (Prarit Bhargava ) [410611]
- [PPC64] kdump: fix irq distribution on ppc970 (Jarod Wilson ) [208659]
- [serial] support PCI Express icom devices (Chris Snook ) [243806]
- [xen] Rebase HV to 15502 (Bill Burns) [318891]

* Wed Nov 27 2007 Don Zickus <dzickus@redhat.com> [2.6.18-58.el5]
- Updated: [net] panic when mounting with insecure ports (Anton Arapov ) [294881]
- [kabitool] - fail on missing symbols (Jon Masters)

* Wed Nov 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-57.el5]
- [misc] lockdep: fix seqlock_init (Peter Zijlstra ) [329851]
- [ppc64] Remove WARN_ON from disable_msi_mode() (Scott Moser ) [354241]
- [GFS2] sysfs  file should contain device id (Bob Peterson ) [363901]
- [x86_64] update IO-APIC dest field to 8-bit for xAPIC (Dave Anderson ) [224373]
- [ia64] add global ACPI OpRegion handler for fw calls (Doug Chapman ) [262281]
- [ia64] add driver for ACPI methods to call native fw (Doug Chapman ) [262281]
- [ppc64] eHEA: ibm,loc-code not unique (Scott Moser ) [271821]
- [ata] SB800 SATA/IDE LAN support (Bhavana Nagendra ) [252961]
- [net] ibmveth: enable large rx buf pool for large mtu (Scott Moser ) [250827]
- [net] ibmveth: h_free_logical_lan err on pool resize (Scott Moser ) [250827]
- [net] ibmveth: fix rx pool deactivate oops (Scott Moser ) [250827]
- [gfs2] Fix ordering of page lock and transaction lock (Steven Whitehouse ) [303351]
- [net] panic when mounting with insecure ports (Anton Arapov ) [294881]
- [ia64] fix vga corruption with term blanking disabled (Jarod Wilson ) [291421]
- [ppc64] panic on DLPAR remove of eHEA (Scott Moser ) [253767]
- [ppc64] boot Cell blades with >2GB memory (Scott Moser ) [303001]
- [x86_64] Add NX mask for PTE entry (Jarod Wilson ) [232748]
- [hotplug] acpiphp: System error during PCI hotplug (Konrad Rzeszutek ) [243003]
- [misc] softirq: remove spurious BUG_ON's (Jarod Wilson ) [221554]
- [audit] collect events for segfaulting programs (Eric Paris ) [239061]
- [misc] cfq-iosched: fix deadlock on nbd writes (Jarod Wilson ) [241540]
- [scsi] stale residual on write following BUSY retry (Jonathan Lim ) [300871]
- ext3: orphan list check on destroy_inode (Eric Sandeen ) [269401]
- [scsi] always update request data_len with resid (George Beshers ) [282781]
- [misc] add vmcoreinfo support to kernel (Neil Horman ) [253850]
- [ia64] remove stack hard limit (Aron Griffis ) [251043]
- [fs] Fix unserialized task->files changing (Vitaly Mayatskikh ) [253866]
- [ide] allow disabling of drivers (Gerd Hoffmann ) [247982]
- [net] fail multicast with connection oriented socket (Anton Arapov ) [259261]
- [net] fix race condition in netdev name allocation (Neil Horman ) [247128]
- [char] tty: set pending_signal on return -ERESTARTSYS (Aristeu Rozanski ) [253873]
- [fs] aio: account for I/O wait properly (Jeff Moyer ) [253337]
- [x86_64] Switching to vsyscall64 causes oops (Jeff Burke ) [224541]
- [net] lvs syncdaemon causes high avg load on system (Anton Arapov ) [245715]
- [i2c] SB600/700/800 use same SMBus controller devID (Bhavana Nagendra ) [252286]
- [acpi] sbs: file permissions set incorrectly (Vitaly Mayatskikh ) [242565]
- [net] ipv6: support RFC4193 local unicast addresses (Neil Horman ) [252264]
- [misc] serial: fix console hang on HP Integrity (Doug Chapman ) [244054]
- [tux] fix crashes during shutdown (Ernie Petrides ) [244439]
- [usb] Support for EPiC-based io_edgeport devices (Jarod Wilson ) [249760]
- [misc] Prevent NMI watchdog triggering during sysrq-T (Konrad Rzeszutek ) [248392]
- [hotplug] acpiphp: 'cannot get bridge info' with PCIe (Konrad Rzeszutek ) [248571]
- [misc] serial: assert DTR for serial console devices (Michal Schmidt ) [244728]
- [net] sctp: rewrite receive buffer management code (Neil Horman ) [246722]
- [net] NetXen: MSI: failed interrupt after fw enabled (Konrad Rzeszutek ) [246019]
- [cifs] make demux thread ignore signals from userspace (Jeff Layton ) [245674]
- [ia64] misc DBS cleanup (Luming Yu ) [245217]
- [misc] Remove non-existing SB600 raid define (Prarit Bhargava ) [244038]

* Tue Nov 13 2007 Don Zickus <dzickus@redhat.com> [2.6.18-56.el5]
- [fs] missing dput in do_lookup error leaks dentries (Eric Sandeen ) [363491] {CVE-2007-5494}
- [ppc] System cpus stuck in H_JOIN after migrating (Scott Moser ) [377901]
- [scsi] ibmvSCSI: Unable to continue migrating lpar after errors (Scott Moser ) [377891]
- [scsi] ibmvSCSI: client can't handle deactive/active device from server (Scott Moser ) [257321]
- [audit] still allocate contexts when audit is disabled (Alexander Viro ) [360841]

* Tue Nov 06 2007 Don Zickus <dzickus@redhat.com> [2.6.18-55.el5]
- Revert: [misc] Denial of service with wedged processes (Jerome Marchand ) [229882] {CVE-2006-6921}
- [autofs4] fix race between mount and expire (Ian Kent ) [354621]
- [net] ieee80211: off-by-two integer underflow (Anton Arapov ) [346401] {CVE-2007-4997}
- [fs] sysfs: fix race condition around sd->s_dentry (Eric Sandeen ) [243728] {CVE-2007-3104}
- [fs] sysfs: fix condition check in sysfs_drop_dentry() (Eric Sandeen ) [243728] {CVE-2007-3104}
- [fs] sysfs: store inode nrs in s_ino (Eric Sandeen ) [243728] {CVE-2007-3104}
- [nfs] v4: umounts oops in shrink_dcache_for_umount (Steve Dickson ) [254106]
- [net] tg3: Fix performance regression on 5705 (Andy Gospodarek ) [330181]
- [net] forcedeth: MSI interrupt bugfix (Andy Gospodarek ) [353281]
- [ppc] kexec/kdump kernel hung on Power5+ and Power6 (Scott Moser ) [245346]

* Mon Oct 22 2007 Don Zickus <dzickus@redhat.com> [2.6.18-54.el5]
- [misc] Denial of service with wedged processes (Jerome Marchand ) [229882] {CVE-2006-6921}
- [alsa] Convert snd-page-alloc proc file to use seq_file (Jerome Marchand ) [297771] {CVE-2007-4571}
- [x86] Fixes for the tick divider patch (Chris Lalancette ) [315471]
- [mm] ia64: flush i-cache before set_pte (Luming Yu ) [253356]
- [fs] jbd: wait for t_sync_datalist buffer to complete (Eric Sandeen ) [250537]
- [audit] improper handling of audit_log_start return values (Eric Paris ) [335731]
- [cifs] fix memory corruption due to bad error handling (Jeff Layton ) [336501]
- [net] bnx2: Add PHY workaround for 5709 A1 (Andy Gospodarek ) [317331]

* Wed Oct 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-53.el5]
- [GFS2] handle multiple demote requests (Wendy Cheng ) [295641]
- [scsi] megaraid_sas: kabi fix for /proc entries (Chip Coldwell ) [323231]
- [sound] allow creation of null parent devices (Brian Maly ) [323771]

* Wed Sep 26 2007 Don Zickus <dzickus@redhat.com> [2.6.18-52.el5]
- [net] iwlwifi: avoid BUG_ON in tx cmd queue processing (John W. Linville ) [306831]
- [GFS2] Get super block a different way (Steven Whitehouse ) [306621]

* Tue Sep 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-51.el5]
- [GFS2] dlm: schedule during recovery loops (David Teigland ) [250464]
- Revert: [pata] IDE (siimage) panics when DRAC4 reset (John Feeney ) [212391]

* Mon Sep 24 2007 Don Zickus <dzickus@redhat.com> [2.6.18-50.el5]
- Revert: [net] bonding: convert timers to workqueues (Andy Gospodarek ) [210577]
- [pata] enable IDE (siimage) DRAC4 (John Feeney ) [212391]
- [GFS2] gfs2_writepage(s) workaround (Wendy Cheng ) [252392]
- [scsi] aacraid: Missing ioctl() permission checks (Vitaly Mayatskikh ) [298381] {CVE-2007-4308}
- [GFS2] Solve journaling/{release|invalidate}page issues (Steven Whitehouse ) [253008]
- [x86_64] syscall vulnerability (Anton Arapov ) [297881] {CVE-2007-4573}
- [GFS2] Fix i_cache stale entry (Wendy Cheng ) [253756]
- [GFS2] deadlock running revolver load with lock_nolock (Benjamin Marzinski ) [288581]
- [net] s2io: check for error_state in ISR (more) (Scott Moser ) [276871]

* Thu Sep 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-49.el5]
- [sata] libata probing fixes and other cleanups (Jeff Garzik ) [260281]
- [net] cxgb3: backport fixups and sysfs corrections (Andy Gospodarek ) [252243]

* Mon Sep 17 2007 Don Zickus <dzickus@redhat.com> [2.6.18-48.el5]
- [net] s2io: check for error_state in ISR (Scott Moser ) [276871]
- [fs] ext3: ensure do_split leaves enough free space in both blocks (Eric Sandeen ) [286501]
- [kabi] whitelist GFS2 export symbols to allow driver updates (Jon Masters) [282901]
- [gfs2] allow process to handle multiple flocks on a file (Abhijith Das ) [272021]
- [gfs2] operations hang after mount--RESEND (Bob Peterson ) [276631]
- [scsi] qlogic: fix nvram/vpd update memory corruptions (Marcus Barrow ) [260701]
- [fs] Reset current->pdeath_signal on SUID binary execution (Peter Zijlstra) [251119] {CVE-2007-3848}
- [gfs2] mount hung after recovery (Benjamin Marzinski ) [253089]
- [GFS2] Move inode delete logic out of blocking_cb (Wendy Cheng ) [286821]
- [dlm] Make dlm_sendd cond_resched more (Patrick Caulfield ) [250464]
- [x86_64] fix 32-bit ptrace access to debug registers (Roland McGrath ) [247427]
- [autofs4] fix deadlock during directory create (Ian Kent ) [253231]
- [nfs] enable 'nosharecache' mounts fixes (Steve Dickson ) [243913]
- [usb] usblcd: Locally triggerable memory consumption (Anton Arapov ) [276011] {CVE-2007-3513}
- [misc] Bounds check ordering issue in random driver (Anton Arapov ) [275971] {CVE-2007-3105}

* Tue Sep 11 2007 Don Zickus <dzickus@redhat.com> [2.6.18-47.el5]
- [ppc64] Fix SPU slb size and invalidation on hugepage faults (Scott Moser ) [285981]
- [s390] qdio: Refresh buffer states for IQDIO Asynch output queue (Hans-Joachim Picht ) [222181]
- [scsi] fusion: allow VMWare's emulator to work again (Chip Coldwell ) [279571]

* Mon Sep 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-46.el5]
- [XEN] x86: 32-bit ASID mode hangs dom0 on AMD (Chris Lalancette ) [275371]
- [scsi] megaraid_sas: intercept cmd timeout and throttle io (Chip Coldwell ) [245184 247581]
- [s390] hypfs: inode corruption due to missing locking (Brad Hinson ) [254169]
- [Xen] Allow 32-bit Xen to kdump >4G physical memory (Stephen C. Tweedie ) [251341]
- [ptrace] NULL pointer dereference triggered by ptrace (Anton Arapov ) [275991] {CVE-2007-3731}
- [XEN] ia64: allocating with GFP_KERNEL in interrupt context fix (Josef Bacik ) [279141]

* Tue Sep 04 2007 Don Zickus <dzickus@redhat.com> [2.6.18-45.el5]
- [XEN] Update spec file to provide specific xen ABI version (Stephen C. Tweedie ) [271981]
- [scsi] qla2xxx: nvram/vpd updates produce soft lockups and system hangs (Marcus Barrow ) [260701]
- [scsi] iscsi: borked kmalloc  (Mike Christie ) [255841]
- [net] qla3xxx: Read iSCSI target disk fail (Marcus Barrow ) [246123]
- [net] igmp: check for NULL when allocating GFP_ATOMIC skbs (Neil Horman ) [252404]
- [mm] madvise call to kernel loops forever (Konrad Rzeszutek ) [263281]

* Mon Aug 27 2007 Don Zickus <dzickus@redhat.com> [2.6.18-44.el5]
- [misc] re-export some symbols as EXPORT_SYMBOL_GPL (Jon Masters ) [252377]
- [xen] ia64: set NODES_SHIFT to 8 (Doug Chapman ) [254050]
- [xen] Fix privcmd to remove nopage handler (Chris Lalancette ) [249409]
- [xen] increase limits to boot on large ia64 platforms (Doug Chapman ) [254062]
- [autofs] autofs4 - fix race between mount and expire (Ian Kent ) [236875]
- [nfs] NFS4: closes and umounts are racing (Steve Dickson ) [245062]
- [GFS2] Fix lock ordering of unlink (Steven Whitehouse ) [253609]
- [openib] Fix two ipath controllers on same subnet (Doug Ledford ) [253005]
- [net] tg3: update to fix suspend/resume problems (Andy Gospodarek ) [253988]
- [GFS2] distributed mmap test cases deadlock (Benjamin Marzinski ) [248480]
- [GFS2] Fix inode meta data corruption (Wendy Cheng ) [253590]
- [GFS2] bad mount option causes panic with NULL superblock pointer (Abhijith Das ) [253921]
- [fs] hugetlb: fix prio_tree unit (Konrad Rzeszutek ) [253930]
- [misc] Microphone stops working (John Feeney ) [240716]
- [GFS2] glock dump dumps glocks for all file systems (Abhijith Das ) [253238]
- [scsi] qla2xxx: disable MSI-X by default (Marcus Barrow ) [252410]

* Tue Aug 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-43.el5]
- [XEN] remove assumption first numa node discovered is node0 (Jarod Wilson ) [210078]

* Mon Aug 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-42.el5]
- [GFS2] More problems unstuffing journaled files (Bob Peterson ) [252191]
- [DLM] Reuse connections rather than freeing them (Patrick Caulfield ) [251179]
- [ppc] EEH: better status string detection (Scott Moser ) [252405]
- [scsi] cciss: set max command queue depth (Tomas Henzl ) [251167]
- [audit] Stop multiple messages from being printed (Eric Paris ) [252358]
- [scsi] uninitialized field in gdth.c (Chip Coldwell ) [245550]
- [scsi] SATA RAID 150-4/6 do not support 64-bit DMA (Chip Coldwell ) [248327]
- [gfs2] fix truncate panic (Wendy Cheng ) [251053]
- [gfs2] panic after can't parse mount arguments  (Benjamin Marzinski ) [253289]
- [fs] CIFS: fix deadlock in cifs_get_inode_info_unix (Jeff Layton ) [249394]
- [sound] support ad1984 codec (Brian Maly ) [252373]
- [scsi] fix iscsi write handling regression (Mike Christie ) [247827]
- [ppc] Fix detection of PCI-e based devices (Doug Ledford ) [252085]
- [gfs2] unstuff quota inode (Abhijith Das ) [250772]
- [net] fix DLPAR remove of eHEA logical port (Scott Moser ) [251370]
- [gfs2] hang when using a large sparse quota file (Abhijith Das ) [235299]
- [x86_64] Fix MMIO config space quirks (Bhavana Nagendra ) [252397]
- [misc] Convert cpu hotplug notifiers to use raw_notifier (Peter Zijlstra ) [238571]
- [sound] fix panic in hda_codec (Brian Maly ) [251854]
- [mm] separate mapped file and anonymous pages in show_mem() output. (Larry Woodman ) [252033]
- [misc] Fix broken AltSysrq-F (Larry Woodman ) [251731]
- [scsi] cciss: increase max sectors to 2048 (Tomas Henzl ) [248121]
- Revert [gfs2] remounting w/o acl option leaves acls enabled (Bob Peterson ) [245663]

* Thu Aug 16 2007 Don Zickus <dzickus@redhat.com> [2.6.18-41.el5]
- Revert [ia64] validate and remap mmap requests (Jarod Wilson ) [240006]

* Tue Aug 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-40.el5]
- [net] s2io: update to driver version 2.0.25.1 (Andy Gospodarek ) [223033]
- [XEN] ia64: use panic_notifier list (Kei Tokunaga ) [250456]
- [XEN] ia64: support nvram (Kei Tokunaga ) [250203]
- [XEN] Allow dom0 to boot with greater than 2 vcpus (Kei Tokunaga ) [250441]
- [XEN] Fix MCE errors on AMD-V (Bhavana Nagendra ) [251435]
- [XEN] set correct paging bit identifier when NP enabled (Chris Lalancette ) [250857]
- [XEN] ia64: fix for hang when running gdb (Doug Chapman ) [246482]
- [XEN] AMD-V fix for W2k3 guest w/ Nested paging (Bhavana Nagendra ) [250850]
- [XEN] blktap tries to access beyond end of disk (Kei Tokunaga ) [247696]
- [ia64] fsys_gettimeofday leaps days if it runs with nojitter (Luming Yu ) [250825]
- [x86] Blacklist for HP DL585G2 and HP dc5700 (Tony Camuso ) [248186]
- [misc] Missing critical phys_to_virt in lib/swiotlb.c (Anton Arapov ) [248102]
- [mm] Prevent the stack growth into hugetlb reserved regions (Konrad Rzeszutek ) [247658]
- [scsi] fix qla4xxx underrun and online handling (Mike Christie ) [242828]
- [sound] Audio playback does not work (John Feeney ) [250269]
- [XEN] ia64: allow guests to vga install (Jarod Wilson ) [249076]
- [net] forcedeth: optimize the tx data path (Andy Gospodarek ) [252034]
- [agp] 945/965GME: bridge id, bug fix, and cleanups (Geoff Gustafson ) [251166]
- [net] tg3: pci ids missed during backport (Andy Gospodarek ) [245135]
- [misc] workaround for qla2xxx vs xen swiotlb (Rik van Riel ) [219216]
- [XEN] netfront: Avoid deref'ing skb after it is potentially freed. (Herbert Xu ) [251905]
- [ia64] validate and remap mmap requests (Jarod Wilson ) [240006]
- [ppc] DLPAR REMOVE I/O resource failed (Scott Moser ) [249617]
- [XEN] ia64: Cannot use e100 and IDE controller (Kei Tokunaga ) [250454]
- [wireless] iwlwifi: update to version 1.0.0 (John W. Linville ) [223560 250675]
- [ppc] make eHCA driver use remap_4k_pfn in 64k kernel (Scott Moser ) [250496]
- [audit] sub-tree signal handling fix (Alexander Viro ) [251232]
- [audit] sub-tree memory leaks (Alexander Viro ) [251160]
- [audit] sub-tree cleanups (Alexander Viro ) [248416]
- [GFS2] invalid metadata block (Bob Peterson ) [248176]
- [XEN] use xencons=xvc by default on non-x86 (Aron Griffis ) [249100]
- [misc] i915_dma: fix batch buffer security bit for i965 chipsets (Aristeu Rozanski ) [251188] {CVE-2007-3851}
- [Xen] Fix restore path for 5.1 PV guests (Chris Lalancette ) [250420]
- [x86] Support mobile processors in fid/did to frequency conversion (Bhavana Nagendra ) [250833]
- [dlm] fix basts for granted PR waiting CW (David Teigland ) [248439]
- [scsi] PCI shutdown for cciss driver (Chip Coldwell ) [248728]
- [scssi] CCISS support for P700m (Chip Coldwell ) [248735]
- [net] forcedeth: fix nic poll (Herbert Xu ) [245191]
- [ppc] 4k page mapping support for userspace 	in 64k kernels (Scott Moser ) [250144]
- [net] tg3: small update for kdump fix (Andy Gospodarek ) [239782]
- [ppc] Cope with PCI host bridge I/O window not starting at 0 (Scott Moser ) [242937]
- [ata]: Add additional device IDs for SB700 (Prarit Bhargava ) [248109]
- [fs] - fix VFAT compat ioctls on 64-bit systems (Eric Sandeen ) [250666] {CVE-2007-2878}
- [fs] - Move msdos compat ioctl to msdos dir (Eric Sandeen ) [250666]

* Thu Aug 09 2007 Don Zickus <dzickus@redhat.com> [2.6.18-39.el5]
- [net] e1000: add support for Bolton NICs (Bruce Allan ) [251221]
- [net] e1000: add support for HP Mezzanine cards (Bruce Allan ) [251214]
- [net] igb: initial support for igb netdriver (Andy Gospodarek ) [244758]
- [net] e1000e: initial support for e1000e netdriver (Andy Gospodarek ) [240086]

* Fri Aug 03 2007 Don Zickus <dzickus@redhat.com> [2.6.18-38.el5]
- [ppc] No Boot/Hang response for PCI-E errors (Scott Moser ) [249667]
- [GFS2] Reduce number of gfs2_scand processes to one (Steven Whitehouse ) [249905]
- [scsi] Adaptec: Add SC-58300 HBA PCI ID (Konrad Rzeszutek ) [249275]
- [GFS2] Fix bug relating to inherit_jdata flag on inodes (Steven Whitehouse ) [248576]
- [ppc] Disable PCI-e completion timeouts on I/O Adapters (Scott Moser ) [232004]
- [x86] Fix tscsync frequency transitions (Bhavana Nagendra ) [245082]
- [CIFS] respect umask when unix extensions are enabled (Jeff Layton ) [246667]
- [CIFS] fix signing sec= mount options (Jeff Layton ) [246595]
- [XEN] netloop: Do not clobber cloned skb page frags (Herbert Xu ) [249683]

* Mon Jul 30 2007 Don Zickus <dzickus@redhat.com> [2.6.18-37.el5]
- [net] Using mac80211 in ad-hoc mode can result in a kernel panic (John W. Linville ) [223558]
- [ppc] Axon memory does not handle double bit errors (Scott Moser ) [249910]
- [xen] x86: HV workaround for invalid PAE PTE clears (Chris Lalancette ) [234375]
- [scsi] Update stex driver (Jeff Garzik ) [241074]
- [scsi] cciss: Re-add missing kmalloc (Prarit Bhargava ) [249104]
- [GFS2] Fix an oops in the glock dumping code (Steven Whitehouse ) [248479]
- [GFS2] locksmith/revolver deadlocks (Steven Whitehouse ) [249406]
- [xen] race loading xenblk.ko and scanning for LVM partitions (Richard Jones ) [247265]

* Fri Jul 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-36.el5]
- [NFS] Re-enable force umount (Steve Dickson ) [244949]
- [sata] regression in support for third party modules (Jeff Garzik ) [248382]
- [utrace] set zombie leader to EXIT_DEAD before release_task (Roland McGrath ) [248621]

* Wed Jul 18 2007 Don Zickus <dzickus@redhat.com> [2.6.18-35.el5]
- [XEN] fix time going backwards in gettimeofday (Rik van Riel ) [245761]
- [GFS2] soft lockup in rgblk_search (Bob Peterson ) [246114]
- [DLM] fix NULL reference in send_ls_not_ready (David Teigland ) [248187]
- [DLM] Clear othercon pointers when a connection is closed (David Teigland ) [220538]

* Thu Jul 12 2007 Don Zickus <dzickus@redhat.com> [2.6.18-34.el5]
- [wireless] iwlwifi: add driver (John W. Linville ) [223560]
- [XEN] make crashkernel=foo@16m work (Gerd Hoffmann ) [243880]
- [XEN] ia64: HV built with crash_debug=y does not boot on NUMA machine (Kei Tokunaga ) [247843]
- [edac] allow edac to panic with memory corruption on non-kdump kernels (Don Zickus ) [237950]
- [GFS2] Mounted file system won't suspend (Steven Whitehouse ) [192082]
- [GFS2] soft lockup detected in databuf_lo_before_commit (Bob Peterson ) [245832]
- [sata] Add Hitachi HDS7250SASUN500G 0621KTAWSD to NCQ blacklist (Prarit Bhargava ) [247627]
- [PCI] unable to reserve mem region on module reload (Scott Moser ) [247701 247400]
- [PPC] eHEA driver can cause kernel panic on recv of VLAN packets (Scott Moser ) [243009]
- [PPC] Fix 64K pages with kexec on native hash table (Scott Moser ) [242550]
- Reverts: Mambo driver on ppc64 [208320]

* Mon Jul 09 2007 Don Zickus <dzickus@redhat.com> [2.6.18-33.el5]
- [XEN] ia64: Windows guest cannot boot with debug mode (Kei Tokunaga ) [245668]
- [XEN] ia64: SMP Windows guest boot fails sometimes (Kei Tokunaga ) [243870]
- [XEN] ia64: Dom0 boot fails on NUMA hardware (Kei Tokunaga ) [245275]
- [XEN] ia64: Windows guest sometimes panic by incorrect ld4.s emulation (Kei Tokunaga ) [243865]
- [XEN] ia64: boot 46 GuestOS makes Dom0 hang (Kei Tokunaga ) [245667]
- [XEN] ia64: HVM guest hangs on vcpu migration (Kei Tokunaga ) [233971]
- [XEN] ia64: Cannot create guest domain due to rid problem (Kei Tokunaga ) [242040]
- [XEN] ia64: HVM domain creation panics if xenheap is not enough. (Kei Tokunaga ) [240108]
- [XEN] ia64: DomU panics by save/restore (Kei Tokunaga ) [243866]
- [XEN] ia64: Guest OS hangs on IPF montetito (Kei Tokunaga ) [245637]
- [xen] Guest access to MSR may cause system crash/data corruption (Bhavana Nagendra ) [245186]
- [xen] Windows HVM guest image migration causes blue screen (Bhavana Nagendra ) [245169]
- [xen] ia64: enable blktap driver (Jarod Wilson ) [216293]
- [scsi] check portstates before invoking target scan (David Milburn ) [246023]
- [nfs] NFSd oops when exporting krb5p mount (Steve Dickson ) [247120]
- [misc] Overflow in CAPI subsystem (Anton Arapov ) [231072] {CVE-2007-1217}
- [dlm] A TCP connection to DLM port blocks DLM operations (Patrick Caulfield ) [245892] {CVE-2007-3380}
- [dm] allow invalid snapshots to be activated (Milan Broz ) [244215]
- [gfs2] inode size inconsistency (Wendy Cheng ) [243136]
- [gfs2] Remove i_mode passing from NFS File Handle (Wendy Cheng ) [243136]
- [gfs2] Obtaining no_formal_ino from directory entry (Wendy Cheng ) [243136]
- [gfs2] EIO error from gfs2_block_truncate_page (Wendy Cheng ) [243136]
- [gfs2] remounting w/o acl option leaves acls enabled (Bob Peterson ) [245663]
- [GFS2] igrab of inode in wrong state (Steven Whitehouse ) [245646]
- [audit] subtree watching cleanups (Alexander Viro ) [182624]

* Mon Jun 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-32.el5]
- [ppc64] Data buffer miscompare (Konrad Rzeszutek ) [245332]
- [xen] fix kexec/highmem failure (Gerd Hoffmann ) [245585]
- [audit] kernel oops when audit disabled with files watched (Eric Paris ) [245164]
- [scsi] Update aic94xx and libsas to 1.0.3 (Ryan Powers ) [224694]
- [xen] ia64: kernel-xen panics when dom0_mem is specified(2) (Kei Tokunaga ) [217593]
- [md] fix EIO on writes after log failure (Jonathan Brassow ) [236271]
- [net] bonding: convert timers to workqueues (Andy Gospodarek ) [210577]
- [scsi] cciss driver updates (Tomas Henzl ) [222852]
- [sata] combined mode regression fix (Jeff Garzik ) [245052]
- Reverts: [audit] protect low memory from user mmap operations (Eric Paris ) [233021]

* Thu Jun 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-31.el5]
- [firewire] New stack technology preview (Jay Fenlason ) [182183]
- [xen] kdump/kexec support (Gerd Hoffmann ) [212843]
- [xen] Add AMD-V support for domain live migration (Chris Lalancette ) [222131]
- [GFS2] assertion failure after writing to journaled file, umount (Bob Peterson ) [243899]
- [pata] IDE (siimage) panics when DRAC4 reset (John Feeney ) [212391]
- [agp] Fix AMD-64 AGP aperture validation (Bhavana Nagendra ) [236826]
- [x86_64] C-state divisor not functioning correctly  (Bhavana Nagendra ) [235404]
- [i2c] SMBus does not work on ATI/AMD SB700 chipset (Bhavana Nagendra ) [244150]
- [ide] Cannot find IDE device with ATI/AMD SB700 (Bhavana Nagendra ) [244150]
- [pci] PCI-X/PCI-Express read control interface (Bhavana Nagendra ) [234335]
- [pata] IDE hotplug support for Promise pata_pdc2027x (Scott Moser ) [184774]

* Thu Jun 21 2007 Don Zickus <dzickus@redhat.com> [2.6.18-30.el5]
- [md] add dm rdac hardware handler (Mike Christie ) [184635]
- [sound]  ALSA update (1.0.14) (Brian Maly ) [227671 240713 223133 238004 223142 244672]
- [xen] : AMD's ASID implementation  (Bhavana Nagendra ) [242932]
- [x86_64] Fix casting issue in tick divider patch (Prarit Bhargava ) [244861]
- [fs] setuid program unable to read own /proc/pid/maps file (Konrad Rzeszutek ) [221173]
- [x86_64] Fixes system panic during boot up with no memory in Node 0 (Bhavana Nagendra ) [218641]
- [nfs] closes and umounts are racing.  (Steve Dickson ) [225515]
- [security] allow NFS nohide and SELinux to work together (Eric Paris ) [219837]
- [ia64] Altix ACPI support (Greg Edwards ) [223577]
- [net] ixgb: update to driver version 1.0.126-k2 (Bruce Allan ) [223380]
- [net] Update netxen_nic driver to version 3.x.x (Konrad Rzeszutek ) [244711]
- [misc] utrace update (Roland McGrath ) [229886 228397 217809 210693]
- [misc] disable pnpacpi on IBM x460 (Brian Maly ) [243730]
- [gfs2] posix lock fixes (David Teigland ) [243195]
- [gfs2] panic in unlink (Steven Whitehouse ) [239737]
- [input] i8042_interrupt() race can deliver bytes swapped to serio_interrupt() (Markus Armbruster ) [240860]
- [s390] qdio: system hang with zfcp in case of adapter problems (Jan Glauber ) [241298]
- [net] Fix tx_checksum flag bug in qla3xxx driver (Marcus Barrow ) [243724]
- [openib] Update OFED code to 1.2 (Doug Ledford ) [225581]
- [openib] kernel backports for OFED 1.2 update (Doug Ledford ) [225581]
- [ppc64] donate cycles from dedicated cpu (Scott Moser ) [242762]
- [scsi] RAID1 goes 'read-only' after resync (Chip Coldwell ) [231040]
- [md] move fn call that could block outside spinlock (Jonathan Brassow ) [242069]
- [fs] FUSE: Minor vfs change (Eric Sandeen ) [193720]
- [net] s2io: Native Support for PCI Error Recovery (Scott Moser ) [228052]
- [xen] x86_64: Fix FS/GS registers for VT bootup (Rik van Riel ) [224671]
- [misc] Add RHEL version info to version.h (Konrad Rzeszutek ) [232534]
- Revert: [mm] memory tracking patch only partially applied to Xen kernel (Kimball Murray ) [242514]
- Revert: [x86_64] Set CONFIG_CALGARY_IOMMU_ENABLED_BY_DEFAULT=n (Konrad Rzeszutek ) [222035]
- Revert: [ppc64] Oprofile kernel module does not distinguish PPC 970MP  (Janice M. Girouard ) [216458]

* Mon Jun 18 2007 Don Zickus <dzickus@redhat.com> [2.6.18-29.el5]
- [xen] Expand VNIF number per guest domain to over four (Kei Tokunaga ) [223908]
- [xen] change interface version for 3.1 (Kei Tokunaga ) [242989]
- [xen] ia64: Fix PV-on-HVM driver (Kei Tokunaga ) [242144]
- [xen] ia64: use generic swiotlb.h header (Kei Tokunaga ) [242138]
- [xen] ia64: xm save/restore does not work (Kei Tokunaga ) [240858]
- [xen] ia64: Skip MCA setup on domU (Kei Tokunaga ) [242143]
- [xen] ia64: Cannot measure process time accurately (Kei Tokunaga ) [240107]
- [xen] Support new xm command: xm trigger (Kei Tokunaga ) [242140]
- [xen] ia64: Fix for irq_desc() missing in new upstream (Kei Tokunaga ) [242137]
- [xen] ia64: Set IRQ_PER_CPU status on percpu IRQs (Kei Tokunaga ) [242136]
- [xen] ia64: improve performance of system call (Kei Tokunaga )
- [xen] ia64: para domain vmcore does not work under crash (Kei Tokunaga ) [224047]
- [xen] ia64: kernel-xen panics when dom0_mem=4194304 is specified (Kei Tokunaga ) [217593]
- [xen] ia64: evtchn_callback fix and clean (Kei Tokunaga ) [242126]
- [xen] ia64: changed foreign domain page mapping semantic (Kei Tokunaga ) [242779]
- [xen] Change to new interrupt deliver mechanism (Kei Tokunaga ) [242125]
- [xen] ia64: Uncorrectable error makes hypervisor hung (MCA  support) (Kei Tokunaga ) [237549]
- [xen] Xen0 can not startX in tiger4 (Kei Tokunaga ) [215536]
- [xen] ia64: Fix xm mem-set hypercall on IA64 (Kei Tokunaga ) [241976]
- [xen] ia64: Fix HVM interrupts on IPF (Kei Tokunaga ) [242124]
- [xen] save/restore fix (Gerd Hoffmann ) [222128]
- [xen] blkback/blktap: fix id type (Gerd Hoffmann ) [222128]
- [xen] xen: blktap race #2 (Gerd Hoffmann ) [222128]
- [xen] blktap: race fix #1 (Gerd Hoffmann ) [222128]
- [xen] blktap: cleanups. (Gerd Hoffmann ) [242122]
- [xen] blktap: kill bogous flush (Gerd Hoffmann ) [222128]
- [xen] binmodal drivers: block backends (Gerd Hoffmann ) [222128]
- [xen] bimodal drivers, blkfront driver (Gerd Hoffmann ) [222128]
- [xen] bimodal drivers, pvfb frontend (Gerd Hoffmann ) [222128]
- [xen] bimodal drivers, protocol header (Gerd Hoffmann ) [222128]

* Fri Jun 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-28.el5]
- [net] netxen: initial support for NetXen 10GbE NIC (Andy Gospodarek ) [231724]
- [net] cxgb3: initial support for Chelsio T3 card (Andy Gospodarek ) [222453]
- [drm] agpgart and drm support for bearlake graphics (Geoff Gustafson ) [229091]
- [acpi] acpi_prt list incomplete (Kimball Murray ) [214439]
- [mm] memory tracking patch only partially applied to Xen kernel (Kimball Murray ) [242514]
- [x86_64] Fix TSC reporting for processors with constant TSC (Bhavana Nagendra ) [236821]
- [pci] irqbalance causes oops during PCI removal (Kimball Murray ) [242517]
- [net] Allow packet drops during IPSec larval state resolution (Vince Worthington ) [240902]
- [net] bcm43xx: backport from 2.6.22-rc1 (John W. Linville ) [213761]
- [net] softmac: updates from 2.6.21 (John W. Linville ) [240354]
- [net] e1000: update to driver version 7.3.20-k2 (Andy Gospodarek ) [212298]
- [net] bnx2: update to driver version 1.5.11 (Andy Gospodarek ) [225350]
- [net] ipw2[12]00: backports from 2.6.22-rc1 (John W. Linville ) [240868]
- [net] b44 ethernet driver update (Jeff Garzik ) [244133]
- [net] sky2: update to version 1.14 from 2.6.21 (John W. Linville ) [223631]
- [net] forcedeth: update to driver version 0.60 (Andy Gospodarek ) [221941]
- [net] bonding: update to driver version 3.1.2 (Andy Gospodarek ) [210577]
- [net] tg3: update to driver version 3.77 (Andy Gospodarek ) [225466 228125]
- [PPC] Update of spidernet to 2.0.A for Cell (Scott Moser ) [227612]
- [scsi] SPI DV fixup (Chip Coldwell ) [237889]
- [audit] audit when opening existing messege queue (Eric Paris ) [223919 ]
- [audit] audit=0 does not disable all audit messages (Eric Paris ) [231371]
- [net] mac80211 inclusion (John W. Linville ) [214982 223558]

* Fri Jun 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-27.el5]
- [sata] kabi fixes [203781]
- [audit] panic and kabi fixes [233021]

* Thu Jun 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-26.el5]
- [x86_64] sparsemem memmap allocation above 4G (grgustaf) [227426]
- [net] ip_conntrack_sctp: fix remotely triggerable panic (Don Howard ) [243244] {CVE-2007-2876}
- [usb] Strange URBs and running out IOMMU (Pete Zaitcev ) [230427]
- [audit] broken class-based syscall audit (Eric Paris ) [239887]
- [audit] allow audit filtering on bit & operations (Eric Paris ) [232967]
- [x86_64] Add L3 cache support to some processors (Bhavana Nagendra ) [236835]
- [x86_64] disable mmconf for HP dc5700 Microtower (Prarit Bhargava ) [219389]
- [misc] cpuset information leak (Prarit Bhargava ) [242811] {CVE-2007-2875}
- [audit] stop softlockup messages when loading selinux policy (Eric Paris ) [231392]
- [fs] nfs does not support leases, send correct error (Peter Staubach ) [216750]
- [dlm] variable allocation types (David Teigland ) [237558]
- [GFS2] Journaled data issues (Steven Whitehouse ) [238162]
- [ipsec] Make XFRM_ACQ_EXPIRES proc-tunable (Vince Worthington ) [241798]
- [GFS2] Missing lost inode recovery code (Steven Whitehouse ) [201012]
- [GFS2] Can't mount GFS2 file system on AoE device (Robert Peterson ) [243131]
- [scsi] update aacraid driver to 1.1.5-2437 (Chip Coldwell ) [197337]
- [scsi] cciss: ignore results from unsent commands on kexec boot (Neil Horman ) [239520]
- [scsi] update iscsi_tcp driver (Mike Christie ) [227739]
- [x86_64] Fix regression in kexec (Neil Horman ) [242648]
- [x86] rtc support for HPET legacy replacement mode (Brian Maly ) [220196]
- [scsi] megaraid_sas update (Chip Coldwell ) [225221]
- [fs] fix ext2 overflows on filesystems > 8T (Eric Sandeen ) [237188]
- [x86] MCE thermal throttling (Brian Maly ) [224187]
- [audit] protect low memory from user mmap operations (Eric Paris ) [233021]
- [scsi] Add FC link speeds. (Tom Coughlan ) [231888]
- [pci] I/O space mismatch with P64H2 (Geoff Gustafson ) [220511]
- [scsi] omnibus lpfc driver update (Chip Coldwell ) [227416]
- [scsi] Update qla2xxx firmware (Marcus Barrow ) [242534]
- [ide] Serverworks data corruptor (Alan Cox ) [222653]
- [scsi] update qla4xxx driver (Mike Christie ) [224435 223087 224203]
- [scsi] update iser driver (Mike Christie ) [234352]
- [dlm] fix debugfs ref counting problem (Josef Bacik ) [242807]
- [md] rh_in_sync should be allowed to block (Jonathan Brassow ) [236624]
- [md] unconditionalize log flush (Jonathan Brassow ) [235039]
- [GFS2] Add nanosecond timestamp feature  (Steven Whitehouse ) [216890]
- [GFS2] quota/statfs sign problem and cleanup _host structures (Steven Whitehouse ) [239686]
- [scsi] mpt adds DID_BUS_BUSY host status on scsi BUSY status (Chip Coldwell ) [228108]
- [scsi] fix for slow DVD drive (Chip Coldwell ) [240910]
- [scsi] update MPT Fusion to 3.04.04 (Chip Coldwell ) [225177]
- [GFS2] Fix calculation for spare log blocks with smaller block sizes (Steven Whitehouse ) [240435]
- [gfs2] quotas non-functional (Abhijith Das ) [201011]
- [gfs2] Cleanup inode number handling (Abhijith Das ) [242584]

* Wed Jun 13 2007 Don Zickus <dzickus@redhat.com> [2.6.18-25.el5]
- [s390] fix possible reboot hang on s390 (Jan Glauber ) [222181]
- [cifs] Update CIFS to version 1.48aRH (Jeff Layton ) [238597]
- [audit] Make audit config immutable in kernel (Eric Paris ) [223530]
- [dio] invalidate clean pages before dio write (Jeff Moyer ) [232715]
- [nfs] fixed oops in symlink code.  (Steve Dickson ) [218718]
- [mm] shared page table for hugetlb  page (Larry Woodman ) [222753]
- [nfs] Numerous oops, memory leaks and hangs found in upstream (Steve Dickson ) [242975]
- [misc] include taskstats.h in kernel-headers package (Don Zickus ) [230648]
- [ide] packet command error when installing rpm (John Feeney ) [229701]
- [dasd] export DASD status to userspace (Chris Snook ) [242681]
- [dasd] prevent dasd from flooding the console (Jan Glauber ) [229590]
- [s390] ifenslave -c causes kernel panic with VLAN and OSA Layer2 (Jan Glauber ) [219826]
- [s390] sclp race condition (Jan Glauber ) [230598]
- [audit] SAD/SPD flush have no security check (Eric Paris ) [233387]
- [audit] Add space in IPv6 xfrm audit record (Eric Paris ) [232524]
- [audit] Match proto when searching for larval SA (Eric Paris ) [234485]
- [audit] pfkey_spdget does not audit xrfm policy changes (Eric Paris ) [229720]
- [audit] collect audit inode information for all f*xattr commands (Eric Paris ) [229094]
- [audit] Initialize audit record sid information to zero (Eric Paris ) [223918]
- [audit] xfrm_add_sa_expire return code error (Eric Paris ) [230620]
- [net] NetLabel: Verify sensitivity level has a valid CIPSO mapping (Eric Paris ) [230255]
- [audit] pfkey_delete and xfrm_del_sa audit hooks wrong (Eric Paris ) [229732]
- [block] Fix NULL bio crash in loop worker thread (Eric Sandeen ) [236880]
- [x86]: Add Greyhound performance counter events (Bhavana Nagendra ) [222126]
- [dio] clean up completion phase of direct_io_worker() (Jeff Moyer ) [242116]
- [audit] add subtrees support (Alexander Viro ) [182624]
- [audit] AVC_PATH handling (Alexander Viro ) [224620]
- [audit] auditing ptrace (Alexander Viro ) [228384]
- [x86_64] Fix a cast in the lost ticks code (Prarit Bhargava ) [241781]
- [PPC64] DMA 4GB boundary protection  (Scott Moser ) [239569]
- [PPC64] MSI support for PCI-E (Scott Moser ) [228081]
- [ppc64] Enable DLPAR support for HEA (Scott Moser ) [237858]
- [ppc64] update ehea driver to latest version. (Janice M. Girouard ) [234225]
- [PPC64] spufs move to sdk2.1 (Scott Moser ) [242763]
- [PPC64] Cell SPE and Performance (Scott Moser ) [228128]
- [cpufreq] Identifies correct number of processors in powernow-k8 (Bhavana Nagendra ) [229716]

* Mon Jun 11 2007 Don Zickus <dzickus@redhat.com> [2.6.18-24.el5]
- [ipmi] update to latest (Peter Martuccelli ) [241928 212415 231436]
- [sata] super-jumbo update (Jeff Garzik ) [203781]
- [sata] move SATA drivers to drivers/ata (Jeff Garzik ) [203781]

* Fri Jun 08 2007 Don Zickus <dzickus@redhat.com> [2.6.18-23.el5]
- [dlm] Allow unprivileged users to create the default lockspace (Patrick Caulfield ) [241902]
- [dlm] fix queue_work oops (David Teigland ) [242070]
- [dlm] misc device removed when lockspace removal fails (David Teigland ) [241817]
- [dlm] dumping master locks (David Teigland ) [241821]
- [dlm] canceling deadlocked lock (David Teigland ) [238898]
- [dlm] wait for config check during join (David Teigland ) [206520]
- [dlm] fix new_lockspace error exit (David Teigland ) [241819]
- [dlm] cancel in conversion deadlock (David Teigland ) [238898]
- [dlm] add lock timeouts and time warning (David Teigland ) [238898]
- [dlm] block scand during recovery (David Teigland ) [238898]
- [dlm] consolidate transport protocols (David Teigland ) [219799]
- [audit] log targets of signals (Alexander Viro ) [228366]

* Thu Jun 07 2007 Don Zickus <dzickus@redhat.com> [2.6.18-22.el5]
- [scsi] Add kernel support for Areca RAID controllers (Tomas Henzl ) [205897]
- [s390] runtime switch for qdio performance statistics (Jan Glauber ) [228048]
- [nfs] enable 'nosharecache' mounts. (Steve Dickson ) [209964]
- [scsi] scsi_error.c - Fix lost EH commands (Chip Coldwell ) [227586]
- [s390] zfcp driver fixes (Jan Glauber ) [232002 232006]
- [misc] synclink_gt: fix init error handling  (Eric Sandeen) [210389]
- [edac] k8_edac: don't panic on PCC check (Aristeu Rozanski ) [237950]
- [mm] Prevent OOM-kill of unkillable children or siblings (Larry Woodman ) [222492]
- [aio] fix buggy put_ioctx call in aio_complete (Jeff Moyer ) [219497]
- [scsi] 3ware 9650SE not recognized by updated  3w-9xxx module (Chip Coldwell ) [223465]
- [scsi] megaraid: update version reported by  MEGAIOC_QDRVRVER (Chip Coldwell ) [237151]
- [nfs] NFS/NLM - Fix double free in __nlm_async_call (Steve Dickson ) [223248]
- [ppc] EEH is improperly enabled for some Power4  systems (Scott Moser ) [225481]
- [net] ixgb: update to 1.0.109 to add pci error recovery (Andy Gospodarek ) [211380]
- [ppc] Fix xmon=off and cleanup xmon initialization (Scott Moser ) [229593]
- [mm] reduce MADV_DONTNEED contention (Rik van Riel ) [237677]
- [x86_64] wall time is not compensated for lost timer ticks (Konrad Rzeszutek ) [232666]
- [PPC] handle <.symbol> lookup for kprobes (Scott Moser ) [238465]
- [pci] Dynamic Add and Remove of PCI-E (Konrad Rzeszutek ) [227727]
- [PPC64] Support for ibm,power-off-ups RTAS  call (Scott Moser ) [184681]

* Fri Jun 01 2007 Don Zickus <dzickus@redhat.com> [2.6.18-21.el5]
- [net] Re-enable and update the qla3xxx networking driver (Konrad Rzeszutek ) [225200]
- [misc] xen: kill sys_{lock,unlock} dependency on microcode driver (Gerd Hoffmann ) [219652]
- [acpi] Update ibm_acpi module (Konrad Rzeszutek ) [231176]
- [nfs] NFSv4: referrals support (Steve Dickson ) [230602]
- [misc] random: fix error in entropy extraction (Aristeu Rozanski ) [241718] {CVE-2007-2453}
- [net] fix DoS in PPPOE (Neil Horman ) [239581] {CVE-2007-2525}
- [GFS2] Fixes related to gfs2_grow (Steven Whitehouse ) [235430]
- [gfs2] Shrink size of struct gdlm_lock (Steven Whitehouse ) [240013]
- [misc] Bluetooth setsockopt() information leaks (Don Howard ) [234292] {CVE-2007-1353}
- [net] RPC/krb5 memory leak (Steve Dickson ) [223248]
- [mm] BUG_ON in shmem_writepage() is triggered (Michal Schmidt ) [234447]
- [nfs] protocol V3 :write procedure patch (Peter Staubach ) [228854]
- [fs] invalid segmentation violation during exec (Dave Anderson ) [230339]
- [md] dm io: fix panic on large request (Milan Broz ) [240751]
- [nfs] RPC: when downsizing response buffer, account for checksum (Jeff Layton ) [238687]
- [md] incorrect parameter to dm_io causes read failures (Jonathan Brassow ) [241006]
- [ia64] eliminate potential deadlock on XPC disconnects (George Beshers ) [223837]
- [md] dm crypt: fix possible data corruptions (Milan Broz ) [241272]
- [ia64] SN correctly update smp_affinity mask (luyu ) [223867]
- [mm]fix OOM wrongly killing processes through MPOL_BIND (Larry Woodman ) [222491]
- [nfs] add nordirplus option to NFS client  (Steve Dickson ) [240126]
- [autofs] fix panic on mount fail - missing autofs module (Ian Kent ) [240307]
- [scsi] Fix bogus warnings from SB600 DVD drive (Prarit Bhargava ) [238570]
- [acpi] _CID support for PCI Root Bridge  detection. (Luming Yu ) [230742]
- [ia64] platform_kernel_launch_event is a noop in non-SN kernel (Luming Yu ) [232657]
- [net] high TCP latency with small packets (Thomas Graf ) [229908]
- [misc] xen: fix microcode driver for new firmware (Gerd Hoffmann ) [237434]
- [GFS2] Bring GFS2 uptodate (Steven Whitehouse ) [239777]
- [scsi] update for new SAS RAID  (Scott Moser ) [228538]
- [md] dm: allow offline devices in table (Milan Broz ) [239655]
- [md] dm: fix suspend error path (Milan Broz ) [239645]
- [md] dm multipath: rr path order is inverted (Milan Broz ) [239643]
- [net] RPC: simplify data check, remove BUG_ON (Jeff Layton ) [237374]
- [mm] VM scalability issues (Larry Woodman ) [238901 238902 238904 238905]
- [misc] lockdep: annotate DECLARE_WAIT_QUEUE_HEAD (Chip Coldwell ) [209539]
- [mm] memory-less node support (Prarit Bhargava ) [228564]

* Thu May 17 2007 Don Howard <dhoward@redhat.com> [2.6.18-20.el5]
- [fs] prevent oops in compat_sys_mount (Jeff Layton ) [239767] {CVE-2006-7203}

* Thu May 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-19.el5]
- [ia64] MCA/INIT issues with printk/messages/console (Kei Tokunaga ) [219158]
- [ia64] FPSWA exceptions take excessive system time  (Erik Jacobson ) [220416]
- [GFS2] flush the glock completely in inode_go_sync (Steven Whitehouse ) [231910]
- [GFS2] mmap problems with distributed test cases (Steven Whitehouse ) [236087]
- [GFS2] deadlock running d_rwdirectlarge (Steven Whitehouse ) [236069]
- [GFS2] panic if you try to rm -rf the lost+found directory (Steven Whitehouse ) [232107]
- [misc] Fix softlockup warnings during sysrq-t (Prarit Bhargava ) [206366]
- [pty] race could lead to double idr index free (Aristeu Rozanski ) [230500]
- [v4l] use __GFP_DMA32 in videobuf_vm_nopage (Aristeu Rozanski ) [221478]
- [scsi] Update QLogic qla2xxx driver to 8.01.07-k6 (Marcus Barrow ) [225249]
- [mm] OOM killer breaks s390 CMM (Jan Glauber ) [217968]
- [fs] stack overflow with non-4k page size (Dave Anderson ) [231312]
- [scsi] scsi_transport_spi: sense buffer size error (Chip Coldwell ) [237889]
- [ppc64] EEH PCI error recovery  support (Scott Moser ) [207968]
- [mm] optimize kill_bdev() (Peter Zijlstra ) [232359]
- [x86] tell sysrq-m to poke the nmi watchdog (Konrad Rzeszutek ) [229563]
- [x86] Use CPUID calls to check for mce (Bhavana Nagendra ) [222123]
- [x86] Fix to nmi to support GH processors (Bhavana Nagendra ) [222123]
- [x86] Fix CPUID calls to support GH processors (Bhavana Nagendra ) [222123]
- [x86] Greyhound cpuinfo output cleanups (Bhavana Nagendra ) [222124]
- [misc] intel-rng: fix deadlock in smp_call_function (Prarit Bhargava ) [227696]
- [net] ixgb: fix early TSO completion (Bruce Allan ) [213642]

* Fri May 04 2007 Don Zickus <dzickus@redhat.com> [2.6.18-18.el5]
- [e1000] fix watchdog timeout panics (Andy Gospodarek ) [217483]
- [net] ipv6_fl_socklist is inadvertently shared (David S. Miller ) [233088] {CVE-2007-1592}
- [dlm] expose dlm_config_info fields in configfs (David Teigland ) [239040]
- [dlm] add config entry to enable log_debug (David Teigland ) [239040]
- [dlm] rename dlm_config_info fields (David Teigland ) [239040]
- [mm] NULL current->mm dereference in grab_swap_token causes oops (Jerome Marchand ) [231639]
- [net] Various NULL pointer dereferences in netfilter code (Thomas Graf ) [234287] {CVE-2007-1496}
- [net] IPv6 fragments bypass in nf_conntrack netfilter code (Thomas Graf ) [234288] {CVE-2007-1497}
- [net] disallow RH0 by default (Thomas Graf ) [238065] {CVE-2007-2242}
- [net] fib_semantics.c out of bounds check (Thomas Graf ) [236386]
- [misc] getcpu system call (luyu ) [233046]
- [ipc] bounds checking for shmmax (Anton Arapov ) [231168]
- [x86_64] GATT pages must be uncacheable (Chip Coldwell ) [238709]
- [gfs2] does a mutex_lock instead of a mutex_unlock (Josef Whiter ) [229376]
- [dm] failures when creating many snapshots (Milan Broz ) [211516 211525]
- [dm] kmirrord: deadlock when dirty log on mirror itself (Milan Broz ) [218068]
- [security] Supress SELinux printk for messages users don't care about (Eric Paris ) [229874]
- [serial] panic in check_modem_status on 8250 (Norm Murray ) [238394]
- [net] Fix user OOPS'able bug in FIB netlink (David S. Miller ) [237913]
- [misc] EFI: only warn on pre-1.00 version (Michal Schmidt ) [223282]
- [autofs4] fix race between mount and expire (Ian Kent ) [236875]
- [GFS2] gfs2_delete_inode: 13 (Steven Whitehouse ) [224480]
- [misc] k8temp (Florian La Roche ) [236205]

* Mon Apr 30 2007 Don Zickus <dzickus@redhat.com> [2.6.18-17.el5]
- [x86_64] Calgary IOMMU cleanups and fixes (Konrad Rzeszutek ) [222035]
- [GFS2] lockdump support (Robert Peterson ) [228540]
- [net] kernel-headers: missing include of types.h (Neil Horman ) [233934]
- [mm] unmapping memory range disturbs page referenced state (Peter Zijlstra ) [232359]
- [IA64] Fix stack layout issues when using ulimit -s (Jarod Wilson ) [234576]
- [CIFS] Windows server bad domain name null terminator fix (Jeff Layton ) [224359]
- [x86_64] Fix misconfigured K8 north bridge (Bhavana Nagendra ) [236759]
- [gfs2] use log_error before LM_OUT_ERROR (David Teigland ) [234338]
- [dlm] fix mode munging (David Teigland ) [234086]
- [dlm] change lkid format (David Teigland ) [237126]
- [dlm] interface for purge (David Teigland ) [237125]
- [dlm] add orphan purging code (David Teigland ) [237125]
- [dlm] split create_message function (David Teigland ) [237125]
- [dlm] overlapping cancel and unlock (David Teigland ) [216113]
- [dlm] zero new user lvbs (David Teigland ) [237124]
- [PPC64] Handle Power6 partition modes (2) (Janice M. Girouard ) [228091]
- [ppc64] Handle Power6 partition modes (Janice M. Girouard ) [228091]
- [mm] oom kills current process on memoryless node. (Larry Woodman ) [222491]
- [x86] Tick Divider (Alan Cox ) [215403]
- [GFS2] hangs waiting for semaphore (Steven Whitehouse ) [217356]
- [GFS2] incorrect flushing of rgrps (Steven Whitehouse ) [230143]
- [GFS2] Clean up of glock code (Steven Whitehouse ) [235349]
- [net] IPsec: panic when large security contexts in ACQUIRE (James Morris ) [235475]
- [ppc64] Cell Platform Base kernel support (Janice M. Girouard ) [228099]
- [s390] fix dasd reservations (Chris Snook ) [230171]
- [x86] Fix invalid write to nmi MSR (Prarit Bhargava ) [221671]

* Fri Apr 20 2007 Don Zickus <dzickus@redhat.com> [2.6.18-16.el5]
- [s390] crypto driver update (Jan Glauber ) [228049]
- [NMI] change watchdog timeout to 30 seconds (Larry Woodman ) [229563]
- [ppc64] allow vmsplice to work in 32-bit mode on ppc64 (Don Zickus ) [235184]
- [nfs] fix multiple dentries pointing to same directory inode (Steve Dickson ) [208862]
- [ipc] mqueue nested locking annotation (Eric Sandeen )
- [net] expand in-kernel socket api (Neil Horman ) [213287]
- [XEN] Better fix for netfront_tx_slot_available(). (Herbert Xu ) [224558]
- [fs] make static counters in new_inode and iunique be 32 bits (Jeff Layton ) [215356]
- [ppc64] remove BUG_ON() in hugetlb_get_unmapped_area() (Larry Woodman ) [222926]
- [dm] stalls on resume if noflush is used (Milan Broz ) [221330]
- [misc]: AMD/ATI SB600 SMBus support (Prarit Bhargava ) [232000]
- [mm] make do_brk() correctly return EINVAL for ppc64.   (Larry Woodman ) [224261]
- [agp] agpgart fixes and new pci ids (Geoff Gustafson ) [227391]
- [net] xfrm_policy delete security check misplaced (Eric Paris ) [228557]
- [x86]: Fix mtrr MODPOST warnings (Prarit Bhargava ) [226854]
- [elevator] move clearing of unplug flag  earlier (Eric Sandeen ) [225435]
- [net] stop leak in flow cache code (Eric Paris ) [229528]
- [ide] SB600 ide only has one channel (Prarit Bhargava ) [227908]
- [scsi] ata_task_ioctl should return ata registers (David Milburn ) [218553]
- [pcie]: Remove PCIE warning for devices with no irq pin (Prarit Bhargava ) [219318]
- [x86] ICH9 device IDs  (Geoff Gustafson ) [223097]
- [mm] Some db2 operations cause system to hang (Michal Schmidt ) [222031]
- [security] invalidate flow cache entries after selinux policy reload (Eric Paris ) [229527]
- [net] wait for IPSEC SA resolution in socket contexts. (Eric Paris ) [225328]
- [net] clean up xfrm_audit_log interface (Eric Paris ) [228422]
- [ipv6]: Fix routing regression. (David S. Miller ) [222122]
- [tux] date overflow fix (Jason Baron ) [231561]
- [cifs] recognize when a file is no longer read-only (Jeff Layton ) [231657]
- [module] MODULE_FIRMWARE support (Jon Masters ) [233494]
- [misc] some apps cannot use IPC msgsnd/msgrcv larger than 64K (Jerome Marchand ) [232012]
- [xen] Fix netfront teardown (Glauber de Oliveira Costa ) [219563]

* Fri Apr 13 2007 Don Zickus <dzickus@redhat.com> [2.6.18-15.el5]
- [x86_64] enable calgary support for x86_64 system (Neil Horman ) [221593]
- [s390] pseudo random number generator (Jan Glauber ) [184809]
- [ppc64] Oprofile kernel module does not distinguish PPC 970MP  (Janice M. Girouard ) [216458]
- [GFS2] honor the noalloc flag during block allocation (Steven Whitehouse ) [235346]
- [GFS2] resolve deadlock when writing and accessing a file (Steven Whitehouse ) [231380]
- [s390] dump on panic support (Jan Glauber ) [228050, 227841]
- [pci] include devices in NIC ordering patch and fix whitespace (Andy Gospodarek ) [226902]
- [ext3] handle orphan inodes vs. readonly snapshots (Eric Sandeen ) [231553]
- [fs] - Fix error handling in check_partition(), again (Eric Sandeen ) [231518]
- [ipv6] /proc/net/anycast6 unbalanced inet6_dev refcnt (Andy Gospodarek ) [231310]
- [s390] kprobes breaks BUG_ON (Jan Glauber ) [231155]
- [edac] add support for revision F processors (Aristeu Rozanski ) [202622]
- [scsi] blacklist touch-up (Chip Coldwell ) [232074]
- [gfs2] remove an incorrect assert (Steven Whitehouse ) [229873]
- [gfs2] inconsistent inode number lookups (Wendy Cheng ) [229395]
- [gfs2] NFS cause recursive locking (Wendy Cheng ) [229349]
- [gfs2] NFS v2 mount failure (Wendy Cheng ) [229345]
- [s390] direct yield for spinlocks on s390 (Jan Glauber ) [228869]
- [s390] crypto support for 3592 tape devices (Jan Glauber ) [228035]
- [cpu-hotplug] make and module insertion script cause a panic (Konrad Rzeszutek ) [217583]
- [s390] runtime switch for dasd erp logging (Jan Glauber ) [228034]
- [suspend] Fix x86_64/relocatable kernel/swsusp breakage. (Nigel Cunningham ) [215954]
- [ext3] buffer: memorder fix (Eric Sandeen ) [225172]
- [scsi] fix incorrect last scatg length (David Milburn ) [219838]
- [usb]: airprime driver corrupts ppp session for EVDO card (Jon Masters ) [222443]
- [misc] Fix race in efi variable delete code (Prarit Bhargava ) [223796]
- [ext3] return ENOENT from ext3_link when racing with unlink (Eric Sandeen ) [219650]
- [scsi] Missing PCI Device in aic79xx driver (Chip Coldwell ) [220603]
- [acpi]: Fix ACPI PCI root bridge querying time (Prarit Bhargava ) [218799]
- [kdump]: Simple bounds checking for crashkernel args (Prarit Bhargava ) [222314]
- [misc] longer CD timeout (Erik Jacobson ) [222362]
- [nfs] Disabling protocols when starting NFS server is broken. (Steve Dickson ) [220894]
- [s390] page_mkclean causes data corruption on s390 (Jan Glauber ) [235373]

* Wed Apr 04 2007 Don Zickus <dzickus@redhat.com> [2.6.18-14.el5]
- [ppc] reduce num_pmcs to 6 for Power6 (Janice M. Girouard ) [220114]
- [sched] remove __cpuinitdata from cpu_isolated_map (Jeff Burke ) [220069]
- [gfs2] corrrectly display revalidated directories (Robert Peterson ) [222302]
- [gfs2] fix softlockups (Josef Whiter ) [229080]
- [gfs2] occasional panic in gfs2_unlink while running bonnie++ (Steven Whitehouse ) [229831]
- [gfs2] Shrink gfs2 in-core inode size (Steven Whitehouse ) [230693]
- [GFS2] Fix list corruption in lops.c (Steven Whitehouse ) [226994]
- [gfs2] fix missing unlock_page() (Steven Whitehouse ) [224686]
- [dlm] make lock_dlm drop_count tunable in sysfs (David Teigland ) [224460]
- [dlm] increase default lock limit (David Teigland ) [224460]
- [dlm] can miss clearing resend flag (David Teigland ) [223522]
- [dlm] fix master recovery (David Teigland ) [222307]
- [dlm] fix user unlocking (David Teigland ) [219388]
- [dlm] saved dlm message can be dropped (David Teigland ) [223102]

* Tue Mar 27 2007 Don Zickus <dzickus@redhat.com> [2.6.18-13.el5]
- [x86_64] Don't leak NT bit into next task (Dave Anderson ) [213313]
- [mm] Gdb does not accurately output the backtrace. (Dave Anderson ) [222826]
- [net] IPV6 security holes in ipv6_sockglue.c - 2 (David S. Miller ) [231517] {CVE-2007-1000}
- [net] IPV6 security holes in ipv6_sockglue.c (David S. Miller ) [231668] {CVE-2007-1388}
- [audit] GFP_KERNEL allocations in non-blocking context fix (Alexander Viro ) [228409]
- [NFS] version 2 over UDP is not working properly (Steve Dickson ) [227718]
- [x86] Fix various data declarations in cyrix.c (Prarit Bhargava ) [226855]
- [sound] Fix various data declarations in sound/drivers (Prarit Bhargava ) [227839]
- [mm] remove __initdata from initkmem_list3 (Prarit Bhargava ) [226865]

* Wed Mar 14 2007 Don Zickus <dzickus@redhat.com> [2.6.18-12.el5]
- [xen] move xen sources out of kernel-xen-devel (Don Zickus ) [212968]
- [net] __devinit & __devexit cleanups for de2104x driver (Prarit Bhargava ) [228736]
- [video] Change rivafb_remove to __deviexit (Prarit Bhargava ) [227838]
- [x86] Reorganize smp_alternatives sections in vmlinuz (Prarit Bhargava ) [226876]
- [atm] Fix __initdata declarations in drivers/atm/he.c (Prarit Bhargava ) [227830]
- [video] Change nvidiafb_remove to __devexit (Prarit Bhargava ) [227837]
- [usb] __init to __devinit in isp116x_probe (Prarit Bhargava ) [227836]
- [rtc] __init to __devinit in rtc drivers' probe functions (Prarit Bhargava ) [227834]
- [x86] remove __init from sysenter_setup (Prarit Bhargava ) [226852]
- [irq] remove __init from noirqdebug_setup (Prarit Bhargava ) [226851]
- [x86] remove __init from efi_get_time (Prarit Bhargava ) [226849]
- [x86] Change __init to __cpuinit data in SMP code (Prarit Bhargava ) [226859]
- [x86] apic probe __init fixes (Prarit Bhargava ) [226875]
- [x86] fix apci related MODPOST warnings (Prarit Bhargava ) [226845]
- [serial] change serial8250_console_setup to __init (Prarit Bhargava ) [226869]
- [init] Break init() into two parts to avoid MODPOST warnings (Prarit Bhargava ) [226829]
- [x86] declare functions __init to avoid  compile warnings (Prarit Bhargava ) [226858]
- [x86] cpu hotplug/smpboot misc MODPOST warning fixes (Prarit Bhargava ) [226826]
- [x86] Fix boot_params and .pci_fixup warnings (Prarit Bhargava ) [226824 226874]
- [xen] Enable Xen booting on machines with > 64G (Chris Lalancette ) [220592]
- [utrace] exploit and unkillable cpu fixes (Roland McGrath ) [229886]
- [pcmcia] buffer overflow in omnikey cardman driver    (Don Howard ) [227478]

* Fri Feb 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-10.el5]
- [cpufreq] Remove __initdata from tscsync (Prarit Bhargava ) [223017]
- [security] Fix key serial number collision problem (David Howells ) [227497] {CVE-2007-0006}
- [fs] core dump of read-only binarys (Don Howard ) [228886] {CVE-2007-0958}

* Thu Feb 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-9.el5]
- enable debug options

* Thu Jan 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-8.el5]
- quiet down the console_loglevel (Don Zickus) [224613]

* Thu Jan 25 2007 Don Zickus <dzickus@redhat.com> [2.6.18-7.el5]
- xen: fix TLB flushing in shadow pagetable mode (Rik van Riel ) [224227]

* Tue Jan 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-6.el5]
- Update: xen: Add PACKET_AUXDATA cmsg (Herbert Xu ) [223505]

* Tue Jan 23 2007 Don Zickus <dzickus@redhat.com> [2.6.18-5.el5]
- x86: /proc/mtrr interface MTRR bug fix (Bhavana Nagendra ) [223821]
- Revert: bonding: eliminate rtnl assertion spew (Andy Gospodarek ) [210577]
- ia64: Check for TIO errors on shub2 Altix (George Beshers ) [223529]
- nfs: Unable to mount more than 1 Secure NFS mount (Steve Dickson ) [220649]

* Wed Jan 17 2007 Don Zickus <dzickus@redhat.com> [2.6.18-4.el5]
- IPSec: incorrect return code in xfrm_policy_lookup (Eric Paris ) [218591]
- more kabi whitelist updates (Jon Masters)

* Tue Jan 16 2007 Don Zickus <dzickus@redhat.com> [2.6.18-3.el5]
- scsi: fix EX8350 panic (stex.ko) (Jun'ichi Nick Nomura ) [220783]
- Audit: Mask upper bits on 32 bit syscall auditing on ppc64 (Eric Paris ) [213276]

* Mon Jan 15 2007 Don Zickus <dzickus@redhat.com> [2.6.18-2.el5]
- mm: handle mapping of memory without a struct page backing it (Erik Jacobson ) [221029]
- rng: check to see if bios locked device (Erik Jacobson ) [221029]
- sata: support legacy IDE mode of SB600 SATA (Bhavana Nagendra ) [221636]
- xen: quick fix for Cannot allocate memory (Steven Rostedt ) [217056]
- XEN: Register PIT handlers to the correct domain (Herbert Xu ) [222520]
- SATA AHCI: support AHCI class code (Jeff Garzik ) [222674]
- fix vdso in core dumps (Roland McGrath ) [211744]

* Fri Jan 12 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.3014.el5]
- XEN: Replace inappropriate domain_crash_synchronous use (Herbert Xu ) [221239]
- SATA timeout boot message  (Peter Martuccelli ) [222108]
- Netlabel: off by one and init bug in netlbl_cipsov4_add_common (Eric Paris ) [221648]
- NetLabel: fix locking issues (Eric Paris ) [221504]
- mm: fix statistics in vmscan.c (Peter Zijlstra ) [222030]
- usb: Sun/AMI virtual floppy issue (Pete Zaitcev ) [219628]
- bonding: eliminate rtnl assertion spew (Andy Gospodarek ) [210577]
- Xen: Make HVM hypercall table NR_hypercalls entries big. (Herbert Xu ) [221818]
- xen: Add PACKET_AUXDATA cmsg (Herbert Xu ) [219681]

* Wed Jan 10 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.3002.el5]
- ppc64: initialization of hotplug memory fixes (Janice M. Girouard ) [220065]
- GFS2: return error for NULL inode (Russell Cattelan ) [217008]
- scsi: prevent sym53c1510 from claiming the wrong pci id (Chip Coldwell ) [218623]
- net: Disable the qla3xxx network driver. (Tom Coughlan ) [221328]
- xen: Disable CONFIG_IDE_GENERIC (Jarod Wilson ) [220099]
- sound: add support for STAC9205 codec (John Feeney ) [219494]
- ipv6: panic when bringing up multiple interfaces (Thomas Graf ) [218039]
- XFRM Audit: correct xfrm auditing panic (Eric Paris ) [222033]
- edac: fix /proc/bus/pci/devices to allow X to start (John Feeney ) [219288]
- x86_64: clear_kernel_mapping: mapping has been split. will leak memory. (Larry Woodman ) [218543]
- xen: >4G guest fix (Steven Rostedt ) [217770]
-  fs: listxattr syscall can corrupt user space programs (Eric Sandeen ) [220119]
- CacheFiles: Fix object struct recycling (David Howells ) [215599]
- Remove capability requirement to reading cap-bound (Eric Paris ) [219230]
- disable building ppc64iseries (Don Zickus) [219185]
- update: utrace fixes (Roland McGrath) [214405 215052 216150 209118]
- PPC config file changes for IPMI and DTLK (Peter Martuccelli ) [210214]
- update: Xen: emulate PIT channels for vbios support (Stephen C. Tweedie ) [215647]
- net: qla3xxx panics when eth1 is sending pings (Konrad Rzeszutek ) [220246]
- s390: inflate spinlock kabi (Jan Glauber ) [219871]
- x86: Add panic on unrecovered NMI (Prarit Bhargava ) [220829]
- ppc64: fix booting kdump env. w/maxcpus=1 on power5 (Jarod Wilson ) [207300]
- netfilter: iptables stop fails because ip_conntrack cannot unload. (Thomas Graf ) [212839]
- gfs: Fix gfs2_rename lock ordering (for local filesystem) (Wendy Cheng ) [221237]
- GFS2: Fix ordering of page disposal vs. glock_dq (Steven Whitehouse ) [220117]
- xen: fix nosegneg detection (Rik van Riel ) [220675]
- mm: Fix for shmem_truncate_range() BUG_ON() (Larry Woodman ) [219821]
- x86_64: enabling lockdep hangs the system (Don Zickus ) [221198]
- dlm: change some log_error to log_debug (David Teigland ) [221326]
- dlm: disable debugging output (David Teigland ) [221326]
- fs: ext2_check_page denial of service (Eric Sandeen ) [217018]
- CPEI - prevent relocating hotplug irqs (Kei Tokunaga ) [218520]
- Networking: make inet->is_icsk assignment binary (Eric Paris ) [220482]
- net: b44: phy reset problem that leads to link flap  (Neil Horman ) [216338]
- autofs - fix panic on mount fail - missing autofs module update (Ian Kent ) [221118]
- net: act_gact: division by zero (Thomas Graf ) [218348]
- ppc64: Avoid panic when taking altivec exceptions from userspace. (David Woodhouse ) [220586]

* Wed Jan 03 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.2961.el5]
- new set of kabi whitelists (Jon Masters) [218682]
- x86: remove unwinder patches from x86/x86_64 (Don Zickus ) [220238]
- usb: disable ub and libusual (Pete Zaitcev ) [210026]
- NetLabel: stricter configuration checking (Eric Paris ) [219393]
- scsi: fix iscsi sense len handling (Mike Christie ) [217933]
- Xen: emulate PIT channels for vbios support (Stephen C. Tweedie ) [215647]
- VM: Fix nasty and subtle race in shared mmap'ed page writeback (Eric Sandeen ) [220963]
- Audit: Add type for 3rd party, emit key for audit events (Eric Paris ) [217958]
- NFS: system stall on NFS stress under high memory  pressure (Steve Dickson ) [213137]
- netfilter: IPv6/IP6Tables Vulnerabilities (Thomas Graf ) [220483]
- acpi: increase ACPI_MAX_REFERENCE_COUNT (Doug Chapman ) [217741]
- Race condition in mincore can cause ps -ef to hang (Doug Chapman ) [220480]
- Call init_timer() for ISDN PPP CCP reset state timer (Marcel Holtmann ) [220163]
- Race condition concerning VLAPIC interrupts (Bhavana Nagendra ) [213858]

* Tue Jan 02 2007 Don Zickus <dzickus@redhat.com> [2.6.18-1.2943.el5]
- CIFS: Explicitly set stat->blksize (Steve Dickson ) [210608]
- FS-Cache: dueling read/write processes fix (Steve Dickson ) [212831]
- xen: Use swiotlb mask for coherent mappings too (Herbert Xu ) [216472]
- ia64: Kexec, Kdump on SGI IA64 NUMA machines fixes (George Beshers ) [219091]
- splice : Must fully check for fifos (Don Zickus ) [214289]
- Xen: Fix potential grant entry leaks on error (Herbert Xu ) [217993]
- e1000: truncated TSO TCP header with 82544, workaround (Herbert Xu ) [206540]
- scsi: fix bus reset in qla1280 driver (George Beshers ) [219819]
- scsi: add qla4032 and fix some bugs (Mike Christie ) [213807]
- XFRM: Config Change Auditing (Eric Paris ) [209520]
- Xen: ia64 guest networking finally works (Jarod Wilson ) [218895]
- scsi structs for future known features and fixes (Mike Christie ) [220458]
- squashfs fixup (Steve Grubb ) [219534]
- ppc64: DLPAR virtual CPU removal failure - cppr bits (Janice M. Girouard ) [218058]
- ia64: allow HP ZX1 systems to initalize swiotlb in kdump (Neil Horman ) [220064]
- export tasklist_lock (David Howells ) [207992]
- gfs2: Initialization of security/acls (Steven Whitehouse ) [206126]
- x86: handle _PSS object range corectly in speedstep-centrino (Brian Maly ) [211690]
- GFS2 change nlink panic (Wendy Cheng ) [215088]
- scsi: fix oops in iscsi packet transfer path (Mike Christie ) [215381]
- Fix Emulex lpfc ioctl on PPC (Tom Coughlan ) [219194]
- Xen: Fix agp on x86_64 under Xen (Stephen C. Tweedie ) [217715]
- Emulex lpfc update to 8.1.10.2 (Tom Coughlan ) [218243]
- bluetooth: Add packet size checks for CAPI messages (Marcel Holtmann ) [219139]
- x86_64: create Calgary boot knob (Konrad Rzeszutek ) [220078]
- cciss bugfixes (Tom Coughlan ) [185021]
- ia64: Do not call SN_SAL_SET_CPU_NUMBER twice on cpu 0 on booting (Erik Jacobson ) [219722]
- scsi: Empty /sys/class/scsi_host/hostX/config  file (Janice M. Girouard ) [210239]
- refresh: Reduce iommu page size to 4K on 64K page PPC systems (Janice M. Girouard) [212097]
- update: Xen netback: Reenable TX queueing and drop pkts after timeout (Herbert Xu ) [216441]

* Sun Dec 17 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2910.el5]
- xen: Update xen paravirt framebuffer to upstream protocol (fixes) (Stephen C. Tweedie ) [218048]
- xen: Update xen paravirt framebuffer to upstream protocol (Stephen C. Tweedie ) [218048]
- nfs: disable Solaris NFS_ACL version 2  (Steve Dickson ) [215073]
- xen: EXPORT_SYMBOL(zap_page_range) needs to be moved (Stephen C. Tweedie ) [218476]
- ppc64: disable unused drivers that cause oops on insmod/rmmod (Janice M. Girouard ) [206658]
- scsi: GoVault not accessible due to software reset. (Konrad Rzeszutek ) [215567]
- GFS2 fix DIO deadlock (Steven Whitehouse ) [212627]
- dlm: fix lost flags in stub replies (David Teigland ) [218525]
- CacheFiles: Improve/Fix reference counting (David Howells ) [212844]
- gfs2: Fails back to readpage() for stuffed files (Steven Whitehouse ) [218966]
- gfs2: Use try locks in readpages (Steven Whitehouse ) [218966]
- GFS2 Readpages fix (part 2) (Steven Whitehouse ) [218966]
- gfs2: Readpages fix  (Steven Whitehouse ) [218966]
- bonding: Don't release slaves when master is admin down (Herbert Xu ) [215887]
- x86_64: fix execshield randomization for heap (Brian Maly ) [214548]
- x86_64: check and enable NXbit support during resume (Vivek Goyal ) [215954]
- GPL export truncate_complete_page (Eric Sandeen ) [216545]
- mm: reject corrupt swapfiles earlier (Eric Sandeen ) [213118]
- QLogic qla2xxx - add missing PCI device IDs (Tom Coughlan ) [219350]
- mpt fusion bugfix and maintainability improvements (Tom Coughlan ) [213736]
- scsi: make fc transport removal of target configurable (Mike Christie ) [215797]
- gfs2: don't try to lockfs after shutdown (Steven Whitehouse ) [215962]
- xen: emulation for accesses faulting on a page boundary (Stephen C. Tweedie ) [219275]
- gfs2: dirent format compatible with gfs1 (Steven Whitehouse ) [219266]
- gfs2: Fix size caclulation passed to the allocator. (Russell Cattelan ) [218950]
- ia64: PAL_GET_PSTATE implementation (Prarit Bhargava ) [184896]
- CacheFiles: Handle ENOSPC on create/mkdir better (David Howells) [212844]
- connector: exessive unaligned access (Erik Jacobson ) [218882]
- revert: Audit: Add type for 3rd party, emit key for audit events (Eric Paris ) [217958]

* Wed Dec 13 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2876.el5]
- touch softdog during oops (Dave Jones ) [218109]
- selinux: allow quoted commas for certain catagories in context mounts (Eric Paris ) [211857]
- xen: oprofile on Intel CORE (Glauber de Oliveira Costa ) [213964]
- Xen: make ballooning work right (xen part) (Rik van Riel ) [212069]
- Xen: make ballooning work right (Rik van Riel ) [212069]
- Xen: HVM crashes on IA32e SMP (Glauber de Oliveira Costa ) [214774]
- gfs2: Fix uninitialised variable (Steven Whitehouse ) [219212]
- GFS2: Don't flush everything on fdatasync (Steven Whitehouse ) [218770]
- Disable PCI mmconf and segmentation on HP xw9300/9400 (Bhavana Nagendra ) [219159]
- Audit: Add type for 3rd party, emit key for audit events (Eric Paris ) [217958]
- Fix time skew on Intel Core 2 processors (Prarit Bhargava ) [213050]
- Xen : Fix for SMP Xen guest slow boot issue on AMD systems (Bhavana Nagendra ) [213138]
- GFS2: fix mount failure (Josef Whiter ) [218327]
- cramfs: fix zlib_inflate oops with corrupted image (Eric Sandeen ) [214705]
- xen: Fix xen swiotlb for b44 module (xen part) (Stephen C. Tweedie ) [216472]
- xen: Fix xen swiotlb for b44 module (Stephen C. Tweedie ) [216472]
- scsi: fix stex_intr signature (Peter Zijlstra ) [219370]
- GFS2: Fix recursive locking in gfs2_permission (Steven Whitehouse ) [218478]
- GFS2: Fix recursive locking in gfs2_getattr (Steven Whitehouse ) [218479]
- cifs: Fix mount failure when domain not specified (Steve Dickson ) [218322]
- GFS2: Fix memory allocation in glock.c (Steven Whitehouse ) [204364]
- gfs2: Fix journal flush problem (Steven Whitehouse ) [203705]
- gfs2: Simplify glops functions (Steven Whitehouse ) [203705]
- gfs2: Fix incorrect fs sync behaviour (Steven Whitehouse ) [203705]
- fix check_partition routines to continue on errors (David Milburn ) [210234]
- fix rescan_partitions to return errors properly (David Milburn ) [210234]
- gfs2: Tidy up bmap & fix boundary bug (Steven Whitehouse ) [218780]
- Fix bmap to map extents properly (Steven Whitehouse ) [218780]
- ide-scsi/ide-cdrom module load race fix (Alan Cox ) [207248]
- dlm: fix receive_request lvb copying (David Teigland ) [214595]
- dlm: fix send_args lvb copying (David Teigland ) [214595]
- device-mapper mirroring - fix sync status change (Jonathan Brassow ) [217582]
- Xen: Copy shared data before verification (Herbert Xu ) [217992]
- s390: common i/o layer fixes (Jan Glauber ) [217799]
- Spurious interrups from ESB2 in native mode (Alan Cox ) [212060]

* Wed Dec 06 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2839.el5]
- Xen: fix xen/ia64/vti panic when config sets maxmem (Aron Griffis ) [214161]
- Xen: ia64 making it work (Aron Griffis ) [210637]
- Xen: upstream patches to make Windows Vista work (Steven Rostedt) [214780]
- enable PCI express hotplug driver (Kei Tokunaga ) [207203]
- d80211: kABI pre-compatibility (John W. Linville ) [214982]
- Xen: ia64 kernel unaligned access (Aron Griffis ) [212505]
- Xen: getting ia64 working; kernel part (Aron Griffis) [210637]
- Xen: Properly close block frontend on non-existant file (Glauber de Oliveira Costa ) [218037]
- SHPCHP driver doesn't work if the system was under heavy load (Kei Tokunaga ) [215561]
- SHPCHP driver doesn't work in poll mode (Kei Tokunaga) [211679]
- pciehp: free_irq called twice (Kei Tokunaga ) [216940]
- pciehp: pci_disable_msi() called to early (Kei Tokunaga ) [216939]
- pciehp: parallel hotplug operations cause kernel panic (Kei Tokunaga ) [216935]
- pciehp: info messages are confusing (Kei Tokunaga ) [216932]
- pciehp: Trying to enable already enabled slot disables the slot (Kei Tokunaga ) [216930]
- CacheFiles: cachefiles_write_page() shouldn't indicate error twice (David Howells) [204570]
- IPMI - allow multiple Baseboard Management Centers (Konrad Rzeszutek ) [212572]
- nfs - set correct mode during create operation (Peter Staubach ) [215011]
- Xen: blkback: Fix potential grant entry leaks on error (Rik van Riel ) [218355]
- Xen: blkback: Copy shared data before verification (Rik van Riel) [217994]
- revert: Xen: fix SMP HVM guest timer irq delivery (Rik van Riel ) [213138]

* Tue Dec 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2817.el5]
- Adding in a kabi_whitelist (Jon Masters) [218402]
- Xen: AMD-V HVM fix for Windows hibernate (Bhavana Nagendra ) [217367]
- Xen: fix SMP HVM guest timer irq delivery (Rik van Riel ) [213138]
- NetLabel: bring current with upstream: cleanup/future work (Eric Paris ) [218097]
- NetLabel: bring current with upstream: performance (Eric Paris ) [218097]
- NetLabel: bring current with upstream: bugs (Eric Paris ) [218097]
- TG3 support Broadcom 5756M/5756ME  Controller (John Feeney ) [213204]
- tg3: BCM5752M crippled after reset (Andy Gospodarek ) [215765]
- sata ata_piix map values (Geoff Gustafson ) [204684]
- e1000: Reset all functions after a PCI error (Janice M. Girouard) [211694]
- prevent /proc/meminfo's HugePages_Rsvd from going negative. (Larry Woodman ) [217910]
- netlabel: disallow editing of ip options on packets with cipso options (Eric Paris ) [213062]
- xen netback: Fix wrap to zero in transmit credit scheduler. (Herbert Xu ) [217574]
- megaraid initialization fix for kdump (Jun'ichi Nick Nomura ) [208451]
- HFS: return error code in case of error (Eric Paris ) [217009]
- Xen: fix 2TB overflow in virtual disk driver (Rik van Riel ) [216556]
- e1000: fix garbled e1000 stats (Neil Horman ) [213939]
- dlm: use recovery seq number to discard old replies (David Teigland ) [215596]
- dlm: resend lock during recovery if master not ready (David Teigland ) [215596]
- dlm: check for incompatible protocol version (David Teigland ) [215596]
- NetLabel: Do not send audit messages if audit is off (Eric Paris ) [216244]
- selinux: give correct response to get_peercon() calls (Eric Paris ) [215006]
- SELinux: Fix oops with non-mls policies (Eric Paris ) [214397]
- Xen blkback: Fix first_sect check. (Rik van Riel ) [217995]
- allow the highest frequency if bios think so. (Dave Jones ) [218106]
- AGP corruption fixes. (Dave Jones ) [218107]

* Mon Dec 04 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2789.el5]
- Xen: fix vcpu hotplug statistics (Rik van Riel ) [209534]
- DLPAR and Hotplug not enabled (Janice M. Girouard ) [207732]
- Reduce iommu page size to 4K on 64K page PPC systems (Janice M. Girouard) [212097]
- e1000: add (2) device ids (Bruce Allan) [184864]
- power6: illegal instruction errors during install (Janice M. Girouard) [216972]
- update_flash is broken across PPC (Janice M. Girouard) [214690]
- write failure on swapout could corrupt data (Peter Zijlstra) [216194]
- IBM veth panic when buffer rolls over (Janice M. Girouard ) [214486]
- Make the x86_64 boot gdt limit exact (Steven Rostedt ) [214736]
- Xen: make netfront device permanent (Glauber de Oliveira Costa ) [216249]
- lockdep: fix ide/proc interaction (Peter Zijlstra ) [210678]
- Xen: fix iSCSI root oops on x86_64 xen domU (Rik van Riel ) [215581]
- Fix flowi clobbering (Chris Lalancette ) [216944]
- Enable netpoll/netconsole for ibmveth (Neil Horman ) [211246]
- dlm: fix size of STATUS_REPLY message (David Teigland ) [215430]
- dlm: fix add_requestqueue checking nodes list (David Teigland ) [214475]
- dlm: don't accept replies to old recovery messages (David Teigland ) [215430]
- x86_64: kdump mptable reservation fix  (Vivek Goyal ) [215417]
- Add Raritan KVM USB dongle to the USB HID blacklist (John Feeney ) [211446]
- Fix bogus warning in [un]lock_cpu_hotplug (Prarit Bhargava ) [211301]
- Xen: Avoid touching the watchdog when gone for too long (Glauber de Oliveira Costa ) [216467]
- add missing ctcmpc Makefile target (Jan Glauber ) [184608]
- remove microcode size check for i386 (Geoff Gustafson ) [214798]

* Thu Nov 30 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2769.el5]
- add the latest 2.6.18.4 security patches (Don Zickus) [217904]
- revert: mspec failures due to memory.c bad pte problem (Erik Jacobson ) [211854]

* Wed Nov 29 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2767.el5]
- disable W1 config (Dave Jones ) [216176]
- Xen netback: Reenable TX queueing and drop pkts after timeout (Herbert Xu ) [216441]
- Xen: fix profiling (Rik van Riel ) [214886]
- bnx2: update firmware to correct rx problem in promisc mode (Neil Horman ) [204534]
- sound-hda: fix typo in patch_realtek.c (John W. Linville) [210691]
- Fix sys_move_pages when a NULL node list is passed. (Dave Jones ) [214295]
- proc: readdir race fix (Nobuhiro Tachino ) [211682]
- device mapper: /sys/block/dm-* entries remain after removal (Milan Broz ) [214905]
- Fix 64k page table problems on ppc specific ehca driver (Doug Ledford ) [199765]
- configfs: mutex_lock_nested() fix (Eric Sandeen ) [211506]
- CIFS: Explicitly set stat->blksize (Eric Sandeen ) [214607]
- Compute checksum properly in netpoll_send_udp (Chris Lalancette ) [214542]
- Noisy stack trace by memory hotplug on memory busy system (Kei Tokunaga ) [213066]
- catch blocks beyond pagecache limit in __getblk_slow (Eric Sandeen ) [214419]
- xen privcmd: Range-check hypercall index. (Herbert Xu ) [213178]
- strange messages around booting and acpi-memory-hotplug (Kei Tokunaga) [212231]
- Fix panic in CPU hotplug on ia64 (Prarit Bhargava ) [213455]
- Fix spinlock bad magic when removing xennet device (Chris Lalancette ) [211684]
- netlabel: various error checking cleanups (Eric Paris ) [210425]
- mspec failures due to memory.c bad pte problem (Erik Jacobson ) [211854]
- Fix autofs creating bad dentries in NFS mount (David Howells ) [216178]

* Thu Nov 09 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2747.el5]
- Set HZ to 1000 for kernel and 250 for Xen (Don Zickus) [198594]
- Custom Diagnostics kernel module fails to load on RHEL5 (Janice Girouard) [213020]
- kernel: FS-Cache: error from cache: -105 (2nd part) (Don Zickus) [214678]

* Mon Nov 06 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2746.el5]
- configure XPC as a loadable kernel module instead of static (Erik Jacobson) [213903]
- kernel BUG at drivers/xen/core/evtchn.c:482! (Glauber de Oliveira Costa) [210672]
- IPv6 MRT: 'lockdep' annotation is missing? (Thomas Graf) [209313]
- sort PCI device list breadth-first (John Feeney) [209484]
- reenable xen pae >4GB patch (Don Zickus)

* Sun Nov 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2745.el5]
- disable the xen-pae patch due to compile problems

* Sun Nov 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2744.el5]
- Kernel Panic on Initial boot of guest (Steven Rostedt) [211633]
- kernel unable to read partition (device busy) (Peter Zijlstra) [212191]
- QEMU always crashes (Don Zickus) [212625]
- kernel: FS-Cache: error from cache: -105 (Steve Dickson) [212831]
- DLM oops in kref_put when umounting (Patrick Caulfield) [213005]
- gfs umount hung, message size too big (Patrick Caulfield) [213289]
- CPU hotplug doesn't work trying to BSP offline (Keiichiro Tokunaga) [213324]
- status messages ping-pong between unmounted nodes (Dave Teigland) [213682]
- res_recover_locks_count not reset when recover_locks is aborted (Dave Teigland) [213684]
- disable CONFIG_ISA (Don Zickus)

* Wed Nov 01 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2740.el5]
- Remove support for ipw3945 driver (Don Zickus) [195534]
- acpiphp will not load due to unknown symbols (Prarit Bhargava) [209506]
- Can not install rhel5 b1 on ipr dasd. (Janice Girouard) [210851]
- Can't make SCTP connections between Xen guests (Don Zickus) [212550]
- eHEA update to support 64K pages for Power6 (Janice Girouard) [212041]
- Failure to boot second kernel on HP hardware (Don Zickus) [212578]
- dlm deadlock during simultaneous mount attempts (Dave Teigland) [211914]
- CMT-eligible ipw2200/2915 driver (John W. Linville) [184862]
- CVE-2006-5174 copy_from_user information leak on s390 (Jan Glauber) [213568]
- NFSv4: fs_locations support (Steve Dickson) [212352]
- [IPv6] irrelevant rules break ipv6 routing. (Thomas Graf) [209354]
- [IPv6] blackhole and prohibit rule types not working (Thomas Graf) [210216]
- [KEXEC] bad offset in icache instruction crashes Montecito systems (Jarod Wilson) [212643]
- assertion "FALSE" failed in gfs/glock.c (Dave Teigland) [211622]
- I/O DLPAR and Hotplug not enabled in RHEL5 (Janice Girouard) [207732]

* Thu Oct 26 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2739.el5]
- SHPCHP driver doesn't work (Keiichiro Tokunaga) [210478]
- ext3/jbd panic (Eric Sandeen) [209647]
- Oops in nfs_cancel_commit_list (Jeff Layton) [210679]
- kernel Soft lockup detected on corrupted ext3 filesystem (Eric Sandeen) [212053]
- CIFS doesn't work (Steve Dickson) [211070]

* Thu Oct 26 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2738.el5]
- need to convert bd_mount_mutex on gfs2 also (Peter Zijlstra)

* Wed Oct 25 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2737.el5]
- Grant table operations unsuitable for guest domains (Rik van Riel) [210489]
- AMD-V HVM windows guest boot menu timer issue (Steven Rostedt) [209001]
- iflags.h is not upstream (Steve Whitehouse) [211583]
- ACPIPHP doesn't work (Keiichiro Tokunaga) [209677]
- IBMVSCSI does not correctly reenable the CRQ (Janice Girouard) [211304]
- librdmacm-utils failures (Doug Ledford) [210711]
- Badness in debug_mutex_unlock at kernel/mutex-debug.c:80 (Janice Girouard) [208500]
- Stratus memory tracking functionality needed in RHEL5 (Kimball Murray) [209173, 211604]

* Tue Oct 24 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2736.el5]
- Can't unload gnbd module, 128 references (Peter Zijlstra) [211905]
- ddruid does not recognize dasd drives (Peter Zijlstra) [210030]

* Mon Oct 23 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2733.el5]
- disable x86_64 dirty page tracking, it breaks some machines (Don Zickus)

* Tue Oct 17 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2732.el5]
- possible recursive locking detected: cachefilesd (David Howells) [204615]
- Stratus memory tracking functionality needed in RHEL5 (Kimball Murray) [209173]
- nfs handled rpc error incorrectly (Steve Dickson) [207040]
- cachefiles: inode count maintance (Steve Dickson) [209434]
- mkinitrd: iSCSI root requires crc32c module (Mike Christie) [210232]
- implemented sysrq-w to dump all cpus (Larry Woodman)
- enable panic_on_oops (Dave Anderson)
- re-enable x86_64 stack unwinder fixes (Don Zickus)
- disable kernel debug flags (Don Zickus)

* Tue Oct 17 2006 Stephen C. Tweedie <sct@redhat.com>
- Fix up xen blktap merge to restore modular build

* Tue Oct 17 2006 Don Zickus <dzickus@redhat.com>
- fix xen breakage from last night's incorrect commits

* Mon Oct 16 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2729.el5]
- revert Kpobes backport from 2.6.19-rc1, it fails to compile

* Mon Oct 16 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2728.el5]
- Update FC transport and Emulex lpfc Fibre Channel Driver (Tom Coughlan) [207551]
- NFSv4 using memory after its freed fix (Steve Dickson) [206996]
- GFS2 dirents are 'unkown' type (Steve Whitehouse) [210493]
- Cachefs double unlock (Steve Dickson) [210701]
- tty locking cleanup (Prarit Bhargava) [210249]
- ibmveth fails in kdump boot (Janice Girouard - IBM on-site partner) [199129]
- Kpobes backport from 2.6.19-rc1 (Anil S Keshavamurthy) [210555]
- Ia64 - kprobe opcode must reside on 16 bytes alignment (Anil S Keshavamurthy) [210552]
- GFS2 forgets to unmap pages (Steve Whitehouse) [207764]
- DIO needs to avoid using page cache (Jeffrey Moyer) [207061]
- megaraid_sas: update (Chip Coldwell) [209463]
- NFS data corruption (Steve Dickson) [210071]
- page align bss sections on x86_64 (Vivek Goyal) [210499]
- blkbk/netbk modules don't load (Aron Griffis) [210070]
- blktap does not build on ia64 (Aron Griffis) [208895]
- blkbk/netbk modules don't load (Rik van Riel) [202971]
- patches from xen-ia64-unstable (Rik van Riel) [210637]
- Xen version strings need to reflect exact Red Hat build number (Stephen Tweedie) [211003]
- updated to 2.6.18.1 stable series (Don Zickus)
- updated execshield patch (Don Zickus)
- revert CONFIG_PCI_CALGARY_IOMMU config (Don Zickus)
- disable CONFIG_MAMBO (Don Zickus)

* Thu Oct 12 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2727.el5]
- I/O errors with dm-multipath when adding new path (Alasdair Kergon) [169302]
- Kdump on i386 fails - Second kernel panics (Vivek Goyal) [207598]
- patch to qla4xxx for supporting ioctl module (Mike Christie) [207356]
- lockdep fixes (Peter Zijlstra) [208165 209135 204767]
- printk cleanup (Dave Jones)
- spec file cleanup (Dave Jones, Bill Nottingham)
- gfs-dlm fix (Patrick Caulfield)
- find-provides fix (Jon Masters)

* Wed Oct 11 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2726.el5]
- need to disable all cpu frequency scaling drivers in Xen kernel (Rik van Riel) [210336 208942]
- radeon hangs DMA when CONFIG_CALGARY_IOMMU is build in kernel. (Konrad Rzeszutek) [210380]
- Got Call Trace message when remove veth module (Janice Girouard) [208938]
- cannot generate kABI deps unless kernel is installed (Jon Masters) [203926]
- ctcmpc driver (Jan Glauber) [184608]
- PTRACE_DETACH doesn't deliver signals under utrace. (Aristeu S. Rozanski F.) [207674]
- SG_SCATTER_SZ causing Oops during scsi disk microcode update (Doug Ledford) [207146]
- ia64 kprobe fixes (David Smith)

* Tue Oct 10 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2725.el5]
- Duplicate dput in sysfs_update_file can cause a panic. (Prarit Bhargava) [209454]
- Lock issue with 2.6.18-1.2702.el5, NetworkManager and ipw3945 (John W. Linville) [208890]
- cpqarray module fails to detect arrays (Chip Coldwell) [205653]
- stex.c driver for Promise SuperTrak EX is missing (Jeff Garzik) [209179]
- NetLabel does not audit configuration changes (Eric Paris) [208456]
- NetLabel has a race problem in the cache (Eric Paris) [209324]
- kernel/lockdep.c:1814/trace_hardirqs_on() (Not tainted) for APM (Peter Zijlstra) [209480]
-  correct netlabel secid for packets without a known label (Eric Paris) [210032]
- IPSec information leak with labeled networking (Eric Paris) [209171]
- NetLabel hot-add memory confict pre-beta2 kenrel x86_64 (Konrad Rzeszutek) [208445]
- NFS data corruption (Steve Dickson) [210071]
- kernel dm multipath: ioctl support (Alasdair Kergon) [207575]
- kernel dm: fix alloc_dev error path (Alasdair Kergon) [209660]
- kernel dm snapshot: fix invalidation ENOMEM (Alasdair Kergon) [209661]
- kernel dm snapshot: chunk_size parameter is not required after creation (Alasdair Kergon) [209840]
- kernel dm snapshot: fix metadata error handling (Alasdair Kergon) [209842]
- kernel dm snapshot: fix metadata writing when suspending (Alasdair Kergon) [209843]
- kernel dm: full snapshot removal attempt causes a seg fault/kernel bug (Alasdair Kergon) [204796]
- dm mirror: remove trailing space from table (Alasdair Kergon) [209848]
- kernel dm: add uevent change event on resume (Alasdair Kergon) [209849]
- kernel dm crypt: Provide a mechanism to clear key while device suspended (Milan Broz) [185471]
- kernel dm: use private biosets to avoid deadlock under memory pressure (Alasdair Kergon) [209851]
- kernel dm: add feature flags to structures for future kABI compatibility (Alasdair Kergon) [208543]
- kernel dm: application visible I/O errors with dm-multipath and queue_if_no_path when adding new path (Alasdair Kergon) [169302]
- refresh ia64-kexec-kdump patch (Don Zickus)
- update exec-shield patch (Don Zickus)
- revert x86 unwinder fixes (Don Zickus)

* Mon Oct 09 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2722.el5]
- update utrace patch to fix s390 build problems
- ia64 hotswap cpu patch fixes to compile under xen
- ia64 export fixes

* Mon Oct 09 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2718.el5]
- Audit Filtering on PPID for = and != is inverted (Eric Paris) [206425]
- Adding Hitachi SANRISE entries into SCSI white list (Chip Coldwell) [206532]
- forward port of SCSI blacklist from RHEL4 (Chip Coldwell) [208256]
- Need to add ALSA support for Broadwater platform (John W. Linville) [184855]
- /proc/<pid>/smaps doesn't give any data (Alexander Viro) [208589]
- ACPI based CPU hotplug causes kernel panic (Keiichiro Tokunaga) [208487]
- New infiniband 12x power driver opensourced from IBM (Janice Girouard) [184791]
- iscsi oops when connection creation fails (Mike Christie) [209006]
- nommconf work-around still needed for AMD chipsets (Jim Baker) [207396]
- ProPack XPMEM exported symbols (Greg Edwards) [206215]
- PCI error recovery bug in e100 and e1000 cards (John W. Linville) [208187]
- / on raid fails to boot post-install system (Jan Glauber) [196943]
- auditctl fails to reject malformed ARCH filter (Eric Paris) [206427]
- oom-killer updates (Larry Woodman) [208583]
- NFS is revalidating directory entries too often (Steve Dickson) [205454]
- kernel-xen cannot reboot (Stephen Tweedie) [209841]
- Unsupported FS's in RHEL 5 Beta 1 (Don Zickus) [206486]

* Thu Oct 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2717.el5]
- patch fix for RDSCTP (Don Zickus)

* Thu Oct 05 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2715.el5]
- RDTSCP Support (Bhavana Nagendra) [185057]
- s390 kprobe on larl instruction crashes system (Jan Glauber) [205738]
- single stepping is broken when kprobes is configured (Jan Glauber) [205739]
- autofs kernel patches resulting from Connectathon testing (Ian Kent) [206952]
- Include the qla3xxx networking driver (Konrad Rzeszutek) [208182]
- overzealous sanity checking in sys_poll() (Chris Snook) [204705]
- automounter cannot shutdown when timeout=0 (Ian Kent) [205836]
- Rewrite of journaling data commit code (Eric Sandeen) [207739]
- qla4xxx soft lockup when ethernet cable disconnected (Mike Christie) [206063]
- hypfs_kill_super() check for initialized root inode (Jan Glauber) [207717]
- The Matrox graphics driver is not built (Janice Girouard) [207200]

* Mon Oct 02 2006 Don Zickus <dzickus@redhat.com> [2.6.18-1.2714.el5]
- Wrong SELinux context prevents hidd from working (David Woodhouse) [204655]
- nfs connectathon component basic test 6 fails.... (Steve Dickson) [208637]
- unstick STICKY bit to fix suspend/resume (Dave Jones)

* Fri Sep 29 2006 Don Zickus <dzickus@redhat.com>
- fix up ipv6 multiple routing table patch

* Thu Sep 28 2006 Don Zickus <dzickus@redhat.com>
- s390 ccs/ccw subsystem does not have proper uevent support (Pete Zaitcev) [199994]
- 'Cannot allocate memory' when cat /proc/scsi/scsi (Chip Coldwell) [200299]
- Add support for Kirkwood and Kirkwood LP NICs (John W. Linville) [207776]
- remove userspace support from qla4xxx (Mike Christie) [206063]
- NetLabel interface has changed in the upstream kernels (Eric Paris) [208119]
- lockdep fixes (Peter Zijlstra) [208304 204795]

* Thu Sep 28 2006 Steven Whitehouse <swhiteho@redhat.com>
- Updated GFS2/DLM patch

* Wed Sep 27 2006 Don Zickus <dzickus@redhat.com>
-Multiple routing tables for IPv6 (Thomas Graf) [179612]
-bunch of lockdep fixes (Peter Zijlstra) [200520 208294 208293 208292 208290]
-rearrange the cachefs patches for easier future maintance (Steve Dickson)
-enable some TCP congestion algorithms (David Miller)
-add a test patch (Eric Paris)

* Tue Sep 26 2006 Don Zickus <dzickus@redhat.com>
- Need to add the sata sas bits

* Tue Sep 26 2006 Don Zickus <dzickus@redhat.com>
-Native SAS and SATA device support - SATA/IDE converter (Janice Girouard) [196336]
-kernel unaligned access messages in rhel5a1 (Prarit Bhargava) [198572]
-problems with LUNs mapped at LUN0 with iscsi and netapp filers (Mike Christie) [205802]
-ext3 fails to mount a 16T filesystem due to overflows (Eric Sandeen) [206721]
-possible recursive locking detected - swapper/1 (Peter Zijlstra) [203098]
-FS-Cache: error from cache: -28 (David Howells) [204614]
-aic94xx driver does not recognise SAS drives in x366 (Konrad Rzeszutek) [206526]
-Support for 3945 driver (John W. Linville) [195534]
-Memory Hotplug fails due to relocatable kernel patches (Vivek Goyal) [207596]
-Potential overflow in jbd for filesystems > 8T (Eric Sandeen) [208024]
-2,4-node x460 halts during bootup after installation (Konrad Rzeszutek) [203971]

* Mon Sep 25 2006 Don Zickus <dzickus@redhat.com>
- fix x86 relocatable patch (again) to build properly

* Mon Sep 25 2006 Dave Jones <davej@redhat.com>
- Disable 31bit s390 kernel builds.

* Mon Sep 25 2006 Jarod Wilson <jwilson@redhat.com>
- Make kernel packages own initrd files

* Mon Sep 25 2006 John W. Linville <linville@redhat.com>
- Add periodic work fix for bcm43xx driver

* Sat Sep 23 2006 Dave Jones <davej@redhat.com>
- Disable dgrs driver.

* Fri Sep 22 2006 David Woodhouse <dwmw2@redhat.com>
- Fix PowerPC audit syscall success/failure check (#204927)
- Remove offsetof() from <linux/stddef.h> (#207569)
- One line per header in Kbuild files to reduce conflicts
- Fix visibility of ptrace operations on ppc32
- Fix ppc32 SECCOMP

* Thu Sep 21 2006 Dave Jones <davej@redhat.com>
- reiserfs: make sure all dentry refs are released before
  calling kill_block_super
- Fix up some compile warnings

* Thu Sep 21 2006 Mike Christie <mchristie@redhat.com>
- clean up spec file.

* Thu Sep 21 2006 Mike Christie <mchristie@redhat.com>
- drop 2.6.18-rc iscsi patch for rebase

* Wed Sep 20 2006 Juan Quintela <quintela@redhat.com>
- xen HV printf rate limit (rostedt).
- xen HV update to xen-unstable cset11540:9837ff37e354
- xen-update:
  * linux-2.6 changeset:   34294:dc1d277d06e0
  * linux-2.6-xen-fedora changeset:   36184:47c098fdce14
  * xen-unstable changeset:   11540:9837ff37e354

* Wed Sep 20 2006 Dave Jones <davej@redhat.com>
- 2.6.18
- i965 AGP suspend support.
- AGP x8 fixes.

* Tue Sep 19 2006 Juan Quintela <quintela@redhat.com>
- xen update to 2.6.18-rc7-git4.
  * linux-2.6 changeset: 34288:3fa5ab23fee7
  * linux-2.6-xen-fedora changeset: 36175:275f8c0b6342
  * xen-unstable changeset: 11486:d8bceca5f07d

* Tue Sep 19 2006 Dave Jones <davej@redhat.com>
- 2.6.18rc7-git4
- Further lockdep fixes. (#207064)

* Tue Sep 19 2006 Don Zickus <dzickus@redhat.com>
- EXT3 overflows at 16TB (#206721)

* Tue Sep 19 2006 Don Zickus <dzickus@redhat.com>
- Increase nodes supported on ia64 (#203184)
- Powernow K8 Clock fix (#204354)
- NetLabel fixes

* Mon Sep 18 2006 Dave Jones <davej@redhat.com>
- Fix RTC lockdep bug. (Peter Zijlstra)

* Mon Sep 18 2006 Juan Quintela <quintela@redhat.com>
- xen HV update (cset 11470:2b8dc69744e3).

* Mon Sep 18 2006 David Woodhouse <dwmw2@redhat.com>
- Fix various Bluetooth compat ioctls

* Sun Sep 17 2006 Juan Quintela <quintela@redhat.com>
- xen update:
  * linux-2.6 changeset: 34228:ea3369ba1e2c
  * linux-2.6-xen-fedora changeset: 36107:47256dbb1583
  * linux-2.6-xen changeset: 22905:d8ae02f7df05
  * xen-unstable changeset: 11460:1ece34466781ec55f41fd29d53f6dafd208ba2fa

* Sun Sep 17 2006 Dave Jones <davej@redhat.com>
- Fix task->mm refcounting bug in execshield. (#191094)
- 2.6.18rc7-git2
- 586 SMP support.

* Sat Sep 16 2006 David Woodhouse <dwmw2@redhat.com>
- Implement futex primitives on IA64 and wire up [gs]et_robust_list again
  (patch from Jakub, #206613)

* Fri Sep 15 2006 Mike Christie <mchristie@redhat.com>
- fix slab corruption when starting qla4xxx with iscsid not started.

* Thu Sep 14 2006 Don Zickus <dzickus@redhat.com>
- add include/asm-x86_64/const.h to exported header file list
  used by the x86 relocatable patch (inside include/asm-x86_64/page.h)

* Thu Sep 14 2006 Dave Jones <davej@redhat.com>
- kprobe changes to make systemtap's life easier.

* Thu Sep 14 2006 Don Zickus <dzickus@redhat.com>
- sync up beta1 fixes and patches
   - includes infiniband driver
   - aic9400/adp94xx updates
   - squashfs s390 fix
- include x86 relocatable patch at end of list
- some /proc/kcore changes for x86 relocatable kernel

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
