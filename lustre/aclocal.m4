# generated automatically by aclocal 1.7.9 -*- Autoconf -*-

# Copyright (C) 1996, 1997, 1998, 1999, 2000, 2001, 2002
# Free Software Foundation, Inc.
# This file is free software; the Free Software Foundation
# gives unlimited permission to copy and/or distribute it,
# with or without modifications, as long as this notice is preserved.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, to the extent permitted by law; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.

# AM_CONDITIONAL                                              -*- Autoconf -*-

# Copyright 1997, 2000, 2001 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# serial 5

AC_PREREQ(2.52)

# AM_CONDITIONAL(NAME, SHELL-CONDITION)
# -------------------------------------
# Define a conditional.
AC_DEFUN([AM_CONDITIONAL],
[ifelse([$1], [TRUE],  [AC_FATAL([$0: invalid condition: $1])],
        [$1], [FALSE], [AC_FATAL([$0: invalid condition: $1])])dnl
AC_SUBST([$1_TRUE])
AC_SUBST([$1_FALSE])
if $2; then
  $1_TRUE=
  $1_FALSE='#'
else
  $1_TRUE='#'
  $1_FALSE=
fi
AC_CONFIG_COMMANDS_PRE(
[if test -z "${$1_TRUE}" && test -z "${$1_FALSE}"; then
  AC_MSG_ERROR([conditional "$1" was never defined.
Usually this means the macro was only invoked conditionally.])
fi])])

#
# LB_CHECK_VERSION
#
# Verify that LUSTRE_VERSION was defined properly
#
AC_DEFUN([LB_CHECK_VERSION],
[if test "LUSTRE_VERSION" = "LUSTRE""_VERSION" ; then
	AC_MSG_ERROR([This script was not built with a version number.])
fi
])

#
# LB_CANONICAL_SYSTEM
#
# fixup $target_os for use in other places
#
AC_DEFUN([LB_CANONICAL_SYSTEM],
[case $target_os in
	linux*)
		lb_target_os="linux"
		;;
	darwin*)
		lb_target_os="darwin"
		;;
	solaris*)
		lb_target_os="SunOS"
		;;esac
AC_SUBST(lb_target_os)
])

#
# LB_CHECK_FILE
#
# Check for file existance even when cross compiling
#
AC_DEFUN([LB_CHECK_FILE],
[AS_VAR_PUSHDEF([lb_File], [lb_cv_file_$1])dnl
AC_CACHE_CHECK([for $1], lb_File,
[if test -r "$1"; then
  AS_VAR_SET(lb_File, yes)
else
  AS_VAR_SET(lb_File, no)
fi])
AS_IF([test AS_VAR_GET(lb_File) = yes], [$2], [$3])[]dnl
AS_VAR_POPDEF([lb_File])dnl
])# LB_CHECK_FILE


#
# LB_ARG_LIBS_INCLUDES
#
# support for --with-foo, --with-foo-includes, and --with-foo-libs in
# a single magical macro
#
AC_DEFUN([LB_ARG_LIBS_INCLUDES],
[lb_pathvar="m4_bpatsubst([$2], -, _)"
AC_MSG_CHECKING([for $1])
AC_ARG_WITH([$2],
	AC_HELP_STRING([--with-$2=path],
		[path to $1]),
	[],[withval=$4])

if test x$withval = xyes ; then
	eval "$lb_pathvar='$3'"
else
	eval "$lb_pathvar='$withval'"
fi
AC_MSG_RESULT([${!lb_pathvar:-no}])

if test x${!lb_pathvar} != x -a x${!lb_pathvar} != xno ; then
	AC_MSG_CHECKING([for $1 includes])
	AC_ARG_WITH([$2-includes],
		AC_HELP_STRING([--with-$2-includes=path],
			[path to $1 includes]),
		[],[withval='yes'])

	lb_includevar="${lb_pathvar}_includes"
	if test x$withval = xyes ; then
		eval "${lb_includevar}='${!lb_pathvar}/include'"
	else
		eval "${lb_includevar}='$withval'"
	fi
	AC_MSG_RESULT([${!lb_includevar}])

	AC_MSG_CHECKING([for $1 libs])
	AC_ARG_WITH([$2-libs],
		AC_HELP_STRING([--with-$2-libs=path],
			[path to $1 libs]),
		[],[withval='yes'])

	lb_libvar="${lb_pathvar}_libs"
	if test x$withval = xyes ; then
		eval "${lb_libvar}='${!lb_pathvar}/lib'"
	else
		eval "${lb_libvar}='$withval'"
	fi
	AC_MSG_RESULT([${!lb_libvar}])
fi
])
])

#
# LB_PATH_LIBSYSIO
#
# Handle internal/external libsysio
#
AC_DEFUN([LB_PATH_LIBSYSIO],
[AC_ARG_WITH([sysio],
	AC_HELP_STRING([--with-sysio=path],
			[set path to libsysio source (default is included libsysio)]),
	[],[
		case $lb_target_os in
			linux)
				with_sysio='yes'
				;;
			*)
				with_sysio='no'
				;;
		esac
	])
AC_MSG_CHECKING([location of libsysio])
enable_sysio="$with_sysio"
case x$with_sysio in
	xyes)
		AC_MSG_RESULT([internal])
		LB_CHECK_FILE([$srcdir/libsysio/src/rmdir.c],[],[
			AC_MSG_ERROR([A complete internal libsysio was not found.])
		])
		LIBSYSIO_SUBDIR="libsysio"
		SYSIO="$PWD/libsysio"
		;;
	xno)
		AC_MSG_RESULT([disabled])
		;;
	*)
		AC_MSG_RESULT([$with_sysio])
		LB_CHECK_FILE([$with_sysio/lib/libsysio.a],[],[
			AC_MSG_ERROR([A complete (built) external libsysio was not found.])
		])
		SYSIO=$with_sysio
		with_sysio="yes"
		;;
esac

# We have to configure even if we don't build here for make dist to work
AC_CONFIG_SUBDIRS(libsysio)
])

#
# LB_PATH_LUSTREIOKIT
#
# Handle internal/external lustre-iokit
#
AC_DEFUN([LB_PATH_LUSTREIOKIT],
[AC_ARG_WITH([],
	AC_HELP_STRING([--with-lustre-iokit=path],
			[set path to lustre-iokit source (default is included lustre-iokit)]),
	[],[
			with_lustre_iokit='yes'
	])
AC_MSG_CHECKING([location of lustre-iokit])
enable_lustre_iokit="$with_lustre_iokit"
case x$with_lustre_iokit in
	xyes)
		AC_MSG_RESULT([internal])
		LB_CHECK_FILE([$srcdir/lustre-iokit/ior-survey/ior-survey],[],[
			AC_MSG_ERROR([A complete internal lustre-iokit was not found.])
		])
		LUSTREIOKIT_SUBDIR="lustre-iokit"
		LUSTREIOKIT="$PWD/lustre-iokit"
		;;
	xno)
		AC_MSG_RESULT([disabled])
		;;
	*)
		AC_MSG_RESULT([$with_lustre_iokit])
		LB_CHECK_FILE([$with_lustre_iokit/ior-survey/ior_survey],[],[
			AC_MSG_ERROR([A complete (built) external lustre-iokit was not found.])
		])
		LUSTREIOKIT="$with_lustre_iokit"
		with_lustre_iokit="yes"
		;;
esac
AC_SUBST(LUSTREIOKIT_SUBDIR)
# We have to configure even if we don't build here for make dist to work
AC_CONFIG_SUBDIRS(lustre-iokit)
])

#
# LB_PATH_LDISKFS
#
# Handle internal/external ldiskfs
#
AC_DEFUN([LB_PATH_LDISKFS],
[AC_ARG_WITH([ldiskfs],
	AC_HELP_STRING([--with-ldiskfs=path],
			[set path to ldiskfs source (default is included ldiskfs)]),
	[],[
		if test x$linux25$enable_server = xyesyes ; then
			with_ldiskfs=yes
		else
			with_ldiskfs=no
		fi
	])
AC_MSG_CHECKING([location of ldiskfs])
case x$with_ldiskfs in
	xyes)
		AC_MSG_RESULT([internal])
		LB_CHECK_FILE([$srcdir/ldiskfs/lustre-ldiskfs.spec.in],[],[
			AC_MSG_ERROR([A complete internal ldiskfs was not found.])
		])
		LDISKFS_SUBDIR="ldiskfs"
		LDISKFS_DIR="$PWD/ldiskfs"
		;;
	xno)
		AC_MSG_RESULT([disabled])
		;;
	*)
		AC_MSG_RESULT([$with_ldiskfs])
		LB_CHECK_FILE([$with_ldiskfs/ldiskfs/linux/ldiskfs_fs.h],[],[
			AC_MSG_ERROR([A complete (built) external ldiskfs was not found.])
		])
		LDISKFS_DIR=$with_ldiskfs
		;;
esac
AC_SUBST(LDISKFS_DIR)
AC_SUBST(LDISKFS_SUBDIR)
AM_CONDITIONAL(LDISKFS_ENABLED, test x$with_ldiskfs != xno)

if test x$enable_ext4 = xyes ; then
	AC_DEFINE(HAVE_EXT4_LDISKFS, 1, [build ext4 based ldiskfs])
fi

# We have to configure even if we don't build here for make dist to work
AC_CONFIG_SUBDIRS(ldiskfs)
])

# Define no libcfs by default.
AC_DEFUN([LB_LIBCFS_DIR],
[
case x$libcfs_is_module in
	xyes)
          LIBCFS_INCLUDE_DIR="libcfs/include"
          LIBCFS_SUBDIR="libcfs"
          ;;
        x*)
          LIBCFS_INCLUDE_DIR="lnet/include"
          LIBCFS_SUBDIR=""
          ;;
esac
AC_SUBST(LIBCFS_SUBDIR)
AC_SUBST(LIBCFS_INCLUDE_DIR)
])

#
# LB_DEFINE_LDISKFS_OPTIONS
#
# Enable config options related to ldiskfs.  These are used both by ldiskfs
# and lvfs (which includes ldiskfs headers.)
#
AC_DEFUN([LB_DEFINE_LDISKFS_OPTIONS],
[
	AC_DEFINE(CONFIG_LDISKFS_FS_MODULE, 1, [build ldiskfs as a module])
	AC_DEFINE(CONFIG_LDISKFS_FS_XATTR, 1, [enable extended attributes for ldiskfs])
	AC_DEFINE(CONFIG_LDISKFS_FS_POSIX_ACL, 1, [enable posix acls for ldiskfs])
	AC_DEFINE(CONFIG_LDISKFS_FS_SECURITY, 1, [enable fs security for ldiskfs])
	AC_DEFINE(CONFIG_LDISKFSDEV_FS_POSIX_ACL, 1, [enable posix acls for ldiskfs])
	AC_DEFINE(CONFIG_LDISKFSDEV_FS_XATTR, 1, [enable extented attributes for ldiskfs])
	AC_DEFINE(CONFIG_LDISKFSDEV_FS_SECURITY, 1, [enable fs security for ldiskfs])
	AC_DEFINE(CONFIG_LDISKFS_FS_NFS4ACL, 1, [enable fs security for ldiskfs])

])

#
# LB_DEFINE_E2FSPROGS_NAMES
#
# Enable the use of alternate naming of ldiskfs-enabled e2fsprogs package.
#
AC_DEFUN([LB_DEFINE_E2FSPROGS_NAMES],
[AC_ARG_WITH([ldiskfsprogs],
        AC_HELP_STRING([--with-ldiskfsprogs],
                       [use alternate names for ldiskfs-enabled e2fsprogs]),
	[],[withval='no'])

if test x$withval = xyes ; then
	AC_DEFINE(HAVE_LDISKFSPROGS, 1, [enable use of ldiskfsprogs package])
	E2FSPROGS="ldiskfsprogs"
	MKE2FS="mkfs.ldiskfs"
	DEBUGFS="debug.ldiskfs"
	TUNE2FS="tune.ldiskfs"
	E2LABEL="label.ldiskfs"
	DUMPE2FS="dump.ldiskfs"
	E2FSCK="fsck.ldiskfs"
	AC_MSG_RESULT([enabled])
else
	E2FSPROGS="e2fsprogs"
	MKE2FS="mke2fs"
	DEBUGFS="debugfs"
	TUNE2FS="tune2fs"
	E2LABEL="e2label"
	DUMPE2FS="dumpe2fs"
	E2FSCK="e2fsck"
	AC_MSG_RESULT([disabled])
fi
	AC_DEFINE_UNQUOTED(E2FSPROGS, "$E2FSPROGS", [name of ldiskfs e2fsprogs package])
	AC_DEFINE_UNQUOTED(MKE2FS, "$MKE2FS", [name of ldiskfs mkfs program])
	AC_DEFINE_UNQUOTED(DEBUGFS, "$DEBUGFS", [name of ldiskfs debug program])
	AC_DEFINE_UNQUOTED(TUNE2FS, "$TUNE2FS", [name of ldiskfs tune program])
	AC_DEFINE_UNQUOTED(E2LABEL, "$E2LABEL", [name of ldiskfs label program])
	AC_DEFINE_UNQUOTED(DUMPE2FS,"$DUMPE2FS", [name of ldiskfs dump program])
	AC_DEFINE_UNQUOTED(E2FSCK, "$E2FSCK", [name of ldiskfs fsck program])
])

#
# LB_DEFINE_E2FSPROGS_NAMES
#
# Enable the use of alternate naming of ldiskfs-enabled e2fsprogs package.
#
AC_DEFUN([LB_DEFINE_E2FSPROGS_NAMES],
[AC_ARG_WITH([ldiskfsprogs],
        AC_HELP_STRING([--with-ldiskfsprogs],
                       [use alternate names for ldiskfs-enabled e2fsprogs]),
	[],[withval='no'])

if test x$withval = xyes ; then
	AC_DEFINE(HAVE_LDISKFSPROGS, 1, [enable use of ldiskfsprogs package])
	E2FSPROGS="ldiskfsprogs"
	MKE2FS="mkfs.ldiskfs"
	DEBUGFS="debug.ldiskfs"
	TUNE2FS="tune.ldiskfs"
	E2LABEL="label.ldiskfs"
	DUMPE2FS="dump.ldiskfs"
	E2FSCK="fsck.ldiskfs"
	AC_MSG_RESULT([enabled])
else
	E2FSPROGS="e2fsprogs"
	MKE2FS="mke2fs"
	DEBUGFS="debugfs"
	TUNE2FS="tune2fs"
	E2LABEL="e2label"
	DUMPE2FS="dumpe2fs"
	E2FSCK="e2fsck"
	AC_MSG_RESULT([disabled])
fi
	AC_DEFINE_UNQUOTED(E2FSPROGS, "$E2FSPROGS", [name of ldiskfs e2fsprogs package])
	AC_DEFINE_UNQUOTED(MKE2FS, "$MKE2FS", [name of ldiskfs mkfs program])
	AC_DEFINE_UNQUOTED(DEBUGFS, "$DEBUGFS", [name of ldiskfs debug program])
	AC_DEFINE_UNQUOTED(TUNE2FS, "$TUNE2FS", [name of ldiskfs tune program])
	AC_DEFINE_UNQUOTED(E2LABEL, "$E2LABEL", [name of ldiskfs label program])
	AC_DEFINE_UNQUOTED(DUMPE2FS,"$DUMPE2FS", [name of ldiskfs dump program])
	AC_DEFINE_UNQUOTED(E2FSCK, "$E2FSCK", [name of ldiskfs fsck program])
])

#
# LB_DEFINE_E2FSPROGS_NAMES
#
# Enable the use of alternate naming of ldiskfs-enabled e2fsprogs package.
#
AC_DEFUN([LB_DEFINE_E2FSPROGS_NAMES],
[AC_ARG_WITH([ldiskfsprogs],
        AC_HELP_STRING([--with-ldiskfsprogs],
                       [use alternate names for ldiskfs-enabled e2fsprogs]),
	[],[withval='no'])

if test x$withval = xyes ; then
	AC_DEFINE(HAVE_LDISKFSPROGS, 1, [enable use of ldiskfsprogs package])
	E2FSPROGS="ldiskfsprogs"
	MKE2FS="mkfs.ldiskfs"
	DEBUGFS="debug.ldiskfs"
	TUNE2FS="tune.ldiskfs"
	E2LABEL="label.ldiskfs"
	DUMPE2FS="dump.ldiskfs"
	E2FSCK="fsck.ldiskfs"
	AC_MSG_RESULT([enabled])
else
	E2FSPROGS="e2fsprogs"
	MKE2FS="mke2fs"
	DEBUGFS="debugfs"
	TUNE2FS="tune2fs"
	E2LABEL="e2label"
	DUMPE2FS="dumpe2fs"
	E2FSCK="e2fsck"
	AC_MSG_RESULT([disabled])
fi
	AC_DEFINE_UNQUOTED(E2FSPROGS, "$E2FSPROGS", [name of ldiskfs e2fsprogs package])
	AC_DEFINE_UNQUOTED(MKE2FS, "$MKE2FS", [name of ldiskfs mkfs program])
	AC_DEFINE_UNQUOTED(DEBUGFS, "$DEBUGFS", [name of ldiskfs debug program])
	AC_DEFINE_UNQUOTED(TUNE2FS, "$TUNE2FS", [name of ldiskfs tune program])
	AC_DEFINE_UNQUOTED(E2LABEL, "$E2LABEL", [name of ldiskfs label program])
	AC_DEFINE_UNQUOTED(DUMPE2FS,"$DUMPE2FS", [name of ldiskfs dump program])
	AC_DEFINE_UNQUOTED(E2FSCK, "$E2FSCK", [name of ldiskfs fsck program])
])

#
# LB_CONFIG_CRAY_XT3
#
# Enable Cray XT3 features
#
AC_DEFUN([LB_CONFIG_CRAY_XT3],
[AC_MSG_CHECKING([whether to build Cray XT3 features])
AC_ARG_ENABLE([cray_xt3],
	AC_HELP_STRING([--enable-cray-xt3],
			[enable building of Cray XT3 features]),
	[enable_cray_xt3='yes'],[enable_cray_xt3='no'])
AC_MSG_RESULT([$enable_cray_xt3])
if test x$enable_cray_xt3 != xno; then
        AC_DEFINE(CRAY_XT3, 1, Enable Cray XT3 Features)
fi
])

#
# LB_CONFIG_BGL
#
# Enable BGL features
#
AC_DEFUN([LB_CONFIG_BGL],
[AC_MSG_CHECKING([whether to build BGL features])
AC_ARG_ENABLE([bgl],
	AC_HELP_STRING([--enable-bgl],
			[enable building of BGL features]),
	[enable_bgl='yes'],[enable_bgl='no'])
AC_MSG_RESULT([$enable_bgl])
if test x$enable_bgl != xno; then
        AC_DEFINE(HAVE_BGL_SUPPORT, 1, Enable BGL Features)
        enable_doc='no'
        enable_tests='no'
        enable_server='no'
        enable_liblustre='no'
        enable_libreadline='no'
fi
])

#
# Support for --enable-uoss
#
AC_DEFUN([LB_UOSS],
[AC_MSG_CHECKING([whether to enable uoss])
AC_ARG_ENABLE([uoss],
	AC_HELP_STRING([--enable-uoss],
			[enable userspace OSS]),
	[enable_uoss='yes'],[enable_uoss='no'])
AC_MSG_RESULT([$enable_uoss])
if test x$enable_uoss = xyes; then
	AC_DEFINE(UOSS_SUPPORT, 1, Enable user-level OSS)
	AC_DEFINE(LUSTRE_ULEVEL_MT, 1, Multi-threaded user-level lustre port)
	enable_uoss='yes'
	enable_ulevel_mt='yes'
	enable_modules='no'
	enable_client='no'
	enable_tests='no'
	enable_liblustre='no'
	with_ldiskfs='no'
fi
AC_SUBST(enable_uoss)
])

#
# Support for --enable-posix-osd
#
AC_DEFUN([LB_POSIX_OSD],
[AC_MSG_CHECKING([whether to enable posix osd])
AC_ARG_ENABLE([posix-osd],
	AC_HELP_STRING([--enable-posix-osd],
			[enable using of posix osd]),
	[enable_posix_osd='yes'],[enable_posix_osd='no'])
AC_MSG_RESULT([$enable_posix_osd])
if test x$enable_uoss = xyes -a x$enable_posix_osd = xyes ; then
	AC_DEFINE(POSIX_OSD, 1, Enable POSIX OSD)
	posix_osd='yes'
fi
AM_CONDITIONAL(POSIX_OSD_ENABLED, test x$posix_osd = xyes)
])

#
# LB_PATH_DMU
#
AC_DEFUN([LB_PATH_DMU],
[AC_ARG_ENABLE([dmu],
	AC_HELP_STRING([--enable-dmu],
	               [enable the DMU backend]),
	[],[with_dmu='default'])
AC_MSG_CHECKING([whether to enable DMU])
case x$with_dmu in
	xyes)
		dmu_osd='yes'
		;;
	xno)
		dmu_osd='no'
		;;
	xdefault)
		if test x$enable_uoss = xyes -a x$posix_osd != xyes; then
			# Enable the DMU if we're configuring a userspace server
			dmu_osd='yes'
		else
			# Enable the DMU by default on the b_hd_kdmu branch
			if test -d $PWD/zfs -a x$linux25$enable_server = xyesyes; then
				dmu_osd='yes'
			else
				dmu_osd='no'
			fi
		fi
		;;
	*)
		dmu_osd='yes'
		;;
esac
AC_MSG_RESULT([$dmu_osd])
if test x$dmu_osd = xyes; then
	AC_DEFINE(DMU_OSD, 1, Enable DMU OSD)
	if test x$enable_uoss = xyes; then
		# Userspace DMU
		DMU_SRC="$PWD/lustre/zfs-lustre"
		AC_SUBST(DMU_SRC)
		LB_CHECK_FILE([$DMU_SRC/src/.patched],[],[
			AC_MSG_ERROR([A complete (patched) DMU tree was not found.])
		])
		AC_CONFIG_SUBDIRS(lustre/zfs-lustre)
	else
		# Kernel DMU
		SPL_DIR="$PWD/spl"
		ZFS_DIR="$PWD/zfs"
		AC_SUBST(SPL_DIR)
		AC_SUBST(ZFS_DIR)

		AC_SUBST(spl_src)

		LB_CHECK_FILE([$SPL_DIR/module/spl/spl-generic.c],[],[
			AC_MSG_ERROR([A complete SPL tree was not found in $SPL_DIR.])
		])

		LB_CHECK_FILE([$ZFS_DIR/module/zfs/dmu.c],[],[
			AC_MSG_ERROR([A complete kernel DMU tree was not found in $ZFS_DIR.])
		])

		AC_CONFIG_SUBDIRS(spl)
		ac_configure_args="$ac_configure_args --with-spl=$SPL_DIR"
		AC_CONFIG_SUBDIRS(zfs)
	fi
fi
AM_CONDITIONAL(DMU_OSD_ENABLED, test x$dmu_osd = xyes)
AM_CONDITIONAL(KDMU, test x$dmu_osd$enable_uoss = xyesno)
])

#
# LB_PATH_SNMP
#
# check for in-tree snmp support
#
AC_DEFUN([LB_PATH_SNMP],
[LB_CHECK_FILE([$srcdir/snmp/lustre-snmp.c],[SNMP_DIST_SUBDIR="snmp"])
AC_SUBST(SNMP_DIST_SUBDIR)
AC_SUBST(SNMP_SUBDIR)
])

#
# LB_CONFIG_MODULES
#
# Build kernel modules?
#
AC_DEFUN([LB_CONFIG_MODULES],
[AC_MSG_CHECKING([whether to build kernel modules])
AC_ARG_ENABLE([modules],
	AC_HELP_STRING([--disable-modules],
			[disable building of Lustre kernel modules]),
	[],[
		LC_TARGET_SUPPORTED([
			enable_modules='yes'
		],[
			enable_modules='no'
		])
	])
AC_MSG_RESULT([$enable_modules ($target_os)])

if test x$enable_modules = xyes ; then
	case $target_os in
		linux*)
			LB_PROG_LINUX
			LIBCFS_PROG_LINUX
			LN_PROG_LINUX
			LC_PROG_LINUX
			;;
		darwin*)
			LB_PROG_DARWIN
			LIBCFS_PROG_DARWIN
			;;
		*)
			# This is strange - Lustre supports a target we don't
			AC_MSG_ERROR([Modules are not supported on $target_os])
			;;
	esac
fi
])

#
# LB_CONFIG_UTILS
#
# Build utils?
#
AC_DEFUN([LB_CONFIG_UTILS],
[AC_MSG_CHECKING([whether to build utilities])
AC_ARG_ENABLE([utils],
	AC_HELP_STRING([--disable-utils],
			[disable building of Lustre utility programs]),
	[],[enable_utils='yes'])
AC_MSG_RESULT([$enable_utils])
if test x$enable_utils = xyes ; then 
	LB_CONFIG_INIT_SCRIPTS
fi
])

#
# LB_CONFIG_TESTS
#
# Build tests?
#
AC_DEFUN([LB_CONFIG_TESTS],
[AC_MSG_CHECKING([whether to build Lustre tests])
AC_ARG_ENABLE([tests],
	AC_HELP_STRING([--disable-tests],
			[disable building of Lustre tests]),
	[],
	[
		enable_tests='yes'
	])
AC_MSG_RESULT([$enable_tests])
])

#
# LB_CONFIG_DOCS
#
# Build docs?
#
AC_DEFUN([LB_CONFIG_DOCS],
[AC_MSG_CHECKING([whether to build docs])
AC_ARG_ENABLE(doc,
	AC_HELP_STRING([--disable-doc],
			[skip creation of pdf documentation]),
	[
		if test x$enable_doc = xyes ; then
		    ENABLE_DOC=1	   
		else
		    ENABLE_DOC=0
		fi
	],[
		ENABLE_DOC=0
		enable_doc='no'
	])
AC_MSG_RESULT([$enable_doc])
AC_SUBST(ENABLE_DOC)
])

#
# LB_CONFIG_INIT_SCRIPTS
#
# our init scripts only work on red hat linux
#
AC_DEFUN([LB_CONFIG_INIT_SCRIPTS],
[ENABLE_INIT_SCRIPTS=0
if test x$enable_utils = xyes ; then
        AC_MSG_CHECKING([whether to install init scripts])
        # our scripts only work on red hat systems
        if test -f /etc/init.d/functions -a -f /etc/sysconfig/network ; then
                ENABLE_INIT_SCRIPTS=1
                AC_MSG_RESULT([yes])
        else
                AC_MSG_RESULT([no])
        fi
fi
AC_SUBST(ENABLE_INIT_SCRIPTS)
])

#
# LB_CONFIG_HEADERS
#
# add -include config.h
#
AC_DEFUN([LB_CONFIG_HEADERS],
[AC_CONFIG_HEADERS([config.h])
CPPFLAGS="-include $PWD/config.h $CPPFLAGS"
EXTRA_KCFLAGS="-include $PWD/config.h $EXTRA_KCFLAGS"
AC_SUBST(EXTRA_KCFLAGS)
])

#
# LB_INCLUDE_RULES
#
# defines for including the toplevel Rules
#
AC_DEFUN([LB_INCLUDE_RULES],
[INCLUDE_RULES="include $PWD/Rules"
AC_SUBST(INCLUDE_RULES)
])

#
# LB_PATH_DEFAULTS
#
# 'fixup' default paths
#
AC_DEFUN([LB_PATH_DEFAULTS],
[# directories for binaries
AC_PREFIX_DEFAULT([/usr])

sysconfdir='/etc'
AC_SUBST(sysconfdir)

# Directories for documentation and demos.
docdir='${datadir}/doc/$(PACKAGE)'
AC_SUBST(docdir)

LIBCFS_PATH_DEFAULTS
LN_PATH_DEFAULTS
LC_PATH_DEFAULTS

])

#
# LB_PROG_CC
#
# checks on the C compiler
#
AC_DEFUN([LB_PROG_CC],
[AC_PROG_RANLIB
AC_MSG_CHECKING([for buggy compiler])
CC_VERSION=`$CC -v 2>&1 | grep "^gcc version"`
bad_cc() {
	AC_MSG_RESULT([buggy compiler found!])
	echo
	echo "   '$CC_VERSION'"
	echo "  has been known to generate bad code, "
	echo "  please get an updated compiler."
	AC_MSG_ERROR([sorry])
}
case "$CC_VERSION" in
	"gcc version 2.95"*)
		bad_cc
		;;
	# ost_pack_niobuf putting 64bit NTOH temporaries on the stack
	# without "sub    $0xc,%esp" to protect the stack from being
	# stomped on by interrupts (bug 606)
	"gcc version 2.96 20000731 (Red Hat Linux 7.1 2.96-98)")
		bad_cc
		;;
	# mandrake's similar sub 0xc compiler bug
	# http://marc.theaimsgroup.com/?l=linux-kernel&m=104748366226348&w=2
	"gcc version 2.96 20000731 (Mandrake Linux 8.1 2.96-0.62mdk)")
		bad_cc
		;;
	*)
		AC_MSG_RESULT([no known problems])
		;;
esac

# ---------  unsigned long long sane? -------
AC_CHECK_SIZEOF(unsigned long long, 0)
echo "---> size SIZEOF $SIZEOF_unsigned_long_long"
echo "---> size SIZEOF $ac_cv_sizeof_unsigned_long_long"
if test $ac_cv_sizeof_unsigned_long_long != 8 ; then
        AC_MSG_ERROR([** we assume that sizeof(long long) == 8.  Tell phil@clusterfs.com])
fi

if test $target_cpu == "powerpc64"; then
	AC_MSG_WARN([set compiler with -m64])
	CFLAGS="$CFLAGS -m64"
	CC="$CC -m64"
fi

CPPFLAGS="-I$PWD/$LIBCFS_INCLUDE_DIR -I$PWD/lnet/include -I$PWD/lustre/include $CPPFLAGS"

LLCPPFLAGS="-D__arch_lib__ -D_LARGEFILE64_SOURCE=1"
AC_SUBST(LLCPPFLAGS)

# Add _GNU_SOURCE for strnlen on linux
LLCFLAGS="-g -Wall -fPIC -D_GNU_SOURCE"
AC_SUBST(LLCFLAGS)

# everyone builds against lnet and lustre
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -g -I$PWD/$LIBCFS_INCLUDE_DIR -I$PWD/lnet/include -I$PWD/lustre/include"
AC_SUBST(EXTRA_KCFLAGS)
])

#
# LB_CONTITIONALS
#
# AM_CONDITIONAL instances for everything
# (so that portals/lustre can disable some if needed)
AC_DEFUN([LB_CONDITIONALS],
[AM_CONDITIONAL(MODULES, test x$enable_modules = xyes)
AM_CONDITIONAL(UTILS, test x$enable_utils = xyes)
AM_CONDITIONAL(TESTS, test x$enable_tests = xyes)
AM_CONDITIONAL(DOC, test x$ENABLE_DOC = x1)
AM_CONDITIONAL(INIT_SCRIPTS, test x$ENABLE_INIT_SCRIPTS = "x1")
AM_CONDITIONAL(LINUX, test x$lb_target_os = "xlinux")
AM_CONDITIONAL(DARWIN, test x$lb_target_os = "xdarwin")
AM_CONDITIONAL(CRAY_XT3, test x$enable_cray_xt3 = "xyes")
AM_CONDITIONAL(SUNOS, test x$lb_target_os = "xSunOS")

# this lets lustre cancel libsysio, per-branch or if liblustre is
# disabled
if test "x$LIBSYSIO_SUBDIR" = xlibsysio ; then
	if test "x$with_sysio" != xyes ; then
		SYSIO=""
		LIBSYSIO_SUBDIR=""
	fi
fi
AC_SUBST(LIBSYSIO_SUBDIR)
AC_SUBST(SYSIO)

LB_LINUX_CONDITIONALS
LB_DARWIN_CONDITIONALS

LIBCFS_CONDITIONALS
LN_CONDITIONALS
LC_CONDITIONALS
])

#
# LB_CONFIG_FILES
#
# build-specific config files
#
AC_DEFUN([LB_CONFIG_FILES],
[
AC_CONFIG_FILES(
[Makefile
autoMakefile
]
[Rules:build/Rules.in]
AC_PACKAGE_TARNAME[.spec]
)
])

#
# LB_CONFIGURE
#
# main configure steps
#
AC_DEFUN([LB_CONFIGURE],
[LB_CANONICAL_SYSTEM

LB_LIBCFS_DIR

LB_INCLUDE_RULES

LB_CONFIG_CRAY_XT3
LB_CONFIG_BGL
LB_PATH_DEFAULTS

LB_PROG_CC

LB_UOSS
LB_POSIX_OSD

LB_CONFIG_DOCS
LB_CONFIG_UTILS
LB_CONFIG_TESTS
LC_CONFIG_CLIENT_SERVER

# two macros for cmd3 
m4_ifdef([LC_CONFIG_SPLIT], [LC_CONFIG_SPLIT])
LN_CONFIG_CDEBUG
LC_QUOTA

LB_CONFIG_MODULES

LN_CONFIG_USERSPACE

LB_PATH_DMU
LB_PATH_LIBSYSIO
LB_PATH_SNMP
LB_PATH_LDISKFS
LB_PATH_LUSTREIOKIT

LB_DEFINE_E2FSPROGS_NAMES

LB_DEFINE_E2FSPROGS_NAMES

LB_DEFINE_E2FSPROGS_NAMES

LC_CONFIG_LIBLUSTRE
LIBCFS_CONFIGURE
LN_CONFIGURE

LC_CONFIGURE

if test "$SNMP_DIST_SUBDIR" ; then
	LS_CONFIGURE
fi


LB_CONDITIONALS
LB_CONFIG_HEADERS

LIBCFS_CONFIG_FILES
LB_CONFIG_FILES
LN_CONFIG_FILES
LC_CONFIG_FILES
if test "$SNMP_DIST_SUBDIR" ; then
	LS_CONFIG_FILES
fi

AC_SUBST(ac_configure_args)

MOSTLYCLEANFILES='.*.cmd .*.flags *.o *.ko *.mod.c .depend .*.1.* Modules.symvers Module.symvers'
AC_SUBST(MOSTLYCLEANFILES)

AC_OUTPUT

cat <<_ACEOF

CC:            $CC
LD:            $LD
CPPFLAGS:      $CPPFLAGS
LLCPPFLAGS:    $LLCPPFLAGS
CFLAGS:        $CFLAGS
EXTRA_KCFLAGS: $EXTRA_KCFLAGS
LLCFLAGS:      $LLCFLAGS

Type 'make' to build Lustre.
_ACEOF
])

#* -*- mode: c; c-basic-offset: 8; indent-tabs-mode: nil; -*-
#* vim:expandtab:shiftwidth=8:tabstop=8:
#
# LC_CONFIG_SRCDIR
#
# Wrapper for AC_CONFIG_SUBDIR
#
AC_DEFUN([LC_CONFIG_SRCDIR],
[AC_CONFIG_SRCDIR([lustre/obdclass/obdo.c])
])

#
# LC_PATH_DEFAULTS
#
# lustre specific paths
#
AC_DEFUN([LC_PATH_DEFAULTS],
[# ptlrpc kernel build requires this
LUSTRE="$PWD/lustre"
AC_SUBST(LUSTRE)

# mount.lustre
rootsbindir='/sbin'
AC_SUBST(rootsbindir)

demodir='$(docdir)/demo'
AC_SUBST(demodir)

pkgexampledir='${pkgdatadir}/examples'
AC_SUBST(pkgexampledir)
])

#
# LC_TARGET_SUPPORTED
#
# is the target os supported?
#
AC_DEFUN([LC_TARGET_SUPPORTED],
[case $target_os in
	linux* | darwin*)
$1
		;;
	*)
$2
		;;
esac
])

#
# LC_CONFIG_EXT3
#
# that ext3 is enabled in the kernel
#
AC_DEFUN([LC_CONFIG_EXT3],
[LB_LINUX_CONFIG([EXT3_FS],[],[
	LB_LINUX_CONFIG([EXT3_FS_MODULE],[],[$2])
])
LB_LINUX_CONFIG([EXT3_FS_XATTR],[$1],[$3])
])

#
# LC_FSHOOKS
#
# If we have (and can build) fshooks.h
#
AC_DEFUN([LC_FSHOOKS],
[LB_CHECK_FILE([$LINUX/include/linux/fshooks.h],[
	AC_MSG_CHECKING([if fshooks.h can be compiled])
	LB_LINUX_TRY_COMPILE([
		#include <linux/fshooks.h>
	],[],[
		AC_MSG_RESULT([yes])
	],[
		AC_MSG_RESULT([no])
		AC_MSG_WARN([You might have better luck with gcc 3.3.x.])
		AC_MSG_WARN([You can set CC=gcc33 before running configure.])
		AC_MSG_ERROR([Your compiler cannot build fshooks.h.])
	])
$1
],[
$2
])
])

#

#
# LC_FUNC_RELEASEPAGE_WITH_GFP
#
# if ->releasepage() takes a gfp_t arg in 2.6.9
# This kernel defines gfp_t (HAS_GFP_T) but doesn't use it for this function,
# while others either don't have gfp_t or pass gfp_t as the parameter.
#
AC_DEFUN([LC_FUNC_RELEASEPAGE_WITH_GFP],
[AC_MSG_CHECKING([if releasepage has a gfp_t parameter])
RELEASEPAGE_WITH_GFP="`grep -c 'releasepage.*gfp_t' $LINUX/include/linux/fs.h`"
if test "$RELEASEPAGE_WITH_GFP" != 0 ; then
	AC_DEFINE(HAVE_RELEASEPAGE_WITH_GFP, 1,
                  [releasepage with gfp_t parameter])
	AC_MSG_RESULT([yes])
else
	AC_MSG_RESULT([no])
fi
])

# LC_FUNC_FILEMAP_FDATASYNC
#
# if filemap_fdatasync() exists
#
AC_DEFUN([LC_FUNC_FILEMAP_FDATAWRITE],
[AC_MSG_CHECKING([whether filemap_fdatawrite() is defined])
LB_LINUX_TRY_COMPILE([
	#include <linux/fs.h>
],[
	int (*foo)(struct address_space *)= filemap_fdatawrite;
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_FILEMAP_FDATAWRITE, 1, [filemap_fdatawrite() found])
],[
	AC_MSG_RESULT([no])
])
])

#
# LC_HEADER_MM_INLINE
#
# RHEL kernels define page_count in mm_inline.h
#
AC_DEFUN([LC_HEADER_MM_INLINE],
[AC_MSG_CHECKING([if kernel has mm_inline.h header])
LB_LINUX_TRY_COMPILE([
	#include <linux/mm_inline.h>
],[
	#ifndef page_count
	#error mm_inline.h does not define page_count
	#endif
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_MM_INLINE, 1, [mm_inline found])
],[
	AC_MSG_RESULT([no])
])
])

#
# LC_STRUCT_INODE
#
# if inode->i_alloc_sem exists
#
AC_DEFUN([LC_STRUCT_INODE],
[AC_MSG_CHECKING([if struct inode has i_alloc_sem])
LB_LINUX_TRY_COMPILE([
	#include <linux/fs.h>
	#include <linux/version.h>
],[
	struct inode i;
	return (char *)&i.i_alloc_sem - (char *)&i;
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_I_ALLOC_SEM, 1, [struct inode has i_alloc_sem])
],[
	AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_REGISTER_CACHE
#
# if register_cache() is defined by kernel
# 
# There are two ways to shrink one customized cache in linux kernels. For the
# kernels are prior than 2.6.5(?), register_cache() is used, and for latest 
# kernels, set_shrinker() is used instead.
#
AC_DEFUN([LC_FUNC_REGISTER_CACHE],
[AC_MSG_CHECKING([if kernel defines cache pressure hook])
LB_LINUX_TRY_COMPILE([
	#include <linux/mm.h>
],[
	shrinker_t shrinker;

	set_shrinker(1, shrinker);
],[
	AC_MSG_RESULT([set_shrinker])
	AC_DEFINE(HAVE_SHRINKER_CACHE, 1, [shrinker_cache found])
	AC_DEFINE(HAVE_CACHE_RETURN_INT, 1, [shrinkers should return int])
],[
	LB_LINUX_TRY_COMPILE([
		#include <linux/list.h>
		#include <linux/cache_def.h>
	],[
		struct cache_definition cache;
	],[
		AC_MSG_RESULT([register_cache])
		AC_DEFINE(HAVE_REGISTER_CACHE, 1, [register_cache found])
		AC_MSG_CHECKING([if kernel expects return from cache shrink ])
		tmp_flags="$EXTRA_KCFLAGS"
		EXTRA_KCFLAGS="-Werror"
		LB_LINUX_TRY_COMPILE([
			#include <linux/list.h>
			#include <linux/cache_def.h>
		],[
			struct cache_definition c;
			c.shrinker = (int (*)(int, unsigned int))1;
		],[
			AC_DEFINE(HAVE_CACHE_RETURN_INT, 1,
				  [kernel expects return from shrink_cache])
			AC_MSG_RESULT(yes)
		],[
			AC_MSG_RESULT(no)
		])
		EXTRA_KCFLAGS="$tmp_flags"
	],[
		AC_MSG_RESULT([no])
	])
])
])

#
# LC_FUNC_GRAB_CACHE_PAGE_NOWAIT_GFP
#
# check for our patched grab_cache_page_nowait_gfp() function
#
AC_DEFUN([LC_FUNC_GRAB_CACHE_PAGE_NOWAIT_GFP],
[AC_MSG_CHECKING([if kernel defines grab_cache_page_nowait_gfp()])
HAVE_GCPN_GFP="`grep -c 'grab_cache_page_nowait_gfp' $LINUX/include/linux/pagemap.h`"
if test "$HAVE_GCPN_GFP" != 0 ; then
	AC_DEFINE(HAVE_GRAB_CACHE_PAGE_NOWAIT_GFP, 1,
		[kernel has grab_cache_page_nowait_gfp()])
	AC_MSG_RESULT(yes)
else
	AC_MSG_RESULT(no)
fi
])

#
# LC_FUNC_DEV_SET_RDONLY
#
# check for the old-style dev_set_rdonly which took an extra "devno" param
# and can only set a single device to discard writes at one time
#
AC_DEFUN([LC_FUNC_DEV_SET_RDONLY],
[AC_MSG_CHECKING([if kernel has new dev_set_rdonly])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        #ifndef HAVE_CLEAR_RDONLY_ON_PUT
        #error needs to be patched by lustre kernel patches from Lustre version 1.4.3 or above.
        #endif
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_DEV_SET_RDONLY, 1, [kernel has new dev_set_rdonly])
],[
        AC_MSG_RESULT([no, Linux kernel source needs to be patches by lustre 
kernel patches from Lustre version 1.4.3 or above.])
])
])

#
# LC_CONFIG_BACKINGFS
#
# setup, check the backing filesystem
#
AC_DEFUN([LC_CONFIG_BACKINGFS],
[
BACKINGFS="ldiskfs"

if test x$with_ldiskfs = xno ; then
	BACKINGFS="ext3"

	if test x$enable_server = xyes ; then
		AC_MSG_ERROR([ldiskfs is required for 2.6-based servers.])
	fi

	# --- Check that ext3 and ext3 xattr are enabled in the kernel
	LC_CONFIG_EXT3([],[
		AC_MSG_ERROR([Lustre requires that ext3 is enabled in the kernel])
	],[
		AC_MSG_WARN([Lustre requires that extended attributes for ext3 are enabled in the kernel])
		AC_MSG_WARN([This build may fail.])
	])
else
	# ldiskfs is enabled
	LB_DEFINE_LDISKFS_OPTIONS
fi #ldiskfs

AC_MSG_CHECKING([which backing filesystem to use])
AC_MSG_RESULT([$BACKINGFS])
AC_SUBST(BACKINGFS)
])

#
# LC_CONFIG_PINGER
#
# the pinger is temporary, until we have the recovery node in place
#
AC_DEFUN([LC_CONFIG_PINGER],
[AC_MSG_CHECKING([whether to enable pinger support])
AC_ARG_ENABLE([pinger],
	AC_HELP_STRING([--disable-pinger],
			[disable recovery pinger support]),
	[],[enable_pinger='yes'])
AC_MSG_RESULT([$enable_pinger])
if test x$enable_pinger != xno ; then
  AC_DEFINE(ENABLE_PINGER, 1, Use the Pinger)
fi
])

#
# LC_CONFIG_CHECKSUM
#
# do checksum of bulk data between client and OST
#
AC_DEFUN([LC_CONFIG_CHECKSUM],
[AC_MSG_CHECKING([whether to enable data checksum support])
AC_ARG_ENABLE([checksum],
       AC_HELP_STRING([--disable-checksum],
                       [disable data checksum support]),
       [],[enable_checksum='yes'])
AC_MSG_RESULT([$enable_checksum])
if test x$enable_checksum != xno ; then
  AC_DEFINE(ENABLE_CHECKSUM, 1, do data checksums)
fi
])

#
# LC_CONFIG_HEALTH_CHECK_WRITE
#
# Turn on the actual write to the disk
#
AC_DEFUN([LC_CONFIG_HEALTH_CHECK_WRITE],
[AC_MSG_CHECKING([whether to enable a write with the health check])
AC_ARG_ENABLE([health-write],
        AC_HELP_STRING([--enable-health-write],
                        [enable disk writes when doing health check]),
        [],[enable_health_write='no'])
AC_MSG_RESULT([$enable_health_write])
if test x$enable_health_write == xyes ; then
  AC_DEFINE(USE_HEALTH_CHECK_WRITE, 1, Write when Checking Health)
fi
])

#
# LC_CONFIG_LIBLUSTRE_RECOVERY
#
AC_DEFUN([LC_CONFIG_LIBLUSTRE_RECOVERY],
[AC_MSG_CHECKING([whether to enable liblustre recovery support])
AC_ARG_ENABLE([liblustre-recovery],
	AC_HELP_STRING([--disable-liblustre-recovery],
			[disable liblustre recovery support]),
	[],[enable_liblustre_recovery='yes'])
AC_MSG_RESULT([$enable_liblustre_recovery])
if test x$enable_liblustre_recovery != xno ; then
  AC_DEFINE(ENABLE_LIBLUSTRE_RECOVERY, 1, Liblustre Can Recover)
fi
])

#
# LC_CONFIG_OBD_BUFFER_SIZE
#
# the maximum buffer size of lctl ioctls
#
AC_DEFUN([LC_CONFIG_OBD_BUFFER_SIZE],
[AC_MSG_CHECKING([maximum OBD ioctl size])
AC_ARG_WITH([obd-buffer-size],
	AC_HELP_STRING([--with-obd-buffer-size=[size]],
			[set lctl ioctl maximum bytes (default=8192)]),
	[
		OBD_BUFFER_SIZE=$with_obd_buffer_size
	],[
		OBD_BUFFER_SIZE=8192
	])
AC_MSG_RESULT([$OBD_BUFFER_SIZE bytes])
AC_DEFINE_UNQUOTED(OBD_MAX_IOCTL_BUFFER, $OBD_BUFFER_SIZE, [IOCTL Buffer Size])
])

#
# LC_STRUCT_STATFS
#
# AIX does not have statfs.f_namelen
#
AC_DEFUN([LC_STRUCT_STATFS],
[AC_MSG_CHECKING([if struct statfs has a f_namelen field])
LB_LINUX_TRY_COMPILE([
	#include <linux/vfs.h>
],[
	struct statfs sfs;
	sfs.f_namelen = 1;
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_STATFS_NAMELEN, 1, [struct statfs has a namelen field])
],[
	AC_MSG_RESULT([no])
])
])

#
# LC_READLINK_SSIZE_T
#
AC_DEFUN([LC_READLINK_SSIZE_T],
[AC_MSG_CHECKING([if readlink returns ssize_t])
AC_TRY_COMPILE([
	#include <unistd.h>
],[
	ssize_t readlink(const char *, char *, size_t);
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_POSIX_1003_READLINK, 1, [readlink returns ssize_t])
],[
	AC_MSG_RESULT([no])
])
])

AC_DEFUN([LC_FUNC_PAGE_MAPPED],
[AC_MSG_CHECKING([if kernel offers page_mapped])
LB_LINUX_TRY_COMPILE([
	#include <linux/mm.h>
],[
	page_mapped(NULL);
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_PAGE_MAPPED, 1, [page_mapped found])
],[
	AC_MSG_RESULT([no])
])
])

AC_DEFUN([LC_STRUCT_FILE_OPS_UNLOCKED_IOCTL],
[AC_MSG_CHECKING([if struct file_operations has an unlocked_ioctl field])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct file_operations fops;
        &fops.unlocked_ioctl;
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_UNLOCKED_IOCTL, 1, [struct file_operations has an unlock ed_ioctl field])
],[
        AC_MSG_RESULT([no])
])
])

AC_DEFUN([LC_FILEMAP_POPULATE],
[AC_MSG_CHECKING([for exported filemap_populate])
LB_LINUX_TRY_COMPILE([
        #include <asm/page.h>
        #include <linux/mm.h>
],[
	filemap_populate(NULL, 0, 0, __pgprot(0), 0, 0);
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_FILEMAP_POPULATE, 1, [Kernel exports filemap_populate])
],[
        AC_MSG_RESULT([no])
])
])

AC_DEFUN([LC_D_ADD_UNIQUE],
[AC_MSG_CHECKING([for d_add_unique])
LB_LINUX_TRY_COMPILE([
        #include <linux/dcache.h>
],[
       d_add_unique(NULL, NULL);
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_D_ADD_UNIQUE, 1, [Kernel has d_add_unique])
],[
        AC_MSG_RESULT([no])
])
])

AC_DEFUN([LC_BIT_SPINLOCK_H],
[LB_CHECK_FILE([$LINUX/include/linux/bit_spinlock.h],[
	AC_MSG_CHECKING([if bit_spinlock.h can be compiled])
	LB_LINUX_TRY_COMPILE([
		#include <asm/processor.h>
		#include <linux/spinlock.h>
		#include <linux/bit_spinlock.h>
	],[],[
		AC_MSG_RESULT([yes])
		AC_DEFINE(HAVE_BIT_SPINLOCK_H, 1, [Kernel has bit_spinlock.h])
	],[
		AC_MSG_RESULT([no])
	])
],
[])
])

#
# LC_POSIX_ACL_XATTR
#
# If we have xattr_acl.h 
#
AC_DEFUN([LC_XATTR_ACL],
[LB_CHECK_FILE([$LINUX/include/linux/xattr_acl.h],[
	AC_MSG_CHECKING([if xattr_acl.h can be compiled])
	LB_LINUX_TRY_COMPILE([
		#include <linux/xattr_acl.h>
	],[],[
		AC_MSG_RESULT([yes])
		AC_DEFINE(HAVE_XATTR_ACL, 1, [Kernel has xattr_acl])
	],[
		AC_MSG_RESULT([no])
	])
],
[])
])

#
# LC_LINUX_FIEMAP_H
#
# If we have fiemap.h
# after 2.6.27 use fiemap.h in include/linux
#
AC_DEFUN([LC_LINUX_FIEMAP_H],
[LB_CHECK_FILE([$LINUX/include/linux/fiemap.h],[
        AC_MSG_CHECKING([if fiemap.h can be compiled])
        LB_LINUX_TRY_COMPILE([
                #include <linux/fiemap.h>
        ],[],[
                AC_MSG_RESULT([yes])
                AC_DEFINE(HAVE_LINUX_FIEMAP_H, 1, [Kernel has fiemap.h])
        ],[
                AC_MSG_RESULT([no])
        ])
],
[])
])


AC_DEFUN([LC_STRUCT_INTENT_FILE],
[AC_MSG_CHECKING([if struct open_intent has a file field])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
        #include <linux/namei.h>
],[
        struct open_intent intent;
        &intent.file;
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_FILE_IN_STRUCT_INTENT, 1, [struct open_intent has a file field])
],[
        AC_MSG_RESULT([no])
])
])


AC_DEFUN([LC_POSIX_ACL_XATTR_H],
[LB_CHECK_FILE([$LINUX/include/linux/posix_acl_xattr.h],[
        AC_MSG_CHECKING([if linux/posix_acl_xattr.h can be compiled])
        LB_LINUX_TRY_COMPILE([
                #include <linux/posix_acl_xattr.h>
        ],[],[
                AC_MSG_RESULT([yes])
                AC_DEFINE(HAVE_LINUX_POSIX_ACL_XATTR_H, 1, [linux/posix_acl_xattr.h found])

        ],[
                AC_MSG_RESULT([no])
        ])
$1
],[
AC_MSG_RESULT([no])
])
])

#
# LC_EXPORT___IGET
# starting from 2.6.19 linux kernel exports __iget()
#
AC_DEFUN([LC_EXPORT___IGET],
[LB_CHECK_SYMBOL_EXPORT([__iget],
[fs/inode.c],[
        AC_DEFINE(HAVE_EXPORT___IGET, 1, [kernel exports __iget])
],[
])
])


AC_DEFUN([LC_LUSTRE_VERSION_H],
[LB_CHECK_FILE([$LINUX/include/linux/lustre_version.h],[
	rm -f "$LUSTRE/include/linux/lustre_version.h"
],[
	touch "$LUSTRE/include/linux/lustre_version.h"
	if test x$enable_server = xyes ; then
        	AC_MSG_WARN([Unpatched kernel detected.])
        	AC_MSG_WARN([Lustre servers cannot be built with an unpatched kernel;])
        	AC_MSG_WARN([disabling server build])
        	enable_server='no'
	fi
])
	if test x$enable_server = xyes ; then
		if test x$RHEL_KERNEL = xyes -a x$LINUXRELEASE != x${LINUXRELEASE##2.6.9} ; then
        		AC_MSG_WARN([Lustre server has been disabled with rhel4 kernel;])
        		AC_MSG_WARN([disabling server build])
        		enable_server='no'
		fi
		if test x$SUSE_KERNEL = xyes -a x$LINUXRELEASE != x${LINUXRELEASE##2.6.5} ; then
        		AC_MSG_WARN([Lustre server has been disabled with sles9 kernel;])
        		AC_MSG_WARN([disabling server build])
			enable_server='no'
		fi
	fi
])

#
# check for FS_RENAME_DOES_D_MOVE flag
#
AC_DEFUN([LC_FS_RENAME_DOES_D_MOVE],
[AC_MSG_CHECKING([if kernel has FS_RENAME_DOES_D_MOVE flag])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        int v = FS_RENAME_DOES_D_MOVE;
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_FS_RENAME_DOES_D_MOVE, 1, [kernel has FS_RENAME_DOES_D_MOVE flag])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_MS_FLOCK_LOCK
#
# SLES9 kernel has MS_FLOCK_LOCK sb flag
#
AC_DEFUN([LC_FUNC_MS_FLOCK_LOCK],
[AC_MSG_CHECKING([if kernel has MS_FLOCK_LOCK sb flag])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        int flags = MS_FLOCK_LOCK;
],[
        AC_DEFINE(HAVE_MS_FLOCK_LOCK, 1,
                [kernel has MS_FLOCK_LOCK flag])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_HAVE_CAN_SLEEP_ARG
#
# SLES9 kernel has third arg can_sleep
# in fs/locks.c: flock_lock_file_wait()
#
AC_DEFUN([LC_FUNC_HAVE_CAN_SLEEP_ARG],
[AC_MSG_CHECKING([if kernel has third arg can_sleep in fs/locks.c: flock_lock_file_wait()])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        int cansleep;
        struct file *file;
        struct file_lock *file_lock;
        flock_lock_file_wait(file, file_lock, cansleep);
],[
        AC_DEFINE(HAVE_CAN_SLEEP_ARG, 1,
                [kernel has third arg can_sleep in fs/locks.c: flock_lock_file_wait()])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_F_OP_FLOCK
#
# rhel4.2 kernel has f_op->flock field
#
AC_DEFUN([LC_FUNC_F_OP_FLOCK],
[AC_MSG_CHECKING([if struct file_operations has flock field])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct file_operations ll_file_operations_flock;
        ll_file_operations_flock.flock = NULL;
],[
        AC_DEFINE(HAVE_F_OP_FLOCK, 1,
                [struct file_operations has flock field])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_MS_FLOCK_LOCK
#
# SLES9 kernel has MS_FLOCK_LOCK sb flag
#
AC_DEFUN([LC_FUNC_MS_FLOCK_LOCK],
[AC_MSG_CHECKING([if kernel has MS_FLOCK_LOCK sb flag])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        int flags = MS_FLOCK_LOCK;
],[
        AC_DEFINE(HAVE_MS_FLOCK_LOCK, 1,
                [kernel has MS_FLOCK_LOCK flag])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_HAVE_CAN_SLEEP_ARG
#
# SLES9 kernel has third arg can_sleep
# in fs/locks.c: flock_lock_file_wait()
#
AC_DEFUN([LC_FUNC_HAVE_CAN_SLEEP_ARG],
[AC_MSG_CHECKING([if kernel has third arg can_sleep in fs/locks.c: flock_lock_file_wait()])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        int cansleep;
        struct file *file;
        struct file_lock *file_lock;
        flock_lock_file_wait(file, file_lock, cansleep);
],[
        AC_DEFINE(HAVE_CAN_SLEEP_ARG, 1,
                [kernel has third arg can_sleep in fs/locks.c: flock_lock_file_wait()])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_TASK_PPTR
#
# task struct has p_pptr instead of parent
#
AC_DEFUN([LC_TASK_PPTR],
[AC_MSG_CHECKING([task p_pptr found])
LB_LINUX_TRY_COMPILE([
	#include <linux/sched.h>
],[
	struct task_struct *p;
	
	p = p->p_pptr;
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_TASK_PPTR, 1, [task p_pptr found])
],[
	AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_F_OP_FLOCK
#
# rhel4.2 kernel has f_op->flock field
#
AC_DEFUN([LC_FUNC_F_OP_FLOCK],
[AC_MSG_CHECKING([if struct file_operations has flock field])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct file_operations ll_file_operations_flock;
        ll_file_operations_flock.flock = NULL;
],[
        AC_DEFINE(HAVE_F_OP_FLOCK, 1,
                [struct file_operations has flock field])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# LC_EXPORT_SYNCHRONIZE_RCU
# after 2.6.12 synchronize_rcu is preferred over synchronize_kernel
AC_DEFUN([LC_EXPORT_SYNCHRONIZE_RCU],
[LB_CHECK_SYMBOL_EXPORT([synchronize_rcu],
[kernel/rcupdate.c],[
        AC_DEFINE(HAVE_SYNCHRONIZE_RCU, 1,
                [in 2.6.12 synchronize_rcu preferred over synchronize_kernel])
],[
])
])

# LC_INODE_I_MUTEX
# after 2.6.15 inode have i_mutex intead of i_sem
AC_DEFUN([LC_INODE_I_MUTEX],
[AC_MSG_CHECKING([if inode has i_mutex ])
LB_LINUX_TRY_COMPILE([
	#include <linux/mutex.h>
	#include <linux/fs.h>
	#undef i_mutex
],[
	struct inode i;

	mutex_unlock(&i.i_mutex);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_INODE_I_MUTEX, 1,
                [after 2.6.15 inode have i_mutex intead of i_sem])
],[
        AC_MSG_RESULT(no)
])
])

# LC_DQUOTOFF_MUTEX
# after 2.6.17 dquote use mutex instead if semaphore
AC_DEFUN([LC_DQUOTOFF_MUTEX],
[AC_MSG_CHECKING([use dqonoff_mutex])
LB_LINUX_TRY_COMPILE([
	#include <linux/mutex.h>
	#include <linux/fs.h>
        #include <linux/quota.h>
],[
        struct quota_info dq;

        mutex_unlock(&dq.dqonoff_mutex);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_DQUOTOFF_MUTEX, 1,
                [after 2.6.17 dquote use mutex instead if semaphore])
],[
        AC_MSG_RESULT(no)
])
])

#
# LC_STATFS_DENTRY_PARAM
# starting from 2.6.18 linux kernel uses dentry instead of
# super_block for first vfs_statfs argument
#
AC_DEFUN([LC_STATFS_DENTRY_PARAM],
[AC_MSG_CHECKING([first vfs_statfs parameter is dentry])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
	int vfs_statfs(struct dentry *, struct kstatfs *);
],[
        AC_DEFINE(HAVE_STATFS_DENTRY_PARAM, 1,
                [first parameter of vfs_statfs is dentry])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_VFS_KERN_MOUNT
# starting from 2.6.18 kernel don't export do_kern_mount
# and want to use vfs_kern_mount instead.
#
AC_DEFUN([LC_VFS_KERN_MOUNT],
[AC_MSG_CHECKING([vfs_kern_mount exist in kernel])
LB_LINUX_TRY_COMPILE([
        #include <linux/mount.h>
],[
        vfs_kern_mount(NULL, 0, NULL, NULL);
],[
        AC_DEFINE(HAVE_VFS_KERN_MOUNT, 1,
                [vfs_kern_mount exist in kernel])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 
# LC_INVALIDATEPAGE_RETURN_INT
# more 2.6 api changes.  return type for the invalidatepage
# address_space_operation is 'void' in new kernels but 'int' in old
#
AC_DEFUN([LC_INVALIDATEPAGE_RETURN_INT],
[AC_MSG_CHECKING([invalidatepage has return int])
LB_LINUX_TRY_COMPILE([
        #include <linux/buffer_head.h>
],[
	int rc = block_invalidatepage(NULL, 0);
],[
	AC_MSG_RESULT(yes)
	AC_DEFINE(HAVE_INVALIDATEPAGE_RETURN_INT, 1,
		[Define if return type of invalidatepage should be int])
],[
	AC_MSG_RESULT(no)
])
])

# LC_UMOUNTBEGIN_HAS_VFSMOUNT
# more 2.6 API changes. 2.6.18 umount_begin has different parameters
AC_DEFUN([LC_UMOUNTBEGIN_HAS_VFSMOUNT],
[AC_MSG_CHECKING([if umount_begin needs vfsmount parameter instead of super_block])
tmp_flags="$EXTRA_KCFLAGS"
EXTRA_KCFLAGS="-Werror"
LB_LINUX_TRY_COMPILE([
	#include <linux/fs.h>

	struct vfsmount;
	static void cfg_umount_begin (struct vfsmount *v, int flags)
	{
    		;
	}

	static struct super_operations cfg_super_operations = {
		.umount_begin	= cfg_umount_begin,
	};
],[
	cfg_super_operations.umount_begin(NULL,0);
],[
	AC_MSG_RESULT(yes)
	AC_DEFINE(HAVE_UMOUNTBEGIN_VFSMOUNT, 1,
		[Define umount_begin need second argument])
],[
	AC_MSG_RESULT(no)
])
EXTRA_KCFLAGS="$tmp_flags"
])

# inode have i_private field since 2.6.17
AC_DEFUN([LC_INODE_IPRIVATE],
[AC_MSG_CHECKING([if inode has a i_private field])
LB_LINUX_TRY_COMPILE([
#include <linux/fs.h>
],[
	struct inode i;
	i.i_private = NULL; 
],[
	AC_MSG_RESULT(yes)
	AC_DEFINE(HAVE_INODE_IPRIVATE, 1,
		[struct inode has i_private field])
],[
	AC_MSG_RESULT(no)
])
])

# 2.6.19 API changes
# inode don't have i_blksize field
AC_DEFUN([LC_INODE_BLKSIZE],
[AC_MSG_CHECKING([inode has i_blksize field])
LB_LINUX_TRY_COMPILE([
#include <linux/fs.h>
],[
	struct inode i;
	i.i_blksize = 0; 
],[
	AC_MSG_RESULT(yes)
	AC_DEFINE(HAVE_INODE_BLKSIZE, 1,
		[struct inode has i_blksize field])
],[
	AC_MSG_RESULT(no)
])
])

# LC_VFS_READDIR_U64_INO
# 2.6.19 use u64 for inode number instead of inode_t
AC_DEFUN([LC_VFS_READDIR_U64_INO],
[AC_MSG_CHECKING([check vfs_readdir need 64bit inode number])
tmp_flags="$EXTRA_KCFLAGS"
EXTRA_KCFLAGS="-Werror"
LB_LINUX_TRY_COMPILE([
#include <linux/fs.h>
	int fillonedir(void * __buf, const char * name, int namlen, loff_t offset,
                      u64 ino, unsigned int d_type)
	{
		return 0;
	}
],[
	filldir_t filter;

	filter = fillonedir;
	return 1;
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_VFS_READDIR_U64_INO, 1,
                [if vfs_readdir need 64bit inode number])
],[
        AC_MSG_RESULT(no)
])
EXTRA_KCFLAGS="$tmp_flags"
])

# LC_FILE_UPDATE_TIME
# 2.6.9 has inode_update_time instead of file_update_time
AC_DEFUN([LC_FILE_UPDATE_TIME],
[AC_MSG_CHECKING([if file_update_time is exported])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        file_update_time(NULL);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_FILE_UPDATE_TIME, 1,
                [use file_update_time])
],[
       AC_MSG_RESULT(no)
])
])

# LC_FILE_WRITEV
# 2.6.19 replaced writev with aio_write
AC_DEFUN([LC_FILE_WRITEV],
[AC_MSG_CHECKING([writev in fops])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct file_operations *fops = NULL;
        fops->writev = NULL;
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_FILE_WRITEV, 1,
                [use fops->writev])
],[
	AC_MSG_RESULT(no)
])
])

# LC_GENERIC_FILE_READ
# 2.6.19 replaced readv with aio_read
AC_DEFUN([LC_FILE_READV],
[AC_MSG_CHECKING([readv in fops])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct file_operations *fops = NULL;
        fops->readv = NULL;
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_FILE_READV, 1,
                [use fops->readv])
],[
        AC_MSG_RESULT(no)
])
])

# LC_NR_PAGECACHE
# 2.6.18 don't export nr_pagecahe
AC_DEFUN([LC_NR_PAGECACHE],
[AC_MSG_CHECKING([kernel export nr_pagecache])
LB_LINUX_TRY_COMPILE([
        #include <linux/pagemap.h>
],[
        return atomic_read(&nr_pagecache);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_NR_PAGECACHE, 1,
                [is kernel export nr_pagecache])
],[
        AC_MSG_RESULT(no)
])
])

# LC_CANCEL_DIRTY_PAGE
# 2.6.20 introduse cancel_dirty_page instead of 
# clear_page_dirty.
AC_DEFUN([LC_CANCEL_DIRTY_PAGE],
[AC_MSG_CHECKING([kernel has cancel_dirty_page])
LB_LINUX_TRY_COMPILE([
        #include <linux/mm.h>
        #include <linux/page-flags.h>
],[
        /* tmp workaround for broken OFED 1.4.1 at SLES10 */
        #if defined(CONFIG_SLE_VERSION) && CONFIG_SLE_VERSION == 10 && defined(_BACKPORT_LINUX_MM_H_)
        #error badly implementation of cancel_dirty_pages
        #endif
        cancel_dirty_page(NULL, 0);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_CANCEL_DIRTY_PAGE, 1,
                  [kernel has cancel_dirty_page instead of clear_page_dirty])
],[
        AC_MSG_RESULT(no)
])
])

#
# LC_PAGE_CONSTANT
#
# In order to support raid5 zerocopy patch, we have to patch the kernel to make
# it support constant page, which means the page won't be modified during the
# IO.
#
AC_DEFUN([LC_PAGE_CONSTANT],
[AC_MSG_CHECKING([if kernel have PageConstant defined])
LB_LINUX_TRY_COMPILE([
        #include <linux/mm.h>
        #include <linux/page-flags.h>
],[
        #ifndef PG_constant
        #error "Have no raid5 zcopy patch"
        #endif
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_PAGE_CONSTANT, 1, [kernel have PageConstant supported])
],[
        AC_MSG_RESULT(no);
])
])

# RHEL5 in FS-cache patch rename PG_checked flag
# into PG_fs_misc
AC_DEFUN([LC_PG_FS_MISC],
[AC_MSG_CHECKING([kernel has PG_fs_misc])
LB_LINUX_TRY_COMPILE([
        #include <linux/mm.h>
        #include <linux/page-flags.h>
],[
        #ifndef PG_fs_misc
        #error PG_fs_misc not defined in kernel
        #endif
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_PG_FS_MISC, 1,
                  [is kernel have PG_fs_misc])
],[
        AC_MSG_RESULT(no)
])
])

# RHEL5 PageChecked and SetPageChecked defined
AC_DEFUN([LC_PAGE_CHECKED],
[AC_MSG_CHECKING([kernel has PageChecked and SetPageChecked])
LB_LINUX_TRY_COMPILE([
        #include <linux/autoconf.h>
#ifdef HAVE_LINUX_MMTYPES_H
        #include <linux/mm_types.h>
#endif
	#include <linux/page-flags.h>
],[
 	struct page *p;

        /* before 2.6.26 this define*/
        #ifndef PageChecked	
 	/* 2.6.26 use function instead of define for it */
 	SetPageChecked(p);
 	PageChecked(p);
 	#endif
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_PAGE_CHECKED, 1,
                  [does kernel have PageChecked and SetPageChecked])
],[
        AC_MSG_RESULT(no)
])
])

AC_DEFUN([LC_EXPORT_TRUNCATE_COMPLETE_PAGE],
[LB_CHECK_SYMBOL_EXPORT([truncate_complete_page],
[mm/truncate.c],[
AC_DEFINE(HAVE_TRUNCATE_COMPLETE_PAGE, 1,
            [kernel export truncate_complete_page])
],[
])
])

AC_DEFUN([LC_EXPORT_TRUNCATE_RANGE],
[LB_CHECK_SYMBOL_EXPORT([truncate_inode_pages_range],
[mm/truncate.c],[
AC_DEFINE(HAVE_TRUNCATE_RANGE, 1,
            [kernel export truncate_inode_pages_range])
],[
])
])

AC_DEFUN([LC_EXPORT_D_REHASH_COND],
[LB_CHECK_SYMBOL_EXPORT([d_rehash_cond],
[fs/dcache.c],[
AC_DEFINE(HAVE_D_REHASH_COND, 1,
            [d_rehash_cond is exported by the kernel])
],[
])
])

AC_DEFUN([LC_EXPORT___D_REHASH],
[LB_CHECK_SYMBOL_EXPORT([__d_rehash],
[fs/dcache.c],[
AC_DEFINE(HAVE___D_REHASH, 1,
            [__d_rehash is exported by the kernel])
],[
])
])

AC_DEFUN([LC_EXPORT_D_MOVE_LOCKED],
[LB_CHECK_SYMBOL_EXPORT([d_move_locked],
[fs/dcache.c],[
AC_DEFINE(HAVE_D_MOVE_LOCKED, 1,
            [d_move_locked is exported by the kernel])
],[
])
])

AC_DEFUN([LC_EXPORT___D_MOVE],
[LB_CHECK_SYMBOL_EXPORT([__d_move],
[fs/dcache.c],[
AC_DEFINE(HAVE___D_MOVE, 1,
            [__d_move is exported by the kernel])
],[
])
])

#
# LC_EXPORT_INVALIDATE_MAPPING_PAGES
#
# SLES9, RHEL4, RHEL5, vanilla 2.6.24 export invalidate_mapping_pages() but
# SLES10 2.6.16 does not, for some reason.  For filter cache invalidation.
#
AC_DEFUN([LC_EXPORT_INVALIDATE_MAPPING_PAGES],
    [LB_CHECK_SYMBOL_EXPORT([invalidate_mapping_pages], [mm/truncate.c], [
         AC_DEFINE(HAVE_INVALIDATE_MAPPING_PAGES, 1,
                        [exported invalidate_mapping_pages])],
    [LB_CHECK_SYMBOL_EXPORT([invalidate_inode_pages], [mm/truncate.c], [
         AC_DEFINE(HAVE_INVALIDATE_INODE_PAGES, 1,
                        [exported invalidate_inode_pages])], [
       AC_MSG_ERROR([no way to invalidate pages])
  ])
    ],[])
])

#
# LC_EXPORT_FILEMAP_FDATASYNC_RANGE
#
# No standard kernels export this
#
AC_DEFUN([LC_EXPORT_FILEMAP_FDATAWRITE_RANGE],
[LB_CHECK_SYMBOL_EXPORT([filemap_fdatawrite_range],
[mm/filemap.c],[
AC_DEFINE(HAVE_FILEMAP_FDATAWRITE_RANGE, 1,
            [filemap_fdatawrite_range is exported by the kernel])
],[
])
])

# The actual symbol exported varies among architectures, so we need
# to check many symbols (but only in the current architecture.)  No
# matter what symbol is exported, the kernel #defines node_to_cpumask
# to the appropriate function and that's what we use.
AC_DEFUN([LC_EXPORT_NODE_TO_CPUMASK],
         [LB_CHECK_SYMBOL_EXPORT([node_to_cpumask],
                                 [arch/$LINUX_ARCH/mm/numa.c],
                                 [AC_DEFINE(HAVE_NODE_TO_CPUMASK, 1,
                                            [node_to_cpumask is exported by
                                             the kernel])]) # x86_64
          LB_CHECK_SYMBOL_EXPORT([node_to_cpu_mask],
                                 [arch/$LINUX_ARCH/kernel/smpboot.c],
                                 [AC_DEFINE(HAVE_NODE_TO_CPUMASK, 1,
                                            [node_to_cpumask is exported by
                                             the kernel])]) # ia64
          LB_CHECK_SYMBOL_EXPORT([node_2_cpu_mask],
                                 [arch/$LINUX_ARCH/kernel/smpboot.c],
                                 [AC_DEFINE(HAVE_NODE_TO_CPUMASK, 1,
                                            [node_to_cpumask is exported by
                                             the kernel])]) # i386
          ])

#
# LC_VFS_INTENT_PATCHES
#
# check if the kernel has the VFS intent patches
AC_DEFUN([LC_VFS_INTENT_PATCHES],
[AC_MSG_CHECKING([if the kernel has the VFS intent patches])
LB_LINUX_TRY_COMPILE([
	#include <linux/fs.h>
        #include <linux/namei.h>
],[
        struct nameidata nd;
        struct lookup_intent *it;

        it = &nd.intent;
        intent_init(it, IT_OPEN);
        it->d.lustre.it_disposition = 0;
        it->d.lustre.it_data = NULL;
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_VFS_INTENT_PATCHES, 1, [VFS intent patches are applied])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.22 lost second parameter for invalidate_bdev
AC_DEFUN([LC_INVALIDATE_BDEV_2ARG],
[AC_MSG_CHECKING([if invalidate_bdev has second argument])
LB_LINUX_TRY_COMPILE([
        #include <linux/buffer_head.h>
],[
        invalidate_bdev(NULL,0);
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_INVALIDATE_BDEV_2ARG, 1,
                [invalidate_bdev has second argument])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.12 merge patch from oracle to convert tree_lock from spinlock to rwlock
AC_DEFUN([LC_RW_TREE_LOCK],
[AC_MSG_CHECKING([if kernel has tree_lock as rwlock])
tmp_flags="$EXTRA_KCFLAGS"
EXTRA_KCFLAGS="-Werror"
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct address_space a;

        write_lock(&a.tree_lock);
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_RW_TREE_LOCK, 1, [kernel has tree_lock as rw_lock])
],[
        AC_MSG_RESULT([no])
])
EXTRA_KCFLAGS="$tmp_flags"
])

# 2.6.18


# 2.6.23 have return type 'void' for unregister_blkdev
AC_DEFUN([LC_UNREGISTER_BLKDEV_RETURN_INT],
[AC_MSG_CHECKING([if unregister_blkdev return int])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        int i = unregister_blkdev(0,NULL);
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_UNREGISTER_BLKDEV_RETURN_INT, 1, 
                [unregister_blkdev return int])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.23 change .sendfile to .splice_read
# RHEL4 (-92 kernel) have both sendfile and .splice_read API
AC_DEFUN([LC_KERNEL_SENDFILE],
[AC_MSG_CHECKING([if kernel has .sendfile])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct file_operations file;

        file.sendfile = NULL;
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_KERNEL_SENDFILE, 1,
                [kernel has .sendfile])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.23 change .sendfile to .splice_read
AC_DEFUN([LC_KERNEL_SPLICE_READ],
[AC_MSG_CHECKING([if kernel has .splice_read])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct file_operations file;

        file.splice_read = NULL;
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_KERNEL_SPLICE_READ, 1,
                [kernel has .slice_read])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.23 extract nfs export related data into exportfs.h
AC_DEFUN([LC_HAVE_EXPORTFS_H],
[LB_CHECK_FILE([$LINUX/include/linux/exportfs.h], [
        AC_DEFINE(HAVE_LINUX_EXPORTFS_H, 1,
                [kernel has include/exportfs.h])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.23 have new page fault handling API
AC_DEFUN([LC_VM_OP_FAULT],
[AC_MSG_CHECKING([if kernel has .fault in vm_operation_struct])
LB_LINUX_TRY_COMPILE([
        #include <linux/mm.h>
],[
        struct vm_operations_struct op;

        op.fault = NULL;
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_VM_OP_FAULT, 1,
                [if kernel has .fault in vm_operation_struct])
],[
        AC_MSG_RESULT([no])
])
])

#2.6.23 has new shrinker API
AC_DEFUN([LC_REGISTER_SHRINKER],
[AC_MSG_CHECKING([if kernel has register_shrinker])
LB_LINUX_TRY_COMPILE([
        #include <linux/mm.h>
],[
        register_shrinker(NULL);
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_REGISTER_SHRINKER, 1,
                [if kernel has register_shrinker])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.23 add code to wait other users to complete before removing procfs entry
AC_DEFUN([LC_PROCFS_USERS],
[AC_MSG_CHECKING([if kernel has pde_users member in procfs entry struct])
LB_LINUX_TRY_COMPILE([
        #include <linux/proc_fs.h>
],[
        struct proc_dir_entry pde;

        pde.pde_users   = 0;
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_PROCFS_USERS, 1, 
                [kernel has pde_users member in procfs entry struct])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.24 has bio_endio with 2 args
AC_DEFUN([LC_BIO_ENDIO_2ARG],
[AC_MSG_CHECKING([if kernel has bio_endio with 2 args])
LB_LINUX_TRY_COMPILE([
        #include <linux/bio.h>
],[
        bio_endio(NULL, 0);
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_BIO_ENDIO_2ARG, 1,
                [if kernel has bio_endio with 2 args])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.24 has new members in exports struct.
AC_DEFUN([LC_FH_TO_DENTRY],
[AC_MSG_CHECKING([if kernel has .fh_to_dentry member in export_operations struct])
LB_LINUX_TRY_COMPILE([
#ifdef HAVE_LINUX_EXPORTFS_H
        #include <linux/exportfs.h>
#else
        #include <linux/fs.h>
#endif
],[
        struct export_operations exp;

        exp.fh_to_dentry   = NULL;
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_FH_TO_DENTRY, 1,
                [kernel has .fh_to_dentry member in export_operations struct])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.24 need linux/mm_types.h included
AC_DEFUN([LC_HAVE_MMTYPES_H],
[LB_CHECK_FILE([$LINUX/include/linux/mm_types.h], [
        AC_DEFINE(HAVE_LINUX_MMTYPES_H, 1,
                [kernel has include/mm_types.h])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.24 remove long aged procfs entry -> deleted member
AC_DEFUN([LC_PROCFS_DELETED],
[AC_MSG_CHECKING([if kernel has deleted member in procfs entry struct])
LB_LINUX_TRY_COMPILE([
	#include <linux/proc_fs.h>
],[
        struct proc_dir_entry pde;

        pde.deleted   = NULL;
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_PROCFS_DELETED, 1,
                [kernel has deleted member in procfs entry struct])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.25 change define to inline
AC_DEFUN([LC_MAPPING_CAP_WRITEBACK_DIRTY],
[AC_MSG_CHECKING([if kernel have mapping_cap_writeback_dirty])
LB_LINUX_TRY_COMPILE([
        #include <linux/backing-dev.h>
],[
        #ifndef mapping_cap_writeback_dirty
        mapping_cap_writeback_dirty(NULL);
        #endif
],[
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_MAPPING_CAP_WRITEBACK_DIRTY, 1,
                [kernel have mapping_cap_writeback_dirty])
],[
        AC_MSG_RESULT([no])
])
])



# 2.6.26 isn't export set_fs_pwd and change paramter in fs struct
AC_DEFUN([LC_FS_STRUCT_USE_PATH],
[AC_MSG_CHECKING([fs_struct use path structure])
LB_LINUX_TRY_COMPILE([
        #include <asm/atomic.h>
        #include <linux/spinlock.h>
        #include <linux/fs_struct.h>
],[
        struct path path;
        struct fs_struct fs;

        fs.pwd = path;
], [
        AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_FS_STRUCT_USE_PATH, 1,
                [fs_struct use path structure])
],[
        AC_MSG_RESULT([no])
])
])

#2.6.27
AC_DEFUN([LC_INODE_PERMISION_2ARGS],
[AC_MSG_CHECKING([inode_operations->permission have two args])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct inode *inode;

        inode->i_op->permission(NULL,0);
],[
        AC_DEFINE(HAVE_INODE_PERMISION_2ARGS, 1, 
                  [inode_operations->permission have two args])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 have file_remove_suid instead of remove_suid
AC_DEFUN([LC_FILE_REMOVE_SUID],
[AC_MSG_CHECKING([kernel have file_remove_suid])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        file_remove_suid(NULL);
],[
        AC_DEFINE(HAVE_FILE_REMOVE_SUID, 1,
                  [kernel have file_remove_suid])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 have new page locking API
AC_DEFUN([LC_TRYLOCKPAGE],
[AC_MSG_CHECKING([kernel use trylock_page for page lock])
LB_LINUX_TRY_COMPILE([
        #include <linux/pagemap.h>
],[
        trylock_page(NULL);
],[
        AC_DEFINE(HAVE_TRYLOCK_PAGE, 1,
                  [kernel use trylock_page for page lock])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 and some older have mapping->tree_lock as spin_lock
AC_DEFUN([LC_RW_TREE_LOCK],
[AC_MSG_CHECKING([mapping->tree_lock is rw_lock])
tmp_flags="$EXTRA_KCFLAGS"
EXTRA_KCFLAGS="-Werror"
LB_LINUX_TRY_COMPILE([
	#include <linux/fs.h>
],[
	struct address_space *map = NULL;

	write_lock_irq(&map->tree_lock);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_RW_TREE_LOCK, 1,
                [mapping->tree_lock is rw_lock])
],[
        AC_MSG_RESULT(no)
])
EXTRA_KCFLAGS="$tmp_flags"
])

# 2.6.5 sles9 hasn't define sysctl_vfs_cache_pressure
AC_DEFUN([LC_HAVE_SYSCTL_VFS_CACHE_PRESSURE],
[LB_CHECK_SYMBOL_EXPORT([sysctl_vfs_cache_pressure],
[fs/dcache.c],[
        AC_DEFINE(HAVE_SYSCTL_VFS_CACHE_PRESSURE, 1, [kernel exports sysctl_vfs_cache_pressure])
],[
])
])

# vfs_symlink seems to have started out with 3 args until 2.6.7 where a
# "mode" argument was added, but then again, in some later version it was
# removed
AC_DEFUN([LC_4ARGS_VFS_SYMLINK],
[AC_MSG_CHECKING([if vfs_symlink wants 4 args])
LB_LINUX_TRY_COMPILE([
	#include <linux/fs.h>
],[
	struct inode *dir;
	struct dentry *dentry;
	const char *oldname = NULL;
	int mode = 0;

	vfs_symlink(dir, dentry, oldname, mode);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_4ARGS_VFS_SYMLINK, 1,
                  [vfs_symlink wants 4 args])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.27 sles11 remove the bi_hw_segments
AC_DEFUN([LC_BI_HW_SEGMENTS],
[AC_MSG_CHECKING([struct bio has a bi_hw_segments field])
LB_LINUX_TRY_COMPILE([
        #include <linux/bio.h>
],[
        struct bio io;
        io.bi_hw_segments = 0;
],[
        AC_DEFINE(HAVE_BI_HW_SEGMENTS, 1,
                [struct bio has a bi_hw_segments field])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 sles11 move the quotaio_v1.h to fs
AC_DEFUN([LC_HAVE_QUOTAIO_V1_H],
[LB_CHECK_FILE([$LINUX/include/linux/quotaio_v1.h],[
        AC_DEFINE(HAVE_QUOTAIO_V1_H, 1,
                [kernel has include/linux/quotaio_v1.h])
],[
        AC_MSG_RESULT([no])
])
])

# sles10 sp2 need 5 parameter for vfs_symlink
AC_DEFUN([LC_VFS_SYMLINK_5ARGS],
[AC_MSG_CHECKING([vfs_symlink need 5 parameter])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct inode *dir = NULL;
        struct dentry *dentry = NULL;
        struct vfsmount *mnt = NULL;
        const char * path = NULL;
        vfs_symlink(dir, dentry, mnt, path, 0);
],[
        AC_DEFINE(HAVE_VFS_SYMLINK_5ARGS, 1,
                [vfs_symlink need 5 parameteres])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 removed the read_inode from super_operations.
AC_DEFUN([LC_READ_INODE_IN_SBOPS],
[AC_MSG_CHECKING([super_operations has a read_inode field])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct super_operations *sop;
        sop->read_inode(NULL);
],[
        AC_DEFINE(HAVE_READ_INODE_IN_SBOPS, 1,
                [super_operations has a read_inode])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 sles11 has sb_any_quota_active
AC_DEFUN([LC_SB_ANY_QUOTA_ACTIVE],
[AC_MSG_CHECKING([Kernel has sb_any_quota_active])
LB_LINUX_TRY_COMPILE([
        #include <linux/quotaops.h>
],[
        sb_any_quota_active(NULL);
],[
        AC_DEFINE(HAVE_SB_ANY_QUOTA_ACTIVE, 1,
                [Kernel has a sb_any_quota_active])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 sles11 has sb_has_quota_active
AC_DEFUN([LC_SB_HAS_QUOTA_ACTIVE],
[AC_MSG_CHECKING([Kernel has sb_has_quota_active])
LB_LINUX_TRY_COMPILE([
        #include <linux/quotaops.h>
],[
        sb_has_quota_active(NULL, 0);
],[
        AC_DEFINE(HAVE_SB_HAS_QUOTA_ACTIVE, 1,
                [Kernel has a sb_has_quota_active])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 has inode_permission instead of permisson
AC_DEFUN([LC_EXPORT_INODE_PERMISSION],
[LB_CHECK_SYMBOL_EXPORT([inode_permission],
[fs/namei.c],[
AC_DEFINE(HAVE_EXPORT_INODE_PERMISSION, 1,
            [inode_permission is exported by the kernel])
],[
])
])

# 2.6.27 use 5th parameter in quota_on for remount.
AC_DEFUN([LC_QUOTA_ON_5ARGS],
[AC_MSG_CHECKING([quota_on needs 5 parameters])
LB_LINUX_TRY_COMPILE([
        #include <linux/quota.h>
],[
        struct quotactl_ops *qop;
        qop->quota_on(NULL, 0, 0, NULL, 0);
],[
        AC_DEFINE(HAVE_QUOTA_ON_5ARGS, 1,
                [quota_on needs 5 paramters])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 use 3th parameter in quota_off for remount.
AC_DEFUN([LC_QUOTA_OFF_3ARGS],
[AC_MSG_CHECKING([quota_off needs 3 parameters])
LB_LINUX_TRY_COMPILE([
        #include <linux/quota.h>
],[
        struct quotactl_ops *qop;
        qop->quota_off(NULL, 0, 0);
],[
        AC_DEFINE(HAVE_QUOTA_OFF_3ARGS, 1,
                [quota_off needs 3 paramters])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

# 2.6.27 has vfs_dq_off inline function.
AC_DEFUN([LC_VFS_DQ_OFF],
[AC_MSG_CHECKING([vfs_dq_off is defined])
LB_LINUX_TRY_COMPILE([
        #include <linux/quotaops.h>
],[
        vfs_dq_off(NULL, 0);
],[
        AC_DEFINE(HAVE_VFS_DQ_OFF, 1, [vfs_dq_off is defined])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# Ensure stack size big than 8k in Lustre server
AC_DEFUN([LC_STACK_SIZE],
[AC_MSG_CHECKING([stack size big than 8k])
LB_LINUX_TRY_COMPILE([
	#include <linux/thread_info.h>
],[
        #if THREAD_SIZE < 8192
        #error "stack size < 8192"
        #endif
],[
        AC_MSG_RESULT(yes)
],[
        AC_MSG_ERROR([Lustre requires that Linux is configured with at least a 8KB stack.])
])
])

#
# LC_PROG_LINUX
#
# Lustre linux kernel checks
#
AC_DEFUN([LC_PROG_LINUX],
         [LC_LUSTRE_VERSION_H
          if test x$enable_server = xyes ; then
              LC_CONFIG_BACKINGFS
              LC_STACK_SIZE
          fi
          LC_CONFIG_PINGER
          LC_CONFIG_CHECKSUM
          LC_CONFIG_LIBLUSTRE_RECOVERY
          LC_CONFIG_HEALTH_CHECK_WRITE
          LC_CONFIG_LRU_RESIZE
          LC_CONFIG_ADAPTIVE_TIMEOUTS
          LC_CONFIG_DELAYED_RECOVERY
          LC_QUOTA_MODULE

          LC_TASK_PPTR
          # RHEL4 patches
          LC_EXPORT_TRUNCATE_COMPLETE_PAGE
          LC_EXPORT_TRUNCATE_RANGE
          LC_EXPORT_D_REHASH_COND
          LC_EXPORT___D_REHASH
          LC_EXPORT_D_MOVE_LOCKED
          LC_EXPORT___D_MOVE
          LC_EXPORT_NODE_TO_CPUMASK

          LC_FUNC_RELEASEPAGE_WITH_GFP
          LC_HEADER_MM_INLINE
          LC_STRUCT_INODE
          LC_FUNC_REGISTER_CACHE
          LC_FUNC_GRAB_CACHE_PAGE_NOWAIT_GFP
          LC_FUNC_DEV_SET_RDONLY
          LC_FUNC_FILEMAP_FDATAWRITE
          LC_STRUCT_STATFS
          LC_FUNC_PAGE_MAPPED
          LC_STRUCT_FILE_OPS_UNLOCKED_IOCTL
          LC_FILEMAP_POPULATE
          LC_D_ADD_UNIQUE
          LC_BIT_SPINLOCK_H
          LC_XATTR_ACL
          LC_STRUCT_INTENT_FILE
          LC_POSIX_ACL_XATTR_H
          LC_EXPORT___IGET
          LC_FUNC_MS_FLOCK_LOCK
          LC_FUNC_HAVE_CAN_SLEEP_ARG
          LC_FUNC_F_OP_FLOCK
          LC_QUOTA_READ
          LC_COOKIE_FOLLOW_LINK
          LC_FUNC_RCU
          LC_PERCPU_COUNTER
          LC_QUOTA64
          LC_4ARGS_VFS_SYMLINK

          # does the kernel have VFS intent patches?
          LC_VFS_INTENT_PATCHES

	  # 2.6.5 sles9
	  LC_HAVE_SYSCTL_VFS_CACHE_PRESSURE

          # 2.6.12
          LC_RW_TREE_LOCK
          LC_EXPORT_SYNCHRONIZE_RCU

          # 2.6.15
          LC_INODE_I_MUTEX

          # 2.6.16
          LC_SECURITY_PLUG  # for SLES10 SP2

          # 2.6.17
          LC_DQUOTOFF_MUTEX

          # 2.6.18
          LC_NR_PAGECACHE
          LC_STATFS_DENTRY_PARAM
          LC_VFS_KERN_MOUNT
          LC_INVALIDATEPAGE_RETURN_INT
          LC_UMOUNTBEGIN_HAS_VFSMOUNT
          LC_INODE_IPRIVATE
          LC_EXPORT_FILEMAP_FDATAWRITE_RANGE
          if test x$enable_server = xyes ; then
                LC_EXPORT_INVALIDATE_MAPPING_PAGES
          fi

          #2.6.18 + RHEL5 (fc6)
          LC_PG_FS_MISC
          LC_PAGE_CHECKED

          # 2.6.19
          LC_INODE_BLKSIZE
          LC_VFS_READDIR_U64_INO
          LC_FILE_UPDATE_TIME
          LC_FILE_WRITEV
          LC_FILE_READV

          # 2.6.20
          LC_CANCEL_DIRTY_PAGE

          # raid5-zerocopy patch
          LC_PAGE_CONSTANT

          # 2.6.22
          LC_INVALIDATE_BDEV_2ARG
          LC_FS_RENAME_DOES_D_MOVE
          # 2.6.23
          LC_UNREGISTER_BLKDEV_RETURN_INT
          LC_KERNEL_SENDFILE
          LC_KERNEL_SPLICE_READ
          LC_HAVE_EXPORTFS_H
          LC_VM_OP_FAULT
          LC_REGISTER_SHRINKER
          LC_PROCFS_USERS

          # 2.6.25
          LC_MAPPING_CAP_WRITEBACK_DIRTY

          # 2.6.24
          LC_HAVE_MMTYPES_H
          LC_BIO_ENDIO_2ARG
          LC_FH_TO_DENTRY
          LC_PROCFS_DELETED

          # 2.6.26
          LC_FS_STRUCT_USE_PATH
          LC_RCU_LIST_SAFE

          # 2.6.27
          LC_INODE_PERMISION_2ARGS
          LC_FILE_REMOVE_SUID
          LC_TRYLOCKPAGE
          LC_RW_TREE_LOCK
          LC_READ_INODE_IN_SBOPS
          LC_EXPORT_INODE_PERMISSION
          LC_QUOTA_ON_5ARGS
          LC_QUOTA_OFF_3ARGS
          LC_VFS_DQ_OFF

          # 2.6.27.15-2 sles11
          LC_BI_HW_SEGMENTS
          LC_HAVE_QUOTAIO_V1_H
          LC_VFS_SYMLINK_5ARGS
          LC_SB_ANY_QUOTA_ACTIVE
          LC_SB_HAS_QUOTA_ACTIVE
])

#
# LC_CONFIG_CLIENT_SERVER
#
# Build client/server sides of Lustre
#
AC_DEFUN([LC_CONFIG_CLIENT_SERVER],
[AC_MSG_CHECKING([whether to build Lustre server support])
AC_ARG_ENABLE([server],
	AC_HELP_STRING([--disable-server],
			[disable Lustre server support]),
	[],[enable_server='yes'])
AC_MSG_RESULT([$enable_server])

AC_MSG_CHECKING([whether to build Lustre client support])
AC_ARG_ENABLE([client],
	AC_HELP_STRING([--disable-client],
			[disable Lustre client support]),
	[],[enable_client='yes'])
AC_MSG_RESULT([$enable_client])])

#
# LC_CONFIG_LIBLUSTRE
#
# whether to build liblustre
#
AC_DEFUN([LC_CONFIG_LIBLUSTRE],
[AC_MSG_CHECKING([whether to build Lustre library])
AC_ARG_ENABLE([liblustre],
	AC_HELP_STRING([--disable-liblustre],
			[disable building of Lustre library]),
	[],[enable_liblustre=$with_sysio])
AC_MSG_RESULT([$enable_liblustre])
# only build sysio if liblustre is built
with_sysio="$enable_liblustre"

AC_MSG_CHECKING([whether to build liblustre tests])
AC_ARG_ENABLE([liblustre-tests],
	AC_HELP_STRING([--enable-liblustre-tests],
			[enable liblustre tests, if --disable-tests is used]),
	[],[enable_liblustre_tests=$enable_tests])
if test x$enable_liblustre != xyes ; then
   enable_liblustre_tests='no'
fi
AC_MSG_RESULT([$enable_liblustre_tests])

AC_MSG_CHECKING([whether to enable liblustre acl])
AC_ARG_ENABLE([liblustre-acl],
	AC_HELP_STRING([--disable-liblustre-acl],
			[disable ACL support for liblustre]),
	[],[enable_liblustre_acl=yes])
AC_MSG_RESULT([$enable_liblustre_acl])
if test x$enable_liblustre_acl = xyes ; then
  AC_DEFINE(LIBLUSTRE_POSIX_ACL, 1, Liblustre Support ACL-enabled MDS)
fi

#
# --enable-mpitest
#
AC_ARG_ENABLE(mpitests,
	AC_HELP_STRING([--enable-mpitests=yes|no|mpicc wrapper],
                           [include mpi tests]),
	[
	 enable_mpitests=yes
         case $enableval in
         yes)
		MPICC_WRAPPER=mpicc
		;;
         no)
		enable_mpitests=no
		;;
         *)
		MPICC_WRAPPER=$enableval
                 ;;
	 esac
	],
	[
	MPICC_WRAPPER=mpicc
	enable_mpitests=yes
	]
)

if test x$enable_mpitests != xno; then
	AC_MSG_CHECKING([whether mpitests can be built])
	oldcc=$CC
	CC=$MPICC_WRAPPER
	AC_LINK_IFELSE(
	    [AC_LANG_PROGRAM([[
		    #include <mpi.h>
	        ]],[[
		    int flag;
		    MPI_Initialized(&flag);
		]])],
	    [
		    AC_MSG_RESULT([yes])
	    ],[
		    AC_MSG_RESULT([no])
		    enable_mpitests=no
	])
	CC=$oldcc
fi
AC_SUBST(MPICC_WRAPPER)

AC_MSG_NOTICE([Enabling Lustre configure options for libsysio])
ac_configure_args="$ac_configure_args --with-lustre-hack --with-sockets"

LC_CONFIG_PINGER
LC_CONFIG_LIBLUSTRE_RECOVERY
])

AC_DEFUN([LC_CONFIG_LRU_RESIZE],
[AC_MSG_CHECKING([whether to enable lru self-adjusting])
AC_ARG_ENABLE([lru_resize], 
	AC_HELP_STRING([--enable-lru-resize],
			[enable lru resize support]),
	[],[enable_lru_resize='yes'])
AC_MSG_RESULT([$enable_lru_resize])
if test x$enable_lru_resize != xno; then
   AC_DEFINE(HAVE_LRU_RESIZE_SUPPORT, 1, [Enable lru resize support])
fi
])

AC_DEFUN([LC_CONFIG_ADAPTIVE_TIMEOUTS],
[AC_MSG_CHECKING([whether to enable ptlrpc adaptive timeouts support])
AC_ARG_ENABLE([adaptive_timeouts],
	AC_HELP_STRING([--disable-adaptive-timeouts],
			[disable ptlrpc adaptive timeouts support]),
	[],[enable_adaptive_timeouts='yes'])
AC_MSG_RESULT([$enable_adaptive_timeouts])
if test x$enable_adaptive_timeouts == xyes; then
   AC_DEFINE(HAVE_AT_SUPPORT, 1, [Enable adaptive timeouts support])
fi
])

# config delayed recovery
AC_DEFUN([LC_CONFIG_DELAYED_RECOVERY],
[AC_MSG_CHECKING([whether to enable delayed recovery support])
AC_ARG_ENABLE([delayed-recovery],
	AC_HELP_STRING([--enable-delayed-recovery],
			[enable late recovery after main one]),
	[],[enable_delayed_recovery='no'])
AC_MSG_RESULT([$enable_delayed_recovery])
if test x$enable_delayed_recovery == xyes; then
   AC_DEFINE(HAVE_DELAYED_RECOVERY, 1, [Enable delayed recovery support])
fi
])

#
# LC_CONFIG_QUOTA
#
# whether to enable quota support global control
#
AC_DEFUN([LC_CONFIG_QUOTA],
[AC_ARG_ENABLE([quota],
	AC_HELP_STRING([--enable-quota],
			[enable quota support]),
	[],[enable_quota='yes'])
])

# whether to enable quota support(kernel modules)
AC_DEFUN([LC_QUOTA_MODULE],
[if test x$enable_quota != xno; then
    LB_LINUX_CONFIG([QUOTA],[
	enable_quota_module='yes'
	AC_DEFINE(HAVE_QUOTA_SUPPORT, 1, [Enable quota support])
    ],[
	enable_quota_module='no'
	AC_MSG_WARN([quota is not enabled because the kernel - lacks quota support])
    ])
fi
])

AC_DEFUN([LC_QUOTA],
[#check global
LC_CONFIG_QUOTA
#check for utils
AC_CHECK_HEADER(sys/quota.h,
                [AC_DEFINE(HAVE_SYS_QUOTA_H, 1, [Define to 1 if you have <sys/quota.h>.])],
                [AC_MSG_ERROR([don't find <sys/quota.h> in your system])])
])

AC_DEFUN([LC_QUOTA_READ],
[AC_MSG_CHECKING([if kernel supports quota_read])
LB_LINUX_TRY_COMPILE([
	#include <linux/fs.h>
],[
	struct super_operations sp;
        void *i = (void *)sp.quota_read;
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(KERNEL_SUPPORTS_QUOTA_READ, 1, [quota_read found])
],[
	AC_MSG_RESULT([no])
])
])

#
# LC_COOKIE_FOLLOW_LINK
#
# kernel 2.6.13+ ->follow_link returns a cookie
#

AC_DEFUN([LC_COOKIE_FOLLOW_LINK],
[AC_MSG_CHECKING([if inode_operations->follow_link returns a cookie])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
        #include <linux/namei.h>
],[
        struct dentry dentry;
        struct nameidata nd;

        dentry.d_inode->i_op->put_link(&dentry, &nd, NULL);
],[
        AC_DEFINE(HAVE_COOKIE_FOLLOW_LINK, 1, [inode_operations->follow_link returns a cookie])
        AC_MSG_RESULT([yes])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_FUNC_RCU
#
# kernels prior than 2.6.0(?) have no RCU supported; in kernel 2.6.5(SUSE), 
# call_rcu takes three parameters.
#
AC_DEFUN([LC_FUNC_RCU],
[AC_MSG_CHECKING([if kernel have RCU supported])
LB_LINUX_TRY_COMPILE([
        #include <linux/rcupdate.h>
],[],[
        AC_DEFINE(HAVE_RCU, 1, [have RCU defined])
        AC_MSG_RESULT([yes])

        AC_MSG_CHECKING([if call_rcu takes three parameters])
        LB_LINUX_TRY_COMPILE([
                #include <linux/rcupdate.h>
        ],[
                struct rcu_head rh;
                call_rcu(&rh, (void (*)(struct rcu_head *))1, NULL);
        ],[
                AC_DEFINE(HAVE_CALL_RCU_PARAM, 1, [call_rcu takes three parameters])
                AC_MSG_RESULT([yes])
        ],[
                AC_MSG_RESULT([no]) 
        ])

],[
        AC_MSG_RESULT([no])
])
])

#
# LC_QUOTA64
# linux kernel may have 64-bit limits support
#
AC_DEFUN([LC_QUOTA64],
if test x$enable_server = xyes ; then
[AC_MSG_CHECKING([if kernel has 64-bit quota limits support])
LB_LINUX_TRY_COMPILE([
        #include <linux/kernel.h>
        #include <linux/fs.h>
        #include <linux/quotaio_v2.h>
        int versions[] = V2_INITQVERSIONS_R1;
        struct v2_disk_dqblk_r1 dqblk_r1;
],[],[
        AC_DEFINE(HAVE_QUOTA64, 1, [have quota64])
        AC_MSG_RESULT([yes])
],[
        tmp_flags="$EXTRA_KCFLAGS"
        EXTRA_KCFLAGS="-I $LINUX/fs"
        LB_LINUX_TRY_COMPILE([
                #include <linux/kernel.h>
                #include <linux/fs.h>
                #include <quotaio_v2.h>
                struct v2r1_disk_dqblk dqblk_r1;
        ],[],[
                AC_DEFINE(HAVE_QUOTA64, 1, [have quota64])
                AC_MSG_RESULT([yes])
        ],[
                AC_MSG_RESULT([no])
                AC_MSG_WARN([4 TB (or larger) block quota limits can only be used with OSTs not larger than 4 TB.])
                AC_MSG_WARN([Continuing with limited quota support.])
                AC_MSG_WARN([quotacheck is needed for filesystems with recent quota versions.])
        ])
        EXTRA_KCFLAGS=$tmp_flags
])
fi
])

# LC_SECURITY_PLUG  # for SLES10 SP2
# check security plug in sles10 sp2 kernel
AC_DEFUN([LC_SECURITY_PLUG],
[AC_MSG_CHECKING([If kernel has security plug support])
LB_LINUX_TRY_COMPILE([
        #include <linux/fs.h>
],[
        struct dentry   *dentry;
        struct vfsmount *mnt;
        struct iattr    *iattr;

        notify_change(dentry, mnt, iattr);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_SECURITY_PLUG, 1,
                [SLES10 SP2 use extra parameter in vfs])
],[
        AC_MSG_RESULT(no)
])
])

AC_DEFUN([LC_PERCPU_COUNTER],
[AC_MSG_CHECKING([if have struct percpu_counter defined])
LB_LINUX_TRY_COMPILE([
        #include <linux/percpu_counter.h>
],[],[
        AC_DEFINE(HAVE_PERCPU_COUNTER, 1, [percpu_counter found])
        AC_MSG_RESULT([yes])

        AC_MSG_CHECKING([if percpu_counter_inc takes the 2nd argument])
        LB_LINUX_TRY_COMPILE([
                #include <linux/percpu_counter.h>
        ],[
                struct percpu_counter c;
                percpu_counter_init(&c, 0);
        ],[
                AC_DEFINE(HAVE_PERCPU_2ND_ARG, 1, [percpu_counter_init has two
                                                   arguments])
                AC_MSG_RESULT([yes])
        ],[
                AC_MSG_RESULT([no])
        ])
],[
        AC_MSG_RESULT([no])
])
])

#
# LC_CONFIGURE
#
# other configure checks
#
AC_DEFUN([LC_CONFIGURE],
[LC_CONFIG_OBD_BUFFER_SIZE

if test $target_cpu == "i686" -o $target_cpu == "x86_64"; then
        CFLAGS="$CFLAGS -Werror"
fi

# include/liblustre.h
AC_CHECK_HEADERS([asm/page.h sys/user.h sys/vfs.h stdint.h blkid/blkid.h])

# liblustre/llite_lib.h
AC_CHECK_HEADERS([xtio.h file.h])

# liblustre/dir.c
AC_CHECK_HEADERS([linux/types.h sys/types.h linux/unistd.h unistd.h])

# liblustre/lutil.c
AC_CHECK_HEADERS([netinet/in.h arpa/inet.h catamount/data.h])
AC_CHECK_FUNCS([inet_ntoa])

# libsysio/src/readlink.c
LC_READLINK_SSIZE_T

# lvfs/prng.c - depends on linux/types.h from liblustre/dir.c
AC_CHECK_HEADERS([linux/random.h], [], [],
                 [#ifdef HAVE_LINUX_TYPES_H
                  # include <linux/types.h>
                  #endif
                 ])

# utils/llverfs.c
AC_CHECK_HEADERS([ext2fs/ext2fs.h])

# check for -lz support
ZLIB=""
AC_CHECK_LIB([z],
             [adler32],
             [AC_CHECK_HEADERS([zlib.h],
                               [ZLIB="-lz"
                                AC_DEFINE([HAVE_ADLER], 1,
                                          [support alder32 checksum type])],
                               [AC_MSG_WARN([No zlib-devel package found,
                                             unable to use adler32 checksum])])],
             [AC_MSG_WARN([No zlib package found, unable to use adler32 checksum])]
)
AC_SUBST(ZLIB)

# Super safe df
AC_ARG_ENABLE([mindf],
      AC_HELP_STRING([--enable-mindf],
                      [Make statfs report the minimum available space on any single OST instead of the sum of free space on all OSTs]),
      [],[])
if test "$enable_mindf" = "yes" ;  then
      AC_DEFINE([MIN_DF], 1, [Report minimum OST free space])
fi

AC_ARG_ENABLE([fail_alloc],
        AC_HELP_STRING([--disable-fail-alloc],
                [disable randomly alloc failure]),
        [],[enable_fail_alloc=yes])
AC_MSG_CHECKING([whether to randomly failing memory alloc])
AC_MSG_RESULT([$enable_fail_alloc])
if test x$enable_fail_alloc != xno ; then
        AC_DEFINE([RANDOM_FAIL_ALLOC], 1, [enable randomly alloc failure])
fi

])

#
# LC_CONDITIONALS
#
# AM_CONDITIONALS for lustre
#
AC_DEFUN([LC_CONDITIONALS],
[AM_CONDITIONAL(LIBLUSTRE, test x$enable_liblustre = xyes)
AM_CONDITIONAL(USE_QUILT, test x$QUILT != xno)
AM_CONDITIONAL(LIBLUSTRE_TESTS, test x$enable_liblustre_tests = xyes)
AM_CONDITIONAL(MPITESTS, test x$enable_mpitests = xyes, Build MPI Tests)
AM_CONDITIONAL(CLIENT, test x$enable_client = xyes)
AM_CONDITIONAL(SERVER, test x$enable_server = xyes)
AM_CONDITIONAL(QUOTA, test x$enable_quota_module = xyes)
AM_CONDITIONAL(BLKID, test x$ac_cv_header_blkid_blkid_h = xyes)
AM_CONDITIONAL(EXT2FS_DEVEL, test x$ac_cv_header_ext2fs_ext2fs_h = xyes)
AM_CONDITIONAL(LIBPTHREAD, test x$enable_libpthread = xyes)
])

#
# LC_CONFIG_FILES
#
# files that should be generated with AC_OUTPUT
#
AC_DEFUN([LC_CONFIG_FILES],
[AC_CONFIG_FILES([
lustre/Makefile
lustre/autoMakefile
lustre/autoconf/Makefile
lustre/contrib/Makefile
lustre/doc/Makefile
lustre/include/Makefile
lustre/include/lustre_ver.h
lustre/include/linux/Makefile
lustre/include/lustre/Makefile
lustre/kernel_patches/targets/2.6-suse.target
lustre/kernel_patches/targets/2.6-vanilla.target
lustre/kernel_patches/targets/2.6-rhel4.target
lustre/kernel_patches/targets/2.6-rhel5.target
lustre/kernel_patches/targets/2.6-fc5.target
lustre/kernel_patches/targets/2.6-patchless.target
lustre/kernel_patches/targets/2.6-sles10.target
lustre/kernel_patches/targets/2.6-sles11.target
lustre/kernel_patches/targets/hp_pnnl-2.4.target
lustre/kernel_patches/targets/rh-2.4.target
lustre/kernel_patches/targets/rhel-2.4.target
lustre/kernel_patches/targets/suse-2.4.21-2.target
lustre/kernel_patches/targets/sles-2.4.target
lustre/ldlm/Makefile
lustre/liblustre/Makefile
lustre/liblustre/tests/Makefile
lustre/liblustre/tests/mpi/Makefile
lustre/llite/Makefile
lustre/llite/autoMakefile
lustre/lov/Makefile
lustre/lov/autoMakefile
lustre/lvfs/Makefile
lustre/lvfs/autoMakefile
lustre/mdc/Makefile
lustre/mdc/autoMakefile
lustre/mds/Makefile
lustre/mds/autoMakefile
lustre/obdclass/Makefile
lustre/obdclass/autoMakefile
lustre/obdclass/linux/Makefile
lustre/obdecho/Makefile
lustre/obdecho/autoMakefile
lustre/obdfilter/Makefile
lustre/obdfilter/autoMakefile
lustre/osc/Makefile
lustre/osc/autoMakefile
lustre/ost/Makefile
lustre/ost/autoMakefile
lustre/mgc/Makefile
lustre/mgc/autoMakefile
lustre/mgs/Makefile
lustre/mgs/autoMakefile
lustre/ptlrpc/Makefile
lustre/ptlrpc/autoMakefile
lustre/quota/Makefile
lustre/quota/autoMakefile
lustre/scripts/Makefile
lustre/tests/Makefile
lustre/tests/mpi/Makefile
lustre/utils/Makefile
])
case $lb_target_os in
        darwin)
                AC_CONFIG_FILES([ lustre/obdclass/darwin/Makefile ])
                ;;
esac

])

#
# LB_LINUX_VERSION
#
# Set things accordingly for a 2.5 kernel
#
AC_DEFUN([LB_LINUX_VERSION],
[LB_CHECK_FILE([$LINUX/include/linux/namei.h],
	[
        	linux25="yes"
		KMODEXT=".ko"
	],[
		KMODEXT=".o"
		linux25="no"
	])
AC_MSG_CHECKING([if you are using Linux 2.6])
AC_MSG_RESULT([$linux25])

MODULE_TARGET="SUBDIRS"
if test $linux25 = "yes" ; then
	makerule="$PWD/build"
	AC_MSG_CHECKING([for external module build support])
	rm -f build/conftest.i
	LB_LINUX_TRY_MAKE([],[],
		[$makerule LUSTRE_KERNEL_TEST=conftest.i],
		[test -s build/conftest.i],
		[
			AC_MSG_RESULT([no])
		],[
			makerule="_module_$makerule"
			MODULE_TARGET="M"
			LB_LINUX_TRY_MAKE([],[],
				[$makerule LUSTRE_KERNEL_TEST=conftest.i],
				[test -s build/conftest.i],
				[
					AC_MSG_RESULT([yes])
				],[
					AC_MSG_ERROR([unknown; check config.log for details])
				])
		])
else
	makerule="_dir_$PWD/build"
fi

AC_SUBST(MODULE_TARGET)
AC_SUBST(linux25)
AC_SUBST(KMODEXT)
])

#
# LB_LINUX_RELEASE
#
# get the release version of linux
#
AC_DEFUN([LB_LINUX_RELEASE],
[LINUXRELEASE=
rm -f build/conftest.i
AC_MSG_CHECKING([for Linux release])
if test -s $LINUX_OBJ/include/linux/utsrelease.h ; then
	LINUXRELEASEHEADER=utsrelease.h
else
	LINUXRELEASEHEADER=version.h
fi
LB_LINUX_TRY_MAKE([
	#include <linux/$LINUXRELEASEHEADER>
],[
	char *LINUXRELEASE;
	LINUXRELEASE=UTS_RELEASE;
],[
	$makerule LUSTRE_KERNEL_TEST=conftest.i
],[
	test -s build/conftest.i
],[
	# LINUXRELEASE="UTS_RELEASE"
	eval $(grep "LINUXRELEASE=" build/conftest.i)
],[
	AC_MSG_RESULT([unknown])
	AC_MSG_ERROR([Could not preprocess test program.  Consult config.log for details.])
])
rm -f build/conftest.i
if test x$LINUXRELEASE = x ; then
	AC_MSG_RESULT([unknown])
	AC_MSG_ERROR([Could not determine Linux release version from linux/version.h.])
fi
AC_MSG_RESULT([$LINUXRELEASE])
AC_SUBST(LINUXRELEASE)

moduledir='/lib/modules/'$LINUXRELEASE/kernel
AC_SUBST(moduledir)

modulefsdir='$(moduledir)/fs/$(PACKAGE)'
AC_SUBST(modulefsdir)

modulenetdir='$(moduledir)/net/$(PACKAGE)'
AC_SUBST(modulenetdir)

# ------------ RELEASE --------------------------------
AC_MSG_CHECKING([for Lustre release])
RELEASE="`echo ${LINUXRELEASE} | tr '-' '_'`_`date +%Y%m%d%H%M`"
AC_MSG_RESULT($RELEASE)
AC_SUBST(RELEASE)

# check is redhat/suse kernels
AC_MSG_CHECKING([that RedHat kernel])
LB_LINUX_TRY_COMPILE([
		#include <linux/version.h>
	],[
		#ifndef RHEL_RELEASE_CODE
		#error "not redhat kernel"
		#endif
	],[
		RHEL_KENEL="yes"
		RHEL_KERNEL="yes"
		AC_MSG_RESULT([yes])
	],[
	        AC_MSG_RESULT([no])
])

LB_LINUX_CONFIG([SUSE_KERNEL],[SUSE_KERNEL="yes"],[])

])

#
#
# LB_LINUX_PATH
#
# Find paths for linux, handling kernel-source rpms
#
AC_DEFUN([LB_LINUX_PATH],
[AC_MSG_CHECKING([for Linux sources])
AC_ARG_WITH([linux],
	AC_HELP_STRING([--with-linux=path],
		       [set path to Linux source (default=/usr/src/linux)]),
	[
		if ! [[[ $with_linux = /* ]]]; then
			AC_MSG_ERROR([You must provide an absolute pathname to the --with-linux= option.])
		else
			LINUX=$with_linux
		fi
	],
	[LINUX=/usr/src/linux])
AC_MSG_RESULT([$LINUX])
AC_SUBST(LINUX)

# -------- check for linux --------
LB_CHECK_FILE([$LINUX],[],
	[AC_MSG_ERROR([Kernel source $LINUX could not be found.])])

# -------- linux objects (for 2.6) --
AC_MSG_CHECKING([for Linux objects dir])
AC_ARG_WITH([linux-obj],
	AC_HELP_STRING([--with-linux-obj=path],
			[set path to Linux objects dir (default=$LINUX)]),
	[LINUX_OBJ=$with_linux_obj],
	[LINUX_OBJ=$LINUX])
AC_MSG_RESULT([$LINUX_OBJ])
AC_SUBST(LINUX_OBJ)

# -------- check for .config --------
AC_ARG_WITH([linux-config],
	[AC_HELP_STRING([--with-linux-config=path],
			[set path to Linux .conf (default=$LINUX_OBJ/.config)])],
	[LINUX_CONFIG=$with_linux_config],
	[LINUX_CONFIG=$LINUX_OBJ/.config])
AC_SUBST(LINUX_CONFIG)

LB_CHECK_FILE([/boot/kernel.h],
	[KERNEL_SOURCE_HEADER='/boot/kernel.h'],
	[LB_CHECK_FILE([/var/adm/running-kernel.h],
		[KERNEL_SOURCE_HEADER='/var/adm/running-kernel.h'])])

AC_ARG_WITH([kernel-source-header],
	AC_HELP_STRING([--with-kernel-source-header=path],
			[Use a different kernel version header.  Consult build/README.kernel-source for details.]),
	[KERNEL_SOURCE_HEADER=$with_kernel_source_header])

# ------------ .config exists ----------------
LB_CHECK_FILE([$LINUX_CONFIG],[],
	[AC_MSG_ERROR([Kernel config could not be found.  If you are building from a kernel-source rpm consult build/README.kernel-source])])

# ----------- make dep run? ------------------
# at 2.6.19 # $LINUX/include/linux/config.h is removed
# and at more old has only one line
# include <autoconf.h>
LB_CHECK_FILE([$LINUX_OBJ/include/linux/autoconf.h],[],
	[AC_MSG_ERROR([Run make config in $LINUX.])])
LB_CHECK_FILE([$LINUX_OBJ/include/linux/version.h],[],
	[AC_MSG_ERROR([Run make config in $LINUX.])])

# ------------ rhconfig.h includes runtime-generated bits --
# red hat kernel-source checks

# we know this exists after the check above.  if the user
# tarred up the tree and ran make dep etc. in it, then
# version.h gets overwritten with a standard linux one.

if grep rhconfig $LINUX_OBJ/include/linux/version.h >/dev/null ; then
	# This is a clean kernel-source tree, we need to
	# enable extensive workarounds to get this to build
	# modules
	LB_CHECK_FILE([$KERNEL_SOURCE_HEADER],
		[if test $KERNEL_SOURCE_HEADER = '/boot/kernel.h' ; then
			AC_MSG_WARN([Using /boot/kernel.h from RUNNING kernel.])
			AC_MSG_WARN([If this is not what you want, use --with-kernel-source-header.])
			AC_MSG_WARN([Consult build/README.kernel-source for details.])
		fi],
		[AC_MSG_ERROR([$KERNEL_SOURCE_HEADER not found.  Consult build/README.kernel-source for details.])])
	EXTRA_KCFLAGS="-include $KERNEL_SOURCE_HEADER $EXTRA_KCFLAGS"
fi

# this is needed before we can build modules
LB_LINUX_UML
LB_LINUX_VERSION

# --- check that we can build modules at all
AC_MSG_CHECKING([that modules can be built at all])
LB_LINUX_TRY_COMPILE([],[],[
	AC_MSG_RESULT([yes])
],[
	AC_MSG_RESULT([no])
	AC_MSG_WARN([Consult config.log for details.])
	AC_MSG_WARN([If you are trying to build with a kernel-source rpm, consult build/README.kernel-source])
	AC_MSG_ERROR([Kernel modules cannot be built.])
])

LB_LINUX_RELEASE
]) # end of LB_LINUX_PATH

# LB_LINUX_SYMVERFILE
# SLES 9 uses a different name for this file - unsure about vanilla kernels
# around this version, but it matters for servers only.
AC_DEFUN([LB_LINUX_SYMVERFILE],
	[AC_MSG_CHECKING([name of module symbol version file])
	if grep -q Modules.symvers $LINUX/scripts/Makefile.modpost ; then
		SYMVERFILE=Modules.symvers
	else
		SYMVERFILE=Module.symvers
	fi
	AC_MSG_RESULT($SYMVERFILE)
	AC_SUBST(SYMVERFILE)
])

#
#
# LB_LINUX_MODPOST
#
# Find modpost and check it
#
AC_DEFUN([LB_LINUX_MODPOST],
[
# Find the modpost utility
LB_CHECK_FILE([$LINUX_OBJ/scripts/mod/modpost],
	[MODPOST=$LINUX_OBJ/scripts/mod/modpost],
	[LB_CHECK_FILE([$LINUX_OBJ/scripts/modpost],
		[MODPOST=$LINUX_OBJ/scripts/modpost],
		AC_MSG_ERROR([modpost not found.])
	)]
)
AC_SUBST(MODPOST)

# Ensure it can run
AC_MSG_CHECKING([if modpost can be run])
if $MODPOST ; then
	AC_MSG_RESULT([yes])
else
	AC_MSG_ERROR([modpost can not be run.])
fi

# Check if modpost supports (and therefore requires) -m
AC_MSG_CHECKING([if modpost supports -m])
if $MODPOST -m 2>/dev/null ; then
	AC_MSG_RESULT([yes])
	MODPOST_ARGS=-m
else
	AC_MSG_RESULT([no])
	MODPOST_ARGS=""
fi
AC_SUBST(MODPOST_ARGS)
])

#
# LB_LINUX_UML
#
# check for a uml kernel
#
AC_DEFUN([LB_LINUX_UML],
[ARCH_UM=
UML_CFLAGS=

AC_MSG_CHECKING([if you are running user mode linux for $target_cpu])
if test -e $LINUX/include/asm-um ; then
	if test  X`ls -id $LINUX/include/asm/ 2>/dev/null | awk '{print [$]1}'` = X`ls -id $LINUX/include/asm-um 2>/dev/null | awk '{print [$]1}'` ; then
		ARCH_UM='ARCH=um'
		# see notes in Rules.in
		UML_CFLAGS='-O0'
		AC_MSG_RESULT(yes)
    	else
		AC_MSG_RESULT([no])
	fi
else
	AC_MSG_RESULT([no (asm-um missing)])
fi
AC_SUBST(ARCH_UM)
AC_SUBST(UML_CFLAGS)
])

# these are like AC_TRY_COMPILE, but try to build modules against the
# kernel, inside the build directory

#
# LB_LINUX_CONFTEST
#
# create a conftest.c file
#
AC_DEFUN([LB_LINUX_CONFTEST],
[cat >conftest.c <<_ACEOF
$1
_ACEOF
])


# LB_LANG_PROGRAM(C)([PROLOGUE], [BODY])
# --------------------------------------
m4_define([LB_LANG_PROGRAM],
[$1
int
main (void)
{
dnl Do *not* indent the following line: there may be CPP directives.
dnl Don't move the `;' right after for the same reason.
$2
  ;
  return 0;
}])

#
# LB_LINUX_COMPILE_IFELSE
#
# like AC_COMPILE_IFELSE
#
AC_DEFUN([LB_LINUX_COMPILE_IFELSE],
[m4_ifvaln([$1], [LB_LINUX_CONFTEST([$1])])dnl
rm -f build/conftest.o build/conftest.mod.c build/conftest.ko
AS_IF([AC_TRY_COMMAND(cp conftest.c build && make -d [$2] ${LD:+"LD=$LD"} CC="$CC" -f $PWD/build/Makefile LUSTRE_LINUX_CONFIG=$LINUX_CONFIG LINUXINCLUDE="$EXTRA_LNET_INCLUDE -I$LINUX/include -I$LINUX_OBJ/include -I$LINUX_OBJ/include2 -include include/linux/autoconf.h" -o tmp_include_depends -o scripts -o include/config/MARKER -C $LINUX_OBJ EXTRA_CFLAGS="-Werror-implicit-function-declaration $EXTRA_KCFLAGS" $ARCH_UM $MODULE_TARGET=$PWD/build) >/dev/null && AC_TRY_COMMAND([$3])],
	[$4],
	[_AC_MSG_LOG_CONFTEST
m4_ifvaln([$5],[$5])dnl])dnl
rm -f build/conftest.o build/conftest.mod.c build/conftest.mod.o build/conftest.ko m4_ifval([$1], [build/conftest.c conftest.c])[]dnl
])

#
# LB_LINUX_ARCH
#
# Determine the kernel's idea of the current architecture
#
AC_DEFUN([LB_LINUX_ARCH],
         [AC_MSG_CHECKING([Linux kernel architecture])
          AS_IF([rm -f $PWD/build/arch
                 make -s --no-print-directory echoarch -f $PWD/build/Makefile \
                     LUSTRE_LINUX_CONFIG=$LINUX_CONFIG -C $LINUX $ARCH_UM \
                     ARCHFILE=$PWD/build/arch && LINUX_ARCH=`cat $PWD/build/arch`],
                [AC_MSG_RESULT([$LINUX_ARCH])],
                [AC_MSG_ERROR([Could not determine the kernel architecture.])])
          rm -f build/arch])

#
# LB_LINUX_TRY_COMPILE
#
# like AC_TRY_COMPILE
#
AC_DEFUN([LB_LINUX_TRY_COMPILE],
[LB_LINUX_COMPILE_IFELSE(
 	[AC_LANG_SOURCE([LB_LANG_PROGRAM([[$1]], [[$2]])])],
	[modules],
	[test -s build/conftest.o],
	[$3], [$4])])

#
# LB_LINUX_CONFIG
#
# check if a given config option is defined
#
AC_DEFUN([LB_LINUX_CONFIG],
[AC_MSG_CHECKING([if Linux was built with CONFIG_$1])
LB_LINUX_TRY_COMPILE([
#include <linux/autoconf.h>
],[
#ifndef CONFIG_$1
#error CONFIG_$1 not #defined
#endif
],[
AC_MSG_RESULT([yes])
$2
],[
AC_MSG_RESULT([no])
$3
])
])

#
# LB_LINUX_CONFIG_IM
#
# check if a given config option is builtin or as module
#
AC_DEFUN([LB_LINUX_CONFIG_IM],
[AC_MSG_CHECKING([if Linux was built with CONFIG_$1 in or as module])
LB_LINUX_TRY_COMPILE([
#include <linux/autoconf.h>
],[
#if !(defined(CONFIG_$1) || defined(CONFIG_$1_MODULE))
#error CONFIG_$1 and CONFIG_$1_MODULE not #defined
#endif
],[
AC_MSG_RESULT([yes])
$2
],[
AC_MSG_RESULT([no])
$3
])
])

#
# LB_LINUX_TRY_MAKE
#
# like LB_LINUX_TRY_COMPILE, but with different arguments
#
AC_DEFUN([LB_LINUX_TRY_MAKE],
[LB_LINUX_COMPILE_IFELSE([AC_LANG_SOURCE([LB_LANG_PROGRAM([[$1]], [[$2]])])], [$3], [$4], [$5], [$6])])

#
# LB_LINUX_CONFIG_BIG_STACK
#
# check for big stack patch
#
AC_DEFUN([LB_LINUX_CONFIG_BIG_STACK],
[if test "x$ARCH_UM" = "x" -a "x$linux25" = "xno" ; then
	case $target_cpu in
		i?86 | x86_64)
			LB_LINUX_CONFIG([STACK_SIZE_16KB],[],[
				LB_LINUX_CONFIG([STACK_SIZE_32KB],[],[
					LB_LINUX_CONFIG([STACK_SIZE_64KB],[],[
						AC_MSG_ERROR([Lustre requires that Linux is configured with at least a 16KB stack.])
					])
				])
			])
			;;
	esac
fi
])

#
# LB_CONFIG_OFED_BACKPORTS
#
# include any OFED backport headers in all compile commands
# NOTE: this does only include the backport paths, not the OFED headers
#       adding the OFED headers is done in the lnet portion
AC_DEFUN([LB_CONFIG_OFED_BACKPORTS],
[AC_MSG_CHECKING([whether to use any OFED backport headers])
# set default
AC_ARG_WITH([o2ib],
	AC_HELP_STRING([--with-o2ib=path],
	               [build o2iblnd against path]),
	[
		case $with_o2ib in
		yes)    O2IBPATHS="$LINUX $LINUX/drivers/infiniband"
			ENABLEO2IB=2
			;;
		no)     ENABLEO2IB=0
			;;
		*)      O2IBPATHS=$with_o2ib
			ENABLEO2IB=3
			;;
		esac
	],[
		O2IBPATHS="$LINUX $LINUX/drivers/infiniband"
		ENABLEO2IB=1
	])
if test $ENABLEO2IB -eq 0; then
	AC_MSG_RESULT([no])
else
	o2ib_found=false
	for O2IBPATH in $O2IBPATHS; do
		if test \( -f ${O2IBPATH}/include/rdma/rdma_cm.h -a \
			   -f ${O2IBPATH}/include/rdma/ib_cm.h -a \
			   -f ${O2IBPATH}/include/rdma/ib_verbs.h -a \
			   -f ${O2IBPATH}/include/rdma/ib_fmr_pool.h \); then
			o2ib_found=true
			break
		fi
	done
	if ! $o2ib_found; then
		AC_MSG_RESULT([no])
		case $ENABLEO2IB in
			1) ;;
			2) AC_MSG_ERROR([kernel OpenIB gen2 headers not present]);;
			3) AC_MSG_ERROR([bad --with-o2ib path]);;
			*) AC_MSG_ERROR([internal error]);;
		esac
	else
                if test -f $O2IBPATH/config.mk; then
			. $O2IBPATH/config.mk
                elif test -f $O2IBPATH/ofed_patch.mk; then
			. $O2IBPATH/ofed_patch.mk
		fi
		if test -n "$BACKPORT_INCLUDES"; then
			OFED_BACKPORT_PATH=`echo $BACKPORT_INCLUDES | sed "s#.*/src/ofa_kernel/#$O2IBPATH/#"`
			EXTRA_LNET_INCLUDE="-I$OFED_BACKPORT_PATH $EXTRA_LNET_INCLUDE"
			AC_MSG_RESULT([yes])
		else
			AC_MSG_RESULT([no])
                fi
	fi
fi
])


#
# LB_PROG_LINUX
#
# linux tests
#
AC_DEFUN([LB_PROG_LINUX],
[LB_LINUX_PATH
LB_LINUX_ARCH
LB_LINUX_SYMVERFILE


LB_LINUX_CONFIG([MODULES],[],[
	AC_MSG_ERROR([module support is required to build Lustre kernel modules.])
])

LB_LINUX_CONFIG([MODVERSIONS])

LB_LINUX_CONFIG([KALLSYMS],[],[
if test "x$ARCH_UM" = "x" ; then
	AC_MSG_ERROR([Lustre requires that CONFIG_KALLSYMS is enabled in your kernel.])
fi
])

LB_LINUX_CONFIG([KMOD],[],[
	AC_MSG_WARN([])
	AC_MSG_WARN([Kernel module loading support is highly recommended.])
	AC_MSG_WARN([])
])

#LB_LINUX_CONFIG_BIG_STACK

# it's ugly to be doing anything with OFED outside of the lnet module, but
# this has to be done here so that the backports path is set before all of
# the LN_PROG_LINUX checks are done
LB_CONFIG_OFED_BACKPORTS
])

#
# LB_LINUX_CONDITIONALS
#
# AM_CONDITIONALS for linux
#
AC_DEFUN([LB_LINUX_CONDITIONALS],
[AM_CONDITIONAL(LINUX25, test x$linux25 = xyes)
])


#
# LB_CHECK_SYMBOL_EXPORT
# check symbol exported or not
# $1 - symbol
# $2 - file(s) for find.
# $3 - do 'yes'
# $4 - do 'no'
#
# 2.6 based kernels - put modversion info into $LINUX/Module.modvers
# or check
AC_DEFUN([LB_CHECK_SYMBOL_EXPORT],
[AC_MSG_CHECKING([if Linux was built with symbol $1 exported])
grep -q -E '[[[:space:]]]$1[[[:space:]]]' $LINUX/$SYMVERFILE 2>/dev/null
rc=$?
if test $rc -ne 0; then
    export=0
    for file in $2; do
    	grep -q -E "EXPORT_SYMBOL.*\($1\)" "$LINUX/$file" 2>/dev/null
    	rc=$?
	if test $rc -eq 0; then
		export=1
		break;
	fi
    done
    if test $export -eq 0; then
    	AC_MSG_RESULT([no])
    	$4
    else
    	AC_MSG_RESULT([yes])
    	$3
    fi
else
    AC_MSG_RESULT([yes])
    $3
fi
])

#
# Like AC_CHECK_HEADER but checks for a kernel-space header
#
m4_define([LB_CHECK_LINUX_HEADER],
[AS_VAR_PUSHDEF([ac_Header], [ac_cv_header_$1])dnl
AC_CACHE_CHECK([for $1], ac_Header,
	       [LB_LINUX_COMPILE_IFELSE([LB_LANG_PROGRAM([@%:@include <$1>])],
				  [modules],
				  [test -s build/conftest.o],
				  [AS_VAR_SET(ac_Header, [yes])],
				  [AS_VAR_SET(ac_Header, [no])])])
AS_IF([test AS_VAR_GET(ac_Header) = yes], [$2], [$3])[]dnl
AS_VAR_POPDEF([ac_Header])dnl
])

#
# LN_CONFIG_MAX_PAYLOAD
#
# configure maximum payload
#
AC_DEFUN([LN_CONFIG_MAX_PAYLOAD],
[AC_MSG_CHECKING([for non-default maximum LNET payload])
AC_ARG_WITH([max-payload-mb],
	AC_HELP_STRING([--with-max-payload-mb=MBytes],
                       [set maximum lnet payload in MBytes]),
        [
		AC_MSG_RESULT([$with_max_payload_mb])
	        LNET_MAX_PAYLOAD_MB=$with_max_payload_mb
		LNET_MAX_PAYLOAD="(($with_max_payload_mb)<<20)"
	], [
		AC_MSG_RESULT([no])
		LNET_MAX_PAYLOAD="LNET_MTU"
	])
        AC_DEFINE_UNQUOTED(LNET_MAX_PAYLOAD, $LNET_MAX_PAYLOAD,
			   [Max LNET payload])
])

#
# LN_CHECK_GCC_VERSION
#
# Check compiler version
#
AC_DEFUN([LN_CHECK_GCC_VERSION],
[AC_MSG_CHECKING([compiler version])
PTL_CC_VERSION=`$CC --version | awk '/^gcc/{print $ 3}'`
PTL_MIN_CC_VERSION="3.2.2"
v2n() {
	awk -F. '{printf "%d\n", (($ 1)*100+($ 2))*100+($ 3)}'
}
if test -z "$PTL_CC_VERSION" -o \
        `echo $PTL_CC_VERSION | v2n` -ge `echo $PTL_MIN_CC_VERSION | v2n`; then
	AC_MSG_RESULT([ok])
else
	AC_MSG_RESULT([Buggy compiler found])
	AC_MSG_ERROR([Need gcc version >= $PTL_MIN_CC_VERSION])
fi
])

#
# LN_CONFIG_CDEBUG
#
# whether to enable various libcfs debugs (CDEBUG, ENTRY/EXIT, LASSERT, etc.)
#
AC_DEFUN([LN_CONFIG_CDEBUG],
[
AC_MSG_CHECKING([whether to enable CDEBUG, CWARN])
AC_ARG_ENABLE([libcfs_cdebug],
	AC_HELP_STRING([--disable-libcfs-cdebug],
			[disable libcfs CDEBUG, CWARN]),
	[],[enable_libcfs_cdebug='yes'])
AC_MSG_RESULT([$enable_libcfs_cdebug])
if test x$enable_libcfs_cdebug = xyes; then
   AC_DEFINE(CDEBUG_ENABLED, 1, [enable libcfs CDEBUG, CWARN])
else
   AC_DEFINE(CDEBUG_ENABLED, 0, [disable libcfs CDEBUG, CWARN])
fi

AC_MSG_CHECKING([whether to enable ENTRY/EXIT])
AC_ARG_ENABLE([libcfs_trace],
	AC_HELP_STRING([--disable-libcfs-trace],
			[disable libcfs ENTRY/EXIT]),
	[],[enable_libcfs_trace='yes'])
AC_MSG_RESULT([$enable_libcfs_trace])
if test x$enable_libcfs_trace = xyes; then
   AC_DEFINE(CDEBUG_ENTRY_EXIT, 1, [enable libcfs ENTRY/EXIT])
else
   AC_DEFINE(CDEBUG_ENTRY_EXIT, 0, [disable libcfs ENTRY/EXIT])
fi

AC_MSG_CHECKING([whether to enable LASSERT, LASSERTF])
AC_ARG_ENABLE([libcfs_assert],
	AC_HELP_STRING([--disable-libcfs-assert],
			[disable libcfs LASSERT, LASSERTF]),
	[],[enable_libcfs_assert='yes'])
AC_MSG_RESULT([$enable_libcfs_assert])
if test x$enable_libcfs_assert = xyes; then
   AC_DEFINE(LIBCFS_DEBUG, 1, [enable libcfs LASSERT, LASSERTF])
fi
])

#
# LN_CONFIG_AFFINITY
#
# check if cpu affinity is available/wanted
#
AC_DEFUN([LN_CONFIG_AFFINITY],
[AC_ARG_ENABLE([affinity],
	AC_HELP_STRING([--disable-affinity],
		       [disable process/irq affinity]),
	[],[enable_affinity='yes'])

AC_MSG_CHECKING([for CPU affinity support])
if test x$enable_affinity = xno ; then
	AC_MSG_RESULT([no (by request)])
else
	LB_LINUX_TRY_COMPILE([
		#include <linux/sched.h>
	],[
		struct task_struct t;
		#if HAVE_CPUMASK_T
		cpumask_t     m;
	        #else
	        unsigned long m;
		#endif
		set_cpus_allowed(&t, m);
	],[
		AC_DEFINE(CPU_AFFINITY, 1, [kernel has cpu affinity support])
		AC_MSG_RESULT([yes])
	],[
		AC_MSG_RESULT([no (no kernel support)])
	])
fi
])

#
# LN_CONFIG_PORTALS
#
# configure support for Portals
#
AC_DEFUN([LN_CONFIG_PORTALS],
[AC_MSG_CHECKING([for portals])
AC_ARG_WITH([portals],
	AC_HELP_STRING([--with-portals=path],
                       [set path to portals]),
        [
		case $with_portals in
			no)     ENABLEPORTALS=0
				;;
			*)	PORTALS="${with_portals}"
				ENABLEPORTALS=1
				;;
		esac
	], [
		ENABLEPORTALS=0
	])
PTLLNDCPPFLAGS=""
if test $ENABLEPORTALS -eq 0; then
	AC_MSG_RESULT([no])
elif test ! \( -f ${PORTALS}/include/portals/p30.h \); then
        AC_MSG_RESULT([no])
	AC_MSG_ERROR([bad --with-portals path])
else
        AC_MSG_RESULT([$PORTALS])
        PTLLNDCPPFLAGS="-I${PORTALS}/include"
fi
AC_SUBST(PTLLNDCPPFLAGS)
])

#
# LN_CONFIG_BACKOFF
#
# check if tunable tcp backoff is available/wanted
#
AC_DEFUN([LN_CONFIG_BACKOFF],
[AC_MSG_CHECKING([for tunable backoff TCP support])
AC_ARG_ENABLE([backoff],
       AC_HELP_STRING([--disable-backoff],
                      [disable socknal tunable backoff]),
       [],[enable_backoff='yes'])
if test x$enable_backoff = xno ; then
       AC_MSG_RESULT([no (by request)])
else
       BOCD="`grep -c TCP_BACKOFF $LINUX/include/linux/tcp.h`"
       if test "$BOCD" != 0 ; then
               AC_DEFINE(SOCKNAL_BACKOFF, 1, [use tunable backoff TCP])
               AC_MSG_RESULT(yes)
               if grep rto_max $LINUX/include/linux/tcp.h|grep -q __u16; then
                   AC_DEFINE(SOCKNAL_BACKOFF_MS, 1, [tunable backoff TCP in ms])
               fi
       else
               AC_MSG_RESULT([no (no kernel support)])
       fi
fi
])

#
# LN_CONFIG_PANIC_DUMPLOG
#
# check if tunable panic_dumplog is wanted
#
AC_DEFUN([LN_CONFIG_PANIC_DUMPLOG],
[AC_MSG_CHECKING([for tunable panic_dumplog support])
AC_ARG_ENABLE([panic_dumplog],
       AC_HELP_STRING([--enable-panic_dumplog],
                      [enable panic_dumplog]),
       [],[enable_panic_dumplog='no'])
if test x$enable_panic_dumplog = xyes ; then
       AC_DEFINE(LNET_DUMP_ON_PANIC, 1, [use dumplog on panic])
       AC_MSG_RESULT([yes (by request)])
else
       AC_MSG_RESULT([no])
fi
])

#
# LN_CONFIG_PTLLND
#
# configure support for Portals LND
#
AC_DEFUN([LN_CONFIG_PTLLND],
[
if test -z "$ENABLEPORTALS"; then
	LN_CONFIG_PORTALS
fi

AC_MSG_CHECKING([whether to build the kernel portals LND])

PTLLND=""
if test $ENABLEPORTALS -ne 0; then
	AC_MSG_RESULT([yes])
	PTLLND="ptllnd"
else
	AC_MSG_RESULT([no])
fi
AC_SUBST(PTLLND)
])

#
# LN_CONFIG_UPTLLND
#
# configure support for Portals LND
#
AC_DEFUN([LN_CONFIG_UPTLLND],
[
if test -z "$ENABLEPORTALS"; then
	LN_CONFIG_PORTALS
fi

AC_MSG_CHECKING([whether to build the userspace portals LND])

UPTLLND=""
if test $ENABLEPORTALS -ne 0; then
	AC_MSG_RESULT([yes])
	UPTLLND="ptllnd"
else
	AC_MSG_RESULT([no])
fi
AC_SUBST(UPTLLND)
])

#
# LN_CONFIG_USOCKLND
#
# configure support for userspace TCP/IP LND
#
AC_DEFUN([LN_CONFIG_USOCKLND],
[AC_MSG_CHECKING([whether to build usocklnd])
AC_ARG_ENABLE([usocklnd],
       	AC_HELP_STRING([--disable-usocklnd],
                      	[disable usocklnd]),
       	[],[enable_usocklnd='yes'])

if test x$enable_usocklnd = xyes ; then
	if test "$ENABLE_LIBPTHREAD" = "yes" ; then
		AC_MSG_RESULT([yes])
      		USOCKLND="usocklnd"
	else
		AC_MSG_RESULT([no (libpthread not present or disabled)])
		USOCKLND=""
	fi
else
	AC_MSG_RESULT([no (disabled explicitly)])
     	USOCKLND=""
fi
AC_SUBST(USOCKLND)
])

#
# LN_CONFIG_QUADRICS
#
# check if quadrics support is in this kernel
#
AC_DEFUN([LN_CONFIG_QUADRICS],
[AC_MSG_CHECKING([for QsNet sources])
AC_ARG_WITH([qsnet],
	AC_HELP_STRING([--with-qsnet=path],
		       [set path to qsnet source (default=$LINUX)]),
	[QSNET=$with_qsnet],
	[QSNET=$LINUX])
AC_MSG_RESULT([$QSNET])

AC_MSG_CHECKING([if quadrics kernel headers are present])
if test -d $QSNET/drivers/net/qsnet ; then
	AC_MSG_RESULT([yes])
	QSWLND="qswlnd"
	AC_MSG_CHECKING([for multirail EKC])
	if test -f $QSNET/include/elan/epcomms.h; then
		AC_MSG_RESULT([supported])
		QSWCPPFLAGS="-I$QSNET/include -DMULTIRAIL_EKC=1"
	else
		AC_MSG_RESULT([not supported])
		AC_MSG_ERROR([Need multirail EKC])
	fi

	if test x$QSNET = x$LINUX ; then
		LB_LINUX_CONFIG([QSNET],[],[
			LB_LINUX_CONFIG([QSNET_MODULE],[],[
				AC_MSG_WARN([QSNET is not enabled in this kernel; not building qswlnd.])
				QSWLND=""
				QSWCPPFLAGS=""
			])
		])
	fi
else
	AC_MSG_RESULT([no])
	QSWLND=""
	QSWCPPFLAGS=""
fi
AC_SUBST(QSWCPPFLAGS)
AC_SUBST(QSWLND)
])

#
# LN_CONFIG_GM
#
# check if GM support is available
#
AC_DEFUN([LN_CONFIG_GM],[
AC_MSG_CHECKING([whether to enable GM support])
AC_ARG_WITH([gm],
        AC_HELP_STRING([--with-gm=path-to-gm-source-tree],
	               [build gmlnd against path]),
	[
	        case $with_gm in
                no)    ENABLE_GM=0
	               ;;
                *)     ENABLE_GM=1
                       GM_SRC="$with_gm"
		       ;;
                esac
        ],[
                ENABLE_GM=0
        ])
AC_ARG_WITH([gm-install],
        AC_HELP_STRING([--with-gm-install=path-to-gm-install-tree],
	               [say where GM has been installed]),
	[
	        GM_INSTALL=$with_gm_install
        ],[
                GM_INSTALL="/opt/gm"
        ])
if test $ENABLE_GM -eq 0; then
        AC_MSG_RESULT([no])
else
        AC_MSG_RESULT([yes])

	GMLND="gmlnd"
        GMCPPFLAGS="-I$GM_SRC/include -I$GM_SRC/drivers -I$GM_SRC/drivers/linux/gm"

	if test -f $GM_INSTALL/lib/libgm.a -o \
                -f $GM_INSTALL/lib64/libgm.a; then
	        GMLIBS="-L$GM_INSTALL/lib -L$GM_INSTALL/lib64"
        else
	        AC_MSG_ERROR([Cant find GM libraries under $GM_INSTALL])
        fi

	EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
	EXTRA_KCFLAGS="$GMCPPFLAGS -DGM_KERNEL $EXTRA_KCFLAGS"

        AC_MSG_CHECKING([that code using GM compiles with given path])
	LB_LINUX_TRY_COMPILE([
		#define GM_STRONG_TYPES 1
		#ifdef VERSION
		#undef VERSION
		#endif
	        #include "gm.h"
		#include "gm_internal.h"
        ],[
	        struct gm_port *port = NULL;
		gm_recv_event_t *rxevent = gm_blocking_receive_no_spin(port);
                return 0;
        ],[
		AC_MSG_RESULT([yes])
        ],[
		AC_MSG_RESULT([no])
		AC_MSG_ERROR([Bad --with-gm path])
        ])

	AC_MSG_CHECKING([that GM has gm_register_memory_ex_phys()])
	LB_LINUX_TRY_COMPILE([
		#define GM_STRONG_TYPES 1
		#ifdef VERSION
		#undef VERSION
		#endif
	        #include "gm.h"
		#include "gm_internal.h"
	],[
		gm_status_t     gmrc;
		struct gm_port *port = NULL;
		gm_u64_t        phys = 0;
		gm_up_t         pvma = 0;

		gmrc = gm_register_memory_ex_phys(port, phys, 100, pvma);
		return 0;
	],[
		AC_MSG_RESULT([yes])
	],[
		AC_MSG_RESULT([no.
Please patch the GM sources as follows...
    cd $GM_SRC
    patch -p0 < $PWD/lnet/klnds/gmlnd/gm-reg-phys.patch
...then rebuild and re-install them])
                AC_MSG_ERROR([Can't build GM without gm_register_memory_ex_phys()])
        ])

	EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
fi
AC_SUBST(GMCPPFLAGS)
AC_SUBST(GMLIBS)
AC_SUBST(GMLND)
])


#
# LN_CONFIG_MX
#
AC_DEFUN([LN_CONFIG_MX],
[AC_MSG_CHECKING([whether to enable Myrinet MX support])
# set default
MXPATH="/opt/mx"
AC_ARG_WITH([mx],
       AC_HELP_STRING([--with-mx=path],
                      [build mxlnd against path]),
       [
               case $with_mx in
               yes)    ENABLEMX=2
                       ;;
               no)     ENABLEMX=0
                       ;;
               *)      MXPATH=$with_mx
                       ENABLEMX=3
                       ;;
               esac
       ],[
               ENABLEMX=1
       ])
if test $ENABLEMX -eq 0; then
       AC_MSG_RESULT([disabled])
elif test ! \( -f ${MXPATH}/include/myriexpress.h -a \
              -f ${MXPATH}/include/mx_kernel_api.h -a \
              -f ${MXPATH}/include/mx_pin.h \); then
       AC_MSG_RESULT([no])
       case $ENABLEMX in
       1) ;;
       2) AC_MSG_ERROR([Myrinet MX kernel headers not present]);;
       3) AC_MSG_ERROR([bad --with-mx path]);;
       *) AC_MSG_ERROR([internal error]);;
       esac
else
       MXCPPFLAGS="-I$MXPATH/include"
       EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
       EXTRA_KCFLAGS="$EXTRA_KCFLAGS $MXCPPFLAGS"
       MXLIBS="-L$MXPATH/lib"
       LB_LINUX_TRY_COMPILE([
               #define MX_KERNEL 1
               #include <mx_extensions.h>
               #include <myriexpress.h>
       ],[
               mx_endpoint_t   end;
               mx_status_t     status;
               mx_request_t    request;
               int             result;

               mx_init();
               mx_open_endpoint(MX_ANY_NIC, MX_ANY_ENDPOINT, 0, NULL, 0, &end);
	       mx_register_unexp_handler(end, (mx_unexp_handler_t) NULL, NULL);
               mx_wait_any(end, MX_INFINITE, 0LL, 0LL, &status, &result);
               mx_iconnect(end, 0LL, 0, 0, 0, NULL, &request);
               return 0;
       ],[
               AC_MSG_RESULT([yes])
               MXLND="mxlnd"
       ],[
               AC_MSG_RESULT([no])
               case $ENABLEMX in
               1) ;;
               2) AC_MSG_ERROR([can't compile with Myrinet MX kernel headers]);;
               3) AC_MSG_ERROR([can't compile with Myrinet MX headers under $MXPATH]);;
               *) AC_MSG_ERROR([internal error]);;
               esac
               MXLND=""
               MXCPPFLAGS=""
       ])
       EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
fi
AC_SUBST(MXCPPFLAGS)
AC_SUBST(MXLIBS)
AC_SUBST(MXLND)
])



#
# LN_CONFIG_O2IB
#
AC_DEFUN([LN_CONFIG_O2IB],[
AC_MSG_CHECKING([whether to enable OpenIB gen2 support])
# set default
AC_ARG_WITH([o2ib],
	AC_HELP_STRING([--with-o2ib=path],
	               [build o2iblnd against path]),
	[
		case $with_o2ib in
		yes)    O2IBPATHS="$LINUX $LINUX/drivers/infiniband"
			ENABLEO2IB=2
			;;
		no)     ENABLEO2IB=0
			;;
		*)      O2IBPATHS=$with_o2ib
			ENABLEO2IB=3
			;;
		esac
	],[
		O2IBPATHS="$LINUX $LINUX/drivers/infiniband"
		ENABLEO2IB=1
	])
if test $ENABLEO2IB -eq 0; then
	AC_MSG_RESULT([disabled])
else
	o2ib_found=false

	for O2IBPATH in $O2IBPATHS; do
		if test \( -f ${O2IBPATH}/include/rdma/rdma_cm.h -a \
			   -f ${O2IBPATH}/include/rdma/ib_cm.h -a \
			   -f ${O2IBPATH}/include/rdma/ib_verbs.h -a \
			   -f ${O2IBPATH}/include/rdma/ib_fmr_pool.h \); then
			o2ib_found=true
			break
		fi
	done

	if ! $o2ib_found; then
		AC_MSG_RESULT([no])
		case $ENABLEO2IB in
			1) ;;
			2) AC_MSG_ERROR([kernel OpenIB gen2 headers not present]);;
			3) AC_MSG_ERROR([bad --with-o2ib path]);;
			*) AC_MSG_ERROR([internal error]);;
		esac
	else
		O2IBCPPFLAGS="-I$O2IBPATH/include"
		EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
		EXTRA_KCFLAGS="$EXTRA_KCFLAGS $O2IBCPPFLAGS"
		EXTRA_LNET_INCLUDE="$EXTRA_LNET_INCLUDE $O2IBCPPFLAGS"

		LB_LINUX_TRY_COMPILE([
		        #include <linux/version.h>
		        #include <linux/pci.h>
		        #if !HAVE_GFP_T
		        typedef int gfp_t;
		        #endif
		        #include <rdma/rdma_cm.h>
		        #include <rdma/ib_cm.h>
		        #include <rdma/ib_verbs.h>
		        #include <rdma/ib_fmr_pool.h>
		],[
		        struct rdma_cm_id          *cm_id;
		        struct rdma_conn_param      conn_param;
		        struct ib_device_attr       device_attr;
		        struct ib_qp_attr           qp_attr;
		        struct ib_pool_fmr          pool_fmr;
		        enum   ib_cm_rej_reason     rej_reason;

		        cm_id = rdma_create_id(NULL, NULL, RDMA_PS_TCP);
		        return PTR_ERR(cm_id);
		],[
		        AC_MSG_RESULT([yes])
		        O2IBLND="o2iblnd"
		],[
		        AC_MSG_RESULT([no])
		        case $ENABLEO2IB in
		        1) ;;
		        2) AC_MSG_ERROR([can't compile with kernel OpenIB gen2 headers]);;
		        3) AC_MSG_ERROR([can't compile with OpenIB gen2 headers under $O2IBPATH]);;
		        *) AC_MSG_ERROR([internal error]);;
		        esac
		        O2IBLND=""
		        O2IBCPPFLAGS=""
		])
		# we know at this point that the found OFED source is good
		O2IB_SYMVER=""
		if test $ENABLEO2IB -eq 3 ; then
			# OFED default rpm not handle sles10 Modules.symvers name
			for name in Module.symvers Modules.symvers; do
				if test -f $O2IBPATH/$name; then
					O2IB_SYMVER=$name;
					break;
				fi
			done
			if test -n "$O2IB_SYMVER"; then
				AC_MSG_NOTICE([adding $O2IBPATH/Module.symvers to $PWD/$SYMVERFILE])
				# strip out the existing symbols versions first
				if test -f $PWD/$SYMVERFILE; then
				    egrep -v $(echo $(awk '{ print $2 }' $O2IBPATH/$O2IB_SYMVER) | tr ' ' '|') $PWD/$SYMVERFILE > $PWD/$SYMVERFILE.old
				else
				    touch $PWD/$SYMVERFILE.old
				fi
				cat $PWD/$SYMVERFILE.old $O2IBPATH/$O2IB_SYMVER > $PWD/$SYMVERFILE
				rm $PWD/$SYMVERFILE.old
			else
				AC_MSG_ERROR([an external source tree was specified for o2iblnd however I could not find a $O2IBPATH/Module.symvers there])
			fi
		fi

		LN_CONFIG_OFED_SPEC
		EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
	fi
fi

AC_SUBST(EXTRA_LNET_INCLUDE)
AC_SUBST(O2IBCPPFLAGS)
AC_SUBST(O2IBLND)
])

#
# LN_CONFIG_OPENIB
#
# check for OpenIB in the kernel
AC_DEFUN([LN_CONFIG_OPENIB],[
AC_MSG_CHECKING([whether to enable OpenIB support])
# set default
OPENIBPATH="$LINUX/drivers/infiniband"
AC_ARG_WITH([openib],
	AC_HELP_STRING([--with-openib=path],
	               [build openiblnd against path]),
	[
		case $with_openib in
		yes)    ENABLEOPENIB=2
			;;
		no)     ENABLEOPENIB=0
			;;
		*)      OPENIBPATH="$with_openib"
			ENABLEOPENIB=3
			;;
		esac
	],[
		ENABLEOPENIB=1
	])
if test $ENABLEOPENIB -eq 0; then
	AC_MSG_RESULT([disabled])
elif test ! \( -f ${OPENIBPATH}/include/ts_ib_core.h -a \
               -f ${OPENIBPATH}/include/ts_ib_cm.h -a \
	       -f ${OPENIBPATH}/include/ts_ib_sa_client.h \); then
	AC_MSG_RESULT([no])
	case $ENABLEOPENIB in
	1) ;;
	2) AC_MSG_ERROR([kernel OpenIB headers not present]);;
	3) AC_MSG_ERROR([bad --with-openib path]);;
	*) AC_MSG_ERROR([internal error]);;
	esac
else
	case $ENABLEOPENIB in
	1|2) OPENIBCPPFLAGS="-I$OPENIBPATH/include -DIN_TREE_BUILD";;
	3)   OPENIBCPPFLAGS="-I$OPENIBPATH/include";;
	*)   AC_MSG_RESULT([no])
	     AC_MSG_ERROR([internal error]);;
	esac
	OPENIBCPPFLAGS="$OPENIBCPPFLAGS -DIB_NTXRXPARAMS=4"
	EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS $OPENIBCPPFLAGS"
	LB_LINUX_TRY_COMPILE([
		#include <ts_ib_core.h>
		#include <ts_ib_cm.h>
	        #include <ts_ib_sa_client.h>
	],[
	        struct ib_device_properties dev_props;
	        struct ib_cm_active_param   cm_active_params;
	        tTS_IB_CLIENT_QUERY_TID     tid;
	        int                         enum1 = IB_QP_ATTRIBUTE_STATE;
		int                         enum2 = IB_ACCESS_LOCAL_WRITE;
		int                         enum3 = IB_CQ_CALLBACK_INTERRUPT;
		int                         enum4 = IB_CQ_PROVIDER_REARM;
		return 0;
	],[
		AC_MSG_RESULT([yes])
		OPENIBLND="openiblnd"
	],[
		AC_MSG_RESULT([no])
		case $ENABLEOPENIB in
		1) ;;
		2) AC_MSG_ERROR([can't compile with kernel OpenIB headers]);;
		3) AC_MSG_ERROR([can't compile with OpenIB headers under $OPENIBPATH]);;
		*) AC_MSG_ERROR([internal error]);;
		esac
		OPENIBLND=""
		OPENIBCPPFLAGS=""
	])
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
fi
AC_SUBST(OPENIBCPPFLAGS)
AC_SUBST(OPENIBLND)
])

#
# LN_CONFIG_CIBLND
#
AC_DEFUN([LN_CONFIG_CIB],[
AC_MSG_CHECKING([whether to enable Cisco/TopSpin IB support])
# set default
CIBPATH=""
CIBLND=""
AC_ARG_WITH([cib],
	AC_HELP_STRING([--with-cib=path],
	               [build ciblnd against path]),
	[
		case $with_cib in
		no)     AC_MSG_RESULT([no]);;
		*)      CIBPATH="$with_cib"
	                if test -d "$CIBPATH"; then
	                 	AC_MSG_RESULT([yes])
                        else
				AC_MSG_RESULT([no])
				AC_MSG_ERROR([No directory $CIBPATH])
			fi;;
		esac
	],[
		AC_MSG_RESULT([no])
	])
if test -n "$CIBPATH"; then
	CIBCPPFLAGS="-I${CIBPATH}/ib/ts_api_ng/include -I${CIBPATH}/all/kernel_services/include -DUSING_TSAPI"
	CIBCPPFLAGS="$CIBCPPFLAGS -DIB_NTXRXPARAMS=3"
	EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS $CIBCPPFLAGS"
	LB_LINUX_TRY_COMPILE([
		#include <ts_ib_core.h>
		#include <ts_ib_cm.h>
	        #include <ts_ib_sa_client.h>
	],[
	        struct ib_device_properties dev_props;
	        struct ib_cm_active_param   cm_active_params;
	        tTS_IB_CLIENT_QUERY_TID     tid;
	        int                         enum1 = TS_IB_QP_ATTRIBUTE_STATE;
		int                         enum2 = TS_IB_ACCESS_LOCAL_WRITE;
		int                         enum3 = TS_IB_CQ_CALLBACK_INTERRUPT;
		int                         enum4 = TS_IB_CQ_PROVIDER_REARM;
		return 0;
	],[
		CIBLND="ciblnd"
	],[
		AC_MSG_ERROR([can't compile ciblnd with given path])
	        CIBCPPFLAGS=""
	])
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
fi
AC_SUBST(CIBCPPFLAGS)
AC_SUBST(CIBLND)
])

#
# LN_CONFIG_IIB
#
# check for infinicon infiniband support
#
AC_DEFUN([LN_CONFIG_IIB],[
AC_MSG_CHECKING([whether to enable Infinicon support])
# set default
IIBPATH="/usr/include"
AC_ARG_WITH([iib],
	AC_HELP_STRING([--with-iib=path],
	               [build iiblnd against path]),
	[
		case $with_iib in
		yes)    ENABLEIIB=2
			;;
		no)     ENABLEIIB=0
			;;
		*)      IIBPATH="${with_iib}/include"
			ENABLEIIB=3
			;;
		esac
	],[
		ENABLEIIB=1
	])
if test $ENABLEIIB -eq 0; then
	AC_MSG_RESULT([disabled])
elif test ! \( -f ${IIBPATH}/linux/iba/ibt.h \); then
	AC_MSG_RESULT([no])
	case $ENABLEIIB in
	1) ;;
	2) AC_MSG_ERROR([default Infinicon headers not present]);;
	3) AC_MSG_ERROR([bad --with-iib path]);;
	*) AC_MSG_ERROR([internal error]);;
	esac
else
	IIBCPPFLAGS="-I$IIBPATH"
	if test $IIBPATH != "/usr/include"; then
		# we need /usr/include come what may
		IIBCPPFLAGS="$IIBCPPFLAGS -I/usr/include"
        fi
	EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS $IIBCPPFLAGS"
	LB_LINUX_TRY_COMPILE([
		#include <linux/iba/ibt.h>
	],[
	        IBT_INTERFACE_UNION interfaces;
        	FSTATUS             rc;

	         rc = IbtGetInterfaceByVersion(IBT_INTERFACE_VERSION_2,
					       &interfaces);

		return rc == FSUCCESS ? 0 : 1;
	],[
		AC_MSG_RESULT([yes])
		IIBLND="iiblnd"
	],[
		AC_MSG_RESULT([no])
		case $ENABLEIIB in
		1) ;;
		2) AC_MSG_ERROR([can't compile with default Infinicon headers]);;
		3) AC_MSG_ERROR([can't compile with Infinicon headers under $IIBPATH]);;
		*) AC_MSG_ERROR([internal error]);;
		esac
		IIBLND=""
		IIBCPPFLAGS=""
	])
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
fi
AC_SUBST(IIBCPPFLAGS)
AC_SUBST(IIBLND)
])

#
# LN_CONFIG_VIB
#
# check for Voltaire infiniband support
#
AC_DEFUN([LN_CONFIG_VIB],
[AC_MSG_CHECKING([whether to enable Voltaire IB support])
VIBPATH=""
AC_ARG_WITH([vib],
	AC_HELP_STRING([--with-vib=path],
		       [build viblnd against path]),
	[
		case $with_vib in
		no)     AC_MSG_RESULT([no]);;
		*)	VIBPATH="${with_vib}/src/nvigor/ib-code"
			if test -d "$with_vib" -a -d "$VIBPATH"; then
	                        AC_MSG_RESULT([yes])
			else
				AC_MSG_RESULT([no])
				AC_MSG_ERROR([No directory $VIBPATH])
                        fi;;
		esac
	],[
		AC_MSG_RESULT([no])
	])
if test -z "$VIBPATH"; then
	VIBLND=""
else
	VIBCPPFLAGS="-I${VIBPATH}/include -I${VIBPATH}/cm"
	EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS $VIBCPPFLAGS"
	LB_LINUX_TRY_COMPILE([
		#include <linux/list.h>
		#include <asm/byteorder.h>
		#ifdef __BIG_ENDIAN
		# define CPU_BE 1
                # define CPU_LE 0
		#endif
		#ifdef __LITTLE_ENDIAN
		# define CPU_BE 0
		# define CPU_LE 1
		#endif
		#include <vverbs.h>
	        #include <ib-cm.h>
	        #include <ibat.h>
	],[
	        vv_hca_h_t       kib_hca;
		vv_return_t      vvrc;
	        cm_cep_handle_t  cep;
	        ibat_arp_data_t  arp_data;
		ibat_stat_t      ibatrc;

		vvrc = vv_hca_open("ANY_HCA", NULL, &kib_hca);
	        cep = cm_create_cep(cm_cep_transp_rc);
	        ibatrc = ibat_get_ib_data((uint32_t)0, (uint32_t)0,
                                          ibat_paths_primary, &arp_data,
					  (ibat_get_ib_data_reply_fn_t)NULL,
                                          NULL, 0);
		return 0;
	],[
		VIBLND="viblnd"
	],[
	        AC_MSG_ERROR([can't compile viblnd with given path])
	])
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
fi
if test -n "$VIBLND"; then
	EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS $VIBCPPFLAGS"
	AC_MSG_CHECKING([if Voltaire still uses void * sg addresses])
	LB_LINUX_TRY_COMPILE([
		#include <linux/list.h>
		#include <asm/byteorder.h>
		#ifdef __BIG_ENDIAN
		# define CPU_BE 1
                # define CPU_LE 0
		#endif
		#ifdef __LITTLE_ENDIAN
		# define CPU_BE 0
		# define CPU_LE 1
		#endif
		#include <vverbs.h>
	        #include <ib-cm.h>
	        #include <ibat.h>
	],[
	        vv_scatgat_t  sg;

	        return &sg.v_address[3] == NULL;
	],[
	        AC_MSG_RESULT([yes])
	        VIBCPPFLAGS="$VIBCPPFLAGS -DIBNAL_VOIDSTAR_SGADDR=1"
	],[
	        AC_MSG_RESULT([no])
	])
	EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
fi
AC_SUBST(VIBCPPFLAGS)
AC_SUBST(VIBLND)
])

#
# LN_CONFIG_RALND
#
# check whether to use the RapidArray lnd
#
AC_DEFUN([LN_CONFIG_RALND],
[#### Rapid Array
AC_MSG_CHECKING([if RapidArray kernel headers are present])
# placeholder
RACPPFLAGS="-I${LINUX}/drivers/xd1/include"
EXTRA_KCFLAGS_save="$EXTRA_KCFLAGS"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS $RACPPFLAGS"
LB_LINUX_TRY_COMPILE([
	#include <linux/types.h>
	#include <rapl.h>
],[
        RAP_RETURN          rc;
	RAP_PVOID           dev_handle;

        rc = RapkGetDeviceByIndex(0, NULL, &dev_handle);

	return rc == RAP_SUCCESS ? 0 : 1;
],[
	AC_MSG_RESULT([yes])
	RALND="ralnd"
],[
	AC_MSG_RESULT([no])
	RALND=""
	RACPPFLAGS=""
])
EXTRA_KCFLAGS="$EXTRA_KCFLAGS_save"
AC_SUBST(RACPPFLAGS)
AC_SUBST(RALND)
])

#
# LN_STRUCT_PAGE_LIST
#
# 2.6.4 no longer has page->list
#
AC_DEFUN([LN_STRUCT_PAGE_LIST],
[AC_MSG_CHECKING([if struct page has a list field])
LB_LINUX_TRY_COMPILE([
	#include <linux/mm.h>
],[
	struct page page;
	&page.list;
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_PAGE_LIST, 1, [struct page has a list field])
],[
	AC_MSG_RESULT([no])
])
])

#
# LN_STRUCT_SIGHAND
#
# red hat 2.4 adds sighand to struct task_struct
#
AC_DEFUN([LN_STRUCT_SIGHAND],
[AC_MSG_CHECKING([if task_struct has a sighand field])
LB_LINUX_TRY_COMPILE([
	#include <linux/sched.h>
],[
	struct task_struct p;
	p.sighand = NULL;
],[
	AC_DEFINE(CONFIG_RH_2_4_20, 1, [this kernel contains Red Hat 2.4.20 patches])
	AC_MSG_RESULT([yes])
],[
	AC_MSG_RESULT([no])
])
])

#
# LN_FUNC_CPU_ONLINE
#
# cpu_online is different in rh 2.4, vanilla 2.4, and 2.6
#
AC_DEFUN([LN_FUNC_CPU_ONLINE],
[AC_MSG_CHECKING([if kernel defines cpu_online()])
LB_LINUX_TRY_COMPILE([
	#include <linux/sched.h>
],[
	cpu_online(0);
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_CPU_ONLINE, 1, [cpu_online found])
],[
	AC_MSG_RESULT([no])
])
])

#
# LN_TYPE_GFP_T
#
# check if gfp_t is typedef-ed
#
AC_DEFUN([LN_TYPE_GFP_T],
[AC_MSG_CHECKING([if kernel defines gfp_t])
LB_LINUX_TRY_COMPILE([
        #include <linux/gfp.h>
],[
	return sizeof(gfp_t);
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_GFP_T, 1, [gfp_t found])
],[
	AC_MSG_RESULT([no])
])
])

#
# LN_TYPE_CPUMASK_T
#
# same goes for cpumask_t
#
AC_DEFUN([LN_TYPE_CPUMASK_T],
[AC_MSG_CHECKING([if kernel defines cpumask_t])
LB_LINUX_TRY_COMPILE([
	#include <linux/sched.h>
],[
	return sizeof (cpumask_t);
],[
	AC_MSG_RESULT([yes])
	AC_DEFINE(HAVE_CPUMASK_T, 1, [cpumask_t found])
],[
	AC_MSG_RESULT([no])
])
])

#
# LN_FUNC_SHOW_TASK
#
# we export show_task(), but not all kernels have it (yet)
#
AC_DEFUN([LN_FUNC_SHOW_TASK],
[LB_CHECK_SYMBOL_EXPORT([show_task],
[kernel/ksyms.c kernel/sched.c],[
AC_DEFINE(HAVE_SHOW_TASK, 1, [show_task is exported])
],[
])
])

# check kernel __u64 type
AC_DEFUN([LN_KERN__U64_LONG_LONG],
[AC_MSG_CHECKING([kernel __u64 is long long type])
tmp_flags="$EXTRA_KCFLAGS"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -Werror"
LB_LINUX_TRY_COMPILE([
	#include <linux/types.h>
	#include <linux/stddef.h>
],[
	unsigned long long *data1;
	__u64 *data2 = NULL;
		
	data1 = data2;
],[
	AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_KERN__U64_LONG_LONG, 1,
                  [kernel __u64 is long long type])
],[
	AC_MSG_RESULT([no])
])
EXTRA_KCFLAGS="$tmp_flags"
])

# check userland __u64 type
AC_DEFUN([LN_USER__U64_LONG_LONG],
[AC_MSG_CHECKING([userspace __u64 is long long type])
tmp_flags="$CFLAGS"
CFLAGS="$CFLAGS -Werror"
AC_COMPILE_IFELSE([
	#include <linux/types.h>
	#include <linux/stddef.h>
	int main(void) {
		unsigned long long *data1;
		__u64 *data2 = NULL;
		
		data1 = data2;
		return 0;
	}
],[
	AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_USER__U64_LONG_LONG, 1,
                  [userspace __u64 is long long type])
],[
	AC_MSG_RESULT([no])
])
CFLAGS="$tmp_flags"
])

# check userland size_t type
AC_DEFUN([LN_SIZE_T_LONG],
[AC_MSG_CHECKING([size_t is unsigned long type])
tmp_flags="$CFLAGS"
CFLAGS="$CFLAGS -Werror"
AC_COMPILE_IFELSE([
	#include <linux/types.h>
	#include <linux/stddef.h>
	int main(void) {
		unsigned long *data1;
		size_t *data2 = NULL;
		
		data1 = data2;
		return 0;
	}
],[
	AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_SIZE_T_LONG, 1,
                  [size_t is long type])
],[
	AC_MSG_RESULT([no])
])
CFLAGS="$tmp_flags"
])

AC_DEFUN([LN_SSIZE_T_LONG],
[AC_MSG_CHECKING([ssize_t is signed long type])
tmp_flags="$CFLAGS"
CFLAGS="$CFLAGS -Werror"
AC_COMPILE_IFELSE([
	#include <linux/types.h>
	#include <linux/stddef.h>
	int main(void) {
		long *data1;
		ssize_t *data2 = NULL;
		
		data1 = data2;
		return 0;
	}
],[
	AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_SSIZE_T_LONG, 1,
                  [ssize_t is long type])
],[
	AC_MSG_RESULT([no])
])
CFLAGS="$tmp_flags"
])


# check kernel __le16, __le32 types
AC_DEFUN([LN_LE_TYPES],
[AC_MSG_CHECKING([__le16 and __le32 types are defined])
LB_LINUX_TRY_COMPILE([
	#include <linux/types.h>
],[
	__le16 a;
	__le32 b;
],[
	AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_LE_TYPES, 1,
                  [__le16 and __le32 types are defined])
],[
	AC_MSG_RESULT([no])
])
])


# check if task_struct with rcu memeber
AC_DEFUN([LN_TASK_RCU],
[AC_MSG_CHECKING([if task_struct has a rcu field])
LB_LINUX_TRY_COMPILE([
	#include <linux/sched.h>
],[
        struct task_struct tsk;

        tsk.rcu.next = NULL;
],[
	AC_MSG_RESULT([yes])
        AC_DEFINE(HAVE_TASK_RCU, 1,
                  [task_struct has rcu field])
],[
	AC_MSG_RESULT([no])
])
])

# LN_TASKLIST_LOCK
# 2.6.18 remove tasklist_lock export
AC_DEFUN([LN_TASKLIST_LOCK],
[LB_CHECK_SYMBOL_EXPORT([tasklist_lock],
[kernel/fork.c],[
AC_DEFINE(HAVE_TASKLIST_LOCK, 1,
         [tasklist_lock exported])
],[
])
])

# 2.6.19 API changes
# kmem_cache_destroy(cachep) return void instead of
# int
AC_DEFUN([LN_KMEM_CACHE_DESTROY_INT],
[AC_MSG_CHECKING([kmem_cache_destroy(cachep) return int])
LB_LINUX_TRY_COMPILE([
        #include <linux/slab.h>
],[
	int i = kmem_cache_destroy(NULL);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_KMEM_CACHE_DESTROY_INT, 1,
                [kmem_cache_destroy(cachep) return int])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.19 API change
#panic_notifier_list use atomic_notifier operations
#
AC_DEFUN([LN_ATOMIC_PANIC_NOTIFIER],
[AC_MSG_CHECKING([panic_notifier_list is atomic])
LB_LINUX_TRY_COMPILE([
	#include <linux/notifier.h>
	#include <linux/kernel.h>
],[
	struct atomic_notifier_head panic_notifier_list;
],[
        AC_MSG_RESULT(yes)
	AC_DEFINE(HAVE_ATOMIC_PANIC_NOTIFIER, 1,
		[panic_notifier_list is atomic_notifier_head])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.20 API change INIT_WORK use 2 args and not
# store data inside
AC_DEFUN([LN_3ARGS_INIT_WORK],
[AC_MSG_CHECKING([check INIT_WORK want 3 args])
LB_LINUX_TRY_COMPILE([
	#include <linux/workqueue.h>
],[
	struct work_struct work;

	INIT_WORK(&work, NULL, NULL);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_3ARGS_INIT_WORK, 1,
                  [INIT_WORK use 3 args and store data inside])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.21 api change. 'register_sysctl_table' use only one argument,
# instead of more old which need two.
AC_DEFUN([LN_2ARGS_REGISTER_SYSCTL],
[AC_MSG_CHECKING([check register_sysctl_table want 2 args])
LB_LINUX_TRY_COMPILE([
        #include <linux/sysctl.h>
],[
	return register_sysctl_table(NULL,0);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_2ARGS_REGISTER_SYSCTL, 1,
                  [register_sysctl_table want 2 args])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.21 marks kmem_cache_t deprecated and uses struct kmem_cache
# instead
AC_DEFUN([LN_KMEM_CACHE],
[AC_MSG_CHECKING([check kernel has struct kmem_cache])
tmp_flags="$EXTRA_KCFLAGS"
EXTRA_KCFLAGS="-Werror"
LB_LINUX_TRY_COMPILE([
        #include <linux/slab.h>
        typedef struct kmem_cache cache_t;
],[
	cache_t *cachep = NULL;

	kmem_cache_alloc(cachep, 0);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_KMEM_CACHE, 1,
                  [kernel has struct kmem_cache])
],[
        AC_MSG_RESULT(no)
])
EXTRA_KCFLAGS="$tmp_flags"
])

# 2.6.23 lost dtor argument
AC_DEFUN([LN_KMEM_CACHE_CREATE_DTOR],
[AC_MSG_CHECKING([check kmem_cache_create has dtor argument])
LB_LINUX_TRY_COMPILE([
        #include <linux/slab.h>
],[
	kmem_cache_create(NULL, 0, 0, 0, NULL, NULL);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_KMEM_CACHE_CREATE_DTOR, 1,
                  [kmem_cache_create has dtor argument])
],[
        AC_MSG_RESULT(no)
])
])

#
# LN_FUNC_DUMP_TRACE
#
# 2.6.23 exports dump_trace() so we can dump_stack() on any task
# 2.6.24 has stacktrace_ops.address with "reliable" parameter
#
AC_DEFUN([LN_FUNC_DUMP_TRACE],
[LB_CHECK_SYMBOL_EXPORT([dump_trace],
[kernel/ksyms.c arch/${LINUX_ARCH%_64}/kernel/traps_64.c],[
	tmp_flags="$EXTRA_KCFLAGS"
	EXTRA_KCFLAGS="-Werror"
	AC_MSG_CHECKING([whether we can really use dump_stack])
	LB_LINUX_TRY_COMPILE([
		struct task_struct;
		struct pt_regs;
		#include <asm/stacktrace.h>
	],[
	],[
		AC_MSG_RESULT(yes)
		AC_DEFINE(HAVE_DUMP_TRACE, 1, [dump_trace is exported])
	],[
		AC_MSG_RESULT(no)
	],[
	])
	AC_MSG_CHECKING([whether print_trace_address has reliable argument])
	LB_LINUX_TRY_COMPILE([
		struct task_struct;
		struct pt_regs;
		void print_addr(void *data, unsigned long addr, int reliable);
		#include <asm/stacktrace.h>
	],[
		struct stacktrace_ops ops;

		ops.address = print_addr;
	],[
		AC_MSG_RESULT(yes)
		AC_DEFINE(HAVE_TRACE_ADDRESS_RELIABLE, 1,
			  [print_trace_address has reliable argument])
	],[
		AC_MSG_RESULT(no)
	],[
	])
EXTRA_KCFLAGS="$tmp_flags"
])
])

# 2.6.24 request not use real numbers for ctl_name
AC_DEFUN([LN_SYSCTL_UNNUMBERED],
[AC_MSG_CHECKING([for CTL_UNNUMBERED])
LB_LINUX_TRY_COMPILE([
        #include <linux/sysctl.h>
],[
	#ifndef CTL_UNNUMBERED
	#error CTL_UNNUMBERED not exist in kernel
	#endif
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_SYSCTL_UNNUMBERED, 1,
                  [sysctl has CTL_UNNUMBERED])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.24 lost scatterlist->page
AC_DEFUN([LN_SCATTERLIST_SETPAGE],
[AC_MSG_CHECKING([for exist sg_set_page])
LB_LINUX_TRY_COMPILE([
        #include <linux/scatterlist.h>
],[
	sg_set_page(NULL,NULL,0,0);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_SCATTERLIST_SETPAGE, 1,
                  [struct scatterlist has page member])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.26 use int instead of atomic for sem.count
AC_DEFUN([LN_SEM_COUNT],
[AC_MSG_CHECKING([atomic sem.count])
LB_LINUX_TRY_COMPILE([
        #include <asm/semaphore.h>
],[
	struct semaphore s;
	
	atomic_read(&s.count);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_SEM_COUNT_ATOMIC, 1,
                  [semaphore counter is atomic])
],[
        AC_MSG_RESULT(no)
])
])

# 2.6.27 have second argument to sock_map_fd
AC_DEFUN([LN_SOCK_MAP_FD_2ARG],
[AC_MSG_CHECKING([sock_map_fd have second argument])
LB_LINUX_TRY_COMPILE([
	#include <linux/net.h>
],[
        sock_map_fd(NULL, 0);
],[
        AC_MSG_RESULT(yes)
        AC_DEFINE(HAVE_SOCK_MAP_FD_2ARG, 1,
                  [sock_map_fd have second argument])
],[
        AC_MSG_RESULT(no)
])
])

#
#
# LN_CONFIG_USERSPACE
#
#
AC_DEFUN([LN_CONFIG_USERSPACE],
[
LN_USER__U64_LONG_LONG
])

#
# LN_PROG_LINUX
#
# LNet linux kernel checks
#
AC_DEFUN([LN_PROG_LINUX],
[
LN_FUNC_CPU_ONLINE
LN_TYPE_GFP_T
LN_TYPE_CPUMASK_T
LN_CONFIG_AFFINITY
LN_CONFIG_BACKOFF
LN_CONFIG_PANIC_DUMPLOG
LN_CONFIG_QUADRICS
LN_CONFIG_GM
LN_CONFIG_OPENIB
LN_CONFIG_CIB
LN_CONFIG_VIB
LN_CONFIG_IIB
LN_CONFIG_O2IB
LN_CONFIG_RALND
LN_CONFIG_PTLLND
LN_CONFIG_MX

LN_STRUCT_PAGE_LIST
LN_STRUCT_SIGHAND
LN_FUNC_SHOW_TASK
LN_KERN__U64_LONG_LONG
LN_SSIZE_T_LONG
LN_SIZE_T_LONG
LN_LE_TYPES
LN_TASK_RCU
# 2.6.18
LN_TASKLIST_LOCK
# 2.6.19
LN_KMEM_CACHE_DESTROY_INT
LN_ATOMIC_PANIC_NOTIFIER
# 2.6.20
LN_3ARGS_INIT_WORK
# 2.6.21
LN_2ARGS_REGISTER_SYSCTL
LN_KMEM_CACHE
# 2.6.23
LN_KMEM_CACHE_CREATE_DTOR
# 2.6.24
LN_SYSCTL_UNNUMBERED
LN_SCATTERLIST_SETPAGE
# 2.6.26
LN_SEM_COUNT
# 2.6.27
LN_SOCK_MAP_FD_2ARG
LN_FUNC_DUMP_TRACE
])

#
# LN_PROG_DARWIN
#
# Darwin checks
#
AC_DEFUN([LN_PROG_DARWIN],
[LB_DARWIN_CHECK_FUNCS([get_preemption_level])
])

#
# LN_PATH_DEFAULTS
#
# default paths for installed files
#
AC_DEFUN([LN_PATH_DEFAULTS],
[
])

#
# LN_CONFIGURE
#
# other configure checks
#
AC_DEFUN([LN_CONFIGURE],
[# lnet/utils/portals.c
AC_CHECK_HEADERS([netdb.h netinet/tcp.h asm/types.h endian.h sys/ioctl.h])
AC_CHECK_FUNCS([gethostbyname socket connect])

# lnet/utils/debug.c
AC_CHECK_HEADERS([linux/version.h])

AC_CHECK_TYPE([spinlock_t],
	[AC_DEFINE(HAVE_SPINLOCK_T, 1, [spinlock_t is defined])],
	[],
	[#include <linux/spinlock.h>])

# lnet/utils/wirecheck.c
AC_CHECK_FUNCS([strnlen])

# --------  Check for required packages  --------------

#
# LC_CONFIG_READLINE
#
# Build with readline
#
AC_MSG_CHECKING([whether to enable readline support])
AC_ARG_ENABLE(readline,
        AC_HELP_STRING([--disable-readline],
                        [disable readline support]),
        [],[enable_readline='yes'])
AC_MSG_RESULT([$enable_readline])

# -------- check for readline if enabled ----
if test x$enable_readline = xyes ; then
	LIBS_save="$LIBS"
	LIBS="-lncurses $LIBS"
	AC_CHECK_LIB([readline],[readline],[
	LIBREADLINE="-lreadline -lncurses"
	AC_DEFINE(HAVE_LIBREADLINE, 1, [readline library is available])
	],[
	LIBREADLINE=""
	])
	LIBS="$LIBS_save"
else
	LIBREADLINE=""
fi
AC_SUBST(LIBREADLINE)

AC_MSG_CHECKING([if efence debugging support is requested])
AC_ARG_ENABLE(efence,
	AC_HELP_STRING([--enable-efence],
			[use efence library]),
	[],[enable_efence='no'])
AC_MSG_RESULT([$enable_efence])
if test "$enable_efence" = "yes" ; then
	LIBEFENCE="-lefence"
	AC_DEFINE(HAVE_LIBEFENCE, 1, [libefence support is requested])
else
	LIBEFENCE=""
fi
AC_SUBST(LIBEFENCE)

# -------- enable acceptor libwrap (TCP wrappers) support? -------
AC_MSG_CHECKING([if libwrap support is requested])
AC_ARG_ENABLE([libwrap],
	AC_HELP_STRING([--enable-libwrap], [use TCP wrappers]),
	[case "${enableval}" in
		yes) enable_libwrap=yes ;;
		no) enable_libwrap=no ;;
		*) AC_MSG_ERROR(bad value ${enableval} for --enable-libwrap) ;;
	esac],[enable_libwrap=no])
AC_MSG_RESULT([$enable_libwrap])
if test x$enable_libwrap = xyes ; then
	LIBWRAP="-lwrap"
	AC_DEFINE(HAVE_LIBWRAP, 1, [libwrap support is requested])
else
	LIBWRAP=""
fi
AC_SUBST(LIBWRAP)

# -------- check for -lpthread support ----
AC_MSG_CHECKING([whether to use libpthread for lnet library])
AC_ARG_ENABLE([libpthread],
       	AC_HELP_STRING([--disable-libpthread],
               	[disable libpthread]),
       	[],[enable_libpthread=yes])
if test "$enable_libpthread" = "yes" ; then
	AC_CHECK_LIB([pthread], [pthread_create],
		[ENABLE_LIBPTHREAD="yes"],
		[ENABLE_LIBPTHREAD="no"])
	if test "$ENABLE_LIBPTHREAD" = "yes" ; then
		AC_MSG_RESULT([$ENABLE_LIBPTHREAD])
		PTHREAD_LIBS="-lpthread"
		AC_DEFINE([HAVE_LIBPTHREAD], 1, [use libpthread])
	else
		PTHREAD_LIBS=""
		AC_MSG_RESULT([no libpthread is found])
	fi
	AC_SUBST(PTHREAD_LIBS)
else
	AC_MSG_RESULT([no (disabled explicitly)])
	ENABLE_LIBPTHREAD="no"
fi
AC_SUBST(ENABLE_LIBPTHREAD)

# ----------------------------------------
# some tests for catamount-like systems
# ----------------------------------------
AC_ARG_ENABLE([sysio_init],
	AC_HELP_STRING([--disable-sysio-init],
		[call sysio init functions when initializing liblustre]),
	[],[enable_sysio_init=yes])
AC_MSG_CHECKING([whether to initialize libsysio])
AC_MSG_RESULT([$enable_sysio_init])
if test x$enable_sysio_init != xno ; then
	AC_DEFINE([INIT_SYSIO], 1, [call sysio init functions])
fi

AC_ARG_ENABLE([urandom],
	AC_HELP_STRING([--disable-urandom],
		[disable use of /dev/urandom for liblustre]),
	[],[enable_urandom=yes])
AC_MSG_CHECKING([whether to use /dev/urandom for liblustre])
AC_MSG_RESULT([$enable_urandom])
if test x$enable_urandom != xno ; then
	AC_DEFINE([LIBLUSTRE_USE_URANDOM], 1, [use /dev/urandom for random data])
fi

# -------- check for -lcap support ----
if test x$enable_liblustre = xyes ; then
	AC_CHECK_LIB([cap], [cap_get_proc],
		[
			CAP_LIBS="-lcap"
			AC_DEFINE([HAVE_LIBCAP], 1, [use libcap])
		],
		[
			CAP_LIBS=""
		])
	AC_SUBST(CAP_LIBS)

fi

LN_CONFIG_MAX_PAYLOAD
LN_CONFIG_UPTLLND
LN_CONFIG_USOCKLND
])

#
# LN_CONDITIONALS
#
# AM_CONDITOINAL defines for lnet
#
AC_DEFUN([LN_CONDITIONALS],
[AM_CONDITIONAL(BUILD_QSWLND, test x$QSWLND = "xqswlnd")
AM_CONDITIONAL(BUILD_GMLND, test x$GMLND = "xgmlnd")
AM_CONDITIONAL(BUILD_MXLND, test x$MXLND = "xmxlnd")
AM_CONDITIONAL(BUILD_O2IBLND, test x$O2IBLND = "xo2iblnd")
AM_CONDITIONAL(BUILD_OPENIBLND, test x$OPENIBLND = "xopeniblnd")
AM_CONDITIONAL(BUILD_CIBLND, test x$CIBLND = "xciblnd")
AM_CONDITIONAL(BUILD_IIBLND, test x$IIBLND = "xiiblnd")
AM_CONDITIONAL(BUILD_VIBLND, test x$VIBLND = "xviblnd")
AM_CONDITIONAL(BUILD_RALND, test x$RALND = "xralnd")
AM_CONDITIONAL(BUILD_PTLLND, test x$PTLLND = "xptllnd")
AM_CONDITIONAL(BUILD_UPTLLND, test x$UPTLLND = "xptllnd")
AM_CONDITIONAL(BUILD_USOCKLND, test x$USOCKLND = "xusocklnd")
])

#
# LN_CONFIG_FILES
#
# files that should be generated with AC_OUTPUT
#
AC_DEFUN([LN_CONFIG_FILES],
[AC_CONFIG_FILES([
lnet/Kernelenv
lnet/Makefile
lnet/autoMakefile
lnet/autoconf/Makefile
lnet/doc/Makefile
lnet/include/Makefile
lnet/include/libcfs/Makefile
lnet/include/libcfs/linux/Makefile
lnet/include/lnet/Makefile
lnet/include/lnet/linux/Makefile
lnet/klnds/Makefile
lnet/klnds/autoMakefile
lnet/klnds/gmlnd/Makefile
lnet/klnds/mxlnd/autoMakefile
lnet/klnds/mxlnd/Makefile
lnet/klnds/gmlnd/autoMakefile
lnet/klnds/openiblnd/Makefile
lnet/klnds/openiblnd/autoMakefile
lnet/klnds/o2iblnd/Makefile
lnet/klnds/o2iblnd/autoMakefile
lnet/klnds/ciblnd/Makefile
lnet/klnds/ciblnd/autoMakefile
lnet/klnds/iiblnd/Makefile
lnet/klnds/iiblnd/autoMakefile
lnet/klnds/viblnd/Makefile
lnet/klnds/viblnd/autoMakefile
lnet/klnds/qswlnd/Makefile
lnet/klnds/qswlnd/autoMakefile
lnet/klnds/ralnd/Makefile
lnet/klnds/ralnd/autoMakefile
lnet/klnds/socklnd/Makefile
lnet/klnds/socklnd/autoMakefile
lnet/klnds/ptllnd/Makefile
lnet/klnds/ptllnd/autoMakefile
lnet/libcfs/Makefile
lnet/libcfs/autoMakefile
lnet/libcfs/linux/Makefile
lnet/lnet/Makefile
lnet/lnet/autoMakefile
lnet/selftest/Makefile
lnet/selftest/autoMakefile
lnet/ulnds/Makefile
lnet/ulnds/autoMakefile
lnet/ulnds/socklnd/Makefile
lnet/ulnds/ptllnd/Makefile
lnet/utils/Makefile
])
case $lb_target_os in
	darwin)
		AC_CONFIG_FILES([
lnet/include/libcfs/darwin/Makefile
lnet/include/lnet/darwin/Makefile
lnet/libcfs/darwin/Makefile
])
		;;
esac
])

#
# LIBCFS stub macros. (These are defined in the libcfs module on HEAD))
#
AC_DEFUN([LIBCFS_PATH_DEFAULTS], [])
AC_DEFUN([LIBCFS_PROG_LINUX], [])
AC_DEFUN([LIBCFS_CONDITIONALS], [])
AC_DEFUN([LIBCFS_CONFIGURE], [])
AC_DEFUN([LIBCFS_CONFIG_FILES], [])

dnl Checks for OFED
AC_DEFUN([LN_CONFIG_OFED_SPEC],
[
	AC_MSG_CHECKING([if OFED has ib_dma_map_single])
	LB_LINUX_TRY_COMPILE([
		#include <linux/version.h>
		#include <linux/pci.h>
		#if !HAVE_GFP_T
		typedef int gfp_t;
		#endif
		#include <rdma/ib_verbs.h>
	],[
		ib_dma_map_single(NULL, NULL, 0, 0);
		return 0;
	],[
		AC_MSG_RESULT(yes)
		AC_DEFINE(HAVE_OFED_IB_DMA_MAP, 1,
			  [ib_dma_map_single defined])
	],[
		AC_MSG_RESULT(no)
	])

	AC_MSG_CHECKING([if ib_create_cq wants comp_vector])
	LB_LINUX_TRY_COMPILE([
		#include <linux/version.h>
		#include <linux/pci.h>
		#if !HAVE_GFP_T
		typedef int gfp_t;
		#endif
		#include <rdma/ib_verbs.h>
	],[
		ib_create_cq(NULL, NULL, NULL, NULL, 0, 0);
		return 0;
	],[
		AC_MSG_RESULT(yes)
		AC_DEFINE(HAVE_OFED_IB_COMP_VECTOR, 1,
			  [has completion vector])
	],[
		AC_MSG_RESULT(no)
	])

	AC_MSG_CHECKING([if OFED supports iWarp transport])
	LB_LINUX_TRY_COMPILE([
		#include <linux/version.h>
		#include <linux/pci.h>
		#if !HAVE_GFP_T
		typedef int gfp_t;
		#endif
		#include <rdma/ib_verbs.h>
	],[
		return RDMA_TRANSPORT_IWARP ==
		       rdma_node_get_transport(RDMA_NODE_RNIC);
	],[
		AC_MSG_RESULT(yes)
		AC_DEFINE(HAVE_OFED_TRANSPORT_IWARP, 1,
			  [has transport iWARP])
	],[
		AC_MSG_RESULT(no)
	])

	AC_MSG_CHECKING([if OFED has RDMA_CM_EVENT_ADDR_CHANGE])
	LB_LINUX_TRY_COMPILE([
		#include <linux/version.h>
		#include <linux/pci.h>
		#if !HAVE_GFP_T
		typedef int gfp_t;
		#endif
		#include <rdma/rdma_cm.h>
	],[
		return (RDMA_CM_EVENT_ADDR_CHANGE == 0);
	],[
		AC_MSG_RESULT(yes)
		AC_DEFINE(HAVE_OFED_RDMA_CMEV_ADDRCHANGE, 1,
			  [has completion vector])
	],[
		AC_MSG_RESULT(no)
	])

	AC_MSG_CHECKING([if OFED has RDMA_CM_EVENT_TIMEWAIT_EXIT])
	LB_LINUX_TRY_COMPILE([
		#include <linux/version.h>
		#include <linux/pci.h>
		#if !HAVE_GFP_T
		typedef int gfp_t;
		#endif
		#include <rdma/rdma_cm.h>
	],[
		return (RDMA_CM_EVENT_TIMEWAIT_EXIT == 0);
	],[
		AC_MSG_RESULT(yes)
		AC_DEFINE(HAVE_OFED_RDMA_CMEV_TIMEWAIT_EXIT, 1,
			  [has completion vector])
	],[
		AC_MSG_RESULT(no)
	])
])

#
# LB_DARWIN_CHECK_FUNCS
#
# check for functions in the darwin kernel
# Note that this is broken for cross compiling
#
AC_DEFUN([LB_DARWIN_CHECK_FUNCS],
[AC_FOREACH([AC_Func], [$1],
  [AH_TEMPLATE(AS_TR_CPP(HAVE_[]AC_Func),
               [Define to 1 if you have the `]AC_Func[' function.])])dnl
for ac_func in $1
do
AC_MSG_CHECKING([for $1])
AS_IF([AC_TRY_COMMAND(nm /mach | grep "[$1]" >/dev/null 2>/dev/null)],[
	AC_MSG_RESULT([yes])
	AC_DEFINE_UNQUOTED(AS_TR_CPP([HAVE_$ac_func])) $2
],[
	AC_MSG_RESULT([no]) $3
])dnl
done
])

#
# LB_DARWIN_CONDITIONALS
#
# AM_CONDITIONALs for darwin
#
AC_DEFUN([LB_DARWIN_CONDITIONALS],
[
])

#
# LB_PROG_DARWIN
#
# darwin tests
#
AC_DEFUN([LB_PROG_DARWIN],
[kernel_framework="/System/Library/Frameworks/Kernel.framework"
#
# FIXME: there should be a better way to get these than hard coding them
#
case $target_cpu in 
	powerpc*)
		EXTRA_KCFLAGS="$EXTRA_KCFLAGS -arch ppc -mtune=G4 -mlong-branch"
		EXTRA_KLDFLAGS="-arch ppc"
		;;
	i?86 | x86_64)
		EXTRA_KCFLAGS="$EXTRA_KCFLAGS -arch i386"
		EXTRA_KLDFLAGS="-arch i386"
		;;
esac

# Kernel of OS X is not 64bits(even in Tiger), but -m64 can be taken by gcc in Tiger
# (Tiger can support 64bits applications), so we have to eliminate -m64 while 
# building kextensions for and OS X.
CC=`echo $CC | sed -e "s/\-m64//g"`
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -x c -pipe -Wno-trigraphs -fasm-blocks -g -O0"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -Wno-four-char-constants -Wmost -O0"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -fmessage-length=0"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -I$kernel_framework/Headers"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -I$kernel_framework/Headers/bsd"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -I$kernel_framework/PrivateHeaders"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -fno-common -nostdinc -fno-builtin"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -finline -fno-keep-inline-functions"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -force_cpusubtype_ALL -fno-exceptions"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -msoft-float -static"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -DKERNEL -DKERNEL_PRIVATE"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -DDRIVER_PRIVATE -DAPPLE -DNeXT"
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -D__KERNEL__ -D__DARWIN__"
#
# C flags for Panther/Tiger
#
case $target_os in
        darwin8*)
                EXTRA_KCFLAGS="$EXTRA_KCFLAGS -D__DARWIN8__"
	;;
        darwin7*)
                EXTRA_KCFLAGS="$EXTRA_KCFLAGS -ffix-and-continue"
        ;;
esac

#
# Debugging flags. Remove!
#
EXTRA_KCFLAGS="$EXTRA_KCFLAGS -O0 -DMACH_ASSERT=1"
EXTRA_KLDFLAGS="$EXTRA_KLDFLAGS -static -nostdlib -r"
EXTRA_KLIBS="-lkmodc++ -lkmod -lcc_kext"
KMODEXT=""

AC_SUBST(EXTRA_KLDFLAGS)
AC_SUBST(EXTRA_KLIBS)

kextdir='/System/Library/Extensions/$(firstword $(macos_PROGRAMS)).kext'
plistdir='$(kextdir)/Contents'
macosdir='$(plistdir)/MacOS'

AC_SUBST(kextdir)
AC_SUBST(plistdir)
AC_SUBST(macosdir)

LN_PROG_DARWIN

LP_PROG_DARWIN

LC_PROG_DARWIN
])

#
# LS_CONFIGURE
#
# configure bits for lustre-snmp
#
AC_DEFUN([LS_CONFIGURE],
[AC_MSG_CHECKING([whether to try to build SNMP support])
AC_ARG_ENABLE([snmp],
	AC_HELP_STRING([--enable-snmp],
		       [require SNMP support (default=auto)]),
	[],[enable_snmp='auto'])
AC_MSG_RESULT([$enable_snmp])

if test x$enable_snmp != xno ; then
	AC_CHECK_PROG([NET_SNMP_CONFIG], [net-snmp-config], [net-snmp-config])
	if test "$NET_SNMP_CONFIG" ; then
		NET_SNMP_CFLAGS=$($NET_SNMP_CONFIG --base-cflags)
		NET_SNMP_LIBS=$($NET_SNMP_CONFIG --agent-libs)

		CPPFLAGS_save="$CPPFLAGS"
		CPPFLAGS="$CPPFLAGS $NET_SNMP_CFLAGS"

		LIBS_save="$LIBS"
		LIBS="$LIBS $NET_SNMP_LIBS"

		AC_CHECK_HEADER([net-snmp/net-snmp-config.h],[
			AC_CHECK_FUNC([register_mib],[SNMP_SUBDIR="snmp"],[
				LIBS="$LIBS -lwrap"
				NET_SNMP_LISB="$NET_SNMP_LIBS -lwrap"
				# fail autoconf's cache
				unset ac_cv_func_register_mib
				AC_CHECK_FUNC([register_mib],[SNMP_SUBDIR="snmp"])
			])
		])

		LIBS="$LIBS_save"
		CPPFLAGS="$CPPFLAGS_save"
	fi
	AC_MSG_CHECKING([for SNMP support])
	if test "$SNMP_SUBDIR" ; then
		AC_MSG_RESULT([yes])
	else
		AC_MSG_RESULT([no (see config.log for errors)])
		if test x$enable_snmp = xyes ; then
			AC_MSG_ERROR([SNMP support was requested, but unavailable])
		fi
	fi
fi

agentdir='${pkglibdir}/snmp'
mibdir='${pkgdatadir}/snmp/mibs'

AC_SUBST(NET_SNMP_CFLAGS)
AC_SUBST(NET_SNMP_LIBS)
AC_SUBST(agentdir)
AC_SUBST(mibdir)
])

#
# LS_CONFIG_FILE
#
# files that should be generated with AC_OUTPUT
#
AC_DEFUN([LS_CONFIG_FILES],
[AC_CONFIG_FILES([
snmp/Makefile
snmp/autoconf/Makefile
])
])

# Do all the work for Automake.                            -*- Autoconf -*-

# This macro actually does too much some checks are only needed if
# your package does certain things.  But this isn't really a big deal.

# Copyright (C) 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003
# Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# serial 10

AC_PREREQ([2.54])

# Autoconf 2.50 wants to disallow AM_ names.  We explicitly allow
# the ones we care about.
m4_pattern_allow([^AM_[A-Z]+FLAGS$])dnl

# AM_INIT_AUTOMAKE(PACKAGE, VERSION, [NO-DEFINE])
# AM_INIT_AUTOMAKE([OPTIONS])
# -----------------------------------------------
# The call with PACKAGE and VERSION arguments is the old style
# call (pre autoconf-2.50), which is being phased out.  PACKAGE
# and VERSION should now be passed to AC_INIT and removed from
# the call to AM_INIT_AUTOMAKE.
# We support both call styles for the transition.  After
# the next Automake release, Autoconf can make the AC_INIT
# arguments mandatory, and then we can depend on a new Autoconf
# release and drop the old call support.
AC_DEFUN([AM_INIT_AUTOMAKE],
[AC_REQUIRE([AM_SET_CURRENT_AUTOMAKE_VERSION])dnl
 AC_REQUIRE([AC_PROG_INSTALL])dnl
# test to see if srcdir already configured
if test "`cd $srcdir && pwd`" != "`pwd`" &&
   test -f $srcdir/config.status; then
  AC_MSG_ERROR([source directory already configured; run "make distclean" there first])
fi

# test whether we have cygpath
if test -z "$CYGPATH_W"; then
  if (cygpath --version) >/dev/null 2>/dev/null; then
    CYGPATH_W='cygpath -w'
  else
    CYGPATH_W=echo
  fi
fi
AC_SUBST([CYGPATH_W])

# Define the identity of the package.
dnl Distinguish between old-style and new-style calls.
m4_ifval([$2],
[m4_ifval([$3], [_AM_SET_OPTION([no-define])])dnl
 AC_SUBST([PACKAGE], [$1])dnl
 AC_SUBST([VERSION], [$2])],
[_AM_SET_OPTIONS([$1])dnl
 AC_SUBST([PACKAGE], ['AC_PACKAGE_TARNAME'])dnl
 AC_SUBST([VERSION], ['AC_PACKAGE_VERSION'])])dnl

_AM_IF_OPTION([no-define],,
[AC_DEFINE_UNQUOTED(PACKAGE, "$PACKAGE", [Name of package])
 AC_DEFINE_UNQUOTED(VERSION, "$VERSION", [Version number of package])])dnl

# Some tools Automake needs.
AC_REQUIRE([AM_SANITY_CHECK])dnl
AC_REQUIRE([AC_ARG_PROGRAM])dnl
AM_MISSING_PROG(ACLOCAL, aclocal-${am__api_version})
AM_MISSING_PROG(AUTOCONF, autoconf)
AM_MISSING_PROG(AUTOMAKE, automake-${am__api_version})
AM_MISSING_PROG(AUTOHEADER, autoheader)
AM_MISSING_PROG(MAKEINFO, makeinfo)
AM_MISSING_PROG(AMTAR, tar)
AM_PROG_INSTALL_SH
AM_PROG_INSTALL_STRIP
# We need awk for the "check" target.  The system "awk" is bad on
# some platforms.
AC_REQUIRE([AC_PROG_AWK])dnl
AC_REQUIRE([AC_PROG_MAKE_SET])dnl
AC_REQUIRE([AM_SET_LEADING_DOT])dnl

_AM_IF_OPTION([no-dependencies],,
[AC_PROVIDE_IFELSE([AC_PROG_CC],
                  [_AM_DEPENDENCIES(CC)],
                  [define([AC_PROG_CC],
                          defn([AC_PROG_CC])[_AM_DEPENDENCIES(CC)])])dnl
AC_PROVIDE_IFELSE([AC_PROG_CXX],
                  [_AM_DEPENDENCIES(CXX)],
                  [define([AC_PROG_CXX],
                          defn([AC_PROG_CXX])[_AM_DEPENDENCIES(CXX)])])dnl
])
])


# When config.status generates a header, we must update the stamp-h file.
# This file resides in the same directory as the config header
# that is generated.  The stamp files are numbered to have different names.

# Autoconf calls _AC_AM_CONFIG_HEADER_HOOK (when defined) in the
# loop where config.status creates the headers, so we can generate
# our stamp files there.
AC_DEFUN([_AC_AM_CONFIG_HEADER_HOOK],
[# Compute $1's index in $config_headers.
_am_stamp_count=1
for _am_header in $config_headers :; do
  case $_am_header in
    $1 | $1:* )
      break ;;
    * )
      _am_stamp_count=`expr $_am_stamp_count + 1` ;;
  esac
done
echo "timestamp for $1" >`AS_DIRNAME([$1])`/stamp-h[]$_am_stamp_count])

# Copyright 2002  Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA

# AM_AUTOMAKE_VERSION(VERSION)
# ----------------------------
# Automake X.Y traces this macro to ensure aclocal.m4 has been
# generated from the m4 files accompanying Automake X.Y.
AC_DEFUN([AM_AUTOMAKE_VERSION],[am__api_version="1.7"])

# AM_SET_CURRENT_AUTOMAKE_VERSION
# -------------------------------
# Call AM_AUTOMAKE_VERSION so it can be traced.
# This function is AC_REQUIREd by AC_INIT_AUTOMAKE.
AC_DEFUN([AM_SET_CURRENT_AUTOMAKE_VERSION],
	 [AM_AUTOMAKE_VERSION([1.7.9])])

# Helper functions for option handling.                    -*- Autoconf -*-

# Copyright 2001, 2002  Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# serial 2

# _AM_MANGLE_OPTION(NAME)
# -----------------------
AC_DEFUN([_AM_MANGLE_OPTION],
[[_AM_OPTION_]m4_bpatsubst($1, [[^a-zA-Z0-9_]], [_])])

# _AM_SET_OPTION(NAME)
# ------------------------------
# Set option NAME.  Presently that only means defining a flag for this option.
AC_DEFUN([_AM_SET_OPTION],
[m4_define(_AM_MANGLE_OPTION([$1]), 1)])

# _AM_SET_OPTIONS(OPTIONS)
# ----------------------------------
# OPTIONS is a space-separated list of Automake options.
AC_DEFUN([_AM_SET_OPTIONS],
[AC_FOREACH([_AM_Option], [$1], [_AM_SET_OPTION(_AM_Option)])])

# _AM_IF_OPTION(OPTION, IF-SET, [IF-NOT-SET])
# -------------------------------------------
# Execute IF-SET if OPTION is set, IF-NOT-SET otherwise.
AC_DEFUN([_AM_IF_OPTION],
[m4_ifset(_AM_MANGLE_OPTION([$1]), [$2], [$3])])

#
# Check to make sure that the build environment is sane.
#

# Copyright 1996, 1997, 2000, 2001 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# serial 3

# AM_SANITY_CHECK
# ---------------
AC_DEFUN([AM_SANITY_CHECK],
[AC_MSG_CHECKING([whether build environment is sane])
# Just in case
sleep 1
echo timestamp > conftest.file
# Do `set' in a subshell so we don't clobber the current shell's
# arguments.  Must try -L first in case configure is actually a
# symlink; some systems play weird games with the mod time of symlinks
# (eg FreeBSD returns the mod time of the symlink's containing
# directory).
if (
   set X `ls -Lt $srcdir/configure conftest.file 2> /dev/null`
   if test "$[*]" = "X"; then
      # -L didn't work.
      set X `ls -t $srcdir/configure conftest.file`
   fi
   rm -f conftest.file
   if test "$[*]" != "X $srcdir/configure conftest.file" \
      && test "$[*]" != "X conftest.file $srcdir/configure"; then

      # If neither matched, then we have a broken ls.  This can happen
      # if, for instance, CONFIG_SHELL is bash and it inherits a
      # broken ls alias from the environment.  This has actually
      # happened.  Such a system could not be considered "sane".
      AC_MSG_ERROR([ls -t appears to fail.  Make sure there is not a broken
alias in your environment])
   fi

   test "$[2]" = conftest.file
   )
then
   # Ok.
   :
else
   AC_MSG_ERROR([newly created file is older than distributed files!
Check your system clock])
fi
AC_MSG_RESULT(yes)])

#  -*- Autoconf -*-


# Copyright 1997, 1999, 2000, 2001 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# serial 3

# AM_MISSING_PROG(NAME, PROGRAM)
# ------------------------------
AC_DEFUN([AM_MISSING_PROG],
[AC_REQUIRE([AM_MISSING_HAS_RUN])
$1=${$1-"${am_missing_run}$2"}
AC_SUBST($1)])


# AM_MISSING_HAS_RUN
# ------------------
# Define MISSING if not defined so far and test if it supports --run.
# If it does, set am_missing_run to use it, otherwise, to nothing.
AC_DEFUN([AM_MISSING_HAS_RUN],
[AC_REQUIRE([AM_AUX_DIR_EXPAND])dnl
test x"${MISSING+set}" = xset || MISSING="\${SHELL} $am_aux_dir/missing"
# Use eval to expand $SHELL
if eval "$MISSING --run true"; then
  am_missing_run="$MISSING --run "
else
  am_missing_run=
  AC_MSG_WARN([`missing' script is too old or missing])
fi
])

# AM_AUX_DIR_EXPAND

# Copyright 2001 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# For projects using AC_CONFIG_AUX_DIR([foo]), Autoconf sets
# $ac_aux_dir to `$srcdir/foo'.  In other projects, it is set to
# `$srcdir', `$srcdir/..', or `$srcdir/../..'.
#
# Of course, Automake must honor this variable whenever it calls a
# tool from the auxiliary directory.  The problem is that $srcdir (and
# therefore $ac_aux_dir as well) can be either absolute or relative,
# depending on how configure is run.  This is pretty annoying, since
# it makes $ac_aux_dir quite unusable in subdirectories: in the top
# source directory, any form will work fine, but in subdirectories a
# relative path needs to be adjusted first.
#
# $ac_aux_dir/missing
#    fails when called from a subdirectory if $ac_aux_dir is relative
# $top_srcdir/$ac_aux_dir/missing
#    fails if $ac_aux_dir is absolute,
#    fails when called from a subdirectory in a VPATH build with
#          a relative $ac_aux_dir
#
# The reason of the latter failure is that $top_srcdir and $ac_aux_dir
# are both prefixed by $srcdir.  In an in-source build this is usually
# harmless because $srcdir is `.', but things will broke when you
# start a VPATH build or use an absolute $srcdir.
#
# So we could use something similar to $top_srcdir/$ac_aux_dir/missing,
# iff we strip the leading $srcdir from $ac_aux_dir.  That would be:
#   am_aux_dir='\$(top_srcdir)/'`expr "$ac_aux_dir" : "$srcdir//*\(.*\)"`
# and then we would define $MISSING as
#   MISSING="\${SHELL} $am_aux_dir/missing"
# This will work as long as MISSING is not called from configure, because
# unfortunately $(top_srcdir) has no meaning in configure.
# However there are other variables, like CC, which are often used in
# configure, and could therefore not use this "fixed" $ac_aux_dir.
#
# Another solution, used here, is to always expand $ac_aux_dir to an
# absolute PATH.  The drawback is that using absolute paths prevent a
# configured tree to be moved without reconfiguration.

# Rely on autoconf to set up CDPATH properly.
AC_PREREQ([2.50])

AC_DEFUN([AM_AUX_DIR_EXPAND], [
# expand $ac_aux_dir to an absolute path
am_aux_dir=`cd $ac_aux_dir && pwd`
])

# AM_PROG_INSTALL_SH
# ------------------
# Define $install_sh.

# Copyright 2001 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

AC_DEFUN([AM_PROG_INSTALL_SH],
[AC_REQUIRE([AM_AUX_DIR_EXPAND])dnl
install_sh=${install_sh-"$am_aux_dir/install-sh"}
AC_SUBST(install_sh)])

# AM_PROG_INSTALL_STRIP

# Copyright 2001 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# One issue with vendor `install' (even GNU) is that you can't
# specify the program used to strip binaries.  This is especially
# annoying in cross-compiling environments, where the build's strip
# is unlikely to handle the host's binaries.
# Fortunately install-sh will honor a STRIPPROG variable, so we
# always use install-sh in `make install-strip', and initialize
# STRIPPROG with the value of the STRIP variable (set by the user).
AC_DEFUN([AM_PROG_INSTALL_STRIP],
[AC_REQUIRE([AM_PROG_INSTALL_SH])dnl
# Installed binaries are usually stripped using `strip' when the user
# run `make install-strip'.  However `strip' might not be the right
# tool to use in cross-compilation environments, therefore Automake
# will honor the `STRIP' environment variable to overrule this program.
dnl Don't test for $cross_compiling = yes, because it might be `maybe'.
if test "$cross_compiling" != no; then
  AC_CHECK_TOOL([STRIP], [strip], :)
fi
INSTALL_STRIP_PROGRAM="\${SHELL} \$(install_sh) -c -s"
AC_SUBST([INSTALL_STRIP_PROGRAM])])

#                                                          -*- Autoconf -*-
# Copyright (C) 2003  Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# serial 1

# Check whether the underlying file-system supports filenames
# with a leading dot.  For instance MS-DOS doesn't.
AC_DEFUN([AM_SET_LEADING_DOT],
[rm -rf .tst 2>/dev/null
mkdir .tst 2>/dev/null
if test -d .tst; then
  am__leading_dot=.
else
  am__leading_dot=_
fi
rmdir .tst 2>/dev/null
AC_SUBST([am__leading_dot])])

# serial 5						-*- Autoconf -*-

# Copyright (C) 1999, 2000, 2001, 2002, 2003  Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.


# There are a few dirty hacks below to avoid letting `AC_PROG_CC' be
# written in clear, in which case automake, when reading aclocal.m4,
# will think it sees a *use*, and therefore will trigger all it's
# C support machinery.  Also note that it means that autoscan, seeing
# CC etc. in the Makefile, will ask for an AC_PROG_CC use...



# _AM_DEPENDENCIES(NAME)
# ----------------------
# See how the compiler implements dependency checking.
# NAME is "CC", "CXX", "GCJ", or "OBJC".
# We try a few techniques and use that to set a single cache variable.
#
# We don't AC_REQUIRE the corresponding AC_PROG_CC since the latter was
# modified to invoke _AM_DEPENDENCIES(CC); we would have a circular
# dependency, and given that the user is not expected to run this macro,
# just rely on AC_PROG_CC.
AC_DEFUN([_AM_DEPENDENCIES],
[AC_REQUIRE([AM_SET_DEPDIR])dnl
AC_REQUIRE([AM_OUTPUT_DEPENDENCY_COMMANDS])dnl
AC_REQUIRE([AM_MAKE_INCLUDE])dnl
AC_REQUIRE([AM_DEP_TRACK])dnl

ifelse([$1], CC,   [depcc="$CC"   am_compiler_list=],
       [$1], CXX,  [depcc="$CXX"  am_compiler_list=],
       [$1], OBJC, [depcc="$OBJC" am_compiler_list='gcc3 gcc'],
       [$1], GCJ,  [depcc="$GCJ"  am_compiler_list='gcc3 gcc'],
                   [depcc="$$1"   am_compiler_list=])

AC_CACHE_CHECK([dependency style of $depcc],
               [am_cv_$1_dependencies_compiler_type],
[if test -z "$AMDEP_TRUE" && test -f "$am_depcomp"; then
  # We make a subdir and do the tests there.  Otherwise we can end up
  # making bogus files that we don't know about and never remove.  For
  # instance it was reported that on HP-UX the gcc test will end up
  # making a dummy file named `D' -- because `-MD' means `put the output
  # in D'.
  mkdir conftest.dir
  # Copy depcomp to subdir because otherwise we won't find it if we're
  # using a relative directory.
  cp "$am_depcomp" conftest.dir
  cd conftest.dir
  # We will build objects and dependencies in a subdirectory because
  # it helps to detect inapplicable dependency modes.  For instance
  # both Tru64's cc and ICC support -MD to output dependencies as a
  # side effect of compilation, but ICC will put the dependencies in
  # the current directory while Tru64 will put them in the object
  # directory.
  mkdir sub

  am_cv_$1_dependencies_compiler_type=none
  if test "$am_compiler_list" = ""; then
     am_compiler_list=`sed -n ['s/^#*\([a-zA-Z0-9]*\))$/\1/p'] < ./depcomp`
  fi
  for depmode in $am_compiler_list; do
    # Setup a source with many dependencies, because some compilers
    # like to wrap large dependency lists on column 80 (with \), and
    # we should not choose a depcomp mode which is confused by this.
    #
    # We need to recreate these files for each test, as the compiler may
    # overwrite some of them when testing with obscure command lines.
    # This happens at least with the AIX C compiler.
    : > sub/conftest.c
    for i in 1 2 3 4 5 6; do
      echo '#include "conftst'$i'.h"' >> sub/conftest.c
      : > sub/conftst$i.h
    done
    echo "${am__include} ${am__quote}sub/conftest.Po${am__quote}" > confmf

    case $depmode in
    nosideeffect)
      # after this tag, mechanisms are not by side-effect, so they'll
      # only be used when explicitly requested
      if test "x$enable_dependency_tracking" = xyes; then
	continue
      else
	break
      fi
      ;;
    none) break ;;
    esac
    # We check with `-c' and `-o' for the sake of the "dashmstdout"
    # mode.  It turns out that the SunPro C++ compiler does not properly
    # handle `-M -o', and we need to detect this.
    if depmode=$depmode \
       source=sub/conftest.c object=sub/conftest.${OBJEXT-o} \
       depfile=sub/conftest.Po tmpdepfile=sub/conftest.TPo \
       $SHELL ./depcomp $depcc -c -o sub/conftest.${OBJEXT-o} sub/conftest.c \
         >/dev/null 2>conftest.err &&
       grep sub/conftst6.h sub/conftest.Po > /dev/null 2>&1 &&
       grep sub/conftest.${OBJEXT-o} sub/conftest.Po > /dev/null 2>&1 &&
       ${MAKE-make} -s -f confmf > /dev/null 2>&1; then
      # icc doesn't choke on unknown options, it will just issue warnings
      # (even with -Werror).  So we grep stderr for any message
      # that says an option was ignored.
      if grep 'ignoring option' conftest.err >/dev/null 2>&1; then :; else
        am_cv_$1_dependencies_compiler_type=$depmode
        break
      fi
    fi
  done

  cd ..
  rm -rf conftest.dir
else
  am_cv_$1_dependencies_compiler_type=none
fi
])
AC_SUBST([$1DEPMODE], [depmode=$am_cv_$1_dependencies_compiler_type])
AM_CONDITIONAL([am__fastdep$1], [
  test "x$enable_dependency_tracking" != xno \
  && test "$am_cv_$1_dependencies_compiler_type" = gcc3])
])


# AM_SET_DEPDIR
# -------------
# Choose a directory name for dependency files.
# This macro is AC_REQUIREd in _AM_DEPENDENCIES
AC_DEFUN([AM_SET_DEPDIR],
[AC_REQUIRE([AM_SET_LEADING_DOT])dnl
AC_SUBST([DEPDIR], ["${am__leading_dot}deps"])dnl
])


# AM_DEP_TRACK
# ------------
AC_DEFUN([AM_DEP_TRACK],
[AC_ARG_ENABLE(dependency-tracking,
[  --disable-dependency-tracking Speeds up one-time builds
  --enable-dependency-tracking  Do not reject slow dependency extractors])
if test "x$enable_dependency_tracking" != xno; then
  am_depcomp="$ac_aux_dir/depcomp"
  AMDEPBACKSLASH='\'
fi
AM_CONDITIONAL([AMDEP], [test "x$enable_dependency_tracking" != xno])
AC_SUBST([AMDEPBACKSLASH])
])

# Generate code to set up dependency tracking.   -*- Autoconf -*-

# Copyright 1999, 2000, 2001, 2002 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

#serial 2

# _AM_OUTPUT_DEPENDENCY_COMMANDS
# ------------------------------
AC_DEFUN([_AM_OUTPUT_DEPENDENCY_COMMANDS],
[for mf in $CONFIG_FILES; do
  # Strip MF so we end up with the name of the file.
  mf=`echo "$mf" | sed -e 's/:.*$//'`
  # Check whether this is an Automake generated Makefile or not.
  # We used to match only the files named `Makefile.in', but
  # some people rename them; so instead we look at the file content.
  # Grep'ing the first line is not enough: some people post-process
  # each Makefile.in and add a new line on top of each file to say so.
  # So let's grep whole file.
  if grep '^#.*generated by automake' $mf > /dev/null 2>&1; then
    dirpart=`AS_DIRNAME("$mf")`
  else
    continue
  fi
  grep '^DEP_FILES *= *[[^ @%:@]]' < "$mf" > /dev/null || continue
  # Extract the definition of DEP_FILES from the Makefile without
  # running `make'.
  DEPDIR=`sed -n -e '/^DEPDIR = / s///p' < "$mf"`
  test -z "$DEPDIR" && continue
  # When using ansi2knr, U may be empty or an underscore; expand it
  U=`sed -n -e '/^U = / s///p' < "$mf"`
  test -d "$dirpart/$DEPDIR" || mkdir "$dirpart/$DEPDIR"
  # We invoke sed twice because it is the simplest approach to
  # changing $(DEPDIR) to its actual value in the expansion.
  for file in `sed -n -e '
    /^DEP_FILES = .*\\\\$/ {
      s/^DEP_FILES = //
      :loop
	s/\\\\$//
	p
	n
	/\\\\$/ b loop
      p
    }
    /^DEP_FILES = / s/^DEP_FILES = //p' < "$mf" | \
       sed -e 's/\$(DEPDIR)/'"$DEPDIR"'/g' -e 's/\$U/'"$U"'/g'`; do
    # Make sure the directory exists.
    test -f "$dirpart/$file" && continue
    fdir=`AS_DIRNAME(["$file"])`
    AS_MKDIR_P([$dirpart/$fdir])
    # echo "creating $dirpart/$file"
    echo '# dummy' > "$dirpart/$file"
  done
done
])# _AM_OUTPUT_DEPENDENCY_COMMANDS


# AM_OUTPUT_DEPENDENCY_COMMANDS
# -----------------------------
# This macro should only be invoked once -- use via AC_REQUIRE.
#
# This code is only required when automatic dependency tracking
# is enabled.  FIXME.  This creates each `.P' file that we will
# need in order to bootstrap the dependency handling code.
AC_DEFUN([AM_OUTPUT_DEPENDENCY_COMMANDS],
[AC_CONFIG_COMMANDS([depfiles],
     [test x"$AMDEP_TRUE" != x"" || _AM_OUTPUT_DEPENDENCY_COMMANDS],
     [AMDEP_TRUE="$AMDEP_TRUE" ac_aux_dir="$ac_aux_dir"])
])

# Check to see how 'make' treats includes.	-*- Autoconf -*-

# Copyright (C) 2001, 2002, 2003 Free Software Foundation, Inc.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

# serial 2

# AM_MAKE_INCLUDE()
# -----------------
# Check to see how make treats includes.
AC_DEFUN([AM_MAKE_INCLUDE],
[am_make=${MAKE-make}
cat > confinc << 'END'
am__doit:
	@echo done
.PHONY: am__doit
END
# If we don't find an include directive, just comment out the code.
AC_MSG_CHECKING([for style of include used by $am_make])
am__include="#"
am__quote=
_am_result=none
# First try GNU make style include.
echo "include confinc" > confmf
# We grep out `Entering directory' and `Leaving directory'
# messages which can occur if `w' ends up in MAKEFLAGS.
# In particular we don't look at `^make:' because GNU make might
# be invoked under some other name (usually "gmake"), in which
# case it prints its new name instead of `make'.
if test "`$am_make -s -f confmf 2> /dev/null | grep -v 'ing directory'`" = "done"; then
   am__include=include
   am__quote=
   _am_result=GNU
fi
# Now try BSD make style include.
if test "$am__include" = "#"; then
   echo '.include "confinc"' > confmf
   if test "`$am_make -s -f confmf 2> /dev/null`" = "done"; then
      am__include=.include
      am__quote="\""
      _am_result=BSD
   fi
fi
AC_SUBST([am__include])
AC_SUBST([am__quote])
AC_MSG_RESULT([$_am_result])
rm -f confinc confmf
])

