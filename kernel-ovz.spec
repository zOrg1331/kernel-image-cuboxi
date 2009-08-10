%set_verify_elf_skiplist /boot/*
%set_strip_skiplist /boot/*

%define with_doc       0
%define with_headers   1
%define with_openafs   0
%define ovzver 028stab064

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
%define rh_release_minor 3

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
%define krelease alt8
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
Patch20107: xen-x86-silence-wrmsr-warnings.patch
Patch20108: xen-x86-fix-dom0-panic-when-using-dom0_max_vcpus.patch
Patch20109: xen-x86-update-the-earlier-aperf-mperf-patch.patch
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
Patch23483: linux-2.6-fs-hfs-fix-namelength-memory-corruption.patch
Patch23484: linux-2.6-fs-hfsplus-check-read_mapping_page-return-value.patch
Patch23485: linux-2.6-fs-hfsplus-fix-buffer-overflow-with-a-corrupted-image.patch
Patch23486: linux-2.6-s390-zfcp-fix-hexdump-data-in-s390dbf-traces.patch
Patch23487: linux-2.6-misc-setpgid-returns-esrch-in-some-situations.patch
Patch23488: linux-2.6-x86_64-copy_user_c-assembler-can-leave-garbage-in-rsi.patch
Patch23489: linux-2.6-net-add-preemption-point-in-qdisc_run.patch
Patch23490: linux-2.6-openib-restore-traffic-in-connected-mode-on-hca.patch
Patch23491: linux-2.6-md-fix-oops-with-device-mapper-mirror-target.patch
Patch23492: linux-2.6-net-sctp-overflow-with-bad-stream-id-in-fwd-tsn-chunk.patch
Patch23493: linux-2.6-nfs-create-rpc-clients-with-proper-auth-flavor.patch
Patch23494: linux-2.6-sched-fix-clock_gettime-monotonicity.patch
Patch23495: linux-2.6-security-introduce-missing-kfree.patch
Patch23496: linux-2.6-wireless-iwl-fix-bug_on-in-driver.patch
Patch23497: linux-2.6-net-deadlock-in-hierarchical-token-bucket-scheduler.patch
Patch23498: linux-2.6-fs-ext-234-directory-corruption-dos.patch
Patch23499: linux-2.6-nfs-handle-attribute-timeout-and-u32-jiffies-wrap.patch
Patch23500: linux-2.6-block-enforce-a-minimum-sg_io-timeout.patch
Patch23501: linux-2.6-misc-fix-memory-leak-during-pipe-failure.patch
Patch23502: linux-2.6-net-ixgbe-frame-reception-and-ring-parameter-issues.patch
Patch23503: linux-2.6-qla2xxx-correct-endianness-during-flash-manipulation-2.patch
Patch23504: linux-2.6-fs-ecryptfs-readlink-flaw.patch
Patch23505: linux-2.6-scsi-libata-sas_ata-fixup-sas_sata_ops.patch
Patch23506: linux-2.6-gfs2-panic-in-debugfs_remove-when-unmounting.patch
Patch23507: linux-2.6-firmware-dell_rbu-prevent-oops.patch
Patch23508: linux-2.6-misc-minor-signal-handling-vulnerability.patch
Patch23509: linux-2.6-ptrace-correctly-handle-ptrace_update-return-value.patch
Patch23510: linux-2.6-x86-limit-max_cstate-to-use-tsc-on-some-platforms.patch
Patch23511: linux-2.6-net-memory-disclosure-in-so_bsdcompat-gsopt.patch
Patch23512: linux-2.6-net-skfp_ioctl-inverted-logic-flaw.patch
Patch23513: linux-2.6-net-fix-icmp_send-and-icmpv6_send-host-re-lookup-code.patch
Patch23514: linux-2.6-x86-tsc-keeps-running-in-c3.patch
Patch23515: linux-2.6-misc-signal-modify-locking-to-handle-large-loads.patch
Patch23517: linux-2.6-wireless-iwlwifi-booting-with-rf-kill-switch-enabled.patch
Patch23518: linux-2.6-x86_64-mce-do-not-clear-an-unrecoverable-error-status.patch
Patch23519: linux-2.6-x86-add-nonstop_tsc-flag-in-proc-cpuinfo.patch
Patch23520: linux-2.6-net-ehea-improve-behaviour-in-low-mem-conditions.patch
Patch23521: linux-2.6-input-wacom-12x12-problem-while-using-lens-cursor.patch
Patch23522: linux-2.6-net-enic-return-notify-intr-credits.patch
Patch23523: linux-2.6-net-bonding-fix-arp_validate-3-slaves-behaviour.patch
Patch23524: linux-2.6-ia64-use-current_kernel_time-xtime-in-hrtimer_start.patch
Patch23525: linux-2.6-nfs-fix-hung-clients-from-deadlock-in-flush_workqueue.patch
Patch23526: linux-2.6-dlm-fix-length-calculation-in-compat-code.patch
Patch23527: linux-2.6-ptrace-audit_syscall_entry-to-use-right-syscall-number.patch
Patch23528: linux-2.6-fs-ecryptfs-fix-memory-leak-into-crypto-headers.patch
Patch23529: linux-2.6-ppc-keyboard-not-recognized-on-bare-metal.patch
Patch23530: linux-2.6-x86-nonstop_tsc-in-tsc-clocksource.patch
Patch23531: linux-2.6-nfs-remove-bogus-lock-if-signalled-case.patch
Patch23532: linux-2.6-net-fix-oops-when-using-openswan.patch
Patch23533: linux-2.6-net-ixgbe-stop-double-counting-frames-and-bytes.patch
Patch23534: linux-2.6-nfs-v4-client-crash-on-file-lookup-with-long-names.patch
Patch23535: linux-2.6-scsi-qla2xxx-reduce-did_bus_busy-failover-errors.patch
Patch23536: linux-2.6-misc-fork-clone_parent-parent_exec_id-interaction.patch
Patch23537: linux-2.6-misc-exit_notify-kill-the-wrong-capable-check.patch
Patch23538: linux-2.6-net-ipv4-remove-uneeded-bh_lock-unlock-from-udp_rcv.patch
Patch23539: linux-2.6-fs-fix-softlockup-in-posix_locks_deadlock.patch
Patch23540: linux-2.6-nfs-race-with-nfs_access_cache_shrinker-and-umount.patch
Patch23541: linux-2.6-ia64-fix-regression-in-nanosleep-syscall.patch
Patch23542: linux-2.6-ata-libata-ahci-enclosure-management-bios-workaround.patch
Patch23543: linux-2.6-misc-waitpid-reports-stopped-process-more-than-once.patch
Patch23544: linux-2.6-fs-keep-eventpoll-from-locking-up-the-box.patch
Patch23545: linux-2.6-agp-zero-pages-before-sending-to-userspace.patch
Patch23546: linux-2.6-misc-add-some-long-missing-capabilities-to-cap_fs_mask.patch
Patch23547: linux-2.6-nfs-fix-hangs-during-heavy-write-workloads.patch
Patch23548: linux-2.6-mm-fork-vs-gup-race-fix.patch
Patch23549: linux-2.6-mm-cow-vs-gup-race-fix.patch
Patch23550: linux-2.6-gfs2-fix-uninterruptible-quotad-sleeping.patch
Patch23551: linux-2.6-misc-random-make-get_random_int-more-random.patch
Patch23552: linux-2.6-misc-compile-add-fwrapv-to-gcc-cflags.patch
Patch23553: linux-2.6-x86-xen-fix-local-denial-of-service.patch
Patch23554: linux-2.6-fs-cifs-unicode-alignment-and-buffer-sizing-problems.patch
Patch23555: linux-2.6-fs-cifs-buffer-overruns-when-converting-strings.patch
Patch23556: linux-2.6-fs-cifs-fix-error-handling-in-parse_dfs_referrals.patch
Patch23557: linux-2.6-fs-cifs-fix-pointer-and-checks-in-cifs_follow_symlink.patch
Patch23558: linux-2.6-scsi-libiscsi-fix-nop-response-reply-and-session-cleanup-race.patch
Patch23559: linux-2.6-net-tg3-fix-firmware-event-timeouts.patch
Patch23560: linux-2.6-fs-proc-avoid-info-leaks-to-non-privileged-processes.patch
Patch23561: linux-2.6-nfs-v4-client-handling-of-may_exec-in-nfs_permission.patch

Patch25000: diff-xen-smpboot-ifdef-hotplug-20090306
Patch25001: diff-ocfs2-drop-duplicate-functions-20090306

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
Patch90000: patch-linux-2.6.18-rhel5-drbd-8.3.1
Patch90001: diff-drbd-8.3.1-cfix

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
Patch100015: diff-show-task-running-20081117
Patch100016: diff-rh-cifs-disable-posix-extensons-by-default-20090304
Patch100017: diff-ms-32bitHW-kernel-panic-string
Patch100018: diff-ms-mmap-min-addr
Patch100019: diff-pb-relink-in-fork_pre_cow-20090703
Patch100020: linux-2.6.18-128.1.1.el5.028stab062.3-build-fixes.diff
Patch100021: diff-ms-fno-delete-null-check-in-makefile
Patch100022: diff-ms-personality-fix-PER_CLEAR_ON_SETID
Patch100023: diff-ve-hook-in-daemonize-20090723
Patch100024: diff-ve-nfs-xprt-owner_env-save-20090724

# NBD
Patch110001: diff-nbd-from-current
Patch110002: diff-nbd-compile-fixes
Patch110003: diff-nbd-umount-after-connection-lost
Patch110005: diff-nbd-spinlock-usage-fix
Patch110006: diff-nbd-xmit-timeout
Patch110007: diff-nbd-remove-truncate-at-disconnect-20090529
Patch110008: diff-nbd-forbid-socket-clear-without-disconnect-20090529

# End VZ patches

# adds rhel version info to version.h
Patch99990: linux-2.6-rhel-version-h.patch
# empty final patch file to facilitate testing of kernel patches
Patch99999: linux-kernel-test.patch

# ALT-specific patches
Patch200000: our_kernel.patch
Patch200001: fix_getcpu_call.patch

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
%patch22906 -p1
%patch22907 -p1
%patch22908 -p1
%patch22909 -p1
%patch22910 -p1
%patch22911 -p1
%patch22912 -p1
%patch22913 -p1
%patch22914 -p1
%patch22915 -p1
%patch22916 -p1
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
%patch22992 -p1
%patch22993 -p1
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
%patch23039 -p1
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
%patch23176 -p1
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
%patch23331 -p1
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
%patch23358 -p1
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
%patch23387 -p1
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
%patch23457 -p1
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
%patch23490 -p1
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
# %patch23548 -p1
# %patch23549 -p1
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

%patch25000 -p1
%patch25001 -p1

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
%patch100015 -p1
%patch100016 -p1
%patch100017 -p1
%patch100018 -p1
# %patch100019 -p1
%patch100020 -p1
%patch100021 -p1
%patch100022 -p1
%patch100023 -p1
%patch100024 -p1

%patch110001 -p1
%patch110002 -p1
%patch110003 -p1
%patch110005 -p1
%patch110006 -p1

%patch110007 -p1
%patch110008 -p1

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

# ALT-specific patch
%patch200000 -p1
%patch200001 -p1

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
cp -a net/mac80211/ieee80211_{i,key,rate}.h \
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
