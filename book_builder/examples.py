#! py -3
# Extract code into config.example_dir from Markdown files.
# import logging
import os
import re
import shutil
import subprocess
import sys
import io
from collections import defaultdict
import string
# from logging import debug
from pathlib import Path

import book_builder.config as config
import book_builder.util as util

# logging.basicConfig(filename=__file__.split(
#     '.')[0] + ".log", filemode='w', level=logging.DEBUG)
def debug(msg): pass
# def debug(msg): print(msg)


def clean():
    "Remove directory containing extracted example code"
    return util.clean(config.example_dir)


def extractExamples():
    print("Extracting examples ...")
    if not config.extracted_examples.exists():
        return f"Cannot find {config.extracted_examples}"
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    if config.example_dir.exists():
        clean()

    slugline = re.compile("^(//|#) .+?\.[a-z]+$", re.MULTILINE)

    for sourceText in config.markdown_dir.glob("*.md"):
        debug(f"--- {sourceText.name} ---")
        with sourceText.open("rb") as chapter:
            text = chapter.read().decode("utf-8", "ignore")
            for group in re.findall("```(.*?)\n(.*?)\n```", text, re.DOTALL):
                listing = group[1].splitlines()
                title = listing[0]
                if '!!!' in title:
                    continue # Don't save files that are marked bad
                if slugline.match(title):
                    debug(title)
                    fpath = title.split()[1].strip()
                    target = config.example_dir / fpath
                    debug(f"writing {target}")
                    if not target.parent.exists():
                        target.parent.mkdir(parents=True)
                    with target.open("w", newline='') as codeListing:
                        debug(group[1])
                        codeListing.write(group[1].strip() + "\n")

    return f"Code extracted into {config.example_dir}"


########################### tasks.gradle generation ##########################


tasks_base = """\
configurations {
    kotlinRuntime
}

dependencies {
    kotlinRuntime "org.jetbrains.kotlin:kotlin-runtime:$kotlin_version"
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


def create_tasks_gradle():
    "Regenerate gradle/tasks.gradle file based on actual extracted examples"
    # Check for duplicate names:
    all_names = [kt.stem for kt in config.example_dir.rglob("*.kt")]
    duplicates = [x.strip() for x in all_names if all_names.count(x) >= 2]
    if duplicates:
        dupstring = '\n\t'.join(duplicates)
        return f"ERROR: Duplicate names: \n{dupstring}"

    # Produces sorted tasks by name:
    task_list = tasks_base
    runnable_list = []
    ktfiles = {kt.stem : kt for kt in config.example_dir.rglob("*.kt")}
    for key in sorted(ktfiles):
        ktfile = ktfiles[key]
        gradle_task = task(ktfile)
        if gradle_task:
            task_list += gradle_task + "\n"
            runnable_list.append("'" + ktfile.stem + "'")
    task_list += run_task.substitute(runtasks = ",\n    ".join(sorted(runnable_list)))
    tasks_file = config.extracted_examples / "gradle" / "tasks.gradle"
    tasks_file.write_text(task_list)
    return f"Wrote {tasks_file}"


task_template = string.Template("""\
task $task_name(type: JavaExec) {
    classpath kotlinClassPath
    main = '$class_file'
}
""")


def task(ktfile):
    code = ktfile.read_text()
    package = [line.split()[1].strip() for line in code.splitlines() if line.startswith("package ")]
    classfile = f"{ktfile.stem + 'Kt'}"
    if package:
        classfile = f"{package[0]}.{classfile}"
    if "fun main(args: Array<String>)" in code:
        return task_template.substitute(task_name = ktfile.stem, class_file = classfile)
    return None


###################### Batch files ##########################

gen_bat = """\
@echo off
generate --edit %*
"""

redo_bat = """\
@echo off
bb code extract
generate --reinsert %*
"""

reinsert_bat = """\
@echo off
generate --reinsert %1
"""

prep_bat = r"kotlinc  ..\atomicTest\AtomicTest.kt -d ."

run_bat ="""\
@echo off& python -x %0".bat" %* &goto :eof
from subprocess import call
from pathlib import Path
import sys, os
def ensure(test, msg):
    if not test:
        print(msg)
        sys.exit(1)
def gradle(kname):
    home = Path.cwd()
    kpath = home / kname
    ensure(kpath.exists(), f"{kpath.name} doesn't exist")
    os.chdir(home.parent.parent)
    call(f"gradlew {kpath.stem}", shell=True)
    os.chdir(home)
def multiple(kname_list):
    knames = " ".join(kname_list)
    home = Path.cwd()
    os.chdir(home.parent.parent)
    call(f"gradlew {knames}", shell=True)
    os.chdir(home)
if len(sys.argv) > 1:
    gradle(sys.argv[1])
else:
    multiple([kpath.stem for kpath in Path.cwd().glob("*.kt") if "fun main(" in kpath.read_text()])
"""

run2_bat ="""\
@echo off& python -x %0".bat" %* &goto :eof
from subprocess import call
from pathlib import Path
call(r"kotlinc  ..\\atomicTest\\AtomicTest.kt -d .", shell=True)
call("kotlinc *.kt -nowarn -cp .", shell=True)
def runkt(kt):
    code = kt.read_text()
    package = [line.split()[1].strip() for line in code.splitlines() if line.startswith("package ")]
    filename = kt.name
    classfile = f"{kt.stem + 'Kt'}"
    if package:
        filename = f"{package[0]}.{filename}"
        classfile = f"{package[0]}.{classfile}"
    if "fun main(args: Array<String>)" in code:
        print(f"{'-'*8} {filename} {'-'*8}")
        call(f"kotlin {classfile}", shell=True)
for kt in Path.cwd().glob("*.kt"):
    runkt(kt)
"""

def create_test_files():
    "Create gen.bat files for each package, to compile and run files"
    if not config.example_dir.exists():
        return "Run 'extract' command first"
    for package in [d for d in config.example_dir.iterdir() if d.is_dir()]:
        (package / "gen.bat").write_text(gen_bat)
        (package / "redo.bat").write_text(redo_bat)
        (package / "reinsert.bat").write_text(reinsert_bat)
        (package / "prep.bat").write_text(prep_bat)
        (package / "run.bat").write_text(run_bat)
        #(package / "run2.bat").write_text(run2_bat)
    return "bat files created"


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
