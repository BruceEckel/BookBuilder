"""
Common program configuration variables for Book Builder. You must create
a 'configuration.py' file in the base directory of each different book; see
README.md.
"""
import os
import sys
from pathlib import Path
from enum import Enum, unique


def get_editor(id):
    """Here and not in util.py because of a circular import"""
    if id not in os.environ:
        print(
            f"To use a different editor, set the {id} environment variable to your favorite editor.")
        if id == 'CODE_EDITOR':
            print(f"Using VS Code by default for {id}")
            return "code"
        elif id == 'MD_EDITOR':
            print(f"Using Sublime by default for {id}")
            return "subl"
        else:
            assert False, f"Don't recognize {id}"
    return os.environ[id]


code_editor = get_editor('CODE_EDITOR')
md_editor = get_editor('MD_EDITOR')

# Defaults in configuration.py, to quiet python developer tools:
title = ""
base_name = ""
language_name = ""
code_ext = ""
code_width = ""
start_comment = ""
extracted_examples = ""
sample_size = ""
exclude_atoms = ""
web_sample_toc = ""
web_html_book = ""
end_of_sample = ""
copyright_notice = '&copy;2020 <a href="http://mindviewllc.com/">Mindview LLC</a>. All Rights Reserved.'

# Add elements from BookProject/configuration.py into this environment:
sys.path.insert(0, str(Path(os.environ['BOOK_PROJECT_HOME'])))
from configuration import *

msgbreak = '-=' * 25


@unique
class BookType(Enum):
    EPUB = "epub"
    MOBI = "mobi"
    MOBIMONO = "mobi-mono"
    DOCX = "docx"
    HTML = "html"

exercise_header = "***Exercises and solutions can be found at www.AtomicKotlin.com.***"

root_name = base_name.lower()
root_path = Path(os.environ['BOOK_PROJECT_HOME'])
markdown_dir = root_path / "Markdown"
example_dir = extracted_examples / "Examples"
exclude_dir = extracted_examples / "ExcludedExamples"
epub_build_dir = root_path / "build" / "epub"
mobi_build_dir = root_path / "build" / "mobi"
docx_build_dir = root_path / "build" / "docx"
html_sample_dir = root_path / "build" / "html_sample"
html_complete_dir = root_path / "build" / "html_complete"
html_stripped_dir = root_path / "build" / "html_stripped"
release_dir = root_path / "build" / "Release"
test_dir = root_path / "test"


def epub_md(fileid): return epub_build_dir / f"{root_name}-{fileid}.md"
def mobi_md(fileid): return mobi_build_dir / f"{root_name}-{fileid}.md"
def docx_md(fileid): return docx_build_dir / f"{root_name}-{fileid}.md"
# def html_md(fileid): return html_build_dir / f"{root_name}-{fileid}.md"
def epub_name(tag=""): return f"{base_name}{tag}.epub"
def mobi_name(tag=""): return f"{base_name}{tag}.mobi"


built_ebooks = [
    epub_build_dir / epub_name(),
    epub_build_dir / epub_name("-monochrome"),
    epub_build_dir / epub_name("-Sample"),
    epub_build_dir / epub_name("-monochrome-Sample"),
    mobi_build_dir / mobi_name(),
    mobi_build_dir / mobi_name("-monochrome"),
    mobi_build_dir / mobi_name("-Sample"),
    mobi_build_dir / mobi_name("-monochrome-Sample"),
]

combined_markdown = epub_md("assembled")
sample_markdown = epub_md("sample")


def resource(path): return root_path / "resources" / path


images = markdown_dir / "images"
fonts = resource("fonts")
bullets = resource("bullets")
cover = resource("cover") / "Cover.png"
banner = resource("cover") / "Banner.png"
favicon = resource("cover") / "favicon.ico"
html_css = resource(root_name + "-html.css")
html_pandoc_template = resource("pandoc-template.html")
epub_css = resource(root_name + "-epub.css")
mobi_css = resource(root_name + "-mobi.css")
mobi_mono_css = resource(root_name + "-mobi-mono.css")
metadata = resource("metadata.yaml")
meta_inf = resource("META-INF")
data_path = root_path / "data"

if __name__ == '__main__':
    "Test: see if identifiers are used in this project"
    from pprint import pprint
    exclude_names = [
        "__",
        "Enum",
        "unique",
        "new_class",
        "prepare_class",
        "coroutine",
        "exclude_names",
        "exclude_types",
        "resource",
        "root_name",
        "mobi_name",
    ]
    exclude_types = [
        "<class 'module'>",
        "<class 'type'>",
    ]
    g = dict(globals().items())
    identifiers = set()
    for k in g:
        if any([ex in k for ex in exclude_names]):
            continue
        if any([ex in str(type(g[k])) for ex in exclude_types]):
            continue
        identifiers.add(k)
    for id in list(identifiers):
        for py in [p for p in Path().rglob("*.py") if p.name != "config.py"]:
            if id in py.read_text():
                identifiers.remove(id)
                break  # Found it so try next identifier
    if identifiers:
        print("The following don't seem to be used")
        pprint(identifiers)
