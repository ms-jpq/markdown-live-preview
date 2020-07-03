from argparse import ArgumentParser, Namespace
from asyncio import run

from watch import watch


def parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("markdown")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-o", "--open", action="store_true")

    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    async for event in watch(args.markdown):
        print(event)


try:
    run(main())
except KeyboardInterrupt:
    exit()
