%define set_enable() %{expand:%%force_enable %{1}} %{expand:%%undefine _disable_%{1}}
%define set_disable() %{expand:%%force_disable %{1}} %{expand:%%undefine _enable_%{1}}
%define set_with() %{expand:%%force_with %{1}} %{expand:%%undefine _without_%{1}}
%define set_without() %{expand:%%force_without %{1}} %{expand:%%undefine _with_%{1}}

%define intel_64 nocona core2 corei7 nehalem
%define intel_32 pentium pentiumpro pentium_mmx pentium2 pentium3 pentium_m pentium4 prescott atom
%define amd_32 5x86 k5 k6 k6_2 k6_3 geode k7 athlon athlon_xp
%define amd_64 opteron k8 k9 k10 barcelona phenom
%define via_64 nano
%define via_32 c3 c3_2
%define x86_64 x86_64 %intel_64 %amd_64 %via_64

%define extra_modules %nil
%define Extra_modules() BuildRequires: kernel-source-%1 = %2 \
%global extra_modules %extra_modules %1=%2

%define base_flavour led
%define sub_flavour ws
%define flavour %base_flavour-%sub_flavour

Name: kernel-image-%flavour
Version: 3.4.29
Release: alt3

%define kernel_req %nil
%define kernel_prov %nil
%define kernel_branch 3.4
%define kernel_stable_version 29
%define kernel_extra_version .%kernel_stable_version
#define kernel_extra_version %nil

%define krelease %release

%define kmandir %{_man9dir}l
# Build options
# You can change compiler version by editing this line:
%define kgcc_version	4.7

%def_enable smp
%def_disable verbose
%def_disable debug
%def_disable modversions
%def_enable kallsyms
%def_with src
%def_enable docs
%def_enable htmldocs
%def_enable man
%def_disable compat
%def_enable x32
%def_disable debugfs
%def_disable numa
%def_enable acpi
%def_enable pci
%def_disable mca
%def_disable math_emu
%def_disable x86_extended_platform
%def_enable pcmcia
%def_enable isdn
%def_enable telephony
%def_enable atm
%def_disable tokenring
%def_enable fddi
%def_enable w1
%def_enable hamradio
%def_enable can
%def_enable fusion
%def_enable drm
%def_enable ipv6
%def_enable edac
%def_enable ide
%def_enable pata
%def_enable firewire
%def_enable bluetooth
%def_enable irda
%def_enable joystick
%def_enable gameport
%def_enable usb_gadget
%def_enable tablet
%def_enable touchscreen
%def_enable lirc
%def_enable watchdog
%def_enable mtd
%def_enable mmc
%def_enable media
%def_enable sound
%def_disable oss
%def_enable alsa
%def_disable pcsp
%def_enable video
%def_enable guest
%def_enable ext4_for_ext23
%def_enable bootsplash
%def_enable zcache
%def_enable security
%def_enable audit
%def_enable selinux
%def_enable tomoyo
%def_enable apparmor
%def_enable smack
%def_enable yama
%def_enable thp
%def_enable kvm
%def_enable hyperv
%def_disable paravirt_guest
%def_disable kvm_quest
%def_disable nfs_swap
%def_enable fatelf
%def_with lnfs
%def_enable lnfs
%def_without perf
%def_enable oprofile
%def_enable secrm
%def_with firmware

%def_disable debug_section_mismatch

%define allocator SLAB

%Extra_modules vboxhost 4.1.24
#Extra_modules vboxguest 4.1.22
#Extra_modules fglrx 8.97.100.3
#Extra_modules netatop 0.1.1

%define strip_mod_opts --strip-unneeded -R .comment

## Don't edit below this line ##################################

%define kversion	%kernel_branch%kernel_extra_version
%define modules_dir	/lib/modules/%kversion-%flavour-%krelease
%define firmware_dir	/lib/firmware/%kversion-%flavour-%krelease

%define kheaders_dir	%_prefix/include/linux-%kernel_branch-%flavour
%define kbuild_dir	%_prefix/src/linux-%kversion-%flavour-%krelease
%define old_kbuild_dir	%_prefix/src/linux-%kversion-%flavour

Summary: The Linux kernel (the core of the Linux operating system)
License: GPL
Group: System/Kernel and hardware
Url: http://www.kernel.org/

Source0: linux-%version.tar
Source1: %flavour-%kernel_branch.x86_64.config
Source2: %flavour-%kernel_branch.i386.config
Source10: Makefile.external

#Patch0000: patch-%kernel_branch.%kernel_stable_version

Patch0011: linux-%kernel_branch.20-fix-arch-arm.patch
Patch0012: linux-%kernel_branch.20-fix-arch-arm-mach-omap2.patch
Patch0013: linux-%kernel_branch.20-fix-arch-arm-mm.patch
Patch0014: linux-%kernel_branch.20-fix-arch-ia64.patch
Patch0015: linux-%kernel_branch.20-fix-arch-powerpc.patch
Patch0016: linux-%kernel_branch.20-fix-arch-powerpc--prom_init.patch
Patch0017: linux-%kernel_branch.20-fix-arch-powerpc-platforms-chrp.patch
Patch0018: linux-%kernel_branch.20-fix-arch-powerpc-xmon.patch
Patch0019: linux-%kernel_branch.20-fix-arch-s390.patch

Patch0020: linux-%kernel_branch.20-fix-arch-x86.patch
Patch0021: linux-%kernel_branch.20-fix-arch-x86--apic.patch
Patch0022: linux-%kernel_branch.20-fix-arch-x86--apm.patch
Patch0023: linux-%kernel_branch.20-fix-arch-x86--hpet.patch
Patch0024: linux-%kernel_branch.20-fix-arch-x86--kexec.patch
Patch0025: linux-%kernel_branch.28-fix-arch-x86--mcheck.patch
Patch0026: linux-%kernel_branch.25-fix-arch-x86-cpu.patch
Patch0027: linux-%kernel_branch.25-fix-arch-x86-cpu--rdrand.patch

Patch0030: linux-%kernel_branch.20-fix-block.patch
Patch0031: linux-%kernel_branch.20-fix-block-partitions--efi.patch

Patch0040: linux-%kernel_branch.28-fix-drivers-acpi.patch
Patch0041: linux-%kernel_branch.20-fix-drivers-acpi--ec_sys.patch
Patch0042: linux-%kernel_branch.20-fix-drivers-acpi--thermal.patch
Patch0043: linux-%kernel_branch.20-fix-drivers-acpi-acpica.patch

Patch0051: linux-%kernel_branch.25-fix-drivers-ata--ata_piix.patch
Patch0052: linux-%kernel_branch.25-fix-drivers-ata--pata_amd.patch
Patch0053: linux-%kernel_branch.25-fix-drivers-ata--pata_mpiix.patch
Patch0054: linux-%kernel_branch.25-fix-drivers-ata--pata_oldpiix.patch
Patch0055: linux-%kernel_branch.25-fix-drivers-ata--pata_sch.patch

Patch0061: linux-%kernel_branch.25-fix-drivers-atm--ambassador.patch

Patch0070: linux-%kernel_branch.25-fix-drivers-base.patch
Patch0071: linux-%kernel_branch.20-fix-drivers-base--dma-contiguous.patch
Patch0072: linux-%kernel_branch.25-fix-drivers-base--dma-buf.patch

Patch0081: linux-%kernel_branch.25-fix-drivers-block--drbd.patch
Patch0082: linux-%kernel_branch.20-fix-drivers-block--zram.patch

Patch0091: linux-%kernel_branch.20-fix-drivers-char--lp.patch
Patch0092: linux-%kernel_branch.25-fix-drivers-char-agp--intel-agp.patch
Patch0093: linux-%kernel_branch.25-fix-drivers-char-hw_random--amd-rng.patch
Patch0094: linux-%kernel_branch.25-fix-drivers-char-hw_random--intel-rng.patch

Patch0101: linux-%kernel_branch.20-fix-drivers-connector--cn_proc.patch

Patch0111: linux-%kernel_branch.20-fix-drivers-cpufreq--acpi-cpufreq.patch
Patch0112: linux-%kernel_branch.20-fix-drivers-cpufreq--cpufreq_ondemand.patch
Patch0113: linux-%kernel_branch.25-fix-drivers-cpufreq--p4-clockmod.patch
Patch0114: linux-%kernel_branch.25-fix-drivers-cpufreq--powernow-k8.patch

Patch0121: linux-%kernel_branch.25-fix-drivers-crypto--padlock.patch

Patch0131: linux-%kernel_branch.25-fix-drivers-dma-ioat.patch
Patch0132: linux-%kernel_branch.25-fix-drivers-dma--intel_mid_dma.patch

Patch0141: linux-%kernel_branch.25-fix-drivers-edac--e752x_edac.patch
Patch0142: linux-%kernel_branch.25-fix-drivers-edac--e7xxx_edac.patch
Patch0143: linux-%kernel_branch.25-fix-drivers-edac--i3000_edac.patch
Patch0144: linux-%kernel_branch.25-fix-drivers-edac--i3200_edac.patch
Patch0145: linux-%kernel_branch.25-fix-drivers-edac--i5000_edac.patch
Patch0146: linux-%kernel_branch.25-fix-drivers-edac--i5100_edac.patch
Patch0147: linux-%kernel_branch.25-fix-drivers-edac--i5400_edac.patch
Patch0148: linux-%kernel_branch.25-fix-drivers-edac--i7300_edac.patch
Patch0149: linux-%kernel_branch.25-fix-drivers-edac--i82443bxgx_edac.patch
Patch0150: linux-%kernel_branch.25-fix-drivers-edac--i82860_edac.patch
Patch0151: linux-%kernel_branch.25-fix-drivers-edac--i82875p_edac.patch
Patch0152: linux-%kernel_branch.25-fix-drivers-edac--i82975x_edac.patch
Patch0153: linux-%kernel_branch.25-fix-drivers-edac--x38_edac.patch

Patch0161: linux-%kernel_branch.25-fix-drivers-gpu-drm--exynosdrm.patch
Patch0162: linux-%kernel_branch.25-fix-drivers-gpu-drm--gma500_gfx.patch
Patch0163: linux-%kernel_branch.25-fix-drivers-gpu-drm--i915.patch
Patch0164: linux-%kernel_branch.20-fix-drivers-gpu-drm--nouveau.patch

Patch0171: linux-%kernel_branch.20-fix-drivers-hid--hid-apple.patch
Patch0172: linux-%kernel_branch.20-fix-drivers-hid--hid-hyperv.patch

Patch0181: linux-%kernel_branch.25-fix-drivers-hsi.patch
Patch0182: linux-%kernel_branch.25-fix-drivers-hsi--hsi.patch

Patch0190: linux-%kernel_branch.20-fix-drivers-hv.patch
Patch0191: linux-%kernel_branch.20-fix-drivers-hv--hv_utils.patch
Patch0192: linux-%kernel_branch.20-fix-drivers-hv--hv_vmbus.patch

Patch0201: linux-%kernel_branch.25-fix-drivers-hwmon--applesmc.patch
Patch0202: linux-%kernel_branch.25-fix-drivers-hwmon--asc7621.patch
Patch0203: linux-%kernel_branch.25-fix-drivers-hwmon--coretemp.patch
Patch0204: linux-%kernel_branch.25-fix-drivers-hwmon--fam15h_power.patch
Patch0205: linux-%kernel_branch.25-fix-drivers-hwmon--i5k_amb.patch
Patch0206: linux-%kernel_branch.25-fix-drivers-hwmon--k10temp.patch
Patch0207: linux-%kernel_branch.25-fix-drivers-hwmon--k8temp.patch
Patch0208: linux-%kernel_branch.25-fix-drivers-hwmon--via-cputemp.patch

Patch0211: linux-%kernel_branch.25-fix-drivers-i2c--i2c-boardinfo.patch
Patch0212: linux-%kernel_branch.25-fix-drivers-i2c--i2c-pxa.patch
Patch0213: linux-%kernel_branch.25-fix-drivers-i2c-busses--i2c-intel-mid.patch

Patch0221: linux-%kernel_branch.25-fix-drivers-idle--i7300_idle.patch

Patch0231: linux-%kernel_branch.25-fix-drivers-infiniband-hw--mlx4.patch

Patch0240: linux-%kernel_branch.25-fix-drivers-input.patch
Patch0241: linux-%kernel_branch.20-fix-drivers-input-keyboard--omap4-keypad.patch
Patch0242: linux-%kernel_branch.20-fix-drivers-input-serio--i8042.patch

Patch0251: linux-%kernel_branch.25-fix-drivers-isdn--sc.patch
Patch0252: linux-%kernel_branch.25-fix-drivers-isdn-gigaset--gigaset.patch
Patch0253: linux-%kernel_branch.20-fix-drivers-isdn-mISDN--mISDN_core.patch

Patch0261: linux-%kernel_branch.20-fix-drivers-macintosh--adb.patch
Patch0262: linux-%kernel_branch.20-fix-drivers-macintosh--adbhid.patch

Patch0271: linux-%kernel_branch.20-fix-drivers-md--dm-mod.patch
Patch0272: linux-%kernel_branch.20-fix-drivers-md--dm-multipath.patch

Patch0281: linux-%kernel_branch.25-fix-drivers-media-common-tuners--tda18212.patch
Patch0282: linux-%kernel_branch.25-fix-drivers-media-common-tuners--tda18218.patch
Patch0283: linux-%kernel_branch.25-fix-drivers-media-dvb-dvb-usb--dvb-usb-mxl111sf.patch
Patch0284: linux-%kernel_branch.25-fix-drivers-media-dvb-ttpci--budget-av.patch
Patch0285: linux-%kernel_branch.25-fix-drivers-media-rc--lirc_dev.patch
Patch0286: linux-%kernel_branch.25-fix-drivers-media-rc-lirc.patch
Patch0287: linux-%kernel_branch.25-fix-drivers-media-rc-lirc--lirc_imon.patch
Patch0288: linux-%kernel_branch.25-fix-drivers-media-rc-lirc--lirc_sasem.patch
Patch0289: linux-%kernel_branch.25-fix-drivers-media-rc-lirc--lirc_serial.patch
Patch0290: linux-%kernel_branch.25-fix-drivers-media-video--uvcvideo.patch
Patch0291: linux-%kernel_branch.25-fix-drivers-media-video-gspca--pac7302.patch

Patch0301: linux-%kernel_branch.25-fix-drivers-mfd--rc5t583.patch
Patch0302: linux-%kernel_branch.25-fix-drivers-mfd--rc5t583-irq.patch
Patch0303: linux-%kernel_branch.25-fix-drivers-mfd--wm8994-core.patch

Patch0311: linux-%kernel_branch.20-fix-drivers-misc--pti.patch

Patch0321: linux-%kernel_branch.20-fix-drivers-mmc-host--mmci.patch

Patch0331: linux-%kernel_branch.27-fix-drivers-net-ethernet-alacritech--slicoss.patch
Patch0332: linux-%kernel_branch.25-fix-drivers-net-ethernet-amd--depca.patch
Patch0333: linux-%kernel_branch.25-fix-drivers-net-ethernet-amd--nmclan_cs.patch
Patch0334: linux-%kernel_branch.25-fix-drivers-net-ethernet-dec--ewrk3.patch
Patch0335: linux-%kernel_branch.20-fix-drivers-net-ethernet-dec-tulip--tulip.patch
Patch0336: linux-%kernel_branch.25-fix-drivers-net-ethernet-fujitsu--at1700.patch
Patch0337: linux-%kernel_branch.25-fix-drivers-net-ethernet-i825xx--znet.patch
Patch0338: linux-%kernel_branch.20-fix-drivers-net-ethernet-ibm--ehea.patch
Patch0339: linux-%kernel_branch.25-fix-drivers-net-ethernet-via--via-rhine.patch

Patch0341: linux-%kernel_branch.20-fix-drivers-net-hyperv.patch

Patch0351: linux-%kernel_branch.20-fix-drivers-net-wireless--b43.patch
Patch0352: linux-%kernel_branch.25-fix-drivers-net-wireless--iwlwifi.patch
Patch0353: linux-%kernel_branch.20-fix-drivers-net-wireless-brcm80211--brcmsmac.patch
Patch0354: linux-%kernel_branch.25-fix-drivers-net-wireless-ipw2x00--libipw.patch
Patch0355: linux-%kernel_branch.20-fix-drivers-net-wireless-rt2x00--rt2800lib.patch

Patch0361: linux-%kernel_branch.27-fix-drivers-platform--asus_oled.patch
Patch0362: linux-%kernel_branch.20-fix-drivers-platform--hdaps.patch
Patch0363: linux-%kernel_branch.25-fix-drivers-platform--intel_ips.patch
Patch0364: linux-%kernel_branch.25-fix-drivers-platform--intel_menlow.patch
Patch0365: linux-%kernel_branch.25-fix-drivers-platform--intel_oaktrail.patch

Patch0371: linux-%kernel_branch.25-fix-drivers-rtc--rtc-m41t80.patch

Patch0381: linux-%kernel_branch.25-fix-drivers-scsi--aha1542.patch
Patch0382: linux-%kernel_branch.25-fix-drivers-scsi--aic94xx.patch
Patch0383: linux-%kernel_branch.28-fix-drivers-scsi--hv_storvsc.patch
Patch0384: linux-%kernel_branch.25-fix-drivers-scsi--mpt2sas.patch
Patch0385: linux-%kernel_branch.25-fix-drivers-scsi--mvsas.patch
Patch0386: linux-%kernel_branch.20-fix-drivers-scsi--scsi_mod.patch
Patch0387: linux-%kernel_branch.20-fix-drivers-scsi--scsi_netlink.patch
Patch0388: linux-%kernel_branch.20-fix-drivers-scsi--sd_mod.patch
Patch0389: linux-%kernel_branch.20-fix-drivers-scsi-device_handler--scsi_dh.patch
Patch0390: linux-%kernel_branch.20-fix-drivers-scsi-ibmvscsi--ibmvscsic.patch
Patch0391: linux-%kernel_branch.20-fix-drivers-scsi-megaraid--megaraid_mbox.patch

Patch0401: linux-%kernel_branch.25-fix-drivers-spi--spi.patch

Patch0411: linux-%kernel_branch.27-fix-drivers-tty--pty.patch
Patch0412: linux-%kernel_branch.20-fix-drivers-tty-serial-8250--8250.patch

Patch0421: linux-%kernel_branch.25-fix-drivers-usb-gadget--g_audio.patch

Patch0431: linux-%kernel_branch.20-fix-drivers-video-aty--radeonfb.patch
Patch0432: linux-%kernel_branch.20-fix-drivers-video-console--vgacon.patch
Patch0433: linux-%kernel_branch.20-fix-drivers-video-geode.patch
Patch0434: linux-%kernel_branch.20-fix-drivers-video-omap2-dss.patch

Patch0441: linux-%kernel_branch.25-fix-firmware--vicam.patch

Patch0450: linux-%kernel_branch.28-fix-fs.patch
Patch0451: linux-%kernel_branch.20-fix-fs-btrfs.patch
Patch0452: linux-%kernel_branch.20-fix-fs-ext4.patch
Patch0453: linux-%kernel_branch.25-fix-fs-nfs.patch
Patch0454: linux-%kernel_branch.20-fix-fs-proc.patch
Patch0455: linux-%kernel_branch.29-fix-fs-quota.patch
Patch0456: linux-%kernel_branch.28-fix-fs-ramfs.patch
Patch0457: linux-%kernel_branch.20-fix-fs-reiserfs.patch

Patch0460: linux-%kernel_branch.20-fix-init.patch

Patch0470: linux-%kernel_branch.20-fix-kernel.patch

Patch0480: linux-%kernel_branch.25-fix-lib.patch
Patch0481: linux-%kernel_branch.25-fix-lib--crc32.patch

Patch0490: linux-%kernel_branch.20-fix-mm.patch
Patch0491: linux-%kernel_branch.20-fix-mm--compaction.patch
Patch0492: linux-%kernel_branch.20-fix-mm--memcontrol.patch
Patch0493: linux-%kernel_branch.20-fix-mm--memory-failure.patch
Patch0494: linux-%kernel_branch.20-fix-mm--memory_hotplug.patch
Patch0495: linux-%kernel_branch.20-fix-mm--swap.patch
Patch0496: linux-%kernel_branch.20-fix-mm--zcache.patch
Patch0497: linux-%kernel_branch.20-fix-mm--zsmalloc.patch

Patch0501: linux-%kernel_branch.25-fix-net-bridge--bridge.patch
Patch0502: linux-%kernel_branch.25-fix-net-mac80211.patch
Patch0503: linux-%kernel_branch.20-fix-net-netfilter--nf_conntrack_ftp.patch
Patch0504: linux-%kernel_branch.28-fix-net-rds--rds_rdma.patch
Patch0505: linux-%kernel_branch.20-fix-net-sunrpc.patch

Patch0511: linux-%kernel_branch.20-fix-scripts--kconfig.patch

Patch0521: linux-%kernel_branch.20-fix-security--apparmor.patch
Patch0522: linux-%kernel_branch.20-fix-security--security.patch

Patch0531: linux-%kernel_branch.20-fix-sound-pci-hda--snd-hda-codec-realtek.patch
Patch0532: linux-%kernel_branch.20-fix-sound-soc-omap--snd-soc-omap.patch
Patch0533: linux-%kernel_branch.20-fix-sound-soc-omap--snd-soc-omap-mcbsp.patch

Patch0541: linux-%kernel_branch.20-fix-tools--perf.patch
Patch0542: linux-%kernel_branch.20-fix-tools-hv.patch

Patch0550: linux-%kernel_branch.20-fix-virt-kvm.patch
Patch0551: linux-%kernel_branch.25-fix-virt-kvm--kvm-amd.patch


Patch1001: linux-%kernel_branch.20-feat-arch-arm-mach-omap2--drm.patch

Patch1011: linux-%kernel_branch-feat-block--bfq-iosched.patch
Patch1012: linux-%kernel_branch-feat-block--sio-iosched.patch

Patch1021: linux-%kernel_branch.20-feat-drivers-block--cloop.patch
Patch1022: linux-%kernel_branch.25-feat-drivers-block--zram.patch

Patch1031: linux-%kernel_branch.20-feat-drivers-char--crasher.patch

Patch1041: linux-%kernel_branch.20-feat-drivers-gpu-drm--cirrus.patch

Patch1051: linux-%kernel_branch.20-feat-drivers-hwmon--ipmisensors.patch

Patch1061: linux-%kernel_branch.20-feat-drivers-input-touchscreen--elousb.patch

Patch1071: linux-%kernel_branch.20-feat-drivers-md--dm-raid45.patch

Patch1081: linux-%kernel_branch.20-feat-drivers-media-rc-lirc.patch

Patch1091: linux-%kernel_branch.20-feat-drivers-misc--rts_pstor.patch

Patch1101: linux-%kernel_branch.27-feat-drivers-net-ethernet-alacritech.patch
Patch1102: linux-%kernel_branch.27-feat-drivers-net-ethernet-alacritech--slicoss.patch
Patch1103: linux-%kernel_branch.20-feat-drivers-net-wireless-rtl8187se.patch
Patch1104: linux-%kernel_branch.20-feat-drivers-net-wireless-rtl8192e.patch
Patch1105: linux-%kernel_branch.20-feat-drivers-net-wireless-rtl8192u.patch
Patch1106: linux-%kernel_branch.20-feat-drivers-net-wireless-rtl8712.patch

Patch1111: linux-%kernel_branch.27-feat-drivers-platform--asus_oled.patch
Patch1112: linux-%kernel_branch.20-feat-drivers-platform--thinkpad_ec.patch
Patch1113: linux-%kernel_branch.20-feat-drivers-platform--tp_smapi.patch

Patch1121: linux-%kernel_branch.20-feat-drivers-usb-usbip.patch

Patch1131: linux-%kernel_branch.20-feat-drivers-video--bootsplash.patch
Patch1132: linux-%kernel_branch.25-feat-drivers-video--xgifb.patch

Patch1141: linux-%kernel_branch-feat-firmware-rtl_nic.patch

Patch1151: linux-%kernel_branch.25-feat-fs--lnfs.patch
Patch1152: linux-%kernel_branch.20-feat-fs--richacl.patch
Patch1153: linux-%kernel_branch.18-feat-fs--secrm.patch
Patch1154: linux-%kernel_branch-feat-fs-aufs.patch
Patch1155: linux-%kernel_branch.20-feat-fs-binfmt_elf--fatelf.patch
Patch1156: linux-%kernel_branch.20-feat-fs-dazukofs.patch
Patch1157: linux-%kernel_branch.18-feat-fs-ext2--secrm.patch
Patch1158: linux-%kernel_branch.18-feat-fs-ext3--secrm.patch
Patch1159: linux-%kernel_branch.26-feat-fs-ext4--richacl.patch
Patch1160: linux-%kernel_branch.20-feat-fs-ext4--secrm.patch
Patch1161: linux-%kernel_branch.20-feat-fs-f2fs.patch
Patch1162: linux-%kernel_branch.18-feat-fs-fat--secrm.patch
Patch1163: linux-%kernel_branch.20-feat-fs-hfs.patch
Patch1164: linux-%kernel_branch.18-feat-fs-jbd--secrm.patch
Patch1165: linux-%kernel_branch.18-feat-fs-jbd2--secrm.patch
Patch1166: linux-%kernel_branch.25-feat-fs-overlayfs.patch
Patch1167: linux-%kernel_branch.20-feat-fs-reiser4.patch
Patch1168: linux-%kernel_branch.20-feat-fs-squashfs--write.patch
Patch1169: linux-%kernel_branch.20-feat-fs-unionfs.patch

Patch1171: linux-%kernel_branch.27-feat-kernel-power-tuxonice.patch
Patch1172: linux-%kernel_branch.27-feat-kernel-power-tuxonice--frontswap.patch

Patch1181: linux-%kernel_branch.20-feat-lib--unwind.patch

Patch1191: linux-%kernel_branch.25-feat-mm--frontswap.patch
Patch1192: linux-%kernel_branch.20-feat-mm--slqb.patch
Patch1193: linux-%kernel_branch.14-feat-mm--uksm.patch
Patch1194: linux-%kernel_branch.20-feat-mm--zcache.patch
Patch1195: linux-%kernel_branch.20-feat-mm--zsmalloc.patch

Patch1201: linux-%kernel_branch.20-feat-net--netatop.patch
Patch1202: linux-%kernel_branch.27-feat-net-ipv4-netfilter--ipt_NETFLOW.patch
Patch1203: linux-%kernel_branch.20-feat-net-netfilter--nf_conntrack_slp.patch


ExclusiveOS: Linux
ExclusiveArch: %x86_64 %ix86

%ifarch %x86_64 %ix86
%define kernel_arch x86
%else
%define kernel_arch %_target_cpu
%endif

%ifarch %x86_64
%define base_arch x86_64
%endif
%ifarch %ix86
%define base_arch i386
%endif

%ifnarch x86_64 i486 i586
%set_disable docs
%set_without src
%endif

%if_disabled docs
%set_disable htmldocs
%set_disable man
%endif

%ifarch i386
%set_disable pci
%set_disable acpi
%set_disable edac
%set_disable media
%set_disable kvm
%set_disable hyperv
%set_disable oprofile
%endif

%ifnarch i386 i486
%set_disable math_emu
%endif

%{?_disable_pci:%set_disable drm}

%{?_disable_media:%set_disable lirc}

%if_disabled sound
%set_disable oss
%set_disable alsa
%endif

%{?_disable_alsa:%set_disable pcsp}

%if_disabled video
%set_disable bootsplash
%endif

%{?_enable_debug:%set_enable debugfs}

%{!?allocator:%define allocator SLAB}

%ifarch %x86_64
%define kernel_base_cpu	GENERIC_CPU
%ifarch k8
%define kernel_cpu	K8
%endif
%ifarch k9
%define kernel_cpu	K9
%endif
%ifarch k10
%define kernel_cpu	K10
%endif
%ifarch nocona
%define kernel_cpu	PSC
%endif
%ifarch core2
%define kernel_cpu	CORE2
%endif
%ifarch corei7 nehalem
%define kernel_cpu	COREI7
%endif
%endif

%ifarch %ix86
%define kernel_base_cpu	M386
%ifarch i486
%define kernel_cpu	486
%endif
%ifarch i586
%define kernel_cpu	586
%endif
%ifarch i686
%define kernel_cpu	686
%endif
%ifarch k6
%define kernel_cpu	K6
%endif
%ifarch athlon
%define kernel_cpu	K7
%endif
%ifarch pentium4
%define kernel_cpu	PENTIUM4
%endif
%ifarch k8_32
%define kernel_cpu	K8
%endif
%ifarch k9_32
%define kernel_cpu	K9
%endif
%ifarch k10_32
%define kernel_cpu	K10
%endif
%ifarch core2_32
%define kernel_cpu	CORE2
%endif
%ifarch atom
%define kernel_cpu	ATOM
%endif
%ifarch corei7_32 nehalem_32
%define kernel_cpu	COREI7
%endif
%endif

%if "x%extra_modules" != "x"
%define extra_mods %(echo "%extra_modules" | sed 's/=[^ ]*//g')
%endif

BuildPreReq: rpm-build-kernel
BuildRequires: dev86 flex
BuildRequires: libdb4-devel
%{?kgcc_version:BuildRequires: gcc%kgcc_version}
BuildRequires: module-init-tools >= 3.1
BuildRequires: patch >= 2.6.1-alt1
%{?_with_src:BuildRequires: pxz}

%{?_enable_htmldocs:BuildRequires: xmlto transfig ghostscript}
%{?_enable_man:BuildRequires: xmlto}
%{?_with_perf:BuildRequires: binutils-devel libelf-devel asciidoc elfutils-devel >= 0.138}

Requires: bootloader-utils >= 0.4.17
Requires: module-init-tools >= 3.1
Requires: mkinitrd >= 1:2.9.9-alt1
Requires: startup >= 0.9.8.24.1

Provides: kernel = %kversion
Provides: kernel-modules-md-%flavour = %version-%release

PreReq: coreutils
PreReq: module-init-tools >= 3.1
PreReq: mkinitrd >= 1:2.9.9-alt1
AutoProv: no, %kernel_prov
AutoReq: no, %kernel_req

%description
This package contains the Linux kernel that is used to boot and run
your system.
Most hardware drivers for this kernel are built as modules.  Some of
these drivers are built separately from the kernel; they are available
in separate packages (kernel-modules-*-%flavour).
The "ws" flavour of kernel packages is kernel for using on
workstations.

%define kernel_modules_package_add_provides() \
Provides: kernel-modules-%{1}-%flavour = %version-%release \
Provides: kernel-modules-%{1}-%kversion-%flavour-%krelease = %version-%release

%define kernel_modules_package_std_body() \
Group: System/Kernel and hardware \
Provides: kernel-modules-%{1}-%kversion-%flavour-%krelease = %kversion-%release \
Conflicts: kernel-modules-%{1}-%kversion-%flavour-%krelease < %kversion-%release \
Conflicts: kernel-modules-%{1}-%kversion-%flavour-%krelease > %kversion-%release \
Requires(postun): %name = %kversion-%release \
AutoProv: no, %kernel_prov \
AutoReq: no, %kernel_req \
PreReq: coreutils module-init-tools >= 3.1 %name = %kversion-%release

%define kernel_doc_package_std_body() \
Group: Documentation \
%{?base_flavour:Provides: kernel-%{1}-%base_flavour = %version-%release} \
Provides: kernel-%{1}-%flavour = %version-%release \
BuildArch: noarch \
AutoProv: no \
AutoReq: no

%if 0
%define kernel_modules_package_post() \
%post -n kernel-modules-%{1}-%flavour \
%post_kernel_modules %kversion-%flavour-%krelease \
\
%postun -n kernel-modules-%{1}-%flavour \
%postun_kernel_modules %kversion-%flavour-%krelease
%else
%define kernel_modules_package_post() \
%nil
%endif

%define kernel_modules_package_files() \
%files -n kernel-modules-%{1}-%flavour -f %{1}.rpmmodlist

%package -n kernel-modules-scsi-%flavour
Summary: SCSI driver modules
%kernel_modules_package_std_body scsi

%description -n kernel-modules-scsi-%flavour
This package contains SCSI modules for the Linux kernel package
%name-%version-%release.


%package -n kernel-modules-infiniband-%flavour
Summary: InfiniBand core and support driver modules
%kernel_modules_package_std_body infiniband
%kernel_modules_package_add_provides ib

%description -n kernel-modules-infiniband-%flavour
This package contains InfiniBand core and support driver modules for the Linux
kernel package %name-%version-%release.


%package -n kernel-modules-ipmi-%flavour
Summary: IPMI core and support driver modules
%kernel_modules_package_std_body ipmi

%description -n kernel-modules-ipmi-%flavour
This package contains IPMI core and support driver modules for the Linux kernel
package %name-%version-%release.


%if_enabled edac
%package -n kernel-modules-edac-%flavour
Summary: EDAC (Error Detection And Correction) driver modules
%kernel_modules_package_std_body ipmi

%description -n kernel-modules-edac-%flavour
This package contains EDAC (Error Detection And Correction) driver modules for
the Linux kernel package %name-%version-%release.
%endif


%if_enabled video
%package -n kernel-modules-video-%flavour
Summary: Video graphics driver modules
%kernel_modules_package_std_body video
%kernel_modules_package_add_provides fb
%kernel_modules_package_add_provides framebuffer

%description -n kernel-modules-video-%flavour
This package contains Video graphics modules for the Linux kernel package
%name-%version-%release.
%endif


%if_enabled irda
%package -n kernel-modules-irda-%flavour
Summary: Linux IrDA (TM) protocols and device drivers modules
%kernel_modules_package_std_body irda

%description -n kernel-modules-irda-%flavour
This package contains IrDA (TM) protocols and device drivers modules for
the Linux kernel package %name-%version-%release.
%endif


%if_enabled joystick
%package -n kernel-modules-joystick-%flavour
Summary: Linux joystick/gamepad driver modules
%kernel_modules_package_std_body joystick
%kernel_modules_package_add_provides gamepad

%description -n kernel-modules-joystick-%flavour
This package contains Linux joystick, 6dof controller, gamepad,
steering wheel, weapon control system or something like driver modules
for the kernel package %name-%version-%release.
%endif


%if_enabled tablet
%package -n kernel-modules-tablet-%flavour
Summary: Linux tablets driver modules
%kernel_modules_package_std_body tablet

%description -n kernel-modules-tablet-%flavour
This package contains Linux tablets driver modules for the kernel package
%name-%version-%release.
%endif


%if_enabled touchscreen
%package -n kernel-modules-touchscreen-%flavour
Summary: Linux touchscreens driver modules
%kernel_modules_package_std_body touchscreen

%description -n kernel-modules-touchscreen-%flavour
This package contains Linux touchscreens driver modules for the kernel
package %name-%version-%release.
%endif


%if_enabled usb_gadget
%package -n kernel-modules-usb-gadget-%flavour
Summary: Linux USB Gadget driver modules
%kernel_modules_package_std_body usb-gadget

%description -n kernel-modules-usb-gadget-%flavour
USB Gadget support on a system involves a peripheral controller,
and the gadget driver using it.
This package contains Linux USB Gadget driver modules for the kernel
package %name-%version-%release.
%endif


%if_enabled atm
%package -n kernel-modules-atm-%flavour
Summary: Linux ATM driver modules
%kernel_modules_package_std_body atm

%description -n kernel-modules-atm-%flavour
ATM is a high-speed networking technology for Local Area Networks and
Wide Area Networks. It uses a fixed packet size and is connection
oriented, allowing for the negotiation of minimum bandwidth requirements.
This package contains ATM driver modules for the Linux kernel package
%name-%version-%release.
%endif


%if_enabled hamradio
%package -n kernel-modules-hamradio-%flavour
Summary: Linux Amateur Radio driver modules
%kernel_modules_package_std_body hamradio

%description -n kernel-modules-hamradio-%flavour
This package contains Amateur Radio driver modules for the Linux kernel
package %name-%version-%release.
%endif


%if_enabled w1
%package -n kernel-modules-w1-%flavour
Summary: Linux Dallas' 1-wire bus driver modules
%kernel_modules_package_std_body w1

%description -n kernel-modules-w1-%flavour
Dallas' 1-wire bus is useful to connect slow 1-pin devices such as
iButtons and thermal sensors.
This package contains Dallas' 1-wire bus driver modules for the Linux
kernel package %name-%version-%release.
%endif


%if_enabled watchdog
%package -n kernel-modules-watchdog-%flavour
Summary: Linux Watchdog Timer driver modules
%kernel_modules_package_std_body watchdog

%description -n kernel-modules-watchdog-%flavour
This package contains Watchdog Timer driver modules for the Linux kernel
package %name-%version-%release.
%endif


%if_enabled mtd
%package -n kernel-modules-mtd-%flavour
Summary: Linux Memory Technology Devices driver and fs modules
%kernel_modules_package_std_body mtd

%description -n kernel-modules-mtd-%flavour
Memory Technology Devices are flash, RAM and similar chips, often used
for solid state file systems on embedded devices.
This package contains Memory Technology Devices driver and fs modules for
the Linux kernel package %name-%version-%release.
%endif


%package -n kernel-modules-fs-extra-%flavour
Summary: Linux extra filesystems drivers modules
%kernel_modules_package_std_body fs-extra

%description -n kernel-modules-fs-extra-%flavour
This package contains extra filesystems drivers modules modules for the
Linux kernel package %name-%version-%release.


%package -n kernel-modules-net-extra-%flavour
Summary: Linux extra net drivers modules
%kernel_modules_package_std_body net-extra

%description -n kernel-modules-net-extra-%flavour
This package contains extra net drivers modules modules for the Linux
kernel package %name-%version-%release.


%if_enabled oss
%package -n kernel-modules-oss-%flavour
Summary: OSS sound driver modules (obsolete)
%kernel_modules_package_std_body oss

%description -n kernel-modules-oss-%flavour
This package contains OSS sound driver modules for the Linux kernel
package %name-%version-%release.
These drivers are declared obsolete by the kernel maintainers; ALSA
drivers should be used instead.  However, the older OSS drivers may be
still useful for some hardware, if the corresponding ALSA drivers do
not work well.
Install this package only if you really need it.
%endif


%if_enabled alsa
%package -n kernel-modules-sound-%flavour
Summary: The Advanced Linux Sound Architecture modules
%kernel_modules_package_std_body sound
%kernel_modules_package_add_provides alsa

%description -n kernel-modules-sound-%flavour
The Advanced Linux Sound Architecture (ALSA) provides audio and MIDI
functionality to the Linux operating system.


%package -n kernel-modules-sound-ext-%flavour
Summary: The Advanced Linux Sound Architecture modules for external adapters
%kernel_modules_package_std_body sound-ext
%kernel_modules_package_add_provides alsa-ext

%description -n kernel-modules-sound-ext-%flavour
The Advanced Linux Sound Architecture (ALSA) provides audio and MIDI
functionality to the Linux operating system.
This package contains modules for extarnal (FireWire, USB) adapters.
%endif


%if_enabled ide
%package -n kernel-modules-ide-%flavour
Summary: The IDE modules (old)
%kernel_modules_package_std_body ide

%description -n kernel-modules-ide-%flavour
Integrated Disk Electronics (IDE aka ATA-1) is a connecting standard for
mass storage units such as hard disks.
These are old IDE modules for your Linux system.
%endif


%if_enabled drm
%package -n kernel-modules-drm-%flavour
Summary: The Direct Rendering Infrastructure modules
%kernel_modules_package_std_body drm

%description -n kernel-modules-drm-%flavour
The Direct Rendering Infrastructure, also known as the DRI, is a framework
for allowing direct access to graphics hardware in a safe and efficient
manner.  It includes changes to the X server, to several client libraries,
and to the kernel.  The first major use for the DRI is to create fast
OpenGL implementations.
These are DRM modules for your Linux system.
%endif


%if_enabled media
%package -n kernel-modules-media-%flavour
Summary: Linux media driver modules
Provides: kernel-modules-lirc-%flavour = %version-%release
# Needed for webcams
Requires: kernel-modules-sound-ext-%flavour = %kversion-%release
%kernel_modules_package_std_body media

%description -n kernel-modules-media-%flavour
V4L kernel modules support for video capture and overlay devices,
webcams and AM/FM radio cards.
DVB kernel modules for DVB/ATSC device handling, software fallbacks etc.
%endif


%if_enabled isdn
%package -n kernel-modules-isdn-%flavour
Summary: The Integrated Services Digital Networks (ISDN) modules
%kernel_modules_package_std_body isdn

%description -n kernel-modules-isdn-%flavour
ISDN ("Integrated Services Digital Networks", called RNIS in France) is
a special type of fully digital telephone service; it's mostly used to
connect to your Internet service provider (with SLIP or PPP). The main
advantage is that the speed is higher than ordinary modem/telephone
connections, and that you can have voice conversations while
downloading stuff. It only works if your computer is equipped with an
ISDN card and both you and your service provider purchased an ISDN line
from the phone company. For details, read
http://www.alumni.caltech.edu/~dank/isdn/ on the WWW.
These are ISDN modules for your Linux system.
%endif


%if_enabled guest
%if "%sub_flavour" != "guest"
%package -n kernel-modules-guest-%flavour
Summary: Linux guest driver modules
%kernel_modules_package_std_body guest

%description -n kernel-modules-guest-%flavour
This package contains Linux guest driver modules for the kernel package
%name-%version-%release.
%endif
%endif


%if_enabled kvm
%package -n kernel-modules-kvm-%flavour
Summary: Kernel-based Virtual Machine (KVM) modules
%kernel_modules_package_std_body kvm

%description -n kernel-modules-kvm-%flavour
Support hosting fully virtualized guest machines using hardware
virtualization extensions. You will need a fairly recent processor
equipped with virtualization extensions.
These are KVM modules for your Linux system.
%endif


%if_enabled hyperv
%package -n kernel-modules-hyperv-%flavour
Summary: Microsoft Hyper-V client drivers modules
%kernel_modules_package_std_body hyperv

%description -n kernel-modules-hyperv-%flavour
Microsoft Hyper-V client drivers modules.
Install this package to run Linux as a Hyper-V client operating system.
%endif


%if_enabled oprofile
%package -n kernel-modules-oprofile-%flavour
Summary: OProfile system profiling module
%kernel_modules_package_std_body oprofile

%description -n kernel-modules-oprofile-%flavour
OProfile is a profiling system capable of profiling the whole system,
include the kernel, kernel modules, libraries, and applications.
These are OProfile module and vmlinux file for your Linux system.
%endif


%package -n kernel-headers-modules-%flavour-%kernel_branch
Summary: Headers and other files needed for building kernel modules
Group: Development/Kernel
%{?kgcc_version:Requires: gcc%kgcc_version}
Provides: kernel-headers-modules-%flavour = %version-%release
Provides: kernel-devel-%flavour = %version-%release
%{?base_flavour:Provides: kernel-devel-%base_flavour = %version-%release}
Provides: kernel-devel = %version-%release
#Obsoletes: kernel-headers-modules-%flavour = %version
AutoProv: no

%description -n kernel-headers-modules-%flavour-%kernel_branch
This package contains header files, Makefiles and other parts of the
Linux kernel build system which are needed to build kernel modules for
the Linux kernel package %name-%version-%release.

If you need to compile a third-party kernel module for the Linux
kernel package %name-%version-%release, install this package
and specify %kbuild_dir as the kernel source directory.


%if_with firmware
%package -n firmware-kernel-%flavour
Summary: Firmware for drivers from %name
Group: System/Kernel and hardware
AutoProv: no
AutoReq: no

%description -n firmware-kernel-%flavour
Firmware for drivers from %name.
%endif


%if_with perf
%package -n perf
Summary: Performance analysis tools for Linux
Group: Development/Tools
AutoReq: yes,noperl,nopython
AutoProv: yes,noperl,nopython

%description -n perf
Performance counters for Linux are are a new kernel-based subsystem that provide
a framework for all things performance analysis. It covers hardware level
(CPU/PMU, Performance Monitoring Unit) features and software features (software
counters, tracepoints) as well.
This package contains performance analysis tools for Linux
%endif


%package -n kernel-headers-%flavour-%kernel_branch
Summary: Header files for the Linux kernel
Group: Development/Kernel
Requires: kernel-headers-common >= 1.1.5
Provides: kernel-headers = %version
%{?base_flavour:Provides: kernel-headers-%base_flavour = %version}
Provides: kernel-headers-%flavour = %version-%release
#Obsoletes: kernel-headers-%flavour = %version
Provides: %kheaders_dir/include
AutoProv: no

%description -n kernel-headers-%flavour-%kernel_branch
This package makes Linux kernel headers corresponding to the Linux
kernel package %name-%version-%release available for building
userspace programs (if this version of headers is selected by
adjust_kernel_headers).


%if_enabled docs
%package -n kernel-doc-%flavour-%kernel_branch
Summary: Linux kernel %kversion-%flavour documentation
%kernel_doc_package_std_body doc

%description -n kernel-doc-%flavour-%kernel_branch
This package contains documentation files for Linux kernel package
kernel-image-%flavour-%kversion-%krelease
The documentation files contained in this package may be different
from the similar files in upstream kernel distributions, because some
patches applied to the corresponding kernel packages may change things
in the kernel and update the documentation to reflect these changes.


%if_enabled htmldocs
%package -n kernel-docbook-%flavour-%kernel_branch
Summary: Linux kernel %kversion-%flavour HTML API documentation
%kernel_doc_package_std_body docbook

%description -n kernel-docbook-%flavour-%kernel_branch
This package contains API documentation HTML files for Linux kernel
package kernel-image-%flavour-%kversion-%krelease
The documentation files contained in this package may be different
from the similar files in upstream kernel distributions, because some
patches applied to the corresponding kernel packages may change things
in the kernel and update the documentation to reflect these changes.
%endif


%if_enabled man
%package -n kernel-man-%flavour-%kernel_branch
Summary: Linux kernel %kversion-%flavour man pages
%kernel_doc_package_std_body man
Conflicts: kernel-man > %version-%release
Conflicts: kernel-man < %version-%release

%description -n kernel-man-%flavour-%kernel_branch
This package contains man pages for Linux kernel package
kernel-image-%flavour-%kversion-%krelease
The man pages contained in this package may be different from the similar
files in upstream kernel distributions, because some patches applied to
the corresponding kernel packages may change things in the kernel and
update the documentation to reflect these changes.
%endif
%endif


%if_with src
%package -n kernel-src-%flavour-%kernel_branch
Summary: Linux kernel %kversion-%flavour sources
Group: Development/Kernel
%{?base_flavour:Provides: kernel-src-%base_flavour = %version-%release}
Provides: kernel-src-%flavour = %version-%release
BuildArch: noarch
AutoProv: no
AutoReq: no

%description -n kernel-src-%flavour-%kernel_branch
This package contains sources for Linux kernel package
kernel-image-%flavour-%kversion-%krelease
%endif


%ifdef extra_mods
%(for m in %extra_mods; do
cat <<__PACKAGE__
%%package -n kernel-modules-$m-%flavour
Summary: $m kernel modules
%kernel_modules_package_std_body $m

%%description -n kernel-modules-$m-%flavour
$m kernel modules.

__PACKAGE__
done)
%endif


%prep
%setup -c -n kernel-image-%flavour-%kversion-%krelease
cd linux-%version
#patch0000 -p1

# fix-arch-*
%patch0011 -p1
%patch0012 -p1
%patch0013 -p1
%patch0014 -p1
%patch0015 -p1
%patch0016 -p1
%patch0017 -p1
%patch0018 -p1
%patch0019 -p1

# fix-arch-x86*
%patch0020 -p1
%patch0021 -p1
%patch0022 -p1
%patch0023 -p1
%patch0024 -p1
%patch0025 -p1
%patch0026 -p1
%patch0027 -p1

%patch0030 -p1
%patch0031 -p1

%patch0040 -p1
%patch0041 -p1
%patch0042 -p1
%patch0043 -p1

# fix-drivers-ata-*
%patch0051 -p1
%patch0052 -p1
%patch0053 -p1
%patch0054 -p1
%patch0055 -p1


# fix-drivers-atm--*
%patch0061 -p1

# fix-drivers-base*
%patch0070 -p1
%patch0071 -p1
%patch0072 -p1

# fix-drivers-block--*
%patch0081 -p1
%patch0082 -p1

# fix-drivers-char-*
%patch0091 -p1
%patch0092 -p1
%patch0093 -p1
%patch0094 -p1

# fix-drivers-connector--*
%patch0101 -p1

# fix-drivers-cpufreq--*
%patch0111 -p1
%patch0112 -p1
%patch0113 -p1
%patch0114 -p1

# fix-drivers-crypto--*
%patch0121 -p1

# fix-drivers-dma-*
%patch0131 -p1
%patch0132 -p1

# fix-drivers-edac--*
%patch0141 -p1
%patch0142 -p1
%patch0143 -p1
%patch0144 -p1
%patch0145 -p1
%patch0146 -p1
%patch0147 -p1
%patch0148 -p1
%patch0149 -p1
%patch0150 -p1
%patch0151 -p1
%patch0152 -p1
%patch0153 -p1

# fix-drivers-gpu-drm--*
%patch0161 -p1
%patch0162 -p1
%patch0163 -p1
%patch0164 -p1

# fix-drivers-hid--*
%patch0171 -p1
%patch0172 -p1

# fix-drivers-hsi*
%patch0181 -p1
%patch0182 -p1

# fix-drivers-hv*
%patch0190 -p1
%patch0191 -p1
%patch0192 -p1

# fix-drivers-hwmon--*
%patch0201 -p1
%patch0202 -p1
%patch0203 -p1
%patch0204 -p1
%patch0205 -p1
%patch0206 -p1
%patch0207 -p1
%patch0208 -p1

# fix-drivers-i2c--*
%patch0211 -p1
%patch0212 -p1
%patch0213 -p1

# fix-drivers-idle--*
%patch0221 -p1

# fix-drivers-infiniband-*
%patch0231 -p1

# fix-drivers-input*
%patch0240 -p1
%patch0241 -p1
%patch0242 -p1

# fix-drivers-isdn-*
%patch0251 -p1
%patch0252 -p1
%patch0253 -p1

%patch0261 -p1
%patch0262 -p1

%patch0271 -p1
%patch0272 -p1

# fix-drivers-media-*
%patch0281 -p1
%patch0282 -p1
%patch0283 -p1
%patch0284 -p1
%patch0285 -p1
%patch0286 -p1
%patch0287 -p1
%patch0288 -p1
%patch0289 -p1
%patch0290 -p1
%patch0291 -p1

# fix-drivers-mfd--*
%patch0301 -p1
%patch0302 -p1
%patch0303 -p1

# fix-drivers-misc--*
%patch0311 -p1

%patch0321 -p1

# fix-drivers-net-ethernet-*
%patch0331 -p1
%patch0332 -p1
%patch0333 -p1
%patch0334 -p1
%patch0335 -p1
%patch0336 -p1
%patch0337 -p1
%patch0338 -p1
%patch0339 -p1

# fix-drivers-net-hyperv-*
%patch0341 -p1

# fix-drivers-net-wireless-*
%patch0351 -p1
%patch0352 -p1
%patch0353 -p1
%patch0354 -p1
%patch0355 -p1

# fix-drivers-platform--*
%patch0361 -p1
%patch0362 -p1
%patch0363 -p1
%patch0364 -p1
%patch0365 -p1

# fix-drivers-rtc--*
%patch0371 -p1

# fix-drivers-scsi-*
%patch0381 -p1
%patch0382 -p1
%patch0383 -p1
%patch0384 -p1
%patch0385 -p1
%patch0386 -p1
%patch0387 -p1
%patch0388 -p1
%patch0389 -p1
%patch0390 -p1
%patch0391 -p1

# fix-drivers-spi--*
%patch0401 -p1

# fix-drivers-tty-*
%patch0411 -p1
%patch0412 -p1

# fix-drivers-usb-*
%patch0421 -p1

# fix-drivers-video-*
%patch0431 -p1
%patch0432 -p1
%patch0433 -p1
%patch0434 -p1

# fix-firmware--*
%patch0441 -p1

# fix-fs*
%patch0450 -p1
%patch0451 -p1
%patch0452 -p1
%patch0453 -p1
%patch0454 -p1
%patch0455 -p1
%patch0456 -p1
%patch0457 -p1

# fix-init
%patch0460 -p1

# fix-kernel*
%patch0470 -p1

# fix-lib*
%patch0480 -p1
%patch0481 -p1

# fix-mm*
%patch0490 -p1
%patch0491 -p1
%patch0492 -p1
%patch0493 -p1
%patch0494 -p1
%patch0495 -p1
%patch0496 -p1
%patch0497 -p1

# fix-net-*
%patch0501 -p1
%patch0502 -p1
%patch0503 -p1
%patch0504 -p1
%patch0505 -p1

%patch0511 -p1

%patch0521 -p1
%patch0522 -p1

%patch0531 -p1
%patch0532 -p1
%patch0533 -p1

%patch0541 -p1
%patch0542 -p1

# fix-virt-kvm*
%patch0550 -p1
%patch0551 -p1


%patch1001 -p1

# feat-block--*
%patch1011 -p1
%patch1012 -p1

# feat-drivers-block--*
%patch1021 -p1
%patch1022 -p1

%patch1031 -p1

%patch1041 -p1

%patch1051 -p1

%patch1061 -p1

%patch1071 -p1

%patch1081 -p1

# feat-drivers-net-*
%patch1091 -p1
%patch1101 -p1
%patch1102 -p1
%patch1103 -p1
%patch1104 -p1
%patch1105 -p1
%patch1106 -p1

# feat-drivers-platform--*
%patch1111 -p1
%patch1112 -p1
%patch1113 -p1

%patch1121 -p1

# feat-drivers-video--*
%patch1131 -p1
%patch1132 -p1

# feat-firmware-*
%patch1141 -p1

# feat-fs-*
%{?_with_lnfs:%patch1151 -p1}
%patch1152 -p1
%patch1153 -p1
%patch1154 -p1
%patch1155 -p1
%patch1156 -p1
%patch1157 -p1
%patch1158 -p1
%patch1159 -p1
%patch1160 -p1
%patch1161 -p1
%patch1162 -p1
%patch1163 -p1
%patch1164 -p1
%patch1165 -p1
%patch1166 -p1
%patch1167 -p1
%patch1168 -p1
%patch1169 -p1

# feat-kernel-power-*
%patch1171 -p1
%patch1172 -p1

%patch1181 -p1

# feat-mm--*
%patch1191 -p1
%patch1192 -p1
%patch1193 -p1
%patch1194 -p1
%patch1195 -p1

# feat-net--*
%patch1201 -p1
%patch1202 -p1
%patch1203 -p1


# get rid of unwanted files resulting from patch fuzz
#find . -name "*.orig" -delete -or -name "*~" -delete

# this file should be usable both with make and sh (for broken modules
# which do not use the kernel makefile system)
%ifdef kgcc_version
GCC_VERSION="%kgcc_version"
%else
GCC_VERSION="$(%__cc --version | head -1 | cut -d' ' -f3 | cut -d. -f1-2)"
%endif
echo -n "export GCC_VERSION=$GCC_VERSION" > gcc_version.inc

sed -i	-e 's/CC.*$(CROSS_COMPILE)gcc/CC\t\t:= '"gcc-$GCC_VERSION/g" Makefile

%{?_with_src:find . -type f -not -empty -not -name '*.orig' -not -name '*~' -not -name '.git*' > ../kernel-src-%flavour.list}

install -m644 %SOURCE1 %SOURCE2 .

%ifdef extra_mods
install -m 0644 %SOURCE10 ./Makefile.external
install -d -m 0755 external
for m in %extra_modules; do
	tar -C external -xf %kernel_src/${m%%=*}-${m#*=}.tar*
done
%endif


%build
cd linux-%version
export ARCH=%base_arch

config_disable()
{
local e
while [ -n "$1" ]; do
	e="$e"'/^CONFIG_'$1'=/s|^\(.*\)=.*$|# \1 is not set|;'
	shift
done
sed -i "$e" .config
}

config_enable()
{
local e s a
while [ -n "$1" ]; do
	a=${1%%=*}
	[ "$a" = "$1" ] && s="=y" || s=
	e="$e"'/^#[[:blank:]]*CONFIG_'$a'[[:blank:]]/s/^#[[:blank:]]*\(CONFIG_'$a'\) .*$/\1'$s'/;'
	shift
done
sed -i "$e" .config
}

if [ -f %flavour-%kernel_branch.%_target_cpu.config ]; then
	cp -vf %flavour-%kernel_branch.%_target_cpu.config .config
else
	cp -vf %flavour-%kernel_branch.%base_arch.config .config
%ifdef kernel_cpu
%if "%base_arch" != "%_target_cpu"
	config_disable %kernel_base_cpu
	config_enable M%kernel_cpu
%endif
%endif
fi

sed -i '/^CONFIG_LOCALVERSION=/s/=.*$/="-%flavour-%krelease"/' .config

%ifarch atom
sed -i '/^CONFIG_NR_CPUS=/s/^\(.*=\).*$/\14/' .config
%endif

%ifarch %intel_64
config_disable CPU_SUP_AMD
%endif

%ifarch %amd_64
config_disable CPU_SUP_INTEL
%endif

%ifarch %ix86
%ifnarch i386 i486 i586
config_disable EISA
%endif
%endif

config_disable \
%if_disabled sound
	SOUND USB_EMI\.* \
%else
	%{?_disable_oss:SOUND_PRIME} %{?_disable_alsa:SND}
%endif
config_disable \
	%{?_disable_smp:SMP} \
	%{?_disable_modversions:MODVERSIONS} \
	%{?_disable_compat:SYSCTL_SYSCALL ACPI_PROC_EVENT COMPAT_VDSO I2C_COMPAT} \
	%{?_disable_numa:NUMA} \
	%{?_disable_video:FB DISPLAY_SUPPORT VIDEO_OUTPUT_CONTROL BACKLIGHT_LCD_SUPPORT} \
	%{?_disable_drm:DRM} \
	%{?_disable_ipv6:IPV6} \
	%{?_disable_edac:EDAC} \
	%{?_disable_can:CAN} \
	%{?_disable_fusion:FUSION} \
	%{?_disable_ide:IDE} \
	%{?_disable_pata:PATA_.\*} \
	%{?_disable_firewire:FIREWIRE} \
	%{?_disable_irda:IRDA} \
	%{?_disable_joystick:INPUT_JOYSTICK} \
	%{?_disable_tablet:INPUT_TABLET} \
	%{?_disable_touchscreen:INPUT_TOUCHSCREEN} \
	%{?_disable_lirc:LIRC} \
	%{?_disable_gameport:GAMEPORT} \
	%{?_disable_usb_gadget:USB_GADGET} \
	%{?_disable_pcmcia:PCCARD PCMCIA} \
	%{?_disable_atm:ATM} \
	%{?_disable_tokenring:TR} \
	%{?_disable_fddi:FDDI} \
	%{?_disable_hamradio:HAMRADIO} \
	%{?_disable_w1:W1} \
	%{?_disable_watchdog:WATCHDOG} \
	%{?_disable_mtd:MTD} \
	%{?_disable_media:MEDIA_SUPPORT} \
	%{?_disable_mmc:MMC} \
	%{?_disable_wireless:WLAN WIRELESS CFG80211 WIMAX} \
	%{?_disable_isdn:ISDN} \
	%{?_disable_telephony:PHONE} \
	%{?_disable_security:SECURITY} \
	%{?_disable_audit:AUDIT} \
	%{?_disable_selinux:SECURITY_SELINUX} \
	%{?_disable_tomoyo:SECURITY_TOMOYO} \
	%{?_disable_apparmor:SECURITY_APPARMOR} \
	%{?_disable_smack:SECURITY_SMACK} \
	%{?_disable_yama:SECURITY_YAMA} \
	%{?_disable_thp:TRANSPARENT_HUGEPAGE} \
	%{?_disable_guest:VIRTIO DRM_KVM_CIRRUS DRM_VMWGFX} \
	%{?_disable_kvm:KVM} \
	%{?_disable_hyperv:HYPERV} \
	%{?_disable_paravirt_guest:PARAVIRT_GUEST} \
	%{?_disable_kvm_guest:KVM_GUEST} \
	%{?_disable_bootsplash:BOOTSPLASH} \
	%{?_disable_zcache:ZCACHE} \
	%{?_disable_pci:PCI} \
	%{?_disable_acpi:ACPI} \
	%{?_disable_math_emu:MATH_EMULATION} \
	%{?_disable_kallsyms:KALLSYMS} \
	%{?_disable_oprofile:PROFILING OPROFILE} \
	%{?_disable_fatelf:BINFMT_FATELF} \
	%{?_enable_ext4_for_ext23:EXT[23]_FS}

config_enable \
%ifarch i386 i486 i586 i686
	X86_GENERIC \
%endif
	%{?_enable_debug_section_mismatch:DEBUG_SECTION_MISMATCH} \
	%{?_enable_modversions:MODVERSIONS} \
	%{?_enable_x32:X86_EXTENDED_PLATFORM} \
	%{?_enable_x86_extended_platform:X86_EXTENDED_PLATFORM} \
	%{?_enable_ext4_for_ext23:EXT4_USE_FOR_EXT23} \
	%{?_enable_mca:MCA} \
	%{?_enable_debugfs:DEBUG_FS} \
	%{?_enable_pcsp:SND_PCSP=m} \
	%{?_enable_secrm:EXT[234]_SECRM FAT_SECRM} \
	%{?_enable_nfs_swap:NFS_SWAP} \
	%{?_enable_lnfs:NFS_V4_SECURITY_LABEL NFSD_V4_SECURITY_LABEL} \
	%{?_enable_kallsyms:KALLSYMS} \
	%allocator

# arch-specific
%ifarch k10
config_disable SENSORS_K8TEMP
%endif
%ifarch corei7 nehalem
config_disable CRYPTO_CRC32C
%endif
%ifarch i386 i486
config_enable CRYPTO_TWOFISH=m CRYPTO_SALSA20=m
%endif

%if_enabled debug
config_enable \
	KALLSYMS_ALL \
	KALLSYMS_EXTRA_PASS \
	DEBUG_KERNEL \
	DETECT_SOFTLOCKUP \
	BOOTPARAM_SOFTLOCKUP_PANIC_VALUE=0 \
	DEBUG_MUTEXES \
	DEBUG_SLAB \
	DEBUG_SLAB_LEAK \
%if 0
	DEBUG_SPINLOCK \
	DEBUG_LOCK_ALLOC \
	PROVE_LOCKING \
	LOCK_STAT \
%endif
	LOCKDEP \
	DEBUG_LOCKDEP \
	DEBUG_SPINLOCK_SLEEP \
	DEBUG_BUGVERBOSE \
	DEBUG_INFO \
	DEBUG_WRITECOUNT \
	FRAME_POINTER
%endif

%ifarch %intel_64 %intel_32 c3 c3_2
sed -i '/^CONFIG_USB_OHCI_HCD=y$/s/=y/=m/' .config
%else
%ifnarch i386 i486 i586 i686 x86_64
sed -i '/^CONFIG_USB_UHCI_HCD=y$/s/=y/=m/' .config
%endif
%endif

echo "Building kernel %kversion-%flavour-%krelease"

%make_build oldconfig
%make_build %{?_enable_verbose:V=1} bzImage modules
%if_with perf
%make_build -C tools/perf %{?_enable_verbose:V=1} \
	prefix=%_prefix perfexecdir=%_libexecdir/perf \
	EXTRA_CFLAGS="%optflags %{?_disable_debug:-g0}"
%make_build -C tools/perf %{?_enable_verbose:V=1} man
%endif

echo "Kernel built %kversion-%flavour-%krelease"

%ifdef extra_mods
%make_build -f Makefile.external %extra_mods
echo "External modules built"
%endif

# psdocs, pdfdocs don't work yet
%{?_enable_htmldocs:%def_enable builddocs}
%{?_enable_man:%def_enable builddocs}
%if_enabled builddocs
%{?_enable_htmldocs:%make_build htmldocs}
%{?_enable_man:%make_build mandocs 2>&1 | tee mandocs.log | grep -vE --line-buffered '^((Warn|Note): (meta author |AUTHOR sect\.):|Note: Writing) '}
echo "Kernel docs built %kversion-%flavour-%krelease"
%endif


%install
export ARCH=%base_arch
pushd linux-%version

install -Dp -m644 System.map %buildroot/boot/System.map-%kversion-%flavour-%krelease
install -Dp -m644 arch/%base_arch/boot/bzImage %buildroot/boot/vmlinuz-%kversion-%flavour-%krelease
install -Dp -m644 .config %buildroot/boot/config-%kversion-%flavour-%krelease

%make_install \
	INSTALL_MOD_PATH=%buildroot \
	INSTALL_FW_PATH=%buildroot%firmware_dir \
	%{!?_enable_debug:%{?strip_mod_opts:INSTALL_MOD_STRIP="%strip_mod_opts"}} \
	modules_install

%ifdef extra_mods
make -f Makefile.external DESTDIR=%buildroot \
	%{!?_enable_debug:%{?strip_mod_opts:INSTALL_MOD_STRIP="%strip_mod_opts"}} \
	INSTALL_MOD_PATH=%modules_dir \
	%extra_mods
%endif

%{?_enable_oprofile:install -m 0644 vmlinux %buildroot%modules_dir/}

install -d -m 0755 %buildroot%kbuild_dir
cp -aL include %buildroot%kbuild_dir/
find %buildroot%kbuild_dir/include/config -type f -empty -delete
find %buildroot%kbuild_dir/include/config -type d -empty -delete
for d in arch/%kernel_arch/include; do
	a="$(dirname "$d")"
	install -d -m 0755 %buildroot%kbuild_dir/$a
	cp -a $d %buildroot%kbuild_dir/$a/
	install -p -m 0644 $a/Makefile* %buildroot%kbuild_dir/$a/
done
find %buildroot%kbuild_dir/{include,arch} -type f -name Kbuild -delete

%if 0
# drivers-headers install
install -d -m 0755 %buildroot%kbuild_dir/{drivers/{scsi,md,usb/core,net/wireless},net/mac80211,kernel,lib}
install -m 0644 drivers/scsi/scsi{{,_typedefs}.h,_module.c} %buildroot%kbuild_dir/drivers/scsi/
install -m 0644 drivers/md/dm*.h %buildroot%kbuild_dir/drivers/md/
install -m 0644 drivers/usb/core/*.h %buildroot%kbuild_dir/drivers/usb/core/
install -m 0644 drivers/net/wireless/Kconfig %buildroot%kbuild_dir/drivers/net/wireless/
install -m 0644 lib/hexdump.c %buildroot%kbuild_dir/lib/
install -m 0644 kernel/workqueue.c %buildroot%kbuild_dir/kernel/
install -m 0644 net/mac80211/{ieee80211_i,sta_info}.h %buildroot%kbuild_dir/net/mac80211/
%endif

# Install files required for building external modules (in addition to headers)
for f in \
	.config \
	Makefile \
	Module.symvers \
	scripts/Kbuild.include \
	scripts/Makefile{,.{build,clean,host,lib,mod*}} \
	scripts/bin2c \
	scripts/check{includes,version}.pl \
	scripts/conmakehash \
	scripts/depmod.sh \
	scripts/extract-ikconfig \
	scripts/gcc-*.sh \
	scripts/kallsyms \
	scripts/makelst \
	scripts/mk{compile_h,makefile,version} \
	scripts/module-common.lds \
	%{?_enable_video:scripts/pnmtologo} \
	scripts/recordmcount.pl \
	scripts/basic/fixdep \
	%{?_enable_modversions:scripts/genksyms/genksyms} \
	scripts/kconfig/conf \
	scripts/mod/{modpost,mk_elfconfig} \
	gcc_version.inc
do
	[ -x "$f" ] && mode=0755 || mode=0644
	install -Dp -m $mode {,%buildroot%kbuild_dir/}$f
done

# Provide kbuild directory with old name (without %%krelease)
ln -s "$(relative %kbuild_dir %old_kbuild_dir)" %buildroot%old_kbuild_dir

# Provide kernel headers for userspace
make -j%__nprocs headers_install INSTALL_HDR_PATH=%buildroot%kheaders_dir
find %buildroot%kheaders_dir -type f -a \( -name .install -o -name ..install.cmd \) -delete

# Fix symlinks to kernel sources in /lib/modules
rm -f %buildroot%modules_dir/{build,source}
ln -s %kbuild_dir %buildroot%modules_dir/build

%if_with perf
%makeinstall_std -C tools/perf prefix=%_prefix perfexecdir=%_libexecdir/perf install install-man
install -d -m 0755 %buildroot%_docdir/perf-%version
install -m 0644 tools/perf/{CREDITS,design.txt,Documentation/examples.txt} %buildroot%_docdir/perf-%version/
%endif

# install documentation
%if_enabled docs
install -d %buildroot%_docdir/kernel-doc-%flavour-%kernel_branch/
for I in Documentation/*; do
	case "$(basename "$I")" in
		DocBook)
%if_enabled htmldocs
			for J in "$I"/*.tmpl; do
				j=$(basename "$J" .tmpl)
				[ -d "$I/$j" ] || continue
				install -d -m 0755 %buildroot%_docdir/kernel-doc-%flavour-%kernel_branch/DocBook/"$j"
				install -m 0644 "$I/$j"/*.html %buildroot%_docdir/kernel-doc-%flavour-%kernel_branch/DocBook/"$j"/
				install -m 0644 "$I/$j.html" %buildroot%_docdir/kernel-doc-%flavour-%kernel_branch/DocBook/
			done
%endif
			;;
		[a-z][a-z]_[A-Z][A-Z]|Makefile|dontdiff) ;;
		*) cp -aL "$I" %buildroot%_docdir/kernel-doc-%flavour-%kernel_branch/ ;;
	esac
done
find %buildroot%_docdir/kernel-doc-%flavour-%kernel_branch -type f -name Makefile -delete
%if_enabled man
install -d %buildroot%kmandir
install -m 0644 Documentation/DocBook/man/* %buildroot%kmandir/
%endif
%endif

%if_with src
install -d -m 0755 %kernel_srcdir
t="%__nprocs"
[ $t -gt 1 ] && XZ="pxz -T$t" || XZ="xz"
tar --transform='s,^,kernel-src-%flavour-%kversion-%krelease/,' \
	--owner=root --group=root --mode=u+w,go-w,go+rX \
	-T ../kernel-src-%flavour.list -cf - | \
	$XZ -8e > %kernel_srcdir/kernel-src-%flavour-%kversion-%krelease.tar.xz
%endif

popd

rm -rf *.rpmmodlist{,~}
gen_rpmmodlist() {
	ls -d $@ | sed 's|^%buildroot||'
}
gen_rpmmodfile() {
	local F=$1.rpmmodlist
	shift
	gen_rpmmodlist $@ > $F
}
gen_rpmmodfile scsi-base \
%if "%sub_flavour" == "guest"
	%buildroot%modules_dir/kernel/drivers/scsi/{{,lib}iscsi*,scsi_transport_iscsi.ko} \
%endif
	%buildroot%modules_dir/kernel/drivers/scsi/{{*_mod,scsi_{tgt,transport_srp}}.ko,osd,device_handler{,/scsi_dh.ko}}
gen_rpmmodlist %buildroot%modules_dir/kernel/drivers/{message/fusion,scsi{,/device_handler}/*,target} | grep -Fxv -f scsi-base.rpmmodlist > scsi.rpmmodlist
mv scsi-base.rpmmodlist scsi-base.rpmmodlist~
gen_rpmmodfile infiniband %buildroot%modules_dir/kernel/{drivers/{infiniband,scsi/scsi_transport_srp.ko},net/{9p/9pnet_rdma.ko,rds,sunrpc/xprtrdma}}
gen_rpmmodfile ipmi %buildroot%modules_dir/kernel/drivers/{acpi/acpi_ipmi,char/ipmi,{acpi/acpi_ipmi,hwmon/i{bm,pmi}*}.ko}
%{?_enable_edac:gen_rpmmodfile edac %buildroot%modules_dir/kernel/drivers/edac}
%{?_enable_atm:gen_rpmmodfile atm %buildroot%modules_dir/kernel/{drivers{,/usb},net}/atm}
%{?_enable_drm:gen_rpmmodfile drm %buildroot%modules_dir/kernel/drivers/gpu/drm}
%{?_enable_fddi:gen_rpmmodfile fddi %buildroot%modules_dir/kernel/{drivers/net,net/802}/fddi*}
%{?_enable_hamradio:gen_rpmmodfile hamradio %buildroot%modules_dir/kernel/{drivers/net/hamradio,net/{netrom,rose,ax25}}}
%{?_enable_irda:gen_rpmmodfile irda %buildroot%modules_dir/kernel/{,drivers/}net/irda}
%{?_enable_isdn:gen_rpmmodfile isdn %buildroot%modules_dir/kernel/{drivers/isdn,net/bluetooth/cmtp}}
%{?_enable_tokenring:gen_rpmmodfile tokenring %buildroot%modules_dir/kernel/{drivers/net/{tokenring,pcmcia/ibmtr_cs.ko},net/802/tr.ko}}
%{?_enable_usb_gadget:gen_rpmmodfile usb-gadget %buildroot%modules_dir/kernel/drivers/usb/gadget}
%{?_enable_video:gen_rpmmodlist %buildroot%modules_dir/kernel/drivers/video/* | grep -xv '%modules_dir/kernel/drivers/video/uvesafb.ko' > video.rpmmodlist}
%{?_enable_watchdog:gen_rpmmodlist %buildroot%modules_dir/kernel/drivers/watchdog/* | grep -xv '%modules_dir/kernel/drivers/watchdog/softdog.ko' > watchdog.rpmmodlist}
for i in %{?_enable_ide:ide} %{?_enable_media:media} %{?_enable_mtd:mtd} %{?_enable_w1:w1}; do
	gen_rpmmodfile $i %buildroot%modules_dir/kernel/drivers/$i
done
for i in %{?_enable_joystick:joystick} %{?_enable_tablet:tablet} %{?_enable_touchscreen:touchscreen}; do
	gen_rpmmodfile $i %buildroot%modules_dir/kernel/drivers/input/$i
done
%if "%sub_flavour" != "guest"
%{?_enable_guest:gen_rpmmodfile guest %buildroot%modules_dir/kernel/{drivers/{virtio,{char{,/hw_random},net,block}/virtio*%{?_enable_drm:,gpu/drm/{cirrus,vmwgfx}}},net/9p/*_virtio.ko}}
%{?_enable_drm:grep -F -f drm.rpmmodlist guest.rpmmodlist | sed 's/^/%%exclude &/' >> drm.rpmmodlist}
%endif
sed 's/^/%%exclude &/' *.rpmmodlist > exclude-drivers.rpmmodlist

%{?_enable_oprofile:%add_verify_elf_skiplist %modules_dir/vmlinux}


%if 0
%post
[ -x /usr/lib/rpm/boot_kernel.filetrigger ] || /sbin/installkernel %kversion-%flavour-%krelease
%endif

%preun
/sbin/installkernel --remove %kversion-%flavour-%krelease


%kernel_modules_package_post scsi

%kernel_modules_package_post infiniband

%kernel_modules_package_post ipmi

%{?_enable_edac:%kernel_modules_package_post edac}

%{?_enable_video:%kernel_modules_package_post video}

%{?_enable_irda:%kernel_modules_package_post irda}

%{?_enable_joystick:%kernel_modules_package_post joystick}

%{?_enable_tablet:%kernel_modules_package_post tablet}

%{?_enable_touchscreen:%kernel_modules_package_post touchscreen}

%{?_enable_usb_gadget:%kernel_modules_package_post usb-gadget}

%{?_enable_atm:%kernel_modules_package_post atm}

%{?_enable_hamradio:%kernel_modules_package_post hamradio}

%{?_enable_w1:%kernel_modules_package_post w1}

%{?_enable_watchdog:%kernel_modules_package_post watchdog}

%{?_enable_mtd:%kernel_modules_package_post mtd}

%kernel_modules_package_post fs-extra

%kernel_modules_package_post net-extra

%{?_enable_oss:%kernel_modules_package_post oss}

%{?_enable_ide:%kernel_modules_package_post ide}

%{?_enable_drm:%kernel_modules_package_post drm}

%{?_enable_media:%kernel_modules_package_post media}

%if_enabled alsa
%kernel_modules_package_post sound

%kernel_modules_package_post sound-ext
%endif

%{?_enable_isdn:%kernel_modules_package_post isdn}

%if "%sub_flavour" != "guest"
%{?_enable_guest:%kernel_modules_package_post guest}
%endif

%{?_enable_kvm:%kernel_modules_package_post kvm}

%{?_enable_hyperv:%kernel_modules_package_post hyperv}

%{?_enable_oprofile:%kernel_modules_package_post oprofile}

%post -n kernel-headers-%flavour-%kernel_branch
%post_kernel_headers %kversion-%flavour-%krelease

%postun -n kernel-headers-%flavour-%kernel_branch
%postun_kernel_headers %kversion-%flavour-%krelease


%ifdef extra_mods
%(for m in %extra_mods; do
cat <<__PACKAGE__
%kernel_modules_package_post $m

__PACKAGE__
done)
%endif


%files -f exclude-drivers.rpmmodlist
/boot/*
%dir %modules_dir
%modules_dir/modules.alias*
%modules_dir/modules.builtin
%modules_dir/modules.dep*
%modules_dir/modules.order
%modules_dir/modules.symbols*
#modules_dir/modules.*map
%ghost %modules_dir/modules.builtin.bin
%ghost %modules_dir/modules.devname
%ghost %modules_dir/modules.softdep
%dir %modules_dir/kernel
%modules_dir/kernel/arch
%modules_dir/kernel/block
%modules_dir/kernel/crypto
%modules_dir/kernel/drivers
%modules_dir/kernel/fs
%modules_dir/kernel/kernel
%modules_dir/kernel/lib
%modules_dir/kernel/net
%modules_dir/kernel/security
%if_enabled sound
%dir %modules_dir/kernel/sound
%{?_enable_pci:%modules_dir/kernel/sound/ac97_bus.ko}
%modules_dir/kernel/sound/soundcore.ko
%exclude %modules_dir/kernel/drivers/usb/misc/emi*
%endif
%{?_enable_kvm:%exclude %modules_dir/kernel/arch/*/kvm}
%if_enabled hyperv
%exclude %modules_dir/kernel/drivers/hv
%exclude %modules_dir/kernel/drivers/hid/hid-hyperv.ko
%exclude %modules_dir/kernel/drivers/net/hyperv
%exclude %modules_dir/kernel/drivers/scsi/hv_storvsc.ko
%endif
%if_enabled oprofile
%exclude %modules_dir/vmlinux
%exclude %modules_dir/kernel/arch/*/oprofile
%endif
# extra fs
%exclude %modules_dir/kernel/fs/afs
%exclude %modules_dir/kernel/fs/adfs
%exclude %modules_dir/kernel/fs/affs
%exclude %modules_dir/kernel/fs/befs
%exclude %modules_dir/kernel/fs/bfs
%exclude %modules_dir/kernel/fs/coda
%exclude %modules_dir/kernel/fs/dlm
%exclude %modules_dir/kernel/fs/efs
%exclude %modules_dir/kernel/fs/exofs
%exclude %modules_dir/kernel/fs/freevxfs
%exclude %modules_dir/kernel/fs/gfs2
%exclude %modules_dir/kernel/fs/hfs*
%exclude %modules_dir/kernel/fs/hpfs
%exclude %modules_dir/kernel/fs/minix
%exclude %modules_dir/kernel/fs/ncpfs
%exclude %modules_dir/kernel/fs/ocfs2
%exclude %modules_dir/kernel/fs/omfs
%exclude %modules_dir/kernel/fs/qnx?
%exclude %modules_dir/kernel/fs/sysv
%if_enabled mtd
%exclude %modules_dir/kernel/fs/jffs2
%exclude %modules_dir/kernel/fs/romfs
%exclude %modules_dir/kernel/fs/ubifs
%endif
# extra net
%exclude %modules_dir/kernel/net/802/p8023.ko
%exclude %modules_dir/kernel/net/appletalk
%exclude %modules_dir/kernel/drivers/net/appletalk
%{?_enable_can:%exclude %modules_dir/kernel/net/can}
%{?_enable_can:%exclude %modules_dir/kernel/drivers/net/can}
%exclude %modules_dir/kernel/net/batman-adv
%exclude %modules_dir/kernel/net/caif
%exclude %modules_dir/kernel/net/dccp
%exclude %modules_dir/kernel/net/decnet
%exclude %modules_dir/kernel/net/econet
%exclude %modules_dir/kernel/net/ieee802154
%exclude %modules_dir/kernel/drivers/ieee802154
%exclude %modules_dir/kernel/net/ipx
%exclude %modules_dir/kernel/net/lapb
%exclude %modules_dir/kernel/net/llc/llc2.ko
%exclude %modules_dir/kernel/net/phonet
%exclude %modules_dir/kernel/drivers/net/usb/cdc-phonet.ko
%exclude %modules_dir/kernel/net/rxrpc
%exclude %modules_dir/kernel/net/sctp
%exclude %modules_dir/kernel/net/tipc
%exclude %modules_dir/kernel/net/wanrouter
%exclude %modules_dir/kernel/drivers/net/wan
%exclude %modules_dir/kernel/drivers/tty/synclink*
%{?_enable_pcmcia:%exclude %modules_dir/kernel/drivers/char/pcmcia/synclink*}
%exclude %modules_dir/kernel/net/x25


%kernel_modules_package_files scsi
%{?_enable_hyperv:%exclude %modules_dir/kernel/drivers/scsi/hv_storvsc.ko}


%kernel_modules_package_files infiniband

%kernel_modules_package_files ipmi

%{?_enable_edac:%kernel_modules_package_files edac}

%{?_enable_video:%kernel_modules_package_files video}

%{?_enable_irda:%kernel_modules_package_files irda}

%{?_enable_joystick:%kernel_modules_package_files joystick}

%{?_enable_tablet:%kernel_modules_package_files tablet}

%{?_enable_touchscreen:%kernel_modules_package_files touchscreen}

%{?_enable_usb_gadget:%kernel_modules_package_files usb-gadget}

%{?_enable_atm:%kernel_modules_package_files atm}

%{?_enable_hamradio:%kernel_modules_package_files hamradio}

%{?_enable_w1:%kernel_modules_package_files w1}

%{?_enable_watchdog:%kernel_modules_package_files watchdog}

%{?_enable_mtd:%kernel_modules_package_files mtd}


%files -n kernel-modules-fs-extra-%flavour
%modules_dir/kernel/fs/afs
%modules_dir/kernel/fs/adfs
%modules_dir/kernel/fs/affs
%modules_dir/kernel/fs/befs
%modules_dir/kernel/fs/bfs
#modules_dir/kernel/fs/ceph
%modules_dir/kernel/fs/coda
%modules_dir/kernel/fs/dlm
%modules_dir/kernel/fs/efs
%modules_dir/kernel/fs/exofs
%modules_dir/kernel/fs/freevxfs
%modules_dir/kernel/fs/gfs2
%modules_dir/kernel/fs/hfs*
%modules_dir/kernel/fs/hpfs
%modules_dir/kernel/fs/minix
%modules_dir/kernel/fs/ncpfs
%modules_dir/kernel/fs/ocfs2
%modules_dir/kernel/fs/omfs
%modules_dir/kernel/fs/qnx?
%modules_dir/kernel/fs/sysv
%if_enabled mtd
%modules_dir/kernel/fs/jffs2
%modules_dir/kernel/fs/romfs
%modules_dir/kernel/fs/ubifs
%endif


%files -n kernel-modules-net-extra-%flavour
%modules_dir/kernel/net/802/p8023.ko
%modules_dir/kernel/net/appletalk
%modules_dir/kernel/drivers/net/appletalk
%if_enabled can
%modules_dir/kernel/net/can
%modules_dir/kernel/drivers/net/can
%endif
%if_enabled tokenring
%{?_enable_pcmcia:%modules_dir/kernel/drivers/net/pcmcia/ibmtr_cs.ko}
%modules_dir/kernel/drivers/net/tokenring
%modules_dir/kernel/net/802/tr.ko
%endif
%if_enabled fddi
%modules_dir/kernel/drivers/net/fddi
%modules_dir/kernel/net/802/fddi.ko
%endif
%modules_dir/kernel/net/batman-adv
%modules_dir/kernel/net/caif
#modules_dir/kernel/net/ceph
%modules_dir/kernel/net/dccp
%modules_dir/kernel/net/decnet
%modules_dir/kernel/net/econet
%modules_dir/kernel/net/ieee802154
%modules_dir/kernel/drivers/ieee802154
%modules_dir/kernel/net/ipx
%modules_dir/kernel/net/lapb
%modules_dir/kernel/net/llc/llc2.ko
%modules_dir/kernel/net/phonet
%modules_dir/kernel/drivers/net/usb/cdc-phonet.ko
%modules_dir/kernel/net/rxrpc
%modules_dir/kernel/net/sctp
%modules_dir/kernel/net/tipc
%modules_dir/kernel/net/wanrouter
%modules_dir/kernel/drivers/net/wan
%modules_dir/kernel/drivers/tty/synclink*
%{?_enable_pcmcia:%modules_dir/kernel/drivers/char/pcmcia/synclink*}
%modules_dir/kernel/net/x25


%if_enabled oss
%files -n kernel-modules-oss-%flavour
%modules_dir/kernel/sound/oss
%modules_dir/kernel/sound/sound_firmware.ko
%endif


%if_enabled alsa
%files -n kernel-modules-sound-%flavour
%modules_dir/kernel/sound
%{?_enable_oss:%exclude %modules_dir/kernel/sound/oss}
%exclude %modules_dir/kernel/sound/*.ko
%exclude %modules_dir/kernel/sound/firewire
%exclude %modules_dir/kernel/sound/usb


%files -n kernel-modules-sound-ext-%flavour
%modules_dir/kernel/sound/firewire
%modules_dir/kernel/sound/usb
%modules_dir/kernel/drivers/usb/misc/emi*
%endif


%if "%sub_flavour" != "guest"
%{?_enable_guest:%kernel_modules_package_files guest}
%{?_enable_drm:%dir %modules_dir/kernel/drivers/gpu/drm}
%endif


%if_enabled kvm
%files -n kernel-modules-kvm-%flavour
%modules_dir/kernel/arch/*/kvm
%endif


%if_enabled hyperv
%files -n kernel-modules-hyperv-%flavour
%modules_dir/kernel/drivers/hv
%modules_dir/kernel/drivers/hid/hid-hyperv.ko
%modules_dir/kernel/drivers/net/hyperv
%modules_dir/kernel/drivers/scsi/hv_storvsc.ko
%endif


%files -n kernel-headers-%flavour-%kernel_branch
%kheaders_dir


%{?_enable_ide:%kernel_modules_package_files ide}

%{?_enable_drm:%kernel_modules_package_files drm}

%{?_enable_media:%kernel_modules_package_files media}

%{?_enable_isdn:%kernel_modules_package_files isdn}


%if_enabled oprofile
%files -n kernel-modules-oprofile-%flavour
%modules_dir/vmlinux
%modules_dir/kernel/arch/*/oprofile
%endif


%if_with firmware
%files -n firmware-kernel-%flavour
%dir /lib/firmware
%dir %firmware_dir
%{?_enable_atm:%{?_enable_pci:%firmware_dir/atm*}}
%firmware_dir/3com
%firmware_dir/acenic
%firmware_dir/adaptec
%firmware_dir/advansys
%firmware_dir/bnx2*
%{?_enable_pcmcia:%firmware_dir/cis}
%firmware_dir/cxgb3
%firmware_dir/e100
%firmware_dir/edgeport
%{?_enable_sound:%firmware_dir/emi*}
%firmware_dir/kaweth
%firmware_dir/keyspan*
%firmware_dir/mts_*
%{?_enable_pcmcia:%firmware_dir/ositech}
%firmware_dir/qlogic
%firmware_dir/rtl_nic
%firmware_dir/sun
%firmware_dir/tehuti
%firmware_dir/ti_*
%firmware_dir/tigon
%{?_enable_hamradio:%firmware_dir/yam}
%ifarch %ix86
%{?_enable_tokenring:%firmware_dir/tr_smctr.*}
%endif
%firmware_dir/whiteheat*
%if_enabled alsa
%{?_enable_pci:%firmware_dir/ess}
%{?_enable_pci:%firmware_dir/korg}
%ifarch %ix86
%firmware_dir/sb16
%endif
%{?_enable_pci:%firmware_dir/yamaha}
%endif
%if_enabled drm
%firmware_dir/matrox
%firmware_dir/r128
%firmware_dir/radeon
%endif
%if_enabled media
%firmware_dir/av7110
%firmware_dir/cpia2
%firmware_dir/ttusb*
%firmware_dir/vicam
%endif
%endif


%if_with perf
%files -n perf
%doc %_docdir/perf-%version
%_bindir/*
%exclude %_libexecdir
%_man1dir/*
%endif


%ifdef extra_mods
%(for m in %extra_mods; do
cat <<__PACKAGE__
%%files -n kernel-modules-$m-%flavour -f linux-%kversion/external/$m.rpmmodlist

__PACKAGE__
done)
%endif


%files -n kernel-headers-modules-%flavour-%kernel_branch
%kbuild_dir
%old_kbuild_dir
%dir %modules_dir
%modules_dir/build


%if_enabled docs
%files -n kernel-doc-%flavour-%kernel_branch
%doc %_docdir/kernel-doc-%flavour-%kernel_branch
%{?_enable_htmldocs:%exclude %_docdir/kernel-doc-%flavour-%kernel_branch/DocBook}


%if_enabled htmldocs
%files -n kernel-docbook-%flavour-%kernel_branch
%doc %dir %_docdir/kernel-doc-%flavour-%kernel_branch
%doc %_docdir/kernel-doc-%flavour-%kernel_branch/DocBook
%endif


%if_enabled man
%files -n kernel-man-%flavour-%kernel_branch
%kmandir
%endif
%endif


%if_with src
%files -n kernel-src-%flavour-%kernel_branch
%_usrsrc/kernel
%endif


%changelog
* Tue Feb 05 2013 Led <led@altlinux.ru> 3.4.29-alt3
- added:
  + fix-fs-quota
- add missed fix-fs-ramfs

* Mon Feb 04 2013 Led <led@altlinux.ru> 3.4.29-alt2
- updated:
  + feat-fs-aufs
- updated configs

* Mon Feb 04 2013 Led <led@altlinux.ru> 3.4.29-alt1
- 3.4.29

* Sun Feb 03 2013 Led <led@altlinux.ru> 3.4.28-alt7
- added:
  + fix-fs-ramfs
  + feat-fs-tmpfs--root

* Sat Feb 02 2013 Led <led@altlinux.ru> 3.4.28-alt6
- updated:
  + fix-drivers-scsi--hv_storvsc
- added:
  + feat-fs-squashfs--write

* Fri Feb 01 2013 Led <led@altlinux.ru> 3.4.28-alt5
- removed:
  + feat-fs-squashfs--write

* Thu Jan 31 2013 Led <led@altlinux.ru> 3.4.28-alt4
- updated:
  + fix-mm--zcache
  + feat-kernel-power-tuxonice
  + feat-mm--zsmalloc

* Tue Jan 29 2013 Led <led@altlinux.ru> 3.4.28-alt3
- updated:
  + fix-arch-x86--mcheck
  + fix-drivers-acpi
  + fix-fs
- added:
  + fix-net-rds--rds_rdma

* Tue Jan 29 2013 Led <led@altlinux.ru> 3.4.28-alt2
- updated:
  + fix-drivers-edac--e752x_edac
  + fix-drivers-edac--i3000_edac
  + fix-drivers-edac--i5000_edac
  + fix-drivers-edac--i5100_edac
  + fix-drivers-edac--i5400_edac
  + fix-drivers-edac--i7300_edac
  + fix-drivers-edac--i82975x_edac
  + fix-drivers-edac--x38_edac
  + fix-mm--zcache

* Mon Jan 28 2013 Led <led@altlinux.ru> 3.4.28-alt1
- 3.4.28
- build with SLAB allocator

* Fri Jan 25 2013 Led <led@altlinux.ru> 3.4.27-alt4
- updated:
  + fix-mm--zcache
- merged kernel-headers-asm-* to kernel-headers-* subpackage
- set kernel-headers-* as no noarch
- kernel-modules-media-* requires kernel-modules-sound-ext-* (for webcams)

* Thu Jan 24 2013 Led <led@altlinux.ru> 3.4.27-alt3
- added:
  + fix-drivers-net-ethernet-alacritech--slicoss
  + fix-drivers-platform--asus_oled
  + feat-drivers-net-ethernet-alacritech
  + feat-drivers-net-ethernet-alacritech--slicoss
  + feat-drivers-platform--asus_oled

* Wed Jan 23 2013 Led <led@altlinux.ru> 3.4.27-alt2
- added:
  + fix-drivers-tty--pty
  + feat-net-ipv4-netfilter--ipt_NETFLOW
- moved content of kernel-modules-lirc-* subpackage to kernel-modules-media-*
  subpackage.
- removed kernel-modules-lirc-* subpackage
- moved qnx6 to kernel-modules-fs-extra-* subpackage

* Tue Jan 22 2013 Led <led@altlinux.ru> 3.4.27-alt1
- 3.4.27

* Mon Jan 21 2013 Led <led@altlinux.ru> 3.4.26-alt5
- added:
  + feat-firmware-rtl_nic

* Mon Jan 21 2013 Led <led@altlinux.ru> 3.4.26-alt4
- added:
  + fix-lib
- spec: support build for corei7 CPU

* Sat Jan 19 2013 Led <led@altlinux.ru> 3.4.26-alt3
- updated:
  + fix-net-bridge--bridge
  + feat-fs-aufs
- removed external modules:
  + fglrx

* Fri Jan 18 2013 Led <led@altlinux.ru> 3.4.26-alt2
- updated:
  + fix-mm--zcache
  + feat-mm--zcache
- disable CRYPTO_FIPS

* Fri Jan 18 2013 Led <led@altlinux.ru> 3.4.26-alt1
- 3.4.26
- removed:
  + fix-drivers-misc--zcache
  + fix-lib--zsmalloc
  + fix-mm--huge_memory
  + fix-mm--mmu
- updated:
  + feat-fs-ext4--richacl
  + feat-kernel-power-tuxonice
- added:
  + fix-mm--zcache
  + fix-mm--zsmalloc
  + feat-drivers-block--zram
  + feat-drivers-video--xgifb
  + feat-kernel-power-tuxonice--frontswap
  + feat-mm--frontswap
  + feat-mm--zcache
  + feat-mm--zsmalloc
- disabled compat (turn off some COMPAT options in .config)

* Thu Jan 17 2013 Led <led@altlinux.ru> 3.4.25-alt2
- added:
  + fix-arch-x86-cpu
  + fix-drivers-net-ethernet-via--via-rhine

* Wed Jan 16 2013 Led <led@altlinux.ru> 3.4.25-alt1
- initial build based on kernel-image-led-ws-3.0.57-alt11 spec
