from dataclasses import dataclass
from typing import AsyncIterator

from aiohttp.web import (
    Application,
    WebSocketResponse,
    WSMsgType,
    get,
    middleware,
    run_app,
)
from aiohttp.web_middlewares import _Handler, normalize_path_middleware
from aiohttp.web_request import BaseRequest
from aiohttp.web_response import StreamResponse

HEARTBEAT_TIME = 1


@dataclass
class Payload:
    markdown: str


@middleware
async def cors(request: BaseRequest, handler: _Handler) -> StreamResponse:
    resp = await handler(request)
    resp.headers()["Access-Control-Allow-Origin"] = "*"
    return resp


async def server(port: int, root: str, gen: AsyncIterator[Payload]) -> None:
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

    run_app(app)
