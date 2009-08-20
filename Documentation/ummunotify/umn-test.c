/*
 * Copyright (c) 2009 Cisco Systems.  All rights reserved.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License version
 * 2 as published by the Free Software Foundation.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <stdint.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

#include <linux/ummunotify.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/ioctl.h>

#define UMN_TEST_COOKIE 123

static int		umn_fd;
static volatile __u64  *umn_counter;

static int umn_init(void)
{
	__u32 flags;

	umn_fd = open("/dev/ummunotify", O_RDONLY);
	if (umn_fd < 0) {
		perror("open");
		return 1;
	}

	if (ioctl(umn_fd, UMMUNOTIFY_EXCHANGE_FEATURES, &flags)) {
		perror("exchange ioctl");
		return 1;
	}

	printf("kernel feature flags: 0x%08x\n", flags);

	umn_counter = mmap(NULL, sizeof *umn_counter, PROT_READ,
			   MAP_SHARED, umn_fd, 0);
	if (umn_counter == MAP_FAILED) {
		perror("mmap");
		return 1;
	}

	return 0;
}

static int umn_register(void *buf, size_t size, __u64 cookie)
{
	struct ummunotify_register_ioctl r = {
		.start		= (unsigned long) buf,
		.end		= (unsigned long) buf + size,
		.user_cookie	= cookie,
	};

	if (ioctl(umn_fd, UMMUNOTIFY_REGISTER_REGION, &r)) {
		perror("register ioctl");
		return 1;
	}

	return 0;
}

static int umn_unregister(__u64 cookie)
{
	if (ioctl(umn_fd, UMMUNOTIFY_UNREGISTER_REGION, &cookie)) {
		perror("unregister ioctl");
		return 1;
	}

	return 0;
}

int main(int argc, char *argv[])
{
	int			page_size;
	__u64			old_counter;
	void		       *t;
	int			got_it;

	if (umn_init())
		return 1;

	printf("\n");

	old_counter = *umn_counter;
	if (old_counter != 0) {
		fprintf(stderr, "counter = %lld (expected 0)\n", old_counter);
		return 1;
	}

	page_size = sysconf(_SC_PAGESIZE);
	t = mmap(NULL, 3 * page_size, PROT_READ,
		 MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE, -1, 0);

	if (umn_register(t, 3 * page_size, UMN_TEST_COOKIE))
		return 1;

	munmap(t + page_size, page_size);

	old_counter = *umn_counter;
	if (old_counter != 1) {
		fprintf(stderr, "counter = %lld (expected 1)\n", old_counter);
		return 1;
	}

	got_it = 0;
	while (1) {
		struct ummunotify_event	ev;
		int			len;

		len = read(umn_fd, &ev, sizeof ev);
		if (len < 0) {
			perror("read event");
			return 1;
		}
		if (len != sizeof ev) {
			fprintf(stderr, "Read gave %d bytes (!= event size %zd)\n",
				len, sizeof ev);
			return 1;
		}

		switch (ev.type) {
		case UMMUNOTIFY_EVENT_TYPE_INVAL:
			if (got_it) {
				fprintf(stderr, "Extra invalidate event\n");
				return 1;
			}
			if (ev.user_cookie_counter != UMN_TEST_COOKIE) {
				fprintf(stderr, "Invalidate event for cookie %lld (expected %d)\n",
					ev.user_cookie_counter,
					UMN_TEST_COOKIE);
				return 1;
			}

			printf("Invalidate event:\tcookie %lld\n",
			       ev.user_cookie_counter);

			if (!(ev.flags & UMMUNOTIFY_EVENT_FLAG_HINT)) {
				fprintf(stderr, "Hint flag not set\n");
				return 1;
			}

			if (ev.hint_start != (uintptr_t) t + page_size ||
			    ev.hint_end != (uintptr_t) t + page_size * 2) {
				fprintf(stderr, "Got hint %llx..%llx, expected %p..%p\n",
					ev.hint_start, ev.hint_end,
					t + page_size, t + page_size * 2);
				return 1;
			}

			printf("\t\t\thint %llx...%llx\n",
			       ev.hint_start, ev.hint_end);

			got_it = 1;
			break;

		case UMMUNOTIFY_EVENT_TYPE_LAST:
			if (!got_it) {
				fprintf(stderr, "Last event without invalidate event\n");
				return 1;
			}

			printf("Empty event:\t\tcounter %lld\n",
			       ev.user_cookie_counter);
			goto done;

		default:
			fprintf(stderr, "unknown event type %d\n",
				ev.type);
			return 1;
		}
	}

done:
	umn_unregister(123);
	munmap(t, page_size);

	old_counter = *umn_counter;
	if (old_counter != 1) {
		fprintf(stderr, "counter = %lld (expected 1)\n", old_counter);
		return 1;
	}

	return 0;
}
