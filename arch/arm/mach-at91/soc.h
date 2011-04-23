/*
 * Copyright (C) 2007 Atmel Corporation.
 * Copyright (C) 2011 Jean-Christophe PLAGNIOL-VILLARD <plagnioj@jcrosoft.com>
 *
 * Under GPLv2
 *
 */

struct at91_soc {
	char *name;
	unsigned int *default_irq_priority;

	void (*init)(unsigned long main_clock);
};

extern struct at91_soc at91rm9200_soc;
extern struct at91_soc at91sam9260_soc;
extern struct at91_soc at91sam9261_soc;
extern struct at91_soc at91sam9263_soc;
extern struct at91_soc at91sam9rl_soc;
extern struct at91_soc at91sam9g45_soc;
extern struct at91_soc at91cap9_soc;
extern struct at91_soc at572d940hf_soc;
