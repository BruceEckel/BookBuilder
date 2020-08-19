import os
import re
import shutil

import book_builder.config as config
from book_builder.util import pushd

exercise_message = "***Exercises and solutions for this atom can be found at [AtomicKotlin.com](https://www.atomickotlin.com/exercises/).***"

leanpub_repo = config.root_path.parent / "AtomicKotlinLeanpub"
manuscript_dir = leanpub_repo / "manuscript"
manuscript_images = manuscript_dir / "images"


def generate_leanpub_manuscript(with_sample=True):
    """
    Create a new version of the Leanpub book
    Make the Book.txt file which determines the chapters and their order for the Leanpub book.
    """
    success, fail_msg = recreate_leanpub_manuscript()
    if not success:
        return False, fail_msg
    (manuscript_dir / "Book.txt").write_text(
        "\n".join([md.name for md in config.markdown_dir.glob("*.md")]).strip())
    if with_sample:
        create_sample_txt()
    strip_double_curly_tags()
    return True, "Succeeded"


def generate_print_ready_manuscript():
    """
    So everything is monochrome in resulting PDF
    """
    success, fail_msg = generate_leanpub_manuscript(with_sample=False)
    if not success:
        return fail_msg
    for md in manuscript_dir.glob("*.md"):
        text = md.read_text()
        text = text.replace("```kotlin", "```text")
        text = text.replace("```java", "```text")
        md.write_text(text)


def recreate_leanpub_manuscript():
    if not config.markdown_dir.exists():
        return False, f"Cannot find {config.markdown_dir}"
    if not leanpub_repo.exists():
        return False, f"Cannot find {leanpub_repo}"
    if manuscript_dir.exists():
        shutil.rmtree(manuscript_dir, ignore_errors=True)
    shutil.copytree(config.markdown_dir, manuscript_dir)
    for id in [id for id in manuscript_images.iterdir() if id.is_dir()]:
        shutil.rmtree(id, ignore_errors=True)
    for md in manuscript_dir.glob("*.md"):
        text = re.sub(r"!\[(.*?)\]\(images/.+?/(.+?)\)", r"![\1](images/\2)", md.read_text())
        result = []
        for line in text.splitlines():
            if line == "## Exercises":
                result.append(exercise_message)
                break
            else:
                result.append(line)
        md.write_text("\n".join(result) + "\n")
    return True, "Succeeded"


def create_sample_txt():
    """Use first 35 atoms, Leanpub can only put in entire files at a time"""

    def table_of_contents():
        toc = []
        for md in manuscript_dir.glob("*.md"):
            title = md.read_text().splitlines()[0]
            toc.append(title.split("{")[0][2:])
        return toc

    if not manuscript_dir.exists():
        return f"Cannot find {manuscript_dir}"
    atom_names = sorted([md.name for md in manuscript_dir.glob("*.md")])
    sample_names = atom_names[:36]
    sample_txt = manuscript_dir / "Sample.txt"
    sample_txt.write_text("About.txt\n" + "\n".join(sample_names) + "\n")
    shutil.copy(config.resource("About.txt"), manuscript_dir)
    about_txt = manuscript_dir / "About.txt"
    sample_description = about_txt.read_text()
    sample_description += "\n".join(["- " + atom for atom in table_of_contents()])
    about_txt.write_text(sample_description)


def strip_double_curly_tags():
    """Remove entirely"""
    if not manuscript_dir.exists():
        return f"Cannot find {manuscript_dir}"
    for md in manuscript_dir.glob("*.md"):
        # print(f"{md.name}: Removing double curlies")
        de_tagged = re.sub(r"{{.+?}}", "", md.read_text())
        md.write_text(de_tagged)


def create_leanpub_html_website():
    """
    Set up to get leanpub to generate HTML output.
    Use {{SAMPLE_END}} tags to create some portion of every chapter, so
    The table of contents contains the entire book.
    """
    success, fail_msg = recreate_leanpub_manuscript()
    if not success:
        return fail_msg
    for md in manuscript_dir.glob("*.md"):
        sample = md.read_text()
        if "{{SAMPLE_END}}" in sample:
            # NOTE: Won't work if {{SAMPLE_END}} has already been removed:
            sample = sample.split("{{SAMPLE_END}}")[0] + "\n***End of Sample***"
            md.write_text(sample)

    # Also add ABOUT.TXT
    atom_list = "ABOUT.TXT\n" + "\n".join([md.name for md in manuscript_dir.glob("*.md")]).strip()
    (manuscript_dir / "Book.txt").write_text(atom_list)
    shutil.copy(config.resource("About.txt"), manuscript_dir)
    about_txt = manuscript_dir / "About.txt"
    about = about_txt.read_text().split("## Complete Table of Contents")[0]
    about_txt.write_text(about)


def git_commit_leanpub(msg):
    """
    Commit current leanpub version to github repo
    """
    with pushd(leanpub_repo):
        os.system(f"""git commit -a -m "{msg}" """)
        os.system("git push")


def check_for_sample_end():
    """
    Look for missing {{SAMPLE_END}} in md files
    """
    for md in config.markdown_dir.glob("*.md"):
        text = md.read_text()
        if "_Section_" in md.name or "Appendices.md" in md.name:
            print(f"{md.name}")
            continue
        if "AtomicTest.md" in md.name: continue
        if int(md.name[0:3]) < 31: continue
        if "{{SAMPLE_END}}" not in text:
            print(f"-> {md.name}\tNO {{SAMPLE_END}}")
