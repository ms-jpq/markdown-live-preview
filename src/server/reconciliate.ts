import { JSDOM } from "jsdom"
import { assert } from "nda/dist/isomorphic/assertion"
import { flat_map, longzip, reduce } from "nda/dist/isomorphic/iterator"
import { _focus_ } from "../consts"

const inline_el = new Set(
  flat_map((t) => [t, t.toUpperCase()], [
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
  ]),
)

const Interrupt = "Interrupt"

const p_attrs = (attrs: NamedNodeMap): Record<string, string> =>
  reduce((a, { name, value }) => Object.assign(a, { [name]: value }), {}, attrs)

const diff_shallow = (prev: Element, next: Element) => {
  if (prev.tagName !== next.tagName) {
    return true
  }
  const pa = Object.assign(p_attrs(prev.attributes), { id: undefined })
  const na = Object.assign(p_attrs(next.attributes), { id: undefined })
  for (const [p, v] of Object.entries(pa)) {
    if (na[p] !== v) {
      return true
    }
    Reflect.deleteProperty(na, p)
  }
  for (const [p, v] of Object.entries(na)) {
    if (pa[p] !== v) {
      return true
    }
  }

  const no_children = !prev.children.length && !next.children.length
  const is_inline = inline_el.has(next.tagName)
  if (no_children || is_inline) {
    return prev.textContent !== next.textContent
  } else {
    return false
  }
}

const mark = (el: Element) => {
  el.id = _focus_
  throw Interrupt
}

const mark_diff = (prev: Element, next: Element) => {
  if (diff_shallow(prev, next)) {
    mark(next)
  } else {
    const zipped = longzip(prev.children, next.children)
    let pp = next
    for (const [p, n] of zipped) {
      if (p && !n) {
        mark(pp)
      } else if (!p && n) {
        mark(n)
      } else {
        mark_diff(p!, n!)
      }
      pp = n || pp
    }
  }
}

export const reconciliate = (prev: JSDOM | undefined, next: string) => {
  const dom = new JSDOM(next)
  if (prev !== undefined) {
    try {
      mark_diff(prev.window.document.body, dom.window.document.body)
    } catch (e) {
      assert(e === Interrupt)
    }
  }
  const html = dom.window.document.body.innerHTML
  return { dom, html }
}

