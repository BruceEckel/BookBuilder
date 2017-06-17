@echo off
rem venv.bat

rem Works if you're outside the starting directory:
if defined VIRTUAL_ENV (
  deactivate.bat
) else (
  rem Only works inside starting directory, otherwise
  rem creates a new virtual environment:
  if exist virtualenv (
    virtualenv\Scripts\activate.bat
  ) else (
    python -m venv virtualenv
    virtualenv\Scripts\activate.bat
    pip install --editable .
  )
)
