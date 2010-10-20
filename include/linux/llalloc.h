#ifndef LLALLOC_H
#define LLALLOC_H

struct ll_pool;

struct ll_pool_chunk {
	atomic_t avail;
	void *data;
	struct ll_pool *pool;
	unsigned long bitmap[0];
};

struct ll_pool {
	int min_alloc_order;
	int chunk_order;
	int chunk_num;
	struct ll_pool_chunk *chunks[0];
};

struct ll_pool *ll_pool_create(int min_alloc_order, int chunk_order,
			       int chunk_num, int nid);
void ll_pool_destroy(struct ll_pool *pool);
void *ll_pool_alloc(struct ll_pool *pool, size_t len);
void ll_pool_free(const void *p, size_t len);
size_t ll_pool_avail(struct ll_pool *pool);
size_t ll_pool_size(struct ll_pool *pool);
#endif /* LLALLOC_H */
