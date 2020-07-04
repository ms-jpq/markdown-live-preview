from dataclasses import dataclass
from typing import AsyncIterator

from aiohttp.web import (
    Application,
    AppRunner,
    TCPSite,
    WebSocketResponse,
    WSMsgType,
    get,
    middleware,
)
from aiohttp.web_middlewares import _Handler, normalize_path_middleware
from aiohttp.web_request import BaseRequest, Request
from aiohttp.web_response import StreamResponse

HEARTBEAT_TIME = 1


@dataclass
class Payload:
    markdown: str


@middleware
async def cors(request: Request, handler: _Handler) -> StreamResponse:
    resp = await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


async def serve(
    localhost: bool, port: int, root: str, gen: AsyncIterator[Payload]
) -> None:
    host = "localhost" if localhost else "0.0.0.0"

    async def ws_resp(request: BaseRequest) -> WebSocketResponse:
        ws = WebSocketResponse(heartbeat=HEARTBEAT_TIME)
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == WSMsgType.text:
                await ws.send_json({})
            elif msg.type == WSMsgType.close:
                break

        return ws

    normalize = normalize_path_middleware()
    middlewares = (normalize, cors)
    routes = (get("/ws", ws_resp),)

    app = Application(middlewares=middlewares)
    app.add_routes(routes)
    app.router.add_static(prefix="/", path=root)

    runner = AppRunner(app)
    await runner.setup()
    site = TCPSite(runner, host=host, port=port)
    await site.start()
