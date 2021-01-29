from asyncio import gather
from dataclasses import dataclass
from pathlib import Path
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


_normalize = normalize_path_middleware()


@middleware
async def _index_html(request: Request, handler: _Handler) -> StreamResponse:
    key = "filename"
    match_info = request.match_info
    if key in match_info and match_info[key] == "":
        match_info[key] = "index.html"

    resp = await handler(request)
    return resp


@middleware
async def _cors(request: Request, handler: _Handler) -> StreamResponse:
    resp = await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


_middlewares = (_normalize, _index_html, _cors)
_routes = RouteTableDef()
_websockets: WeakSet[WebSocketResponse] = WeakSet()
_app = Application(middlewares=_middlewares)


def build(
    localhost: bool,
    port: int,
    root: Path,
    payloads: AsyncIterator[Payload],
    updates: AsyncIterator[None],
) -> Callable[[Callable[[], Awaitable[None]]], Awaitable[None]]:
    host = "localhost" if localhost else "0.0.0.0"

    @_routes.get("/api/info")
    async def title_resp(request: BaseRequest) -> StreamResponse:
        payload = await payloads.__anext__()
        json = {"follow": payload.follow, "title": payload.title, "sha": payload.sha}
        return json_response(json)

    @_routes.get("/api/markdown")
    async def markdown_resp(request: BaseRequest) -> StreamResponse:
        payload = await payloads.__anext__()
        return Response(text=payload.markdown, content_type="text/html")

    @_routes.get("/ws")
    async def ws_resp(request: BaseRequest) -> WebSocketResponse:
        ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
        await ws.prepare(request)
        _websockets.add(ws)

        async for msg in ws:
            pass
        return ws

    async def broadcast() -> None:
        async for _ in updates:
            tasks = (ws.send_str("NEW -- from server") for ws in _websockets)
            await gather(*tasks)

    _routes.static(prefix="/", path=JS_ROOT)
    # _routes.static(prefix="/", path=root)
    _app.add_routes(_routes)

    async def start(post: Callable[[], Awaitable[None]]) -> None:
        runner = AppRunner(_app)
        await runner.setup()
        site = TCPSite(runner, host=host, port=port)
        try:
            await site.start()
            await post()
            await broadcast()
        finally:
            await runner.cleanup()

    return start
