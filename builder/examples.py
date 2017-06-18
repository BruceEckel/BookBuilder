#! py -3
# TODO: change to hunt for `package` and use that to place resulting file
# Extract code config.example_dir from Atomic Kotlin Markdown files.
# Configures for Gradle build by copying from AtomicKotlin-Examples.
import logging
import os
import re
import shutil
import sys
from logging import debug
from pathlib import Path

import builder.config

def test():
    print("AtomicKotlinBuilder examples.py")

logging.basicConfig(filename=__file__.split(
    '.')[0] + ".log", filemode='w', level=logging.DEBUG)

# For Development:
tools_to_copy = [Path(sys.path[0]) / f for f in [
    # "__tests.bat",
    # "_check_markdown.bat",
    # "_output_file_check.bat",
    # "_verify_output.bat",
    # "_update_extracted_example_output.bat",
    # "_capture_gradle.bat",
    # "chkstyle.bat",  # Run checkstyle, capturing output
    # "gg.bat", # Short for gradlew
]]


def copyTestFiles():
    print("Copying Test Files ...")
    for test_path in list(config.github_code_dir.rglob("tests/*")):
        dest = config.example_dir / \
            test_path.relative_to(config.github_code_dir)
        if(test_path.is_file()):
            if(not dest.parent.exists()):
                debug("creating " + str(dest.parent))
                os.makedirs(str(dest.parent))
            debug("copy " + str(test_path.relative_to(config.github_code_dir.parent)
                                ) + " " + str(dest.relative_to(config.example_dir)))
            shutil.copy(str(test_path), str(dest))


maindef = re.compile("public\s+static\s+void\s+main")


def extractExamples():
    print("Extracting examples ...")
    if not config.example_dir.exists():
        debug("creating {}".format(config.example_dir))
        config.example_dir.mkdir()
    # copyTestFiles()

    for f in tools_to_copy:
        shutil.copy(str(f), str(config.example_dir))

    if not config.markdown_dir.exists():
        print("Cannot find", config.markdown_dir)
        sys.exit()

    slugline = re.compile("^(//|#) .+?\.[a-z]+$", re.MULTILINE)
    xmlslug = re.compile("^<!-- .+?\.[a-z]+ +-->$", re.MULTILINE)

    for sourceText in config.markdown_dir.glob("*.md"):
        debug("--- {} ---".format(sourceText.name))
        with sourceText.open("rb") as chapter:
            text = chapter.read().decode("utf-8", "ignore")
            for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL):
                listing = group[1].splitlines()
                title = listing[0]
                if slugline.match(title) or xmlslug.match(title):
                    debug(title)
                    fpath = title.split()[1].strip()
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


def copyGradleFiles():
    print("Copying Gradle Files ...")
    if not config.github_code_dir.exists():
        print("Doesn't exist: %s" % config.github_code_dir)
        sys.exit(1)
    for gradle_path in list(config.github_code_dir.rglob("*gradle*")) + \
            list(config.github_code_dir.rglob("*.xml")) + \
            list(config.github_code_dir.rglob("*.yml")) + \
            list(config.github_code_dir.rglob("*.md")) + \
            list((config.github_code_dir / "buildSrc").rglob("*")):
        dest = config.example_dir / \
            gradle_path.relative_to(config.github_code_dir)
        if gradle_path.is_file():
            if(not dest.parent.exists()):
                debug("creating " + str(dest.parent))
                os.makedirs(str(dest.parent))
            debug("copy " + str(gradle_path.relative_to(config.github_code_dir.parent)
                                ) + " " + str(dest.relative_to(config.example_dir)))
            shutil.copy(str(gradle_path), str(dest))


def clean():
    "Remove ExtractedExamples directory"
    print("Cleaning ...")
    try:
        if config.example_dir.exists():
            shutil.rmtree(str(config.example_dir))
    except:
        print("Old path removal failed")
        raise RuntimeError()


def extractAndCopyBuildFiles():
    "Clean, then extract examples from Markdown, copy gradle files from AtomicKotlin-Examples"
    clean()
    extractExamples()
    copyGradleFiles()


if __name__ == '__main__':
    CmdLine.run()
