#!/usr/bin/env python3

from os import chdir
from os.path import dirname, join
from subprocess import run

__dir__ = dirname(__file__)


def call(prog: str, *args: str) -> None:
    proc = run([prog, *args])
    if proc.returncode != 0:
        exit(proc.returncode)


def main() -> None:
    chdir(__dir__)
    node_bin = join("node_modules", ".bin")
    package = join("markdown_live_preview")
    js_dist = join(package, "js")

    call("./lint.sh")
    call(
        join(node_bin, "parcel"),
        "build",
        "--target",
        "node",
        "--bundle-node-modules",
        "--out-dir",
        js_dist,
        "--",
        join(package, "server", "render.ts"),
    )
    call(
        join(node_bin, "parcel"),
        "build",
        "--out-dir",
        js_dist,
        "--",
        join(package, "client", "index.html"),
    )


main()
