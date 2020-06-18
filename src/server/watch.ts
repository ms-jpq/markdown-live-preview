import { promises as fs } from "fs"
import { tiktok } from "nda/dist/isomorphic/prelude"

export type WatchOpts = {
  file: string
  interval: number
}

export const watch = async function*({ file, interval }: WatchOpts) {
  const stat = await fs.stat(file)
  let mtime = stat.mtimeMs
  let err = 0
  for await (const _ of tiktok(interval)) {
    try {
      const curr = (await fs.stat(file)).mtimeMs
      if (mtime !== curr) {
        yield
      }
      mtime = curr
      err = 0
    } catch {
      err += 1
      if (err >= 5) {
        break
      }
    }
  }
}

