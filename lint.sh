#!/usr/bin/env bash

set -eu
set -o pipefail

cd "$(dirname "$0")" || exit


mypy src/server/*.py
