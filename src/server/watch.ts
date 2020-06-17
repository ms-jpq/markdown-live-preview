import { watch as fs_watch } from "chokidar"
import { sleep } from "nda/dist/isomorphic/prelude"

export type WatchOpts = {
  file: string
  interval: number
  delay: number
}

export const watch = async function* ({ file, delay, interval }: WatchOpts) {
  let cb = (_: string) => {}

  const mon = fs_watch(file, { interval: delay })
  mon.on("all", (event) => cb(event))

  while (true) {
    const e1 = (async () => {
      await sleep(interval)
      return "poll"
    })()
    const e2 = new Promise<string>((resolve) => (cb = resolve))

    const event = await Promise.race([e1, e2])
    if (event === "unlink") {
      break
    }
    yield
  }
}

