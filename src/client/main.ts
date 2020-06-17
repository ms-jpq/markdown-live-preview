import { sleep } from "nda/dist/isomorphic/prelude"
import { $ } from "nda/dist/browser/dom"

type MSG = { hash: string; page: string }

const connect = async function* <T>() {
  const remote = `ws://${location.host}`
  let cb: (_: T) => void = () => {}
  let ws = new WebSocket(remote)

  const provision = () => {
    ws.onmessage = ({ data }) => cb(JSON.parse(data))
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

const update = (page: string) => {
  document.body.innerHTML = page
  const focus = $("#FOCUS")
  if (focus) {
    focus.scrollTo()
  } else {
    console.error("MISSING -- focus el")
  }
}

const main = async () => {
  let sha: string | undefined = undefined
  for await (const { hash, page } of connect<MSG>()) {
    if (sha === hash) {
      return
    }
    sha = hash
    update(page)
  }
}

main()

