#! py -3
"""
Tool to build a full release from scratch
"""
import os
import book_builder.config as config
from book_builder.util import clean


def create_release():
    "Fix and put as a standalone command which runs everything"
    return "Incomplete"
    books = [
        config.epub_file_name,
        config.epub_mono_file_name,
    ]
    samples = [
        config.epub_sample_file_name,
        config.epub_sample_mono_file_name,
    ]
    if config.release_dir.exists():
        clean(config.release_dir)
    os.makedirs(config.release_dir)
    for src in books + samples:
        os.system(f"cp {config.epub_build_dir / src} {config.release_dir}")
    os.chdir(str(config.release_dir))

    def zzip(target_name, file_list):
        "zip utility"
        os.system(f"zip {target_name}.zip {' '.join(file_list)}")
    zzip(config.base_name, books + [b[:-4] + "mobi" for b in books])
    zzip(config.base_name + "Sample", samples + [b[:-4] + "mobi" for b in samples])
