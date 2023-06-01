MAKEFLAGS += --jobs
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS := -Eeuo pipefail -O dotglob -O nullglob -O failglob -O globstar -c

.DEFAULT_GOAL := dev

.PHONY: clean clobber

clean:
	shopt -u failglob
	rm -rf -- .mypy_cache/ build/ dist/ markdown_live_preview.egg-info/ markdown_live_preview/js/*.{css,js,html}

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

lint: .venv/bin/mypy
	'$<' -- .

node_modules/.bin/vite:
	npm install

.PHONY: lint

init: .venv/bin/mypy node_modules/.bin/vite

.PHONY: build

build: .venv/bin/mypy node_modules/.bin/vite
	.venv/bin/python3 ./build.py

.PHONY: release

release: build
	.venv/bin/python3 <<EOF
	from setuptools import setup
	from sys import argv
	argv.extend(("sdist", "bdist_wheel"))
	setup()
	EOF

fmt: .venv/bin/mypy
	.venv/bin/isort --profile=black --gitignore -- .
	.venv/bin/black --extend-exclude pack -- .

.PHONY: run

run: build
	.venv/bin/python3 -m markdown_live_preview --open -- ./README.md

.PHONY: dev

dev:
	watchexec --shell none --restart --exts html,scss,ts,py -- make run
