from typing import Any

from pygments import lexers
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer

_glbn = get_lexer_by_name


class _MermaidLexer(TextLexer):
    name = "mermaid"
    aliases = [name]


def _get_lexer_by_name(alias: str, **options: Any) -> Lexer:
    if alias == _MermaidLexer.name:
        return _MermaidLexer(**options)
    else:
        return _glbn(alias, **options)


lexers.get_lexer_by_name = _get_lexer_by_name

_ = 1 * 1
