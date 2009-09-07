/*
 *   Creation Date: <1997/07/02 19:52:18 samuel>
 *   Time-stamp: <2004/04/03 18:29:26 samuel>
 *
 *	<extralib.h>
 *
 *
 *
 *   Copyright (C) 2001, 2002, 2003, 2004 Samuel Rydh (samuel@ibrium.se)
 *
 *   This program is free software; you can redistribute it and/or
 *   modify it under the terms of the GNU General Public License
 *   as published by the Free Software Foundation
 *
 */

#ifndef _H_EXTRALIB
#define _H_EXTRALIB

#define CLEAR( x ) memset( &x, 0, sizeof(x))

/* in extralib.h */
extern int	ilog2( int val );

extern char	*num_to_string( ulong num );
extern int 	is_number_str( char *str );
extern ulong	string_to_ulong( char * );
extern ulong	hexbin( int num );

extern char	*strncpy0( char *dest, const char *str, size_t n );
extern char	*strncat0( char *dest, const char *str, size_t n );
extern char	*strncat3( char *dest, const char *s1, const char *s2, size_t n );
extern char	*strnpad( char *dest, const char *s1, size_t n );

struct iovec;
extern int	memcpy_tovec( const struct iovec *vec, size_t nvec, const char *src, unsigned int len );
extern int	memcpy_fromvec( char *dst, const struct iovec *vec, size_t nvec, unsigned int len );
extern int	iovec_getbyte( int offs, const struct iovec *vec, size_t nvec );
extern int	iovec_skip( int skip, struct iovec *vec, size_t nvec );

extern void	open_logfile( const char *filename );
extern void	close_logfile( void );

#define __printf_format	__attribute__ ((format (printf, 1, 2)))
extern int	printm( const char *fmt,...) __printf_format;
extern int	aprint( const char *fmt,... ) __printf_format;
extern void	perrorm(const char *fmt,... ) __printf_format;
extern void	fatal(const char *fmt,... ) __printf_format __attribute__((noreturn));
#define 	fatal_err(fmt, args...) \
		do { printm("Fatal error: "); perrorm(fmt, ## args ); exit(1); } while(0)
extern void	fail_nil( void *p );
extern void	set_print_hook( int (*hook)(char *buf) );
extern void	set_print_guard( void (*hook)(void) );

extern int	script_exec( char *name, char *arg1, char *arg2 );

/* in unicode.c */
extern int	asc2uni( unsigned char *ustr, const char *astr, int maxlen );
extern int	uni2asc( char *astr, const unsigned char *ustr, int ustrlen, int maxlen );

/* in backtrace.c */
extern void	print_btrace_sym( ulong addr, const char *sym_filename );

/* color output support */
#define C_GREEN         "\33[1;32m"
#define C_YELLOW        "\33[1;33m"
#define C_NORMAL        "\33[0;39m"
#define C_RED           "\33[1;31m"

#endif   /* _H_EXTRALIB */
