import os
import subprocess
from pathlib import Path

for pyfile in Path.cwd().rglob("*.py"):
    os.chdir(str(pyfile.parent))
    subprocess.run(['pyflakes', pyfile.name], shell=True)
