import {} from "nda/dist/isomorphic/prelude"

const main = () => {
  const ws = new WebSocket(location.host)

  ws.onmessage = (msg) => {
    console.log(msg)
  }
}

main()

