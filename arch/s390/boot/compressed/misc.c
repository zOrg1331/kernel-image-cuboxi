/*
 * Definitions and wrapper functions for kernel decompressor
 *
 * Copyright IBM Corp. 2010
 *
 * Author(s): Martin Schwidefsky <schwidefsky@de.ibm.com>
 */

#include <asm/uaccess.h>
#include <asm/page.h>
#include "sizes.h"

/*
 * gzip declarations
 */
#define STATIC static

#undef memset
#undef memcpy
#define memzero(s, n) memset((s), 0, (n))

/* Symbols defined by linker scripts */
extern char input_data[];
extern int input_len;
extern int _text;
extern int _end;

static void error(char *m);

static unsigned long free_mem_ptr;
static unsigned long free_mem_end_ptr;

#ifdef CONFIG_HAVE_KERNEL_BZIP2
#define HEAP_SIZE	0x400000
#else
#define HEAP_SIZE	0x10000
#endif

#ifdef CONFIG_KERNEL_GZIP
#include "../../../../lib/decompress_inflate.c"
#endif

#ifdef CONFIG_KERNEL_BZIP2
#include "../../../../lib/decompress_bunzip2.c"
#endif

#ifdef CONFIG_KERNEL_LZMA
#include "../../../../lib/decompress_unlzma.c"
#endif

extern _sclp_print_early(const char *);

int puts(const char *s)
{
	_sclp_print_early(s);
	return 0;
}

void *memset(void* s, int c, size_t n)
{
	char *xs;

	if (c == 0)
		return __builtin_memset(s, 0, n);

	xs = (char *) s;
	if (n > 0)
		do {
			*xs++ = c;
		} while (--n > 0);
	return s;
}

void *memcpy(void* __dest, __const void* __src, size_t __n)
{
	return __builtin_memcpy(__dest, __src, __n);
}

static void error(char *x)
{
	unsigned long psw[2] = { 0x000a0000UL, 0xdeadbeefUL };

	puts("\n\n");
	puts(x);
	puts("\n\n -- System halted");

	asm volatile("lpsw 0(%0)" : : "a" (&psw));
}

unsigned long decompress_kernel(void)
{
	unsigned long output_addr;
	unsigned char *output;

	free_mem_ptr = (unsigned long)&_end;
	free_mem_end_ptr = free_mem_ptr + HEAP_SIZE;
	output = (unsigned char *) ((free_mem_end_ptr + 4095UL) & -4096UL);

#ifdef CONFIG_BLK_DEV_INITRD
	/*
	 * Move the initrd right behind the end of the decompressed
	 * kernel image.
	 */
	if (INITRD_START && INITRD_SIZE &&
	    INITRD_START < (unsigned long) output + SZ__bss_start) {
		memcpy(output + SZ__bss_start,
		       (void *) INITRD_START, INITRD_SIZE);
		INITRD_START = (unsigned long) output + SZ__bss_start;
	}
#endif

	puts("Uncompressing Linux... ");
	decompress(input_data, input_len, NULL, NULL, output, NULL, error);
	puts("Ok, booting the kernel.\n");
	return (unsigned long) output;
}

