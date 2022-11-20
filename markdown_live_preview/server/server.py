from asyncio import gather
from dataclasses import dataclass
from pathlib import Path, PurePath, PurePosixPath
from posixpath import join, sep
from typing import AsyncIterator, Awaitable, Callable
from weakref import WeakSet

from aiohttp.typedefs import Handler
from aiohttp.web import (
    Application,
    AppRunner,
    Response,
    RouteTableDef,
    TCPSite,
    WebSocketResponse,
    json_response,
    middleware,
)
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_middlewares import normalize_path_middleware
from aiohttp.web_request import BaseRequest, Request
from aiohttp.web_response import StreamResponse

from .consts import HEARTBEAT_TIME, JS_ROOT


@dataclass(frozen=True)
class Payload:
    follow: bool
    title: str
    sha: str
    xhtml: str


def build(
    localhost: bool, port: int, cwd: PurePath, gen: AsyncIterator[Payload]
) -> Callable[[], Awaitable[None]]:
    host = "localhost" if localhost else ""
    payload = Payload(follow=False, title="", sha="", xhtml="")

    @middleware
    async def cors(request: Request, handler: Handler) -> StreamResponse:
        resp = await handler(request)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    @middleware
    async def local_files(request: Request, handler: Handler) -> StreamResponse:
        try:
            rel = PurePosixPath(request.path).relative_to(join(sep, "cwd"))
            path = Path(cwd / rel).resolve(strict=True)
        except (ValueError, OSError):
            return await handler(request)
        else:
            if path.relative_to(cwd) and path.is_file():
                return FileResponse(path)
            else:
                return await handler(request)

    middlewares = (
        normalize_path_middleware(),
        local_files,
        cors,
    )
    routes = RouteTableDef()
    websockets: WeakSet = WeakSet()
    app = Application(middlewares=middlewares)

    @routes.get(sep)
    async def index_resp(request: BaseRequest) -> FileResponse:
        assert request
        return FileResponse(JS_ROOT / "index.html")

    assert index_resp

    @routes.get(join(sep, "ws"))
    async def ws_resp(request: BaseRequest) -> WebSocketResponse:
        ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
        await ws.prepare(request)
        websockets.add(ws)
        async for _ in ws:
            pass
        return ws

    assert ws_resp

    @routes.get(join(sep, "api", "info"))
    async def meta_resp(request: BaseRequest) -> StreamResponse:
        assert request

        json = {"follow": payload.follow, "title": payload.title, "sha": payload.sha}
        return json_response(json)

    assert meta_resp

    @routes.get(join(sep, "api", "markdown"))
    async def markdown_resp(request: BaseRequest) -> StreamResponse:
        assert request

        return Response(text=payload.xhtml, content_type="text/html")

    assert markdown_resp

    async def broadcast() -> None:
        nonlocal payload
        async for p in gen:
            payload = p
            tasks = (ws.send_str("") for ws in websockets)
            await gather(*tasks)

    routes.static(prefix=sep, path=JS_ROOT)
    app.add_routes(routes)

    async def start() -> None:
        runner = AppRunner(app)
        try:
            await runner.setup()
            site = TCPSite(runner, host=host, port=port)
            await site.start()
            await broadcast()
        finally:
            await runner.cleanup()

    return start
