import re
from pprint import pprint
import book_builder.config as config
import book_builder.util as util

exclusions = set(["`it`", "`this`", "`trace`"])

def find_missing_function_parens(md: str):
    if not config.markdown_dir.exists():
        return f"Cannot find {config.markdown_dir}"
    fname = config.markdown_dir / md
    if not fname.exists():
        return f"Cannot find {fname}"
    print(f"testing {md}")
    text = fname.read_text()
    candidates = set(re.findall("`[a-z][a-zA-Z0-9_]+`", text)) - exclusions
    pprint(candidates)
