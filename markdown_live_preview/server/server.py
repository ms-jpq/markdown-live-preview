from asyncio import gather
from dataclasses import dataclass
from pathlib import PurePath
from typing import AsyncIterator, Awaitable, Callable
from weakref import WeakSet

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
from aiohttp.web_middlewares import _Handler, normalize_path_middleware
from aiohttp.web_request import BaseRequest, Request
from aiohttp.web_response import StreamResponse

from .consts import HEARTBEAT_TIME, JS_ROOT


@dataclass(frozen=True)
class Payload:
    follow: bool
    title: str
    sha: str
    markdown: str


@middleware
async def _cors(request: Request, handler: _Handler) -> StreamResponse:
    resp = await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


_middlewares = (
    normalize_path_middleware(),
    _cors,
)
_routes = RouteTableDef()
_websockets: WeakSet[WebSocketResponse] = WeakSet()
_app = Application(middlewares=_middlewares)


@_routes.route("*", "/")
async def _index_resp(request: BaseRequest) -> FileResponse:
    return FileResponse(JS_ROOT / "index.html")


@_routes.get("/ws")
async def _ws_resp(request: BaseRequest) -> WebSocketResponse:
    ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
    await ws.prepare(request)
    _websockets.add(ws)
    async for _ in ws:
        pass
    return ws


def build(
    localhost: bool, port: int, cwd: PurePath, gen: AsyncIterator[Payload]
) -> Callable[[], Awaitable[None]]:
    host = "localhost" if localhost else ""
    payload = Payload(follow=False, title="", sha="", markdown="")

    @_routes.get("/api/info")
    async def meta_resp(request: BaseRequest) -> StreamResponse:
        json = {"follow": payload.follow, "title": payload.title, "sha": payload.sha}
        return json_response(json)

    @_routes.get("/api/markdown")
    async def markdown_resp(request: BaseRequest) -> StreamResponse:
        return Response(text=payload.markdown, content_type="text/html")

    async def broadcast() -> None:
        nonlocal payload
        async for p in gen:
            payload = p
            tasks = (ws.send_str("") for ws in _websockets)
            await gather(*tasks)

    _routes.static(prefix="/", path=JS_ROOT)
    _routes.static(prefix="/cwd/", path=cwd)
    _app.add_routes(_routes)

    async def start() -> None:
        runner = AppRunner(_app)
        try:
            await runner.setup()
            site = TCPSite(runner, host=host, port=port)
            await site.start()
            await broadcast()
        finally:
            await runner.cleanup()

    return start
