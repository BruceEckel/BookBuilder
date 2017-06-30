# py -3
# -*- coding: utf8 -*-
"""
Common tools for ebook building
"""
from pathlib import Path
import sys
import shutil
import config
import time

try:
    import psutil
except ImportError:
    print("Download psutil wheel from http://www.lfd.uci.edu/~gohlke/pythonlibs/#psutil")
    print("Then run:")
    print("pip install psutil-3.2.2-cp35-none-win32.whl")
    print("(you may need to substitute the latest version number)")
    sys.exit(1)


def close_viewer():
    "Close PDF and eBook viewer"
    for p in psutil.process_iter():
        if p.name() == "PDFXCview.exe" or p.name() == "FoxitReader.exe" :
            print("Closing PDF Viewer")
            p.terminate()
        if p.name() == "ebook-viewer.exe":
            print("Closing eBook Viewer")
            p.terminate()


def copy(src):
    shutil.copy(str(src), str(config.build_dir))


def populate_ebook_build_dir():
    # shutil.copytree(
    #     str(config.markdown_dir / "images"),
    #     str(config.build_dir / "images"))

    [copy(font) for font in config.fonts.glob("*")]
    copy(config.cover)
    copy(config.css)
    # copy(config.metadata)
    copy(config.ebookResources / "AtomBullet.jpg")
    copy(config.ebookResources / "subhead.png")
    copy(config.ebookResources / "level-2.png")
    # copy(config.ebookResources / "onjava.tex")
    # copy(config.ebookResources / "onjava.cls")


def recreate_build_dir():
    "Create and populate a fresh build_dir"
    if config.build_dir.exists():
        shutil.rmtree(str(config.build_dir))
        time.sleep(1)
    config.build_dir.mkdir()
    populate_ebook_build_dir()


def ensure_ebook_build_dir():
    """
    Prepare ebook_build_dir for a build
    """
    if not config.build_dir.exists():
        config.build_dir.mkdir()
    # Use images dir as an indicator that "populate" hasn't been run:
    # if not config.build_dir_images.exists():
    populate_ebook_build_dir()
    copy(config.css)
    print("css refreshed")
    if (config.build_dir / "epub_files").exists():
        shutil.rmtree(str(config.build_dir / "epub_files"))


def remove_ebook_build_dir():
    if config.build_dir.exists():
        shutil.rmtree(str(config.build_dir))
        time.sleep(1)


def combine_markdown_files(target):
    """
    Put markdown files together
    """
    assembled = ""
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        print(str(md.name), end=", ")
        with md.open(encoding="utf8") as chapter:
            assembled += chapter.read() + "\n"
    with target.open('w', encoding="utf8") as book:
        book.write(assembled)
    print("\n\n")
