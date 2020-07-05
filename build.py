#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from os import chdir
from os.path import dirname, join
from subprocess import run

__dir__ = dirname(__file__)


def call(prog: str, *args: str) -> None:
    proc = run([prog, *args])
    if proc.returncode != 0:
        exit(proc.returncode)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-w", "--watch", action="store_true")
    return parser.parse_args()


def main() -> None:
    chdir(__dir__)
    args = parse_args()
    node_bin = join(__dir__, "node_modules", ".bin")
    if args.watch:
        pass
    else:
        package = join(__dir__, "markdown_live_preview")
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
