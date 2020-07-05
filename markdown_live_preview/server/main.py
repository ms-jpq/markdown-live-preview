from argparse import ArgumentParser, Namespace
from os import R_OK, access
from os.path import basename, dirname, join
from socket import getfqdn
from sys import stderr
from typing import AsyncIterator

from .reconciliate import reconciliate
from .render import render
from .server import Payload, build
from .watch import watch

__dir__ = dirname(__file__)


def parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("markdown")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-o", "--open", action="store_true")

    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    if not access(args.markdown, R_OK):
        print(f"cannot read -- {args.markdown}", file=stderr)
        exit(1)

    name = basename(args.markdown)
    cached, markdown = None, ""

    async def gen_payload() -> AsyncIterator[Payload]:
        while True:
            payload = Payload(title=name, markdown=markdown)
            yield payload

    async def gen_update() -> AsyncIterator[None]:
        nonlocal markdown, cached
        async for md in watch(args.markdown):
            xhtml = await render(md)
            cached, markdown = reconciliate(cached, xhtml)
            yield

    serve = build(
        localhost=not args.open,
        port=args.port,
        root=join(dirname(__dir__), "js"),
        payloads=gen_payload(),
        updates=gen_update(),
    )

    host = getfqdn() if args.open else "localhost"
    print(f"SERVING -- http://{host}:{args.port}")
    await serve()
