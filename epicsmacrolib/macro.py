import collections.abc
from typing import Dict

from _epicsmacrolib.macro import _MacroContext


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
