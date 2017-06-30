# py -3
# -*- coding: utf8 -*-
"""
TODO: normalize spaces at ends of files

Splits combined markdown file into chapters.

For use after mass edits on single document.
"""
from pathlib import Path
import sys
import re
import shutil
import time
from collections import OrderedDict
from betools import CmdLine
import config

assert config.markdown_dir.exists()
assert config.build_dir.exists()
assert config.combined_markdown.exists()

chapter_splitter = re.compile(r"\n([0-9A-Za-z\:\&\?\+\/ \(\)\-]*)\n=+\n")


def show(text):
    try:
        print(text)
    except:
        print(text.encode("utf8"))


@CmdLine('x')
def find_embedded_chapters_for_debugging():
    level_1_finder = re.compile(r"=+")
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
    # for md in config.markdown_dir.glob("13_*.md"):
        chapter = md.read_text(encoding="utf8").splitlines()
        del chapter[:2]
        for n, line in enumerate(chapter):
            # if line.startswith("==") and line.endswith("=="):
            if level_1_finder.fullmatch(line):
                print(str(md.name))
                show(chapter[n-1])
                show(chapter[n])


@CmdLine('d')
def disassemble_combined_markdown_file():
    "turn markdown file into a collection of chapter-based files"
    with Path(config.combined_markdown).open(encoding="utf8") as ojmd:
        book = ojmd.read()
    parts = chapter_splitter.split(book)
    names = parts[1::2]
    bodies = parts[0::2]
    chaps = OrderedDict()
    chaps["Front"] = bodies[0]
    for i, nm in enumerate(names):
        chaps[nm] = bodies[i + 1].strip() + "\n"

    def mdfilename(h1, n):
        fn = h1.replace(": ", "_")
        fn = fn.replace(" ", "_") + ".md"
        fn = fn.replace("&", "and")
        fn = fn.replace("?", "")
        fn = fn.replace("+", "P")
        fn = fn.replace("/", "")
        fn = fn.replace("(", "")
        fn = fn.replace(")", "")
        fn = fn.replace("-", "_")
        return "%02d_" % n + fn

    # if config.test_dir.exists():
    #     shutil.rmtree(str(config.test_dir))
    #     time.sleep(1)
    # config.test_dir.mkdir()

    for i, p in enumerate(chaps):
        disassembled_file_name = mdfilename(p, i)
        print(disassembled_file_name)
        dest = config.markdown_dir / disassembled_file_name
        # dest = config.test_dir / disassembled_file_name
        with dest.open('w', encoding="utf8") as chp:
            if "Front" not in p:
                chp.write(p + "\n")
                chp.write("=" * len(p) + "\n\n")
            chp.write(chaps[p])


if __name__ == '__main__':
    CmdLine.run()
