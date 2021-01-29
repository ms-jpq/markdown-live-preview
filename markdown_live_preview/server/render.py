from typing import Optional, cast

from markdown import markdown
from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.lexers.special import TextLexer
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound


def _get_lexer(file_name: Optional[str], text: str) -> Lexer:
    try:
        return get_lexer_for_filename(file_name)
    except (ClassNotFound, TypeError):
        try:
            return guess_lexer(text)
        except ClassNotFound:
            return TextLexer()


def _pprn_html(theme: str, filename: Optional[str], text: str) -> str:
    style = get_style_by_name(theme)
    fmt = get_formatter_by_name("html", style=style)

    lexer = _get_lexer(filename, text)
    pretty = highlight(text, lexer=lexer, formatter=fmt)
    return cast(str, pretty)


def render(md: str) -> str:
    xhtml = markdown(md, output_format="xhtml", extensions=["extra"])
    return xhtml
