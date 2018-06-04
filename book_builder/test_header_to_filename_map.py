from util import header_to_filename_map
import pprint
from pathlib import Path

test_path = Path(r"C:\Users\Bruce\Documents\Git\AtomicKotlin\Markdown")
print(test_path)

pprint.pprint(header_to_filename_map(test_path))