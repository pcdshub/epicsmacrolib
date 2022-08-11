from . import _version
__version__ = _version.get_versions()['version']

def _preload_shared_libraries():
    """
    Pre-load epicscorelibs shared libraries.

    Ensuring we find the ones distributed with the installed epicscorelibs.
    """
    import ctypes
    import pathlib
    import sys
    import epicscorelibs.lib

    lib_path = pathlib.Path(epicscorelibs.lib.__file__).resolve().parent

    pattern = {
        "darwin": "{lib_prefix}*.dylib",
        "linux": "{lib_prefix}.so.*",
        "windows": "{lib_prefix}*.dll"
    }.get(sys.platform, "{lib_prefix}.so.*")

    for lib_prefix in ["libCom", "libca", "libdbCore"]:
        print("preloading", lib_prefix)
        for lib in lib_path.glob(pattern.format(lib_prefix=lib_prefix)):
            print("preloading", lib_path, lib)
            ctypes.CDLL(str(lib))


_preload_shared_libraries()

from .macro import MacroContext, macros_from_string
from .iocsh import split_iocsh_line

__all__ = ["MacroContext", "macros_from_string", "split_iocsh_line"]
