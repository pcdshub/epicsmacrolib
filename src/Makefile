all: libmaclib.a

libmaclib.a: ellLib.o macEnv.o macUtil.o macCore.o osdAssert.o
		$(AR) r libmaclib.a $<

%.o: %.c
		$(CC) -c -Wall $<

update:
	# I want 4 files from a massive repository; forgive me:
	curl https://raw.githubusercontent.com/epics-base/epics-base/7.0/modules/libcom/src/ellLib/ellLib.c > ellLib.c
	curl https://raw.githubusercontent.com/epics-base/epics-base/7.0/modules/libcom/src/macLib/macCore.c > macCore.c
	curl https://raw.githubusercontent.com/epics-base/epics-base/7.0/modules/libcom/src/macLib/macEnv.c > macEnv.c
	curl https://raw.githubusercontent.com/epics-base/epics-base/7.0/modules/libcom/src/macLib/macUtil.c > macUtil.c

clean:
	rm -rf *.o *.a

.PHONY: clean all update
