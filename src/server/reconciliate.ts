import { JSDOM } from "jsdom"
import { reduce } from "nda/dist/isomorphic/iterator"

const p_attrs = (attrs: NamedNodeMap): Record<string, string> =>
  reduce((a, { name, value }) => Object.assign(a, { [name]: value }), {}, attrs)

const diff_shallow = (prev: HTMLElement, next: HTMLElement) => {
  if (prev.tagName !== next.tagName) {
    return true
  }
  const pa = p_attrs(prev.attributes)
  const na = p_attrs(next.attributes)
  Reflect.deleteProperty(pa, "id")
  Reflect.deleteProperty(na, "id")
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

