/*
 * builtin-inject.c
 *
 * Builtin inject command: Examine the live mode (stdin) event stream
 * and repipe it to stdout while optionally injecting additional
 * events into it.
 */
#include "builtin.h"

#include "perf.h"
#include "util/session.h"
#include "util/debug.h"

#include "util/parse-options.h"
#include "util/trace-event.h"

static char		const *input_name = "-";
static const char	*output_name		= "-";
static int		pipe_output		= 0;
static int		output;
static u64		bytes_written		= 0;

static bool		inject_build_ids;
static bool		inject_sched_stat;

struct perf_session	*session;

static int perf_event__repipe_synth(union perf_event *event,
				    struct perf_session *s __used)
{
	uint32_t size;
	void *buf = event;

	size = event->header.size;

	while (size) {
		int ret = write(output, buf, size);
		if (ret < 0)
			return -errno;

		size -= ret;
		buf += ret;

		bytes_written += ret;
	}

	return 0;
}

static int perf_event__repipe(union perf_event *event,
			      struct perf_sample *sample __used,
			      struct perf_session *s)
{
	return perf_event__repipe_synth(event, s);
}

static int perf_event__repipe_sample(union perf_event *event,
			      struct perf_sample *sample __used,
			      struct perf_evsel *evsel __used,
			      struct perf_session *s)
{
	return perf_event__repipe_synth(event, s);
}

static int perf_event__repipe_mmap(union perf_event *event,
				   struct perf_sample *sample,
				   struct perf_session *s)
{
	int err;

	err = perf_event__process_mmap(event, sample, s);
	perf_event__repipe(event, sample, s);

	return err;
}

static int perf_event__repipe_task(union perf_event *event,
				   struct perf_sample *sample,
				   struct perf_session *s)
{
	int err;

	err = perf_event__process_task(event, sample, s);
	perf_event__repipe(event, sample, s);

	return err;
}

static int perf_event__repipe_tracing_data(union perf_event *event,
					   struct perf_session *s)
{
	int err;

	perf_event__repipe_synth(event, s);
	err = perf_event__process_tracing_data(event, s);

	return err;
}

static int dso__read_build_id(struct dso *self)
{
	if (self->has_build_id)
		return 0;

	if (filename__read_build_id(self->long_name, self->build_id,
				    sizeof(self->build_id)) > 0) {
		self->has_build_id = true;
		return 0;
	}

	return -1;
}

static int dso__inject_build_id(struct dso *self, struct perf_session *s)
{
	u16 misc = PERF_RECORD_MISC_USER;
	struct machine *machine;
	int err;

	if (dso__read_build_id(self) < 0) {
		pr_debug("no build_id found for %s\n", self->long_name);
		return -1;
	}

	machine = perf_session__find_host_machine(s);
	if (machine == NULL) {
		pr_err("Can't find machine for session\n");
		return -1;
	}

	if (self->kernel)
		misc = PERF_RECORD_MISC_KERNEL;

	err = perf_event__synthesize_build_id(self, misc, perf_event__repipe,
					      machine, s);
	if (err) {
		pr_err("Can't synthesize build_id event for %s\n", self->long_name);
		return -1;
	}

	return 0;
}

static int perf_event__inject_buildid(union perf_event *event,
				      struct perf_sample *sample,
				      struct perf_evsel *evsel __used,
				      struct perf_session *s)
{
	struct addr_location al;
	struct thread *thread;
	u8 cpumode;

	cpumode = event->header.misc & PERF_RECORD_MISC_CPUMODE_MASK;

	thread = perf_session__findnew(s, event->ip.pid);
	if (thread == NULL) {
		pr_err("problem processing %d event, skipping it.\n",
		       event->header.type);
		goto repipe;
	}

	thread__find_addr_map(thread, s, cpumode, MAP__FUNCTION,
			      event->ip.pid, event->ip.ip, &al);

	if (al.map != NULL) {
		if (!al.map->dso->hit) {
			al.map->dso->hit = 1;
			if (map__load(al.map, NULL) >= 0) {
				dso__inject_build_id(al.map->dso, s);
				/*
				 * If this fails, too bad, let the other side
				 * account this as unresolved.
				 */
			} else
				pr_warning("no symbols found in %s, maybe "
					   "install a debug package?\n",
					   al.map->dso->long_name);
		}
	}

repipe:
	perf_event__repipe(event, sample, s);
	return 0;
}

struct event_entry
{
	struct list_head list;
	u32 pid;
	union perf_event event[0];
};

static LIST_HEAD(samples);

static int perf_event__sched_stat(union perf_event *event,
				      struct perf_sample *sample,
				      struct perf_evsel *evsel __used,
				      struct perf_session *s)
{
	int type;
	struct event *e;
	const char *evname = NULL;
	uint32_t size;
	struct event_entry *ent;
	union perf_event *event_sw = NULL;
	struct perf_sample sample_sw;
	int sched_process_exit;

	size = event->header.size;

	type = trace_parse_common_type(sample->raw_data);
	e = trace_find_event(type);
	if (e)
		evname = e->name;

	sched_process_exit = !strcmp(evname, "sched_process_exit");

	if (!strcmp(evname, "sched_switch") ||  sched_process_exit) {
		list_for_each_entry(ent, &samples, list)
			if (sample->pid == ent->pid)
				break;

		if (&ent->list != &samples) {
			list_del(&ent->list);
			free(ent);
		}

		if (sched_process_exit)
			return 0;

		ent = malloc(size + sizeof(struct event_entry));
		ent->pid = sample->pid;
		memcpy(&ent->event, event, size);
		list_add(&ent->list, &samples);
		return 0;

	} else if (!strncmp(evname, "sched_stat_", 11)) {
		u32 pid;

		pid = raw_field_value(e, "pid", sample->raw_data);

		list_for_each_entry(ent, &samples, list) {
			if (pid == ent->pid)
				break;
		}

		if (&ent->list == &samples) {
			pr_debug("Could not find sched_switch for pid %u\n", pid);
			return 0;
		}

		event_sw = &ent->event[0];
		perf_session__parse_sample(session, event_sw, &sample_sw);
		sample_sw.period = sample->period;
		sample_sw.time = sample->time;
		perf_session__synthesize_sample(session, event_sw, &sample_sw);
		perf_event__repipe(event_sw, &sample_sw, s);
		return 0;
	}

	perf_event__repipe(event, sample, s);

	return 0;
}

struct perf_event_ops inject_ops = {
	.sample		= perf_event__repipe_sample,
	.mmap		= perf_event__repipe,
	.comm		= perf_event__repipe,
	.fork		= perf_event__repipe,
	.exit		= perf_event__repipe,
	.lost		= perf_event__repipe,
	.read		= perf_event__repipe,
	.throttle	= perf_event__repipe,
	.unthrottle	= perf_event__repipe,
	.attr		= perf_event__repipe_synth,
	.event_type 	= perf_event__repipe_synth,
	.tracing_data 	= perf_event__repipe_synth,
	.build_id 	= perf_event__repipe_synth,
};

extern volatile int session_done;

static void sig_handler(int sig __attribute__((__unused__)))
{
	session_done = 1;
}

static int __cmd_inject(void)
{
	int ret = -EINVAL;

	signal(SIGINT, sig_handler);

	if (inject_build_ids) {
		inject_ops.sample	= perf_event__inject_buildid;
		inject_ops.mmap		= perf_event__repipe_mmap;
		inject_ops.fork		= perf_event__repipe_task;
		inject_ops.tracing_data	= perf_event__repipe_tracing_data;
	} else if (inject_sched_stat) {
		inject_ops.sample	= perf_event__sched_stat;
		inject_ops.ordered_samples = true;
	}

	session = perf_session__new(input_name, O_RDONLY, false, true, &inject_ops);
	if (session == NULL)
		return -ENOMEM;

	if (!pipe_output)
		lseek(output, session->header.data_offset, SEEK_SET);

	ret = perf_session__process_events(session, &inject_ops);

	if (!pipe_output) {
		session->header.data_size += bytes_written;
		perf_session__write_header(session, session->evlist, output, true);
	}

	perf_session__delete(session);

	return ret;
}

static const char * const report_usage[] = {
	"perf inject [<options>]",
	NULL
};

static const struct option options[] = {
	OPT_BOOLEAN('b', "build-ids", &inject_build_ids,
		    "Inject build-ids into the output stream"),
	OPT_BOOLEAN('s', "sched-stat", &inject_sched_stat,
		    "correct call-chains for shed-stat-*"),
	OPT_STRING('i', "input", &input_name, "file",
		    "input file name"),
	OPT_STRING('o', "output", &output_name, "file",
		    "output file name"),
	OPT_INCR('v', "verbose", &verbose,
		 "be more verbose (show build ids, etc)"),
	OPT_END()
};

int cmd_inject(int argc, const char **argv, const char *prefix __used)
{
	argc = parse_options(argc, argv, options, report_usage, 0);

	/*
	 * Any (unrecognized) arguments left?
	 */
	if (argc)
		usage_with_options(report_usage, options);

	if (!strcmp(output_name, "-")) {
		pipe_output = 1;
		output = STDOUT_FILENO;
	} else {
		output = open(output_name, O_CREAT| O_WRONLY | O_TRUNC,
							S_IRUSR | S_IWUSR);
		if (output < 0) {
			perror("failed to create output file");
			exit(-1);
		}
	}

	if (symbol__init() < 0)
		return -1;

	return __cmd_inject();
}
