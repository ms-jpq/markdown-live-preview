#!/usr/bin/env python3

from pathlib import Path
from subprocess import check_call

from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_style_by_name

_TOP_LV = Path(__file__).resolve().parent
_HL_CSS = _TOP_LV / ".cache" / "codehl.css"


def main() -> None:
    _HL_CSS.parent.mkdir(parents=True, exist_ok=True)
    style = get_style_by_name("friendly")
    css = HtmlFormatter(style=style).get_style_defs()
    _HL_CSS.write_text(css)

    node_bin = _TOP_LV / "node_modules" / ".bin"
    package = _TOP_LV / "markdown_live_preview"

    check_call((str(_TOP_LV / "lint.sh"),))
    check_call(
        (
            str(node_bin / "parcel"),
            "build",
            "--no-source-maps",
            "--out-dir",
            str(package / "js"),
            "--",
            str(package / "client" / "index.html"),
        )
    )


main()
