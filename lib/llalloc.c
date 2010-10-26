/*
 * Lock-less memory allocator, This can be used to allocate/free
 * memory in IRQ/NMI handler. This is useful for hardware error
 * handling, which needs to collect hardware error information in
 * IRQ/NMI handler.
 *
 * The memory pages for lock-less memory allocator are pre-allocated
 * during initialization. Bitmap is used to record allocated/free
 * memory blocks. To support lock-less allocate/free operation,
 * lock-less bitmap set/clear operations are used.
 *
 * The difference between this allocator and the gen_pool
 * implementation in lib/genalloc.c is that memory can be
 * allocated/freed by multiple users simultaneously without lock.
 *
 * Copyright 2010 Intel Corp.
 *   Author: Huang Ying <ying.huang@intel.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version
 * 2 as published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/bitmap.h>
#include <linux/slab.h>
#include <linux/mm.h>
#include <linux/llalloc.h>

static inline void ll_page_set_chunk(struct page *page,
				     struct ll_pool_chunk *chunk)
{
	page->lru.prev = (struct list_head *)chunk;
}

static inline struct ll_pool_chunk *ll_virt_to_pool_chunk(const void *p)
{
	struct page *page = virt_to_head_page(p);
	return (struct ll_pool_chunk *)page->lru.prev;
}

static void ll_pool_chunk_destroy(struct ll_pool_chunk *chunk)
{
	int chunk_size = PAGE_SIZE << chunk->pool->chunk_order;

	BUG_ON(atomic_read(&chunk->avail) != chunk_size);
	__free_pages(virt_to_page(chunk->data), chunk->pool->chunk_order);
	kfree(chunk);
}

/**
 * ll_pool_destroy - destroy a lock-less memory pool
 * @ pool: pool to destroy
 *
 * Destroy the lock-less memory pool. Verify that there are no
 * outstanding allocations. Memory pages backed the lock-less
 * allocator are freed.
 */
void ll_pool_destroy(struct ll_pool *pool)
{
	int i;

	for (i = 0; i < pool->chunk_num; i++) {
		if (pool->chunks[i])
			ll_pool_chunk_destroy(pool->chunks[i]);
	}
}
EXPORT_SYMBOL_GPL(ll_pool_destroy);

static struct ll_pool_chunk *ll_pool_chunk_create(struct ll_pool *pool, int nid)
{
	struct ll_pool_chunk *chunk;
	int chunk_size = PAGE_SIZE << pool->chunk_order;
	int nbits = chunk_size >> pool->min_alloc_order;
	int nbytes = sizeof(struct ll_pool_chunk) + \
		DIV_ROUND_UP(nbits, BITS_PER_LONG) * sizeof(unsigned long);
	struct page *page;

	chunk = kmalloc_node(nbytes, GFP_KERNEL | __GFP_ZERO, nid);
	if (!chunk)
		return NULL;
	page = alloc_pages_node(nid, GFP_KERNEL, pool->chunk_order);
	if (!page)
		goto err_free_chunk;
	chunk->data = page_address(page);
	atomic_set(&chunk->avail, chunk_size);
	ll_page_set_chunk(page, chunk);
	chunk->pool = pool;

	return chunk;
err_free_chunk:
	kfree(chunk);
	return NULL;
}

/**
 * ll_pool_create - create a new lock-less memory pool
 * @min_alloc_order: log base 2 of number of bytes each bitmap bit represents
 * @chunk_order: log base 2 of number of pages each chunk manages
 * @chunk_num: number of chunks
 * @nid: node id of the node the pool structure should be allocated on, or -1
 *
 * Create a new lock-less memory pool that can be used in IRQ/NMI
 * context. (PAGE_SIZE << @chunk_order) * @chunk_num memory pages
 * backed the lock-less allocator are allocated with alloc_pages_node.
 */
struct ll_pool *ll_pool_create(int min_alloc_order, int chunk_order,
			       int chunk_num, int nid)
{
	struct ll_pool *pool;
	int i;

	pool = kmalloc_node(sizeof(*pool) + chunk_num * sizeof(void *),
			    GFP_KERNEL | __GFP_ZERO, nid);
	if (!pool)
		return NULL;
	pool->min_alloc_order = min_alloc_order;
	pool->chunk_order = chunk_order;
	pool->chunk_num = chunk_num;
	for (i = 0; i < chunk_num; i++) {
		pool->chunks[i] = ll_pool_chunk_create(pool, nid);
		if (!pool->chunks[i])
			goto err_pool_destroy;
	}

	return pool;
err_pool_destroy:
	ll_pool_destroy(pool);
	return NULL;
}
EXPORT_SYMBOL_GPL(ll_pool_create);

static void *ll_pool_chunk_alloc(struct ll_pool_chunk *chunk, size_t len)
{
	struct ll_pool *pool = chunk->pool;
	int order = pool->min_alloc_order;
	int chunk_bits = (PAGE_SIZE << pool->chunk_order) >> order;
	int pos = 0, bits, remain;

	if (len > atomic_read(&chunk->avail))
		return NULL;

	bits = (len + (1UL << order) - 1) >> order;
	for (;;) {
		pos = bitmap_find_next_zero_area(chunk->bitmap, chunk_bits,
						 pos, bits, 0);
		if (pos >= chunk_bits)
			return NULL;
		remain = bitmap_set_ll(chunk->bitmap, pos, bits);
		if (!remain)
			break;
		remain = bitmap_clear_ll(chunk->bitmap, pos, bits - remain);
		BUG_ON(remain);
	}
	len = bits << order;
	atomic_sub(len, &chunk->avail);

	return chunk->data + (pos << order);
}

/**
 * ll_pool_alloc - allocate memory from the pool
 * @pool: pool to allocate from
 * @len: number of bytes to allocate from the pool
 *
 * Allocate the required number of bytes from the pool. Uses a
 * first-fit algorithm.
 */
void *ll_pool_alloc(struct ll_pool *pool, size_t len)
{
	int i;
	void *p;
	struct ll_pool_chunk *chunk;

	for (i = 0; i < pool->chunk_num; i++) {
		chunk = pool->chunks[i];
		p = ll_pool_chunk_alloc(chunk, len);
		if (p)
			return p;
	}

	return NULL;
}
EXPORT_SYMBOL_GPL(ll_pool_alloc);

static void ll_pool_chunk_free(struct ll_pool_chunk *chunk,
			       const void *p, size_t len)
{
	struct ll_pool *pool = chunk->pool;
	int order = pool->min_alloc_order;
	int mask = (1UL << order) - 1;
	int chunk_size = PAGE_SIZE << pool->chunk_order;
	int remain, pos, bits;

	BUG_ON(p < chunk->data || p + len > chunk->data + chunk_size);
	BUG_ON((p - chunk->data) & mask);
	bits = (len + mask) >> order;
	len = bits << order;
	pos = (p - chunk->data) >> order;
	remain = bitmap_clear_ll(chunk->bitmap, pos, bits);
	BUG_ON(remain);
	atomic_add(len, &chunk->avail);
}

/**
 * ll_pool_free - free allocated memory back to the pool
 * @p: starting address of memory to free back to pool
 * @len: size in bytes of memory to free
 *
 * Free previously allocated memory back the the pool.
 */
void ll_pool_free(const void *p, size_t len)
{
	struct ll_pool_chunk *chunk;

	chunk = ll_virt_to_pool_chunk(p);
	ll_pool_chunk_free(chunk, p, len);
}
EXPORT_SYMBOL_GPL(ll_pool_free);

/**
 * ll_pool_avail - get available free space of the pool
 * @pool: pool to get available free space
 *
 * Return available free space of the specified pool.
 */
size_t ll_pool_avail(struct ll_pool *pool)
{
	int i;
	size_t avail = 0;

	for (i = 0; i < pool->chunk_num; i++)
		avail += atomic_read(&pool->chunks[i]->avail);

	return avail;
}
EXPORT_SYMBOL_GPL(ll_pool_avail);

/**
 * ll_pool_size - get size in bytes of memory managed by the pool
 * @pool: pool to get size
 *
 * Return size in bytes of memory managed by the pool.
 */
size_t ll_pool_size(struct ll_pool *pool)
{
	return (PAGE_SIZE << pool->chunk_order) * pool->chunk_num;
}
EXPORT_SYMBOL_GPL(ll_pool_size);
