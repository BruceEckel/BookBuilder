#! py -3
# Various validation checks
import re
import sys

import atomic_kotlin_builder.config as config
from atomic_kotlin_builder.epub import create_markdown_filename
from atomic_kotlin_builder.util import *


slugline = re.compile("^// .+?\.kt$", re.MULTILINE)


def examples_without_sluglines(text):
    for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL):
        listing = group[1]
        lines = listing.splitlines()
        if slugline.match(lines[0]):
            continue
        if "Type1" in listing or "ReturnType" in listing:
            continue
        for line in lines:
            if line.strip().startswith("fun "):
                return listing
    else:
        return False


def extract_listings(text):
    return [group[1] for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL)]


def parse_comment_block(n, lines):
    block = ""
    while n < len(lines) and "//" in lines[n]:
        block += lines[n].split("//")[1].lstrip()
        n += 1
    return n, block


def parse_blocks_of_comments(listing):
    result = []
    lines = listing.splitlines()
    n = 0
    while n < len(lines):
        if "//" in lines[n]:
            n, block = parse_comment_block(n, lines)
            result.append(block)
        else:
            n += 1
    return result


def find_uncapitalized_comment(text):
    "Need to add checks for '.' and following cap"
    for listing in extract_listings(text):
        for comment_block in parse_blocks_of_comments(listing):
            first_char = comment_block.strip()[0]
            if first_char.isalpha() and not first_char.isupper():
                return comment_block
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
        with md.open() as f:
            text = f.read()
            lines = text.splitlines()

        if re.search("``` +kotlin", text):
            error("Contains spaces between ``` and kotlin")

        noslug = examples_without_sluglines(text)
        if noslug:
            error("Contains compileable example(s) without a slugline: {}".format(noslug))

        if md.name != "00_Front.md":
            title = lines[0]
            if create_markdown_filename(title) != md.name[3:]:
                error("Atom Title: {}".format(title))
            if " and " in title:
                error("'and' in title should be '&': {}".format(title))

        uncapped = find_uncapitalized_comment(text)
        if uncapped:
            error("Uncapitalized comment: {}".format(uncapped))
