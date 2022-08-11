/*************************************************************************\
* Copyright (c) 2009 UChicago Argonne LLC, as Operator of Argonne
*     National Laboratory.
* Copyright (c) 2002 The Regents of the University of California, as
*     Operator of Los Alamos National Laboratory.
* SPDX-License-Identifier: EPICS
* EPICS BASE is distributed subject to a Software License Agreement found
* in file LICENSE that is included with this distribution.
\*************************************************************************/
/*
 *      Author:         Jeffrey Hill
 *      Date:           02-27-95
 */

#include "errlog.h"
#include "stdlib.h"


void epicsAssert (const char *pFile, const unsigned line,
    const char *pExp, const char *pAuthorName)
{
    errlogPrintf("\n\n\n"
        "A call to 'assert(%s)'\n"
        "    failed in %s line %u.\n",
        pExp, pFile, line
    );

    exit(1);
}
