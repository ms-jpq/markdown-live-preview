#!/usr/bin/env ts-node

import { slurp } from "nda/dist/node/fs"
import { argparse } from "./argparse"
import { watch } from "./watch"
import { render } from "./render"

const main = async () => {
  const args = await argparse()
  const mon = watch({
    file: args.markdown,
    delay: args.delay,
    interval: args.interval,
  })

  const run = (async () => {
    for await (const _ of mon) {
      const markdown = await slurp(args.markdown)
      const html = render(markdown)
    }
  })()

  await run
}

main()

