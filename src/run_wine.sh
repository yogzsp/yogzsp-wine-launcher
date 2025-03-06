#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_exe>"
    exit 1
fi

PROGRAM_PATH="$1"
PROGRAM_DIR=$(dirname "$PROGRAM_PATH")
PROGRAM_NAME=$(basename "$PROGRAM_PATH")

cd "$PROGRAM_DIR" || exit 1
wine "$PROGRAM_NAME"
