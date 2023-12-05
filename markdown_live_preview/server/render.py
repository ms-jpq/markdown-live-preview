from locale import strxfrm
from os import linesep
from typing import Callable, Sequence, no_type_check

from markdown import Markdown
from markdown.extensions import Extension
from markdown.extensions.abbr import makeExtension as abbr
from markdown.extensions.attr_list import makeExtension as attr_list
from markdown.extensions.footnotes import makeExtension as footnotes
from markdown.extensions.md_in_html import makeExtension as md_in_html
from markdown.extensions.sane_lists import makeExtension as sane_lists
from markdown.extensions.smarty import makeExtension as smarty
from markdown.extensions.tables import makeExtension as tables
from markdown.extensions.toc import makeExtension as toc
from markdown.extensions.wikilinks import makeExtension as wikilinks
from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_all_styles, get_style_by_name
from pymdownx.arithmatex import makeExtension as arithmatex
from pymdownx.b64 import makeExtension as b64
from pymdownx.betterem import makeExtension as betterem
from pymdownx.blocks.admonition import makeExtension as admonition
from pymdownx.blocks.definition import makeExtension as definition
from pymdownx.blocks.details import makeExtension as details
from pymdownx.blocks.html import makeExtension as html
from pymdownx.blocks.tab import makeExtension as tab
from pymdownx.caret import makeExtension as caret
from pymdownx.critic import makeExtension as critic
from pymdownx.highlight import makeExtension as highlight
from pymdownx.keys import makeExtension as keys
from pymdownx.mark import makeExtension as mark
from pymdownx.progressbar import makeExtension as progressbar
from pymdownx.saneheaders import makeExtension as saneheaders
from pymdownx.smartsymbols import makeExtension as smartsymbols
from pymdownx.snippets import makeExtension as snippets
from pymdownx.superfences import makeExtension as superfences
from pymdownx.tasklist import makeExtension as tasklist
from pymdownx.tilde import makeExtension as tilde

_CODEHL_CLASS = "codehilite"


@no_type_check
def _extensions(style: str) -> Sequence[Extension]:
    return (
        abbr(),
        admonition(),
        arithmatex(),
        attr_list(),
        b64(),
        betterem(),
        caret(),
        critic(),
        definition(),
        details(),
        footnotes(),
        highlight(
            css_class=f"{_CODEHL_CLASS} {style}",
            pygments_lang_class=True,
        ),
        html(),
        keys(),
        mark(),
        md_in_html(),
        progressbar(),
        sane_lists(),
        saneheaders(),
        smartsymbols(),
        smarty(),
        snippets(),
        superfences(),
        tab(),
        tables(),
        tasklist(),
        tilde(),
        toc(),
        wikilinks(),
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
    parser = Markdown(extensions=_extensions(style), tab_length=2)

    def render(md: str) -> str:
        return parser.convert(md)

    return render
