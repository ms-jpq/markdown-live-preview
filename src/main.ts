#!/usr/bin/env node

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

  ;(async () => {
    for await (const _ of mon) {
      const markdown = await slurp(args.markdown)
      const html = render(markdown)
    }
    console.error(`File Moved -- ${args.markdown}`)
    process.exit(1)
  })()
  await serve({
    port: args.port,
    html: {},
    js: {},
    css: {},
  })
}

main()

