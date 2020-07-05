#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from os import chdir
from os.path import dirname, join
from subprocess import run

__dir__ = dirname(__file__)
package = join(__dir__, "markdown_live_preview")


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
        call("./lint.sh")
        call(
            join(node_bin, "tsc"),
            "--project",
            join(package, "server"),
            "--outDir",
            join(package, "js"),
        )
        call(
            join(node_bin, "parcel"),
            "build",
            "--out-dir",
            join(package, "js"),
            "--",
            join(package, "client", "index.html"),
        )


main()
