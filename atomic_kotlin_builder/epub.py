#! py -3
# epub tools
import os
import re
import pprint
from collections import OrderedDict
from pathlib import Path

import atomic_kotlin_builder.config as config

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
    if not config.ebook_build_dir.exists():
        os.makedirs(config.ebook_build_dir)
    assembled = ""
    atom_names = []
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        atom_names.append(md.name[3:-3])
        print(str(md.name), end=", ")
        with md.open(encoding="utf8") as chapter:
            assembled += chapter.read() + "\n"
    with config.combined_markdown.open('w', encoding="utf8") as book:
        book.write(assembled)
    config.recent_atom_names.write_text("anames = " + pprint.pformat(atom_names) + "\n")
    return "{} Created".format(config.combined_markdown.name)


def disassemble_combined_markdown_file(target_dir=config.markdown_dir):
    "Turn markdown file into a collection of chapter-based files"
    with Path(config.combined_markdown).open(encoding="utf8") as akmd:
        book = akmd.read()
    chapters = re.compile(r"\n([A-Za-z0-9\,\!\:\&\?\+\-\/\(\)\` ]*)\n=+\n")
    parts = chapters.split(book)
    names = parts[1::2]
    bodies = parts[0::2]
    chaps = OrderedDict()
    chaps["Front"] = bodies[0]
    for i, nm in enumerate(names):
        chaps[nm] = bodies[i + 1].strip() + "\n"

    # Ensure new names match old names:
    import atomic_kotlin_builder.recent_atom_names
    old_names = set(atomic_kotlin_builder.recent_atom_names.anames)
    new_names = {create_markdown_filename(nm)[:-3] for nm in names}
    new_names.add("Front")
    diff = old_names.difference(new_names)
    if diff:
        print("Old names not in new names:")
        for d in diff:
            print("   {}".format(d))
        print("=== New Names ===")
        for nm in new_names:
            print(nm)
        print("=== Old Names ===")
        for nm in old_names:
            print(nm)
        return "Disassembly failed"

    # Ensure the number of names are the same
    len_old_names = len(atomic_kotlin_builder.recent_atom_names.anames)
    len_new_names = len(names) + 1 # for Front
    if len_old_names != len_new_names:
        print("Number of old names: {}".format(len_old_names))
        print("Number of new names: {}".format(len_new_names))
        return "Disassembly failed"

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
            chp.write(chaps[p].strip() + "\n")
    return "Successfully disassembled combined Markdown"
