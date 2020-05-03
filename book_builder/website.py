import re
import shutil
import os
import book_builder.config as config
from book_builder.util import pushd

website_repo = config.root_path.parent / "AtomicKotlin-hugo"
sample_dir = website_repo / "content"
toc_file = sample_dir / "sample" / "index.md"


def create_website_toc():
    """Produce annotated table of contents for website"""
    toc = []
    highlight = "***"
    if not config.markdown_dir.exists():
        raise Exception(f"Cannot find {config.markdown_dir}")
    for md in config.markdown_dir.glob("*.md"):
        text = md.read_text()
        lines = text.splitlines()
        first = lines[0]
        if "Copyright" in first:
            continue
        if first.startswith("-#"):
            tag = "##"
        else:
            tag = "- "
        title = ((first.split("{")[0]).split(maxsplit=1)[1]).strip()
        if "**This Atom is Incomplete**" in text:
            toc.append(f"{tag}  {title} (In Progress)")
        else:
            if tag == "##":
                toc.append(f"{tag}  {title}")
            else:
                toc.append(f"{tag}  {highlight}{title}{highlight}")
        # print(toc[-1])
        if "`when` Expressions" in first:
            highlight = ""
    return "\n".join(toc)


def update_website_repo():
    """
    Make the Book.txt file which determines the chapters and their order for the Leanpub book.
    """
    if not website_repo.exists():
        return f"Cannot find {website_repo}"
    if not sample_dir.exists():
        return f"Cannot find {sample_dir}"
    if not toc_file.exists():
        return f" Cannot find {toc_file}"
    toc = create_website_toc()
    toc_head = toc_file.read_text().split("##  Section I: Programming Basics")[0]
    new_toc = toc_head + toc + "\n"
    print(new_toc)
    toc_file.write_text(new_toc)




def git_commit_website():
    """
    Commit current website version to github repo
    """
    with pushd(website_repo):
        os.system(f"""git commit -a -m "auto-update from book" """)
        os.system("git push")
