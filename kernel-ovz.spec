%set_verify_elf_skiplist /boot/*
%set_strip_skiplist /boot/*
# ------------- translate OVZ build system settings to RHEL -----------------
%define buildup 1
%define buildsmp 0
%define buildpae 0
%define buildenterprise 0
%define buildxen 0
%define buildopenafs 0

%define builddebug 0
%define builddoc 0
%define buildkdump 0
%define buildheaders 0
%define _without_kabichk 1

%define ovzver 028stab059
%define ovzrel 6

%if !%buildup
%define _without_up 1
%endif
%if !%buildsmp
%define _without_smp 1
%endif
%if !%buildpae
%define _without_pae 1
%endif
%if !%buildenterprise
%define _without_ent 1
%endif
%if !%buildxen
%define _without_xen 1
%endif
%if !%builddebug
%define _without_debug 1
%endif
%if !%builddoc
%define _without_doc 1
%endif
%if !%buildkdump
%define _without_kdump 1
%endif
%if !%buildheaders
%define _without_headers 1
%endif
%if !%buildopenafs
%define _without_openafs 1
%endif

%define _without_debuginfo 1
# ---------------------------------------------------------------------------

%define _unpackaged_files_terminate_build 0
Summary: Virtuozzo Linux kernel (the core of the Linux operating system)

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel-smp (only valid for ppc 32-bit, sparc64)
%define with_smp       %{?_without_smp:       0} %{?!_without_smp:       1}
# kernel-PAE (only valid for i686)
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-ent (only valid for i686)
%define with_ent       %{?_without_ent:       0} %{?!_without_ent:       1}
# kernel-xen (only valid for i686, x86_64 and ia64)
%define with_xen       %{?_without_xen:       0} %{?!_without_xen:       1}
# kernel-kdump (only valid for ppc64)
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{!?_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{!?_without_debuginfo: 1}
# openafs module
%define with_openafs   %{?_without_openafs:   0} %{?!_without_openafs:   1}

# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the smp kernel (--with smponly):
%define with_smponly   %{?_with_smponly:      1} %{?!_with_smponly:      0}
# Only build the xen kernel (--with xenonly):
%define with_xenonly   %{?_with_xenonly:      1} %{?!_with_xenonly:      0}

# Whether to apply the Xen patches -- leave this enabled.
%define includexen 1
%define includeovz 1

%define openafs_version 1.4.6

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

%define _enable_debug_packages 0
%global __debug_package 0

# define a flavour (default is empty)
%define flavour %nil
%if %with_pae
%define flavour PAE
%endif
%if %with_ent
%define flavour ent
%endif
%if %with_smp
%define flavour smp
%endif
%if %with_kdump
%define flavour kdump
%endif


# Versions of various parts

# After branching, please hardcode these values as the
# %%dist and %%rhel tags are not reliable yet
# For example dist -> .el5 and rhel -> 5
%define dist .el5
%define rhel 5

# Values used for RHEL version info in version.h
%define rh_release_major %rhel
%define rh_release_minor 2

#
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456"
#
%define altrelease alt1
%define buildid .%ovzver.%ovzrel.%altrelease
#
%define sublevel 18
%define kversion 2.6.%sublevel
%define rpmversion 2.6.%sublevel
%define release 92.1.13%{?dist}%{?buildid}
%define signmodules 0
%define xen_hv_cset 15502
%define xen_abi_ver 3.1
%define make_target bzImage
%define kernel_image x86
%define xen_flags verbose=y crash_debug=y XEN_VENDORVERSION=-%PACKAGE_RELEASE
%define xen_target vmlinuz
%define xen_image vmlinuz

%define KVERREL %PACKAGE_VERSION-%PACKAGE_RELEASE
%define hdrarch %_target_cpu

%if !%debugbuildsenabled
%define with_debug 0
%endif

%if !%with_debuginfo
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# if requested, only build base kernel
%if %with_baseonly
%define with_smp 0
%define with_pae 0
%define with_xen 0
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %with_smponly
%define with_up 0
%define with_pae 0
%define with_xen 0
%define with_kdump 0
%define with_debug 0
%endif

# if requested, only build xen kernel
%if %with_xenonly
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_kdump 0
%define with_debug 0
%endif

# groups of related archs
#OLPC stuff
%if 0%{?olpc}
%define with_xen 0
%endif
# Don't build 586 kernels for RHEL builds.
%if 0%{?rhel}
%define all_x86 i386 i686
# we differ here b/c of the reloc patches
%ifarch i686 x86_64
%define with_kdump 0
%endif
%else
%define all_x86 i386 i586 i686
%endif

# Overrides for generic default options

# Only ppc and sparc64 need separate smp kernels
%ifnarch ppc sparc64
%define with_smp 0
%endif

# pae is only valid on i686
%ifnarch i686
%define with_pae 0
%define with_ent 0
%endif

# xen only builds on i686, x86_64 and ia64
%ifnarch i686 x86_64 ia64
%define with_xen 0
%endif

# only build kernel-kdump on i686, x86_64 and ppc64
%ifnarch i686 x86_64 ppc64 ppc64iseries s390x
%define with_kdump 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%endif

# no need to build headers again for these arches,
# they can just use i386 and ppc64 headers
%ifarch i586 i686 ppc64iseries
%define with_headers 0
%endif

# obviously, don't build noarch kernels or headers
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_debug 0
%define all_arch_configs kernel-%kversion-*.config
%endif

# Per-arch tweaks

%ifarch %all_x86
%define all_arch_configs kernel-%kversion-i?86*.config.ovz
%define image_install_path boot
%define signmodules 0
%define hdrarch i386
%endif

%ifarch i686
# we build always xen i686 HV with pae
%define xen_flags verbose=y crash_debug=y pae=y XEN_VENDORVERSION=-%PACKAGE_RELEASE
%endif

%ifarch x86_64
%define all_arch_configs kernel-%kversion-x86_64*.config.ovz
%define image_install_path boot
%define signmodules 0
%define xen_flags verbose=y crash_debug=y max_phys_cpus=64 XEN_VENDORVERSION=-%PACKAGE_RELEASE
%endif

%ifarch ppc64 ppc64iseries
%define all_arch_configs kernel-%kversion-ppc64*.config.ovz
%define image_install_path boot
%define signmodules 0
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define hdrarch powerpc
%endif

%ifarch s390
%define all_arch_configs kernel-%kversion-s390*.config.ovz
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%endif

%ifarch s390x
%define all_arch_configs kernel-%kversion-s390x*.config.ovz
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%define hdrarch s390
%endif

%ifarch sparc
%define all_arch_configs kernel-%kversion-sparc.config.ovz
%define make_target image
%define kernel_image image
%endif

%ifarch sparc64
%define all_arch_configs kernel-%kversion-sparc64*.config.ovz
%define make_target image
%define kernel_image image
%endif

%ifarch ppc
%define all_arch_configs kernel-%kversion-ppc{-,.}*config.ovz
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define hdrarch powerpc
%endif

%ifarch ia64
%define all_arch_configs kernel-%kversion-ia64*.config.ovz
%define image_install_path boot/efi/EFI/redhat
%define signmodules 0
%define make_target compressed
%define kernel_image vmlinux.gz
# ia64 xen HV doesn't build with debug=y at the moment
%define xen_flags verbose=y crash_debug=y XEN_VENDORVERSION=-%PACKAGE_RELEASE
%define xen_target compressed
%define xen_image vmlinux.gz
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We don't build a kernel on i386 or s390x or ppc -- we only do kernel-headers there.
%define nobuildarches i386 s390 ppc

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_ent 0
%define with_xen 0
%define with_kdump 0
%define with_debug 0
%define with_debuginfo 0
%define _enable_debug_packages 0
%endif

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%if !%includeovz
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2
%else
%define kernel_dot_org_conflicts  ppp <= 2.3.15, pcmcia-cs <= 3.1.20, isdn4k-utils <= 3.0, mount < 2.10r-5, nfs-utils < 1.0.3, e2fsprogs < 1.29, util-linux < 2.10, jfsutils < 1.0.14, reiserfsprogs < 3.6.3, xfsprogs < 2.1.0, procps < 2.0.9, oprofile < 0.5.3
%endif

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%if !%includeovz
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, selinux-policy-targeted < 1.25.3-14
%else
%define package_conflicts cipe < 1.4.5, tux < 2.1.0, kudzu <= 0.92, dev < 3.2-7, iptables < 1.2.5-3, bcm5820 < 1.81, nvidia-rh72 <= 1.0
%endif

#
# The ld.so.conf.d file we install uses syntax older ldconfig's don't grok.
#
%define xen_conflicts glibc < 2.3.5-1, xen < 3.0.1

#
# Packages that need to be installed before the kernel is, because the %post
# scripts use them.
#
%if !%includeovz
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, mkinitrd >= 4.2.21-1
%else
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 5.83, mkinitrd >= 3.5.5
%endif

Name: ovzkernel
Group: System Environment/Kernel
License: GPLv2
Url: http://www.kernel.org/
Version: %rpmversion
Release: %release
%if 0%{?olpc}
ExclusiveArch: i386 i586
%else
# DO NOT CHANGE THIS LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %all_x86 x86_64 ppc ppc64 ia64 sparc sparc64 s390 s390x
%endif
ExclusiveOS: Linux
Provides: kernel = %version
Provides: kernel-drm = 4.3.0
Provides: kernel-%_target_cpu = %rpmversion-%release
Provides: vzkernel = %KVERREL
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

#
# List the packages used during the kernel build
#
BuildRequires(pre): rpm-build-kernel
BuildPreReq: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildPreReq: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils
%if %signmodules
BuildPreReq: gnupg
%endif
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

%package devel
Summary: Development package for building kernel modules to match the kernel
Group: System Environment/Kernel
AutoReqProv: no
Provides: kernel-devel-%_target_cpu = %rpmversion-%release
PreReq: /usr/bin/find

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.

%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation

%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.

%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders
# For ovzkernel-headers to install properly
Obsoletes: kernel-headers
Provides: glibc-kernheaders = 3.0-46
Provides: kernel-headers

%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package PAE
Summary: The Linux kernel compiled for PAE capable machines

Group: System Environment/Kernel
Provides: kernel = %version
Provides: kernel-drm = 4.3.0
Provides: kernel-%_target_cpu = %rpmversion-%{release}PAE
Provides: vzkernel = %KVERREL
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
Obsoletes: kernel-smp < 2.6.17
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description PAE
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

%package PAE-devel
Summary: Development package for building kernel modules to match the PAE kernel
Group: System Environment/Kernel
Provides: kernel-PAE-devel-%_target_cpu = %rpmversion-%release
Provides: kernel-devel-%_target_cpu = %rpmversion-%{release}PAE
Provides: kernel-devel = %rpmversion-%{release}PAE
AutoReqProv: no
PreReq: /usr/bin/find

%description PAE-devel
This package provides kernel headers and makefiles sufficient to build modules
against the PAE kernel package.

%package ent
Summary: The Linux kernel compiled for huge mem capable machines

Group: System Environment/Kernel
Provides: kernel = %version
Provides: kernel-drm = 4.3.0
Provides: kernel-%_target_cpu = %rpmversion-%{release}ent
Provides: vzkernel = %KVERREL
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
Obsoletes: kernel-smp < 2.6.17
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description ent
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE)
and works using 4GB split feature which increases normal zone size.
Install the kernel-ent package if your machine has more than 8GB of memory.

%package ent-devel
Summary: Development package for building kernel modules to match the ent kernel
Group: System Environment/Kernel
Provides: kernel-ent-devel-%_target_cpu = %rpmversion-%release
Provides: kernel-devel-%_target_cpu = %rpmversion-%{release}ent
Provides: kernel-devel = %rpmversion-%{release}ent
AutoReqProv: no
PreReq: /usr/bin/find

%description ent-devel
This package provides kernel headers and makefiles sufficient to build modules
against the ent kernel package.

%package smp
Summary: The Linux kernel compiled for SMP machines

Group: System Environment/Kernel
Provides: kernel = %version
Provides: kernel-drm = 4.3.0
Provides: kernel-%_target_cpu = %rpmversion-%{release}smp
Provides: vzkernel = %KVERREL
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
# upto and including kernel 2.4.9 rpms, the 4Gb+ kernel was called kernel-enterprise
# now that the smp kernel offers this capability, obsolete the old kernel
Obsoletes: kernel-enterprise < 2.4.10
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description smp
This package includes a SMP version of the Linux kernel. It is
required only on machines with two or more CPUs as well as machines with
hyperthreading technology.

Install the kernel-smp package if your machine uses two or more CPUs.

%package smp-devel
Summary: Development package for building kernel modules to match the SMP kernel
Group: System Environment/Kernel
Provides: kernel-smp-devel-%_target_cpu = %rpmversion-%release
Provides: kernel-devel-%_target_cpu = %rpmversion-%{release}smp
Provides: kernel-devel = %rpmversion-%{release}smp
AutoReqProv: no
PreReq: /usr/bin/find

%description smp-devel
This package provides kernel headers and makefiles sufficient to build modules
against the SMP kernel package.

%package xen
Summary: The Linux kernel compiled for Xen VM operations

Group: System Environment/Kernel
Provides: kernel = %version
Provides: kernel-%_target_cpu = %rpmversion-%{release}xen
Provides: xen-hypervisor-abi = %xen_abi_ver
Provides: vzkernel = %KVERREL
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
Conflicts: %xen_conflicts
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description xen
This package includes a version of the Linux kernel which
runs in Xen VM. It works for both priviledged and unpriviledged guests.

%package xen-devel
Summary: Development package for building kernel modules to match the kernel
Group: System Environment/Kernel
AutoReqProv: no
Provides: kernel-xen-devel-%_target_cpu = %rpmversion-%release
Provides: kernel-devel-%_target_cpu = %rpmversion-%{release}xen
Provides: kernel-devel = %rpmversion-%{release}xen
PreReq: /usr/bin/find

%description xen-devel
This package provides kernel headers and makefiles sufficient to build modules
against the kernel package.

%package kdump
Summary: A minimal Linux kernel compiled for kernel crash dumps

Group: System Environment/Kernel
Provides: kernel = %version
Provides: kernel-drm = 4.3.0
Provides: kernel-%_target_cpu = %rpmversion-%{release}kdump
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function
AutoReq: no
AutoProv: yes

%description kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.

%package kdump-devel
Summary: Development package for building kernel modules to match the kdump kernel
Group: System Environment/Kernel
Provides: kernel-kdump-devel-%_target_cpu = %rpmversion-%release
Provides: kernel-devel-%_target_cpu = %rpmversion-%{release}kdump
Provides: kernel-devel = %rpmversion-%{release}kdump
AutoReqProv: no
PreReq: /usr/bin/find

%description kdump-devel
This package provides kernel headers and makefiles sufficient to build modules
against the kdump kernel package.

%package debug
Summary: The Linux kernel compiled with debug config

Group: System Environment/Kernel
Provides: vzkernel
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
AutoReq: no
AutoProv: yes

%description debug
Debug kernel

%package PAE-debug
Summary: The Linux PAE kernel compiled with debug config

Group: System Environment/Kernel
Provides: vzkernel
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
AutoReq: no
AutoProv: yes

%description PAE-debug
Debug PAE kernel

%package ent-debug
Summary: The Linux ent kernel compiled with debug config

Group: System Environment/Kernel
Provides: vzkernel
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
AutoReq: no
AutoProv: yes

%description ent-debug
Debug ent kernel

%package smp-debug
Summary: The Linux smp kernel compiled with debug config

Group: System Environment/Kernel
Provides: vzkernel
Provides: vzquotamod
PreReq: %kernel_prereq
Conflicts: %kernel_dot_org_conflicts
Conflicts: %package_conflicts
AutoReq: no
AutoProv: yes

%description smp-debug
Debug smp kernel

%prep
# do a few sanity-checks for --with *only builds
%if %with_baseonly
%if !%with_up
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if %with_smponly
%if !%with_smp
echo "Cannot build --with smponly, smp build is disabled"
exit 1
%endif
%endif

%if %with_xenonly
%if !%with_xen
echo "Cannot build --with xenonly, xen build is disabled"
exit 1
%endif
%endif

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

#if a rhel kernel, apply the rhel config options
%if !%includeovz
%if 0%{?rhel}
  for i in %all_arch_configs
  do
    mv $i $i.tmp
    %_sourcedir/merge.pl %_sourcedir/config-rhel-generic $i.tmp > $i
    rm $i.tmp
  done
%ifarch ppc64 noarch
  #CONFIG_FB_MATROX is disabled for rhel generic but needed for ppc64 rhel
  for i in kernel-%kversion-ppc64.config
  do
    mv $i $i.tmp
    %_sourcedir/merge.pl %_sourcedir/config-rhel-ppc64-generic $i.tmp > $i
    rm $i.tmp
  done
%endif
%endif
%endif
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

%if !%with_debug
rm -f kernel-%kversion-*-debug.config
%endif

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
#
# Create gpg keys for signing the modules
#

%if %signmodules
gpg --homedir . --batch --gen-key %SOURCE11
gpg --homedir . --export --keyring ./kernel.pub Red > extract.pub
make linux-%kversion.%_target_cpu/scripts/bin2c
linux-%kversion.%_target_cpu/scripts/bin2c ksign_def_public_key __initdata < extract.pub > linux-%kversion.%_target_cpu/crypto/signature/key.h
%endif

###
# DO it...
###

# prepare directories

cd linux-%kversion.%_target_cpu

# Pick the right config file for the kernel we're building
if [ -n "%flavour" ] ; then
	Config=kernel-%kversion-%_target_cpu-%flavour.config.ovz
else
	Config=kernel-%kversion-%_target_cpu.config.ovz
fi

echo BUILDING A KERNEL FOR %flavour %_target_cpu...

# make sure EXTRAVERSION says what we want it to say
perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%release%flavour/" Makefile

# and now to start the build process

%make_build -s mrproper
cp configs/${Config//-debug/} .config

if echo "%flavour" | grep debug ; then
	%_sourcedir/make_debug_config.sh
fi

Arch=`head -1 .config | cut -b 3-`
echo USING ARCH=$Arch
echo "$Arch" > .buildarch

%make_build -s ARCH=$Arch nonint_oldconfig > /dev/null
%make_build -s ARCH=$Arch %{?_smp_mflags} %make_target
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
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %nil

%if %with_debuginfo
%ifnarch noarch
%global __debug_package 1
%package debuginfo-common
Summary: Kernel source files used by %name-debuginfo packages
Group: Development/Debug
Provides: %name-debuginfo-common-%_target_cpu = %KVERREL

%description debuginfo-common
This package is required by %name-debuginfo subpackages.
It provides the kernel source files common to all builds.

%files debuginfo-common
/usr/src/debug/%name-%version/linux-%kversion.%_target_cpu
%if %includexen
%if %with_xen
/usr/src/debug/%name-%version/xen
%endif
%endif
%dir /usr/src/debug
%dir %debuginfodir
%dir %debuginfodir/%image_install_path
%dir %debuginfodir/lib
%dir %debuginfodir/lib/modules
%dir %debuginfodir/usr/src/kernels
%endif
%endif

###
### install
###

%install
cd linux-%kversion.%_target_cpu
# Start installing the results

Arch=`cat .buildarch`
KernelVer=%version-%release%flavour
if [ -n "%flavour" ] ; then
	DevelDir=/usr/src/kernels/%KVERREL-%flavour-%_target_cpu
	DevelLink=/usr/src/kernels/%KVERREL%flavour-%_target_cpu
else
	DevelDir=/usr/src/kernels/%KVERREL-%_target_cpu
	DevelLink=
fi

%if %with_debuginfo
mkdir -p %buildroot%debuginfodir/boot
mkdir -p %buildroot%debuginfodir/%image_install_path
%endif
mkdir -p %buildroot/%image_install_path
install -m 644 .config %buildroot/boot/config-$KernelVer
install -m 644 System.map %buildroot/boot/System.map-$KernelVer
touch %buildroot/boot/initrd-$KernelVer.img

if [ "%kernel_image" == "x86" ]; then
    kernel_image=arch/$Arch/boot/bzImage
else
    kernel_image="%kernel_image"
fi
cp $kernel_image %buildroot/%image_install_path/vmlinuz-$KernelVer
if [ -f arch/$Arch/boot/zImage.stub ]; then
  cp arch/$Arch/boot/zImage.stub %buildroot/%image_install_path/zImage.stub-$KernelVer || :
fi

%if %includeovz
cp vmlinux %buildroot/%image_install_path/vmlinux-$KernelVer
chmod 600 %buildroot/%image_install_path/vmlinux-$KernelVer
%endif

if [ "%flavour" == "kdump" -a "$Arch" != "s390" ]; then
    rm -f %buildroot/%image_install_path/vmlinuz-$KernelVer
fi

mkdir -p %buildroot/lib/modules/$KernelVer
if [ "$Arch" != "s390" -o "%flavour" != "kdump" ]; then
  make -s ARCH=$Arch INSTALL_MOD_PATH=%buildroot modules_install KERNELRELEASE=$KernelVer
else
  touch Module.symvers
fi

# Create the kABI metadata for use in packaging
echo "**** GENERATING kernel ABI metadata ****"
gzip -c9 < Module.symvers > %buildroot/boot/symvers-$KernelVer.gz
chmod 0755 %_sourcedir/kabitool
if [ ! -e %buildroot/kabi_whitelist_%_target_cpu%flavour ]; then
    echo "**** No KABI whitelist was available during build ****"
    %_sourcedir/kabitool -b %buildroot/$DevelDir -k $KernelVer -l %buildroot/kabi_whitelist
else
cp %buildroot/kabi_whitelist_%_target_cpu%flavour %buildroot/kabi_whitelist
fi
rm -f %_tmppath/kernel-$KernelVer-kabideps
%_sourcedir/kabitool -b . -d %_tmppath/kernel-$KernelVer-kabideps -k $KernelVer -w %buildroot/kabi_whitelist

%if %with_kabichk
echo "**** kABI checking is enabled in kernel SPEC file. ****"
chmod 0755 %_sourcedir/check-kabi
if [ -e %_sourcedir/Module.kabi_%_target_cpu%flavour ]; then
cp %_sourcedir/Module.kabi_%_target_cpu%flavour %buildroot/Module.kabi
%_sourcedir/check-kabi -k %buildroot/Module.kabi -s Module.symvers || exit 1
else
echo "**** NOTE: Cannot find reference Module.kabi file. ****"
fi
%endif

# And save the headers/makefiles etc for building modules against
#
# This all looks scary, but the end result is supposed to be:
# * all arch relevant include/ files
# * all Makefile/Kconfig files
# * all script/ files

rm -f %buildroot/lib/modules/$KernelVer/build
rm -f %buildroot/lib/modules/$KernelVer/source
mkdir -p %buildroot/lib/modules/$KernelVer/build
(cd %buildroot/lib/modules/$KernelVer ; ln -s build source)
# dirs for additional modules per module-init-tools, kbuild/modules.txt
mkdir -p %buildroot/lib/modules/$KernelVer/extra
mkdir -p %buildroot/lib/modules/$KernelVer/updates
mkdir -p %buildroot/lib/modules/$KernelVer/weak-updates
%if %with_openafs
find $OpenAfsDir -name libafs.ko -execdir cp '{}' %buildroot/lib/modules/$KernelVer/extra/openafs.ko \;
%endif
# first copy everything
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %buildroot/lib/modules/$KernelVer/build
cp Module.symvers %buildroot/lib/modules/$KernelVer/build
mv %buildroot/kabi_whitelist %buildroot/lib/modules/$KernelVer/build
if [ -e %buildroot/Module.kabi ]; then
mv %buildroot/Module.kabi %buildroot/lib/modules/$KernelVer/build
fi
cp symsets-$KernelVer.tar.gz %buildroot/lib/modules/$KernelVer/build
# then drop all but the needed Makefiles/Kconfig files
rm -rf %buildroot/lib/modules/$KernelVer/build/Documentation
rm -rf %buildroot/lib/modules/$KernelVer/build/scripts
rm -rf %buildroot/lib/modules/$KernelVer/build/include
cp .config %buildroot/lib/modules/$KernelVer/build
cp -a scripts %buildroot/lib/modules/$KernelVer/build
if [ -d arch/%_arch/scripts ]; then
  cp -a arch/%_arch/scripts %buildroot/lib/modules/$KernelVer/build/arch/%_arch || :
fi
if [ -f arch/%_arch/*lds ]; then
  cp -a arch/%_arch/*lds %buildroot/lib/modules/$KernelVer/build/arch/%_arch/ || :
fi
rm -f %buildroot/lib/modules/$KernelVer/build/scripts/*.o
rm -f %buildroot/lib/modules/$KernelVer/build/scripts/*/*.o
mkdir -p %buildroot/lib/modules/$KernelVer/build/include
pushd include
cp -a acpi config keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound video asm asm-generic ub %buildroot/lib/modules/$KernelVer/build/include
cp -a `readlink asm` %buildroot/lib/modules/$KernelVer/build/include
if [ "$Arch" = "x86_64" ]; then
  cp -a asm-i386 %buildroot/lib/modules/$KernelVer/build/include
fi
# While arch/powerpc/include/asm is still a symlink to the old
# include/asm-ppc{64,} directory, include that in kernel-devel too.
if [ "$Arch" = "powerpc" -a -r ../arch/powerpc/include/asm ]; then
  cp -a `readlink ../arch/powerpc/include/asm` %buildroot/lib/modules/$KernelVer/build/include
  mkdir -p %buildroot/lib/modules/$KernelVer/build/arch/$Arch/include
  pushd %buildroot/lib/modules/$KernelVer/build/arch/$Arch/include
  ln -sf ../../../include/asm-ppc* asm
  popd
fi
%if %includexen
%if %with_xen
cp -a xen %buildroot/lib/modules/$KernelVer/build/include
%endif
%endif

# Make sure the Makefile and version.h have a matching timestamp so that
# external modules can be built
touch -r %buildroot/lib/modules/$KernelVer/build/Makefile %buildroot/lib/modules/$KernelVer/build/include/linux/version.h
touch -r %buildroot/lib/modules/$KernelVer/build/.config %buildroot/lib/modules/$KernelVer/build/include/linux/autoconf.h
# Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
cp %buildroot/lib/modules/$KernelVer/build/.config %buildroot/lib/modules/$KernelVer/build/include/config/auto.conf
popd

#
# save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
#
%if %with_debuginfo
mkdir -p %buildroot%debuginfodir/lib/modules/$KernelVer
cp vmlinux %buildroot%debuginfodir/lib/modules/$KernelVer
%endif

find %buildroot/lib/modules/$KernelVer -name "*.ko" -type f >modnames

# gpg sign the modules
%if %signmodules
gcc -o scripts/modsign/mod-extract scripts/modsign/mod-extract.c -Wall
KEYFLAGS="--no-default-keyring --homedir .."
KEYFLAGS="$KEYFLAGS --secret-keyring ../kernel.sec"
KEYFLAGS="$KEYFLAGS --keyring ../kernel.pub"
export KEYFLAGS

for i in `cat modnames`
do
  sh ./scripts/modsign/modsign.sh $i Red
  mv -f $i.signed $i
done
unset KEYFLAGS
%endif

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
rm -f modinfo
rm -f modnames
# remove files that will be auto generated by depmod at rpm -i time
rm -f %buildroot/lib/modules/$KernelVer/modules.*

# Move the devel headers out of the root file system
mkdir -p %buildroot/usr/src/kernels
mv %buildroot/lib/modules/$KernelVer/build %buildroot/$DevelDir
ln -sf ../../..$DevelDir %buildroot/lib/modules/$KernelVer/build
[ -z "$DevelLink" ] || ln -sf `basename $DevelDir` %buildroot/$DevelLink

	# Temporary fix for upstream "make prepare" bug.
#	pushd $RPM_BUILD_ROOT/$DevelDir > /dev/null
#	if [ -f Makefile ]; then
#		make prepare
#	fi
#	popd > /dev/null

# EOoldBuildKernel
%ifnarch %nobuildarches noarch
mkdir -p %buildroot/etc/modprobe.d
cat > %buildroot/etc/modprobe.d/blacklist-firewire << \EOF
# Comment out the next line to enable the firewire drivers
blacklist firewire-ohci
EOF
%endif

%if %includexen
%if %with_xen
mkdir -p %buildroot/etc/ld.so.conf.d
rm -f %buildroot/etc/ld.so.conf.d/kernelcap-%KVERREL.conf
cat > %buildroot/etc/ld.so.conf.d/kernelcap-%KVERREL.conf <<\EOF
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 0 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 0 nosegneg
EOF
chmod 444 %buildroot/etc/ld.so.conf.d/kernelcap-%KVERREL.conf
%endif
%endif

%if %with_doc
mkdir -p %buildroot/usr/share/doc/kernel-doc-%kversion/Documentation

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a+r *
# copy the source over
tar cf - Documentation | tar xf - -C %buildroot/usr/share/doc/kernel-doc-%kversion
%endif

%if %with_headers
# Install kernel headers
make ARCH=%hdrarch INSTALL_HDR_PATH=%buildroot/usr headers_install

# Manually go through the 'headers_check' process for every file, but
# don't die if it fails
chmod +x scripts/hdrcheck.sh
echo -e '*****\n*****\nHEADER EXPORT WARNINGS:\n*****' > hdrwarnings.txt
for FILE in `find %buildroot/usr/include` ; do
    scripts/hdrcheck.sh %buildroot/usr/include $FILE >> hdrwarnings.txt || :
done
echo -e '*****\n*****' >> hdrwarnings.txt
if grep -q exist hdrwarnings.txt; then
   sed s:^%buildroot/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

# glibc provides scsi headers for itself, for now
rm -rf %buildroot/usr/include/scsi
rm -f %buildroot/usr/include/asm*/atomic.h
rm -f %buildroot/usr/include/asm*/io.h
rm -f %buildroot/usr/include/asm*/irq.h
%endif

###
### scripts
###

%post
%post_kernel_image %KVERREL

%post debug
%post_kernel_image %{KVERREL}debug

%post devel
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%KVERREL-%_target_cpu > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post smp
%post_kernel_image %{KVERREL}smp

%post smp-debug
[ -x /sbin/vzkernel-install ] && /sbin/vzkernel-install --install --mkinitrd --depmod %KVERREL-smp-debug
[ -f /etc/modprobe.conf ] && ! grep -qE "ip_conntrack_(en|dis)able_ve0" /etc/modprobe.conf && \
	echo 'options ip_conntrack ip_conntrack_disable_ve0=1' >> /etc/modprobe.conf
[ -f /etc/modules.conf ] && ! grep -qE "ip_conntrack_(en|dis)able_ve0" /etc/modules.conf && \
	echo 'options ip_conntrack ip_conntrack_disable_ve0=1' >> /etc/modules.conf
exit 0

%post smp-devel
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%KVERREL-smp-%_target_cpu > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post PAE
%post_kernel_image %{KVERREL}PAE

%post PAE-debug
%post_kernel_image %{KVERREL}PAE-debug

%post PAE-devel
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%KVERREL-PAE-%_target_cpu > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post ent
%post_kernel_image %{KVERREL}ent

%post ent-debug
%post_kernel_image %{KVERREL}ent-debug

%post ent-devel
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%KVERREL-ent-%_target_cpu > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post xen
if [ -e /proc/xen/xsd_kva -o ! -d /proc/xen ]; then
	/sbin/new-kernel-pkg --package kernel-xen --mkinitrd --depmod --install --multiboot=/%image_install_path/xen.gz-%KVERREL %{KVERREL}xen || exit $?
else
	%post_kernel_image %{KVERREL}xen || exit $?
fi
if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi
exit 0

%post xen-devel
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%KVERREL-xen-%_target_cpu > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%post kdump
%post_kernel_image %{KVERREL}kdump

%post kdump-devel
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ] ; then
  pushd /usr/src/kernels/%KVERREL-kdump-%_target_cpu > /dev/null
  /usr/bin/find . -type f | while read f; do hardlink -c /usr/src/kernels/*FC*/$f $f ; done
  popd > /dev/null
fi

%preun
%preun_kernel_image %KVERREL

%preun debug
%preun_kernel_image %{KVERREL}debug

%preun smp
%preun_kernel_image %{KVERREL}smp

%preun smp-debug
%preun_kernel_image %{KVERREL}smp-debug

%preun PAE
%preun_kernel_image %{KVERREL}PAE

%preun PAE-debug
%preun_kernel_image %{KVERREL}PAE-debug

%preun ent
%preun_kernel_image %{KVERREL}ent

%preun ent-debug
%preun_kernel_image %{KVERREL}ent-debug

%preun kdump
%preun_kernel_image %{KVERREL}kdump

%preun xen
%preun_kernel_image %{KVERREL}xen

###
### file lists
###

# This is %image_install_path on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%image_install_path}

%if %with_up
%if %with_debuginfo
%ifnarch noarch
%package debuginfo
Summary: Debug information for package %name
Group: Development/Debug
Requires: %name-debuginfo-common-%_target_cpu = %KVERREL
Provides: %name-debuginfo-%_target_cpu = %KVERREL
%description debuginfo
This package provides debug information for package %name
This is required to use SystemTap with %name-%KVERREL.
%files debuginfo
%if "%elf_image_install_path" != ""
%debuginfodir/%elf_image_install_path/*-%KVERREL.debug
%endif
%debuginfodir/lib/modules/%KVERREL
%debuginfodir/usr/src/kernels/%KVERREL-%_target_cpu
%endif
%endif

%files
/%image_install_path/vmlinuz-%KVERREL
/%image_install_path/vmlinux-%KVERREL
/boot/System.map-%KVERREL
/boot/symvers-%KVERREL.gz
/boot/config-%KVERREL
%dir /lib/modules/%KVERREL
/lib/modules/%KVERREL/kernel
/lib/modules/%KVERREL/build
/lib/modules/%KVERREL/source
/lib/modules/%KVERREL/extra
/lib/modules/%KVERREL/updates
/lib/modules/%KVERREL/weak-updates
%ghost /boot/initrd-%KVERREL.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%if %with_debug
%files debug
/%image_install_path/vmlinuz-%{KVERREL}debug
/%image_install_path/vmlinux-%{KVERREL}debug
/boot/System.map-%{KVERREL}debug
/boot/symvers-%{KVERREL}debug.gz
/boot/config-%{KVERREL}debug
%dir /lib/modules/%{KVERREL}debug
/lib/modules/%{KVERREL}debug/kernel
/lib/modules/%{KVERREL}debug/build
/lib/modules/%{KVERREL}debug/source
/lib/modules/%{KVERREL}debug/extra
/lib/modules/%{KVERREL}debug/updates
/lib/modules/%{KVERREL}debug/weak-updates
%ghost /boot/initrd-%{KVERREL}debug.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire
%endif

%files devel
%verify(not mtime) /usr/src/kernels/%KVERREL-%_target_cpu
%endif

%if %with_headers
%files headers
/usr/include/*
%endif

%if %with_pae
%if %with_debuginfo
%ifnarch noarch
%package PAE-debuginfo
Summary: Debug information for package %name-PAE
Group: Development/Debug
Requires: %name-debuginfo-common-%_target_cpu = %KVERREL
Provides: %name-%PAE-debuginfo-%_target_cpu = %KVERREL
%description PAE-debuginfo
This package provides debug information for package %name-PAE
This is required to use SystemTap with %name-PAE-%KVERREL.
%files PAE-debuginfo
%if "%elf_image_install_path" != ""
%debuginfodir/%elf_image_install_path/*-%{KVERREL}PAE.debug
%endif
%debuginfodir/lib/modules/%{KVERREL}PAE
%debuginfodir/usr/src/kernels/%KVERREL-PAE-%_target_cpu
%endif
%endif

%files PAE
/%image_install_path/vmlinuz-%{KVERREL}PAE
/%image_install_path/vmlinux-%{KVERREL}PAE
/boot/System.map-%{KVERREL}PAE
/boot/symvers-%{KVERREL}PAE.gz
/boot/config-%{KVERREL}PAE
%dir /lib/modules/%{KVERREL}PAE
/lib/modules/%{KVERREL}PAE/kernel
/lib/modules/%{KVERREL}PAE/build
/lib/modules/%{KVERREL}PAE/source
/lib/modules/%{KVERREL}PAE/extra
/lib/modules/%{KVERREL}PAE/updates
/lib/modules/%{KVERREL}PAE/weak-updates
%ghost /boot/initrd-%{KVERREL}PAE.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%if %with_debug
%files PAE-debug
/%image_install_path/vmlinuz-%{KVERREL}PAE-debug
/%image_install_path/vmlinux-%{KVERREL}PAE-debug
/boot/System.map-%{KVERREL}PAE-debug
/boot/symvers-%{KVERREL}PAE-debug.gz
/boot/config-%{KVERREL}PAE-debug
%dir /lib/modules/%{KVERREL}PAE-debug
/lib/modules/%{KVERREL}PAE-debug/kernel
/lib/modules/%{KVERREL}PAE-debug/build
/lib/modules/%{KVERREL}PAE-debug/source
/lib/modules/%{KVERREL}PAE-debug/extra
/lib/modules/%{KVERREL}PAE-debug/updates
/lib/modules/%{KVERREL}PAE-debug/weak-updates
%ghost /boot/initrd-%{KVERREL}PAE-debug.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire
%endif

%files PAE-devel
%verify(not mtime) /usr/src/kernels/%KVERREL-PAE-%_target_cpu
/usr/src/kernels/%{KVERREL}PAE-%_target_cpu
%endif

%if %with_ent
%if %with_debuginfo
%ifnarch noarch
%package ent-debuginfo
Summary: Debug information for package %name-ent
Group: Development/Debug
Requires: %name-debuginfo-common-%_target_cpu = %KVERREL
Provides: %name-%ent-debuginfo-%_target_cpu = %KVERREL
%description ent-debuginfo
This package provides debug information for package %name-ent
This is required to use SystemTap with %name-ent-%KVERREL.
%files ent-debuginfo
%if "%elf_image_install_path" != ""
%debuginfodir/%elf_image_install_path/*-%{KVERREL}ent.debug
%endif
%debuginfodir/lib/modules/%{KVERREL}ent
%debuginfodir/usr/src/kernels/%KVERREL-ent-%_target_cpu
%endif
%endif

%files ent
/%image_install_path/vmlinuz-%{KVERREL}ent
/boot/System.map-%{KVERREL}ent
/boot/symvers-%{KVERREL}ent.gz
/boot/config-%{KVERREL}ent
%dir /lib/modules/%{KVERREL}ent
/lib/modules/%{KVERREL}ent/kernel
/lib/modules/%{KVERREL}ent/build
/lib/modules/%{KVERREL}ent/source
/lib/modules/%{KVERREL}ent/extra
/lib/modules/%{KVERREL}ent/updates
/lib/modules/%{KVERREL}ent/weak-updates
%ghost /boot/initrd-%{KVERREL}ent.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%if %with_debug
%files ent-debug
/%image_install_path/vmlinuz-%{KVERREL}ent-debug
/%image_install_path/vmlinux-%{KVERREL}ent-debug
/boot/System.map-%{KVERREL}ent-debug
/boot/symvers-%{KVERREL}ent-debug.gz
/boot/config-%{KVERREL}ent-debug
%dir /lib/modules/%{KVERREL}ent-debug
/lib/modules/%{KVERREL}ent-debug/kernel
/lib/modules/%{KVERREL}ent-debug/build
/lib/modules/%{KVERREL}ent-debug/source
/lib/modules/%{KVERREL}ent-debug/extra
/lib/modules/%{KVERREL}ent-debug/updates
/lib/modules/%{KVERREL}ent-debug/weak-updates
%ghost /boot/initrd-%{KVERREL}ent-debug.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire
%endif

%files ent-devel
%verify(not mtime) /usr/src/kernels/%KVERREL-ent-%_target_cpu
/usr/src/kernels/%{KVERREL}ent-%_target_cpu
%endif

%if %with_smp
%if %with_debuginfo
%ifnarch noarch
%package smp-debuginfo
Summary: Debug information for package %name-smp
Group: Development/Debug
Requires: %name-debuginfo-common-%_target_cpu = %KVERREL
Provides: %name-%smp-debuginfo-%_target_cpu = %KVERREL
%description smp-debuginfo
This package provides debug information for package %name-smp
This is required to use SystemTap with %name-smp-%KVERREL.
%files smp-debuginfo
%if "%elf_image_install_path" != ""
%debuginfodir/%elf_image_install_path/*-%{KVERREL}smp.debug
%endif
%debuginfodir/lib/modules/%{KVERREL}smp
%debuginfodir/usr/src/kernels/%KVERREL-smp-%_target_cpu
%endif
%endif

%files smp
/%image_install_path/vmlinuz-%{KVERREL}smp
/boot/System.map-%{KVERREL}smp
/boot/symvers-%{KVERREL}smp.gz
/boot/config-%{KVERREL}smp
%dir /lib/modules/%{KVERREL}smp
/lib/modules/%{KVERREL}smp/kernel
/lib/modules/%{KVERREL}smp/build
/lib/modules/%{KVERREL}smp/source
/lib/modules/%{KVERREL}smp/extra
/lib/modules/%{KVERREL}smp/updates
/lib/modules/%{KVERREL}smp/weak-updates
%ghost /boot/initrd-%{KVERREL}smp.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files smp-devel
%verify(not mtime) /usr/src/kernels/%KVERREL-smp-%_target_cpu
/usr/src/kernels/%{KVERREL}smp-%_target_cpu
%endif

%if %includexen
%if %with_xen
%if %with_debuginfo
%ifnarch noarch
%package xen-debuginfo
Summary: Debug information for package %name-xen
Group: Development/Debug
Requires: %name-debuginfo-common-%_target_cpu = %KVERREL
Provides: %name-xen-debuginfo-%_target_cpu = %KVERREL
%description xen-debuginfo
This package provides debug information for package %name-xen
This is required to use SystemTap with %name-xen-%KVERREL.
%files xen-debuginfo
%if "%elf_image_install_path" != ""
%debuginfodir/%elf_image_install_path/*-%{KVERREL}xen.debug
%endif
%debuginfodir/lib/modules/%{KVERREL}xen
%debuginfodir/usr/src/kernels/%KVERREL-xen-%_target_cpu
%debuginfodir/boot/xen*-%KVERREL.debug
%endif
%endif

%files xen
/%image_install_path/vmlinuz-%{KVERREL}xen
/boot/System.map-%{KVERREL}xen
/boot/symvers-%{KVERREL}xen.gz
/boot/config-%{KVERREL}xen
/%image_install_path/xen.gz-%KVERREL
/boot/xen-syms-%KVERREL
%dir /lib/modules/%{KVERREL}xen
/lib/modules/%{KVERREL}xen/kernel
%verify(not mtime) /lib/modules/%{KVERREL}xen/build
/lib/modules/%{KVERREL}xen/source
/etc/ld.so.conf.d/kernelcap-%KVERREL.conf
/lib/modules/%{KVERREL}xen/extra
/lib/modules/%{KVERREL}xen/updates
/lib/modules/%{KVERREL}xen/weak-updates
%ghost /boot/initrd-%{KVERREL}xen.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files xen-devel
%verify(not mtime) /usr/src/kernels/%KVERREL-xen-%_target_cpu
/usr/src/kernels/%{KVERREL}xen-%_target_cpu
%endif

%endif

%if %with_kdump
%if %with_debuginfo
%ifnarch noarch
%package kdump-debuginfo
Summary: Debug information for package %name-kdump
Group: Development/Debug
Requires: %name-debuginfo-common-%_target_cpu = %KVERREL
Provides: %name-kdump-debuginfo-%_target_cpu = %KVERREL
%description kdump-debuginfo
This package provides debug information for package %name-kdump
This is required to use SystemTap with %name-kdump-%KVERREL.
%files kdump-debuginfo
%ifnarch s390x
%if "%image_install_path" != ""
%debuginfodir/%image_install_path/*-%{KVERREL}kdump.debug
%endif
%else
%if "%elf_image_install_path" != ""
%debuginfodir/%elf_image_install_path/*-%{KVERREL}kdump.debug
%endif
%endif
%debuginfodir/lib/modules/%{KVERREL}kdump
%debuginfodir/usr/src/kernels/%KVERREL-kdump-%_target_cpu
%endif
%endif

%files kdump
%ifnarch s390x
/%image_install_path/vmlinux-%{KVERREL}kdump
%else
/%image_install_path/vmlinuz-%{KVERREL}kdump
%endif
/boot/System.map-%{KVERREL}kdump
/boot/symvers-%{KVERREL}kdump.gz
/boot/config-%{KVERREL}kdump
%dir /lib/modules/%{KVERREL}kdump
/lib/modules/%{KVERREL}kdump/build
/lib/modules/%{KVERREL}kdump/source
%ifnarch s390x
/lib/modules/%{KVERREL}kdump/kernel
/lib/modules/%{KVERREL}kdump/extra
/lib/modules/%{KVERREL}kdump/updates
/lib/modules/%{KVERREL}kdump/weak-updates
%endif
%ghost /boot/initrd-%{KVERREL}kdump.img
%config(noreplace) /etc/modprobe.d/blacklist-firewire

%files kdump-devel
%verify(not mtime) /usr/src/kernels/%KVERREL-kdump-%_target_cpu
/usr/src/kernels/%{KVERREL}kdump-%_target_cpu
%endif

# only some architecture builds need kernel-doc

%if %with_doc
%files doc
%_datadir/doc/kernel-doc-%kversion/Documentation/*
%dir %_datadir/doc/kernel-doc-%kversion/Documentation
%dir %_datadir/doc/kernel-doc-%kversion
%endif
