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

