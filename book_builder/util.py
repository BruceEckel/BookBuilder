"""
Utilities for BookBuilder
"""
import shutil
import sys
import os
import re
import time
from pathlib import Path
from typing import List
from distutils.dir_util import copy_tree
from collections import OrderedDict
import textwrap
import book_builder.config as config
from book_builder.config import BookType
import contextlib
import os


@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


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


def header_to_filename_map(dir_to_map: Path):
    """Produces mapping between header/crosslink strings and file name bases"""
    result = dict()
    for md in sorted(list(dir_to_map.glob("*.md"))):
        if "000_Front.md" in md.name or "00_Front.md" in md.name:
            continue
        header = md.read_text().splitlines()[0].strip()
        name_base = create_markdown_filename(header)[:-3]
        assert name_base in md.name
        result[header] = (name_base, md.stem)
    return result


def erase(dir_to_remove):
    """Remove directory"""
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


def retain_files(target_dir: Path, extensions: List[str]):
    """
    Delete all files except those with 'extensions'
    """
    all_ = set(target_dir.glob("*"))
    keep = {f for f in all_ for ext in extensions if f.name.endswith(ext)}
    remove = all_ - keep
    # for k in keep:
    #     print(k.name)
    for r in remove:
        if r.is_dir():
            erase(r)
        if r.is_file():
            r.unlink()


if __name__ == '__main__':
    retain_files(config.mobi_build_dir, ["mobi"])


def regenerate_ebook_build_dir(ebook_build_dir, ebook_type: BookType = BookType.EPUB):
    erase(ebook_build_dir)
    time.sleep(1)
    os.makedirs(ebook_build_dir)

    def copy(src):
        source = Path(src)
        assert source.exists()
        shutil.copy(src, ebook_build_dir)
        assert (Path(ebook_build_dir) / source.name).exists()

    for font in config.fonts.glob("*.ttf"):
        copy(font)
    for bullet in config.bullets.glob("*"):
        copy(bullet)
    copy(config.cover)
    if ebook_type == BookType.EPUB:
        copy(config.epub_css)
    elif ebook_type == BookType.MOBI:
        copy(config.mobi_css)
        copy(config.mobi_mono_css)
    elif ebook_type == BookType.HTML:
        copy(config.html_css)
        copy(config.html_pandoc_template)
        copy(config.banner)
        copy(config.favicon)
    dest_images = ebook_build_dir / "images"
    copy_tree(str(config.images), str(dest_images))
    for f in dest_images.rglob("*.graffle"):
        f.unlink()

    # copy(config.metadata)


def strip_chapter(chapter_text):
    """Remove blank newlines at beginning and end, right-hand spaces on lines"""
    chapter_text = chapter_text.strip()
    lines = [line.rstrip() for line in chapter_text.splitlines()]
    stripped = "\n".join(lines)
    return stripped.strip()  # In case the previous line adds another newline


def strip_review_notes(target: Path):
    lines = target.read_text().strip().splitlines()
    review = [x for x in lines if x.startswith("+ [")]
    mistakes = [
        x for x in review if not "Ready for Review" in x and not "Tech Checked" in x]
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


def copy_markdown_files(target_dir, strip_notes=False):
    """
    Copy markdown files to target directory
    """
    if not target_dir.exists():
        os.makedirs(target_dir)

    def copy(src):
        source = Path(src)
        assert source.exists()
        shutil.copy(src, target_dir)
        copied_file = Path(target_dir) / source.name
        assert copied_file.exists()
        if strip_notes:
            strip_review_notes(copied_file)
        return f"Created {copied_file.name}"

    return "\n".join([copy(file) for file in sorted(list(config.markdown_dir.glob("*.md")))])


def combine_markdown_files(target, strip_notes=False):
    """
    Put markdown files together and place result in target directory
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
    """Turn assembled markdown file into a collection of chapter-based files"""
    with Path(config.combined_markdown).open(encoding="utf8") as akmd:
        book = akmd.read()
    chapters = re.compile(r"\n(-?# .+?)\n")
    parts = chapters.split(book)
    names = parts[1::2]
    bodies = parts[0::2]
    chaps = OrderedDict()
    chaps["Front"] = bodies[0]
    for i, nm in enumerate(names):
        chaps[nm] = bodies[i + 1].strip() + "\n"
    if not target_dir.exists():
        target_dir.mkdir()
    for i, p in enumerate(chaps):
        name = p
        if "{#" in name:
            name = name.split("{#")[0].strip()
        if "#" in name:
            name = name.split(maxsplit=1)[1]
        disassembled_file_name = create_numbered_markdown_filename(name, i)
        print(f"{disassembled_file_name}")
        dest = target_dir / disassembled_file_name
        with dest.open('w', encoding="utf8") as chp:
            if p != "Front":
                chp.write(f"{p}\n\n")
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
    # import pprint
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
    """Create STATUS.md"""
    status_file = config.root_path / "STATUS.md"
    if status_file.exists():
        return "STATUS.md already exists; new one not created"
    md_files = sorted(
        [md.name for md in config.markdown_dir.glob("[0-9][0-9]_*.md")])
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
