# py -3
# -*- coding: utf8 -*-
"""
Assemble individual markdown files together and produce epub book.
"""
from pathlib import Path
import os
import sys
import shutil
from betools import CmdLine
from ebook_build import *
import config


@CmdLine('c')
def clean_new_build_dir():
    """
    Delete and create basic book build directory
    """
    close_viewer()
    recreate_build_dir()

@CmdLine('s')
def edit_combined_files():
    """
    Put markdown files together and open result in editor
    """
    combine_markdown_files(config.combined_markdown)
    os.system("subl {}".format(config.combined_markdown))


def pandoc_epub_command(output_name):
    return (
        "pandoc " + config.ebookName + "-assembled.md -t epub3 -o " + output_name +
        " -f markdown-native_divs "
        " --smart "
        " --epub-cover-image=cover.jpg "
        " --epub-embed-font=AtomBullet.jpg "
        " --epub-embed-font=subhead.png "
        " --epub-embed-font=level-2.png "
        " --epub-embed-font=UbuntuMono-R.ttf "
        " --epub-embed-font=UbuntuMono-RI.ttf "
        " --epub-embed-font=UbuntuMono-B.ttf "
        " --epub-embed-font=UbuntuMono-BI.ttf "
        " --epub-embed-font=georgia.ttf "
        " --epub-embed-font=georgiab.ttf "
        " --epub-embed-font=georgiai.ttf "
        " --epub-embed-font=georgiaz.ttf "
        " --epub-embed-font=verdana.ttf "
        " --epub-embed-font=verdanab.ttf "
        " --epub-embed-font=verdanai.ttf "
        " --epub-embed-font=verdanaz.ttf "
        " --epub-embed-font=YuGothicUI-Semibold.ttf "
        " --toc-depth=2 "
        " --epub-stylesheet=AtomicKotlin.css ")


def pandoc_html_command(output_name):
    return (
        "pandoc " + config.ebookName + "-assembled.md -t html5 -o " + output_name +
        " -f markdown-native_divs "
        " --smart "
        " --toc-depth=2 "
        " --standalone "
        " --css=AtomicKotlin.css ")


def convert_to_epub():
    """
    Pandoc markdown to epub
    """
    os.chdir(str(config.build_dir))
    cmd = pandoc_epub_command(config.epubName)
    print(cmd)
    os.system(cmd)
    os.system("start " + config.epubName)
    os.system(r'copy /Y " + config.epubName +  " C:\Users\Bruce\Google Drive\ebooks"')
    os.system(r'copy /Y " + config.epubName +  " C:\Users\Bruce\Dropbox\__Ebooks"')


def copy_and_unzip_epub():
    """
    Create unpacked epub
    """
    zipfile = config.ebookName + ".zip"
    shutil.copy(config.epubName, zipfile)
    os.system("unzip " + zipfile + " -d epub_files")


def convert_to_epub_for_e_ink():
    """
    Pandoc markdown to black & white epub
    """
    os.chdir(str(config.build_dir))
    cmd = pandoc_epub_command(config.ebookName + "-E-INK.epub") + " --no-highlight "
    print(cmd)
    os.system(cmd)


def convert_to_e_ink_mobi():
    """
    epub to e-ink kindle (mobi)
    """
    os.chdir(str(config.build_dir))
    cmd = "kindlegen " + config.ebookName + "-E-INK.epub"
    print(cmd)
    os.system(cmd)


def convert_to_color_mobi():
    """
    epub to color kindle (mobi)
    """
    os.chdir(str(config.build_dir))
    cmd = "kindlegen " + config.epubName
    print(cmd)
    os.system(cmd)


@CmdLine('e')
def create_fresh_epub():
    """
    Fresh conversion from Markdown
    """
    close_viewer()
    ensure_ebook_build_dir()
    combine_markdown_files(config.combined_markdown)
    convert_to_epub()
    copy_and_unzip_epub()


@CmdLine('t')
def test_epub():
    """
    Run EpubCheck on the book
    """
    outfile = str(config.build_dir / "epubcheck_output.txt")
    os.system('''java -jar "C:\Program Files\epubcheck-4.0.1\epubcheck.jar" "''' + str(config.build_dir / config.epubName) + '" 2> ' + outfile)
    os.system("subl " + outfile)


@CmdLine('5')
def convert_to_html():
    """
    Pandoc markdown to html
    """
    os.chdir(str(config.build_dir))
    cmd = pandoc_html_command(config.ebookName + ".html")
    print(cmd)
    os.system(cmd)


@CmdLine('m')
def convert_to_mobi_via_html():
    """
    Pandoc markdown to mobi by starting with html
    (No joy here yet; might require processing HTML)
    """
    html_book = config.ebookName + ".html"
    os.chdir(str(config.build_dir))
    cmd = pandoc_html_command(html_book)
    print(cmd)
    os.system(cmd)
    cmd = "kindlegen " + html_book
    print(cmd)
    os.system(cmd)


@CmdLine('a')
def all():
    """
    Create fresh epub, epub for E-ink, and mobi for e-ink
    """
    close_viewer()
    ensure_ebook_build_dir()
    combine_markdown_files(config.combined_markdown)
    convert_to_epub()
    copy_and_unzip_epub()
    convert_to_mobi_via_html()
    # convert_to_epub_for_e_ink()
    # convert_to_e_ink_mobi()
    # convert_to_color_mobi()


if __name__ == '__main__':
    CmdLine.run()
