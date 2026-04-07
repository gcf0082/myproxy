#!/bin/bash
# Query myproxy captured requests

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

python main.py query --seconds 3600 "$@"
