import mermaid from "mermaid"
import { reconciliate } from "./recon.js"

const CYCLE = 500

const head = document.body.querySelector("#title")!
const root = document.body.querySelector("article")!
const template = document.createElement("template")

const diff_key = "diff"
const mermaid_class = "language-mermaid"

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

  try {
    while (true) {
      if (!acc.length) {
        await new Promise<void>((resolve) => (cb = resolve))
      }
      const a = acc
      acc = []
      yield* a
    }
  } finally {
    ws.close()
  }
}

const render = async (el: HTMLElement) => {
  const nodes = el.querySelectorAll<HTMLElement>(`.${mermaid_class} code`)
  await Promise.all(
    (function* () {
      for (const node of nodes) {
        if (!node.firstElementChild) {
          node.removeAttribute("data-processed")
        }
        yield (async () => {
          try {
            await mermaid.run({ nodes: [node] })
          } catch (e) {
            const { message } = e as Error
            const el = document.createElement("pre")
            el.append(new Text(message))
            node.nextElementSibling?.append(el)
          }
        })()
      }
    })(),
  )
}

const update = ((sha) => async (follow: boolean, new_sha: string) => {
  if (new_sha === sha) {
    return
  } else {
    sha = new_sha
  }

  const page = await (await fetch(`${location.origin}/api/markdown`)).text()
  template.innerHTML = page
  for (const el of template.content.querySelectorAll<HTMLElement>(
    `.${mermaid_class}`,
  )) {
    el.dataset.mermaid = el.textContent ?? ""
  }
  template.normalize()

  reconciliate({
    root,
    diff_key,
    mermaid_class,
    lhs: root,
    rhs: template.content,
  })
  await render(root)

  const marked = root.querySelectorAll(`[${diff_key}="${true}"]`)
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
  mermaid.initialize({ startOnLoad: false })

  const gen = ws_connect<string>()

  do {
    try {
      const { title, follow, sha } = await api_request()
      document.title ||= title
      head.textContent ||= title
      await update(follow, sha)
      await Promise.race([
        gen.next(),
        new Promise((resolve) => setTimeout(resolve, CYCLE)),
      ])
    } catch (e) {
      console.error(e)
      await new Promise((resolve) => setTimeout(resolve, CYCLE))
    }
  } while (true)
}

await main()
