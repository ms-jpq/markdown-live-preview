import { createServer } from "http"
import { createHash } from "crypto"
import express, { static as srv_statis } from "express"
import WebSocket, { Server } from "ws"
import { tiktok } from "nda/dist/isomorphic/prelude"

export type ServerOpts = {
  port: number
  root: string
  title: string
  wheel: () => AsyncGenerator<string>
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

export const serve = async ({ port, root, title, wheel }: ServerOpts) => {
  const expr = express()
  const server = createServer(expr)
  const wss = new Server({ server })

  let page = ""

  expr.use((_, resp, next) => {
    resp.header("Access-Control-Allow-Origin", "*")
    next()
  })

  expr.get("/api/title", (_, resp) => {
    resp.type("text")
    resp.send(title)
  })

  expr.get("/api/markdown", (_, resp) => {
    resp.type("text/html")
    resp.send(page)
  })

  const comm = (ws: WebSocket) => {
    if (ws.readyState !== WebSocket.OPEN) {
      return
    }
    const sha = createHash("sha1")
    sha.update(page)
    const hash = sha.digest("hex")
    const msg = { hash }
    ws.send(JSON.stringify(msg))
  }
  wss.on("connection", (ws) => comm(ws))

  heartbeat(wss)
  expr.use(srv_statis(root))
  server.listen(port)

  for await (const html of wheel()) {
    page = html
    wss.clients.forEach(comm)
  }
}

