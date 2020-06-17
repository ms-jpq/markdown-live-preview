export type ServerOpts = {
  port: number
  html: Record<string, string>
  js: Record<string, string>
  css: Record<string, string>
}

export const serve = async ({ port, html, js, css }: ServerOpts) => {}

