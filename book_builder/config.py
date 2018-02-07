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


exec(settings_path().read_text())
# if 'comment_capitalization_OK' in globals():
#     comment_capitalization_OK = comment_capitalization_OK.strip().splitlines()
#     print(comment_capitalization_OK)

root_name = base_name.lower()

epub_file_name = base_name + ".epub"
epub_sample_file_name = base_name + "-Sample.epub"
epub_mono_file_name = base_name + "-monochrome.epub"
epub_sample_mono_file_name = base_name + "-monochrome-Sample.epub"


tools_dir = Path(__file__).parent.parent.resolve()
root_path = tools_dir.parent / base_name
bb_code_dir = tools_dir / "book_builder"
markdown_dir = root_path / "Markdown"
example_dir = extracted_examples / "Examples"
exclude_dir = extracted_examples / "ExcludedExamples"

ebook_build_dir = root_path / "ebook_build"
html_dir = ebook_build_dir / "html"
images_dir = ebook_build_dir / "images"
test_dir = root_path / "test"

def ebook_file(fileid): return ebook_build_dir / f"{root_name}-{fileid}.md"

combined_markdown = ebook_file("assembled")
stripped_markdown = ebook_file("assembled-stripped")
combined_markdown_html = ebook_file("assembled-html")
combined_markdown_pdf = ebook_file("assembled-pdf")

sample_markdown = ebook_file("sample")
sample_markdown_html = ebook_file("sample-html")
sample_markdown_pdf = ebook_file("sample-pdf")

stripped_for_style = ebook_file("stripped-for-style")
stripped_for_spelling = ebook_file("stripped-for-spelling")

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
