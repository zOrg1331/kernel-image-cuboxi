#ifndef LINUX_MOD_EXPORT_H
#define LINUX_MOD_EXPORT_H
/*
 * Define EXPORT_SYMBOL() and friends for kernel modules.
 *
 * Under __GENKSYMS__ these definitions are skipped, making it possible to
 * scan for EXPORT_SYMBOL() in preprocessed C files.
 *
 * Under __MODPOST_EXPORTS__ we skip C definitions and define __EXPORT_SYMBOL()
 * in arch-independent assembly code.  This makes it possible to construct
 * sorted symbol tables.
 */

#ifndef __GENKSYMS__
#ifndef __MODPOST_EXPORTS__

#include <linux/compiler.h>

/* Some toolchains use a `_' prefix for all user symbols. */
#ifdef CONFIG_SYMBOL_PREFIX
#define MODULE_SYMBOL_PREFIX CONFIG_SYMBOL_PREFIX
#else
#define MODULE_SYMBOL_PREFIX ""
#endif

#ifdef CONFIG_MODULES

struct kernel_symbol {
	unsigned long value;
	const char *name;
};

#ifdef CONFIG_MODVERSIONS
/* Mark the CRC weak since genksyms apparently decides not to
 * generate a checksums for some symbols */
#define __CRC_SYMBOL(sym, sec)					\
	extern void *__crc_##sym __attribute__((weak));		\
	static const unsigned long __kcrctab_##sym		\
	__used							\
	__attribute__((section("__kcrctab" sec), unused))	\
	= (unsigned long) &__crc_##sym;
#else
#define __CRC_SYMBOL(sym, sec)
#endif

/* For every exported symbol, place a struct in the __ksymtab section */
#define __EXPORT_SYMBOL(sym, sec)				\
	extern typeof(sym) sym;					\
	__CRC_SYMBOL(sym, sec)					\
	static const char __kstrtab_##sym[]			\
	__attribute__((section("__ksymtab_strings"), aligned(1))) \
	= MODULE_SYMBOL_PREFIX #sym;                    	\
	static const struct kernel_symbol __ksymtab_##sym	\
	__used							\
	__attribute__((section("__ksymtab" sec), unused))	\
	= { (unsigned long)&sym, __kstrtab_##sym }

#define EXPORT_SYMBOL(sym)					\
	__EXPORT_SYMBOL(sym, "")

#define EXPORT_SYMBOL_GPL(sym)					\
	__EXPORT_SYMBOL(sym, "_gpl")

#define EXPORT_SYMBOL_GPL_FUTURE(sym)				\
	__EXPORT_SYMBOL(sym, "_gpl_future")

#ifdef CONFIG_UNUSED_SYMBOLS
#define EXPORT_UNUSED_SYMBOL(sym) __EXPORT_SYMBOL(sym, "_unused")
#define EXPORT_UNUSED_SYMBOL_GPL(sym) __EXPORT_SYMBOL(sym, "_unused_gpl")
#else
#define EXPORT_UNUSED_SYMBOL(sym)
#define EXPORT_UNUSED_SYMBOL_GPL(sym)
#endif

#else /* !CONFIG_MODULES */

#define EXPORT_SYMBOL(sym)
#define EXPORT_SYMBOL_GPL(sym)
#define EXPORT_SYMBOL_GPL_FUTURE(sym)
#define EXPORT_UNUSED_SYMBOL(sym)
#define EXPORT_UNUSED_SYMBOL_GPL(sym)

#endif /* CONFIG_MODULES */

#else /* __MODPOST_EXPORTS__ */
/*
 * Here is the arch-independent assembly version, used in .tmp_exports-asm.S.
 *
 * We use CPP macros since they are more familiar than assembly macros.
 * Note that CPP macros eat newlines, so each pseudo-instruction must be
 * terminated by a semicolon.
 */

#include <asm/bitsperlong.h>
#include <linux/stringify.h>

#if BITS_PER_LONG == 64
#define PTR .quad
#define ALGN .balign 8
#else
#define PTR .long
#define ALGN .balign 4
#endif

/* build system gives us an unstringified version of CONFIG_SYMBOL_PREFIX */
#ifndef SYMBOL_PREFIX
#define SYM(sym) sym
#else
#define PASTE2(x,y) x##y
#define PASTE(x,y) PASTE2(x,y)
#define SYM(sym) PASTE(SYMBOL_PREFIX, sym)
#endif


#ifdef CONFIG_MODVERSIONS
#define __CRC_SYMBOL(sym, crcsec)				\
	.globl SYM(__crc_##sym);				\
	.weak SYM(__crc_##sym);					\
	.pushsection crcsec, "a";				\
	ALGN;							\
	SYM(__kcrctab_##sym):					\
	PTR SYM(__crc_##sym);					\
	.popsection;
#else
#define __CRC_SYMBOL(sym, section)
#endif

#define __EXPORT_SYMBOL(sym, sec, strsec, crcsec)		\
	.globl SYM(sym);					\
								\
	__CRC_SYMBOL(sym, crcsec)				\
								\
	.pushsection strsec, "a";				\
	SYM(__kstrtab_##sym):					\
	.asciz __stringify(SYM(sym));				\
	.popsection;						\
								\
	.pushsection sec, "a";					\
	ALGN;							\
	SYM(__ksymtab_##sym):					\
	PTR SYM(sym);						\
	PTR SYM(__kstrtab_##sym);				\
	.popsection;

#endif /* __MODPOST_EXPORTS__ */

#endif /* __GENKSYMS__ */

#endif /* LINUX_MOD_EXPORT_H */
