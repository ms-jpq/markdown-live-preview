export const diff_key = "diff"
export const mermaid_class = "language-mermaid"

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

export const reconciliate = ({
  root,
  lhs,
  rhs,
}: {
  root: Node
  lhs: Node
  rhs: Node
}) => {
  let diff = false
  for (const [l, r] of long_zip([...lhs.childNodes], [...rhs.childNodes])) {
    if (l && !r) {
      diff = true
      l.remove()
    } else if (!l && r) {
      if (
        !(
          lhs instanceof HTMLElement &&
          rhs instanceof HTMLElement &&
          lhs.classList.contains(mermaid_class) &&
          rhs.classList.contains(mermaid_class) &&
          lhs.dataset.mermaid === rhs.dataset.mermaid
        )
      ) {
        diff = true
      }
      lhs.appendChild(r)
    } else if (l instanceof HTMLElement && r instanceof HTMLElement) {
      if (l.tagName !== r.tagName) {
        l.replaceWith(r)
      } else {
        for (const { name, value } of l.attributes) {
          if (r.getAttribute(name) !== value) {
            if (name !== diff_key) {
              diff = true
            }
            l.removeAttribute(name)
          }
        }

        for (const { name, value } of r.attributes) {
          if (l.getAttribute(name) !== value) {
            diff = true
            l.setAttribute(name, value)
          }
        }

        reconciliate({ root, lhs: l, rhs: r })
      }
    } else if (l!.nodeType !== r!.nodeType) {
      diff = true
      lhs.replaceChild(r!, l!)
    } else if (l!.nodeValue !== r!.nodeValue) {
      diff = true
      l!.nodeValue = r!.nodeValue
    }
  }

  if (diff && lhs !== root) {
    const el = lhs instanceof Element ? lhs : lhs.parentElement
    el?.setAttribute(diff_key, String(true))
  } else if (lhs instanceof Element) {
    lhs.removeAttribute(diff_key)
  }
}
