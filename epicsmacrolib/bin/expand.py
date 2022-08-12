"""
`epicsmacrolib expand` will interpolate text given macros.
"""

import argparse
import sys
from typing import List, Optional

from ..macro import MacroContext

DESCRIPTION = __doc__


def build_arg_parser(argparser=None):
    if argparser is None:
        argparser = argparse.ArgumentParser()

    argparser.description = DESCRIPTION
    argparser.formatter_class = argparse.RawTextHelpFormatter

    group = argparser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--string",
        dest="text_string",
        required=False,
        type=str,
        help="Text string to expand, in place of --file",
    )

    group.add_argument(
        "-f", "--file",
        type=str,
        dest="filename",
        required=False,
        help="Filename to expand. Use - for standard input.",
    )

    argparser.add_argument(
        "-m", "--macro",
        type=str,
        dest="macros",
        action="append",
        help="Define one or more macros in the form A=B...",
    )

    argparser.add_argument(
        "--use-env",
        action="store_true",
        help="Include environment variables as macros",
    )

    argparser.add_argument(
        "-d", "--delimiter",
        default="\n",
        help="Multi-line delimiter.",
    )

    return argparser


def main(
    filename: Optional[str] = None,
    text_string: Optional[str] = None,
    macros: Optional[List[str]] = None,
    use_env: bool = False,
    delimiter: str = "\n",
):

    if filename == "-":
        text_string = sys.stdin.read()
    elif filename is not None:
        with open(filename, "rt") as fp:
            text_string = fp.read()

    if text_string is None:
        raise ValueError("Filename or text string required")

    ctx = MacroContext(use_environment=use_env)
    for macro in macros or []:
        ctx.define_from_string(macro)

    print(ctx.expand_by_line(text_string, delimiter=delimiter))
