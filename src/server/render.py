from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from os.path import join
from shutil import which

from markdown import markdown

from .consts import __dir__


class ParseError(Exception):
    pass


def render_py(md: str) -> str:
    xhtml = markdown(md, output_format="xhtml", extensions=["extra"])
    return xhtml


async def render_node(md: str) -> str:
    node_md = join(__dir__, "dist", "render.js")
    proc = await create_subprocess_exec(
        "node", node_md, stdin=PIPE, stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = await proc.communicate(md.encode())
    if proc.returncode != 0:
        raise ParseError(stderr)
    else:
        xhtml = stdout.decode()
        return xhtml


async def render(markdown: str) -> str:
    if which("node"):
        return await render_node(markdown)
    else:
        return render_py(markdown)