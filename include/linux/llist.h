#ifndef LLIST_H
#define LLIST_H

/* lock-less NULL terminated single linked list */
struct llist_head {
	struct llist_head *next;
};

#define LLIST_HEAD_INIT(name) { NULL }

#define LLIST_HEAD(name)				\
	struct llist_head name = LLIST_HEAD_INIT(name)

/**
 * init_llist_head - initialize lock-less list head
 * @head:	the head for your lock-less list
 */
static inline void init_llist_head(struct llist_head *list)
{
	list->next = NULL;
}

/**
 * llist_entry - get the struct of this entry
 * @ptr:	the &struct llist_head pointer.
 * @type:	the type of the struct this is embedded in.
 * @member:	the name of the llist_head within the struct.
 */
#define llist_entry(ptr, type, member)		\
	container_of(ptr, type, member)

/**
 * llist_for_each - iterate over a lock-less list
 * @pos:	the &struct llist_head to use as a loop cursor
 * @head:	the head for your lock-less list
 */
#define llist_for_each(pos, head)					\
	for (pos = (head)->next; pos; pos = pos->next)

/**
 * llist_for_each_entry - iterate over lock-less list of given type
 * @pos:	the type * to use as a loop cursor.
 * @head:	the head for your lock-less list.
 * @member:	the name of the llist_head with the struct.
 */
#define llist_for_each_entry(pos, head, member)				\
	for (pos = llist_entry((head)->next, typeof(*pos), member);	\
	     &pos->member != NULL;					\
	     pos = llist_entry(pos->member.next, typeof(*pos), member))

/**
 * llist_empty - tests whether a lock-less list is empty
 * @head:	the list to test
 */
static inline int llist_empty(const struct llist_head *head)
{
	return head->next == NULL;
}

void llist_add(struct llist_head *new, struct llist_head *head);
struct llist_head *llist_del_first(struct llist_head *head);
void llist_move_all(struct llist_head *list, struct llist_head *head);

#endif /* LLIST_H */
