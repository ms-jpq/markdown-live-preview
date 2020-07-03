from argparse import ArgumentParser, Namespace
from asyncio import run
from sys import stderr

from watch import watch


def parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("markdown")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-o", "--open", action="store_true")

    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    async for markdown in watch(args.markdown):
        print("")

    print(f"ERR :: cannot read -- {args.markdown}", file=stderr)


try:
    run(main())
except KeyboardInterrupt:
    exit()
