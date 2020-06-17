#!/usr/bin/env ts-node

import { call } from "nda/dist/node/sub_process"

const main = async () => {
  await call({
    cmd: "npm",
    args: ["run", "build"],
  })
}

main()

