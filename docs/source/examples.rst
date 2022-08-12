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
