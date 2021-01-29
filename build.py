#!/usr/bin/env python3

from locale import strxfrm
from os import linesep
from pathlib import Path
from shutil import rmtree
from subprocess import check_call

from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_all_styles, get_style_by_name

_TOP_LV = Path(__file__).resolve().parent
_CODEHL_CLASS = "codehilite"


def main() -> None:
    hl_css = _TOP_LV / ".cache" / "codehl.css"
    hl_css.parent.mkdir(parents=True, exist_ok=True)
    lines = (
        f".{_CODEHL_CLASS}.{name} {line}"
        for name in get_all_styles()
        for line in HtmlFormatter(style=get_style_by_name(name))
        .get_style_defs()
        .splitlines()
    )
    css = linesep.join(sorted(lines, key=strxfrm))
    hl_css.write_text(css)

    node_bin = _TOP_LV / "node_modules" / ".bin"
    package = _TOP_LV / "markdown_live_preview"
    js_dist = package / "js"

    rmtree(js_dist)
    check_call((str(_TOP_LV / "lint.sh"),))
    check_call(
        (
            str(node_bin / "parcel"),
            "build",
            "--no-source-maps",
            "--out-dir",
            str(js_dist),
            "--",
            str(package / "client" / "index.html"),
        )
    )


main()
