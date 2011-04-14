/*
 * Common module linker script, always used when linking a module.
 * Archs are free to supply their own linker scripts.  ld will
 * combine them automatically.
 */
SECTIONS {
	/DISCARD/ : { *(.discard) }

	__ksymtab				: { *(SORT(___ksymtab__*)) }
	__ksymtab_gpl			: { *(SORT(___ksymtab_gpl__*)) }
	__ksymtab_unused		: { *(SORT(___ksymtab_unused__*)) }
	__ksymtab_unused_gpl	: { *(SORT(___ksymtab_unused_gpl__*)) }
	__ksymtab_gpl_future	: { *(SORT(___ksymtab_gpl_future__*)) }
	__kcrctab				: { *(SORT(___kcrctab__*)) }
	__kcrctab_gpl			: { *(SORT(___kcrctab_gpl__*)) }
	__kcrctab_unused		: { *(SORT(___kcrctab_unused__*)) }
	__kcrctab_unused_gpl	: { *(SORT(___kcrctab_unused_gpl__*)) }
	__kcrctab_gpl_future	: { *(SORT(___kcrctab_gpl_future__*)) }
}
