#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from http.server import ThreadingHTTPServer
from os import getcwd, environ
from os.path import basename, dirname, isfile, isdir, join, splitext
from sys import stderr
from typing import Any, Callable, Dict, List, Tuple


try:
  import jinja2
  import markdown
  import watchdog
except ImportError:
  if environ.get("VIRTUAL_ENV") is None:
    venv_home = join(getcwd(), ".venv")
    if isdir(venv_home):
      print(f"Please Source VENV - {venv_home}", file=stderr)
    else:
      from venv import create
      create(venv_home, with_pip=True)
      print(f"Installed VENV - {venv_home}", file=stderr)
    exit(1)
  else:
    from subprocess import run
    run(["pip", "install", "jinja2", "markdown", "watchdog"], stdout=stderr)
    print("\n\n!!\n\n", file=stderr)


from jinja2 import Environment, FileSystemLoader, Template, StrictUndefined
from markdown import markdown
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent


__dir__ = dirname(__file__)
__site__ = join(__dir__, "site")
__templates__ = join(__dir__, "templates")
__css__ = join(__site__, "site.css")
__js__ = join(__site__, "site.js")
__index_html__ = "index.html.j2"


def parse_args() -> Namespace:
  parser = ArgumentParser()
  parser.add_argument("markdown")
  return parser.parse_args()


def build_j2(src: str, filters: Dict[str, Callable] = {}) -> Environment:
  j2 = Environment(
      enable_async=True,
      trim_blocks=True,
      lstrip_blocks=True,
      undefined=StrictUndefined,
      loader=FileSystemLoader(src))
  j2.filters = {**j2.filters, **filters}
  return j2


def slurp(name) -> str:
  with open(name) as fd:
    return fd.read()


def build_engine() -> Tuple[Template, Dict[str, str]]:
  j2 = build_j2(__templates__)
  index_template = j2.get_template(__index_html__)
  css = slurp(__css__)
  js = slurp(__js__)
  values = {"css": css, "js": js}
  return j2, values


def md_html(name: str, j2: Template, values: Dict[str, Any]) -> str:
  md = slurp(name)
  inner_html = markdown(md)
  rendered: str = j2.render({**values, "md": inner_html})
  return rendered


def main() -> None:
  args = parse_args()
  name = args.markdown
  if not isfile(name):
    print(f"Not a file -- {args.markdown}", file=stderr)
    exit(1)
  else:
    watch = FileModifiedEvent(name)


try:
  main()
except KeyboardInterrupt:
  pass

