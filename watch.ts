#!/usr/bin/env ts-node

import nodemon, { Settings } from "nodemon"
//@ts-ignore
import parse from "parse-gitignore"
import { slurp } from "nda/dist/node/fs"
import { big_print } from "nda/dist/node/console"

const watch = (settings: Settings) =>
  nodemon(settings)
    .on("start", () => {
      console.log(big_print("STARTED", "$"))
    })
    .on("restart", (files) => {
      console.log(big_print("RESTARTED", "$"))
      console.log(files)
    })

const main = async () => {
  const exts = ["ts", "scss", "html"]
  const git_ignore = await slurp(".gitignore")
  const ignore = parse(git_ignore)
  const exec = "./build.ts && node ./dist/server/main.js"
  watch({
    ext: exts.join(),
    colours: true,
    ignore,
    exec,
  })
}

main()

