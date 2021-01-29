from typing import Callable, Sequence, no_type_check

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

_CODEHL_CLASS = "codehilite"


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
    )


def render(style: str) -> Callable[[str], str]:
    def render(md: str) -> str:
        _markdown = Markdown(output_format="xhtml", extensions=_extensions(style))
        return _markdown.convert(md)

    return render
