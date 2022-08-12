from . import _version
__version__ = _version.get_versions()['version']

from .macro import MacroContext as MacroContext
from .macro import macros_from_string as macros_from_string
from .iocsh import IocshRedirect as IocshRedirect
from .iocsh import IocshSplit as IocshSplit
from .iocsh import split_iocsh_line as split_iocsh_line

__all__ = []
