#include <stdio.h>

int errlogMessage(const char *message) {
  fprintf(stderr, "%s\n", message);
  return 0;
}

int errlogPrintf(const char *message, ...) {
  // fprintf(stderr, "%s\n", message);
  return 0;
}
