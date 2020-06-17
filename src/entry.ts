#!/usr/bin/env ts-node

import { argparse } from "./argparse"

const main = async () => {
  const args = await argparse()
  console.log(args)
}

main()

