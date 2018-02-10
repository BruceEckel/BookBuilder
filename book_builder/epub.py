#! py -3
# Tools to create EPUBs
import os
import pprint
import re
from pathlib import Path
from collections import OrderedDict
import zipfile
# import difflib
import book_builder.config as config
from book_builder.util import *


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
    regenerate_ebook_build_dir(config.epub_build_dir)
    combine_markdown_files(config.stripped_markdown, strip_notes = True)
    combine_sample_markdown(config.sample_markdown)
    os.chdir(str(config.epub_build_dir))
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
    regenerate_ebook_build_dir(config.epub_build_dir)
    combine_markdown_files(config.stripped_markdown, strip_notes = True)
    os.chdir(str(config.epub_build_dir))
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
    [ os.system(f"cp {config.epub_build_dir / src} {release_dir}") for src in books + samples ]
    os.chdir(str(release_dir))
    [ os.system(f"kindlegen {epf}") for epf in books + samples ]
    def zzip(target_name, file_list):
        os.system(f"zip {target_name}.zip {' '.join(file_list)}")
    zzip(config.base_name, books + [b[:-4] + "mobi" for b in books])
    zzip(config.base_name + "Sample", samples + [b[:-4] + "mobi" for b in samples])
