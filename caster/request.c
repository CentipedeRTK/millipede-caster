#include <stdlib.h>

#include "request.h"
#include "hash.h"

struct request *request_new() {
	struct request *this = (struct request *)malloc(sizeof(struct request));
	if (this != NULL) {
		this->hash = NULL;
		this->status = 200;
	}
	return this;
}

void request_free(struct request *this) {
	if (this->hash != NULL)
		hash_table_free(this->hash);
	free(this);
}
