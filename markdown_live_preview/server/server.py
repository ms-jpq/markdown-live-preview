from asyncio import gather
from dataclasses import dataclass
from datetime import datetime
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

from .da import anext

HEARTBEAT_TIME = 1


@dataclass
class Payload:
    follow: bool
    title: str
    sha: str
    markdown: str


normalize = normalize_path_middleware()


@middleware
async def index_html(request: Request, handler: _Handler) -> StreamResponse:
    key = "filename"
    match_info = request.match_info
    if key in match_info and match_info[key] == "":
        match_info[key] = "index.html"

    resp = await handler(request)
    return resp


@middleware
async def cors(request: Request, handler: _Handler) -> StreamResponse:
    resp = await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


def build(
    localhost: bool,
    port: int,
    root: str,
    payloads: AsyncIterator[Payload],
    updates: AsyncIterator[None],
) -> Callable[[Callable[[], Awaitable[None]]], Awaitable[None]]:
    host = "localhost" if localhost else "0.0.0.0"
    websockets: WeakSet[WebSocketResponse] = WeakSet()

    routes = RouteTableDef()

    @routes.get("/api/info")
    async def title_resp(request: BaseRequest) -> StreamResponse:
        payload = await anext(payloads)
        json = {"follow": payload.follow, "title": payload.title, "sha": payload.sha}
        return json_response(json)

    @routes.get("/api/markdown")
    async def markdown_resp(request: BaseRequest) -> StreamResponse:
        payload = await anext(payloads)
        return Response(text=payload.markdown, content_type="text/html")

    @routes.get("/ws")
    async def ws_resp(request: BaseRequest) -> WebSocketResponse:
        ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
        await ws.prepare(request)
        websockets.add(ws)

        async for msg in ws:
            pass
        return ws

    async def broadcast() -> None:
        async for _ in updates:
            tasks = (ws.send_str("NEW -- from server") for ws in websockets)
            time = datetime.now().strftime("%H:%M:%S")
            await gather(*tasks)
            print(f"⏰ - {time}")

    routes.static(prefix="/", path=root)

    middlewares = (normalize, index_html, cors)
    app = Application(middlewares=middlewares)
    app.add_routes(routes)

    async def start(post: Callable[[], Awaitable[None]]) -> None:
        runner = AppRunner(app)
        await runner.setup()
        site = TCPSite(runner, host=host, port=port)
        try:
            await site.start()
            await post()
            await broadcast()
        finally:
            await runner.cleanup()

    return start
