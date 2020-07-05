import hljs from "highlight.js"
import markdown from "markdown-it"
import split from "split2"

const highlight = (str: string, lang: string) => {
  if (lang && hljs.getLanguage(lang)) {
    return hljs.highlight(lang, str).value
  } else {
    return ""
  }
}

const md = markdown({ xhtmlOut: true, highlight })

const render = (markdown: string) => md.render(markdown)

const main = async () => {
  const SEP = "\0"
  const stream = process.stdin.pipe(split(SEP))
  for await (const data of stream) {
    const xhtml = render(data)
    process.stdout.write(xhtml)
    process.stdout.write(SEP)
  }
}

main()
