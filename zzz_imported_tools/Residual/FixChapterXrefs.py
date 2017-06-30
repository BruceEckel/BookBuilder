from pathlib import Path
import sys
import shutil
import config
import time
import os
import re
from betools import CmdLine

def show(text):
    try:
        print(text)
    except:
        print(text.encode("utf8"))

def generate_xref_list():
    raw = []
    result = []
    for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
        lines = md.read_text(encoding="utf8").splitlines()
        title = lines[0].strip()
        raw.append(title)
        title = r"\s+".join([word for word in title.split()])
        search_for = re.compile(r"[^\./]\s+" + title + "\s+")
        result.append(search_for)
    return result, raw


def create_test_directory():
    if config.test_dir.exists():
        shutil.rmtree(str(config.test_dir))
        time.sleep(1)
    config.test_dir.mkdir()


def open_first_xref(lines, md, xref_list):
    def fname():
        print(str(md.name))
    for n, line in enumerate(lines):
        for xref in xref_list:
            # if xref in line and (". " + xref) not in line:
            if xref.search(line):
                # fname()
                # fname = lambda: None
                # print(xref, end=': ')
                # show(line)
                os.system("subl {}:{}".format(str(md), n + 3))
                return

def regex_find_all_potential_xrefs(lines, xref_list):
    potentials = []
    for n, line in enumerate(lines):
        for xref in xref_list:
            if xref.search(line):
                potentials.append("{}:>|{}".format(n + 3, line))
    return potentials


def plain_find_all_potential_xrefs(lines, raw_xref):
    potentials = []
    for n, line in enumerate(lines):
        for xref in raw_xref:
            if xref in line:
                potentials.append("{}:>|{}".format(n + 3, line))
    return potentials


@CmdLine('p')
def trace_potential_chapter_xrefs():
    """
    Chapter cross-references
    """
    def save(items, fname):
        with (config.test_dir / fname).open("w") as xrf:
            for xr in items:
                print(type(xr), file=xrf, end=": ")
                print(xr, file=xrf)

    create_test_directory()
    xref_list, raw_xref = generate_xref_list()
    save(xref_list, "xref_list.txt")
    save(raw_xref, "raw_xref.txt")

    with (config.test_dir / "trace.txt").open('w') as trace:
        for md in config.markdown_dir.glob("[0-9][0-9]_*.md"):
            lines = md.read_text(encoding="utf8").splitlines()[2:]
            # potentials = regex_find_all_potential_xrefs(lines, xref_list)
            potentials = plain_find_all_potential_xrefs(lines, raw_xref)
            if potentials:
                print("[[>{}".format(md.name), file=trace)
                print("\n".join(potentials), file= trace)
                print("", file=trace)

    os.system("subl {}".format(config.test_dir / "trace.txt"))


@CmdLine('d')
def display_potential_chapter_xrefs():
    trace = (config.test_dir / "trace.txt").read_text()
    for block in trace.split("[[>"):
        if block:
            lines = block.strip().splitlines()
            fname = lines[0]
            line_num, __ = lines[1].split(":>|")
            os.system("subl {}:{}".format(config.markdown_dir / fname, line_num))


if __name__ == '__main__':
    CmdLine.run()