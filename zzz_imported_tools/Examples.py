# py -3
# -*- coding: utf8 -*-
"""
Extract code examples from book
"""
from pathlib import Path
import os
import sys
import shutil
import re
import time
from betools import CmdLine
import config
from make_build_scripts import powershellfile, batchfile, bashfile

def recreate_examples_dir():
    "Create and populate a fresh examples_dir"
    if config.examples_dir.exists():
        shutil.rmtree(str(config.examples_dir))
        time.sleep(1)
    config.examples_dir.mkdir()


example = re.compile("```(?:kotlin|java)\s+(//.*?)```", re.DOTALL)

def extract_examples():
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        atom = md.read_text(encoding="utf8")
        for part in example.split(atom):
            if part.startswith("//"):
                part = part.strip()
                lines = part.splitlines()
                filename = lines[0].split()[1]
                fname = config.examples_dir / filename
                fname.write_text(part + "\n")



if __name__ == '__main__':
    recreate_examples_dir()
    extract_examples()

    # bashfile(config.examples_dir.glob("*.kt"))
    # batchfile(config.examples_dir.glob("*.kt"))
    # powershellfile(config.examples_dir.glob("*.kt"))
    # print("Atomic Kotlin examples extracted and build scripts created")
    # os.system("subl " + str(config.examples_dir / "testall.sh"))
    # os.system("subl " + str(config.examples_dir / "testall.ps1"))
    # os.system("subl " + str(config.examples_dir / "testall.bat"))
