#!/usr/bin/env ts-node

import { hostname } from "os"
import { basename, dirname } from "path"
import { slurp } from "nda/dist/node/fs"
import { big_print } from "nda/dist/node/console"
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
    interval: args.interval,
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
  }

  console.log(
    big_print(
      `Serving -- http://${args.open ? hostname() : "localhost"}:${args.port}`,
    ),
  )
  await serve({
    local: !args.open,
    port: args.port,
    root: "dist",
    title: basename(args.markdown),
    wheel,
  })

  console.error(big_print("EXITED"))
  process.exit(1)
}

main()

