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
        call("./lint.sh")
        call(join(node_bin, "tsc"), "-p", "--", "src/server")
        call(
            join(node_bin, "parcel"), "build", "-d", "js", "--", "src/client/index.html"
        )


main()
