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
  const [, , ...args] = process.argv

  const exts = ["ts", "scss", "html"]
  const git_ignore = await slurp(".gitignore")
  const ignore = parse(git_ignore)

  const escaped = args.map((a) => `'${a}'`).join(" ")
  const exec = `./build.ts 'watch' && node ./dist/server/main.js ${escaped}`

  watch({
    ext: exts.join(),
    colours: true,
    ignore,
    exec,
  })
}

main()

