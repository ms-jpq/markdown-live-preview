#!/usr/bin/env python3

from pathlib import Path
from subprocess import check_call

_TOP_LV = Path(__file__).resolve().parent


def main() -> None:
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
