#!/usr/bin/env bash
# venv.sh
# Turns virtual environment on and off.
# Initializes virtualenv if it doesn't exist.

set -e pipefail

# Works even if you're outside the starting directory:
if [[ -v "${VIRTUAL_ENV}" ]]; then
    echo "Deactivating"
    deactivate
else
    # Only works inside starting directory, otherwise
    # creates a new virtual environment:
    if [[ -e ./virtualenv/bin/activate ]]; then
        echo "Activating"
        source ./virtualenv/bin/activate # How to make this affect the calling shell?
    else
        echo "Initializing new virtualenv"
        python3 -m venv virtualenv
        source ./virtualenv/bin/activate # How to make this affect the calling shell?
        pip install --editable .
    fi
fi
