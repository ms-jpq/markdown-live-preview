from itertools import zip_longest
from typing import Dict, List, Optional, Tuple, Union, cast

from .html_to_dict import Node, parse, unparse


def recon(
    prev: Union[Node, str, None], curr: Union[Node, str]
) -> Tuple[bool, Union[Node, str]]:
    if type(curr) == str:
        return prev != curr, curr
    else:
        p_node = type(prev) == Node

        curr = cast(Node, curr)
        depth = curr.depth
        p_tag = cast(Node, prev).tag if p_node else ""
        p_children = cast(Node, prev).children if p_node else []
        p_attrs = cast(Node, prev).attrs if p_node else []

        diff = False

        if p_tag != curr.tag:
            diff = True
        elif len(p_children) != len(curr.children):
            diff = True
        elif p_attrs != curr.attrs:
            diff = True

        next_lv = (
            recon(p, c)
            for p, c in zip_longest(p_children, curr.children)
            if c is not None
        )

        children: List[Union[Node, str]] = []
        for d, c in next_lv:
            children.append(c)
            diff = diff or d

        attrs: Dict[str, Optional[str]] = {
            **curr.attrs,
            "diff": str(diff),
            "depth": str(depth),
        }

        node = Node(depth=depth, tag=curr.tag, attrs=attrs, children=children)
        return diff, node


def reconciliate(prev: Optional[Node], curr: str) -> Tuple[Node, str]:
    nxt = parse(curr)
    if prev is None:
        return (nxt, curr)
    else:
        _, marked = recon(prev, nxt)
        assert type(marked) == Node
        parsed = unparse(cast(Node, marked))
        return (nxt, parsed)
