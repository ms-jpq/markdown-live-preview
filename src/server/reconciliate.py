from itertools import zip_longest
from typing import Any, Optional, Tuple

from html_to_dict import Node, parse, unparse


def jee(prev: Node, curr: Node) -> Node:
    all_attrs = zip_longest(prev.attrs, curr.attrs)
    pass


def reconciliate(prev: Optional[Node], curr: str) -> Tuple[Node, str]:
    nxt = parse(curr)
    parsed = unparse(jee(prev, nxt) if prev else nxt)
    return (nxt, parsed)
