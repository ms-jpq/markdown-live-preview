from asyncio import gather
from dataclasses import dataclass
from pathlib import Path, PurePath, PurePosixPath
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
    markdown: str


def build(
    localhost: bool, port: int, cwd: PurePath, gen: AsyncIterator[Payload]
) -> Callable[[], Awaitable[None]]:
    host = "localhost" if localhost else ""
    payload = Payload(follow=False, title="", sha="", markdown="")

    @middleware
    async def cors(request: Request, handler: Handler) -> StreamResponse:
        resp = await handler(request)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    @middleware
    async def local_files(request: Request, handler: Handler) -> StreamResponse:
        try:
            rel = PurePosixPath(request.path).relative_to("/cwd")
            path = Path(cwd / rel).resolve(strict=True)
        except (ValueError, OSError):
            return await handler(request)
        else:
            if path.relative_to(cwd):
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

    @routes.route("*", "/")
    async def index_resp(request: BaseRequest) -> FileResponse:
        return FileResponse(JS_ROOT / "index.html")

    @routes.get("/ws")
    async def ws_resp(request: BaseRequest) -> WebSocketResponse:
        ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
        await ws.prepare(request)
        websockets.add(ws)
        async for _ in ws:
            pass
        return ws

    @routes.get("/api/info")
    async def meta_resp(request: BaseRequest) -> StreamResponse:
        json = {"follow": payload.follow, "title": payload.title, "sha": payload.sha}
        return json_response(json)

    @routes.get("/api/markdown")
    async def markdown_resp(request: BaseRequest) -> StreamResponse:
        return Response(text=payload.markdown, content_type="text/html")

    async def broadcast() -> None:
        nonlocal payload
        async for p in gen:
            payload = p
            tasks = (ws.send_str("") for ws in websockets)
            await gather(*tasks)

    routes.static(prefix="/", path=JS_ROOT)
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
