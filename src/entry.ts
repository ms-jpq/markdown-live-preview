#!/usr/bin/env ts-node

import { argparse } from "./argparse"
import { watch } from "./watch"

const main = async () => {
  const args = await argparse()
  for await (const _ of watch(args.markdown)) {
    console.log("NEXT")
  }
}

main()

