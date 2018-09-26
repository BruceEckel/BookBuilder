#! py -3
# Extract code into config.example_dir from Markdown files.
# import logging
import os
import re
import stat
import string
import subprocess
import sys
from collections import defaultdict

import book_builder.config as config
import book_builder.util as util

# from logging import debug
# logging.basicConfig(filename=__file__.split(
#     '.')[0] + ".log", filemode='w', level=logging.DEBUG)


def debug(msg): pass
# def debug(msg): print(msg)


def clean():
    "Remove directory containing extracted example code"
    util.clean(config.example_dir)
    return f"{config.example_dir} removed"


def write_listing(file_path, listing):
    debug(f"writing {file_path}")
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)
    with file_path.open("w", newline='') as listing_file:
        debug(listing)
        listing_file.write(listing.strip() + "\n")


def extractExamples():
    print("Extracting examples ...")
    if not config.extracted_examples.exists():
        return f"Cannot find {config.extracted_examples}"
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    if config.example_dir.exists():
        print(clean())

    slugline = re.compile("^(//|#) .+?\.[a-z]+$", re.MULTILINE)

    for sourceText in config.markdown_dir.glob("*.md"):
        debug(f"--- {sourceText.name} ---")
        with sourceText.open("rb") as chapter:
            text = chapter.read().decode("utf-8", "ignore")
            for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL):
                listing = group[1].splitlines()
                title = listing[0]
                if '!!!' in title:
                    continue  # Don't save files that are marked bad
                if slugline.match(title):
                    debug(title)
                    fpath = title.split()[1].strip()
                    atom_directory = fpath.split('/')[0]
                    if atom_directory in config.exclude_atoms:
                        # Put it in the separate exclude tree:
                        write_listing(config.exclude_dir / fpath, group[1])
                    else:
                        write_listing(config.example_dir / fpath, group[1])

    return f"Code extracted into {config.example_dir}"


########################### tasks.gradle generation ##########################


tasks_base = """\
configurations {
    kotlinRuntime
}

dependencies {
    kotlinRuntime "org.jetbrains.kotlin:kotlin-runtime:1.3-M1"
}

def kotlinClassPath = configurations.kotlinRuntime + sourceSets.main.runtimeClasspath

"""

run_task = string.Template("""\
task run (dependsOn: [
    $runtasks
    ]) {
    doLast {
        println '*** run complete ***'
    }
}
""")


def report_duplicate_file_names(*patterns, check_for_duplicates):
    fnames = []
    for pattern in patterns:
        fnames += [kt.name for kt in config.example_dir.rglob(pattern)]
    # from pprint import pprint
    # pprint(fnames)
    duplicates = [x.strip() for x in fnames if fnames.count(x) >= 2]
    if duplicates and check_for_duplicates:
        dupstring = '\n\t'.join(duplicates)
        print(f"ERROR: Duplicate code file names: \n{dupstring}")
        sys.exit(1)


def create_tasks_for_gradle(check_for_duplicates):
    "Regenerate gradle/tasks.gradle file based on actual extracted examples"
    report_duplicate_file_names("*.kt", "*.java", check_for_duplicates=check_for_duplicates)
    # Produces sorted tasks by name:
    task_list = tasks_base
    runnable_list = []
    ktfiles = {kt.stem: kt for kt in config.example_dir.rglob("*.kt")}
    javafiles = {
        java.stem: java for java in config.example_dir.rglob("*.java")}
    codefiles = {**ktfiles, **javafiles}  # Combine the dictionaries
    for key in sorted(codefiles):
        codefile = codefiles[key]
        gradle_task = task(codefile)
        if gradle_task:
            task_list += gradle_task + "\n"
            runnable_list.append("'" + codefile.stem + "'")
    task_list += run_task.substitute(
        runtasks=",\n    ".join(sorted(runnable_list)))
    tasks_file = config.extracted_examples / "gradle" / "tasks.gradle"
    tasks_file.write_text(task_list)
    return f"Wrote {tasks_file}"


task_template = string.Template("""\
task $task_name(type: JavaExec) {
    classpath kotlinClassPath
    main = '$class_file'
}
""")


def task(codefile):
    package = ""
    code = codefile.read_text()
    packages = [line.split()[1].strip()
                for line in code.splitlines()
                if line.startswith("package ")]
    if packages:
        package = packages[0]
        if package.endswith(";"):
            package = package[:-1]
    if codefile.suffix == ".kt":
        classfile = f"{codefile.stem + 'Kt'}"
    if codefile.suffix == ".java":
        classfile = f"{codefile.stem}"
    if package:
        classfile = f"{package}.{classfile}"
    if "main(" in code:
        return task_template.substitute(task_name=codefile.stem, class_file=classfile)
    return None


###################### Batch files ##########################

python_bat = """\
@echo off& python -x %0".bat" %* &goto :eof
"""

python_shell = """\
#!/usr/bin/env python3.6
"""

run_py = """\
from subprocess import call
from pathlib import Path
import sys, os

def ensure(test, msg):
    if not test:
        print(msg)
        sys.exit(1)

def gradle(name):
    home = Path.cwd()
    fpath = home / name
    ensure(fpath.exists(), f"{fpath.name} doesn't exist")
    ensure("main(" in fpath.read_text(), f"No main() in {fpath.name}")
    os.chdir(home.parent.parent)
    call(f"./gradlew {fpath.stem}", shell=True)
    os.chdir(home)

def multiple(name_list):
    names = " ".join(name_list)
    home = Path.cwd()
    os.chdir(home.parent.parent)
    call(f"./gradlew {names}", shell=True)
    os.chdir(home)

def glob(ext):
    return list(Path.cwd().glob("*." + ext))

if len(sys.argv) > 1:
    gradle(sys.argv[1])
else:
    multiple([fpath.stem for fpath in glob("kt") + glob("java")
              if "main(" in fpath.read_text()])
"""


def create_test_files():
    "Create run.bat and run.sh files for each package, to compile and run files"
    if not config.example_dir.exists():
        return "Run 'extract' command first"
    for package in [d for d in config.example_dir.iterdir() if d.is_dir()]:
        (package / "run.bat").write_text(python_bat +
                                         run_py.replace("./gradlew", "gradlew"))
        (package / "run.sh").write_text(python_shell + run_py)
    return "run.bat and run.sh files created"


def make_all_run_sh_executable():
    """
    Modify all run.sh files to make them executable. This is a slow operation,
    so only do it when you've created new run.sh files, before you check them
    into Github.
    TODO: Discover which files have actually changed and only modify those.
    """
    for package in [d for d in config.example_dir.iterdir() if d.is_dir()]:
        os.chdir(package)
        os.system("git update-index --chmod=+x run.sh")
        # os.chmod(package / "run.sh", stat.S_IXOTH)
    return "run.sh files now executable via git"


def display_extracted_examples():
    for package in [d for d in config.example_dir.iterdir() if d.is_dir()]:
        print(package.relative_to(config.example_dir))
        for example in package.rglob(f"*.{config.code_ext}"):
            print(f"    {example.relative_to(package)}")


class ExampleTest:
    def __init__(self, path):
        assert path.suffix == f".{config.code_ext}"
        self.path = path
        self.success = None

    def test(self):
        os.chdir(self.path.parent)
        cmd = ["kotlinc", f"{self.path.name}"]
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
    for example in (config.example_dir / "abstractclasses").rglob(f"*.{config.code_ext}"):
        examples[example.parts[-2]].append(ExampleTest(example))
        count += 1
    for edir in examples:
        print(edir)
        for exmpl in examples[edir]:
            print(f"    {exmpl}")
            exmpl.test()
    print(f"example count = {count}")
    for edir in examples:
        print(f"=== {edir} ===")
        for et in examples[edir]:
            print(f"    {et}")
            if not et.success:
                print(f"    {et.stderr}")
