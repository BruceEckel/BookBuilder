#! py -3
# Utilities
import os
import re
from pathlib import Path
from collections import OrderedDict

import atomic_kotlin_builder.config as config


def clean(dir_to_remove):
    "Remove directory"
    try:
        if dir_to_remove.exists():
            shutil.rmtree(str(dir_to_remove))
            return "Removed: {}".format(dir_to_remove)
        else:
            return "Doesn't exist: {}".format(dir_to_remove)
    except:
        return """Removal failed: {}
        Are you inside that directory, or using a file inside it?
        """.format(dir_to_remove)
        # raise RuntimeError()


def create_markdown_filename(h1):
    fn = h1.replace(": ", "_")
    fn = fn.replace(" ", "_") + ".md"
    fn = fn.replace("&", "and")
    fn = fn.replace("?", "")
    fn = fn.replace("+", "P")
    fn = fn.replace("/", "")
    fn = fn.replace("-", "_")
    fn = fn.replace("(", "")
    fn = fn.replace(")", "")
    fn = fn.replace("`", "")
    fn = fn.replace(",", "")
    fn = fn.replace("!", "")
    return fn


def create_numbered_markdown_filename(h1, n):
    return "%02d_" % n + create_markdown_filename(h1)


def combine_markdown_files():
    """
    Put markdown files together
    """
    if not config.build_dir.exists():
        os.makedirs(config.build_dir)
    assembled = ""
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        print(str(md.name), end=", ")
        with md.open(encoding="utf8") as chapter:
            assembled += chapter.read() + "\n"
    with config.combined_markdown.open('w', encoding="utf8") as book:
        book.write(assembled)
    return "{} Created".format(config.combined_markdown.name)


def disassemble_combined_markdown_file(target_dir=config.markdown_dir):
    "Turn markdown file into a collection of chapter-based files"
    with Path(config.combined_markdown).open(encoding="utf8") as akmd:
        book = akmd.read()
    chapters = re.compile(r"\n([A-Za-z\:\&\?\+\-\/\(\)\` ]*)\n=+\n")
    parts = chapters.split(book)
    names = parts[1::2]
    bodies = parts[0::2]
    chaps = OrderedDict()
    chaps["Front"] = bodies[0]
    for i, nm in enumerate(names):
        chaps[nm] = bodies[i + 1].strip() + "\n"

    if not target_dir.exists():
        target_dir.mkdir()
    for i, p in enumerate(chaps):
        disassembled_file_name = create_numbered_markdown_filename(p, i)
        print(disassembled_file_name)
        dest = target_dir / disassembled_file_name
        with dest.open('w', encoding="utf8") as chp:
            if "Front" not in p:
                chp.write(p + "\n")
                chp.write("=" * len(p) + "\n\n")
            chp.write(chaps[p])
