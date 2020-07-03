#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from os import chdir, environ
from os.path import dirname, join
from subprocess import run

__dir__ = dirname(__file__)


def path_mod() -> None:
    chdir(__dir__)
    node_bin = join(__dir__, "node_modules", ".bin")
    environ["PATH"] = environ["PATH"] + ":" + node_bin


def call(prog: str, *args: str) -> None:
    proc = run([prog, *args])
    if proc.returncode != 0:
        exit(proc.returncode)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-w", "--watch", action="store_true")
    return parser.parse_args()


def main() -> None:
    path_mod()
    args = parse_args()
    if args.watch:
        pass
    else:
        call("./lint.sh")
        call("tsc", "-p", "src/server")
        call("parcel", "build", "src/client/index.html")


main()
