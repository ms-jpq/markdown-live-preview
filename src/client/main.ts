import { sleep } from "nda/dist/isomorphic/prelude"

type MSG = { hash: string; page: string }

const connect = async function* () {
  const remote = `ws://${location.host}`
  let cb: (_: MSG) => void = () => {}
  let ws = new WebSocket(remote)

  const provision = () => {
    ws.onmessage = ({ data }) => {
      const msg = JSON.parse(data)
      cb(msg)
    }
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
    const next = new Promise<MSG>((resolve) => (cb = resolve))
    yield next
  }
}

const main = async () => {
  for await (const msg of connect()) {
    console.log(msg)
  }
}

main()

