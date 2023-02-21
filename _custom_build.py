import os
import pathlib
import sys

from Cython.Build import cythonize
from setuptools import Extension
from setuptools.command.build_py import build_py as _build_py

if sys.platform == "darwin":
    # Required for building on macOS - an appropriate deployment target:
    os.environ.setdefault("MACOSX_DEPLOYMENT_TARGET", "10.9")


def get_extensions():
    """Get the list of Cython extensions to add."""
    SRC_DIR = pathlib.Path("src")
    ext_options = dict(
        include_dirs=["./src"],
        libraries=[],
        library_dirs=["./src"],
        language="c++",
    )

    macro_lib_sources = list(str(path) for path in SRC_DIR.glob("*.c"))
    extensions = [
        Extension("_epicsmacrolib.iocsh", ["epicsmacrolib/iocsh.pyx"], **ext_options),
        Extension(
            "_epicsmacrolib.macro",
            ["epicsmacrolib/macro.pyx"] + macro_lib_sources,
            **ext_options,
        ),
    ]

    compiler_directives = {"language_level": 3, "embedsignature": True}
    return cythonize(extensions, compiler_directives=compiler_directives)


class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()

    def initialize_options(self):
        super().initialize_options()
        self.distribution.ext_modules = (self.distribution.ext_modules or []) + get_extensions()
