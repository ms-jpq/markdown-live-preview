# [Markdown Live Preview](https://ms-jpq.github.io/markdown-live-preview)

## Features

- **Live Preview:** Updates preview on file save

- **Auto Follow:** Focus on edited element

- **Syntax Highlight:** Highlighted using [Pygments](https://github.com/pygments/pygments)

- **Github flavoured:** Looks familiar

## Preview

The animation is only choppy because it's a compressed gif.

![preview.gif](https://github.com/ms-jpq/markdown-live-preview/raw/md/preview/smol.gif)

## Usage

```bash
mlp |name of markdown|
```

| Flags                  | Meaning                  |
| ---------------------- | ------------------------ |
| `-p, --port PORT=8080` | Port to use              |
| `-o, --open`           | No localhost restriction |
| `--nf, --no-follow`    | Do not follow edits      |
| `--nf, --no-browser`   | Do not open browser      |

## [Install](https://pypi.org/project/markdown-live-preview)

```bash
pip install -U markdown_live_preview
```
