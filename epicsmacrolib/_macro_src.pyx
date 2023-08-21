# cython: language_level=3

import contextlib
import dataclasses
import os
from typing import Dict, Optional, Union

from libc.stdlib cimport free, malloc

MacroEntry = dataclasses.make_dataclass(
    "MacroEntry",
    [
        ("name", str),
        ("rawval", str),
        ("value", str),
        ("type", str),
    ],
    frozen=True,
)


cdef extern from "<ellLib.h>" nogil:
    cdef struct ELLNODE:
        ELLNODE *next
        ELLNODE *previous

    cdef struct ELLLIST:
        ELLNODE node   # Pointers to the first and last nodes on list
        int     count  # Number of nodes on the list


ctypedef struct MAC_ENTRY:
    # prev and next pointers
    ELLNODE     node
    # entry name
    char        *name
    # entry type
    char        *type
    # raw (unexpanded) value
    char        *rawval
    # expanded macro value
    char        *value
    # length of value
    size_t      length
    # error expanding value?
    int         error
    # ever been visited?
    int         visited
    # special (internal) entry?
    int         special
    # scoping level
    int         level


cdef extern from "<macLib.h>" nogil:
    ctypedef struct MAC_HANDLE:
        long        magic     # magic number (used for authentication)
        int         dirty     # values need expanding from raw values?
        int         level     # scoping level
        int         debug     # debugging level
        ELLLIST     list      # macro name / value list
        int         flags     # operating mode flags

    char *macEnvExpand(const char *str)
    MAC_HANDLE *macCreateHandle(MAC_HANDLE **handle, const char *pairs[])
    long macDeleteHandle(MAC_HANDLE *handle)
    long macExpandString(MAC_HANDLE *handle, const char *src, char *dest, long capacity)
    long macInstallMacros(MAC_HANDLE *handle, char *pairs[])
    long macParseDefns(MAC_HANDLE *handle, const char *defns, char **pairs[])
    void macPopScope(MAC_HANDLE *handle)
    void macPushScope(MAC_HANDLE *handle)
    void macSuppressWarning(MAC_HANDLE *handle, int)


cdef class _MacroContext:
    cdef MAC_HANDLE *handle
    _show_warnings: bool
    cdef public str string_encoding
    cdef public int use_environment

    def __init__(
        self,
        use_environment=True,
        show_warnings=False,
        string_encoding: str = "latin-1",
    ):
        cdef const char **env_pairs = ["", "environ", NULL, NULL]

        if macCreateHandle(&self.handle, env_pairs if use_environment else NULL):
            raise RuntimeError("Failed to initialize the handle")

        self.show_warnings = show_warnings
        self.string_encoding = string_encoding
        self.use_environment = bool(use_environment)

    @property
    def show_warnings(self):
        return self._show_warnings

    @show_warnings.setter
    def show_warnings(self, value: bool):
        self._show_warnings = bool(value)
        suppress = not self._show_warnings
        macSuppressWarning(self.handle, suppress)

    def __cinit__(self):
        self.handle = NULL

    def __dealloc__(self):
        if self.handle is not NULL:
            macDeleteHandle(self.handle)
            self.handle = NULL

    def _push_scope(self):
        macPushScope(self.handle)

    def _pop_scope(self):
        macPopScope(self.handle)

    def _definitions_to_dict(self, defn: Union[str, bytes], string_encoding: str = "") -> Dict[str, str]:
        """Convert a definition string of the form ``A=value_a,B=value_a`` to a dictionary."""
        cdef char **pairs = NULL
        cdef int count

        string_encoding = string_encoding or self.string_encoding

        if not isinstance(defn, bytes):
            defn = defn.encode(string_encoding)

        count = macParseDefns(self.handle, defn, &pairs)
        if pairs == NULL or count <= 0:
            return {}

        result = {}
        for idx in range(count):
            variable = (pairs[2 * idx] or b'').decode(string_encoding)
            value = (pairs[2 * idx + 1] or b'').decode(string_encoding)
            result[variable] = value

        free(pairs)
        return result

    def define(self, **macros):
        """Use kwargs to define macros."""
        for key, value in macros.items():
            self._add_encoded_macro(
                str(key).encode(self.string_encoding),
                str(value).encode(self.string_encoding)
            )

    cdef int _add_encoded_macro(self, key: bytes, value: bytes):
        cdef char** pairs = [key, value, NULL];
        return macInstallMacros(self.handle, pairs)

    def get_macro_details(self) -> Dict[str, MacroEntry]:
        """
        Get a dictionary of all MacroEntry items.

        This represents the internal state of the MAC_ENTRY nodes.

        Entry attributes include: name, rawval, value, type.
        """
        encoding = self.string_encoding
        result = {}
        cdef MAC_ENTRY* entry = <MAC_ENTRY*>self.handle.list.node.next
        while entry != NULL:
            if entry.name:
                name = (entry.name or b"").decode(encoding)
                result[name] = MacroEntry(
                    name=name,
                    rawval=(entry.rawval or b"").decode(encoding),
                    value=(entry.value or b"").decode(encoding),
                    type=(entry.type or b"").decode(encoding),
                )
            entry = <MAC_ENTRY*>entry.node.next
        return result

    def _get_defined_names(self):
        cdef MAC_ENTRY* entry = <MAC_ENTRY*>self.handle.list.node.next
        cdef list names = []
        cdef set ignored_names = {b"", b"<scope>"}
        while entry != NULL:
            if entry.name != NULL and entry.name not in ignored_names:
                string_name = entry.name.decode(self.string_encoding)
                if string_name not in names:
                    names.append(string_name)
            entry = <MAC_ENTRY*>entry.node.next
        return names

    def _get_unique_names(self):
        defined_names = self._get_defined_names()
        yield from defined_names

        if self.use_environment:
            for name in os.environ:
                if name not in defined_names:
                    yield name

    def __len__(self):
        return len(list(self._get_unique_names()))

    def __iter__(self):
        yield from self._get_unique_names()

    def __getitem__(self, item):
        encoding = self.string_encoding
        # Start at the end for scoping
        cdef MAC_ENTRY* entry = <MAC_ENTRY*>self.handle.list.node.previous

        while entry != NULL:
            if entry.name:
                name = (entry.name or b"").decode(encoding)
                if name == item:
                    string_value = (entry.rawval or b"").decode(self.string_encoding)
                    return self.expand(
                        string_value,
                        max_length=max((1024, len(entry.rawval) * 2))
                    )
            entry = <MAC_ENTRY*>entry.node.previous

        if self.use_environment and item in os.environ:
            return os.environ[item]

        raise KeyError(item)

    def __setitem__(self, item, value):
        self.define(**{item: value})

    def _expand_with_length(
        self, value: str, max_length: int = 1024, *, empty_on_failure: bool = False
    ) -> str:
        """
        Expand a string, specifying the maximum length of the buffer.

        Trivia: 1024 is "MY_BUFFER_SIZE" in epics-base, believe it or not...
        """
        assert max_length > 0
        cdef char* buf = <char *>malloc(max_length)
        if not buf:
            raise MemoryError("Failed to allocate buffer")
        try:
            if macExpandString(self.handle, value.encode(self.string_encoding), buf, max_length) < 0:
                if empty_on_failure:
                    return ""
            return buf.decode(self.string_encoding)
        finally:
            free(buf)

    def _expand(self, value: str, *, empty_on_failure: bool = False) -> str:
        """Expand a string, using the implicit buffer length of 1024 used in EPICS."""
        cdef char buf[1024]
        #         n = macExpandString(handle, str, dest, destCapacity);
        # return < 0? return NULL...
        if macExpandString(self.handle, value.encode(self.string_encoding), buf, 1024) < 0:
            if empty_on_failure:
                return ""
        return buf.decode(self.string_encoding)
