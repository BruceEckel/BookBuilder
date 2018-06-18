# The driver script for the main program
import os
import re
import click
import book_builder.config as config
import book_builder.util as util
import book_builder.examples as examples
import book_builder.packages as _packages
import book_builder.validate as _validate
from book_builder.ebook_generators import convert_to_epub
from book_builder.ebook_generators import convert_to_mobi
from book_builder.ebook_generators import convert_to_docx
from book_builder.ebook_generators import convert_to_html
from book_builder.ebook_generators import create_release
from book_builder.ebook_generators import generate_epub_bug_demo_file
from book_builder.renumber_atoms import fix_names_and_renumber_atoms
import book_builder.zubtools


@click.group()
@click.version_option()
def cli():
    """Book Builder

    Provides all book building and testing utilities under a single central command.
    """


##########################################################


@cli.group()
def code():
    """Code extraction and testing."""


@code.command('clean')
def code_clean():
    "Remove directory containing extracted example code"
    click.echo(examples.clean())


@code.group('extract')
def code_extract():
    "Choose how to extract examples from book's Markdown files"


@code_extract.command('with_duplicates')
def with_duplicates():
    "Keep duplicate filenames"
    click.echo(examples.extractExamples())
    if config.language_name.lower() == "kotlin" or "java":
        click.echo(examples.create_test_files())
        click.echo(examples.create_tasks_for_gradle(check_for_duplicates=False))


@code_extract.command('without_duplicates')
def without_duplicates():
    "Remove duplicate filenames"
    click.echo(examples.extractExamples())
    if config.language_name.lower() == "kotlin" or "java":
        click.echo(examples.create_test_files())
        click.echo(examples.create_tasks_for_gradle(check_for_duplicates=True))


@code.command('exec_run_sh')
def code_exec_run_sh():
    "Make run.sh files executable via git"
    click.echo(examples.make_all_run_sh_executable())


##########################################################

@cli.command()
@click.option('--trace', default="")
def validate(trace):
    "Validation tests"
    click.echo(_validate.Validator.all_checks(trace))


##########################################################


# @cli.command()
# def fix():
#     "Batch fixes"
#     click.echo(_fix.all_fixes())


##########################################################

@cli.group()
def epub():
    "Creates epub"


@epub.command('clean')
def epub_clean():
    "Remove directory containing epub"
    click.echo(util.clean(config.epub_build_dir))


@epub.command('regen')
def epub_regen():
    "Create and populate epub build dir"
    click.echo(util.regenerate_epub_build_dir())


@epub.command('build')
def epub_build():
    "Create epub from Markdown files"
    click.echo(convert_to_epub())


@epub.command('bugdemo')
@click.option('--mdfile', prompt='Markdown File Name')
def epub_bugdemo(mdfile):
    "Create EPUB file from single Markdown file, to demonstrate epub reader bugs"
    click.echo(generate_epub_bug_demo_file(mdfile))


##########################################################

@cli.group()
def markdown():
    "Markdown file manipulation"


@markdown.command('combine')
def markdown_combine():
    "Combine Markdown files into a single file"
    click.echo(util.combine_markdown_files(
        config.combined_markdown, strip_notes=False))
    os.system(f"{config.md_editor}  {config.combined_markdown}")


@markdown.command('disassemble')
@click.option('--test', is_flag=True,
              help='Unpack to "test" directory instead of overwriting Markdown.')
def markdown_disassemble(test):
    "Split combined into atom-numbered files"
    if test:
        if config.test_dir.exists():
            click.echo(util.clean(config.test_dir))
        click.echo(util.disassemble_combined_markdown_file(config.test_dir))
    else:
        click.echo(util.disassemble_combined_markdown_file())


@markdown.command('renumber')
def markdown_renumber():
    "Renumber atoms and fix atom names"
    click.echo(fix_names_and_renumber_atoms())


# @epub.command('sample_markdown')
# def epub_sample_markdown():
#     "Combine sample Markdown files into a single Markdown file"
#     click.echo(util.combine_sample_markdown(config.sample_markdown))
#     os.system(f"{config.md_editor}  {config.sample_markdown}")


# @epub.command('newStatus')
# def epub_create_new_status_file():
#     "Create fresh STATUS.md if one doesn't exist"
#     click.echo(util.create_new_status_file())


##########################################################

@cli.group()
def mobi():
    "Creates mobi files for kindle"


@mobi.command('build')
def mobi_build():
    "Create epub from Markdown files"
    click.echo(convert_to_mobi())


##########################################################

@cli.group()
def docx():
    "Create docx file for print version"


@docx.command('build')
def docx_build():
    "Create docx from Markdown files"
    click.echo(convert_to_docx())


##########################################################

@cli.group()
def html():
    "Create html ebook"


@html.command('build')
def html_build():
    "Create html from Markdown files"
    click.echo(convert_to_html())


##########################################################


@cli.command()
def release():
    "Create full release from scratch"
    click.echo(create_release())


##########################################################


@cli.command()
def notes():
    "Show all {{ Notes }} and atoms under construction except {{SAMPLE_END}}"
    for md in config.markdown_dir.glob("*.md"):
        text = md.read_text()
        curly_notes = set(re.findall("{{.*?}}", text, flags=re.DOTALL))
        curly_notes.discard("{{SAMPLE_END}}")
        if "Under Construction" in text:
            curly_notes.add("Under Construction")
        if curly_notes:
            print(md.name)
            for cn in curly_notes:
                print(cn)
            print("-" * 40)


##########################################################


@cli.command()
def edit():
    "Edit BookBuilder files using VS Code"
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    os.chdir("..")
    os.system(f"{config.code_editor} .")


##########################################################


@cli.group()
def z():
    "Subtools for special needs"


@z.command()
def remove_ready_boxes():
    """
    Remove + [ ] Ready for Review, + [ ] Tech Checked, convert + Notes: to {{}}
    """
    click.echo(book_builder.zubtools.remove_checkboxes())


@z.command()
def test():
    "Perform current test"
    from book_builder.ebook_generators import show_important_kindlegen_output
    click.echo(show_important_kindlegen_output("AtomicKotlin-monochrome"))
    # click.echo(_validate.test_markdown_individually())


@z.command('unpackaged')
def packages_unpackaged():
    "Show all examples that aren't in packages"
    click.echo(_packages.unpackaged())

# @z.command('add')
# def packages_add_packages():
#     "Add package statements to all examples that don't have them"
#     click.echo(_packages.add_packages())


##########################################################
