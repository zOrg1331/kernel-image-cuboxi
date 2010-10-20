#ifndef HERR_INTERNAL_H
#define HERR_INTERNAL_H

#define HERR_NOTIFY_BIT			0

extern unsigned long herr_flags;

int herr_persist_read_done(void);
ssize_t herr_persist_peek_user(u64 *record_id, char __user *ercd,
			       size_t bufsiz);
int herr_persist_clear(u64 record_id);
#endif /* HERR_INTERNAL_H */
