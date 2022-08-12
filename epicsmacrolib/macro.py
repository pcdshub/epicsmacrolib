import collections.abc
import contextlib
import dataclasses
from typing import Dict, Optional, Union

from _epicsmacrolib.macro import _MacroContext


@dataclasses.dataclass(frozen=True)
class MacroEntry:
    name: str
    rawval: str
    value: str
    type: str


class MacroContext(_MacroContext, collections.abc.MutableMapping):
    """
    A context for using EPICS macLib handle from Python.

    When other macro expansion tools just aren't enough, go with the one true
    macro expander - the one provided by EPICS - macLib.

    Parameters
    ----------
    use_environment : bool, optional
        Include environment variables when expanding macros.

    show_warnings : bool, optional
        Show warnings (see ``macSuppressWarning``).

    string_encoding : str, optional
        The default string encoding to use.  Defaults to latin-1, as these
        tools were written before utf-8 was really a thing.
    """

    #: Show warnings
    show_warnings: bool
    #: String encoding to use internally with macLib.
    string_encoding: str
    #: Include environment variables as macros.
    use_environment: bool

    def __init__(
        self,
        use_environment: bool = True,
        show_warnings: bool = False,
        string_encoding: str = "latin-1",
        macro_string: Optional[str] = None,
        macros: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            use_environment=use_environment,
            show_warnings=show_warnings,
            string_encoding=string_encoding,
        )

        if macros is not None:
            self.define(**macros)

        if macro_string is not None:
            self.define_from_string(macro_string)

    @contextlib.contextmanager
    def scoped(self, **macros: str):
        """A context manager to define macros (as kwargs) in a given scope."""
        self._push_scope()
        try:
            self.define(**macros)
            yield
        finally:
            self._pop_scope()

    def definitions_to_dict(
        self,
        defn: Union[str, bytes],
        string_encoding: str = ""
    ) -> Dict[str, str]:
        """
        Convert a definition string of the form ``A=value_a,B=value_a`` to a
        dictionary.

        Parameters
        ----------
        defn : Union[str, bytes]
            Definition string of the form ``A=value_a,B=value_a``.
        string_encoding : str, optional
            Encoding to use for the string, as macro lib works with bytes.
            Defaults to ``self.string_encoding``.

        Returns
        -------
        dict[str, str]
            Dictionary of name to value
        """
        return self._definitions_to_dict(
            defn,
            string_encoding=string_encoding or self.string_encoding,
        )

    def define_from_string(self, macro_string: str) -> Dict[str, str]:
        """Define macros with the standard VAR=VALUE syntax."""
        definitions = self.definitions_to_dict(macro_string)
        self.define(**definitions)
        return definitions

    def define(self, **macros: str) -> Dict[str, str]:
        """Use kwargs to define macros."""
        return super().define(**macros)

    def get_macro_details(self) -> Dict[str, MacroEntry]:
        """
        Get a dictionary of all MacroEntry items.

        This represents the internal state of the MAC_ENTRY nodes.

        Entry attributes include: name, rawval, value, type.
        """
        return super().get_macro_details()

    def get_macros(self) -> Dict[str, str]:
        """Get macros as a dictionary."""
        return dict(
            (macro.name, macro.value)
            for macro in self.get_macro_details().values()
        )

    def expand(
        self,
        value: str,
        *,
        empty_on_failure: bool = False,
        max_length: int = 1024,
    ) -> str:
        """
        Expand (interpolate) a string, replacing macros with values.

        By default, use the implicit buffer length of 1024 used in EPICS.

        Note that EPICS performs string interpolation line-by-line and not on a
        full-file basis.  See also ``expand_by_line``.

        Parameters
        ----------
        value : str
            The string to interpolate.
        empty_on_failure : bool, optional
            On failure (due to buffer size, a failed macExpandString result),
            return an empty string.
        max_length : int, optional
            Maximum length to use in macExpandString.

        Returns
        -------
        str
            The resulting interpolated string.
        """
        if max_length == 1024:
            return self._expand(value, empty_on_failure=empty_on_failure)
        return self._expand_with_length(
            value, empty_on_failure=empty_on_failure, max_length=max_length
        )

    def expand_by_line(self, contents: str, *, delimiter: str = "\n") -> str:
        """
        Expand a multi-line string, line-by-line.

        EPICS performs string interpolation line-by-line and not on a full-file
        basis.

        Parameters
        ----------
        contents : str
            The multi-line string.
        delimiter : str, optional
            The delimiter between lines.  Defaults to "\n".

        Returns
        -------
        str
            Interpolated multi-line string.
        """
        return delimiter.join(
            self.expand(line)
            for line in contents.splitlines()
        )


def macros_from_string(
    macro_string: str,
    use_environment: bool = False
) -> Dict[str, str]:
    """
    Get a macro dictionary from a macro string.

    Parameters
    ----------
    macro_string : str
        The macro string, in the format A=B,C=D,...

    use_environment : bool, optional
        Use environment variables as well.  Defaults to False.

    Returns
    -------
    macros : Dict[str, str]
        Macro key to value.
    """
    if not macro_string.strip():
        return {}
    macro_context = MacroContext(use_environment=use_environment)
    return macro_context.define_from_string(macro_string)


__all__ = ["MacroContext", "macros_from_string"]
