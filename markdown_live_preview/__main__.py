from argparse import ArgumentParser, Namespace
from asyncio import run
from pathlib import Path
from socket import getfqdn
from sys import exit, stderr
from typing import AsyncIterator, NoReturn
from webbrowser import open as open_w

from .server.log import log
from .server.render import render
from .server.server import Payload, build
from .server.watch import watch


def _parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("markdown")

    location = parser.add_argument_group()
    location.add_argument("-p", "--port", type=int, default=8080)
    location.add_argument("-o", "--open", action="store_true")

    watcher = parser.add_argument_group()
    watcher.add_argument("-t", "--throttle", type=float, default=0.10)

    behaviour = parser.add_argument_group()
    behaviour.add_argument("--nf", "--no-follow", dest="follow", action="store_false")
    behaviour.add_argument("--nb", "--no-browser", dest="browser", action="store_false")

    return parser.parse_args()


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
            async for _ in watch(args.throttle, path=path):
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

        serve = build(
            localhost=not args.open,
            port=args.port,
            cwd=path.parent,
            gen=gen(),
        )
        host = getfqdn() if args.open else "localhost"
        uri = f"http://{host}:{args.port}"
        if args.browser:
            open_w(uri)
        log.info("%s", f"SERVING -- {uri}")
        await serve()
        return 0


def main() -> NoReturn:
    try:
        code = run(_main())
    except KeyboardInterrupt:
        stderr.close()
        exit(130)
    else:
        exit(code)


if __name__ == "__main__":
    main()
