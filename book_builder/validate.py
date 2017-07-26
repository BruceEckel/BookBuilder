#! py -3
# Various validation checks
import re
import sys

import book_builder.config as config
from book_builder.epub import create_markdown_filename
from book_builder.util import *


def all_checks():
    "Multiple tests to find problems in the book"
    print("Running all validation tests ...")
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        reporter = ErrorReporter(md.name)
        with md.open() as f:
            text = f.read()
        validate_tag_no_gap(text, reporter)
        validate_complete_examples(text, reporter)
        validate_filenames_and_titles(md, text, reporter)
        validate_capitalized_comments(text, reporter)
        validate_no_tabs(text, reporter)
        validate_listing_indentation(text, reporter)


#################################################################
############## Individual validation functions ##################
#################################################################


### Ensure there's no gap between ``` and language_name:


def validate_tag_no_gap(text, error_reporter):
    if re.search(f"``` +{config.language_name}", text):
        error_reporter(f"Contains spaces between ``` and {config.language_name}")


### Check for code fragments that should be turned into examples:

slugline = re.compile(f"^// .+?\.{config.code_ext}$", re.MULTILINE)

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


def validate_complete_examples(text, error_reporter):
    noslug = examples_without_sluglines(text)
    if noslug:
        error_reporter(f"Contains compileable example(s) without a slugline: {noslug}")


### Ensure atom titles conform to standard and agree with file names:


def validate_filenames_and_titles(md, text, error_reporter):
    if md.name == "00_Front.md":
        return
    title = text.splitlines()[0]
    if create_markdown_filename(title) != md.name[3:]:
        error_reporter(f"Atom Title: {title}")
    if " and " in title:
        error_reporter(f"'and' in title should be '&': {title}")


### Check for un-capitalized comments:


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
                return comment_block.strip()
    return False


def validate_capitalized_comments(text, error_reporter):
    with (config.root_path / "data" / "comment_capitalization_exclusions.txt").open() as f:
        exclusions = f.read()
    uncapped = find_uncapitalized_comment(text)
    if uncapped and uncapped not in exclusions:
        error_reporter(f"Uncapitalized comment: {uncapped}")


### Check for four-space indentation:

def bad_indentation(lines, error_reporter):
    indents = [(len(line) - len(line.lstrip(' ')), line) for line in lines]
    if indents[0][0]: return True # First line can't be indented
    for indent, line in indents:
        if indent % 2 != 0:
            error_reporter(f"Non-even indent in line: {line}")
            return True
    indent_counts = [ind//2 for ind, ln in indents]
    ok = all(y == x + 1
            or y == x
            or y == x - 1
            or y == 0
            for x, y in zip(indent_counts, indent_counts[1:]))
    if not ok:
        print(indent_counts)
        return True
    return False


def find_bad_indentation(text, error_reporter):
    for listing in extract_listings(text):
        lines = listing.splitlines()
        if bad_indentation(lines, error_reporter):
            return lines[0]
    return False


def validate_listing_indentation(text, error_reporter):
    bad_indent = find_bad_indentation(text, error_reporter)
    if bad_indent:
        error_reporter(f"Bad indentation: {bad_indent}")


### Check for tabs:

def validate_no_tabs(text, error_reporter):
    "\t"
    if "\t" in text:
        error_reporter("Tab found!")


