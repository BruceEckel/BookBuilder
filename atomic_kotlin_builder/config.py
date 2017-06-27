"""
Common program configuration variables for Atomic Kotlin Builder
"""
import os
import sys
from pathlib import Path

base_name = "AtomicKotlin"
epub_file_name = base_name + ".epub"
epub_sample_file_name = base_name + "Sample.epub"

code_width = 56

try:
    tools_dir = Path(os.environ['ATOMIC_KOTLIN_BUILDER'])
except:
    print("Error: need to set ATOMIC_KOTLIN_BUILDER")
    sys.exit(1)

root_path = tools_dir.parent / "AtomicKotlin"
akb_code_dir = tools_dir / "atomic_kotlin_builder"
markdown_dir = root_path / "Markdown"
example_dir = root_path / "ExtractedExamples"

ebook_build_dir = root_path / "ebook_build"
html_dir = ebook_build_dir / "html"
images_dir = ebook_build_dir / "images"
test_dir = root_path / "test"

combined_markdown = ebook_build_dir / "atomickotlin-assembled.md"
combined_markdown_html = ebook_build_dir / "atomickotlin-assembled-html.md"
combined_markdown_pdf = ebook_build_dir / "atomickotlin-assembled-pdf.md"
stripped_for_style = ebook_build_dir / "atomickotlin-stripped-for-style.md"
stripped_for_spelling = ebook_build_dir / \
    "atomickotlin-stripped-for-spelling.md"
kotlin_code_only = ebook_build_dir / "atomickotlin-kotlin-code-only.md"
kotlin_comments_only = ebook_build_dir / "atomickotlin-kotlin-comments-only.md"

recent_atom_names = akb_code_dir / "recent_atom_names.py"

ebookResources = root_path / "resources"
images = ebookResources / "images"
fonts = ebookResources / "fonts"
cover = ebookResources / "cover.jpg"
css = ebookResources / "atomickotlin.css"
metadata = ebookResources / "metadata.yaml"

reformat_dir = root_path / "Reformatted"

sample_book_dir = root_path / "SampleBook"
sample_book_original_dir = root_path / "SampleBook" / "Original"
combined_markdown_sample = sample_book_dir / "atomickotlin-assembled.md"
