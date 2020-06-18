#!/usr/bin/env ts-node

import { hostname } from "os"
import { dirname } from "path"
import { slurp } from "nda/dist/node/fs"
import { JSDOM } from "jsdom"
import { argparse } from "./argparse"
import { watch } from "./watch"
import { render } from "./render"
import { reconciliate } from "./reconciliate"
import { serve } from "./server"

const _base_ = dirname(dirname(__dirname))

const main = async () => {
  process.chdir(_base_)

  const args = await argparse()
  const mon = watch({
    file: args.markdown,
  })

  const wheel = async function*() {
    let prev: JSDOM | undefined = undefined
    for await (const _ of mon) {
      const markdown = await slurp(args.markdown)
      const rendered = render(markdown)
      const { dom, html } = reconciliate(prev, rendered)
      prev = dom
      yield html
    }
    console.error(`File Moved -- ${args.markdown}`)
    process.exit(1)
  }

  console.log(`Serving -- http://${hostname()}:${args.port}`)
  await serve({
    port: args.port,
    root: "dist",
    title: args.markdown,
    wheel,
  })
}

main()

