from . import _version

__version__ = _version.get_versions()['version']

from .iocsh import IocshRedirect as IocshRedirect  # noqa
from .iocsh import IocshSplit as IocshSplit  # noqa
from .iocsh import split_iocsh_line as split_iocsh_line
from .macro import MacroContext as MacroContext
from .macro import macros_from_string as macros_from_string

__all__ = ["MacroContext", "macros_from_string", "split_iocsh_line"]
