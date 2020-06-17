import hljs from "highlight.js"
import markdown from "markdown-it"

const highlight = (str: string, lang: string) => {
  if (lang && hljs.getLanguage(lang)) {
    return hljs.highlight(lang, str).value
  } else {
    return ""
  }
}

const md = markdown({ highlight })

export const render = (markdown: string) => md.render(markdown)

