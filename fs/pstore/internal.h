extern void	pstore_get_records(void);
extern int	pstore_mkfile(char *name, char *data, size_t size,
			      struct timespec time, void *private);
extern void	pstore_erase(void *private);
extern int	pstore_is_mounted(void);
