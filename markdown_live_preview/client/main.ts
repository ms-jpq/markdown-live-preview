import { reconciliate } from "./recon.js"

const CYCLE = 500

const title = document.body.querySelector("#title")!
const root = document.body.querySelector("article")!
const template = document.createElement("template")

const diff_key = "diff"

type API = { title: string; sha: string; follow: boolean }

const api_request = async (): Promise<API> =>
  await (await fetch(`${location.origin}/api/info`)).json()

const ws_connect = async function* <T>() {
  const remote = new URL(`ws://${location.host}/ws`)
  let acc = Array<T>()
  let cb = (): void => undefined
  let ws = new WebSocket(remote)

  const provision = () => {
    ws.onmessage = ({ data }) => {
      acc.push(data)
      cb()
    }
    ws.onclose = async () => {
      await new Promise((resolve) => setTimeout(resolve, CYCLE))
      ws = new WebSocket(remote)
      provision()
    }
  }
  provision()

  while (true) {
    await new Promise<void>((resolve) => {
      cb = resolve
      if (acc.length) {
        resolve()
      }
    })
    const a = acc
    acc = []
    yield* a
  }
}

const update = ((sha) => async (follow: boolean, new_sha: string) => {
  if (new_sha === sha) {
    return
  } else {
    sha = new_sha
  }

  const page = await (await fetch(`${location.origin}/api/markdown`)).text()
  template.innerHTML = page
  template.normalize()
  reconciliate({ root, diff_key, lhs: root, rhs: template.content })

  await new Promise((resolve) => requestAnimationFrame(resolve))
  const marked = document.body.querySelectorAll(`[${diff_key}="${true}"]`)
  const [focus, ..._] = marked

  if (follow && focus) {
    focus.scrollIntoView({
      behavior: "smooth",
      block: "center",
      inline: "center",
    })
  }
})("")

const main = async () => {
  const info = await api_request()
  document.title = info.title
  title.textContent = info.title

  const loop1 = async () => {
    while (true) {
      try {
        for await (const _ of ws_connect<string>()) {
          await update(info.follow, info.sha)
        }
      } catch (err) {
        console.error(err)
      }
    }
  }

  const loop2 = async () => {
    while (true) {
      try {
        const info = await api_request()
        await update(info.follow, info.sha)
      } catch (err) {
        console.error(err)
      }
      await new Promise((resolve) => setTimeout(resolve, CYCLE))
    }
  }

  await Promise.all([loop1(), loop2()])
}

await main()
