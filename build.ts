#!/usr/bin/env ts-node

import { call } from "nda/dist/node/sub_process"

const main = async () => {
  process.chdir(__dirname)

  const [, , ...args] = process.argv
  const watch = args[0] === "watch"

  const c1 = await call({
    cmd: "tsc",
    args: ["-p", "src"],
  })
  if (c1 !== 0 && !watch) {
    process.exit(c1)
  }
  const c2 = await call({
    cmd: "parcel",
    args: ["build", "src/client/index.html"],
  })
  if (c2 !== 0 && !watch) {
    process.exit(c2)
  }
}

main()

