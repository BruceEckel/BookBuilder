# py -3
# -*- coding: utf8 -*-
"""
Fix code listings in Atomic Scala into Pandoc-flavored Markdown
"""
from pathlib import Path
from pprint import pprint
import os, sys, re, shutil, time
from itertools import chain
from sortedcontainers import SortedSet
from collections import OrderedDict
from betools import CmdLine, visitDir, ruler, head
import webbrowser
import textwrap
import config


def start_marker(tag):
    return '[${}$]'.format(tag)


def end_marker(tag):
    return '[$end_{}$]'.format(tag)


# remove annoying characters
chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : ''          # modifier - under line
}
def replace_chars(match):
    char = match.group(0)
    return chars[char]

def fix_text(text):
    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, text)


@CmdLine('s')
def fix_spaces():
    """
    replace nonbreaking spaces in AtomicScala.md
    """
    mdown = config.markdown.read_text(encoding="utf8")
    mdown = mdown.replace(u'\xa0', u' ')
    config.markdown.with_name("AtomicScala-2.md").write_text(mdown, encoding="utf8")


#@CmdLine('c')
def fix_code_starts():
    """
    Put in "```scala" lines
    """
    mdown = config.markdown.read_text(encoding="utf8")
    result = []
    for n, line in enumerate(mdown.splitlines()):
        if line.startswith("1 "):
            print("{}: {}".format(n, line))
            result.append("```scala")
        result.append(line)


    config.markdown.with_name("AtomicScala-2.md").write_text("\n".join(result), encoding="utf8")


def fixline(line):
    if not line:
        return line
    start_spaces = 0
    while line[start_spaces] == " ":
        start_spaces += 1
    if start_spaces == 0 or start_spaces % 2 == 0:
        return line
    return line[1:]


class FixCode:
    def __init__(self, source):
        self.input = list(source)
        self.output = []
        self.index = 0

        while self.index < len(self.input):
            if self.input[self.index].startswith("```scala"):
                if self.input[self.index + 1].startswith("1   //"):
                    self.fixup()
                else:
                    self.output.append(self.input[self.index])
            else:
                self.output.append(self.input[self.index])
            self.index += 1


    def fixup(self):
        self.output.append(self.input[self.index])
        while True:
            self.index += 1
            if re.match("\d+", self.input[self.index]):
                self.output.append(fixline(self.input[self.index][3:]))
            elif self.input[self.index] is "":
                pass
            else:
                self.output.append("```")
                self.output.append("")
                self.output.append(self.input[self.index])
                return



@CmdLine('e')
def fix_code_ends():
    """
    Put in "```" lines
    """
    fixed = FixCode(config.markdown.read_text(encoding="utf8").splitlines())
    config.markdown.with_name("AtomicScala-2.md").write_text("\n".join(fixed.output), encoding="utf8")


@CmdLine('f')
def fix_code():
    """
    Fix code listings in AtomicScala.md
    """
    mdown = config.markdown.read_text(encoding="utf8")
    starts = [line for line in mdown.splitlines() if line.startswith("1 ") ]
    pprint(starts)
    print(len(starts))



if __name__ == '__main__': CmdLine.run()
