#! py -3
# Various validation checks
import re
import sys

import book_builder.config as config
from book_builder.epub import create_markdown_filename
from book_builder.util import *


def all_checks():
    "Multiple tests to find problems in the book"
    print(f"Validating {config.markdown_dir}")
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    for md in config.markdown_dir.glob("[0-9]*_*.md"):
        # print(md)
        reporter = ErrorReporter(md.name)
        with md.open() as f:
            text = f.read()
        validate_tag_no_gap(text, reporter)
        validate_complete_examples(text, reporter)
        validate_filenames_and_titles(md, text, reporter)
        validate_capitalized_comments(text, reporter)
        validate_no_tabs(text, reporter)
        validate_listing_indentation(text, reporter)
        validate_example_sluglines(text, reporter)
        validate_package_names(text, reporter)
        validate_code_listing_line_widths(text, reporter)


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
    if "Front.md" in md.name:
        return
    title = text.splitlines()[0]
    if create_markdown_filename(title) != md.name[4:]:
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
    lines = listing.splitlines()[1:] # Ignore slugline
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


### Check for inconsistent indentation:

def inconsistent_indentation(lines):
    listing_name = lines[0]
    if listing_name.startswith('//'):
        listing_name = listing_name[3:]
    else: # Skip listings without sluglines
        return False
    indents = [(len(line) - len(line.lstrip(' ')), line) for line in lines]
    if indents[0][0]: return "First line can't be indented"
    for indent, line in indents:
        if indent % 2 != 0 and not line.startswith(" *"):
            return f"{listing_name}: Non-even indent in line: {line}"
    indent_counts = [ind//2 for ind, ln in indents] # For a desired indent of 2
    indent_pairs = list(zip(indent_counts, indent_counts[1:]))
    def test(x, y): return (
        y == x + 1
        or y == x
        or y < x # No apparent consistency with dedenting
    )
    ok = [test(x, y) for x, y in indent_pairs]
    if not all(ok):
        return f"{listing_name} lines {[n + 2 for n, x in enumerate(ok) if not x]}"
    return False


def find_inconsistent_indentation(text):
    for listing in extract_listings(text):
        lines = listing.splitlines()
        inconsistent = inconsistent_indentation(lines)
        if inconsistent:
            return inconsistent
    return False


def validate_listing_indentation(text, error_reporter):
    bad_indent = find_inconsistent_indentation(text)
    if bad_indent:
        error_reporter(f"Inconsistent indentation: {bad_indent}")


### Check for tabs:

def validate_no_tabs(text, error_reporter):
    if "\t" in text:
        error_reporter("Tab found!")


### Check for sluglines that don't match the format

def  validate_example_sluglines(text, error_reporter):
    for listing in extract_listings(text):
        lines = listing.splitlines()
        slug = lines[0]
        if not slug.startswith(config.start_comment):
            continue # Improper code fragments caught elsewhere
        if not slug.startswith(config.start_comment + " "):
            error_reporter(f"Bad first line (no space after beginning of comment):\n\t{slug}")
            continue
        slug = slug.split(None, 1)[1]
        if "/" not in slug:
            error_reporter(f"Missing directory in {slug}")


### Check for package names with capital letters

def  validate_package_names(text, error_reporter):
    for listing in extract_listings(text):
        package_decl = [line for line in listing.splitlines() if line.startswith("package ")]
        if not package_decl:
            continue
        # print(package_decl)
        if bool(re.search('([A-Z])', package_decl[0])):
            error_reporter(f"Capital letter in package name:\n\t{package_decl}")

### Check code listing line widths

def  validate_code_listing_line_widths(text, error_reporter):
    for listing in extract_listings(text):
        lines = listing.splitlines()
        if not lines[0].startswith("// "):
            continue
        for n, line in enumerate(lines):
            if len(line.rstrip()) > config.code_width:
                error_reporter(f"Line {n} too wide in {lines[0]}")
