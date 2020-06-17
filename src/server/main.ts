#!/usr/bin/env ts-node

import { hostname } from "os"
import { join } from "path"
import { slurp } from "nda/dist/node/fs"
import { argparse } from "./argparse"
import { watch } from "./watch"
import { render } from "./render"
import { serve } from "./server"
import { _base_ } from "./consts"

const main = async () => {
  const args = await argparse()
  const mon = watch({
    file: args.markdown,
    delay: args.delay,
    interval: args.interval,
  })

  let page = ""

  ;(async () => {
    for await (const _ of mon) {
      const markdown = await slurp(args.markdown)
      const html = render(markdown)
      page = html
    }
    console.error(`File Moved -- ${args.markdown}`)
    process.exit(1)
  })()

  await (async () => {
    console.log(`Serving -- http://${hostname()}:${args.port}`)
    const client_home = join(_base_, "dist", "client")
    const [js, css] = await Promise.all([
      slurp(join(client_home, "main.js")),
      slurp(join(client_home, "main.js")),
    ])
    await serve({
      port: args.port,
      html: () => page,
      js,
      css,
    })
  })()
}

main()

