from difflib import SequenceMatcher
from pathlib import PurePosixPath
from typing import Callable, Optional, Sequence, Union
from urllib.parse import urlsplit, urlunsplit

from .html_to_dict import Node, TextNode, parse, unparse

_Nodes = Sequence[Union[Node, TextNode]]


def reconciliate() -> Callable[[str], str]:
    prev: Optional[Node] = None

    def localize(root: Node) -> None:
        for node in root:
            if isinstance(node, Node):
                if node.tag == "img" and (src := node.attrs.get("src")):
                    parsed = urlsplit(src)
                    if not parsed.scheme:
                        path = PurePosixPath(parsed.path)
                        if not path.is_absolute():
                            new_path = PurePosixPath("/cwd") / path
                            unparsed = parsed._replace(path=str(new_path))
                            new_uri = urlunsplit(unparsed)
                            node.attrs["src"] = new_uri

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
        localize(root)
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
