#!/usr/bin/env bash
# venv.sh
# Turns virtual environment on and off.
# Initializes virtualenv if it doesn't exist.

set -e pipefail

# Works even if you're outside the starting directory:
if [[ -x "${VIRTUAL_ENV}" ]]; then
    echo "Deactivating"
    deactivate
else
    # Only works inside starting directory, otherwise
    # creates a new virtual environment:
    if [[ -n ./virtualenv/bin/activate ]]; then
        echo "Activating"
        source ./virtualenv/bin/activate
    else
        echo "Initializing new virtualenv"
        python3 -m venv virtualenv
        source ./virtualenv/bin/activate
        pip install --editable .
    fi
fi
