from asyncio import Task, create_task
from dataclasses import dataclass
from typing import AsyncIterator, Awaitable, Callable, List
from weakref import WeakSet

from aiohttp.web import (
    Application,
    AppRunner,
    TCPSite,
    WebSocketResponse,
    get,
    middleware,
)
from aiohttp.web_middlewares import _Handler, normalize_path_middleware
from aiohttp.web_request import BaseRequest, Request
from aiohttp.web_response import StreamResponse

HEARTBEAT_TIME = 1


@dataclass
class Payload:
    title: str
    markdown: str


@dataclass
class Update:
    sha: str


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
    updates: AsyncIterator[Update],
) -> Callable[[], Awaitable[None]]:
    host = "localhost" if localhost else "0.0.0.0"
    websockets: WeakSet[WebSocketResponse] = WeakSet()
    jobs: List[Task] = []

    async def ws_resp(request: BaseRequest) -> WebSocketResponse:
        ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
        await ws.prepare(request)
        websockets.add(ws)

        async for msg in ws:
            print(msg)
            pass

        return ws

    async def broadcast() -> None:
        async for update in updates:
            for ws in websockets:
                ws.send_json(update)

    async def start_jobs(app: Application) -> None:
        b_task = create_task(broadcast())
        jobs.append(b_task)

    async def stop_jobs(app: Application) -> None:
        for job in jobs:
            job.cancel()

    normalize = normalize_path_middleware()
    middlewares = (normalize, cors)
    routes = (get("/ws", ws_resp),)

    app = Application(middlewares=middlewares)
    app.add_routes(routes)
    app.router.add_static(prefix="/", path=root)
    app.on_startup.append(start_jobs)
    app.on_cleanup.append(stop_jobs)

    async def start() -> None:
        runner = AppRunner(app)
        await runner.setup()
        site = TCPSite(runner, host=host, port=port)
        await site.start()

    return start
