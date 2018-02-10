"""
Tool to create MOBIs
"""
import os
from pathlib import Path
import book_builder.config as config
from book_builder.util import regenerate_ebook_build_dir, combine_markdown_files
from book_builder.util import combine_sample_markdown, pandoc_epub_command
from book_builder.config import mobi_md, mobi


def convert_to_mobi():
    """
    Pandoc markdown to mobi
    NOTE: Need to create our own EPUBs first in this directory,
    so as to use the special AtomicKotlin-mobi.css
    """
    regenerate_ebook_build_dir(config.mobi_build_dir)
    combine_markdown_files(mobi_md("assembled-stripped"), strip_notes = True)
    combine_sample_markdown(mobi_md("sample"))
    os.chdir(str(config.mobi_build_dir))
    pandoc_epub_command(
        mobi_md("assembled-stripped"),
        mobi(),
        config.title)
    pandoc_epub_command(
        mobi_md("sample"),
        mobi("-Sample"),
        config.title + " Sample")
    pandoc_epub_command(
        mobi_md("assembled-stripped"),
        mobi("-monochrome"),
        config.title,
        highlighting="monochrome")
    pandoc_epub_command(
        mobi_md("sample"),
        mobi("-monochrome-Sample"),
        config.title + " Sample",
        highlighting="monochrome")
    # for epf in Path('.').glob("*.epub"):
    #     os.system(f"kindlegen {epf.name}")
