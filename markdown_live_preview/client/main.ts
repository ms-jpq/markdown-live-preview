import mermaid from "mermaid"
import { diff_key, mermaid_class, reconciliate } from "./recon.js"

const CYCLE = 500

const head = document.body.querySelector("#title")!
const root = document.body.querySelector("article")!
const template = document.createElement("template")

type API = { title: string; sha: string; follow: boolean }

const api_request = async (): Promise<API> =>
  await (await fetch(`${location.origin}/api/info`)).json()

const ws_connect = async function* () {
  const remote = new URL(`ws://${location.host}/ws`)
  let flag = false
  let cb = (): void => undefined
  let ws = new WebSocket(remote)

  const provision = () => {
    ws.onmessage = () => {
      flag = true
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
    try {
      if (!flag) {
        await new Promise<void>((resolve) => (cb = resolve))
      }
      yield
    } catch (e) {
      console.error(e)
      ws.close()
    }
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
          yield (async () => {
            try {
              const { svg, bindFunctions } = await mermaid.render(id, text)
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

  template.innerHTML = page
  const figs = document.querySelectorAll<HTMLElement>(`figure.${mermaid_class}`)
  for (const fig of figs) {
    fig.firstElementChild?.removeAttribute("id")
  }
  await render(template.content)
  template.normalize()
  for (const fig of figs) {
    fig.firstElementChild?.remove()
  }

  reconciliate({
    root,
    lhs: root,
    rhs: template.content,
  })

  const marked = root.querySelectorAll(`[${diff_key}="${true}"]`)
  const [touched, ..._] = marked

  if (follow && touched) {
    new IntersectionObserver((entries, obs) => {
      obs.disconnect()
      const visible = entries.some(({ isIntersecting }) => isIntersecting)
      if (!visible) {
        touched.scrollIntoView({
          behavior: "smooth",
          block: "center",
          inline: "center",
        })
      }
    }).observe(touched)
  }
})("")

const main = async () => {
  mermaid.initialize({ startOnLoad: false })

  const gen = ws_connect()
  for await (const _ of gen) {
    try {
      const { title, follow, sha } = await api_request()
      document.title ||= title
      head.textContent ||= title
      await update(follow, sha)
    } catch (e) {
      console.error(e)
      await new Promise((resolve) => setTimeout(resolve, CYCLE))
    }
  }
}

await main()
