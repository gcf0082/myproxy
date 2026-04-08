#!/bin/bash
# Query myproxy captured requests

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

DB_PATH="/tmp/test_proxy.db"

python main.py query --db "$DB_PATH" "$@"
