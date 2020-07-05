from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from os.path import dirname, join
from shutil import which
from typing import Awaitable, Callable

from markdown import markdown

node_md = join(dirname(dirname(__file__)), "js", "render.js")


class ParseError(Exception):
    pass


async def render_py(md: str) -> str:
    xhtml = markdown(md, output_format="xhtml", extensions=["extra"])
    return xhtml


async def render_node(md: str) -> str:
    proc = await create_subprocess_exec(
        "node", node_md, stdin=PIPE, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = await proc.communicate(md.encode())
    if proc.returncode != 0:
        raise ParseError(stderr.decode())
    else:
        xhtml = stdout.decode()
        return xhtml


def render() -> Callable[[str], Awaitable[str]]:
    if which("node"):
        return render_node
    else:
        return render_py
