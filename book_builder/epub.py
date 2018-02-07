#! py -3
# epub tools
import os
import pprint
import re
from pathlib import Path
from collections import OrderedDict
from itertools import chain
import zipfile
# import difflib

import book_builder.config as config
from book_builder.util import *


def regenerate_epub_build_dir():
    clean(config.ebook_build_dir)
    os.makedirs(config.ebook_build_dir)
    def copy(src):
        source = Path(src)
        assert source.exists()
        shutil.copy(src, config.ebook_build_dir)
        assert (Path(config.ebook_build_dir) / source.name).exists()
    [copy(font) for font in config.fonts.glob("*")]
    [copy(bullet) for bullet in config.bullets.glob("*")]
    copy(config.cover)
    copy(config.css)
    # copy(config.metadata)


def combine_markdown_files(target, strip_notes = False, trace=False):
    """
    Put markdown files together
    """
    if not config.ebook_build_dir.exists():
        os.makedirs(config.ebook_build_dir)
    assembled = ""
    atom_names = []
    for md in config.markdown_dir.glob("*.md"):
        aname = md.name[:-3]
        atom_names.append(aname.split('_', 1)[1])
        #print(str(md.name), end=", ")
        with md.open(encoding="utf8") as chapter:
            assembled += chapter.read() + "\n\n"
    if strip_notes:
        assembled = strip_review_notes(assembled)
    with target.open('w', encoding="utf8") as book:
        book.write(assembled)
    if trace:
        pprint.pprint(atom_names)
    # config.recent_atom_names.write_text(
    #     "anames = " + pprint.pformat(atom_names) + "\n")
    return f"{target.name} Created"


def combine_sample_markdown():
    """
    Build markdown file for free sample
    """
    def extract(md, title_only=False):
        with md.open(encoding="utf8") as chapter:
            content = chapter.read().strip()
            if title_only:
                return ("\n".join(content.splitlines()[:3])).strip() + "\n\n"
            return content + "\n\n"

    if not config.ebook_build_dir.exists():
        os.makedirs(config.ebook_build_dir)
    assembled = ""
    atoms = [md for md in config.markdown_dir.glob("*.md")]
    for content in atoms[:config.sample_size + 1]:
        assembled += extract(content)
    for title_only in atoms[config.sample_size + 1:]:
        assembled += extract(title_only, True)
        assembled += "(Not included in sample)\n\n"
    with config.sample_markdown.open('w', encoding="utf8") as book:
        book.write(strip_review_notes(assembled))
    return f"{config.sample_markdown.name} Created"


def strip_chapter(chapter_text):
    "Remove blank newlines at beginning and end, right-hand spaces on lines"
    chapter_text = chapter_text.strip()
    lines = [line.rstrip() for line in chapter_text.splitlines()]
    stripped = "\n".join(lines)
    return stripped.strip() # In case the previous line adds another newline


def strip_review_notes(text):
    lines = text.strip().splitlines()
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
    return result3 + "\n"



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
            if "Front" != p:
                chp.write(p + "\n")
                chp.write("=" * len(p) + "\n\n")
            chp.write(strip_chapter(chaps[p]) + "\n")
    if target_dir != config.markdown_dir:
        print("now run 'diff -r Markdown test'")
    return "Successfully disassembled combined Markdown"


def pandoc_epub_command(input_file, output_name, title, highlighting=None):
    "highlighting=None uses default (pygments) for source code color syntax highlighting"
    if not input_file.exists():
        return "Error: missing " + input_file.name
    command = (
        "pandoc " + str(input_file.name) +
        " -t epub3 -o " + output_name +
        " -f markdown-native_divs "
        " -f markdown+smart "
        """ --epub-subdirectory="" """
        " --epub-cover-image=Cover.png " +
        " ".join([f"--epub-embed-font={font.name}" for font in
          chain(config.bullets.glob("*"), config.fonts.glob("*")) ])
        + " --toc-depth=2 "
        f'--metadata title="{title}"'
        " --css=" + config.base_name + ".css ")
    if highlighting:
        command += f" --highlight-style={highlighting} "
    print(command)
    os.system(command)


def pandoc_docx_command(input_file, output_name, title):
    if not input_file.exists():
        return "Error: missing " + input_file.name
    command = (
        "pandoc " + str(input_file.name) +
        " -t docx -o " + output_name +
        " -f markdown-native_divs "
        " -f markdown+smart "
        " --toc-depth=2 " +
        f'--metadata title="{title}"' +
        " --css=" + config.base_name + ".css ")
    print(command)
    os.system(command)


def fix_for_apple(epub_name):
    epub = zipfile.ZipFile(epub_name, "a")
    epub.write(config.meta_inf, "META-INF")
    epub.close()


def convert_to_epub():
    """
    Pandoc markdown to epub
    """
    regenerate_epub_build_dir()
    combine_markdown_files(config.stripped_markdown, strip_notes = True)
    combine_sample_markdown()
    os.chdir(str(config.ebook_build_dir))
    pandoc_epub_command(
        config.stripped_markdown,
        config.epub_file_name,
        config.title)
    pandoc_epub_command(
        config.sample_markdown,
        config.epub_sample_file_name,
        config.title + " Sample")
    pandoc_epub_command(
        config.stripped_markdown,
        config.epub_mono_file_name,
        config.title,
        highlighting="monochrome")
    pandoc_epub_command(
        config.sample_markdown,
        config.epub_sample_mono_file_name,
        config.title + " Sample",
        highlighting="monochrome")
    fix_for_apple(config.epub_file_name)
    fix_for_apple(config.epub_sample_file_name)


def convert_to_docx():
    """
    Pandoc markdown to docx
    """
    regenerate_epub_build_dir()
    combine_markdown_files(config.stripped_markdown, strip_notes = True)
    os.chdir(str(config.ebook_build_dir))
    cmd = pandoc_docx_command(
        config.stripped_markdown, config.base_name + ".docx", config.title)
    print(cmd)
    os.system(cmd)


def create_release():
    books = [
        config.epub_file_name,
        config.epub_mono_file_name,
    ]
    samples = [
        config.epub_sample_file_name,
        config.epub_sample_mono_file_name,
    ]
    release_dir = config.root_path / "Release"
    if release_dir.exists():
        clean(release_dir)
    os.makedirs(release_dir)
    [ os.system(f"cp {config.ebook_build_dir / src} {release_dir}") for src in books + samples ]
    os.chdir(str(release_dir))
    [ os.system(f"kindlegen {epf}") for epf in books + samples ]
    def zzip(target_name, file_list):
        os.system(f"zip {target_name}.zip {' '.join(file_list)}")
    zzip(config.base_name, books + [b[:-4] + "mobi" for b in books])
    zzip(config.base_name + "Sample", samples + [b[:-4] + "mobi" for b in samples])
