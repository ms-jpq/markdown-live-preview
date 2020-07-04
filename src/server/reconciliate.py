from itertools import zip_longest
from typing import Dict, Optional, Tuple, Union, cast

from html_to_dict import Node, parse, unparse

ParseState = Union[Node, str, None]


def recon(prev: ParseState, curr: ParseState) -> ParseState:
    if curr is None:
        return curr
    elif prev is None:
        return curr
    elif type(prev) != type(curr):
        return curr
    elif type(curr) == str and prev != curr:
        return curr
    else:
        prev, curr = cast(Node, prev), cast(Node, curr)
        marked = prev.tag != curr.tag or prev.attrs != curr.attrs
        attrs: Dict[str, Optional[str]] = {**curr.attrs, "id": "focus"} if marked else {
            **curr.attrs
        }
        children = [
            n
            for n in (recon(p, c) for p, c in zip_longest(prev.children, curr.children))
            if n is not None
        ]
        return Node(tag=curr.tag, attrs=attrs, children=children)


def reconciliate(prev: Optional[Node], curr: str) -> Tuple[Node, str]:
    nxt = parse(curr)
    marked = recon(prev, nxt)
    assert type(marked) == Node
    parsed = unparse(cast(Node, marked))
    return (nxt, parsed)
