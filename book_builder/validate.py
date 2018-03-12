"""
Validation test framework and checks
TODO: check for use of 'variable'
"""
import re
import os
import sys
import pprint
import textwrap
from pathlib import Path
from abc import ABC, abstractmethod
import book_builder.config as config
from book_builder.util import create_markdown_filename


class MarkdownFile:
    pass


misspellings = set()


class Validator(ABC):
    "Base class for all validators"

    def __init__(self, trace):
        self.trace = trace

    @abstractmethod
    def validate(self, md: MarkdownFile):
        pass

    def name(self):
        return f"{self.__class__.__name__}"

    @staticmethod
    def all_checks(trace):
        "Run all tests to find problems in the book"
        print(f"Validating {config.markdown_dir}")
        assert config.markdown_dir.exists(
        ), f"Cannot find {config.markdown_dir}"
        # Create an object for each Validator:
        validators = [v(trace)
                      for v in globals()['Validator'].__subclasses__()]
        for md_path in config.markdown_dir.glob("[0-9]*_*.md"):
            markdown_file = MarkdownFile(md_path, trace)
            for val in validators:
                val.validate(markdown_file)
            markdown_file.show()
            markdown_file.edit()

        if misspellings:
            Path(config.all_misspelled).write_text(
                "\n".join(sorted(misspellings)))
            os.system(f"{config.md_editor} {config.all_misspelled}")
            os.system(f"{config.md_editor} {config.supplemental_dictionary}")


class MarkdownFile:
    """
    Contains everything about a Markdown file, including
    all discovered error information.
    Pass into functions to capture errors in Markdown files.
    """

    def __init__(self, md_path, trace=False):
        self.path = md_path
        self.trace_flag = trace
        self.text = md_path.read_text(encoding="UTF-8")
        self.lines = self.text.splitlines()
        self.title = self.lines[0]
        self.titled = False
        self.err_msg = ""
        self.line_number = None
        self.listings = [CodeListing(marker, code, self) for (marker, code) in
                         re.findall("(```.*?)\n(.*?)\n```", self.text, flags=re.DOTALL)]
        # for lst in self.listings:
        #     print(lst)
        self.no_listings = re.sub(
            "```(.*?)\n(.*?)\n```", "", self.text, flags=re.DOTALL)

    def trace(self, msg):
        if self.trace_flag:
            print(msg)

    def error(self, msg, line_number=None):
        # Add title for the first error only:
        if not self.titled:
            self.err_msg += self.path.name + "\n"
            self.titled = True
        self.err_msg += f"    {msg}\n"
        if line_number:
            self.line_number = line_number
        return self.err_msg

    def show(self):
        if self.err_msg:
            print(self.err_msg)

    def edit(self):
        if self.err_msg:
            self.trace(f"Editing {self}")
            if self.line_number:
                os.system(
                    f"{config.md_editor} {self.path}:{self.line_number + 1}")
            else:
                os.system(f"{config.md_editor} {self.path}")

    def __str__(self):
        return self.path.name


class CodeListing:

    is_slugline = re.compile(f"^// .+?\.[a-z]+$", re.MULTILINE)

    strip_comments = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE)

    package_name = re.compile(r'^package (\S*).*$', flags=re.MULTILINE)

    @staticmethod
    def comment_remover(text):
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " "  # note: a space and not an empty string
            else:
                return s
        return re.sub(CodeListing.strip_comments, replacer, text)

    def __init__(self, marker, code, md: MarkdownFile):
        self.md = md
        self.marker = marker
        self.code = code
        self.lines = code.splitlines()
        self.slug = self.lines[0]
        self.proper_slugline = CodeListing.is_slugline.match(self.slug)
        if self.proper_slugline:
            self.directory = self.slug[3:].split('/')[0]
        else:
            self.directory = None
        self.md_starting_line = self.md.lines.index(self.slug)
        self.no_comments = CodeListing.comment_remover(code)
        self.package = ""
        package = CodeListing.package_name.findall(self.code)
        if package:
            self.package = package[0].replace(";", "")

    def __str__(self):
        return f"{self.marker}:\n{self.code}"


class ExclusionFile:
    "Maintains the exclusion file for a particular validate function"
    ef_names = {}

    def __init__(self, exclusion_file_name, md: MarkdownFile):
        if exclusion_file_name not in ExclusionFile.ef_names:
            # Not reported
            ExclusionFile.ef_names[exclusion_file_name] = "False"
        self.needs_edit = False
        self.ef_path = config.data_path / exclusion_file_name
        self.md = md
        if not self.ef_path.exists():
            self.ef_path.write_text("")
        self.exclusions = self.ef_path.read_text()
        if config.msgbreak in self.exclusions and not ExclusionFile.ef_names[exclusion_file_name]:
            ExclusionFile.ef_names[exclusion_file_name] = True
            # print(f"{self.ef_path.name} Needs Editing!")
            # os.system(f"{config.md_editor} {self.ef_path}")
            md.error(f"{self.ef_path.name} Needs Editing!")
        self.set = {line.strip() for line in self.exclusions.splitlines()}

    def error(self, msg):
        "Add message to exclusion file and edit that file"
        with open(self.ef_path, "a") as ef:
            ef.write(f"{self.md.path.name}:\n")
            ef.write(f"    {msg}\n")
            ef.write(config.msgbreak + "\n")
        os.system(f"{config.md_editor} {self.ef_path}")

    def __contains__(self, item):
        return item in self.exclusions

    def __iter__(self):
        return self.exclusions.splitlines().__iter__()


### Validators ###


class TagNoGap(Validator):
    "Ensure there's no gap between ``` and language_name"

    def validate(self, md: MarkdownFile):
        for listing in md.listings:
            if " " in listing.marker:
                md.error(
                    f"Contains spaces between ``` and {config.language_name}",
                    listing.md_starting_line - 1)


class CompleteExamples(Validator):
    "Check for code fragments that should be turned into examples"

    @staticmethod
    def examples_without_sluglines(md: MarkdownFile, exclusions):
        for listing in md.listings:
            if listing.proper_slugline:
                continue
            if listing.slug in exclusions:
                continue
            for line in listing.lines:
                if line.strip().startswith("fun "):
                    return listing
        return False

    def validate(self, md: MarkdownFile):
        exclusions = ExclusionFile("validate_complete_examples.txt", md)
        noslug = CompleteExamples.examples_without_sluglines(md, exclusions)
        if noslug:
            exclusions.error(md.error(
                f"Contains compileable example(s) without a slugline:\n{noslug.slug}",
                noslug.md_starting_line))


class FilenamesAndTitles(Validator):
    "Ensure atom titles conform to standard and agree with file names"

    def validate(self, md: MarkdownFile):
        if "Front.md" in md.path.name:
            return
        if create_markdown_filename(md.title) != md.path.name[4:]:
            md.error(f"Atom Title: {md.title}")
        if " and " in md.title:
            md.error(f"'and' in title should be '&': {md.title}")


class CapitalizedComments(Validator):
    "Check for un-capitalized comments"

    @staticmethod
    def parse_comment_block(n, lines):
        block = ""
        while n < len(lines) and "//" in lines[n]:
            block += lines[n].split("//")[1].strip() + " "
            n += 1
        return n, block

    @staticmethod
    def parse_blocks_of_comments(listing: CodeListing):
        result = []
        lines = listing.lines[1:]  # Ignore slugline
        n = 0
        while n < len(lines):
            if "//" in lines[n]:
                n, block = CapitalizedComments.parse_comment_block(n, lines)
                result.append(block)
            else:
                n += 1
        return result

    @staticmethod
    def find_uncapitalized_comment(md: MarkdownFile):
        "Need to add checks for '.' and following cap"
        for listing in md.listings:
            for comment_block in CapitalizedComments.parse_blocks_of_comments(listing):
                first_char = comment_block.strip()[0]
                if first_char.isalpha() and not first_char.isupper():
                    return comment_block.strip()
        return False

    def validate(self, md: MarkdownFile):
        # This should be an exclusion file:
        exclusions = config.comment_capitalization_exclusions.read_text()
        uncapped = CapitalizedComments.find_uncapitalized_comment(md)
        if uncapped and uncapped not in exclusions:
            md.error(f"Uncapitalized comment: {uncapped}")


class ListingIndentation(Validator):
    "Check for inconsistent indentation"

    @staticmethod
    def inconsistent_indentation(listing: CodeListing):
        if not listing.proper_slugline:
            return False
        indents = [(len(line) - len(line.lstrip(' ')), line)
                   for line in listing.lines]
        if indents[0][0]:
            return "First line can't be indented"
        for indent, line in indents:
            if indent % 2 != 0 and not line.startswith(" *"):
                return f"{listing.name}: Non-even indent in line: {line}"
        # For a desired indent of 2
        indent_counts = [ind//2 for ind, ln in indents]
        indent_pairs = list(zip(indent_counts, indent_counts[1:]))

        def test(x, y): return (
            y == x + 1
            or y == x
            or y < x  # No apparent consistency with dedenting
        )
        ok = [test(x, y) for x, y in indent_pairs]
        if not all(ok):
            return f"{listing.slug} lines {[n + 2 for n, x in enumerate(ok) if not x]}"
        return False

    @staticmethod
    def find_inconsistent_indentation(md: MarkdownFile):
        for listing in md.listings:
            inconsistent = ListingIndentation.inconsistent_indentation(listing)
            if inconsistent:
                return inconsistent
        return False

    def validate(self, md: MarkdownFile):
        bad_indent = ListingIndentation.find_inconsistent_indentation(md)
        if bad_indent:
            md.error(f"Inconsistent indentation: {bad_indent}")


class NoTabs(Validator):
    "Check for tabs"

    def validate(self, md: MarkdownFile):
        if "\t" in md.text:
            md.error("Tab found!")


class ExampleSluglines(Validator):
    "Check for sluglines that don't match the format"

    def validate(self, md: MarkdownFile):
        exclusions = ExclusionFile("validate_example_sluglines.txt", md)
        for listing in md.listings:
            if not listing.slug.startswith(config.start_comment):
                continue  # Improper code fragments caught elsewhere
            if not listing.slug.startswith(config.start_comment + " "):
                md.error(
                    f"Bad first line (no space after beginning of comment):\n\t{listing.slug}")
                continue
            slug = listing.slug.split(None, 1)[1]
            if "/" not in slug and slug not in exclusions:
                exclusions.error(md.error(f"Missing directory in:\n{slug}"))


class PackageNames(Validator):
    "Check for package names with capital letters"

    def validate(self, md: MarkdownFile):
        for listing in md.listings:
            if bool(re.search('([A-Z])', listing.package)):
                md.error(
                    f"Capital letter in package name:\n\t{listing.package}", listing.md_starting_line)


class CodeListingLineWidths(Validator):
    "Check code listing line widths"

    def validate(self, md: MarkdownFile):
        for listing in md.listings:
            if not listing.slug.startswith("// "):
                continue
            for n, line in enumerate(listing.lines):
                if len(line.rstrip()) > config.code_width:
                    md.error(f"Line {n} too wide in {listing.slug}",
                             listing.md_starting_line + n)


class TickedWords(Validator):
    "Spell-check single-ticked items against compiled code"

    non_letters = re.compile("[^a-zA-Z]+")

    def validate(self, md: MarkdownFile):

        def trace(id, description, item):
            if id in self.trace:
                print(f"{md} -> {description}: {pprint.pformat(item)}")

        exclusions = ExclusionFile("validate_ticked_words.txt", md)
        stripped_listings = [TickedWords.non_letters.split(listing.no_comments)
                             for listing in md.listings]
        trace('a', "stripped_listings", stripped_listings)
        # Flatten list
        pieces = {item for sublist in stripped_listings for item in sublist}
        trace('b', "pieces", pieces)
        pieces = pieces.union(exclusions)
        raw_single_ticks = set(
            t for t in re.findall("`.+?`", md.text, flags=re.DOTALL) if t != "```"
        )
        trace('c', "raw_single_ticks", raw_single_ticks)
        single_ticks = [TickedWords.non_letters.sub(" ", t[1:-1]).split()
                        for t in raw_single_ticks]
        # Flatten list
        single_ticks = {item for sublist in single_ticks for item in sublist}
        trace('d', "single_ticks", single_ticks)
        not_in_examples = single_ticks.difference(
            pieces).difference(exclusions.set)
        if not_in_examples:
            e = next(iter(not_in_examples))  # Select any element from the set
            for n, line in enumerate(md.lines):
                if '`' in line and e in line:
                    break
            md.error(
                f"Backticked word(s) not in examples: {pprint.pformat(not_in_examples)}", n)
            exclusions.error(pprint.pformat(not_in_examples))


class FullSpellcheck:  # (Validator):
    "Spell-check everything"

    dictionary = set(config.dictionary.read_text().splitlines()).union(
        set(config.supplemental_dictionary.read_text().splitlines()))

    def validate(self, md: MarkdownFile):
        words = set(
            re.split("(?:(?:[^a-zA-Z]+')|(?:'[^a-zA-Z]+))|(?:[^a-zA-Z']+)", md.text))
        misspelled = words - FullSpellcheck.dictionary
        if '' in misspelled:
            misspelled.remove('')
        if len(misspelled):
            global misspellings
            misspellings = misspellings.union(misspelled)
            md.error(f"Spelling Errors: {pprint.pformat(misspelled)}")


class HangingHyphens(Validator):
    "Ensure there are no hanging em-dashes or hyphens"

    hanging_emdash = re.compile("[^-]+---$")
    hanging_hyphen = re.compile("[^-]+-$")

    def validate(self, md: MarkdownFile):
        for line in md.lines:
            line = line.rstrip()
            if HangingHyphens.hanging_emdash.match(line):
                md.error(f"Hanging emdash: {line}")
            if HangingHyphens.hanging_hyphen.match(line):
                md.error(f"Hanging hyphen: {line}")


class CrossLinks(Validator):
    "Check for invalid cross-links"

    explicit_link = re.compile(r"\[[^]]+?\]\([^)]+?\)", flags=re.DOTALL)
    cross_link = re.compile(r"\[.*?\]", flags=re.DOTALL)
    titles = {p.read_text().splitlines()[0].strip()
              for p in config.markdown_dir.glob("*.md")}

    def validate(self, md: MarkdownFile):
        explicits = [e.replace("\n", " ")
                     for e in CrossLinks.explicit_link.findall(md.no_listings)]
        explicits = [
            CrossLinks.cross_link.findall(e)[0][1:-1] for e in explicits]
        candidates = [c.replace("\n", " ")[1:-1]
                      for c in CrossLinks.cross_link.findall(md.no_listings)]
        cross_links = []
        for c in candidates:
            if c in explicits:
                continue
            if len(c) < 4:
                continue
            if c.endswith(".com]"):
                continue
            if any([ch in c for ch in """,<'"()$%/"""]):
                continue
            cross_links.append(c)
        unresolved = [cl for cl in cross_links if cl not in CrossLinks.titles]
        if unresolved:
            md.error(f"""Unresolved cross-links:
            {pprint.pformat(unresolved)}""")


class FunctionDescriptions(Validator):
    "Make sure functions use parentheses, not 'function'"

    def validate(self, md: MarkdownFile):
        func_descriptions = \
            re.findall(r"`[^(`]+?`\s+function", md.text) + \
            re.findall(r"function\s+`[^(`]+?`", md.text)
        if func_descriptions:
            err_msg = "Function descriptions missing '()':\n"
            for f in func_descriptions:
                f = f.replace("\n", " ").strip()
                err_msg += f"\t{f}\n"
            md.error(err_msg.strip())


class PunctuationInsideQuotes(Validator):
    "Punctuation inside quotes"

    def validate(self, md: MarkdownFile):
        text = re.sub("```(.*?)\n(.*?)\n```", "", md.text, flags=re.DOTALL)
        text = re.sub("`.*?`", "", text, flags=re.DOTALL)
        punctuation_outside = [line for line in text.splitlines()
            if line.find('",') != -1 or line.find('".') != -1]
        if punctuation_outside:
            md.error("'.' or ',' outside quotes", md.lines.index(punctuation_outside[0]))


class Characters(Validator):
    "Check for bad characters"

    bad_chars = ['’']

    def validate(self, md: MarkdownFile):
        for n, line in enumerate(md.lines):
            if any([bad_char in line for bad_char in Characters.bad_chars]):
                md.error(f"line {n} contains bad character:\n{line}", n)


class MistakenBackquotes(Validator):
    "Discover when backquotes are messed up by paragraph reformatting"

    def validate(self, md: MarkdownFile):
        if not config.mistaken_backquote_exclusions.exists():
            config.mistaken_backquote_exclusions.write_text("")
        exclusions = config.mistaken_backquote_exclusions.read_text()
        if config.msgbreak in exclusions:
            print(f"{config.mistaken_backquote_exclusions.name} Needs Editing!")
            os.system(
                f"{config.md_editor} {config.mistaken_backquote_exclusions}")
            sys.exit()
        lines = md.no_listings.splitlines()
        for n, line in enumerate(lines):
            if n+1 >= len(lines):
                break
            if line.startswith("`") and lines[n+1].startswith("`"):
                if line in exclusions and lines[n+1] in exclusions:
                    continue
                md.error(
                    f"{config.msgbreak}\nPotential error on line {n}:\n{line}\n{lines[n+1]}\n")
                with open(config.mistaken_backquote_exclusions, "a") as mbe:
                    mbe.write(md.err_msg)
                os.system(
                    f"{config.md_editor} {config.mistaken_backquote_exclusions}")


class PrintlnOutput(Validator):
    "Test for println() without /* Output:"

    OK = ["/* Output:", "/* Sample output:", "/* Input/Output:"]

    def validate(self, md: MarkdownFile):
        exclusions = ExclusionFile("validate_println_output.txt", md)
        for listing in re.findall("```kotlin(.*?)```", md.text, flags=re.DOTALL):
            slug = listing.strip().splitlines()[0]
            if "println" in listing and not any([ok in listing for ok in PrintlnOutput.OK]):
                if slug in exclusions:
                    continue  # Next listing
                for n, line in enumerate(md.lines):
                    if slug in line:
                        exclusions.error(md.error(
                            f"println without /* Output:\n{slug}\n", n))
                        break


class JavaPackageDirectory(Validator):
    """
    Test for Java package name and directory name.
    Directory names for atoms that contain Java examples must be lowercase.
    """

    def debug(self, md: MarkdownFile, listing: CodeListing):
        if self.trace:
            print(textwrap.dedent(f"""\
            {md}
                marker: {listing.marker}
                slug: {listing.slug}
                directory [{listing.directory}]
                package ({listing.package})
            """))

    def validate(self, md: MarkdownFile):
        for listing in [lst for lst in md.listings if 'java' in lst.marker and lst.package]:
            if bool(re.search('([A-Z])', listing.directory)):
                self.debug(md, listing)
                md.error(textwrap.dedent(f"""\
                    Capitalized directory containing a Java file:
                        {listing.slug}
                        directory: {listing.directory}
                        package: {listing.package}
                    """),
                         listing.md_starting_line)
