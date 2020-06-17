import nodemon from "nodemon"

export type WatchOpts = {
  file: string
  delay: number
}

export const watch = async function* ({ file, delay }: WatchOpts) {
  const mon = nodemon({
    exec: "sh -c exit",
    watch: [file],
    delay,
  })

  await new Promise<void>((resolve) => mon.once("start", resolve))
  yield
  while (true) {
    await new Promise<void>((resolve) => mon.once("restart", resolve))
    yield
  }
}

