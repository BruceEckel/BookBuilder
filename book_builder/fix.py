#! py -3
# Various batch fixes
import re
import sys
import book_builder.config as config
# from book_builder.epub import create_markdown_filename
from book_builder.util import *


def all_fixes():
    "Multiple batch fixes on the book"
    print("Running all fixes ...")
    if not config.markdown_dir.exists():
        return "Cannot find {}".format(config.markdown_dir)
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        # print(f"{md}")
        reporter = ErrorReporter(md.name)
        lines = md.read_text().splitlines()
        lines = fix_gap_between_package_and_import(lines, reporter)
        text = "\n".join(lines)
        text = text.strip() + "\n"
        md.write_text(text)


##################################################
############## Individual fixes ##################
##################################################


def degap(lines):
    for n, line in enumerate(lines):
        if  line.startswith("package ") and \
            lines[n+1].strip() == "" and \
            lines[n+2].startswith("import "):
                del lines[n+1]
                # for i in range(n, n+2):
                #     print(f"{lines[i]}")
                return lines, True
    return lines, False


def fix_gap_between_package_and_import(lines, error_reporter):
    "Ensure there's no gap between package and imports"
    while True:
        lines, degapped = degap(lines)
        if not degapped:
            return lines
