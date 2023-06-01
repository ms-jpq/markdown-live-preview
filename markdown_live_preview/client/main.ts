import mermaid from "mermaid"
import { reconciliate } from "./recon.js"

import { sched } from "./sched.js"

const CYCLE = 500

const title = document.body.querySelector("#title")!
const root = document.body.querySelector("article")!
const template = document.createElement("template")

const diff_key = "diff"
const mermaid_class = "mermaid"

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

const update = (
  (sha) =>
  async (follow: boolean, new_sha: string, post: () => Promise<void>) => {
    if (new_sha === sha) {
      console.debug("no change")
      return
    } else {
      sha = new_sha
    }

    const page = await (await fetch(`${location.origin}/api/markdown`)).text()
    template.innerHTML = page
    template.normalize()
    reconciliate({
      root,
      diff_key,
      mermaid_class,
      lhs: root,
      rhs: template.content,
    })
    await post()

    const marked = root.querySelectorAll(`[${diff_key}="${true}"]`)
    const [focus, ..._] = marked

    if (follow && focus) {
      focus.scrollIntoView({
        behavior: "smooth",
        block: "center",
        inline: "center",
      })
    }
  }
)("")

const id = (
  (id) => () =>
    id++
)(0)

const main = async () => {
  mermaid.initialize({ startOnLoad: false })

  const info = await api_request()
  document.title = info.title
  title.textContent = info.title

  const scheduler = sched(CYCLE)
  const render = async () => {
    const nodes = [...root.querySelectorAll<HTMLElement>(".mermaid")]
    await mermaid.run({ nodes })
  }

  const loop0 = (async function* () {
    while (true) {
      const [follow, sha]: [boolean, string] = yield
      try {
        await update(follow, sha, render)
      } finally {
        console.debug("rendered")
      }
    }
  })()

  const loop1 = async () => {
    while (true) {
      try {
        for await (const _ of ws_connect<string>()) {
          scheduler.reset()
          console.debug("ws")
          await loop0.next([info.follow, info.sha])
        }
      } catch (err) {
        console.error(err)
      }
    }
  }

  const loop2 = async () => {
    for await (const _ of scheduler) {
      try {
        console.debug("poll")
        const info = await api_request()
        await loop0.next([info.follow, info.sha])
      } catch (err) {
        console.error(err)
      }
    }
  }

  await Promise.all([loop1(), loop2()])
}

await main()
