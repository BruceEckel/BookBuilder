
@validate.command()
@click.option('--trace', default="")
def tabs(trace):
    """
    Check for tabs
    """
    click.echo(_validate.Validator.one_check(_validate.NoTabs, trace))


@validate.command()
@click.option('--trace', default="")
def bad_chars(trace):
    """
    Check for bad characters
    """
    click.echo(_validate.Validator.one_check(_validate.Characters, trace))


@validate.command()
@click.option('--trace', default="")
def backtick_gap(trace):
    """
    Ensure there's no gap between ``` and language_name
    """
    click.echo(_validate.Validator.one_check(_validate.TagNoGap, trace))


@validate.command()
@click.option('--trace', default="")
def titles(trace):
    """
    Ensure atom titles conform to standard and agree with file names
    """
    click.echo(_validate.Validator.one_check(_validate.FilenamesAndTitles, trace))


@validate.command()
@click.option('--trace', default="")
def package_names(trace):
    """
    Package names shouldn't have capital letters
    """
    click.echo(_validate.Validator.one_check(_validate.PackageNames, trace))


@validate.command()
@click.option('--trace', default="")
def hotwords(trace):
    """
    Words that might need rewriting
    """
    click.echo(_validate.Validator.one_check(_validate.HotWords, trace))


@validate.command()
@click.option('--trace', default="")
def listing_width(trace):
    """
    Code listings shouldn't exceed line widths
    """
    click.echo(_validate.Validator.one_check(_validate.CodeListingLineWidths, trace))


@validate.command()
@click.option('--trace', default="")
def sluglines(trace):
    """
    Sluglines should match the format
    """
    click.echo(_validate.Validator.one_check(_validate.ExampleSluglines, trace))


@validate.command()
@click.option('--trace', default="")
def complete_examples(trace):
    """
    Find code fragments that should be turned into examples
    """
    click.echo(_validate.Validator.one_check(_validate.CompleteExamples, trace))


@validate.command()
@click.option('--trace', default="")
def spelling(trace):
    """
    Spell-check everything
    """
    click.echo(_validate.Validator.one_check(_validate.SpellCheck, trace))


@validate.command()
@click.option('--trace', default="")
def hanging_hyphens(trace):
    """
    No hanging em-dashes or hyphens
    """
    click.echo(_validate.Validator.one_check(_validate.HangingHyphens, trace))


@validate.command()
@click.option('--trace', default="")
def function_descriptions(trace):
    """
    Functions in prose should use parentheses
    """
    click.echo(_validate.Validator.one_check(_validate.FunctionDescriptions, trace))


@validate.command()
@click.option('--trace', default="")
def println_output(trace):
    """
    println() should have /* Output:
    """
    click.echo(_validate.Validator.one_check(_validate.PrintlnOutput, trace))


@validate.command()
@click.option('--trace', default="")
def comment_capitalization(trace):
    """
    Comments should be capitalized
    """
    click.echo(_validate.Validator.one_check(_validate.CapitalizedComments, trace))


@validate.command()
@click.option('--trace', default="")
def listing_indentation(trace):
    """
    Indentation should be consistent
    """
    click.echo(_validate.Validator.one_check(_validate.ListingIndentation, trace))


@validate.command()
@click.option('--trace', default="")
def ticked_words(trace):
    """
    Spell-check single-ticked items against compiled code
    """
    click.echo(_validate.Validator.one_check(_validate.TickedWords, trace))


@validate.command()
@click.option('--trace', default="")
def cross_links(trace):
    """
    Find invalid cross-links
    """
    click.echo(_validate.Validator.one_check(_validate.CrossLinks, trace))


@validate.command()
@click.option('--trace', default="")
def mistaken_backquotes(trace):
    """
    Discover when backquotes are messed up by paragraph reformatting
    """
    click.echo(_validate.Validator.one_check(_validate.MistakenBackquotes, trace))


@validate.command()
@click.option('--trace', default="")
def java_packages(trace):
    """
    Directory names for atoms that contain Java examples must be lowercase.
    """
    click.echo(_validate.Validator.one_check(_validate.JavaPackageDirectory, trace))


@validate.command()
@click.option('--trace', default="")
def blank_lines(trace):
    """
    Make sure there isn't more than a single blank line anywhere,
    and that there's a single blank line before/after the end of a code listing.
    """
    click.echo(_validate.Validator.one_check(_validate.CheckBlankLines, trace))


@validate.command()
@click.option('--trace', default="")
def duplicate_example_names(trace):
    """
    Example names can't be duplicated
    """
    click.echo(_validate.Validator.one_check(_validate.DuplicateExampleNames, trace))


@validate.command()
@click.option('--trace', default="")
def package_and_directory_names(trace):
    """
    Package names should be consistent with directory names
    """
    click.echo(_validate.Validator.one_check(_validate.PackageAndDirectoryNames, trace))


@validate.command()
@click.option('--trace', default="")
def directory_name_consistency(trace):
    """
    Directory names in sluglines should be consistent with atom names
    """
    click.echo(_validate.Validator.one_check(_validate.DirectoryNameConsistency, trace))

