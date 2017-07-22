"""
Common program configuration variables for Book Builder,
to target the Atomic Kotlin book. Each different book
will only differ by this configuration file, so you create
a different one for each book.
"""
import os
import sys
from pathlib import Path

base_name = "AtomicKotlin"
root_name = "atomickotlin"
language_name = "kotlin"

epub_file_name = base_name + ".epub"
epub_sample_file_name = base_name + "Sample.epub"

code_width = 56

tools_dir = Path(__file__).parent.parent.resolve()
root_path = tools_dir.parent / base_name
bb_code_dir = tools_dir / "book_builder"
markdown_dir = root_path / "Markdown"
example_dir = root_path / "ExtractedExamples"

ebook_build_dir = root_path / "ebook_build"
html_dir = ebook_build_dir / "html"
images_dir = ebook_build_dir / "images"
test_dir = root_path / "test"

combined_markdown = ebook_build_dir / (root_name +"-assembled.md")
combined_markdown_html = ebook_build_dir / (root_name +"-assembled-html.md")
combined_markdown_pdf = ebook_build_dir / (root_name +"-assembled-pdf.md")
stripped_for_style = ebook_build_dir / (root_name +"-stripped-for-style.md")
stripped_for_spelling = ebook_build_dir / \
    (root_name +"-stripped-for-spelling.md")
kotlin_code_only = ebook_build_dir / (root_name +"-" + language_name + "-code-only.md")
kotlin_comments_only = ebook_build_dir / (root_name +"-" + language_name + "-comments-only.md")

recent_atom_names = bb_code_dir / "recent_atom_names.py"

ebookResources = root_path / "resources"
images = ebookResources / "images"
fonts = ebookResources / "fonts"
cover = ebookResources / "cover.jpg"
css = ebookResources / (root_name +".css")
metadata = ebookResources / "metadata.yaml"

reformat_dir = root_path / "Reformatted"

sample_book_dir = root_path / "SampleBook"
sample_book_original_dir = root_path / "SampleBook" / "Original"
combined_markdown_sample = sample_book_dir / (root_name +"-assembled.md")
