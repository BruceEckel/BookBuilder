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
from book_builder.leanpub import update_leanpub_repo
from book_builder.leanpub import modify_for_print_ready


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


@leanpub.command('update')
def update_leanpub():
    """Update Leanpub Github repository"""
    click.echo(update_leanpub_repo())


@leanpub.command()
def print_ready():
    """Operations for print-ready version"""
    click.echo(update_leanpub_repo())
    click.echo(modify_for_print_ready())


# @leanpub.command('test')
# def leanpub_test():
#     """Test modify_exercise_numbers()"""
#     click.echo(modify_exercise_numbers())


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


@cli.command()
def notes():
    """Show all {{ Notes }} and atoms under construction except {{SAMPLE_END}}"""
    for md in config.markdown_dir.glob("*.md"):
        text = md.read_text()
        curly_notes = set(re.findall("{{.*?}}", text, flags=re.DOTALL))
        curly_notes.discard("{{SAMPLE_END}}")
        if "Under Construction" in text:
            curly_notes.add("Under Construction")
        if curly_notes:
            print(md.name, end=': ')
            for cn in curly_notes:
                print(cn)
            print("-" * 40)


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
