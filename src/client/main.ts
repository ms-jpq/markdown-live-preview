import { sleep } from "nda/dist/isomorphic/prelude"
import { $, wait_frame } from "nda/dist/browser/dom"
import { _focus_ } from "../consts"

type MSG = { hash: string }

const connect = async function* <T>() {
  const remote = `ws://${location.host}`
  let cb: (_: T) => void = () => {}
  let ws = new WebSocket(remote)

  const provision = () => {
    ws.onmessage = ({ data }) => cb(JSON.parse(data))
    ws.onopen = () => {
      ws.send(JSON.stringify({}))
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
  const focus = $(`#${_focus_}`)
  focus?.scrollIntoView({
    behavior: "smooth",
    block: "nearest",
    inline: "center",
  })
}

const main = async () => {
  const title = await (await fetch("/api/title")).text()
  document.title = title

  let sha: string | undefined = undefined
  for await (const { hash } of connect<MSG>()) {
    if (sha === hash) {
      continue
    }
    sha = hash
    const page = await (await fetch("/api/markdown")).text()
    await update(page)
  }
}

main()

