"""
Common program configuration variables for Book Builder. You must create
a 'configuration.py' file in the base directory of each different book; see
README.md.
"""
import os
import sys
from pathlib import Path
from enum import Enum, unique
import importlib
# Add elements from configuration.py into this environment:
sys.path.append(str(Path(os.environ['BOOK_PROJECT_HOME'])))
from configuration import *


@unique
class BookType(Enum):
    EPUB = "epub"
    MOBI = "mobi"
    DOCX = "docx"


root_name = base_name.lower()

def epub_name(tag=""): return f"{base_name}{tag}.epub"
def mobi_name(tag=""): return f"{base_name}{tag}.mobi"

tools_dir = Path(__file__).parent.parent.resolve()
root_path = tools_dir.parent / base_name
bb_code_dir = tools_dir / "book_builder"
markdown_dir = root_path / "Markdown"
example_dir = extracted_examples / "Examples"
exclude_dir = extracted_examples / "ExcludedExamples"

epub_build_dir = root_path / "build"/ "epub"
mobi_build_dir = root_path / "build"/ "mobi"
docx_build_dir = root_path / "build"/ "docx"
release_dir    = root_path / "build"/ "Release"

html_dir = epub_build_dir / "html"
# images_dir = epub_build_dir / "images"
test_dir = root_path / "test"

def epub_md(fileid): return epub_build_dir / f"{root_name}-{fileid}.md"
def mobi_md(fileid): return mobi_build_dir / f"{root_name}-{fileid}.md"
def docx_md(fileid): return docx_build_dir / f"{root_name}-{fileid}.md"

combined_markdown = epub_md("assembled")
sample_markdown = epub_md("sample")
# recent_atom_names = bb_code_dir / "recent_atom_names.py"

ebookResources = root_path / "resources"
images = ebookResources / "images"
fonts = ebookResources / "fonts"
bullets = ebookResources / "bullets"
cover = ebookResources / "cover" / "Cover.png"
epub_css = ebookResources / (root_name + "-epub.css")
mobi_css = ebookResources / (root_name + "-mobi.css")
metadata = ebookResources / "metadata.yaml"
meta_inf = ebookResources / "META-INF"

reformat_dir = root_path / "Reformatted"

sample_book_dir = root_path / "SampleBook"
sample_book_original_dir = root_path / "SampleBook" / "Original"
combined_markdown_sample = sample_book_dir / (root_name + "-assembled.md")
