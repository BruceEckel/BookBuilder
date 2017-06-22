#! py -3
# Various validation checks
import logging
from logging import debug
import os
import re
import shutil
import sys
from pathlib import Path

from atomic_kotlin_builder.util import *
import atomic_kotlin_builder.config as config
import atomic_kotlin_builder.package_names as package_names


logging.basicConfig(filename=__file__.split('.')[0] + ".log", filemode='w', level=logging.DEBUG)


def markdown_names():
    "Ensure markdown file names match chapter titles"
    print("Validating Markdown File Names ...")
    if not config.markdown_dir.exists():
        return "Cannot find {}".format(config.markdown_dir)
    for md in [f for f in config.markdown_dir.iterdir() if f.name[0].isdigit()]:
        if md.name == "00_Front.md":
            continue
        text = md.read_text().splitlines()
        if not text[1].startswith("==="):
            print("{} Missing Chapter Name".format(md))
            sys.exit(1)
        chap_name = md.name[3:-3]
        title = create_markdown_filename(text[0].strip())[:-3]
        if chap_name != title:
            print("{}: {} chapter title inconstent: {}".format(md.name, chap_name, title))


