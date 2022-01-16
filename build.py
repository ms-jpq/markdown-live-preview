#!/usr/bin/env python3

from pathlib import Path
from subprocess import check_call, check_output
from sys import executable

_TOP_LV = Path(__file__).resolve().parent


def main() -> None:
    hl_css = _TOP_LV / ".cache" / "codehl.css"
    hl_css.parent.mkdir(parents=True, exist_ok=True)
    css = check_output((executable, "-m", "markdown_live_preview.server"), cwd=_TOP_LV)
    hl_css.write_bytes(css)

    node_bin = _TOP_LV / "node_modules" / ".bin"
    package = _TOP_LV / "markdown_live_preview"
    js_dist = package / "js"

    for path in js_dist.iterdir():
        if path.name not in {"__init__.py", ".gitignore"}:
            path.unlink(missing_ok=True)

    check_call(("mypy", "--", "."), cwd=_TOP_LV)
    check_call(
        (
            node_bin / "parcel",
            "build",
            "--no-source-maps",
            "--dist-dir",
            js_dist,
            "--",
            package / "client" / "index.html",
        ),
        cwd=_TOP_LV,
    )


main()
