# The driver script for the main program
import click


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


@code.command('delete')
def code_delete():
    """Removes a code at a specific coordinate."""
    click.echo("code directory removed")


@code.command('set')
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.option('ty', '--moored', flag_value='moored',
              default=True,
              help='Moored (anchored) code. Default.')
@click.option('ty', '--drifting', flag_value='drifting',
              help='Drifting code.')
def code_set(x, y, ty):
    """Sets a code at a specific coordinate."""
    click.echo('Set %s code at %s,%s' % (ty, x, y))


##########################################################

@cli.group()
def epub():
    """Manages epubs."""


@epub.command('new')
@click.argument('name')
def epub_new(name):
    """Creates a new epub."""
    click.echo('Created epub %s' % name)


@epub.command('move')
@click.argument('epub')
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.option('--speed', metavar='KN', default=10,
              help='Speed in knots.')
def epub_move(epub, x, y, speed):
    """Moves epub to the new location X,Y."""
    click.echo('Moving epub %s to %s,%s with speed %s' % (epub, x, y, speed))


@epub.command('shoot')
@click.argument('epub')
@click.argument('x', type=float)
@click.argument('y', type=float)
def epub_shoot(epub, x, y):
    """Makes epub fire to X,Y."""
    click.echo('epub %s fires to %s,%s' % (epub, x, y))
