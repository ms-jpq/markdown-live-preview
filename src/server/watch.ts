import { watch as fs_watch } from "chokidar"

export type WatchOpts = {
  file: string
  interval: number
}

export const watch = async function*({ file, interval }: WatchOpts) {
  let cb = (_: string) => {}

  const mon = fs_watch(file, {
    disableGlobbing: true,
    followSymlinks: true,
    usePolling: true,
    awaitWriteFinish: true,
    interval,
  })
  mon.on("all", (event) => cb(event))

  while (true) {
    const event = await new Promise<string>((resolve) => (cb = resolve))
    if (event === "unlink") {
      await mon.close()
      break
    }
    yield event
  }
}

