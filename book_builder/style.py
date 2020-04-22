import re
import book_builder.config as config
import book_builder.util as util

exclusions = set(["`it`", "`this`", "`trace`"])


def fix_missing_function_parens(md: str, fix):
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    fname = config.markdown_dir / md
    if not fname.exists():
        return f"Cannot find {fname}"
    text = fname.read_text()
    candidates = set(re.findall("`[a-z][a-zA-Z0-9_]+`", text)) - exclusions
    replacements = [(f"{c}", f"{c[:-1]}()`") for c in candidates]
    for old, new in replacements:
        print(f"{old} --> {new}")
    if fix:
        print(f"Modifying {fname.name}")
        for old, new in replacements:
            text = text.replace(old, new)
        fname.write_text(text)
