from typing import Any, Optional, Tuple

from html_to_dict import parse, unparse


def reconciliate(prev: Optional[Any], curr: str) -> Tuple[Any, str]:
    nxt = parse(curr)
    unparse(nxt)
    return (nxt, curr)
