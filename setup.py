#!/usr/bin/env python3

from os.path import normcase
from pathlib import Path

from setuptools import find_packages, setup

_TOP_LEVEL = Path(__file__).resolve().parent

install_requires = Path("requirements.txt").read_text().splitlines()
packages = find_packages(exclude=("tests*",))
package_data = {
    pkg: [
        "py.typed",
        "*.css",
        "*.eot",
        "*.html",
        "*.js",
        "*.svg",
        "*.tff",
        "*.woff",
        "*.woff2",
    ]
    for pkg in packages
}
scripts = [
    normcase(path.relative_to(_TOP_LEVEL))
    for path in (_TOP_LEVEL / "scripts").iterdir()
]

setup(
    name="markdown-live-preview",
    python_requires=">=3.8.0",
    version="0.2.17",
    description="live web preview of markdown docs",
    long_description=(_TOP_LEVEL / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="ms-jpq",
    author_email="github@bigly.dog",
    url="https://github.com/ms-jpq/markdown-live-preview",
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    install_requires=install_requires,
    scripts=scripts,
)
