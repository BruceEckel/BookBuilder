"""
Generate ebooks in different formats
"""
from pathlib import Path
import os
import zipfile
import book_builder.config as config
from book_builder.config import BookType
from book_builder.config import epub_name
from book_builder.util import generate_epub_files
from book_builder.util import regenerate_ebook_build_dir
from book_builder.util import combine_markdown_files


def fix_for_apple(name):
    epub = zipfile.ZipFile(name, "a")
    epub.write(config.meta_inf, "META-INF")
    epub.close()


def convert_to_epub():
    """
    Pandoc markdown to epub
    """
    generate_epub_files(config.epub_build_dir, config.epub_md, BookType.EPUB)
    fix_for_apple(epub_name())
    fix_for_apple(epub_name("-Sample"))
    return f"{config.epub_build_dir.name} Completed"


def convert_to_mobi():
    """
    Pandoc markdown to mobi
    Create special EPUBs first in this directory that use AtomicKotlin-mobi.css
    """
    generate_epub_files(config.mobi_build_dir, config.mobi_md, BookType.MOBI)
    # for epf in Path('.').glob("*.epub"):
    #     os.system(f"kindlegen {epf.name}")
    return f"{config.mobi_build_dir.name} Completed"


def pandoc_docx_command(input_file, output_name, title):
    assert input_file.exists(), f"Error: missing {input_file.name}"
    command = (
        "pandoc " + str(input_file.name) +
        " -t docx -o " + output_name +
        " -f markdown-native_divs "
        " -f markdown+smart "
        " --toc-depth=2 " +
        f'--metadata title="{title}"' +
        " --css=" + config.base_name + ".css ")
    print(command)
    os.system(command)


def convert_to_docx():
    """
    Pandoc markdown to docx
    """
    regenerate_ebook_build_dir(config.docx_build_dir, BookType.DOCX)
    combine_markdown_files(config.docx_md("assembled-stripped"), strip_notes=True)
    os.chdir(str(config.docx_build_dir))
    pandoc_docx_command(
        config.docx_md("assembled-stripped"), config.base_name + ".docx", config.title)
    return f"{config.docx_build_dir.name} Completed"
