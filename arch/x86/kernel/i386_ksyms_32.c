#include <linux/module.h>

#include <asm/checksum.h>
#include <asm/pgtable.h>
#include <asm/desc.h>
#include <asm/ftrace.h>

#ifdef CONFIG_FTRACE
/* mcount is defined in assembly */
EXPORT_SYMBOL(mcount);
#endif

EXPORT_SYMBOL_GPL(cpu_gdt_table);

/* Networking helper routines. */
EXPORT_SYMBOL(csum_partial_copy_generic);
EXPORT_SYMBOL(csum_partial_copy_generic_to_user);
EXPORT_SYMBOL(csum_partial_copy_generic_from_user);

EXPORT_SYMBOL(__get_user_1);
EXPORT_SYMBOL(__get_user_2);
EXPORT_SYMBOL(__get_user_4);

EXPORT_SYMBOL(__put_user_1);
EXPORT_SYMBOL(__put_user_2);
EXPORT_SYMBOL(__put_user_4);
EXPORT_SYMBOL(__put_user_8);

EXPORT_SYMBOL(strstr);

EXPORT_SYMBOL(csum_partial);
EXPORT_SYMBOL(empty_zero_page);

#ifdef CONFIG_PAX_KERNEXEC
EXPORT_SYMBOL(KERNEL_TEXT_OFFSET);
#endif
