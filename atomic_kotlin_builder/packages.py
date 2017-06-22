#! py -3
# Discover examples that don't have packages, add package statements
import logging
from logging import debug
import os
import re
import shutil
import sys
from pathlib import Path

import atomic_kotlin_builder.config as config


logging.basicConfig(filename=__file__.split('.')[0] + ".log", filemode='w', level=logging.DEBUG)


def unpackaged():
    "Discover examples that don't have packages"
    return "Not implemented yet"
    print("Extracting examples ...")
    if not config.example_dir.exists():
        debug("creating {}".format(config.example_dir))
        config.example_dir.mkdir()

    if not config.markdown_dir.exists():
        return "Cannot find {}".format(config.markdown_dir)

    slugline = re.compile("^(//|#) .+?\.[a-z]+$", re.MULTILINE)
    xmlslug = re.compile("^<!-- .+?\.[a-z]+ +-->$", re.MULTILINE)

    for sourceText in config.markdown_dir.glob("*.md"):
        debug("--- {} ---".format(sourceText.name))
        with sourceText.open("rb") as chapter:
            text = chapter.read().decode("utf-8", "ignore")
            for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL):
                listing = group[1].splitlines()
                title = listing[0]
                package = None
                for line in listing:
                    if line.startswith("package "):
                        package = line.split()[1].strip()
                if slugline.match(title) or xmlslug.match(title):
                    debug(title)
                    fpath = title.split()[1].strip()
                    if package:
                        target = config.example_dir / package / fpath
                    else:
                        target = config.example_dir / fpath
                    debug("writing {}".format(target))
                    if not target.parent.exists():
                        target.parent.mkdir(parents=True)
                    with target.open("w", newline='') as codeListing:
                        debug(group[1])
                        if slugline.match(title):
                            codeListing.write(group[1].strip() + "\n")
                        elif xmlslug.match(title):  # Drop the first line
                            codeListing.write("\n".join(listing[1:]))

    return "Code extracted into {}".format(config.example_dir)


def add_packages():
    "Insert package statements into examples that lack them"
    return "--- Implementation Incomplete ---"
    print("Creating test.bat files ...")
    if not config.example_dir.exists():
        return "Run 'extract' command first"
    for package in [d for d in config.example_dir.iterdir() if d.is_dir()]:
        os.chdir(package)
        print(os.getcwd())


