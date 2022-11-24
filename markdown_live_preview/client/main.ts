const CYCLE = 500

const title = document.body.querySelector("#title")!
const article = document.body.querySelector("article")!
const template = document.createElement("template")

const diff_key = "diff"

type API = { title: string; sha: string; follow: boolean }

const long_zip = function* <
  T extends Iterable<unknown>[],
  R extends {
    readonly [K in keyof T]: T[K] extends Iterable<infer V>
      ? V | undefined
      : never
  },
>(...iterables: T): IterableIterator<R> {
  const iterators = iterables.map((i) => i[Symbol.iterator]())
  while (true) {
    const acc = iterators.map((i) => i.next())
    if (acc.every((r) => r.done ?? false)) {
      break
    } else {
      yield acc.map((r) => r.value) as unknown as R
    }
  }
}

const api_request = async (): Promise<API> =>
  await (await fetch(`${location.origin}/api/info`)).json()

const ws_connect = async function* <T>() {
  const remote = `ws://${location.host}/ws`
  let cb: (_: T) => void = () => {}
  let ws = new WebSocket(remote)

  const provision = () => {
    ws.onmessage = ({ data }) => cb(data)
    ws.onclose = async () => {
      await new Promise((resolve) => setTimeout(resolve, CYCLE))
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

const reconciliate = (lhs: Node, rhs: Node) => {
  let diff = false

  for (const [l, r] of long_zip([...lhs.childNodes], [...rhs.childNodes])) {
    if (l && !r) {
      diff = true
      l.remove()
    } else if (!l && r) {
      diff = true
      lhs.appendChild(r)
    } else if (l instanceof Element && r instanceof Element) {
      if (l.tagName !== r.tagName) {
        l.replaceWith(r)
      } else {
        const attrs = new Map(
          (function* () {
            for (const { name, value } of r.attributes) {
              yield [name, value]
            }
          })(),
        )

        for (const { name } of l.attributes) {
          if (!attrs.has(name)) {
            if (name !== diff_key) {
              diff = true
            }
            l.removeAttribute(name)
          }
        }

        for (const [name, value] of attrs) {
          if (l.getAttribute(name) !== value) {
            diff = true
            l.setAttribute(name, value)
          }
        }

        reconciliate(l, r)
      }
    } else {
      if (l!.nodeType !== r!.nodeType) {
        diff = true
        lhs.replaceChild(r!, l!)
      } else if (l!.nodeValue !== r!.nodeValue) {
        diff = true
        l!.nodeValue = r!.nodeValue
      }
    }
  }

  if (diff && lhs instanceof Element && lhs !== article) {
    lhs.setAttribute(diff_key, String(true))
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
  reconciliate(article, template.content)

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

await update(false, "<>")
await main()
