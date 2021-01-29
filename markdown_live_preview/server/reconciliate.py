from difflib import SequenceMatcher
from typing import Callable, Sequence, Union

from .html_to_dict import Node, TextNode, parse, unparse


def reconciliate() -> Callable[[str], str]:
    prev: Sequence[Union[Node, TextNode]] = ()

    def recon(xhtml: str) -> str:
        nonlocal prev
        node = parse(xhtml)
        curr = tuple(node)

        matcher = SequenceMatcher(isjunk=None, autojunk=False, a=curr, b=prev)
        for group in matcher.get_grouped_opcodes():
            for op, i, j, _, _ in group:
                if op == "replace":
                    for n in curr[i:j]:
                        if isinstance(n, Node):
                            n.diff = True
                        else:
                            parent = n.parent and n.parent()
                            if parent:
                                parent.diff = True

                elif op == "delete":
                    for n in curr[i:j]:
                        if isinstance(n, Node):
                            n.diff = True
                        else:
                            parent = n.parent and n.parent()
                            if parent:
                                parent.diff = True

                elif op == "insert":
                    for n in curr[i:j]:
                        parent = n.parent and n.parent()
                        if parent:
                            parent.diff = True

                elif op == "equal":
                    pass

                else:
                    assert False

        prev = curr
        return unparse(node)

    return recon
