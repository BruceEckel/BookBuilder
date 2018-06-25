"""
Generate HTML ebook
"""
import os
import re
from distutils.dir_util import copy_tree
from pathlib import Path
from collections import deque, OrderedDict
import book_builder.config as config
from book_builder.config import BookType
from book_builder.util import (copy_markdown_files,
                               header_to_filename_map,
                               regenerate_ebook_build_dir,
                               strip_review_notes)


def pandoc_html_command(input_file, ebook_type: BookType, highlighting=None):
    "highlighting=None uses default (pygments) for source code color syntax highlighting"
    assert input_file.exists(), f"Error: missing {input_file.name}"
    css_file = f"{config.base_name}-{ebook_type.value}.css".lower()
    command = (
        f"pandoc {input_file.name}"
        f" -t html -o {input_file.stem}.html"
        " --standalone"
        " --template=pandoc-template.html"
        " -f markdown-native_divs"
        " -f markdown+smart"
        " --toc-depth=2"
        f' --metadata title="{config.title}: {(input_file.stem)[4:]}"'
        f" --css={css_file}")
    if highlighting:
        command += f" --highlight-style={highlighting} "
    print(f"{input_file.stem}.html")
    os.system(command)


def html_fix_crosslinks(target_dir):
    hfm = header_to_filename_map(target_dir)
    titles = list(hfm.keys())
    cross_link = re.compile(r"\[.*?\]", flags=re.DOTALL)
    for md in target_dir.glob("*.md"):
        if "000_Front" in md.name:
            continue
        text = md.read_text()
        for lnk in cross_link.findall(text):
            link = lnk.replace("\n", " ")
            if link[1:-1] in titles:  # Trim first and last to remove []
                trans = hfm[link[1:-1]]
                new_link = f'<a target="_blank" href="{trans[1]}.html">{link[1:-1]}</a>'
                text = text.replace(lnk, new_link)
        md.write_text(text)


def html_sample_end_fixup(target_dir, end_text=""):
    tag = "{{SAMPLE_END}}"
    for md in target_dir.glob("*.md"):
        text = md.read_text()
        if tag not in text:
            continue
        lines = text.splitlines()
        i = lines.index(tag)
        md.write_text("\n".join(lines[:i]).strip() + "\n\n" + end_text)
        strip_review_notes(md)


def create_markdown_toc_for_html(target_dir):
    toc_tag = "## Table of Contents"
    index_md = config.web_sample_toc / "index.md"

    def toc_entry(name, target_url):
        return f'<p class="toc-entry"><a target="_blank" href="../htmlbook/{target_url}.html">{name}</a></p>'
    toc = [toc_entry(h, f[1]) for h, f in header_to_filename_map(
        target_dir).items()]
    old_index_md = index_md.read_text()
    assert toc_tag in old_index_md
    lines = old_index_md.splitlines()
    new_index_md = "\n".join(lines[:lines.index(toc_tag)]) + \
        f"\n{toc_tag}\n\n" + \
        "\n".join(toc)
    new_index_md = re.sub("`(.*?)`", "<code>\g<1></code>",
                          new_index_md, flags=re.DOTALL)
    index_md.write_text(new_index_md)


class Footer:
    copyright = f'\n<p class="copy">{config.copyright_notice}</p><br><br>'

    @staticmethod
    def init(target_dir):
        Footer.markdowns = sorted(target_dir.glob("*.md"))
        Footer.markdowns.pop(0)  # Remove "000_Front"
        Footer.stems = [md.stem for md in Footer.markdowns]
        Footer.nexts = deque(Footer.stems)
        Footer.nexts.rotate(-1)
        Footer.previouses = deque(Footer.stems)
        Footer.previouses.rotate(1)
        Footer.links = OrderedDict()
        for n, current in enumerate(Footer.stems):
            Footer.links[current] = (Footer.previouses[n], Footer.nexts[n])

    def __init__(self, md):
        self.md = md
        self.previous = Footer.links[md.stem][0]
        self.next = Footer.links[md.stem][1]

    def __str__(self):
        return f'<br><br><a href="{self.previous}.html">Previous</a>' + \
            "&nbsp;" * 10 + f'<a href="{self.next}.html">Next</a><br>' + \
            self.copyright


def convert_to_html(target_dir, sample: bool = True):
    """
    Pandoc markdown to html demo book for website
    """
    def patch_tags(md: Path):
        # According to Leonardo's directions
        text = re.sub("<pre.*?>(.*?)</pre>", "\g<1>",
                      md.read_text(encoding='utf-8'),
                      flags=re.DOTALL)
        text = text.replace("a.sourceLine { display: inline-block; line-height: 1.25; }",
                            "a.sourceLine { display: inline; line-height: 1.25; }")
        md.write_text(text, encoding='utf-8')

    regenerate_ebook_build_dir(target_dir, BookType.HTML)
    copy_markdown_files(target_dir, strip_notes=False)
    html_fix_crosslinks(target_dir)
    if sample:
        html_sample_end_fixup(target_dir, config.end_of_sample)
    create_markdown_toc_for_html(target_dir)
    Footer.init(target_dir)
    for md in Footer.markdowns:
        md.write_text(md.read_text() + str(Footer(md)))
    os.chdir(str(target_dir))
    for md in sorted(list(Path().glob("*.md"))):
        strip_review_notes(md)
        pandoc_html_command(md, BookType.HTML)
    for md in target_dir.rglob("*.md"):
        md.unlink()
    for html in target_dir.rglob("*.html"):
        patch_tags(html)
    pandoc_template = target_dir / "pandoc-template.html"
    if pandoc_template.exists():
        pandoc_template.unlink()
    if sample:
        # Inject results into hugo site:
        copy_tree(str(target_dir), str(config.web_html_book))
    return f"\n[{target_dir.name} Completed]"
