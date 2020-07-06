from argparse import ArgumentParser, Namespace
from hashlib import sha1
from os import R_OK, access
from os.path import basename, dirname, join
from socket import getfqdn
from sys import stderr
from typing import AsyncIterator
from webbrowser import open as open_w

from .reconciliate import reconciliate
from .render import render
from .server import Payload, build
from .stream import stream
from .watch import watch

__dir__ = dirname(__file__)


def parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("markdown")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-o", "--open", action="store_true")
    parser.add_argument("-n", "--no-follow", dest="follow", action="store_false")

    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    if (not args.stdin) and (not access(args.markdown, R_OK)):
        print(f"cannot read -- {args.markdown}", file=stderr)
        exit(1)

    render_f = await render()
    watch_f = stream if args.stdin else watch

    name = basename(args.markdown)
    cached, markdown = None, ""
    sha = ""

    async def gen_payload() -> AsyncIterator[Payload]:
        while True:
            payload = Payload(
                follow=args.follow, title=name, sha=sha, markdown=markdown
            )
            yield payload

    async def gen_update() -> AsyncIterator[None]:
        nonlocal markdown, cached, sha
        async for md in watch_f(args.markdown):
            xhtml = await render_f(md)
            cached, markdown = reconciliate(cached, xhtml)
            sha = sha1(markdown.encode()).hexdigest()
            yield

    serve = build(
        localhost=not args.open,
        port=args.port,
        root=join(dirname(__dir__), "js"),
        payloads=gen_payload(),
        updates=gen_update(),
    )

    async def post() -> None:
        host = getfqdn() if args.open else "localhost"
        uri = f"http://{host}:{args.port}"
        open_w(uri)
        print(f"SERVING -- {uri}")

    await serve(post)
