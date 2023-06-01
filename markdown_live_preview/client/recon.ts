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
  diff_key,
  lhs,
  rhs,
}: {
  root: Node
  diff_key: string
  lhs: Node
  rhs: Node
}) => {
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

        reconciliate({ diff_key, root, lhs: l, rhs: r })
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

  if (diff && lhs instanceof Element && lhs !== root) {
    lhs.setAttribute(diff_key, String(true))
  }
}
