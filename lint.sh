#!/usr/bin/env bash

set -eu
set -o pipefail

cd "$(dirname "$0")" || exit


mypy --ignore-missing-imports -- src/server/*.py *.py
