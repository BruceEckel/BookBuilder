import book_builder.config as config


def create_book_txt():
    """
    Make the Book.txt file which determines the chapters and their order for the Leanpub book.
    """
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    (config.markdown_dir / "Book.txt").write_text(
        "\n".join([md.name for md in config.markdown_dir.glob("*.md")]).strip())
