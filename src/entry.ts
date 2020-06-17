#!/usr/bin/env ts-node

import { Command } from "commander"
import { slurp } from "nda/dist/node/fs"
import { dirname, join } from "path"

const main = async () => {
  const prog = new Command()
  const pkg_data = await slurp(join(dirname(__dirname), "package.json"))
  const pkg_info = JSON.parse(pkg_data)
  const ver = pkg_info["version"]
  prog.version(ver)
  prog.parse(process.argv)
}

main()

