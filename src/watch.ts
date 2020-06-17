import { watch as fs_watch } from "chokidar"

export type WatchOpts = {
  file: string
  delay: number
}

export const watch = async function* ({ file, delay }: WatchOpts) {
  let cb = () => {}
  const mon = fs_watch(file, { interval: delay })
  mon.on("all", () => cb())
  while (true) {
    await new Promise<void>((resolve) => (cb = resolve))
    yield
  }
}

