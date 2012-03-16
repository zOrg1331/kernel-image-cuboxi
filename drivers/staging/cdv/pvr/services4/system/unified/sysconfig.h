/**********************************************************************
 *
 * Copyright(c) 2008 Imagination Technologies Ltd. All rights reserved.
 * 
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 * 
 * This program is distributed in the hope it will be useful but, except 
 * as otherwise stated in writing, without any warranty; without even the 
 * implied warranty of merchantability or fitness for a particular purpose. 
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
 * 
 * The full GNU General Public License is included in this distribution in
 * the file called "COPYING".
 *
 * Contact Information:
 * Imagination Technologies Ltd. <gpl-support@imgtec.com>
 * Home Park Estate, Kings Langley, Herts, WD4 8LZ, UK 
 *
 ******************************************************************************/

#if !defined(__SOCCONFIG_H__)
#define __SOCCONFIG_H__
#include "syscommon.h"
#include "extsyscache.h"

#define VS_PRODUCT_NAME	"SGX Cedarview"

#define SYS_NO_POWER_LOCK_TIMEOUT

/*#define SGX_FEATURE_HOST_PORT */

#define SYS_SGX_USSE_COUNT					(2)

#define POULSBO_REGS_OFFSET	0x00000
#define POULSBO_REG_SIZE	0x2100	

#define SGX_REGS_OFFSET		0x80000
#define PSB_SGX_REGS_OFFSET	0x40000
#define SGX_REG_SIZE 		0x4000
#define MSVDX_REGS_OFFSET	0x90000

#ifdef SUPPORT_MSVDX
#define	POULSBO_MAX_OFFSET	(MSVDX_REGS_OFFSET + MSVDX_REG_SIZE)
#else
#define	POULSBO_MAX_OFFSET	(SGX_REGS_OFFSET + SGX_REG_SIZE)
#define	PSB_POULSBO_MAX_OFFSET	(PSB_SGX_REGS_OFFSET + SGX_REG_SIZE)
#endif

#define SYS_SGX_DEV_VENDOR_ID		0x8086
#define PSB_SYS_SGX_DEV_DEVICE_ID_1	0x8108
#define PSB_SYS_SGX_DEV_DEVICE_ID_2	0x8109

#define SYS_SGX_DEV_DEVICE_ID		0x4102

#define SYS_SGX_DEVICE_IDS \
    {0x8086, 0x8108, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_PSB_8108}, \
    {0x8086, 0x8109, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_PSB_8109}, \
    {0x8086, 0x4100, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x4101, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x4102, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x4103, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x4104, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x4105, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x4106, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x4107, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MRST_4100}, \
    {0x8086, 0x0130, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0131, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0132, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0133, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0134, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0135, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0136, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0137, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_MDFLD_0130}, \
    {0x8086, 0x0BE0, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0x8086, 0x0BE1, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0x8086, 0x0BE2, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0x8086, 0x0BE3, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0x8086, 0x0BE4, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0x8086, 0x0BE5, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0x8086, 0x0BE6, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0x8086, 0x0BE7, PCI_ANY_ID, PCI_ANY_ID, 0, 0, CHIP_CDV_0BE0}, \
    {0, 0, 0}


#define MMADR_INDEX			4
#define IOPORT_INDEX		5
#define GMADR_INDEX			6
#define MMUADR_INDEX		7
#define FBADR_INDEX			23
#define FBSIZE_INDEX		24

#define DISPLAY_SURFACE_SIZE        (4 * 1024 * 1024)

#define DEVICE_SGX_INTERRUPT		(1<<0)
#define DEVICE_MSVDX_INTERRUPT		(1<<1)
#define DEVICE_DISP_INTERRUPT		(1<<2)
#define DEVICE_TOPAZ_INTERRUPT		(1<<3)

#define POULSBO_INTERRUPT_ENABLE_REG		0x20A0
#define POULSBO_INTERRUPT_IDENTITY_REG		0x20A4
#define POULSBO_INTERRUPT_MASK_REG			0x20A8
#define POULSBO_INTERRUPT_STATUS_REG		0x20AC

#define POULSBO_DISP_MASK					(1<<17)
#define POULSBO_THALIA_MASK					(1<<18)
#define POULSBO_MSVDX_MASK					(1<<19)
#define POULSBO_VSYNC_PIPEA_VBLANK_MASK		(1<<7)
#define POULSBO_VSYNC_PIPEA_EVENT_MASK		(1<<6)
#define POULSBO_VSYNC_PIPEB_VBLANK_MASK		(1<<5)
#define POULSBO_VSYNC_PIPEB_EVENT_MASK		(1<<4)

#define POULSBO_DISPLAY_REGS_OFFSET			0x70000
#define POULSBO_DISPLAY_REG_SIZE			0x2000		

#define POULSBO_DISPLAY_A_CONFIG			0x00008
#define POULSBO_DISPLAY_A_STATUS_SELECT		0x00024
#define POULSBO_DISPLAY_B_CONFIG			0x01008
#define POULSBO_DISPLAY_B_STATUS_SELECT		0x01024

#define POULSBO_DISPLAY_PIPE_ENABLE			(1<<31)
#define POULSBO_DISPLAY_VSYNC_STS_EN		(1<<25)
#define POULSBO_DISPLAY_VSYNC_STS			(1<<9)

#if defined(SGX_FEATURE_HOST_PORT)
	#define SYS_SGX_HP_SIZE		0x8000000
	#define PSB_SYS_SGX_HP_SIZE	0x4000000
	
	#define SYS_SGX_HOSTPORT_BASE_DEVVADDR 0xD0000000
	#if defined(FIX_HW_BRN_22997) && defined(FIX_HW_BRN_23030)
		


		#define SYS_SGX_HOSTPORT_BRN23030_OFFSET 0x7C00000
	#endif
#endif

 
typedef struct
{
	union
	{
		IMG_UINT8	aui8PCISpace[256];
		IMG_UINT16	aui16PCISpace[128];
		IMG_UINT32	aui32PCISpace[64];
		struct  
		{
			IMG_UINT16	ui16VenID;
			IMG_UINT16	ui16DevID;
			IMG_UINT16	ui16PCICmd;
			IMG_UINT16	ui16PCIStatus;
		}s;
	}u;
} PCICONFIG_SPACE, *PPCICONFIG_SPACE;

#endif	
