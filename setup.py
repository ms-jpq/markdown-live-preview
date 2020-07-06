#!/usr/bin/env python3

from setuptools import setup

name = "markdown_live_preview"


def slurp(path: str) -> str:
    with open(path) as fd:
        return fd.read()


setup(
    name="markdown-live-preview",
    version="0.1.16",
    description="live web preview of markdown docs",
    long_description=slurp("README.md"),
    long_description_content_type="text/markdown",
    author="ms-jpq",
    author_email="github@bigly.dog",
    url="https://github.com/ms-jpq/markdown-live-preview",
    install_requires=slurp("requirements.txt").splitlines(),
    packages=[name, name + ".server"],
    package_data={name: ["js/*"]},
    scripts=["mlp"],
)
