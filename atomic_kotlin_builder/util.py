#! py -3
# Utilities
import shutil
import sys
import textwrap

import atomic_kotlin_builder.config as config


def clean(dir_to_remove):
    "Remove directory"
    try:
        if dir_to_remove.exists():
            shutil.rmtree(str(dir_to_remove))
            return "Removed: {}".format(dir_to_remove)
        else:
            return "Doesn't exist: {}".format(dir_to_remove)
    except Exception as e:
        print("""Removal failed: {}
        Are you inside that directory, or using a file inside it?
        """.format(dir_to_remove))
        print(e)


def check_for_existence(extension):
    files_with_extension = list(config.example_dir.rglob(extension))
    if len(files_with_extension) < 1:
        print("Error: no " + extension + " files found")
        sys.exit(1)
    return files_with_extension


# Format output:
# (0) Do first/last lines before formatting to width
# (1) Combine output and error (if present) files
# (2) Format all output to width limit
# (3) Add closing '*/'


def adjust_lines(text):
    text = text.replace("\0", "NUL")
    lines = text.splitlines()
    slug = lines[0]
    if "(First and Last " in slug:
        num_of_lines = int(slug.split()[5])
        adjusted = lines[:num_of_lines + 1] +\
            ["...________...________...________...________..."] +\
            lines[-num_of_lines:]
        return "\n".join(adjusted)
    elif "(First " in slug:
        num_of_lines = int(slug.split()[3])
        adjusted = lines[:num_of_lines + 1] +\
            ["                  ..."]
        return "\n".join(adjusted)
    else:
        return text


def fill_to_width(text):
    result = ""
    for line in text.splitlines():
        result += textwrap.fill(line, width=config.code_width - 1) + "\n"
    return result.strip()


def reformat_runoutput_files():
    for outfile in check_for_existence("*.out"):
        kotlin = outfile.with_suffix(".kt")
        if kotlin.exists():
            if "{VisuallyInspectOutput}" in kotlin.read_text():  # Don't create p1 file
                print("{} Excluded".format(kotlin.name))
                continue
        out_text = adjust_lines(outfile.read_text())
        phase_1 = outfile.with_suffix(".p1")
        with phase_1.open('w') as phs1:
            phs1.write(fill_to_width(out_text) + "\n")
            errfile = outfile.with_suffix(".err")
            if errfile.exists():
                phs1.write("___[ Error Output ]___\n")
                phs1.write(fill_to_width(errfile.read_text()) + "\n")
            phs1.write("*/\n")
