from html.parser import HTMLParser
from typing import Any


class Parser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(dir(self))

    def handle_starttag(self, tag: str, attrs) -> None:
        pass

    def handle_endtag(self, tag: str) -> None:
        pass

    def handle_charref(self, name) -> None:
        pass

    def handle_entityref(self, name) -> None:
        pass

    def handle_data(self, data) -> None:
        pass

    def handle_comment(self, data) -> None:
        pass

    def handle_decl(self, decl) -> None:
        pass

    def handle_pi(self, data) -> None:
        pass

    def unknown_decl(self, data) -> None:
        pass

    def end(self) -> Any:
        return ""
        # return self.data


def parse(html: str) -> Any:
    parser = Parser()
    parser.feed(html)
    data = parser.end()

    print(data)
    return data


def unparse(data: Any) -> str:
    return ""
