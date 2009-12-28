/*
 * arch/x86_64/kernel/stacktrace.c
 *
 * Stack trace management functions
 *
 *  Copyright (C) 2006 Red Hat, Inc., Ingo Molnar <mingo@redhat.com>
 */
#include <linux/sched.h>
#include <linux/stacktrace.h>
#include <linux/module.h>
#include <asm/stacktrace.h>

/*
 * Save stack-backtrace addresses into a stack_trace buffer.
 */
void save_stack_trace(struct stack_trace *trace)
{
}
EXPORT_SYMBOL(save_stack_trace);

void __ia64_save_stack_nonlocal(struct stack_trace *trace)
{
}
EXPORT_SYMBOL(__ia64_save_stack_nonlocal);
