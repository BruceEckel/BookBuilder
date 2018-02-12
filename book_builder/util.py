"""
Utilities for BookBuilder
"""
import shutil
import sys
import os
import re
import time
from pathlib import Path
from distutils.dir_util import copy_tree
from collections import OrderedDict
import textwrap
import pprint
import book_builder.config as config
from book_builder.config import BookType


class ErrorReporter:
    """
    Pass into functions to capture errors in Markdown files.
    Used by validate.py
    """
    def __init__(self, md_path):
        self.md_path = md_path
        self.titled = False
        self.msg = ""

    def __call__(self, msg):
        if not self.titled:
            self.msg += self.md_path.name + "\n"
            self.titled = True # Print only once
        self.msg += f"    {msg}"

    def show(self):
        if self.msg:
            print(self.msg)

    def edit(self):
        if self.msg:
            os.system(f"subl {self.md_path}")



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
    return "%03d_" % n + create_markdown_filename(h1)


def clean(dir_to_remove):
    "Remove directory"
    try:
        if dir_to_remove.exists():
            shutil.rmtree(str(dir_to_remove))
            return f"Removed: {dir_to_remove}"
        return f"Doesn't exist: {dir_to_remove}"
    except Exception as e:
        print(f"""Removal failed: {dir_to_remove}
        Are you inside that directory, or using a file inside it?
        """)
        print(e)


def regenerate_ebook_build_dir(ebook_build_dir, ebook_type: BookType = BookType.EPUB):
    clean(ebook_build_dir)
    time.sleep(1)
    os.makedirs(ebook_build_dir)
    def copy(src):
        source = Path(src)
        assert source.exists()
        shutil.copy(src, ebook_build_dir)
        assert (Path(ebook_build_dir) / source.name).exists()
    for font in config.fonts.glob("*"):
        copy(font)
    for bullet in config.bullets.glob("*"):
        copy(bullet)
    copy(config.cover)
    if ebook_type == BookType.EPUB:
        copy(config.epub_css)
    elif ebook_type == BookType.MOBI:
        copy(config.mobi_css)
        copy(config.mobi_mono_css)
    copy_tree(str(config.images), str(ebook_build_dir / "images"))
    # copy(config.metadata)


def strip_chapter(chapter_text):
    "Remove blank newlines at beginning and end, right-hand spaces on lines"
    chapter_text = chapter_text.strip()
    lines = [line.rstrip() for line in chapter_text.splitlines()]
    stripped = "\n".join(lines)
    return stripped.strip() # In case the previous line adds another newline


def strip_review_notes(target):
    lines = target.read_text().strip().splitlines()
    review = [x for x in lines if x.startswith("+ [")]
    mistakes = [x for x in review if not "Ready for Review" in x and not "Tech Checked" in x]
    assert not mistakes, mistakes
    result = [x.rstrip() for x in lines if not x.startswith("+ [")]
    result2 = ""
    in_notes = False
    for line in result:
        if line.startswith("+ Notes:"):
            in_notes = True
        if in_notes and len(line) == 0:
            in_notes = False
        if not in_notes:
            result2 += line + "\n"
    result3 = re.sub("{{.*?}}", "", result2, flags=re.DOTALL)
    target.write_text(result3 + "\n")


def combine_markdown_files(target, strip_notes=False):
    """
    Put markdown files together
    """
    if not target.parent.exists():
        os.makedirs(target.parent)
    files = sorted(list(config.markdown_dir.glob("*.md")))
    with open(target, 'w') as assembled:
        for f in files:
            assembled.write(f.read_text() + "\n\n")
    if strip_notes:
        strip_review_notes(target)
    return f"{target.name} Created"


def combine_sample_markdown(target):
    """
    Build markdown file for free sample
    """
    def extract(md, title_only=False):
        with md.open(encoding="utf8") as chapter:
            content = chapter.read().strip()
            if title_only:
                return ("\n".join(content.splitlines()[:3])).strip() + "\n\n"
            return content + "\n\n"

    if not target.parent.exists():
        os.makedirs(target.parent)
    assembled = ""
    atoms = [md for md in config.markdown_dir.glob("*.md")]
    for content in atoms[:config.sample_size + 1]:
        assembled += extract(content)
    for title_only in atoms[config.sample_size + 1:]:
        assembled += extract(title_only, True)
        assembled += "(Not included in sample)\n\n"
    with target.open('w', encoding="utf8") as book:
        book.write(assembled)
    strip_review_notes(target)
    return f"{target.name} Created"


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
    # import book_builder.recent_atom_names
    # old_names = set(book_builder.recent_atom_names.anames)
    # new_names = {create_markdown_filename(nm)[:-3] for nm in names}
    # new_names.add("Front")
    # diff = old_names.difference(new_names)
    # if diff:
    #     print("Old names not in new names:")
    #     for d in diff:
    #         print("   {}".format(d))
    #     print("---- Near matches: ----")
    #     for d in diff:
    #         print("{}: {}".format(d, difflib.get_close_matches(d, new_names)))
    #     return "Disassembly failed"

    # Notify if the number of chapters are different
    # len_old_names = len(book_builder.recent_atom_names.anames)
    # len_new_names = len(names) + 1  # for Front
    # if len_old_names != len_new_names:
    #     print("Number of old names: {}".format(len_old_names))
    #     print("Number of new names: {}".format(len_new_names))

    if not target_dir.exists():
        target_dir.mkdir()
    for i, p in enumerate(chaps):
        disassembled_file_name = create_numbered_markdown_filename(p, i)
        print(disassembled_file_name)
        dest = target_dir / disassembled_file_name
        with dest.open('w', encoding="utf8") as chp:
            if p != "Front":
                chp.write(p + "\n")
                chp.write("=" * len(p) + "\n\n")
            chp.write(strip_chapter(chaps[p]) + "\n")
    if target_dir != config.markdown_dir:
        print("now run 'diff -r Markdown test'")
    return "Successfully disassembled combined Markdown"


def check_for_existence(extension):
    files_with_extension = list(config.example_dir.rglob(extension))
    if len(files_with_extension) < 1:
        print("Error: no " + extension + " files found")
        sys.exit(1)
    return files_with_extension


def find_end(text_lines, n):
    """
    n is the index of the code listing title line,
    searches for closing ``` and returns that index
    """
    for i, line in enumerate(text_lines[n:]):
        if line.rstrip() == "```":
            return n + i
        if line.rstrip() == f"```{config.language_name}":
            assert False, f"```{config.language_name} before closing ```"
    else:
        assert False, "closing ``` not found"


def replace_code_in_text(generated, text):
    """
    Returns 'text' after replacing code listing matching 'generated'
    Both generated and text are NOT lists, but normal chunks of text
    returns new_text, starting_index so an editor can be opened at that line
    """
    code_lines = generated.splitlines()
    title = code_lines[0].strip()
    assert title in text, f"{title} not in text"
    text_lines = text.splitlines()
    for n, line in enumerate(text_lines):
        if line.strip() == title:
            end = find_end(text_lines, n)
            # print(f"n: {n}, end: {end}")
            # pprint.pprint(text_lines[n:end])
            # print("=" * 60)
            # pprint.pprint(code_lines)
            # print("-" * 60)
            text_lines[n:end] = code_lines
            new_text = ("\n".join(text_lines)).strip()
            return new_text, n
    assert False, f"{title} not found in text"


def create_new_status_file():
    "Create STATUS.md"
    status_file = config.root_path / "STATUS.md"
    if status_file.exists():
        return "STATUS.md already exists; new one not created"
    md_files = sorted([md.name for md in config.markdown_dir.glob("[0-9][0-9]_*.md")])
    status = ""
    def checkbox(item):
        nonlocal status
        status += f"+ [ ] {item}\n"
    for md in md_files:
        status += f"#### {md}\n"
        checkbox("Examples Replaced")
        checkbox("Rewritten")
        checkbox("Tech Checked")
        status += "+ Notes:\n"
    status_file.write_text(status)


# Format output:
# (0) Do first/last lines before formatting to width
# (1) Combine output and error (if present) files
# (2) Format all output to width limit
# (3) Add closing '*/'


def adjust_lines(text):
    text = text.replace("\0", "NUL")
    lines = text.splitlines()
    slug = lines[0]
    if "(First and Last " in slug:
        num_of_lines = int(slug.split()[5])
        adjusted = lines[:num_of_lines + 1] +\
            ["...________...________...________...________..."] +\
            lines[-num_of_lines:]
        return "\n".join(adjusted)
    elif "(First " in slug:
        num_of_lines = int(slug.split()[3])
        adjusted = lines[:num_of_lines + 1] +\
            ["                  ..."]
        return "\n".join(adjusted)
    return text


def fill_to_width(text):
    result = ""
    for line in text.splitlines():
        result += textwrap.fill(line, width=config.code_width - 1) + "\n"
    return result.strip()


def reformat_runoutput_files():
    for outfile in check_for_existence("*.out"):
        output_file = outfile.with_suffix(f".{config.code_ext}")
        if output_file.exists():
            if "{VisuallyInspectOutput}" in output_file.read_text():  # Don't create p1 file
                print(f"{output_file.name} Excluded")
                continue
        out_text = adjust_lines(outfile.read_text())
        phase_1 = outfile.with_suffix(".p1")
        with phase_1.open('w') as phs1:
            phs1.write(fill_to_width(out_text) + "\n")
            errfile = outfile.with_suffix(".err")
            if errfile.exists():
                phs1.write("___[ Error Output ]___\n")
                phs1.write(fill_to_width(errfile.read_text()) + "\n")
            phs1.write("*/\n")
