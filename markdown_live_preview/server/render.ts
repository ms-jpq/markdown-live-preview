import hljs from "highlight.js"
import markdown from "markdown-it"

const read_stdin = (): Promise<string> => {
  const bufs: Buffer[] = []
  process.stdin.on("data", (buf) => bufs.push(buf))
  return new Promise<string>((resolve) =>
    process.stdin.once("end", () => resolve(Buffer.concat(bufs).toString())),
  )
}

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
  const data = await read_stdin()
  const xhtml = render(data)
  process.stdout.write(xhtml)
}

main()
