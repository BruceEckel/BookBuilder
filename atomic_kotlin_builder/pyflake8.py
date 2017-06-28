import os
import subprocess
from pathlib import Path

for pyfile in Path.cwd().rglob("*.py"):
    os.chdir(str(pyfile.parent))
    subprocess.run(['flake8', pyfile.name], shell=True)
