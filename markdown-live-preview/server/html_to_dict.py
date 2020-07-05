from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple, Union, cast


class ParseError(Exception):
    pass


@dataclass
class Node:
    depth: int
    tag: str
    attrs: Dict[str, Optional[str]] = field(default_factory=dict)
    children: List[Union[Node, str]] = field(default_factory=list)


class Parser(HTMLParser):
    def __init__(self, *args, root_el: str, **kwargs):
        super().__init__(*args, **kwargs)
        root = Node(depth=0, tag=root_el)
        self.__root = root
        self.__stack: List[Node] = [root]

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if stack := self.__stack:
            node = Node(depth=len(stack), tag=tag, attrs=dict(attrs))
            parent = stack[-1]
            parent.children.append(node)
            stack.append(node)
        else:
            raise ParseError()

    def handle_endtag(self, tag: str) -> None:
        if stack := self.__stack:
            node = stack.pop()
            if node.tag != tag:
                raise ParseError()
        else:
            raise ParseError()

    def handle_data(self, data: str) -> None:
        if stack := self.__stack:
            parent = stack[-1]
            parent.children.append(data)
        else:
            raise ParseError()

    def consume(self) -> Node:
        return self.__root


def parse(html: str) -> Node:
    parser = Parser(root_el="div")
    parser.feed(html)
    node = parser.consume()

    return node


def unparse(node: Node) -> str:
    attrs = " ".join(f'{k}="{v}"' if v else k for k, v in node.attrs.items())
    opening = f"<{node.tag} {attrs}>"
    closing = f"</{node.tag}>"
    middle = "".join(
        unparse(cast(Node, c)) if type(c) == Node else cast(str, c)
        for c in node.children
    )
    return f"{opening}{middle}{closing}"
