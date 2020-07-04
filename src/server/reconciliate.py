from itertools import zip_longest
from typing import Dict, Optional, Tuple, Union, cast

from html_to_dict import Node, parse, unparse


def recon(prev: Union[Node, str, None], curr: Union[Node, str]) -> Union[Node, str]:
    if type(curr) == str:
        return curr
    elif type(prev) != Node:
        return curr
    else:
        prev, curr = cast(Node, prev), cast(Node, curr)
        attrs: Dict[str, Optional[str]] = {**curr.attrs} if prev == curr else {
            **curr.attrs,
            "diff": "true",
        }
        children = [
            recon(p, c)
            for p, c in zip_longest(prev.children, curr.children)
            if c is not None
        ]
        node = Node(tag=curr.tag, attrs=attrs, children=children)
        return node


def reconciliate(prev: Optional[Node], curr: str) -> Tuple[Node, str]:
    nxt = parse(curr)
    marked = recon(prev, nxt)
    assert type(marked) == Node
    parsed = unparse(cast(Node, marked))
    return (nxt, parsed)
