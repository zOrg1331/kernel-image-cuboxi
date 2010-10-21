/*
 *  veip_mgmt.c
 *
 *  Copyright (C) 2005  SWsoft
 *  All rights reserved.
 *  
 *  Licensing governed by "linux/COPYING.SWsoft" file.
 *
 */

/*
 * Virtual Networking device used to change VE ownership on packets
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/seq_file.h>

#include <linux/inet.h>
#include <net/ip.h>
#include <linux/skbuff.h>
#include <linux/venet.h>

static void veip_release(struct ve_struct *ve)
{
	veip_put(ve->veip);
	ve->veip = NULL;
}

static int veip_create(struct ve_struct *ve)
{
	struct veip_struct *veip;

	veip = veip_findcreate(ve->veid);
	if (veip == NULL)
		return -ENOMEM;

	ve->veip = veip;
	return 0;
}

static struct ip_entry_struct *veip_entry_create(struct ve_struct *ve)
{
	return kzalloc(sizeof(struct ip_entry_struct), GFP_KERNEL);
}

static void veip_entry_free(struct ip_entry_struct *entry)
{
	kfree(entry);
}

static int veip_entry_conflict(struct ip_entry_struct *entry, struct ve_struct *ve)
{
	return -EADDRINUSE;
}

static int skb_extract_addr(struct sk_buff *skb,
		struct ve_addr_struct *addr, int dir)
{
	switch (skb->protocol) {
	case __constant_htons(ETH_P_IP):
		addr->family = AF_INET;
		addr->key[0] = 0;
		addr->key[1] = 0;
		addr->key[2] = 0;
		addr->key[3] = (dir ? ip_hdr(skb)->daddr : ip_hdr(skb)->saddr);
		return 0;
#if defined(CONFIG_IPV6) || defined(CONFIG_IPV6_MODULE)
	case __constant_htons(ETH_P_IPV6):
		addr->family = AF_INET6;
		memcpy(&addr->key, dir ?
				ipv6_hdr(skb)->daddr.s6_addr32 :
				ipv6_hdr(skb)->saddr.s6_addr32,
				sizeof(addr->key));
		return 0;
#endif
	}

	return -EAFNOSUPPORT;
}

static struct ve_struct *venet_find_ve(struct sk_buff *skb, int dir)
{
	struct ip_entry_struct *entry;
	struct ve_addr_struct addr;

	if (skb_extract_addr(skb, &addr, dir) < 0)
		return NULL;

	entry = venet_entry_lookup(&addr);
	if (entry == NULL)
		return NULL;

	return entry->active_env;
}

static struct ve_struct *veip_lookup(struct sk_buff *skb)
{
	struct ve_struct *ve, *ve_old;

	ve_old = skb->owner_env;

	read_lock(&veip_hash_lock);
	if (!ve_is_super(ve_old)) {
		/* from VE to host */
		ve = venet_find_ve(skb, 0);
		if (ve == NULL)
			goto out_drop;
		if (!ve_accessible_strict(ve, ve_old))
			goto out_source;
		ve = get_ve0();
	} else {
		/* from host to VE */
		ve = venet_find_ve(skb, 1);
		if (ve == NULL)
			goto out_drop;
	}
	read_unlock(&veip_hash_lock);

	return ve;

out_drop:
	read_unlock(&veip_hash_lock);
	return ERR_PTR(-ESRCH);

out_source:
	read_unlock(&veip_hash_lock);
	if (net_ratelimit() && skb->protocol == __constant_htons(ETH_P_IP)) {
		printk(KERN_WARNING "Dropped packet, source wrong "
		       "veid=%u src-IP=%u.%u.%u.%u "
		       "dst-IP=%u.%u.%u.%u\n",
		       skb->owner_env->veid,
		       NIPQUAD(ip_hdr(skb)->saddr),
		       NIPQUAD(ip_hdr(skb)->daddr));
	}
	return ERR_PTR(-EACCES);
}

static void veip_cleanup(void)
{
	int i;

	write_lock_irq(&veip_hash_lock);
	for (i = 0; i < VEIP_HASH_SZ; i++)
		while (!list_empty(ip_entry_hash_table + i)) {
			struct ip_entry_struct *entry;

			entry = list_first_entry(ip_entry_hash_table + i,
					struct ip_entry_struct, ip_hash);
			list_del(&entry->ip_hash);
			list_del(&entry->ve_list);
			kfree(entry);
		}
	write_unlock_irq(&veip_hash_lock);
}

static struct veip_pool_ops open_pool_ops = {
	.ip_entry_create = veip_entry_create,
	.ip_entry_release = veip_entry_free,
	.ip_entry_conflict = veip_entry_conflict,
	.veip_create = veip_create,
	.veip_release = veip_release,
	.veip_cleanup = veip_cleanup,
	.veip_lookup = veip_lookup,
};

struct veip_pool_ops *veip_pool_ops = &open_pool_ops;
EXPORT_SYMBOL(veip_pool_ops);
