import book_builder.config as config
import shutil

leanpub_repo = config.root_path.parent / "AtomicKotlinLeanpub"
manuscript_dir = leanpub_repo / "manuscript"


def update_leanpub_repo():
    """
    Make the Book.txt file which determines the chapters and their order for the Leanpub book.
    """
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    if not leanpub_repo.exists():
        return f"Cannot find {leanpub_repo}"
    if manuscript_dir.exists():
        shutil.rmtree(manuscript_dir)
    shutil.copytree(config.markdown_dir, manuscript_dir)
    (manuscript_dir / "Book.txt").write_text(
        "\n".join([md.name for md in config.markdown_dir.glob("*.md")]).strip())
