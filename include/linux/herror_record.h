#ifndef LINUX_HERROR_RECORD_H
#define LINUX_HERROR_RECORD_H

#include <linux/types.h>

/*
 * Hardware Error Record Definition
 */
enum herr_severity {
	HERR_SEV_NONE,
	HERR_SEV_CORRECTED,
	HERR_SEV_RECOVERABLE,
	HERR_SEV_FATAL,
};

#define HERR_RCD_REV1_0		0x0100
#define HERR_MIN_ALIGN_ORDER	3
#define HERR_MIN_ALIGN		(1 << HERR_MIN_ALIGN_ORDER)

enum herr_record_flags {
	HERR_RCD_PREV		= 0x0001, /* record is for previous boot */
	HERR_RCD_PERSIST	= 0x0002, /* record is from flash, need to be
					   * cleared after writing to disk */
};

/*
 * sizeof(struct herr_record) and sizeof(struct herr_section) should
 * be multiple of HERR_MIN_ALIGN to make error record packing easier.
 */
struct herr_record {
	__u16	length;
	__u16	flags;
	__u16	rev;
	__u8	severity;
	__u8	pad1;
	__u64	id;
	__u64	timestamp;
	__u8	data[0];
};

/* Section type ID are allocated here */
enum herr_section_type_id {
	/* 0x0 - 0xff are reserved by core */
	/* 0x100 - 0x1ff are allocated to CPER */
	HERR_TYPE_CPER		= 0x0100,
	HERR_TYPE_GESR		= 0x0110, /* acpi_hest_generic_status */
	/* 0x200 - 0x2ff are allocated to PCI/PCIe subsystem */
	HERR_TYPE_PCIE_AER	= 0x0200,
};

struct herr_section {
	__u16	length;
	__u16	flags;
	__u32	type;
	__u8	data[0];
};

#define herr_record_for_each_section(ercd, esec)		\
	for ((esec) = (struct herr_section *)(ercd)->data;	\
	     (void *)(esec) - (void *)(ercd) < (ercd)->length;	\
	     (esec) = (void *)(esec) + (esec)->length)

#define HERR_SEC_LEN_ROUND(len)						\
	(((len) + HERR_MIN_ALIGN - 1) & ~(HERR_MIN_ALIGN - 1))
#define HERR_SEC_LEN(type)						\
	(sizeof(struct herr_section) + HERR_SEC_LEN_ROUND(sizeof(type)))

#define HERR_RECORD_LEN_ROUND1(sec_len1)				\
	(sizeof(struct herr_record) + HERR_SEC_LEN_ROUND(sec_len1))
#define HERR_RECORD_LEN_ROUND2(sec_len1, sec_len2)			\
	(sizeof(struct herr_record) + HERR_SEC_LEN_ROUND(sec_len1) +	\
	 HERR_SEC_LEN_ROUND(sec_len2))
#define HERR_RECORD_LEN_ROUND3(sec_len1, sec_len2, sec_len3)		\
	(sizeof(struct herr_record) + HERR_SEC_LEN_ROUND(sec_len1) +	\
	 HERR_SEC_LEN_ROUND(sec_len2) + HERR_SEC_LEN_ROUND(sec_len3))

#define HERR_RECORD_LEN1(sec_type1)				\
	(sizeof(struct herr_record) + HERR_SEC_LEN(sec_type1))
#define HERR_RECORD_LEN2(sec_type1, sec_type2)			\
	(sizeof(struct herr_record) + HERR_SEC_LEN(sec_type1) + \
	 HERR_SEC_LEN(sec_type2))
#define HERR_RECORD_LEN3(sec_type1, sec_type2, sec_type3)	\
	(sizeof(struct herr_record) + HERR_SEC_LEN(sec_type1) + \
	 HERR_SEC_LEN(sec_type2) + HERR_SEC_LEN(sec_type3))

static inline struct herr_section *herr_first_sec(struct herr_record *ercd)
{
	return (struct herr_section *)(ercd + 1);
}

static inline struct herr_section *herr_next_sec(struct herr_section *esrc)
{
	return (void *)esrc + esrc->length;
}

static inline void *herr_sec_data(struct herr_section *esec)
{
	return (void *)(esec + 1);
}
#endif
