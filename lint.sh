#!/usr/bin/env bash

set -eu
set -o pipefail

cd "$(dirname "$0")" || exit


mypy --ignore-missing-imports -- markdown_live_preview/**/*.py *.py
