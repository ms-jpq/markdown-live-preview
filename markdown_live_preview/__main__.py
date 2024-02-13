from argparse import ArgumentParser, Namespace
from asyncio import run
from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager
from functools import lru_cache
from ipaddress import IPv4Address, IPv6Address, ip_address
from os import environ
from pathlib import Path
from socket import (
    IPPROTO_IPV6,
    IPV6_V6ONLY,
    AddressFamily,
    SocketKind,
    getfqdn,
    has_ipv6,
    socket,
)
from sys import exit, stderr
from typing import NoReturn
from webbrowser import open as open_w

from .server.lexers import _
from .server.log import log
from .server.render import render
from .server.server import Payload, build
from .server.watch import watch

assert _

_TITLE = Path(__file__).resolve(strict=True).parent.name


def _parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("markdown")

    location = parser.add_argument_group()
    location.add_argument("-p", "--port", type=int, default=0)
    location.add_argument("-o", "--open", action="store_true")

    watcher = parser.add_argument_group()
    watcher.add_argument("-t", "--throttle", type=float, default=0.10)

    behaviour = parser.add_argument_group()
    behaviour.add_argument("--nf", "--no-follow", dest="follow", action="store_false")
    behaviour.add_argument("--nb", "--no-browser", dest="browser", action="store_false")

    return parser.parse_args()


@contextmanager
def _title() -> Iterator[None]:
    def cont(title: str) -> None:
        if "TMUX" in environ:
            stderr.write(f"\x1Bk{title}\x1B\\")
        else:
            stderr.write(f"\x1B]0;{title}\x1B\\")

        stderr.flush()

    cont(_TITLE)
    try:
        yield None
    finally:
        cont("")


def _sock(open: bool, port: int) -> socket:
    fam = AddressFamily.AF_INET6 if has_ipv6 else AddressFamily.AF_INET
    sock = socket(family=fam, type=SocketKind.SOCK_STREAM)
    host = "" if open else "localhost"
    if fam == AddressFamily.AF_INET6:
        sock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)
    sock.bind((host, port))
    return sock


@lru_cache(maxsize=None)
def _fqdn() -> str:
    return getfqdn()


def _addr(sock: socket) -> str:
    addr, bind, *_ = sock.getsockname()
    ip = ip_address(addr)
    map = {
        IPv4Address(0): _fqdn(),
        IPv6Address(0): _fqdn(),
        IPv4Address(1): "localhost",
        IPv6Address(1): "localhost",
    }
    mapped = map.get(ip, ip)
    host = f"[{mapped}]" if isinstance(mapped, IPv6Address) else str(mapped)
    return f"{host}:{bind}"


async def _main() -> int:
    args = _parse_args()
    try:
        path = Path(args.markdown).resolve(strict=True)
    except OSError as e:
        log.critical("%s", e)
        return 1
    else:
        render_f = render("friendly")

        async def gen() -> AsyncIterator[Payload]:
            async for __ in watch(args.throttle, path=path):
                assert __ or True
                try:
                    md = path.read_text()
                except OSError as e:
                    log.critical("%s", e)
                    break
                else:
                    xhtml = render_f(md)
                    sha = str(hash(xhtml))
                    payload = Payload(
                        follow=args.follow, title=path.name, sha=sha, xhtml=xhtml
                    )
                    yield payload

        sock = _sock(args.open, port=args.port)

        serve = build(sock, cwd=path.parent, gen=gen())
        with _title():
            async for __ in serve():
                assert not __
                bind = _addr(sock)
                uri = f"http://{bind}"
                log.info("%s", f"SERVING -- {uri}")
                if args.browser:
                    open_w(uri)

        return 0


def main() -> NoReturn:
    try:
        code = run(_main())
    except KeyboardInterrupt:
        exit(130)
    else:
        exit(code)


if __name__ == "__main__":
    main()
