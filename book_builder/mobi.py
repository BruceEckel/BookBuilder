"""
Tool to create MOBIs
"""
import os
from pathlib import Path
import book_builder.config as config
from book_builder.util import regenerate_ebook_build_dir, combine_markdown_files
from book_builder.util import combine_sample_markdown, pandoc_epub_command


def convert_to_mobi():
    """
    Pandoc markdown to mobi
    NOTE: Need to create our own EPUBs first in this directory,
    so as to use the special AtomicKotlin-mobi.css
    """
    return "Incomplete"
    regenerate_ebook_build_dir(config.mobi_build_dir)
    combine_markdown_files(config.stripped_markdown, config.mobi_build_dir, strip_notes=True)
    combine_sample_markdown(config.sample_markdown, config.mobi_build_dir)
    os.chdir(str(config.mobi_build_dir))
    pandoc_epub_command(
        config.stripped_markdown,
        config.mobi_file_name,
        config.title)
    pandoc_epub_command(
        config.sample_markdown,
        config.mobi_sample_file_name,
        config.title + " Sample")
    pandoc_epub_command(
        config.stripped_markdown,
        config.mobi_mono_file_name,
        config.title,
        highlighting="monochrome")
    pandoc_epub_command(
        config.sample_markdown,
        config.mobi_sample_mono_file_name,
        config.title + " Sample",
        highlighting="monochrome")
    os.chdir(str(config.release_dir))
    for epf in Path('.').glob("*.epub"):
        os.system(f"kindlegen {epf.name}")
