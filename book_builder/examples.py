#! py -3
# Extract code into config.example_dir from Markdown files.
import logging
import os
import re
import shutil
import subprocess
import sys
import io
from collections import defaultdict
from logging import debug
from pathlib import Path

import book_builder.config as config
import book_builder.util as util

logging.basicConfig(filename=__file__.split(
    '.')[0] + ".log", filemode='w', level=logging.DEBUG)


def clean():
    "Remove directory containing extracted example code"
    return util.clean(config.example_dir)


def extractExamples():
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
                        package = package.replace(".", "/")
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


def display_extracted_examples():
    for package in [d for d in config.example_dir.iterdir() if d.is_dir()]:
        print(package.relative_to(config.example_dir))
        for kt in package.rglob("*.kt"):
            print("    {}".format(kt.relative_to(package)))


gen_bat = """\
@echo off
generate --edit %*
"""

redo_bat = """\
@echo off
akb code extract
generate --reinsert %*
"""

def create_test_files():
    "Create gen.bat files for each package, to compile and run files"
    if not config.example_dir.exists():
        return "Run 'extract' command first"
    for package in [d for d in config.example_dir.iterdir() if d.is_dir()]:
        # with io.StringIO() as batch:
        #     for kt in package.rglob("*.kt"):
        #         print("cmd /c kotlinc {}".format(kt.relative_to(package)), file=batch)
        #         print("cmd /c kotlin {}.{}".format(package.name, kt.stem + "Kt"), file=batch)
        #     (package / "test.bat").write_text(batch.getvalue())
        (package / "gen.bat").write_text(gen_bat)
        (package / "redo.bat").write_text(redo_bat)
    return "bat files created"


class ExampleTest:
    def __init__(self, path):
        assert path.suffix == ".kt"
        self.path = path
        self.success = None

    def test(self):
        os.chdir(self.path.parent)
        cmd = ["kotlinc", "{}".format(self.path.name)]
        self.result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.stdout = self.result.stdout.decode('utf-8')
        self.stderr = self.result.stderr.decode('utf-8')
        self.success = len(self.stderr) == 0

    def __str__(self):
        result = ""
        if self.success is not None:
            result = "OK: " if self.success else "Failed: "
        result += self.path.name
        return result


def compile_all_examples():
    "Compile and capture all results, to show percentage of rewritten examples"
    count = 0
    examples = defaultdict(list)
    for example in (config.example_dir / "abstractclasses").rglob("*.kt"):
        examples[example.parts[-2]].append(ExampleTest(example))
        count += 1
    for edir in examples:
        print(edir)
        for exmpl in examples[edir]:
            print("    {}".format(exmpl))
            exmpl.test()
    print("example count = {}".format(count))
    for edir in examples:
        print("=== {} ===".format(edir))
        for et in examples[edir]:
            print("    {}".format(et))
            if not et.success:
                print("    {}".format(et.stderr))


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


def extractAndCopyBuildFiles():
    "Clean, then extract examples from Markdown, copy gradle files"
    clean()
    extractExamples()
    copyGradleFiles()


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
