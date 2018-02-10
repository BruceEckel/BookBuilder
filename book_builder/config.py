"""
Common program configuration variables for Book Builder. You must create
a 'settings.config' file in the base directory of each different book; see
README.md.
"""
import os
import sys
from pathlib import Path


def settings_path():
    """
    Starts wherever bb is invoked and climbs up the directory path
    looking for settings.config
    """
    this = Path.cwd()
    root = this.root
    while True:
        config = this / "settings.config"
        if config.exists():
            return config
        this = this.parent
        if this.samefile(root):
            print(
                "ERROR: You must put a 'settings.config' in your book repo base directory")
            sys.exit(1)

# Add elements from settings.config into this environment:
exec(settings_path().read_text())


root_name = base_name.lower()

epub_file_name = base_name + ".epub"
epub_sample_file_name = base_name + "-Sample.epub"
epub_mono_file_name = base_name + "-monochrome.epub"
epub_sample_mono_file_name = base_name + "-monochrome-Sample.epub"

mobi_file_name = base_name + ".mobi"
mobi_sample_file_name = base_name + "-Sample.mobi"
mobi_mono_file_name = base_name + "-monochrome.mobi"
mobi_sample_mono_file_name = base_name + "-monochrome-Sample.mobi"

tools_dir = Path(__file__).parent.parent.resolve()
root_path = tools_dir.parent / base_name
bb_code_dir = tools_dir / "book_builder"
markdown_dir = root_path / "Markdown"
example_dir = extracted_examples / "Examples"
exclude_dir = extracted_examples / "ExcludedExamples"

epub_build_dir = root_path / "epub_build"
mobi_build_dir = root_path / "mobi_build"
html_dir = epub_build_dir / "html"
images_dir = epub_build_dir / "images"
test_dir = root_path / "test"

release_dir = root_path / "Release"

def epub_file(fileid): return epub_build_dir / f"{root_name}-{fileid}.md"

combined_markdown = epub_file("assembled")
stripped_markdown = epub_file("assembled-stripped")
combined_markdown_html = epub_file("assembled-html")
combined_markdown_pdf = epub_file("assembled-pdf")

sample_markdown = epub_file("sample")
sample_markdown_html = epub_file("sample-html")
sample_markdown_pdf = epub_file("sample-pdf")

stripped_for_style = epub_file("stripped-for-style")
stripped_for_spelling = epub_file("stripped-for-spelling")

# recent_atom_names = bb_code_dir / "recent_atom_names.py"

ebookResources = root_path / "resources"
images = ebookResources / "images"
fonts = ebookResources / "fonts"
bullets = ebookResources / "bullets"
cover = ebookResources / "cover" / "Cover.png"
css = ebookResources / (root_name + ".css")
metadata = ebookResources / "metadata.yaml"
meta_inf = ebookResources / "META-INF"

reformat_dir = root_path / "Reformatted"

sample_book_dir = root_path / "SampleBook"
sample_book_original_dir = root_path / "SampleBook" / "Original"
combined_markdown_sample = sample_book_dir / (root_name + "-assembled.md")
