#!/usr/bin/env ts-node

import { argparse } from "./argparse"
import { watch } from "./watch"

const main = async () => {
  const args = await argparse()
  const mon = watch({
    file: args.markdown,
    delay: args.delay,
    interval: args.interval,
  })
  for await (const _ of mon) {
    console.log(new Date())
  }
}

main()

