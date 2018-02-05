#! py -3
# Various validation checks
import re
import sys
import pprint
from pathlib import Path
import book_builder.config as config
from book_builder.epub import create_markdown_filename
from book_builder.util import *

all_misspelled = set()


def all_checks():
    "Multiple tests to find problems in the book"
    print(f"Validating {config.markdown_dir}")
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    global validators
    for md in config.markdown_dir.glob("[0-9]*_*.md"):
        # print(md)
        error_reporter = ErrorReporter(md)
        with md.open() as f:
            text = f.read()
        validate_tag_no_gap(text, error_reporter)
        validate_complete_examples(text, error_reporter)
        validate_filenames_and_titles(text, error_reporter)
        validate_capitalized_comments(text, error_reporter)
        validate_no_tabs(text, error_reporter)
        validate_listing_indentation(text, error_reporter)
        validate_example_sluglines(text, error_reporter)
        validate_package_names(text, error_reporter)
        validate_code_listing_line_widths(text, error_reporter)
        validate_hanging_hyphens(text, error_reporter)
        validate_cross_links(text, error_reporter)
        validate_ticked_phrases(text, error_reporter)
        validate_function_descriptions(text, error_reporter)
        validate_full_spellcheck(text, error_reporter)
        validate_punctuation_inside_quotes(text, error_reporter)
        error_reporter.show()
        error_reporter.edit()

    Path(config.root_path / "data" / "all_misspelled.txt").write_text("\n".join(sorted(all_misspelled)))


#################################################################
############## Individual validation functions ##################
#################################################################


### Ensure there's no gap between ``` and language_name


def validate_tag_no_gap(text, error_reporter):
    if re.search(f"``` +{config.language_name}", text):
        error_reporter(f"Contains spaces between ``` and {config.language_name}")


### Check for code fragments that should be turned into examples

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


### Ensure atom titles conform to standard and agree with file names

def validate_filenames_and_titles(text, error_reporter):
    if "Front.md" in error_reporter.md_path.name:
        return
    title = text.splitlines()[0]
    if create_markdown_filename(title) != error_reporter.md_path.name[4:]:
        error_reporter(f"Atom Title: {title}")
    if " and " in title:
        error_reporter(f"'and' in title should be '&': {title}")


### Check for un-capitalized comments

def extract_listings(text):
    return [group[1] for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL)]


def parse_comment_block(n, lines):
    block = ""
    while n < len(lines) and "//" in lines[n]:
        block += lines[n].split("//")[1].strip() + " "
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


### Check for inconsistent indentation

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


### Check for tabs

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

def validate_code_listing_line_widths(text, error_reporter):
    for listing in extract_listings(text):
        lines = listing.splitlines()
        if not lines[0].startswith("// "):
            continue
        for n, line in enumerate(lines):
            if len(line.rstrip()) > config.code_width:
                error_reporter(f"Line {n} too wide in {lines[0]}")


### Spell-check single-ticked items against compiled code

single_tick_dictionary = set(Path(config.root_path / "data" / "single_tick_dictionary.txt").read_text().splitlines())

def remove_nonletters(str):
    for rch in "\"'\\/_`?$|#@(){}[]<>:;.,=!-+*%&0123456789":
        str = str.replace(rch, " ")
    return str.strip()


def strip_comments_from_code(listing):
    listing = re.sub("/\*.*?\*/", "", listing, flags=re.DOTALL)
    lines = listing.splitlines()
    if lines[0].startswith("//"): # Retain elements of slugline
        lines[0] = lines[0][3:]
    lines = [line.split("//")[0].rstrip() for line in lines]
    words = []
    for line in lines:
        words += [word for word in remove_nonletters(line).split()]
    return words


def validate_ticked_phrases(text, error_reporter):
    stripped_listings = [strip_comments_from_code(listing) for listing in extract_listings(text)]
    pieces = {item for sublist in stripped_listings for item in sublist} # Flatten list
    pieces = pieces.union(single_tick_dictionary)
    raw_single_ticks = [t for t in re.findall("`.+?`", text) if t != "```"]
    single_ticks = [remove_nonletters(t[1:-1]).split() for t in raw_single_ticks]
    single_ticks = {item for sublist in single_ticks for item in sublist} # Flatten list
    not_in_examples = single_ticks.difference(pieces)
    if not_in_examples:
        err_msg = ""
        for nie in not_in_examples:
            err_msg += f"Not in examples: {nie}\n"
            for rst in raw_single_ticks:
                if nie in rst:
                    err_msg += f"\t{rst}\n"
        error_reporter(err_msg)


### Spell-check everything

dictionary = set(Path(config.root_path / "data" / "dictionary.txt").read_text().splitlines()).union(
    set(Path(config.root_path / "data" / "supplemental_dictionary.txt").read_text().splitlines()))

def validate_full_spellcheck(text, error_reporter):
    words = set(re.split("(?:(?:[^a-zA-Z]+')|(?:'[^a-zA-Z]+))|(?:[^a-zA-Z']+)", text))
    misspelled = words - dictionary
    if '' in misspelled:
        misspelled.remove('')
    if len(misspelled):
        global all_misspelled
        all_misspelled = all_misspelled.union(misspelled)
        error_reporter(f"Spelling Errors: {pprint.pformat(misspelled)}")


### Ensure there are no hanging em-dashes or hyphens

hanging_emdash = re.compile("[^-]+---$")
hanging_hyphen = re.compile("[^-]+-$")

def validate_hanging_hyphens(text, error_reporter):
    for line in text.splitlines():
        line = line.rstrip()
        if hanging_emdash.match(line):
            error_reporter(f"Hanging emdash: {line}")
        if hanging_hyphen.match(line):
            error_reporter(f"Hanging hyphen: {line}")


### Check for invalid cross-links

explicit_link = re.compile("\[[^]]+?\]\([^)]+?\)", flags=re.DOTALL)
cross_link = re.compile("\[.*?\]", flags=re.DOTALL)

titles = {p.read_text().splitlines()[0].strip() for p in config.markdown_dir.glob("*.md")}

def validate_cross_links(text, error_reporter):
    text = re.sub("```(.*?)\n(.*?)\n```", "", text, flags=re.DOTALL)
    explicits = [e.replace("\n", " ") for e in explicit_link.findall(text)]
    explicits = [cross_link.findall(e)[0][1:-1] for e in explicits]
    candidates = [c.replace("\n", " ")[1:-1] for c in cross_link.findall(text)]
    cross_links = []
    for c in candidates:
        if c in explicits: continue
        if len(c) < 4: continue
        if c.endswith(".com]"): continue
        if any([ch in c for ch in """,<'"()$%/"""]): continue
        cross_links.append(c)
    unresolved = [cl for cl in cross_links if cl not in titles]
    if unresolved:
        error_reporter(f"""Unresolved cross-links:
        {pprint.pformat(unresolved)}""")


### Make sure functions use parentheses, not 'function'

def validate_function_descriptions(text, error_reporter):
    func_descriptions = re.findall("`[^(`]+?`\s+function", text) + re.findall("function\s+`[^(`]+?`", text)
    if func_descriptions:
        err_msg = "Function descriptions missing '()':\n"
        for f in func_descriptions:
            f = f.replace("\n", " ").strip()
            err_msg += f"\t{f}\n"
        error_reporter(err_msg.strip())


### Punctuation inside quotes

def validate_punctuation_inside_quotes(text, error_reporter):
    text = re.sub("```(.*?)\n(.*?)\n```", "", text, flags=re.DOTALL)
    text = re.sub("`.*?`", "", text, flags=re.DOTALL)
    outside_commas = re.findall("\",", text)
    if outside_commas:
        error_reporter("commas outside quotes")
    outside_periods = re.findall("\"\.", text)
    if outside_periods:
        error_reporter("periods outside quotes")


### Capture all defined validators

# validators = [v for v in globals() if v.startswith("validate_")]
# pprint.pprint(validators)
