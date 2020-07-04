from typing import Any, Optional, Tuple

from html_to_dict import HtmlDict, parse, unparse


def reconciliate(prev: Optional[HtmlDict], curr: str) -> Tuple[HtmlDict, str]:
    nxt = parse(curr)
    unparse(nxt)
    return (nxt, curr)
