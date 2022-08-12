/*************************************************************************\
* Copyright (c) 2014 UChicago Argonne LLC, as Operator of Argonne
*     National Laboratory.
* Copyright (c) 2002 The Regents of the University of California, as
*     Operator of Los Alamos National Laboratory.
* SPDX-License-Identifier: EPICS
* EPICS BASE is distributed subject to a Software License Agreement found
* in file LICENSE that is included with this distribution.
\*************************************************************************/

#ifndef INC_errlog_H
#define INC_errlog_H

#include "libComAPI.h"

#ifdef __cplusplus
extern "C" {
#endif

LIBCOM_API int errlogMessage(const char *message);
LIBCOM_API int errlogPrintf(const char *pformat, ...);

#ifdef __cplusplus
}
#endif

#endif /*INC_errlog_H*/
