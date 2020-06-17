import { sleep } from "nda/dist/isomorphic/prelude"

type MSG = { hash: string; page: string }

const connect = (cb: (_: MSG) => void) => {
  let ws = new WebSocket(`ws://${location.host}`)

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
      ws = new WebSocket(`ws://${location.host}`)
      provision()
    }
  }

  provision()
}

const update = (msg: MSG) => {
  console.log(msg)
}

const main = () => {
  connect(update)
}

main()

