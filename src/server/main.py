from argparse import ArgumentParser, Namespace
from asyncio import run
from hashlib import sha1
from os.path import basename, join
from socket import getfqdn
from sys import stderr
from typing import AsyncIterator

from consts import __dir__

# from reconciliate import reconciliate
from render import render
from server import Payload, Update, build
from watch import watch


def parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("markdown")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-o", "--open", action="store_true")

    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    name = basename(args.markdown)
    markdown = ""

    async def gen_payload() -> AsyncIterator[Payload]:
        while True:
            payload = Payload(title=name, markdown=markdown)
            yield payload

    async def gen_update() -> AsyncIterator[Update]:
        async for markdown in watch(args.markdown):
            xhtml = await render(markdown)
            markdown = xhtml
            sha = sha1(markdown.encode()).hexdigest()
            update = Update(sha=str(sha))
            yield update

    serve = build(
        localhost=not args.open,
        port=args.port,
        root=join(__dir__, "dist"),
        payloads=gen_payload(),
        updates=gen_update(),
    )

    host = getfqdn() if args.open else "localhost"
    print(f"SERVING -- http://{host}:{args.port}")
    await serve()
    print(f"ERR :: cannot read -- {args.markdown}", file=stderr)


try:
    run(main())
except KeyboardInterrupt:
    exit()
