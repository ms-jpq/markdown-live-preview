import { JSDOM } from "jsdom"

const diff_pair = (prev: HTMLElement, next: HTMLElement) => {
  if (prev.tagName !== next.tagName) {
    return true
  } else if (prev.textContent !== next.textContent) {
    return true
  } else {
    return false
  }
}

const reconciliate = (prev: HTMLElement, next: HTMLElement) => {}

export const mark = (prev: JSDOM, next: JSDOM) => {
  return { prev, next }
}

