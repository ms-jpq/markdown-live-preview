#!/usr/bin/env ts-node

import { hostname } from "os"
import { slurp } from "nda/dist/node/fs"
import { argparse } from "./argparse"
import { watch } from "./watch"
import { render } from "./render"
import { serve } from "./server"


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
      console.log(`Updated -- ${new Date()}`)
    }
    console.error(`File Moved -- ${args.markdown}`)
    process.exit(1)
  })()

  await (async () => {
    console.log(`Serving -- http://${hostname()}:${args.port}`)
    await serve({
      port: args.port,
      html: () => page,
      js: "js-stub",
      css: "css-stub",
    })
  })()
}

main()

