import os
import shutil
import sys
from distutils.core import setup
from distutils.extension import Extension
from os import path

import versioneer
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext

min_version = (3, 7)

if sys.version_info < min_version:
    error = """
epicsmacrolib does not support Python {0}.{1}.
Python {2}.{3} and above is required. Check your Python version like so:

python3 --version

This may be due to an out-of-date pip. Make sure you have pip >= 9.0.1.
Upgrade pip like so:

pip install --upgrade pip
""".format(*sys.version_info[:2], *min_version)
    sys.exit(error)


if sys.platform == "darwin":
    # Required for building on macOS - an appropriate deployment target:
    os.environ.setdefault("MACOSX_DEPLOYMENT_TARGET", "10.9")

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines()
                    if not line.startswith('#')]


git_requirements = [r for r in requirements if r.startswith('git+')]
if git_requirements:
    print('User must install the following packages manually:')
    print()
    print("\n".join(f'* {r}' for r in git_requirements))
    print()

if os.environ.get("CONDA_BUILD_STATE") == "RENDER":
    epicscorelibs = None
else:
    try:
        import epicscorelibs
        import epicscorelibs.path
        from Cython.Build import cythonize
    except (ImportError, ModuleNotFoundError, Exception) as ex:
        print(f"""\
Sorry, the following are required to build `whatrecord`. Please install these first:
    epicscorelibs
    cython
{type(ex).__name__}: {ex}
""", file=sys.stderr)
        raise

# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = f"{path}{ext}"
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


def get_extensions():
    """Get the list of Cython extensions to add."""
    ext_options = dict(
        include_dirs=[
            epicscorelibs.path.base_path,
            epicscorelibs.path.include_path,
            "include",
        ],
        libraries=["Com", "dbCore"],
        library_dirs=[epicscorelibs.path.lib_path],
        language="c++",
    )

    extensions = [
        Extension(
            "epicsmacrolib.iocsh",
            ["epicsmacrolib/iocsh.pyx"],
            **ext_options
        ),
        Extension(
            "epicsmacrolib._macro",
            ["epicsmacrolib/_macro.pyx"],
            **ext_options,
        ),
    ]

    CYTHONIZE = bool(int(os.getenv("CYTHONIZE", "1")))

    if CYTHONIZE:
        compiler_directives = {"language_level": 3, "embedsignature": True}
        return cythonize(extensions, compiler_directives=compiler_directives)
    return no_cythonize(extensions)


with open("requirements.txt") as fp:
    install_requires = [
        line for line in fp.read().splitlines() if line and not line.startswith("#")
    ]

with open("README.rst", encoding="utf-8") as fp:
    readme = fp.read()


class BuildExt(build_ext):
    def run(self):
        super().run()
        for lib in ["Com", "ca", "dbCore"]:
            to = os.path.join(self.build_lib, "_whatrecord")
            from_ = epicscorelibs.path.get_lib(lib)
            print(f"Copying {from_} to {to}...")
            shutil.copy2(from_, to)


setup(
    name='epicsmacrolib',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='BSD',
    author='SLAC National Accelerator Laboratory',
    packages=find_packages(exclude=['docs', 'tests']),
    description='epics-base compliant macro tools',
    long_description=readme,
    long_description_content_type="text/x-rst",
    url='https://github.com/pcdshub/epicsmacrolib',  # noqa
    entry_points={
        "console_scripts": [
            "epicsmacrolib=epicsmacrolib.bin.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        'epicsmacrolib': [
            # When adding files here, remember to update MANIFEST.in as well,
            # or else they will not be included in the distribution on PyPI!
            # 'path/to/data_file',
        ]
    },
    install_requires=requirements,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    ext_modules=get_extensions() if epicscorelibs is not None else [],
)

