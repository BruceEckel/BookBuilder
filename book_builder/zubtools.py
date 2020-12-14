"""
Random automation subtools
"""
import os
import pprint
import re
from itertools import filterfalse
from PIL import Image

import book_builder.config as config


def display_image_resolutions():
    images = config.markdown_dir / "images"
    print(images)
    for md in images.rglob("*"):
        if md.is_file():
            print(md.name)
            with Image.open(md) as img:
                print(img.info.get("dpi"))


class CodeCheckListing:
    slugline = re.compile("^(//|#) .+?\.[a-z]+$", re.MULTILINE)

    def __init__(self, code_block: str):
        def remove(block: str, pattern: str) -> str:
            return re.sub(pattern, '', block, flags=re.DOTALL)

        self.code_block = code_block
        self.code = remove(code_block, r'/\*.*?\*/')
        self.code = remove(self.code, r'""".*?"""')
        self.lines = self.code.splitlines()
        self.title = self.lines[0]
        self.is_listing = CodeCheckListing.slugline.match(self.title)
        if not self.is_listing:
            return
        first_blank = self.lines.index("")
        self.header = self.lines[0:first_blank]
        self.body = self.lines[first_blank:]
        self.package = any([line.startswith("package") for line in self.lines])
        self.cleaned = [line.split('//')[0] for line in self.body]
        self.main = any([line.startswith("fun main(") for line in self.cleaned])
        self.definitions = [line for line in self.cleaned
                            if not line.startswith(' ')
                            and not line.startswith('}')
                            and not line.startswith(')')
                            and not line.startswith("fun main(")
                            and line.strip()
                            ]
        self.joined_definitions = "\n".join(self.definitions)

    def __str__(self):
        if not self.is_listing:
            return f"is_listing: {self.is_listing}\n{self.code_block}\n{'=' * 80}"
        return f"{self.title}\npackage: {self.package}\nmain: {self.main}\n" + \
               f"{self.code_block}\n{'-' * 20}\n" + \
               f"{self.joined_definitions}\n" + \
               f"{'=' * 80}"

    def display(self, msg: str):
        s = ' ' + msg + ' '
        print(s.center(78, '='))
        print(self.code_block)


def check_package_consistency():
    results = []
    files = set()
    found_packages = False
    for md in config.markdown_dir.glob("*.md"):
        if not found_packages and "Packages" not in md.name:
            continue
        if "Packages" in md.name:
            found_packages = True
            continue
        for group in re.findall("```(.*?)\n(.*?)\n```", md.read_text(), flags=re.DOTALL):
            ccl = CodeCheckListing(group[1])
            if not ccl.is_listing:
                continue
            if ccl.definitions and not ccl.package:
                ccl.display("No Package")
                results.append([md.name, ccl.title])
                files.add(md)
            if ccl.main and ccl.package and not ccl.definitions:
                ccl.display("Package but only main")
                results.append([md.name, ccl.title])
                files.add(md)
    pprint.pprint(results)
    for file in files:
        print(f"subl {file}")

def find_missing_listing_header():
    """
    Look for missing ```kotlin
    """
    for md in config.markdown_dir.glob("*.md"):
        lines = md.read_text().splitlines()
        for n, line in enumerate(lines):
            if (
                    line.startswith("//")
                    and line.endswith(".kt")
                    and not lines[n - 1].startswith("```kotlin")
            ):
                print(f"{md.name}: {line}")


def check_kotlin_usage():
    kt = re.compile("\s+kotlin[^.]")
    for md in config.markdown_dir.glob("*.md"):
        for line in md.read_text().splitlines():
            if kt.search(line):
                # if line.startswith("import "):
                #     continue
                print(line)


def find_imports_and_packages():
    all_imports = set()
    all_packages = set()
    for md in config.markdown_dir.glob("*.md"):
        for line in md.read_text().splitlines():
            if line.startswith("import "):
                all_imports.add(line)
            if line.startswith("package "):
                all_packages.add(line)
    pprint.pprint(all_imports)
    pprint.pprint(all_packages)


def find_classes():
    slugline = re.compile("^(//|#) .+?\.[a-z]+$", re.MULTILINE)
    inside = False
    for md in config.markdown_dir.glob("*.md"):
        for group in re.findall("```(.*?)\n(.*?)\n```", md.read_text(), re.DOTALL):
            listing = group[1].splitlines()
            title = listing[0]
            if slugline.match(title):
                for line in listing:
                    if inside:
                        print(line)
                        if line.startswith("}"):
                            inside = False
                    if line.startswith("class") and line.endswith("{"):
                        print(title)
                        print(line)
                        inside = True


def check_exercise_count():
    exclusions = [
        "_Front.md",
        "_Introduction.md",
        "_Section_",
        "_Appendices.md",
        "_Appendix_",
    ]
    for md in config.markdown_dir.glob("*.md"):
        if any(ex in md.name for ex in exclusions):
            continue
        text = md.read_text()
        for n in [1, 2, 3]:
            if f"##### Exercise {n}" not in text:
                print(f"{md.name} Missing Exercise {n}")


def generate_crosslink_tag(atom_title):
    atom_title = re.sub(r"\s+", " ", atom_title)
    title = re.sub('[`:!,()]', '', atom_title)
    title = title.replace('&', 'and')
    title = title.replace(' ', '-')
    return title.lower()


def fix_crosslink_references():
    for md in config.markdown_dir.glob("*.md"):
        if md.name == "098_Appendix_B_Java_Interoperability.md":
            continue
        text = md.read_text()
        crosslinks = set(re.findall(r"\s(\[[A-Z`][^,]+?\])[^(:]", text)) - {"[Error]"}
        if crosslinks:
            print(f"\n{md.name}")
            for cl in crosslinks:
                fixed_tag = f"{cl}(#{generate_crosslink_tag(cl[1:-1])})"
                print(fixed_tag)
            md.write_text(text.replace(cl, fixed_tag))


def check_crosslink_references():
    targets = set()
    all: str = ""
    for md in config.markdown_dir.glob("*.md"):
        text = md.read_text()
        all += text
        target: str = re.findall(r"#\s+.+?{(#.+?)}", text)[0]
        targets.add(target)
    pprint.pprint(targets)

    references = re.findall(r"\[.+?\]\((#.+?)\)", all)
    pprint.pprint(references)
    for ref in references:
        if ref not in targets:
            print(f"-> {ref}")

    # candidates = filter_items(set(re.findall(r"\[.+?\][^(]", text)))
    # if candidates:
    #     print(f"\n{md.name}")
    #     for c in candidates:
    #         print(c)


def change_to_new_heading1():
    for md in config.markdown_dir.glob("*.md"):
        print(f"\n{md.name}")
        text = md.read_text().splitlines()
        del text[1]
        text[0] = f"# {text[0]} {{#{generate_crosslink_tag(text[0])}}}"
        print(text[0])
        md.write_text("\n".join(text) + "\n")
        # for n, line in enumerate(text):
        #     print(line)
        #     if n > 5:
        #         break


def change_to_new_heading2():
    for md in config.markdown_dir.glob("*.md"):
        print(f"\n{md.name}")
        text = md.read_text()
        heading2_list = re.findall(r"\n[a-zA-Z0-9_ `,&]+\n-+\n", text)
        for h2 in heading2_list:
            print(h2)


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
    if not config.html_stripped_dir.exists():
        config.html_stripped_dir.mkdir()
    for html in config.html_complete_dir.glob("*.html"):
        print(f"----- {html.name} -----")
        text = html.read_text(encoding='utf-8')  # , errors='ignore')
        text = re.sub("<pre.*?>(.*?)</pre>", "\g<1>", text, flags=re.DOTALL)
        (config.html_stripped_dir / html.name).write_text(text, encoding='utf-8')
        # for code in re.findall("<pre.*?>(.*?)</pre>", text, flags=re.DOTALL):
        #     print(code + "\n\n")

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
    #         print(
