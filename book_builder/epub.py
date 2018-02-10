#! py -3
# Tools to create EPUBs
import os
import pprint
import re
from pathlib import Path
from collections import OrderedDict
import zipfile
import book_builder.config as config
from book_builder.config import epub_md, epub
from book_builder.util import *


def fix_for_apple(epub_name):
    epub = zipfile.ZipFile(epub_name, "a")
    epub.write(config.meta_inf, "META-INF")
    epub.close()


def convert_to_epub():
    """
    Pandoc markdown to epub
    """
    regenerate_ebook_build_dir(config.epub_build_dir)
    combine_markdown_files(epub_md("assembled-stripped"), strip_notes = True)
    combine_sample_markdown(epub_md("sample"))
    os.chdir(str(config.epub_build_dir))
    pandoc_epub_command(
        epub_md("assembled-stripped"),
        epub(),
        config.title)
    pandoc_epub_command(
        epub_md("sample"),
        epub("-Sample"),
        config.title + " Sample")
    pandoc_epub_command(
        epub_md("assembled-stripped"),
        epub("-monochrome"),
        config.title,
        highlighting="monochrome")
    pandoc_epub_command(
        epub_md("sample"),
        epub("-monochrome-Sample"),
        config.title + " Sample",
        highlighting="monochrome")
    fix_for_apple(epub())
    fix_for_apple(epub("-Sample"))
