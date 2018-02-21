"""
Generate ebooks in different formats
"""
import os
import re
from pathlib import Path
import zipfile
from itertools import chain
import book_builder.config as config
from book_builder.config import BookType
from book_builder.config import epub_name
from book_builder.util import clean
from book_builder.util import regenerate_ebook_build_dir
from book_builder.util import combine_markdown_files
from book_builder.util import combine_sample_markdown
from book_builder.util import retain_files


def pandoc_epub_command(
        input_file,
        output_name,
        title,
        ebook_type: BookType,
        highlighting=None):
    "highlighting=None uses default (pygments) for source code color syntax highlighting"
    print(f"\tPandoc producing {output_name}")
    assert input_file.exists(), "Error: missing " + input_file.name
    command = (
        f"pandoc {input_file.name}"
        f" -t epub3 -o {output_name}"
        " -f markdown-native_divs"
        " -f markdown+smart "
        # ' --epub-subdirectory="" '
        " --epub-cover-image=Cover.png " +
        " ".join([f"--epub-embed-font={font.name}" for font in
                  chain(config.bullets.glob("*"), config.fonts.glob("*.ttf"))])
        + " --toc-depth=2 "
        f'--metadata title="{title}"'
        f" --css={config.base_name}-{ebook_type.value}.css ")
    if highlighting:
        command += f" --highlight-style={highlighting} "
    os.system(command)


def generate_epub_files(target_dir, markdown_name, ebook_type: BookType):
    """
    Pandoc markdown to epub
    """
    regenerate_ebook_build_dir(target_dir, ebook_type)
    combine_markdown_files(markdown_name("assembled-stripped"), strip_notes=True)
    combine_sample_markdown(markdown_name("sample"))
    os.chdir(str(target_dir))
    print(f"Producing {target_dir.name}")
    pandoc_epub_command(
        markdown_name("assembled-stripped"),
        epub_name(),
        config.title,
        ebook_type)
    pandoc_epub_command(
        markdown_name("sample"),
        epub_name("-Sample"),
        config.title + " Sample",
        ebook_type)

    if ebook_type is BookType.MOBI:
        ebook_type = BookType.MOBIMONO
    pandoc_epub_command(
        markdown_name("assembled-stripped"),
        epub_name("-monochrome"),
        config.title,
        ebook_type,
        highlighting="monochrome")
    pandoc_epub_command(
        markdown_name("sample"),
        epub_name("-monochrome-Sample"),
        config.title + " Sample",
        ebook_type,
        highlighting="monochrome")


def fix_for_apple(name):
    epub = zipfile.ZipFile(name, "a")
    epub.write(config.meta_inf, "META-INF")
    epub.close()


def convert_to_epub():
    """
    Pandoc markdown to epub
    """
    generate_epub_files(config.epub_build_dir, config.epub_md, BookType.EPUB)
    # fix_for_apple(epub_name())
    # fix_for_apple(epub_name("-Sample"))
    retain_files(config.epub_build_dir, ["epub"])
    return f"\n{config.epub_build_dir.name} Completed"


def show_important_kindlegen_output(fname_stem):
    "Removes unimportant errors"
    skip = [
        "Amazon kindlegen(Windows)",
        "'position: absolute'",
        "'position: relative'",
        "'overflow'",
        "Added metadata",
        "Info(prcgen)",
        "Info(pagemap)",
        "Warning(prcfile):W14029"
    ]
    path = config.mobi_build_dir / f"{fname_stem}-kindlegen-messages.txt"
    messages = re.split("\n\n", path.read_text())
    cleaned = []
    for n, msg in enumerate(messages):
        if any([s in msg for s in skip]):
            continue
        cleaned.append(msg)
    if cleaned:
        for m in [m for m in cleaned if m.strip()]:
            print(m)


def convert_to_mobi():
    """
    Pandoc markdown to mobi
    Create special EPUBs first in this directory that use AtomicKotlin-mobi.css
    """
    generate_epub_files(config.mobi_build_dir, config.mobi_md, BookType.MOBI)
    os.chdir(str(config.mobi_build_dir))
    for epf in Path('.').glob("*.epub"):
    # for epf in [Path() / "AtomicKotlin-monochrome.epub"]:
        cmd = f"kindlegen {epf.name} > {epf.stem}-kindlegen-messages.txt"
        print(f"\tCreating {epf.stem}.mobi")
        os.system(cmd)
        show_important_kindlegen_output(epf.stem)
        # os.system(f"start AtomicKotlin-monochrome.mobi")
    retain_files(config.mobi_build_dir, ["mobi"])
    return f"{config.mobi_build_dir.name} Completed"


def pandoc_docx_command(input_file, output_name, title):
    assert input_file.exists(), f"Error: missing {input_file.name}"
    command = (
        "pandoc " + str(input_file.name) +
        " -t docx -o " + output_name +
        " -f markdown-native_divs "
        " -f markdown+smart "
        " --toc-depth=2 " +
        f'--metadata title="{title}"' +
        " --css=" + config.base_name + ".css ")
    print(command)
    os.system(command)


def convert_to_docx():
    """
    Pandoc markdown to docx
    """
    regenerate_ebook_build_dir(config.docx_build_dir, BookType.DOCX)
    combine_markdown_files(config.docx_md("assembled-stripped"), strip_notes=True)
    os.chdir(str(config.docx_build_dir))
    pandoc_docx_command(
        config.docx_md("assembled-stripped"), config.base_name + ".docx", config.title)
    return f"{config.docx_build_dir.name} Completed"


def create_release():
    "Create a release from scratch"
    import glob
    if config.release_dir.exists():
        clean(config.release_dir)
    os.makedirs(config.release_dir)
    convert_to_epub()
    convert_to_mobi()
    for src in config.built_ebooks:
        os.system(f"cp {config.epub_build_dir / src} {config.release_dir}")
    os.chdir(str(config.release_dir))

    def zzip(target_name, file_list):
        "zip utility"
        print(f"creating {target_name}.zip")
        os.system(f"zip -m {target_name}.zip {' '.join(file_list)}")

    files = glob.glob("*")
    zzip(config.base_name, [f for f in files if not "Sample" in f])
    zzip(config.base_name + "Sample", [f for f in files if "Sample" in f])
    retain_files(config.release_dir, ["zip"])
    return f"\n{config.release_dir} Completed"
