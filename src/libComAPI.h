#include <stdio.h>

#ifndef _H_COMAPI
#define _H_COMAPI

#if defined(_WIN32) || defined(__CYGWIN__)

#  if !defined(epicsStdCall)
#    define epicsStdCall __stdcall
#  endif

#  if defined(BUILDING_LIBCOM_API) && defined(EPICS_BUILD_DLL)
/* Building library as dll */
#    define LIBCOM_API __declspec(dllexport)
#  elif !defined(BUILDING_LIBCOM_API) && defined(EPICS_CALL_DLL)
/* Calling library in dll form */
#    define LIBCOM_API __declspec(dllimport)
#  endif

#elif __GNUC__ >= 4
#  define LIBCOM_API __attribute__ ((visibility("default")))
#endif

#if !defined(LIBCOM_API)
#  define LIBCOM_API
#endif

#if !defined(epicsStdCall)
#  define epicsStdCall
#endif

#ifndef EPICS_PRINTF_STYLE
/*
 * No format-string checking
 */
#   define EPICS_PRINTF_STYLE(f,a)
#endif

#define TRUE 1
#define FALSE 0

// Not using dbmf allocations; malloc/free are good enough for us
#define dbmfMalloc malloc
#define dbmfFree free

#endif
