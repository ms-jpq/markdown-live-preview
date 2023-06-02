MAKEFLAGS += --jobs
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -Eeuo pipefail -O dotglob -O nullglob -O extglob -O failglob -O globstar -c

.DEFAULT_GOAL := dev

.PHONY: clean clobber

DIST := markdown_live_preview/js

clean:
	shopt -u failglob
	rm -rf -- .cache/ .mypy_cache/ build/ dist/ markdown_live_preview.egg-info/ '$(DIST)' tsconfig.tsbuildinfo

clobber: clean
	shopt -u failglob
	rm -rf -- node_modules/ .venv/

.PHONY: init

.venv/bin/pip:
	python3 -m venv -- .venv

.venv/bin/mypy: .venv/bin/pip
	.venv/bin/python3 <<EOF
	from itertools import chain
	from os import execl
	from sys import executable
	from tomllib import load

	toml = load(open("pyproject.toml", "rb"))
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
	EOF

.PHONY: tsc

.FORCE:

tsc: node_modules/.bin/esbuild
	node_modules/.bin/tsc

.PHONY: mypy

mypy: .venv/bin/mypy
	'$<' --disable-error-code=method-assign -- .

.PHONY: lint

lint: mypy tsc

node_modules/.bin/esbuild:
	npm install

init: .venv/bin/mypy node_modules/.bin/esbuild

.PHONY: build

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

.PHONY: release

release: build
	.venv/bin/python3 <<EOF
	from setuptools import setup
	from sys import argv
	argv.extend(("sdist", "bdist_wheel"))
	setup()
	EOF

.PHONY: black

.PHONY: prettier

.PHONY: fmt

black: .venv/bin/mypy
	.venv/bin/isort --profile=black --gitignore -- .
	.venv/bin/black --extend-exclude pack -- .

prettier:
	npx --yes -- prettier --write -- .

fmt: black prettier

.PHONY: run

run:
	.venv/bin/python3 -m markdown_live_preview --open -- ./README.md

.PHONY: watch-js

watch-js:
	watchexec --shell none --restart --exts html,scss,ts -- make build

.PHONY: watch-py

watch-py:
	watchexec --shell none --restart --exts py -- make run

.PHONY: dev

dev: watch-js watch-py
