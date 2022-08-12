from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict, cast

from _epicsmacrolib.iocsh import split_iocsh_line as _split_iocsh_line


@dataclass
class IocshRedirect:
    fileno: int
    name: str
    mode: str


@dataclass
class IocshSplit:
    argv: List[str]
    redirects: Optional[Dict[int, IocshRedirect]] = None
    error: Optional[str] = None


class _IocshRedirect(TypedDict):
    fileno: int
    name: str
    mode: str


def split_iocsh_line(
    input_line: str,
    string_encoding: str = 'latin-1',
    ifs: bytes = b" \t(),\r",
    num_redirects: int = 5,
) -> IocshSplit:
    """
    Split ``input_line`` into words, according to how the IOC shell would.

    Note that this is almost a direct conversion of the original C code, making
    an attempt to avoid introducing inconsistencies between this implementation
    and the original.

    Parameters
    ----------
    input_line : str
        The line to split.

    Returns
    -------
    info : IocshSplit
    """
    res = _split_iocsh_line(
        input_line,
        string_encoding=string_encoding,
        ifs=ifs,
        num_redirects=num_redirects,
    )
    split = IocshSplit(argv=res["argv"], redirects=None, error=res["error"])

    redirects = res["redirects"]
    if redirects is not None:
        redirects = cast(Dict[int, _IocshRedirect], redirects)
        split.redirects = {
            idx: IocshRedirect(**redirect)
            for idx, redirect in redirects.items()
        }
    return split
