import { JSDOM } from "jsdom"
import {
  filter,
  longzip,
  join,
  map,
  reduce,
} from "nda/dist/isomorphic/iterator"
import { _focus_ } from "../consts"

const p_attrs = (attrs: NamedNodeMap): Record<string, string> =>
  reduce((a, { name, value }) => Object.assign(a, { [name]: value }), {}, attrs)

const p_text = (el: Element) =>
  join(
    "",
    map(
      (n) => n.nodeValue,
      filter((n) => n.nodeType === 3, el.childNodes),
    ),
  )

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
  return p_text(prev) !== p_text(next)
}

const mark = (el: Element) => {
  el.id = _focus_
  throw undefined
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
        mark_diff(p, n)
      }
      pp = n
    }
  }
}

export const reconciliate = (prev: JSDOM | undefined, next: string) => {
  const dom = new JSDOM(next)
  if (prev !== undefined) {
    try {
      mark_diff(prev.window.document.body, dom.window.document.body)
    } catch {}
  } else {
    const child = dom.window.document.body.firstElementChild
    if (child) {
      child.id = _focus_
    }
  }
  const html = dom.window.document.body.innerHTML
  return { dom, html }
}

