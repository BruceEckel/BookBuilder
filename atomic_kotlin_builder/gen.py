#! py -3
# For running from gen.bat (placed in each atom directory)
# Compiles and runs each example, attaches output to new version
# of that example, placed in the 'generated' subdirectory
import os
import subprocess
import sys
from pathlib import Path
import click
import atomic_kotlin_builder.config as config
import atomic_kotlin_builder.util as util


def generate_example(source_file):
    "Compile and capture results, create new source file with output appended"
    gen = Path.cwd() / "generated"
    if not gen.exists():
        gen.mkdir()
    def execute(cmd, topic):
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = result.stdout.decode('utf-8')
        err = result.stderr.decode('utf-8')
        if len(err):
            print("{}".format(err))
        return out, err

    compiler_out, compiler_err = execute(["kotlinc", "{}".format(source_file.name)], "compile")
    run_out, run_err = execute(["kotlin", "{}.{}".format(source_file.parent.stem, source_file.stem + "Kt")], "run")

    if "error" in compiler_err or "error" in run_err:
        return None

    def chop_output(source_path):
        lines = source_path.read_text().strip().splitlines()
        for n, line in enumerate(lines):
            if line.startswith("/* Output:"):
                return "\n".join(lines[:n])
        return "\n".join(lines)

    run_out = ("\n".join([ln.rstrip() for ln in run_out.splitlines()])).strip()
    source_code = chop_output(source_file)
    if len(run_out):
        source_code += "\n/* Output:\n{}\n*/".format(run_out.strip())
    generated_example = gen / source_file.name
    generated_example.write_text(source_code)
    print("wrote {}".format(generated_example.relative_to(Path.cwd())))
    return generated_example


def reinsert_file(generated_file):
    generated = generated_file.read_text()
    lines = generated.splitlines()
    slug = lines[0]
    def find_package(lines):
        for line in lines:
            if line.startswith("package "):
                return line.strip()
    package = find_package(lines)
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        text = md.read_text()
        if slug in text and package in text:
            updated_text, index = util.replace_code_in_text(generated, text)
            # Write markdown file, open in sublime at index
            md.write_text(updated_text + "\n")
            os.system("subl {}:{}".format(md, index))
            # test_file = md.with_suffix(".test")
            # test_file.write_text(updated_text + "\n")
            # os.system("subl {}:{}".format(test_file, index))
            return
    assert False, "No code found in any Markdown files for {}".format(generated_file)


def process_file(source_file, reinsert):
    generated_file = generate_example(source_file)
    if generated_file:
        os.system("subl {}".format(generated_file))
    if reinsert:
        reinsert_file(generated_file)


@click.command()
@click.option('--reinsert', is_flag=True, help='Insert result back into md file.')
@click.argument('kotlin_files', nargs=-1)
def generate(kotlin_files, reinsert):
    """
    Takes kotlin files compiles them, runs them, and creates a new files with the output
    appended. With no arguments, does all files in this directory.
    """
    if len(kotlin_files):
        for kf in kotlin_files:
            process_file(Path.cwd() / kf, reinsert)
    else: # No arguments, do them all
        for source_file in Path.cwd().glob("*.kt"):
            process_file(source_file, reinsert)


if __name__ == '__main__':
    generate()
