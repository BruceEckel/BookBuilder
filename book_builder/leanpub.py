import book_builder.config as config
import shutil
import re
import pprint

leanpub_repo = config.root_path.parent / "AtomicKotlinLeanpub"
manuscript_dir = leanpub_repo / "manuscript"


def modify_exercise_numbers():
    if not manuscript_dir.exists():
        return f"Cannot find {leanpub_repo}"
    for md in manuscript_dir.glob("*.md"):
        print(md.name)
        text = md.read_text()
        # exercises = re.findall(r"##### (\d+)\.\s+", text)
        # pprint.pprint(exercises)
        modified = re.sub(r"##### (\d+)\.\s+", r"\1. ", text)
        md.write_text(modified)



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
    modify_exercise_numbers()
