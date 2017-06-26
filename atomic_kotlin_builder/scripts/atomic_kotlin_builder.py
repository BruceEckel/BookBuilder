# The driver script for the main program
import click
import atomic_kotlin_builder.examples as examples
import atomic_kotlin_builder.packages as _packages
import atomic_kotlin_builder.validate as _validate
from atomic_kotlin_builder.util import *


@click.group()
@click.version_option()
def cli():
    """Atomic Kotlin Builder

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


@code.command('extract')
def code_extract():
    "Extract examples from book's Markdown files"
    click.echo(examples.extractExamples())


@code.command('testall')
def code_test_all_examples():
    "Compile and capture all results, to show percentage of rewritten examples"
    click.echo(examples.compile_all_examples())


@code.command('testfiles')
def code_test_files():
    "Create test.bat files for each package, to compile and run all files"
    click.echo(examples.create_test_files())


##########################################################


@cli.group()
def packages():
    """Discover and fix package issues"""


@packages.command('unpackaged')
def packages_unpackaged():
    "Show all examples that aren't in packages"
    click.echo(_packages.unpackaged())


@packages.command('add')
def packages_add_packages():
    "Add package statements to all examples that don't have them"
    click.echo(_packages.add_packages())

##########################################################


@cli.group()
def validate():
    """Various validation tools"""


@validate.command('general')
def validate_general():
    "A collection of validation tests"
    click.echo(_validate.general())


@validate.command('markdown_names')
def validate_markdown_names():
    "Check Markdown file names against chapter titles"
    click.echo(_validate.markdown_names())


# @validate.command('add')
# def validate_add_packages():
#     "Add package statements to all examples that don't have them"
#     click.echo(_validate.add_packages())


##########################################################

@cli.group()
def epub():
    "Creates Atomic Kotlin epub"


@epub.command('clean')
def epub_clean():
    "Remove directory containing epub"
    click.echo("Not implemented yet")


@epub.command('combine')
def epub_combine():
    "Combine Markdown files into a single file"
    click.echo(combine_markdown_files())
    os.system("subl {}".format(config.combined_markdown))


@epub.command('disassemble')
def epub_disassemble():
    "Split combined Markdown file into atom-numbered markdown files"
    # if config.test_dir.exists():
    #     clean(config.test_dir)
    # click.echo(disassemble_combined_markdown_file(config.test_dir))
    click.echo(disassemble_combined_markdown_file())


# @epub.command('new')
# @click.argument('name')
# def epub_new(name):
#     """Creates a new epub."""
#     click.echo('Created epub %s' % name)


# @epub.command('move')
# @click.argument('epub')
# @click.argument('x', type=float)
# @click.argument('y', type=float)
# @click.option('--speed', metavar='KN', default=10,
#               help='Speed in knots.')
# def epub_move(epub, x, y, speed):
#     """Moves epub to the new location X,Y."""
#     click.echo('Moving epub %s to %s,%s with speed %s' % (epub, x, y, speed))


# @epub.command('shoot')
# @click.argument('epub')
# @click.argument('x', type=float)
# @click.argument('y', type=float)
# def epub_shoot(epub, x, y):
#     """Makes epub fire to X,Y."""
#     click.echo('epub %s fires to %s,%s' % (epub, x, y))
