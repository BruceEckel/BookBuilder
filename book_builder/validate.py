"""
Validation test framework and checks
"""
import re
import os
import sys
import shutil
import pprint
from pathlib import Path
import book_builder.config as config
from book_builder.util import create_markdown_filename
from book_builder.util import clean
def trace(_): pass
# def trace(msg): print(msg)
misspellings = set()


class ErrorReporter:
    """
    Pass into functions to capture errors in Markdown files.
    Used by validate.py
    """
    def __init__(self, md_path):
        self.md_path = md_path
        self.titled = False
        self.msg = ""
        self.line_number = None

    def __call__(self, msg, line_number = None):
        if not self.titled:
            self.msg += self.md_path.name + "\n"
            self.titled = True # Print only once
        self.msg += f"    {msg}\n"
        if line_number:
            self.line_number = line_number
        return self.msg

    def show(self):
        if self.msg:
            print(self.msg)

    def edit(self):
        if self.msg:
            if self.line_number:
                os.system(f"{config.editor} {self.md_path}:{self.line_number}")
            else:
                os.system(f"{config.editor} {self.md_path}")


class ExclusionFile:
    "Maintains the exclusion file for a particular validate function"
    ef_names = {}
    def __init__(self, exclusion_file_name, error_reporter):
        if exclusion_file_name not in ExclusionFile.ef_names:
            ExclusionFile.ef_names[exclusion_file_name] = "False" # Not reported
        self.needs_edit = False
        self.ef_path = config.data_path / exclusion_file_name
        self.error_reporter = error_reporter
        if not self.ef_path.exists():
            self.ef_path.write_text("")
        self.exclusions = self.ef_path.read_text()
        if config.msgbreak in self.exclusions and not ExclusionFile.ef_names[exclusion_file_name]:
            ExclusionFile.ef_names[exclusion_file_name] = True
            print(f"{self.ef_path.name} Needs Editing!")
            os.system(f"{config.editor} {self.ef_path}")
            # sys.exit()

    def __call__(self, msg):
        with open(self.ef_path, "a") as ef:
            ef.write(f"{self.error_reporter.md_path.name}:\n")
            ef.write(f"    {msg}\n")
            ef.write(config.msgbreak + "\n")
        os.system(f"{config.editor} {self.ef_path}")

    def __contains__(self, item):
        return item in self.exclusions

    def __iter__(self):
        return self.exclusions.splitlines().__iter__()


def all_checks():
    "Multiple tests to find problems in the book"
    print(f"Validating {config.markdown_dir}")
    assert config.markdown_dir.exists(), f"Cannot find {config.markdown_dir}"
    g = dict(sorted(globals().items()))
    validators = [g[v] for v in g if v.startswith("validate_")]
    for md in config.markdown_dir.glob("[0-9]*_*.md"):
        # print(md.name)
        error_reporter = ErrorReporter(md)
        text = md.read_text(encoding="UTF-8")
        for val in validators:
            trace(f"{val.__name__}")
            val(text, error_reporter)
        error_reporter.show()
        error_reporter.edit()

    if misspellings:
        Path(config.all_misspelled).write_text("\n".join(sorted(misspellings)))
        os.system(f"{config.editor} {config.all_misspelled}")
        os.system(f"{config.editor} {config.supplemental_dictionary}")


#################################################################
############## Individual validation functions ##################
#################################################################


### Ensure there's no gap between ``` and language_name


def validate_tag_no_gap(text, error_reporter):
    if re.search(f"``` +{config.language_name}", text):
        error_reporter(f"Contains spaces between ``` and {config.language_name}")


### Check for code fragments that should be turned into examples

slugline = re.compile(f"^// .+?\.{config.code_ext}$", re.MULTILINE)

def examples_without_sluglines(text, exclusions):
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
    return False


def validate_complete_examples(text, error_reporter):
    exclusions = ExclusionFile("validate_complete_examples.txt", error_reporter)
    noslug = examples_without_sluglines(text, exclusions)
    if noslug:
        error_reporter(f"Contains compileable example(s) without a slugline:\n{noslug}")


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
    exclusions = config.comment_capitalization_exclusions.read_text()
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

def validate_example_sluglines(text, error_reporter):
    exclusions = ExclusionFile("validate_example_sluglines.txt", error_reporter)
    for listing in extract_listings(text):
        lines = listing.splitlines()
        slug = lines[0]
        if not slug.startswith(config.start_comment):
            continue # Improper code fragments caught elsewhere
        if not slug.startswith(config.start_comment + " "):
            error_reporter(f"Bad first line (no space after beginning of comment):\n\t{slug}")
            continue
        slug = slug.split(None, 1)[1]
        if "/" not in slug and slug not in exclusions:
            exclusions(error_reporter(f"Missing directory in:\n{slug}"))


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

single_tick_dictionary = set(Path(
    config.root_path / "data" / "single_tick_dictionary.txt")
    .read_text().splitlines())

def remove_nonletters(text):
    for rch in "\"'\\/_`?$|#@(){}[]<>:;.,=!-+*%&0123456789":
        text = text.replace(rch, " ")
    return text.strip()


def strip_comments_from_code(listing, error_reporter):
    if len(listing.strip()) == 0:
        error_reporter("Empty listing")
        return []
    listing = re.sub("/\*.*?\*/", "", listing, flags=re.DOTALL)
    if len(listing.strip()) == 0:
        return []
    lines = listing.splitlines()
    if lines[0].startswith("//"): # Retain elements of slugline
        lines[0] = lines[0][3:]
    lines = [line.split("//")[0].rstrip() for line in lines]
    words = []
    for line in lines:
        words += [word for word in remove_nonletters(line).split()]
    return words

### Temporarily disabled:
def _validate_ticked_phrases(text, error_reporter):
    exclusions = ExclusionFile("validate_ticked_phrases.txt", error_reporter)
    stripped_listings = [strip_comments_from_code(listing, error_reporter)
        for listing in extract_listings(text)]
    pieces = {item for sublist in stripped_listings for item in sublist} # Flatten list
    # pieces = pieces.union(single_tick_dictionary)
    pieces = pieces.union(exclusions)
    raw_single_ticks = [t for t in re.findall("`.+?`", text) if t != "```"]
    single_ticks = [remove_nonletters(t[1:-1]).split() for t in raw_single_ticks]
    single_ticks = {item for sublist in single_ticks for item in sublist} # Flatten list
    not_in_examples = single_ticks.difference(pieces)
    if not_in_examples:
        err_msg = ""
        for nie in not_in_examples:
            if nie in exclusions:
                continue
            err_msg += f"Not in examples: {nie}\n"
            for rst in raw_single_ticks:
                if nie in rst:
                    exclusions(nie)
                    err_msg += f"\t{rst}\n"
        error_reporter(err_msg)


### Spell-check everything

dictionary = set(config.dictionary.read_text().splitlines()).union(
    set(config.supplemental_dictionary.read_text().splitlines()))

def validate_full_spellcheck(text, error_reporter):
    words = set(re.split("(?:(?:[^a-zA-Z]+')|(?:'[^a-zA-Z]+))|(?:[^a-zA-Z']+)", text))
    misspelled = words - dictionary
    if '' in misspelled:
        misspelled.remove('')
    if len(misspelled):
        global misspellings
        misspellings = misspellings.union(misspelled)
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


def remove_listings(text):
    return re.sub("```(.*?)\n(.*?)\n```", "", text, flags=re.DOTALL)


def validate_cross_links(text, error_reporter):
    text = remove_listings(text)
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
    func_descriptions = \
        re.findall("`[^(`]+?`\s+function", text) + \
        re.findall("function\s+`[^(`]+?`", text)
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

### Check for bad characters:

bad_chars = ['’']

def validate_characters(text, error_reporter):
    for n, line in enumerate(text.splitlines()):
        if any([bad_char in line for bad_char in bad_chars]):
            error_reporter(f"line {n} contains bad character:\n{line}")


### Test files individually to find problem characters

def pandoc_test(md):
    command = (
        f"pandoc {md.name}"
        f" -t epub3 -o {md.stem}.epub"
        " -f markdown-native_divs "
        " -f markdown+smart "
        f'--metadata title="TEST"')
    print(md.name)
    os.system(command)

def test_markdown_individually():
    clean(config.test_dir)
    config.test_dir.mkdir()
    for md in config.markdown_dir.glob("*.md"):
        shutil.copy(md, config.test_dir)
    os.chdir(config.test_dir)
    files = sorted(list(Path().glob("*.md")))
    pprint.pprint(files)
    with open('combined.md', 'w') as combined:
        for f in files:
            combined.write(f.read_text() + "\n")
    pandoc_test(Path('combined.md'))


### Test files individually to find problem characters

def validate_mistaken_backquotes(text, error_reporter):
    "Discover when backquotes are messed up by paragraph reformatting"
    if not config.mistaken_backquote_exclusions.exists():
        config.mistaken_backquote_exclusions.write_text("")
    exclusions = config.mistaken_backquote_exclusions.read_text()
    if config.msgbreak in exclusions:
        print(f"{config.mistaken_backquote_exclusions.name} Needs Editing!")
        os.system(f"{config.editor} {config.mistaken_backquote_exclusions}")
        sys.exit()
    lines = remove_listings(text).splitlines()
    for n, line in enumerate(lines):
        if n+1 >= len(lines):
            break
        if line.startswith("`") and lines[n+1].startswith("`"):
            if line in exclusions and lines[n+1] in exclusions:
                continue
            error_reporter(f"{config.msgbreak}\nPotential error on line {n}:\n{line}\n{lines[n+1]}\n")
            with open(config.mistaken_backquote_exclusions, "a") as mbe:
                mbe.write(error_reporter.msg)
            os.system(f"{config.editor} {config.mistaken_backquote_exclusions}")


### Test for println() without /* Output:

OK = ["/* Output:", "/* Sample output:", "/* Input/Output:"]

def validate_println_output(text, error_reporter):
    exclusions = ExclusionFile("validate_println_output.txt", error_reporter)
    lines = text.splitlines()
    for listing in re.findall("```kotlin(.*?)```", text, flags=re.DOTALL):
        slug = listing.strip().splitlines()[0]
        if "println" in listing and not any([ok in listing for ok in OK]):
            if slug in exclusions:
                continue # Next listing
            for n, line in enumerate(lines):
                if slug in line:
                    exclusions(error_reporter(f"println without /* Output:\n{slug}\n", n))
                    break
