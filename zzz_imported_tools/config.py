"""
Common program configuration variables for "Atomic Kotlin" tools
"""
from pathlib import Path
import sys

ebookName = "AtomicKotlin"
epubName = ebookName + ".epub"
code_width = 60

tools_dir = Path(sys.path[0])
rootPath = tools_dir.parent

test_dir = rootPath / "test"

markdown_dir = rootPath / "Markdown"
img_dir = markdown_dir / "images"
build_dir = rootPath / "ebook_build"
html_dir = build_dir / "html"
epub_dir = build_dir / "epub_files"
examples_dir = rootPath / "Examples"

# docm = rootPath / "AtomicKotlin.docx"
ebookBuildPath = rootPath / "ebook_build"
html = ebookBuildPath / (ebookName + ".html")
ebookResources = rootPath / "resources"
css = ebookResources / (ebookName + ".css")
fonts = ebookResources / "fonts"
cover = ebookResources / "cover" / "Cover.jpg"
example_path = rootPath / "ExtractedExamples"
tablepath = ebookBuildPath / "tables"
markdown_source = rootPath / (ebookName + ".md")

combined_markdown = build_dir / (ebookName + "-assembled.md")

