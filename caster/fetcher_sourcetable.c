#include <event2/event.h>
#include <event2/bufferevent.h>

#include "conf.h"
#include "ntripcli.h"
#include "ntrip_common.h"
#include "fetcher_sourcetable.h"

static void
get_sourcetable_cb(int fd, short what, void *arg) {
	struct sourcetable_fetch_args *a = (struct sourcetable_fetch_args *)arg;
	event_free(a->ev);
	a->ev = NULL;
	fetcher_sourcetable_start(arg);
}

/*
 * Initialize, but don't start, a sourcetable fetcher.
 */
struct sourcetable_fetch_args *fetcher_sourcetable_new(struct caster_state *caster,
	const char *host, unsigned short port, int refresh_delay, int priority) {
	struct sourcetable_fetch_args *this = (struct sourcetable_fetch_args *)malloc(sizeof(struct sourcetable_fetch_args));
	if (this == NULL)
		return NULL;
	this->host = mystrdup(host);
	if (this->host == NULL) {
		free(this);
		return NULL;
	}
	this->port = port;
	this->refresh_delay = refresh_delay;
	this->caster = caster;
	this->sourcetable = NULL;
	this->sourcetable_cb = NULL;
	this->ev = NULL;
	this->st = NULL;
	this->priority = priority;
	return this;
}

/*
 * Stop fetcher.
 */
static void _fetcher_sourcetable_stop(struct sourcetable_fetch_args *this, int keep_sourcetable) {
	logfmt(&this->caster->flog, "Stopping sourcetable fetch from %s:%d\n", this->host, this->port);
	if (this->ev) {
		event_free(this->ev);
		this->ev = NULL;
	}
	if (this->st && this->st->state != NTRIP_END) {
		bufferevent_lock(this->st->bev);
		ntrip_deferred_free(this->st, "fetcher_sourcetable_stop");
		this->st = NULL;
	}
	if (!keep_sourcetable)
		stack_replace_host(this->st, &this->caster->sourcetablestack, this->host, this->port, NULL);
}

void fetcher_sourcetable_free(struct sourcetable_fetch_args *this) {
	_fetcher_sourcetable_stop(this, 0);
	strfree(this->host);
	free(this);
}

void fetcher_sourcetable_stop(struct sourcetable_fetch_args *this) {
	_fetcher_sourcetable_stop(this, 0);
}

/*
 * Reload fetcher.
 *
 * Same as a stop/start, except we keep the sourcetable during the reload.
 */
void fetcher_sourcetable_reload(struct sourcetable_fetch_args *this, int refresh_delay, int priority) {
	_fetcher_sourcetable_stop(this, 1);
	this->refresh_delay = refresh_delay;
	this->priority = priority;
	fetcher_sourcetable_start(this);
}

static void
sourcetable_cb(int fd, short what, void *arg) {
	struct sourcetable_fetch_args *a = (struct sourcetable_fetch_args *)arg;
	struct caster_state *caster = a->caster;
	struct sourcetable *sourcetable = a->sourcetable;
	struct timeval t1;
	gettimeofday(&t1, NULL);
	timersub(&t1, &a->st->start, &t1);

	if (sourcetable != NULL) {
		ntrip_log(a->st, LOG_NOTICE, "sourcetable loaded, %d entries, %.3f ms\n",
			sourcetable_nentries(sourcetable, 0),
			t1.tv_sec*1000 + t1.tv_usec/1000.);
		sourcetable->priority = a->priority;
		stack_replace_host(a->st, &a->caster->sourcetablestack, a->host, a->port, sourcetable);
		a->sourcetable = NULL;
	} else {
		ntrip_log(a->st, LOG_NOTICE, "sourcetable load failed, %.3f ms\n",
			t1.tv_sec*1000 + t1.tv_usec/1000.);
	}
	a->st = NULL;

	if (a->refresh_delay) {
		struct timeval timeout_interval = { a->refresh_delay, 0 };
		logfmt(&caster->flog, "Starting refresh callback for sourcetable %s:%d in %d seconds\n", a->host, a->port, a->refresh_delay);
		a->ev = event_new(caster->base, -1, 0, get_sourcetable_cb, a);
		event_add(a->ev, &timeout_interval);
	}
}

/*
 * Start a sourcetable fetcher.
 */
void
fetcher_sourcetable_start(struct sourcetable_fetch_args *arg_cb) {
	arg_cb->sourcetable_cb = sourcetable_cb;

	ntripcli_start(arg_cb->caster, arg_cb->host, arg_cb->port, "sourcetable_fetcher", arg_cb);
}
