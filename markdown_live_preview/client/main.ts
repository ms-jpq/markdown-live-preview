import mermaid from "mermaid"
import { diff_key, mermaid_class, reconciliate } from "./recon.js"

const CYCLE = 500

const head = document.body.querySelector("#title")!
const root = document.body.querySelector("article")!
const template = document.createElement("template")

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

const render = async (root: DocumentFragment) => {
  const nodes = root.querySelectorAll<HTMLElement>(`.${mermaid_class} code`)
  await Promise.all(
    (function* () {
      let i = 0
      for (const node of nodes) {
        const text = node.textContent
        if (text) {
          const id = `${mermaid_class}-svg-${i++}`
          const parent =
            document.querySelector(`#${id}`)?.parentElement ?? undefined
          yield (async () => {
            try {
              const { svg, bindFunctions } = await mermaid.render(
                id,
                text,
                parent,
              )
              const figure = document.createElement("figure")
              figure.classList.add(mermaid_class)
              figure.dataset.mermaid = text
              figure.innerHTML = svg
              bindFunctions?.(figure)
              node.replaceWith(figure)
            } catch (e) {
              const { message } = e as Error
              const el = document.createElement("pre")
              el.append(new Text(message))
              node.parentElement?.insertBefore(el, node)
            }
          })()
        }
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
  const [sx, sy] = [globalThis.scrollX, globalThis.scrollY]

  template.innerHTML = page
  await render(template.content)
  template.normalize()

  reconciliate({
    root,
    lhs: root,
    rhs: template.content,
  })

  const marked = root.querySelectorAll(`[${diff_key}="${true}"]`)
  const [touched, ..._] = marked
  const touched_mermaid =
    touched?.parentElement?.classList.contains(mermaid_class)
  const focus = touched_mermaid ? touched?.parentElement : touched

  if (follow && focus) {
    new IntersectionObserver((entries, obs) => {
      obs.disconnect()
      const visible = entries.some(({ isIntersecting }) => isIntersecting)
      if (!visible) {
        focus.scrollIntoView({
          behavior: "smooth",
          block: "center",
          inline: "center",
        })
      } else if (touched_mermaid) {
        globalThis.scrollTo(sx, sy)
      }
    }).observe(focus)
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
