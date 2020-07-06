from asyncio import get_running_loop
from sys import stdin
from typing import Any, AsyncIterator


def readuntil(sep: bytes) -> str:
    buf = bytearray()
    while c := stdin.buffer.read(1):
        if c == sep:
            break
        else:
            buf.extend(c)
    return buf.decode()


async def stream(_: Any) -> AsyncIterator[str]:
    loop = get_running_loop()
    while chunk := await loop.run_in_executor(None, readuntil, b"\0"):
        yield chunk
