from html.parser import HTMLParser
from typing import Any, List, Optional, Tuple

HtmlDict = Any
Attrs = List[Tuple[str, Optional[str]]]


class ParseError(Exception):
    pass


class __Parser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__data: HtmlDict = {}
        self.__stack: List[str] = []

    def handle_starttag(self, tag: str, attrs: Attrs) -> None:
        print(attrs)
        pass

    def handle_endtag(self, tag: str) -> None:
        pass

    def handle_data(self, data: str) -> None:
        pass

    def consume(self) -> HtmlDict:
        if self.__stack:
            raise ParseError()
        else:
            return self.__data


def parse(html: str) -> HtmlDict:
    parser = __Parser()
    parser.feed(html)
    data = parser.consume()

    print(data)
    return data


def unparse(data: HtmlDict) -> str:
    return ""
