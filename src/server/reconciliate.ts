import { JSDOM } from "jsdom"
import { reduce } from "nda/dist/isomorphic/iterator"

const p_attrs = (attrs: NamedNodeMap) =>
  reduce((a, { name, value }) => Object.assign(a, { [name]: value }), {}, attrs)

const diff_shallow = (prev: HTMLElement, next: HTMLElement) => {
  if (prev.tagName !== next.tagName) {
    return true
  }
  const pa = Object.entries(p_attrs(prev.attributes))
  const na = Object.entries(p_attrs(next.attributes))
  for (const [p, v] of pa) {
    if (na[p] !== v) {
      return true
    }
    Reflect.deleteProperty(na, p)
  }
  for (const [p, v] of na) {
    if (pa[p] !== v) {
      return true
    }
  }
  const pc = prev.classList.value
  const nc = next.classList.value
  if (pc !== nc) {
    return true
  }
  return false
}

export const reconciliate = (prev: JSDOM | undefined, next: string) => {
  const dom = new JSDOM(next)
  const html = dom.window.document.body.innerHTML
  return { dom, html }
}

