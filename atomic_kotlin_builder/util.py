#! py -3
# Utilities

def create_markdown_filename(h1):
    fn = h1.replace(": ", "_")
    fn = fn.replace(" ", "_") + ".md"
    fn = fn.replace("&", "and")
    fn = fn.replace("?", "")
    fn = fn.replace("+", "P")
    fn = fn.replace("/", "")
    fn = fn.replace("-", "_")
    fn = fn.replace("(", "")
    fn = fn.replace(")", "")
    fn = fn.replace("`", "")
    fn = fn.replace(",", "")
    fn = fn.replace("!", "")
    return fn

def create_numbered_markdown_filename(h1, n):
    return "%02d_" % n + create_markdown_filename(h1)
