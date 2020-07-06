from asyncio import StreamReader, StreamWriter, create_subprocess_exec
from asyncio.subprocess import PIPE, Process
from os.path import dirname, join
from shutil import which
from typing import Awaitable, Callable, cast

from markdown import markdown

node_md = join(dirname(dirname(__file__)), "js", "render.js")


async def render_py() -> Callable[[str], Awaitable[str]]:
    async def render(md: str) -> str:
        xhtml = markdown(md, output_format="xhtml", extensions=["extra"])
        return xhtml

    return render


async def render_node() -> Callable[[str], Awaitable[str]]:
    proc, stdin, stdout = None, None, None

    async def init() -> None:
        nonlocal proc, stdin, stdout
        if proc and proc.returncode is None:
            return
        proc = await create_subprocess_exec(
            "node", node_md, stdin=PIPE, stdout=PIPE, stderr=PIPE
        )

    async def render(md: str) -> str:
        await init()
        p = cast(Process, proc)
        stdin = cast(StreamWriter, p.stdin)
        stdout = cast(StreamReader, p.stdout)

        SEP = b"\0"
        stdin.write(md.encode())
        stdin.write(SEP)
        xhtml = await stdout.readuntil(SEP)
        return xhtml.decode()

    return render


async def render() -> Callable[[str], Awaitable[str]]:
    if which("node"):
        return await render_node()
    else:
        return await render_py()
