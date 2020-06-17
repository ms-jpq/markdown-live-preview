#!/usr/bin/env ts-node

import { argparse } from "./argparse"
import { watch } from "./watch"

const main = async () => {
  const args = await argparse()
  for await (const _ of watch({ file: args.markdown, delay: args.delay })) {
    console.log("NEXT")
  }
}

main()

