#!/usr/bin/env ts-node

import { call } from "nda/dist/node/sub_process"

const main = async () => {
  process.chdir(__dirname)
  await call({
    cmd: "tsc",
    args: ["-p", "src"],
  })
  await call({
    cmd: "parcel",
    args: ["build", "src/client/index.html"],
  })
}

main()

