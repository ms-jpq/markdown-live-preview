MAKEFLAGS += --jobs
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar -c

.DEFAULT_GOAL := dev
.FORCE:

.PHONY: clean clobber init run
.PHONY: lint mypy tsc
.PHONY: fmt black prettier
.PHONY: release build
.PHONY: dev watch-py watch-js

DIST := markdown_live_preview/js

clean:
	shopt -u failglob
	rm -rf -- .cache/ .mypy_cache/ build/ dist/ markdown_live_preview.egg-info/ '$(DIST)' tsconfig.tsbuildinfo

clobber: clean
	shopt -u failglob
	rm -rf -- node_modules/ .venv/

.venv/bin/python3:
	python3 -m venv -- .venv

define PYDEPS
from itertools import chain
from os import execl
from sys import executable

from tomli import load

with open("pyproject.toml", "rb") as fd:
  toml = load(fd)

project = toml["project"]
execl(
  executable,
  executable,
  "-m",
  "pip",
  "install",
  "--upgrade",
  "--",
  *project.get("dependencies", ()),
  *chain.from_iterable(project["optional-dependencies"].values()),
)
endef
export -- PYDEPS

.venv/bin/mypy: .venv/bin/python3
	'$<' -m pip install -- tomli
	'$<' <<< "$$PYDEPS"

tsc: node_modules/.bin/esbuild
	node_modules/.bin/tsc

mypy: .venv/bin/mypy
	'$<' --disable-error-code=method-assign -- .

node_modules/.bin/esbuild:
	npm install

init: .venv/bin/mypy node_modules/.bin/esbuild

lint: mypy tsc

$(DIST):
	mkdir -p -- '$@'

$(DIST)/__init__.py: $(DIST)
	touch -- '$@'

.cache/codehl.css:: .venv/bin/mypy
	mkdir -p -- .cache
	.venv/bin/python3 -m markdown_live_preview.server > '$@'

$(DIST)/site.css: markdown_live_preview/client/site.scss .cache/codehl.css $(DIST)
	node_modules/.bin/sass --style compressed -- '$<' '$@'

$(DIST)/index.html: markdown_live_preview/client/index.html $(DIST)
	cp --recursive --force --reflink=auto -- '$<' '$@'

$(DIST)/main.js: node_modules/.bin/esbuild .FORCE
	node_modules/.bin/esbuild --bundle --format=esm --outfile='$@' ./markdown_live_preview/client/main.ts

build: $(DIST)/__init__.py $(DIST)/index.html $(DIST)/main.js $(DIST)/site.css

release: build
	.venv/bin/python3 <<EOF
	from setuptools import setup
	from sys import argv
	argv.extend(("sdist", "bdist_wheel"))
	setup()
	EOF

black: .venv/bin/mypy
	.venv/bin/isort --profile=black --gitignore -- .
	.venv/bin/black --extend-exclude pack -- .

prettier:
	npx --yes -- prettier --write -- .

fmt: black prettier

run: .venv/bin/mypy build
	.venv/bin/python3 -m markdown_live_preview --open -- ./README.md

watch-js:
	watchexec --shell none --restart --exts html,scss,ts -- make build

watch-py:
	watchexec --shell none --restart --exts py -- make run

dev: watch-js watch-py
