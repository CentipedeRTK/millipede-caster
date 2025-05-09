#ifndef __SOURCELINE_H__
#define __SOURCELINE_H__

#include "queue.h"
#include "util.h"

/*
 * Description of a source as found in a source table.
 */
struct sourceline {
	TAILQ_ENTRY(sourceline) next;
	char *key;		// mountpoint name
	char *value;		// STR string
	pos_t pos;		// base position
	int bps;		// approx. stream data rate, bits per second
	char virtual;		// source is virtual
	char on_demand;
	char *host;
	unsigned short port;
	int tls;
};
TAILQ_HEAD (sourcelineq, sourceline);

struct sourceline *sourceline_new(const char *host, unsigned short port, int tls, const char *key, const char *value);
struct sourceline *sourceline_new_parse(const char *entry, const char *caster, unsigned short port, int tls, int priority, int on_demand);
struct sourceline *sourceline_copy(struct sourceline *orig);
void sourceline_free(struct sourceline *this);

#endif
