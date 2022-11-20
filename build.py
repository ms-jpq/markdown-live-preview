#!/usr/bin/env python3

from pathlib import Path
from shutil import rmtree
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
            try:
                path.unlink(missing_ok=True)
            except IsADirectoryError:
                rmtree(path)

    check_call(("mypy", "--", "."), cwd=_TOP_LV)
    check_call(
        (node_bin / "vite", "build", "--outDir", js_dist, "--assetsDir", "."),
        cwd=package / "client",
    )


main()
