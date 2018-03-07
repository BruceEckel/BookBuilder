"""
1. Renames atoms according to first line (headline) in the atom
2. Renumbers atoms
"""
from pathlib import Path
import re
import sys
import book_builder.config as config


def generate_name(n, markdown_atom):
    atom_title = markdown_atom.read_text().splitlines()[0]
    title = re.sub('`|:|!|,', '', atom_title)
    title = title.replace('&', 'and')
    title = title.replace('-', '_')
    title = title.replace(' ', '_')
    return "%03d_" % n + title + ".md"


def title_list():
    return [[md.name, generate_name(n, md)]
            for n, md in enumerate(config.markdown_dir.glob("*.md"))
            ][1:]  # Remove zeroeth element


def rename_atoms(titles):
    for t in reversed(titles):
        if t[0] != t[1]:
            old = config.markdown_dir / t[0]
            new = config.markdown_dir / t[1]
            print(f"renaming {old.name} to {new.name}")
            old.rename(new)


def fix_names_and_renumber_atoms():
    titles = title_list()
    rename_atoms(titles)
