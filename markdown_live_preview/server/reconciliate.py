from difflib import SequenceMatcher
from typing import Callable, Optional, Sequence, Union

from .html_to_dict import Node, TextNode, parse, unparse

_Nodes = Sequence[Union[Node, TextNode]]


def reconciliate() -> Callable[[str], str]:
    prev: Optional[Node] = None

    def set_diff(nodes: _Nodes) -> None:
        for node in nodes:
            node.diff = True
            if isinstance(node, TextNode) and not node.text.isspace():
                if parent := node.parent and node.parent():
                    parent.diff = True

    def diff_inplace(before: _Nodes, after: _Nodes) -> None:
        matcher = SequenceMatcher(isjunk=None, autojunk=False, a=after, b=before)
        for group in matcher.get_grouped_opcodes():
            for op, i, j, _, _ in group:
                if op == "replace":
                    set_diff(after[i:j])

                elif op == "delete":
                    set_diff(after[i:j])

                elif op == "insert":
                    set_diff(after[i:j])

                elif op == "equal":
                    pass

                else:
                    assert False

    def recon(xhtml: str) -> str:
        nonlocal prev
        root = parse(xhtml)
        if not prev:
            prev = root
            return unparse(root)
        else:
            before, after = tuple(prev), tuple(root)
            if before == after:
                return unparse(prev)
            else:
                diff_inplace(before, after=after)
                prev = root
                return unparse(root)

    return recon
