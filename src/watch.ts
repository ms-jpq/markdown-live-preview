import { watch as fs_watch } from "chokidar"

export type WatchOpts = {
  file: string
  delay: number
}

export const watch = async function* ({ file, delay }: WatchOpts) {
  let cb = (_: string) => {}
  const mon = fs_watch(file, { interval: delay })
  mon.on("all", (event) => cb(event))
  while (true) {
    const event = await new Promise<string>((resolve) => (cb = resolve))
    if (event === "unlink") {
      break
    }
    yield
  }
}

