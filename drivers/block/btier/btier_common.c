#include "btier.h"

u64 round_to_blksize(u64 size)
{
	u64 roundsize;
	roundsize = size / BLKSIZE;
	roundsize *= BLKSIZE;
	return roundsize;
}

u64 calc_bitlist_size(u64 devicesize)
{
	u64 bitlistsize;
	u64 startofbitlist;
	u64 round;
	u64 rdevsize;

	rdevsize = round_to_blksize(devicesize);
	startofbitlist = TIER_HEADERSIZE;
	bitlistsize = (rdevsize / BLKSIZE);
	round = bitlistsize / BLKSIZE;
	round *= BLKSIZE;
	if (round < bitlistsize)
		bitlistsize = round + BLKSIZE;
	return bitlistsize;
}

u64 calc_blocklist_size(u64 total_device_size, u64 total_bitlist_size)
{
	u64 blocklistsize;
	u64 round;
	u64 netdevsize;
	u64 blocks;
	u64 binfosize = sizeof(struct blockinfo);

	netdevsize = total_device_size - total_bitlist_size;
	blocks = BLKSIZE / binfosize;
	blocks++;
	blocklistsize = div64_u64(netdevsize, blocks);
	round = div64_u64(blocklistsize, binfosize);
	round *= sizeof(struct blockinfo);
	if (round < blocklistsize)
		blocklistsize = round + sizeof(struct blockinfo);
	round = blocklistsize / BLKSIZE;
	round *= BLKSIZE;
	if (round < blocklistsize)
		blocklistsize = round + BLKSIZE;
	return blocklistsize;
}
