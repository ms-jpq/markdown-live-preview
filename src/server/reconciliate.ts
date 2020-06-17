import { JSDOM } from "jsdom"

const diff_pair = (prev: HTMLElement, next: HTMLElement) => {
  if (prev.tagName !== next.tagName) {
    return true
  } else if (prev.children.length !== next.children.length) {
    return true
  } else if (prev.textContent !== next.textContent) {
    return true
  } else {
    return false
  }
}

export const reconciliate = (prev: JSDOM | undefined, next: string) => {
  const dom = new JSDOM(next)
  const html = dom.window.document.body.innerHTML
  return { dom, html }
}

