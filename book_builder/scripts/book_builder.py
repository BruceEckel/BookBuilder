# The driver script for the main program
import os
import re
from pathlib import Path

import click

import book_builder.config as config
import book_builder.examples as examples
import book_builder.util as util
import book_builder.validate as _validate
import book_builder.zubtools
from book_builder.leanpub import create_leanpub_html_website
from book_builder.leanpub import create_print_ready_manuscript
from book_builder.leanpub import git_commit_leanpub
from book_builder.leanpub import update_leanpub_manuscript
from book_builder.leanpub import recreate_leanpub_manuscript
from book_builder.leanpub import check_for_sample_end
from book_builder.renumber_atoms import fix_names_and_renumber_atoms
from book_builder.style import fix_missing_function_parens
from book_builder.website import git_commit_website
from book_builder.website import update_website_repo


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


###################### Style #############################

@cli.group()
def style():
    """Test and apply stylistic issues"""


@style.command('function_parens')
@click.argument('mdfile')
@click.option('--fix', is_flag=True)
def function_parens(mdfile, fix):
    """Fix missing function parens"""
    click.echo(fix_missing_function_parens(mdfile, fix))


###################### leanpub ###########################

@cli.group()
def leanpub():
    """Leanpub creation tools"""


@leanpub.command('test')
def test_leanpub():
    """Test recreate_leanpub_manuscript()"""
    click.echo(recreate_leanpub_manuscript())

@leanpub.command('update')
def update_leanpub():
    """Update Leanpub Github repository"""
    click.echo(update_leanpub_manuscript())
    click.echo(git_commit_leanpub("ebook"))


@leanpub.command()
def print_ready():
    """Operations for print-ready version"""
    click.echo(create_print_ready_manuscript())
    click.echo(git_commit_leanpub("print-ready"))


@leanpub.command()
def website():
    """Prepare for leanpub-generated web version of book"""
    click.echo(create_leanpub_html_website())

@leanpub.command()
def sample_end():
    """Look for missing {{SAMPLE_END}} in md files"""
    click.echo(check_for_sample_end())


###################### Website ###########################

@cli.group()
def website():
    """Maintenance"""


@website.command('update')
def update_website():
    """Update Website repository"""
    click.echo(update_website_repo())
    click.echo(git_commit_website())


##########################################################

@cli.group()
def markdown():
    """Markdown file manipulation"""


@markdown.command('combine')
def markdown_combine():
    """Combine Markdown files into a single file"""
    click.echo(util.combine_markdown_files(
        config.combined_markdown, strip_notes=False))
    os.system(f"{config.md_editor}  {config.combined_markdown}")


@markdown.command('disassemble')
@click.option('--test', is_flag=True,
              help='Unpack to "test" directory instead of overwriting Markdown.')
def markdown_disassemble(test):
    """Split combined into atom-numbered files"""
    if test:
        if config.test_dir.exists():
            click.echo(util.clean(config.test_dir))
        click.echo(util.disassemble_combined_markdown_file(config.test_dir))
    else:
        click.echo(util.disassemble_combined_markdown_file())


@markdown.command('renumber')
def markdown_renumber():
    """Renumber atoms and fix atom names"""
    click.echo(fix_names_and_renumber_atoms())


##########################################################


@cli.group()
def z():
    """Subtools for special needs"""


@z.command()
def missing_code_markers():
    """
    Check for missing ```kotlin
    """
    click.echo(book_builder.zubtools.find_missing_listing_header())


@z.command()
def check_kotlin():
    """
    Check for improper usage of "Kotlin"
    """
    click.echo(book_builder.zubtools.check_kotlin_usage())

@z.command()
def check_packages():
    """
    Packages not in their named directory
    """
    click.echo("Not implemented")


@z.command()
def check_exercises():
    """
    Find any atoms without 3 exercises
    """
    click.echo(book_builder.zubtools.check_exercise_count())


@z.command()
def check_crosslinks():
    """
    Display potential links
    """
    click.echo(book_builder.zubtools.check_crosslink_references())


@z.command()
def fix_crosslinks():
    """
    Create Leanpub-style crosslinks
    """
    click.echo(book_builder.zubtools.fix_crosslink_references())


@z.command()
def notes():
    """Show all {{ Notes }} and incomplete atoms"""
    for md in config.markdown_dir.glob("*.md"):
        text = md.read_text()
        curly_notes = set(re.findall("{{.*?}}", text, flags=re.DOTALL))
        curly_notes.discard("{{SAMPLE_END}}")
        if "This Atom is Incomplete" in text:
            curly_notes.add("This Atom is Incomplete")
        if curly_notes:
            print(md.name, end=': ')
            for cn in curly_notes:
                print(cn)
            print("-" * 40)


@z.command()
def imports_and_packages():
    """
    One of each import/package statement in the book
    """
    click.echo(book_builder.zubtools.find_imports_and_packages())

@z.command()
def classes():
    """
    One of each import/package statement in the book
    """
    click.echo(book_builder.zubtools.find_classes())


# @z.command()
# def test():
#     """Perform current test"""
#     from book_builder.ebook_generators import show_important_kindlegen_output
#     click.echo(show_important_kindlegen_output("AtomicKotlin-monochrome"))
#     # click.echo(_validate.test_markdown_individually())

##########################################################
