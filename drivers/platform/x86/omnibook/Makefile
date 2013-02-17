
# Makefile -- makefile for the HP OmniBook support module

# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# Written by Soós Péter <sp@osb.hu>, 2002-2004
#
# Note! Dependencies are done automagically by 'make dep', which also
# removes any old dependencies. DON'T put your own dependencies here
# unless it's something special (ie not a .c file).
#
# Note 2! The CFLAGS definitions are now in the main makefile...

EXTRA_LDFLAGS += $(src)/sections.lds
obj-$(CONFIG_OMNIBOOK) += omnibook.o

omnibook-objs := init.o ec.o compal.o acpi.o nbsmi.o \
ac.o kbc.o lib.o pio.o battery.o blank.o bluetooth.o display.o dock.o dump.o \
fan.o fan_policy.o hotkeys.o info.o lcd.o muteled.o temperature.o \
touchpad.o wireless.o


