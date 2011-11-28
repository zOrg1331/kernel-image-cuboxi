%set_verify_elf_skiplist /boot/*
%set_strip_skiplist /boot/*

%define with_doc       0
%define with_headers   1
%define with_openafs   0
%define ovzver 028stab095
%define ovzrel 1

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
%define rh_release_minor 7

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
%define krelease alt13.M51.34
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
Provides: vzeventmod
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
Source107: kabi_whitelist_s390x
Source108: kabi_whitelist_x86_64
Source109: kabi_whitelist_x86_64xen

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

Patch0: patch-2.6.18.4

Patch1: kernel-2.6.18-redhat.patch
Patch2: xen-config-2.6.18-redhat.patch
Patch3: xen-2.6.18-redhat.patch

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
Patch90000: patch-linux-2.6.18-rhel5-drbd-8.3.10
Patch90001: diff-drbd-compilation
Patch90002: diff-drbd-dont-use-connector
Patch90003: diff-drbd-compilation-a
Patch90004: diff-drbd-compilation-b

# Areca
# replaced with linux-2.6-scsi-add-kernel-support-for-areca-raid-controller.patch
# Patch90200: linux-2.6.18-arcmsr-1.20.0X.14.devel.patch

# 3ware

Patch90210: linux-2.6.18-atl1-2.1.3.patch
Patch90211: diff-backport-dm-delay-20070716
Patch90212: diff-dm-limits-bounce_pfn-20071029
# Patch90213: diff-forcedeth-fix-timeout-20071129
# Patch90214: linux-2.6.18-r8169-2.2LK-NAPI-ms-2.6.24-rc3.patch
# this patch doesn't fully help, see bug #95898. simply disabled CONFIG_FB_INTEL
# Patch90215: diff-intelfb-noregister-workaround-20071212
Patch90216: diff-snd-hda-intel
Patch90217: diff-drv-e1000-depends-e1000e-20080718
Patch90220: diff-drv-e1000-select-e1000e

Patch90225: diff-drv-aacraid-PMC-Sierra-support-20110912

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
Patch91004: diff-serial-pci-add-netmos-9901-support
Patch91006: diff-serial-pci-add-netmos-9835-support

# Bells and whistles
Patch100001: diff-ms-devleak-dstdebug-20080504
Patch100002: diff-ipv4-dumpbaddst-20080929
Patch100003: diff-ipv4-reliable-dst-garbage-20080929
Patch100004: diff-ve-moreleaks-20090829
Patch100014: diff-ms-devleaktime-20081111
Patch100016: diff-rh-cifs-disable-posix-extensons-by-default-20090304
Patch100017: diff-ms-32bitHW-kernel-panic-string
Patch100018: diff-ms-mmap-min-addr
Patch100020: linux-2.6.18-128.1.1.el5.028stab062.3-build-fixes.diff
Patch100024: diff-make-sysrq-mask-affect-proc-sysrq-trigger-20090826
Patch100025: diff-ms-alow-ve0-exceed-threads-max
Patch100026: diff-ms-ext4-nodelalloc-by-default
Patch100027: diff-rh-hung-task-tunes-and-fixes
Patch100029: diff-vmalloc-supress-passing-gfp-dma32-to-slab
Patch100036: diff-ubc-debug-sock-orphan-acct

Patch100038: linux-2.6-fs-fix-wrongly-kfree-ing-a-vmalloc-ed-area.patch
Patch100039: diff-cpt-remove-div_long_long_rem.patch

# MAC HW hacks
Patch101000: diff-mac-acpi-scan-rsdp-bit-lower-20090811
Patch101001: diff-mac-cpufreq-bug-on-apple-xserve-20090811
Patch101007: diff-ms-reboot-via-pci-port-cf9-20090922

# NBD
Patch110001: diff-nbd-from-current-1
Patch110002: diff-nbd-compile-fixes-1
Patch110003: diff-nbd-umount-after-connection-lost
Patch110005: diff-nbd-spinlock-usage-fix
Patch110006: diff-nbd-xmit-timeout
Patch110007: diff-nbd-remove-truncate-at-disconnect-20090529
Patch110008: diff-nbd-forbid-socket-clear-without-disconnect-20090529
Patch110009: diff-nbd-pid_show-args-number-20090916

# End VZ patches

# empty final patch file to facilitate testing of kernel patches
Patch99999: linux-kernel-test.patch

# ALT-specific patches
Patch200000: our_kernel.patch
Patch200001: diff-rh-vdso-remove-note-part.alt-specific

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
This package contains the Linux kernel that is used to boot and run
your system.

Most hardware drivers for this kernel are built as modules.  Some of
these drivers are built separately from the kernel; they are available
in separate packages (kernel-modules-*-%flavour).

The "ovz-rhel" variant of kernel packages is a RHEL5 based OpenVZ kernel.
OpenVZ is container-based virtualization for Linux that creates multiple
secure, isolated containers on a single physical server enabling better
server utilization and ensuring that applications do not conflict.

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

%patch0 -p1

%patch1 -p1 -E

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
%patch90003 -p1
%patch90004 -p1

%patch90210 -p1
%patch90211 -p1
%patch90212 -p1
# %patch90213 -p1 obsoleted by linux-2.6-net-forcedeth-boot-delay-fix.patch
# %patch90214 -p1 obsoleted by linux-2.6-net-r8169-support-realtek-8111c-and-8101e-loms.patch
#%patch90215 -p1
%patch90216 -p1
%patch90217 -p1
%patch90220 -p1

%patch90225 -p1

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
%patch91004 -p1
%patch91006 -p1

%patch100001 -p1
%patch100002 -p1
%patch100003 -p1
%patch100004 -p1
%patch100014 -p1
%patch100016 -p1
%patch100017 -p1
%patch100018 -p1
%patch100020 -p1
%patch100024 -p1
%patch100025 -p1
%patch100026 -p1
%patch100027 -p1
%patch100029 -p1
%patch100036 -p1

%patch100038 -p1
%patch100039 -p1

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
%patch200001 -p1

# END OF PATCH APPLICATIONS

cp %SOURCE10 Documentation/

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# Unpack the Xen tarball.

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
cp -a acpi config keys linux math-emu media mtd net pcmcia rdma rxrpc scsi sound trace video asm asm-generic ub %buildroot%modules_dir/build/include
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
* Mon Nov 28 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.34
- Release of 2.6.18-274.7.1.el5 028stab095.1

* Fri Nov 11 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.33
- Release of 2.6.18-274.3.1.el5 028stab094.3

* Tue Jul 26 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.32
- Release of 2.6.18-238.19.1.el5 028stab092.2

* Tue Jun 14 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.31
- Release of 2.6.18-238.12.1.el5 028stab091.1

* Fri Apr 15 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.30
- Release of 2.6.18-238.9.1.el5 028stab089.1

* Mon Apr 11 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.29
- Release of 2.6.18-238.5.1.el5 028stab088.1

* Fri Mar 18 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.28
- Release of 2.6.18-238.5.1.el5 028stab087.1

* Sat Mar 12 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.27
- Release of 2.6.18-238.5.1.el5 028stab085.2

* Sun Mar 06 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.26
- Release of 2.6.18-238.5.1.el5 028stab085.1

* Wed Mar 02 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.25
- Fix several CVE:
  * CVE-2010-4249: kernel: unix socket local dos
  * CVE-2010-4251: kernel: multicast IPv4 traffic on hipersockets device DoS
  * CVE-2010-4655: kernel: heap contents leak for CAP_NET_ADMIN via ethtool ioctl

* Tue Feb 15 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.24
- Release of 2.6.18-238.1.1.el5 028stab084.4

* Tue Feb 08 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.23
- Release of 2.6.18-238.1.1.el5 028stab084.2

* Fri Feb 04 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.22
- Release of 2.6.18-238.1.1.el5 028stab084.1

* Thu Jan 27 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.21
- Release of 2.6.18-238.1.1.el5 028stab083.1

* Fri Jan 21 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.20
- Release of 2.6.18-194.32.1.el5 028stab082.1

* Mon Jan 17 2011 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.19
- Enable IPv6

* Wed Dec 22 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.18
- Release of 2.6.18-194.26.1.el5 028stab079.2

* Wed Dec 01 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.17
- Release of 2.6.18-194.26.1.el5 028stab079.1

* Thu Nov 11 2010 Anton Protopopov <aspsk@altlinux.org> 2.6.18-alt13.M51.16
- Release of 2.6.18-194.17.1.el5 028stab077.1

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
