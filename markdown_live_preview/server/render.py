from html import escape
from locale import strxfrm
from os import linesep
from typing import Callable, Match, Sequence, Tuple, Union, no_type_check

from markdown import Markdown
from markdown.extensions import Extension
from markdown.extensions.abbr import makeExtension as abbr
from markdown.extensions.admonition import makeExtension as admonition
from markdown.extensions.attr_list import makeExtension as attr_list
from markdown.extensions.codehilite import makeExtension as codehilite
from markdown.extensions.def_list import makeExtension as def_list
from markdown.extensions.fenced_code import makeExtension as fenced_code
from markdown.extensions.footnotes import makeExtension as footnotes
from markdown.extensions.md_in_html import makeExtension as md_in_html
from markdown.extensions.nl2br import makeExtension as nl2br
from markdown.extensions.sane_lists import makeExtension as sane_lists
from markdown.extensions.smarty import makeExtension as smarty
from markdown.extensions.tables import makeExtension as tables
from markdown.extensions.toc import makeExtension as toc
from markdown.extensions.wikilinks import makeExtension as wikilinks
from markdown.inlinepatterns import InlineProcessor
from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_all_styles, get_style_by_name

_CODEHL_CLASS = "codehilite"


class _B4HtmlProcessor(InlineProcessor):
    """
    The builtin html processors store & restore `<...>`
    But does not check if `<...>` is valid html

    This processor tries to escape invalid html
    before the builtin ones
    """

    PRIORITY = 91

    def __init__(self) -> None:
        super().__init__(pattern="<([^>]*)>")

    @no_type_check
    def handleMatch(
        self, m: Match[str], data: str
    ) -> Union[Tuple[str, int, int], Tuple[None, None, None]]:
        maybe_html = m.group(1)
        chars = {*maybe_html}

        if maybe_html.endswith("/") or "<" in chars or chars > {"=", '"'}:
            return None, None, None
        else:
            escaped = escape(data)
            return escaped, m.start(0), m.end(0)


class _UserExts(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(
            _B4HtmlProcessor(),
            name=_B4HtmlProcessor.__qualname__,
            priority=_B4HtmlProcessor.PRIORITY,
        )


@no_type_check
def _extensions(style: str) -> Sequence[Extension]:
    return (
        abbr(),
        admonition(),
        attr_list(),
        codehilite(css_class=f"{_CODEHL_CLASS} {style}"),
        def_list(),
        fenced_code(),
        footnotes(),
        md_in_html(),
        nl2br(),
        sane_lists(),
        smarty(),
        tables(),
        toc(),
        wikilinks(),
        _UserExts(),
    )


def css() -> str:
    lines = (
        f".{_CODEHL_CLASS}.{name} {line}"
        for name in get_all_styles()
        for line in HtmlFormatter(style=get_style_by_name(name))
        .get_style_defs()
        .splitlines()
    )
    css = linesep.join(sorted(lines, key=strxfrm))
    return css


def render(style: str) -> Callable[[str], str]:
    _markdown = Markdown(extensions=_extensions(style))

    def render(md: str) -> str:
        return _markdown.convert(md)

    return render
