import { createServer } from "http"
import cors from "cors"
import express from "express"
import WebSocket, { Server } from "ws"
import { tiktok } from "nda/dist/isomorphic/prelude"

export type ServerOpts = {
  port: number
  html: () => string
  js: string
  css: string
  wheel: () => AsyncGenerator<undefined, never>
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

export const serve = async ({ port, html, js, css, wheel }: ServerOpts) => {
  const expr = express().use(cors())
  const server = createServer(expr)
  const wss = new Server({ server })

  expr.get(/\.js/, (_, resp) => {
    resp.type("text/javascript")
    resp.send(js)
  })

  expr.get(/\.css$/, (_, resp) => {
    resp.type("text/css")
    resp.send(css)
  })

  expr.get("*", (_, resp) => {
    resp.type("text/html")
    resp.send(html())
  })

  heartbeat(wss)
  server.listen(port)

  for await (const _ of wheel()) {
    wss.clients
  }
}

