#! py -3
# Tools to create MOBIs
import os
import book_builder.config as config
from book_builder.util import *


def convert_to_mobi():
    """
    Pandoc markdown to mobi
    """
    regenerate_ebook_build_dir(config.mobi_build_dir)
    combine_markdown_files(config.stripped_markdown, strip_notes = True)
    combine_sample_markdown(config.sample_markdown)
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
