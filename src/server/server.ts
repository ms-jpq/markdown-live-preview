import { createServer } from "http"
import cors from "cors"
import express, { static as srv_statis } from "express"
import WebSocket, { Server } from "ws"
import { tiktok } from "nda/dist/isomorphic/prelude"

export type ServerOpts = {
  port: number
  root: string
  wheel: () => AsyncGenerator<string, never>
}

const heartbeat = (wss: Server) => {
  const keepalive = (ws: WebSocket) => {
    ws["is_alive"] = true
    ws.on("pong", () => (ws["is_alive"] = true))
  }

  const pluse = (ws: WebSocket) => {
    if (!ws["is_alive"]) {
      ws.terminate()
    } else {
      ws["is_alive"] = false
      ws.ping()
    }
  }

  wss.on("connection", keepalive)
  ;(async () => {
    for await (const _ of tiktok(1000 * 5)) {
      wss.clients.forEach(pluse)
    }
  })()
}

export const serve = async ({ port, root, wheel }: ServerOpts) => {
  const expr = express().use(cors())
  const server = createServer(expr)
  const wss = new Server({ server })

  heartbeat(wss)
  expr.use(srv_statis(root))
  server.listen(port)

  let page = ""
  const comm = (ws: WebSocket) => {
    ws.send(page)
  }
  for await (const html of wheel()) {
    page = html
    wss.clients.forEach(comm)
  }
}

