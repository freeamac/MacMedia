#!/usr/bin/env bash

# Python code style checker
set -eu

fail=0
cd "$(dirname "$0")/.."

# For module imports
: ${PYTHONPATH:=}
export PYTHONPATH="${PYTHONPATH}:`pwd`/app"

if ! flake8 "./app" "./tests"; then
    fail=$(($fail + 1))
fi

exit $fail
