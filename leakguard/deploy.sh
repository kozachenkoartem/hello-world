#!/bin/sh
set -eu

script_directory=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$script_directory"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 user@orange-pi-host" >&2
    exit 2
fi

target="$1"
target_directory="leakguard-experiments"
project_directory="$target_directory/leakguard"

ssh "$target" "mkdir -p '$project_directory'"
scp -pr __init__.py wake_listener.py tuya_worker.py leakguard.service config.example.json README.md tests "$target:$project_directory/"
