#!/bin/bash
# venv.sh
# Works if you're outside the starting directory:
if [ -n "$VIRTUAL_ENV" ];
then
  deactivate
else
  # Only works inside starting directory, otherwise
  # creates a new virtual environment:
  if test -d virtualenv;
  then
    source virtualenv/Scripts/activate
  else
    python -m venv virtualenv
    source virtualenv/Scripts/activate
    pip install --editable .
  fi
fi
