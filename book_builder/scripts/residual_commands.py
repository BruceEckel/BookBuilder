# The driver script for the main program
import os
import re
from pathlib import Path

import click

import book_builder.config as config
import book_builder.examples as examples
import book_builder.packages as _packages
import book_builder.util as util
import book_builder.validate as _validate
import book_builder.zubtools
from book_builder.ebook_generators import convert_to_docx
from book_builder.ebook_generators import convert_to_epub
from book_builder.ebook_generators import convert_to_mobi
from book_builder.ebook_generators import create_release
from book_builder.ebook_generators import generate_epub_bug_demo_file
from book_builder.html_generator import convert_to_html
from book_builder.renumber_atoms import fix_names_and_renumber_atoms
from book_builder.style import fix_missing_function_parens
from book_builder.leanpub import update_leanpub_manuscript
from book_builder.leanpub import create_print_ready_manuscript
from book_builder.leanpub import git_commit_leanpub
from book_builder.website import update_website_repo
from book_builder.website import git_commit_website
from book_builder.website import create_website_toc


@click.group()
@click.version_option()
def cli():
    """Book Builder

    Provides all book building and testing utilities under a single central command.
    """


##########################################################


@cli.group()
def code():
    """Code extraction and testing"""


@code.command('clean')
def code_clean():
    """Remove directory containing extracted example code"""
    click.echo(examples.clean())


@code.group('extract')
def code_extract():
    """Choose how to extract examples from book's Markdown files"""


@code_extract.command('with_duplicates')
def with_duplicates():
    """Keep duplicate filenames"""
    click.echo(examples.extractExamples())
    if config.language_name.lower() == "kotlin" or "java":
        click.echo(examples.create_test_files())
        click.echo(examples.create_tasks_for_gradle(
            check_for_duplicates=False))


@code_extract.command('without_duplicates')
def without_duplicates():
    """Remove duplicate filenames"""
    click.echo(examples.extractExamples())
    if config.language_name.lower() == "kotlin" or "java":
        click.echo(examples.create_test_files())
        click.echo(examples.create_tasks_for_gradle(check_for_duplicates=True))


@code.command('exec_run_sh')
def code_exec_run_sh():
    """Make run.sh files executable via git"""
    click.echo(examples.make_all_run_sh_executable())


################### Validation ###########################

@cli.group()
def validate():
    """Validation testing"""


@validate.command()
@click.option('--trace', default="")
def all(trace):
    """Run all tests"""
    click.echo(_validate.Validator.all_checks(trace))


gen_validators = Path(__file__).parent.parent / "generated_validators.py"
exec(gen_validators.read_text())


##########################################################


# @cli.command()
# def fix():
#     "Batch fixes"
#     click.echo(_fix.all_fixes())


##########################################################

@cli.group()
def epub():
    """Creates epub"""


@epub.command('clean')
def epub_clean():
    """Remove directory containing epub"""
    click.echo(util.clean(config.epub_build_dir))


@epub.command('regen')
def epub_regen():
    """Create and populate epub build dir"""
    click.echo(util.regenerate_epub_build_dir())


@epub.command('build')
def epub_build():
    """Create epub from Markdown files"""
    click.echo(convert_to_epub())


@epub.command('bugdemo')
@click.option('--mdfile', prompt='Markdown File Name')
def epub_bugdemo(mdfile):
    """Create EPUB file from single Markdown file, to demonstrate epub reader bugs"""
    click.echo(generate_epub_bug_demo_file(mdfile))


##########################################################

@cli.group()
def mobi():
    """Creates mobi files for kindle"""


@mobi.command('build')
def mobi_build():
    """Create epub from Markdown files"""
    click.echo(convert_to_mobi())


##########################################################

@cli.group()
def docx():
    """Create docx file for print version"""


@docx.command('build')
def docx_build():
    """Create docx from Markdown files"""
    click.echo(convert_to_docx())


##########################################################

@cli.group()
def html():
    """Create html ebook"""


@html.command('clean')
def html_clean():
    """Remove build directories containing html"""

    def remove(path):
        click.echo(util.clean(path))

    remove(config.html_sample_dir)
    remove(config.html_complete_dir)
    remove(config.html_stripped_dir)


@html.command('sample')
def html_build_sample():
    """Create sample html from Markdown files"""
    click.echo(convert_to_html(config.html_sample_dir, sample=True))


@html.command('complete')
def html_build_complete():
    """Create complete html from Markdown files"""
    click.echo(convert_to_html(config.html_complete_dir, sample=False))


##########################################################


@cli.command()
def release():
    """Create full release from scratch"""
    click.echo(create_release())


##########################################################


# @cli.command()
# def edit():
#     """Edit BookBuilder files using VS Code"""
#     os.chdir(os.path.dirname(os.path.realpath(__file__)))
#     os.chdir("..")
#     os.system(f"{config.code_editor} .")


##########################################################


@cli.group()
def z():
    """Subtools for special needs"""


@z.command()
def new_heading1():
    """
    Change to new heading 1
    """
    click.echo(book_builder.zubtools.change_to_new_heading1())


@z.command()
def new_heading2():
    """
    Change to new heading 2
    """
    click.echo(book_builder.zubtools.change_to_new_heading2())


@z.command()
def remove_ready_boxes():
    """
    Remove + [ ] Ready for Review, + [ ] Tech Checked, convert + Notes: to {{}}
    """
    click.echo(book_builder.zubtools.remove_checkboxes())


@z.command()
def check_pre_tags():
    """
    Make sure all <pre class="sourceCode kotlin"> are followed by <code class="sourceCode kotlin">
    """
    click.echo(book_builder.zubtools.find_pre_and_code_tags_in_html())


@z.command()
def test():
    """Perform current test"""
    from book_builder.ebook_generators import show_important_kindlegen_output
    click.echo(show_important_kindlegen_output("AtomicKotlin-monochrome"))
    # click.echo(_validate.test_markdown_individually())


@z.command('unpackaged')
def packages_unpackaged():
    """Show all examples that aren't in packages"""
    click.echo(_packages.unpackaged())

# @z.command('add')
# def packages_add_packages():
#     "Add package statements to all examples that don't have them"
#     click.echo(_packages.add_packages())


##########################################################
