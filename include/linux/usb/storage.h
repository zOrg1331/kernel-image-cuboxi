/*
 * linux/usb/storage.h
 *
 * Copyright Matthew Wilcox for Intel Corp, 2010
 *
 * This file contains definitions taken from the
 * USB Mass Storage Class Specification Overview
 *
 * Distributed under the terms of the GNU GPL, version two.
 */

/* Storage subclass codes */

#define US_SC_RBC	0x01		/* Typically, flash devices */
#define US_SC_8020	0x02		/* CD-ROM */
#define US_SC_QIC	0x03		/* QIC-157 Tapes */
#define US_SC_UFI	0x04		/* Floppy */
#define US_SC_8070	0x05		/* Removable media */
#define US_SC_SCSI	0x06		/* Transparent */
#define US_SC_LOCKABLE	0x07		/* Password-protected */

#define US_SC_ISD200    0xf0		/* ISD200 ATA */
#define US_SC_CYP_ATACB 0xf1		/* Cypress ATACB */
#define US_SC_DEVICE	0xff		/* Use device's value */

/* Storage protocol codes */

#define US_PR_CBI	0x00		/* Control/Bulk/Interrupt */
#define US_PR_CB	0x01		/* Control/Bulk w/o interrupt */
#define US_PR_BULK	0x50		/* bulk only */
#define US_PR_UAS	0x62		/* USB Attached SCSI */

#define US_PR_USBAT	0x80		/* SCM-ATAPI bridge */
#define US_PR_EUSB_SDDR09	0x81	/* SCM-SCSI bridge for SDDR-09 */
#define US_PR_SDDR55	0x82		/* SDDR-55 (made up) */
#define US_PR_DPCM_USB  0xf0		/* Combination CB/SDDR09 */
#define US_PR_FREECOM   0xf1		/* Freecom */
#define US_PR_DATAFAB   0xf2		/* Datafab chipsets */
#define US_PR_JUMPSHOT  0xf3		/* Lexar Jumpshot */
#define US_PR_ALAUDA    0xf4		/* Alauda chipsets */
#define US_PR_KARMA     0xf5		/* Rio Karma */

#define US_PR_DEVICE	0xff		/* Use device's value */

