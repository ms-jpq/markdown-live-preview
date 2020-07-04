from asyncio import CancelledError, Task, create_task, gather, sleep
from dataclasses import dataclass
from typing import AsyncIterator, Awaitable, Callable, List
from weakref import WeakSet

from aiohttp.web import (
    Application,
    AppRunner,
    Response,
    RouteTableDef,
    TCPSite,
    WebSocketResponse,
    middleware,
)
from aiohttp.web_middlewares import _Handler, normalize_path_middleware
from aiohttp.web_request import BaseRequest, Request
from aiohttp.web_response import StreamResponse

from da import anext

HEARTBEAT_TIME = 1


@dataclass
class Payload:
    title: str
    markdown: str


async def run_forever() -> None:
    while True:
        await sleep(420)


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
) -> Callable[[], Awaitable[None]]:
    jobs: List[Task] = []
    host = "localhost" if localhost else "0.0.0.0"
    websockets: WeakSet[WebSocketResponse] = WeakSet()
    forever = create_task(run_forever())

    routes = RouteTableDef()

    @routes.get("/api/title")
    async def title_resp(request: BaseRequest) -> StreamResponse:
        payload = await anext(payloads)
        return Response(text=payload.title)

    @routes.get("/api/markdown")
    async def markdown_resp(request: BaseRequest) -> StreamResponse:
        payload = await anext(payloads)
        return Response(text=payload.markdown)

    @routes.get("/ws")
    async def ws_resp(request: BaseRequest) -> WebSocketResponse:
        ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
        await ws.prepare(request)
        websockets.add(ws)

        await ws.send_str("HELO -- from server")
        async for msg in ws:
            pass

        return ws

    async def broadcast(app: Application) -> None:
        async for _ in updates:
            tasks = (ws.send_str("NEW -- from server") for ws in websockets)
            await gather(*tasks)

        await app.shutdown()
        await app.cleanup()
        forever.cancel()

    async def start_jobs(app: Application) -> None:
        b_task = create_task(broadcast(app))
        jobs.append(b_task)

    routes.static(prefix="/", path=root)

    middlewares = (normalize, index_html, cors)
    app = Application(middlewares=middlewares)
    app.on_startup.append(start_jobs)
    app.add_routes(routes)

    async def start() -> None:
        runner = AppRunner(app)
        await runner.setup()
        site = TCPSite(runner, host=host, port=port)
        try:
            await site.start()
            try:
                await forever
            except CancelledError:
                pass
        finally:
            await runner.cleanup()

    return start
