#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from http.server import ThreadingHTTPServer
from os import getcwd, environ
from os.path import basename, dirname, isdir, join, splitext
from sys import stderr
from typing import Any, Callable, Dict, List


try:
  import jinja2
  import markdown
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
    run(["pip", "install", "jinja2", "markdown"])


from jinja2 import Environment, FileSystemLoader, Template, StrictUndefined
from markdown import markdown


__dir__ = dirname(__file__)
__templates__ = join(__dir__, "templates")
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


def md_html(name: str) -> str:
  md = slurp(name)
  return markdown.markdown(md)


def render(template: Template, values: Dict[str, Any]) -> str:
  rendered: str = template.render(**values)
  return rendered


def srv(name: str) -> str:
  return 2


def main() -> None:
  args = parse_args()
  j2 = build_j2(__templates__)
  index_template = j2.get_template(__index_html__)
  md_html(args.markdown)


try:
  main()
except KeyboardInterrupt:
  pass

