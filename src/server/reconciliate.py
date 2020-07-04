from itertools import zip_longest
from typing import Dict, Optional, Tuple, Union, cast

from .html_to_dict import Node, parse, unparse


def recon(prev: Union[Node, str, None], curr: Union[Node, str]) -> Union[Node, str]:
    if type(curr) == str:
        return curr
    else:
        curr = cast(Node, curr)
        depth = curr.depth
        attrs: Dict[str, Optional[str]] = {**curr.attrs} if prev == curr else {
            **curr.attrs,
            "diff": "true",
            "depth": str(depth),
        }
        p_children = cast(Node, prev).children if type(prev) == Node else []
        children = [
            recon(p, c)
            for p, c in zip_longest(p_children, curr.children)
            if c is not None
        ]
        node = Node(depth=depth, tag=curr.tag, attrs=attrs, children=children)
        return node


def reconciliate(prev: Optional[Node], curr: str) -> Tuple[Node, str]:
    nxt = parse(curr)
    marked = recon(prev, nxt)
    assert type(marked) == Node
    parsed = unparse(cast(Node, marked))
    return (nxt, parsed)
