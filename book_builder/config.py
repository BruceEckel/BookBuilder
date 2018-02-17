"""
Common program configuration variables for Book Builder. You must create
a 'configuration.py' file in the base directory of each different book; see
README.md.
"""
import os
import sys
from pathlib import Path
from enum import Enum, unique
# Add elements from configuration.py into this environment:
sys.path.append(str(Path(os.environ['BOOK_PROJECT_HOME'])))
from configuration import *

if 'EDITOR' not in os.environ:
    print("You must set the EDITOR environment variable to your favorite editor")
    sys.exit()
editor = os.environ['EDITOR']

msgbreak = '-=' * 25


@unique
class BookType(Enum):
    EPUB = "epub"
    MOBI = "mobi"
    MOBIMONO = "mobi-mono"
    DOCX = "docx"


root_name = base_name.lower()

root_path = Path(__file__).parent.parent.parent.resolve() / base_name
markdown_dir = root_path / "Markdown"
example_dir = extracted_examples / "Examples"
exclude_dir = extracted_examples / "ExcludedExamples"

epub_build_dir = root_path / "build"/ "epub"
mobi_build_dir = root_path / "build"/ "mobi"
docx_build_dir = root_path / "build"/ "docx"
release_dir    = root_path / "build"/ "Release"
test_dir       = root_path / "test"

def epub_md(fileid): return epub_build_dir / f"{root_name}-{fileid}.md"
def mobi_md(fileid): return mobi_build_dir / f"{root_name}-{fileid}.md"
def docx_md(fileid): return docx_build_dir / f"{root_name}-{fileid}.md"

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
# recent_atom_names = bb_code_dir / "recent_atom_names.py"

def resource(path): return root_path / "resources" / path
images        = resource("images")
fonts         = resource("fonts")
bullets       = resource("bullets")
cover         = resource("cover") / "Cover.png"
epub_css      = resource(root_name + "-epub.css")
mobi_css      = resource(root_name + "-mobi.css")
mobi_mono_css = resource(root_name + "-mobi-mono.css")
metadata      = resource("metadata.yaml")
meta_inf      = resource("META-INF")

data_path = root_path / "data"
dictionary = data_path / "dictionary.txt"
supplemental_dictionary = data_path / "supplemental_dictionary.txt"
all_misspelled = data_path / "all_misspelled.txt"
comment_capitalization_exclusions = data_path / "comment_capitalization_exclusions.txt"
mistaken_backquote_exclusions = data_path / "mistaken_backquote_exclusions.txt"


if __name__ == '__main__':
    "Check to see if identifiers are used in this project"
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
                break # Found it so try next identifier
    if identifiers:
        print("The following don't seem to be used")
        pprint(identifiers)
