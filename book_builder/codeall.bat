@echo off
for %%f in (*.py) do (
    code "%%~nf.py"
)
