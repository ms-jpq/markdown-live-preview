import { promises as fs } from "fs"
import { Command } from "commander"
import { isfile, slurp } from "nda/dist/node/fs"
import { big_print } from "nda/dist/node/console"

export type Arguments = {
  markdown: string
  open: boolean
  port: number
  interval: number
}

export const argparse = async (): Promise<Arguments> => {
  const prog = new Command()
  prog.storeOptionsAsProperties(false)

  const pkg_data = await slurp("package.json")
  const pkg_info = JSON.parse(pkg_data)
  prog.name(pkg_info["name"])
  prog.version(pkg_info["version"])

  prog.arguments("<markdown>")
  prog.option("-p, --port <port>", "PORT", Number, 8080)
  prog.option("-o, --open", "OPEN", false)
  prog.option("-i, --interval, <interval>", "INTERVAL", Number, 0.1)

  await prog.parseAsync(process.argv)
  if (prog.args.length != 1) {
    console.error(prog.helpInformation())
    process.exit(1)
  }
  const [path] = prog.args
  const args = prog.opts()

  if (!(await isfile(path))) {
    console.error(big_print(`Cannot Access -- ${path}`))
    process.exit(1)
  }
  const markdown = await fs.realpath(path)

  return {
    ...args,
    markdown,
    interval: args.interval * 1000,
  } as Arguments
}

