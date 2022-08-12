===============================
epicsmacrolib
===============================

.. image:: https://img.shields.io/travis/pcdshub/epicsmacrolib.svg
        :target: https://travis-ci.org/pcdshub/epicsmacrolib

.. image:: https://img.shields.io/pypi/v/epicsmacrolib.svg
        :target: https://pypi.python.org/pypi/epicsmacrolib


epics-base compliant macro tools.

---------
What?
---------

Do you want epics-base compliant macro expansion, with all of its idiosyncracies?

No? I didn't think so. This is a really boring project and you probably don't need it.

---------
Then why?
---------

This will be the future of the macro and IOC shell splitting tools in ``whatrecord``,
removing its reliance on Cython and epicscorelibs.

--------
Examples
--------

``macros_from_string``

.. code:: python

    from epicsmacrolib import macros_from_string

    macros_from_string("A=5,  B=$(A=3)")
    # -> {'A': '5', 'B': '$(A=3)'}


``MacroContext``

.. code:: python

    from epicsmacrolib import MacroContext

    ctx = MacroContext(use_environment=True)
    ctx.define(TEST="A")
    print(ctx.expand("TEST=$(TEST) SHELL=$(SHELL)"))
    # TEST=A SHELL=/bin/bash

    ctx = MacroContext(use_environment=False)
    ctx.define_from_string("A=5,B=6")
    ctx.define(C="7")
    print(ctx.expand("$(A) $(B) ${C} ${D=5} ${E}"))
    # -> 5 6 7 5 $(E)

    ctx = MacroContext(use_environment=False, show_warnings=True)
    ctx.define_from_string("A=5,B=6")
    ctx.define(C="7")
    print(ctx.expand("$(A) $(B) ${C} ${D=5} ${E}"))
    # -> 5 6 7 5 $(E,undefined)

    ctx.define_from_string("A=5,B=$(B)")
    print(ctx.expand("$(A) $(B)"))
    # -> 5 $(B,recursive)

    with ctx.scoped(A="10", B="0"):
        print(ctx.expand("$(A)"))
        # -> 10
        with ctx.scoped(A="0"):
            print(ctx.expand("$(A)"))
            # -> 0
        print(ctx.expand("$(A)"))
        # -> 10


``split_iocsh_line`` (like ``shlex.split``)

.. code:: python

    from epicsmacrolib import split_iocsh_line
    split_iocsh_line("dbLoadRecords > output_filename")
    # -> IocshSplit(
    #     argv=["dbLoadRecords"],
    #     redirects={1: IocshRedirect(fileno=1, name="output_filename", mode="w")},
    #     error=None,
    # )


--------
License
--------

The Python portions of this code is under a BSD-3 clause license
(``LicenseRef-BSD-3-Clause-SLAC``, see ``LICENSE``).
Portions of epics-base have been vendored in ``src`` under its original license
(see ``src/LICENSE``).
