from difflib import SequenceMatcher
from typing import Callable, Sequence, Union

from .html_to_dict import Node, TextNode, parse, unparse


def reconciliate() -> Callable[[str], str]:
    prev: Sequence[Union[Node, TextNode]] = ()

    def recon(xhtml: str) -> str:
        nonlocal prev
        root = parse(xhtml)
        curr = tuple(root)

        matcher = SequenceMatcher(isjunk=None, autojunk=False, a=curr, b=prev)
        for group in matcher.get_grouped_opcodes():
            for op, i, j, _, _ in group:
                if op == "replace":
                    for node in curr[i:j]:
                        if isinstance(node, Node):
                            node.diff = True
                        else:
                            parent = node.parent and node.parent()
                            if parent:
                                parent.diff = True

                elif op == "delete":
                    for node in curr[i:j]:
                        if isinstance(node, Node):
                            node.diff = True
                        else:
                            parent = node.parent and node.parent()
                            if parent:
                                parent.diff = True

                elif op == "insert":
                    for node in curr[i:j]:
                        parent = node.parent and node.parent()
                        if parent:
                            parent.diff = True

                elif op == "equal":
                    pass

                else:
                    assert False

        prev = curr
        return unparse(root)

    return recon
