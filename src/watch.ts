import { watch as fs_watch } from "fs"

export const watch = async function* (file: string) {
  let watcher = fs_watch(file)
  while (true) {
    const { event, filename } = await new Promise<{
      event: string
      filename: string | Buffer
    }>((resolve) =>
      watcher.once("change", (event, filename) => resolve({ event, filename })),
    )
    if (event === "change") {
      yield
    } else if (event === "rename") {
      watcher = fs_watch(filename)
    } else {
      throw new Error(`Unanticipated Watch Event -- ${event}`)
    }
  }
}

