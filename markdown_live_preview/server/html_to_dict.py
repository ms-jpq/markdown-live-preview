from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from itertools import chain
from typing import (
    Iterator,
    MutableMapping,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    Union,
)
from weakref import ref

_SELF_CLOSING = {
    "area",
    "base",
    "basefont",
    "bgsound",
    "br",
    "col",
    "command",
    "embed",
    "frame",
    "hr",
    "image",
    "img",
    "input",
    "isindex",
    "keygen",
    "link",
    "menuitem",
    "meta",
    "nextid",
    "param",
    "source",
    "track",
    "wbr",
}


class ParseError(Exception):
    ...


@dataclass
class TextNode:
    parent: Optional[ref[Node]]
    text: str
    diff: bool = False

    def __eq__(self, o: object) -> bool:
        return isinstance(o, TextNode) and o.text == self.text

    def __hash__(self) -> int:
        return hash(self.text)


@dataclass
class Node:
    parent: Optional[ref[Node]]
    tag: str
    attrs: MutableMapping[str, Optional[str]] = field(default_factory=dict)
    children: MutableSequence[Union[Node, TextNode]] = field(default_factory=list)
    diff: bool = False

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Node) and o.tag == self.tag and o.attrs == self.attrs

    def __hash__(self) -> int:
        return hash((self.tag, *((key, val) for key, val in self.attrs.items())))

    def __iter__(self) -> Iterator[Union[Node, TextNode]]:
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child
            else:
                yield child


class _Parser(HTMLParser):
    def __init__(self, root_el: str):
        super().__init__()
        root = Node(parent=None, tag=root_el)
        self._root = root
        self._stack: MutableSequence[Node] = [root]

    def handle_starttag(
        self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]
    ) -> None:
        if stack := self._stack:
            parent = stack[-1]
            node = Node(parent=ref(parent), tag=tag, attrs=dict(attrs))
            parent.children.append(node)
            stack.append(node)
        else:
            raise ParseError()

    def handle_endtag(self, tag: str) -> None:
        if stack := self._stack:
            node = stack.pop()
            if node.tag != tag:
                raise ParseError()
        else:
            raise ParseError()

    def handle_data(self, data: str) -> None:
        if stack := self._stack:
            parent = stack[-1]
            node = TextNode(parent=ref(parent), text=data)
            parent.children.append(node)
        else:
            raise ParseError()

    def consume(self) -> Node:
        return self._root


def parse(html: str) -> Node:
    parser = _Parser(root_el="")
    parser.feed(html)
    node = parser.consume()

    return node


def unparse(node: Node) -> str:
    attrs = " ".join(
        f'{escape(k)}="{escape(v)}"' if v else escape(k)
        for k, v in chain(
            node.attrs.items(), (("diff", str(True)),) if node.diff else ()
        )
    )
    kids = "".join(
        unparse(child) if isinstance(child, Node) else escape(child.text)
        for child in node.children
    )

    if not node.tag:
        return kids
    elif node.tag in _SELF_CLOSING:
        return f"<{node.tag} {attrs}/>"
    else:
        return f"<{node.tag} {attrs}>{kids}</{node.tag}>"
