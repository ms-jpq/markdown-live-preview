import cors from "cors"
import express from "express"

export type ServerOpts = {
  port: number
  html: () => string
  js: string
  css: string
}

export const serve = async ({ port, html, js, css }: ServerOpts) => {
  const srv = express().use(cors())

  srv.get(/\.js/, (_, resp) => {
    resp.type("text/javascript")
    resp.send(js)
  })

  srv.get(/\.css$/, (_, resp) => {
    resp.type("text/css")
    resp.send(css)
  })

  srv.get("*", (_, resp) => {
    resp.type("text/html")
    resp.send(html())
  })

  srv.listen(port)
}

