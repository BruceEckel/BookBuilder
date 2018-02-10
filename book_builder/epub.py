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
