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


def convert_to_docx():
    """
    Pandoc markdown to docx
    """
    regenerate_ebook_build_dir(config.epub_build_dir)
    combine_markdown_files(config.stripped_markdown, strip_notes = True)
    os.chdir(str(config.epub_build_dir))
    cmd = pandoc_docx_command(
        config.stripped_markdown, config.base_name + ".docx", config.title)

