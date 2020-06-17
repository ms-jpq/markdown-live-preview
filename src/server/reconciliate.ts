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

// const reconciliate = (prev: HTMLElement, next: HTMLElement) => {}

export const reconciliate = (prev: JSDOM, next: string) => {
  return next
}

