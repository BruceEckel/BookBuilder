import re
import shutil
import os
import book_builder.config as config
from book_builder.util import pushd

leanpub_repo = config.root_path.parent / "AtomicKotlinLeanpub"
manuscript_dir = leanpub_repo / "manuscript"


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
        text = md.read_text()
        # tags = re.findall(r"{{.+?}}", text)
        # if tags:
        #     print(f"-{{}} {md.name}")
        #     for tag in tags:
        #         print(tag)
        de_tagged = re.sub(r"{{.+?}}", "", text)
        md.write_text(de_tagged)


def update_leanpub_repo():
    """
    Make the Book.txt file which determines the chapters and their order for the Leanpub book.
    """
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    if not leanpub_repo.exists():
        return f"Cannot find {leanpub_repo}"
    if manuscript_dir.exists():
        shutil.rmtree(manuscript_dir, ignore_errors=True)
    shutil.copytree(config.markdown_dir, manuscript_dir)
    (manuscript_dir / "Book.txt").write_text(
        "\n".join([md.name for md in config.markdown_dir.glob("*.md")]).strip())
    create_sample_txt()
    strip_double_curly_tags()


def modify_for_print_ready():
    """
    So that everything is monochrome in resulting PDF
    Change ```kotlin to ```text
    Change ```java to ```text
    """
    if not manuscript_dir.exists():
        return f"Cannot find {manuscript_dir}"
    for md in manuscript_dir.glob("*.md"):
        print(f"-> {md.name}")
        text = md.read_text()
        text = text.replace("```kotlin", "```text")
        text = text.replace("```java", "```text")
        # for line in text.splitlines():
        #     if line.strip() == "```": continue
        #     if line.startswith("```"):
        #         print(line)
        md.write_text(text)


def git_commit_leanpub(msg):
    """
    Commit current leanpub version to github repo
    """
    with pushd(leanpub_repo):
        os.system(f"""git commit -a -m "{msg}" """)
        os.system("git push")


#
# def modify_exercise_numbers():
#     for md in config.markdown_dir.glob("*.md"):
#         print(md.name)
#         text = md.read_text()
#         # exercises = re.findall(r"##### (\d+)\.\s+", text)
#         # pprint.pprint(exercises)
#         modified = re.sub(r"##### (\d+)\.", r"##### Exercise \1", text)
#         md.write_text(modified)
