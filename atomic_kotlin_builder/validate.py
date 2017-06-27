#! py -3
# Various validation checks
import re
import sys

import atomic_kotlin_builder.config as config
from atomic_kotlin_builder.util import create_markdown_filename

slugline = re.compile("^// .+?\.kt$", re.MULTILINE)


def examples_without_sluglines(text):
    for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL):
        listing = group[1]
        lines = listing.splitlines()
        if slugline.match(lines[0]):
            continue
        for line in lines:
            if line.strip().startswith("fun "):
                return True
    else:
        return False


def general():
    "Multiple tests to find problems in the book"
    print("Running general validation tests ...")
    if not config.markdown_dir.exists():
        return "Cannot find {}".format(config.markdown_dir)
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        name_printed = False

        def error(msg):
            nonlocal name_printed
            if not name_printed:
                print("{}".format(md.name))
                name_printed = True
            print("    {}".format(msg))
        text = md.read_text()

        if re.search("``` +kotlin", text):
            error("Contains spaces between ``` and kotlin")

        if examples_without_sluglines(text):
            error("Contains compileable example(s) without a slugline")


def markdown_names():
    "Ensure markdown file names match chapter titles"
    print("Validating Markdown File Names ...")
    if not config.markdown_dir.exists():
        return "Cannot find {}".format(config.markdown_dir)
    for md in [f for f in config.markdown_dir.iterdir() if f.name[0].isdigit()]:
        if md.name == "00_Front.md":
            continue
        lines = md.read_text().splitlines()
        if not lines[1].startswith("==="):
            print("{} Missing Chapter Name".format(md))
            sys.exit(1)
        chap_name = md.name[3:-3]
        title = create_markdown_filename(lines[0].strip())[:-3]
        if chap_name != title:
            print("{}: {} chapter title inconstent: {}".format(
                md.name, chap_name, title))
