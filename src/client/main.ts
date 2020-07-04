import { sleep } from "nda/dist/isomorphic/prelude"
import { sort_by } from "nda/dist/isomorphic/iterator"
import { $, $$, wait_frame } from "nda/dist/browser/dom"

const connect = async function* <T>() {
  const remote = `ws://${location.host}/ws`
  let cb: (_: T) => void = () => {}
  let ws = new WebSocket(remote)

  const provision = () => {
    ws.onmessage = ({ data }) => cb(data)
    ws.onopen = () => {
      ws.send("HELO -- from client")
      ws.onopen = null
    }
    ws.onclose = async () => {
      await sleep(1000)
      ws = new WebSocket(remote)
      provision()
    }
  }
  provision()

  while (true) {
    const next = new Promise<T>((resolve) => (cb = resolve))
    yield next
  }
}

const update = async (page: string) => {
  $("#main")!.innerHTML = page
  await wait_frame()
  const marked = $$(`[diff="true"]`)
  const [focus] = sort_by(
    (m) => Number(m.attributes["depth"].value) * -1,
    marked,
  )

  if (focus) {
    focus.id = "focus"
    focus.scrollIntoView({
      behavior: "smooth",
      block: "center",
      inline: "center",
    })
  }
}

const main = async () => {
  const title = await (await fetch("/api/title")).text()
  document.title = title

  for await (const _ of connect<unknown>()) {
    const page = await (await fetch("/api/markdown")).text()
    await update(page)
  }
}

main()
