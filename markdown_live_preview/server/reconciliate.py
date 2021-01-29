from difflib import SequenceMatcher
from typing import Callable, Optional, Sequence, Union

from .html_to_dict import Node, TextNode, parse, unparse

_Nodes = Sequence[Union[Node, TextNode]]


def reconciliate() -> Callable[[str], str]:
    prev: Optional[Node] = None

    def diff_inplace(before: _Nodes, after: _Nodes) -> None:
        matcher = SequenceMatcher(isjunk=None, autojunk=False, a=after, b=before)
        for group in matcher.get_grouped_opcodes():
            for op, i, j, _, _ in group:
                if op == "replace":
                    for node in after[i:j]:
                        node.diff = True

                elif op == "delete":
                    for node in after[i:j]:
                        node.diff = True

                elif op == "insert":
                    for node in after[i:j]:
                        parent = node.parent and node.parent()
                        if parent:
                            parent.diff = True

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
