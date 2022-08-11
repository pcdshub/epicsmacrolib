#*************************************************************************
# Copyright (c) 2010 UChicago Argonne LLC, as Operator of Argonne
#     National Laboratory.
# EPICS BASE is distributed subject to a Software License Agreement found
# in file LICENSE that is included with this distribution. 
#*************************************************************************

# This is a Makefile fragment, see src/libCom/Makefile.

all: libmaclib.a

libmaclib.a: ellLib.o macEnv.o macUtil.o macCore.o osdAssert.o
		$(AR) r libmaclib.a $<

%.o: %.c
		$(CC) -c -Wall $<

clean:
	rm -rf *.o *.a

.PHONY: clean all
