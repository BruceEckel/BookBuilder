"""
Random automation subtools
"""
from pathlib import Path
import os
import re
import sys
from itertools import filterfalse
from pprint import pprint
import book_builder.config as config


def check_for_notes(md, lines):
    notes = False
    for line in lines:
        if line.startswith("+ Notes:") and len(line) > len("+ Notes:"):
            print(f"{md.stem}: [{line}]")
            os.system(f"{config.md_editor} {md}:6:10")
            notes = True
    return notes


def remove_checkboxes():
    def determine(line):
        return (
            line.strip().endswith("] Ready for Review") or
            line.strip().endswith("] Tech Checked") or
            line.startswith("+ Notes:")
        )
    for md in config.markdown_dir.glob("*.md"):
        lines = md.read_text().splitlines()
        if check_for_notes(md, lines):
            return "Notes need changing to {{}}"
        lines[:] = filterfalse(determine, lines)
        text = re.sub('\n{2,}', '\n\n', "\n".join(lines))
        md.write_text(text + "\n")


def find_pre_and_code_tags_in_html():
    if not config.html_complete_dir.exists():
        return "run 'bb html complete' before running this command"
    for html in config.html_complete_dir.glob("*.html"):
        print(f"----- {html.name} -----")
        text = html.read_text(errors='ignore')
        # print(text)
        for code in re.findall("<pre.*?>(.*?)</pre>", text, flags=re.DOTALL):
            print(code + "\n\n")

    # for html in config.html_complete_dir.glob("*.html"):
    #     results = []
    #     for line in html.read_text(errors='ignore').splitlines():
    #         if "<pre" in line and "<code" not in line:
    #             results.append(f"\t{line}")
    #         if "<pre" in line and '<pre class="sourceCode' not in line:
    #             results.append(f"\t{line}")
    #         if '<pre class="sourceCode' in line and '<code class="sourceCode' not in line:
    #             results.append(f"\t{line}")
    #     if results:
    #         print(html.name)
    #         print("\n".join(results))
