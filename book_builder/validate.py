"""
Validation test framework and checks
"""
import os
import pprint
import re
import sys
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
import book_builder.config as config
from book_builder.util import create_markdown_filename

class Editor:
    """
    Controls editing of Markdown files and validation results.
    In particular, organizes results to make it easier to
    fix up the files. Also delays invoking the editor until all
    the results are ready, to minimize screen thrashing and time-wasting.
    """

    def __init__(self):
        self.data_files = set()
        self.markdown_files = []

    def open(self):
        data_files = " ".join(self.data_files)
        markdown_files = " ".join(self.markdown_files)
        # pprint.pprint(self.data_files)
        # pprint.pprint(self.markdown_files)
        os.system(f"{config.md_editor} {data_files} {markdown_files}")


editor = Editor()  # Global Editor for working with the results

class MarkdownFile:
    """
    Contains everything about a Markdown file, including
    all discovered error information. Pass into functions
    to capture errors in Markdown files.
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
        # With listings removed:
        self.prose = re.sub(
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
            editor.markdown_files.append(
                f"{self.path}:{self.line_number + 1}" if self.line_number else f"{self.path}"
            )

    def __str__(self):
        return self.path.name


class CodeListing:
    """
    Holds all information about a single code listing in a Markdown file.
    """

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


class Validator(ABC):
    "Abstract base class for all validators"

    def __init__(self, trace):
        self.trace = trace

    @abstractmethod
    def validate(self, md: MarkdownFile):
        "Performs the actual validation."
        pass

    def post_process(self):
        """
        (Optional) Run once, at the end of all_checks().
        Performs any desired 'group actions'.
        """
        pass

    def name(self):
        return f"{self.__class__.__name__}"

    @staticmethod
    def all_checks(trace):
        "Run all tests to find problems in the book"
        md_dir = config.markdown_dir
        print(f"Validating {md_dir}")
        assert md_dir.exists(), f"Cannot find {md_dir}"
        # Create an object for each Validator:
        validators = [v(trace) for v in Validator.__subclasses__()]
        for md_path in md_dir.glob("[0-9]*_*.md"):
            markdown_file = MarkdownFile(md_path, trace)
            for val in validators:
                val.validate(markdown_file)
            markdown_file.show()
            markdown_file.edit()

        for val in validators:
            val.post_process()

        editor.open()

    @staticmethod
    def one_check(validator, trace):
        "Run a single Validator"
        md_dir = config.markdown_dir
        vdtor = validator(trace)
        print(f"Running {vdtor.name()} on {md_dir}")
        assert md_dir.exists(), f"Cannot find {md_dir}"
        # Create an object for each Validator:
        for md_path in md_dir.glob("[0-9]*_*.md"):
            markdown_file = MarkdownFile(md_path, trace)
            vdtor.validate(markdown_file)
            markdown_file.show()
            markdown_file.edit()

        vdtor.post_process()
        editor.open()


class Data:
    "Maintains a data file for a particular validate function"
    names = {}

    def __init__(self, data_file_name, storage_dir = config.data_path):
        if data_file_name not in Data.names:
            # Not reported
            Data.names[data_file_name] = "False"
        self.needs_edit = False
        self.ef_path = storage_dir / data_file_name
        if not self.ef_path.exists():
            self.ef_path.write_text("")
        self.data = self.ef_path.read_text()
        if config.msgbreak in self.data and not Data.names[data_file_name]:
            Data.names[data_file_name] = True
            print(f"{self.ef_path.name} Needs Editing!")
        self.set = {line.strip() for line in self.data.splitlines()}

    def error(self, msg, md: MarkdownFile):
        "Add message to exclusion file and edit that file"
        with open(self.ef_path, "a") as ef:
            ef.write(f"{md.path.name}:\n")
            ef.write(f"    {msg}\n")
            ef.write(config.msgbreak + "\n")
        editor.data_files.add(f"{self.ef_path}")

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        return self.data.splitlines().__iter__()


class Exclusions(Data):
    """
    Maintains an exclusion file for a particular validate function.
    Places files in the "exclusions" subdirectory.
    """
    def __init__(self, exclusion_file_name):
        super().__init__(exclusion_file_name, config.data_path / "exclusions")


### Validators ###


class NoTabs(Validator):
    "Check for tabs"

    def validate(self, md: MarkdownFile):
        for n, line in enumerate(md.lines):
            if "\t" in line:
                md.error("Tab found!", n)


class Characters(Validator):
    "Check for bad characters"

    bad_chars = ['’']

    def validate(self, md: MarkdownFile):
        for n, line in enumerate(md.lines):
            if any([bad_char in line for bad_char in Characters.bad_chars]):
                md.error(f"line {n} contains bad character:\n{line}", n)


class TagNoGap(Validator):
    "Ensure there's no gap between ``` and language_name"

    def validate(self, md: MarkdownFile):
        for listing in md.listings:
            if " " in listing.marker:
                md.error(
                    f"Contains spaces between ``` and {config.language_name}",
                    listing.md_starting_line - 1)


class FilenamesAndTitles(Validator):
    "Ensure atom titles conform to standard and agree with file names"

    def validate(self, md: MarkdownFile):
        if "Front.md" in md.path.name:
            return
        if create_markdown_filename(md.title) != md.path.name[4:]:
            md.error(f"Atom Title: {md.title}")
        if " and " in md.title:
            md.error(f"'and' in title should be '&': {md.title}")


class PackageNames(Validator):
    "Check for package names with capital letters"

    def validate(self, md: MarkdownFile):
        for listing in md.listings:
            if bool(re.search('([A-Z])', listing.package)):
                md.error(
                    f"Capital letter in package name:\n\t{listing.package}", listing.md_starting_line)


class HotWords(Validator):
    "Check for words that might need rewriting"
    exclude = Exclusions("hotwords_sentences.txt")
    words = Data("hotwords_to_find.txt")

    def validate(self, md: MarkdownFile):
        for n, line in enumerate(md.lines):
            hw = [
                w for w in HotWords.words.set if w in line and not line in HotWords.exclude]
            if hw:
                md.error(f"Hot word: {hw}\n{line}", n)
                HotWords.exclude.error(f"Hot word [{n}]: {hw}\n{line}", md)


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


class ExampleSluglines(Validator):
    "Check for sluglines that don't match the format"
    exclude = Exclusions("valid_example_sluglines.txt")

    def validate(self, md: MarkdownFile):
        for listing in md.listings:
            if not listing.slug.startswith(config.start_comment):
                continue  # Improper code fragments caught elsewhere
            if not listing.slug.startswith(config.start_comment + " "):
                md.error(
                    f"Bad first line (no space after beginning of comment):\n\t{listing.slug}")
                continue
            slug = listing.slug.split(None, 1)[1]
            if "/" not in slug and slug not in ExampleSluglines.exclude:
                ExampleSluglines.exclude.error(
                    md.error(f"Missing directory in:\n{slug}"), md)


class CompleteExamples(Validator):
    "Check for code fragments that should be turned into examples"
    exclude = Exclusions("valid_complete_examples.txt")

    @staticmethod
    def examples_without_sluglines(md: MarkdownFile):
        for listing in md.listings:
            if listing.proper_slugline:
                continue
            if listing.slug in CompleteExamples.exclude:
                continue
            for line in listing.lines:
                if line.strip().startswith("fun "):
                    return listing
        return False

    def validate(self, md: MarkdownFile):
        noslug = CompleteExamples.examples_without_sluglines(md)
        if noslug:
            CompleteExamples.exclude.error(md.error(
                f"Contains compileable example(s) without a slugline:\n{noslug.slug}",
                noslug.md_starting_line), md)


class SpellCheck(Validator):
    "Spell-check everything"

    main_dictionary = Data("dictionary.txt")
    supplemental = Data("supplemental_dictionary.txt")
    dictionary = main_dictionary.set.union(supplemental.set)

    def validate(self, md: MarkdownFile):
        words = set(
            re.split("(?:(?:[^a-zA-Z]+')|(?:'[^a-zA-Z]+))|(?:[^a-zA-Z']+)", md.text))
        misspelled = words - SpellCheck.dictionary
        misspelled.discard('')
        if len(misspelled):
            SpellCheck.supplemental.error(f"{pprint.pformat(misspelled)}", md)
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


class FunctionDescriptions(Validator):
    "Make sure functions use parentheses, not 'function'"

    exclude = Exclusions("function_descriptions.txt")

    def validate(self, md: MarkdownFile):
        func_descriptions = \
            re.findall(r"`[^(`]+?`\s+function", md.text) + \
            re.findall(r"function\s+`[^(`]+?`", md.text)
        if func_descriptions:
            err_msg = None
            for f in func_descriptions:
                if f not in FunctionDescriptions.exclude:
                    if not err_msg:
                        err_msg = "Function descriptions missing '()':\n"
                    f = f.replace("\n", " ").strip()
                    err_msg += f"\t{f}\n"
                    FunctionDescriptions.exclude.error(f"{f}", md)
            if err_msg:
                md.error(err_msg.strip())


class PunctuationInsideQuotes: #(Validator):
    "Punctuation inside quotes"

    def validate(self, md: MarkdownFile):
        text = re.sub("```(.*?)\n(.*?)\n```", "", md.text, flags=re.DOTALL)
        text = re.sub("`.*?`", "", text, flags=re.DOTALL)
        punctuation_outside = [line for line in text.splitlines()
                               if line.find('",') != -1 or line.find('".') != -1]
        if punctuation_outside:
            md.error("'.' or ',' outside quotes",
                     md.lines.index(punctuation_outside[0]))


class PrintlnOutput(Validator):
    "Test for println() without /* Output:"

    OK = ["/* Output:", "/* Sample output:", "/* Input/Output:"]  ######## A Data file?
    exclude = Exclusions("valid_println_output.txt")

    def validate(self, md: MarkdownFile):
        for listing in md.listings:
            if "println" in listing.code and not any([ok in listing.code for ok in PrintlnOutput.OK]):
                if listing.slug in PrintlnOutput.exclude:
                    continue  # Next listing
                md.error(
                    f"println without /* Output:\n{listing.slug}\n", listing.md_starting_line)
                PrintlnOutput.exclude.error(f"{listing.slug}", md)


class CapitalizedComments(Validator):
    "Check for un-capitalized comments"
    exclude = Exclusions("comment_capitalization.txt")

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
        uncapped = CapitalizedComments.find_uncapitalized_comment(md)
        if uncapped and uncapped not in CapitalizedComments.exclude:
            md.error(f"Uncapitalized comment: {uncapped}")
            CapitalizedComments.exclude.error(f"{uncapped}", md)


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
                return f"{listing.slug}: Non-even indent in line: {line}"
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


class TickedWords(Validator):
    "Spell-check single-ticked items against compiled code"

    exclude = Exclusions("valid_ticked_words.txt")
    non_letters = re.compile("[^a-zA-Z]+")

    def validate(self, md: MarkdownFile):

        def trace(id, description, item):
            if id in self.trace:
                print(f"{md} -> {description}: {pprint.pformat(item)}")

        stripped_listings = [TickedWords.non_letters.split(listing.no_comments)
                             for listing in md.listings]
        trace('a', "stripped_listings", stripped_listings)
        # Flatten list
        pieces = {item for sublist in stripped_listings for item in sublist}
        trace('b', "pieces", pieces)
        pieces = pieces.union(TickedWords.exclude)
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
            pieces).difference(TickedWords.exclude.set)
        if not_in_examples:
            e = next(iter(not_in_examples))  # Select any element from the set
            for n, line in enumerate(md.lines):
                if '`' in line and e in line:
                    break
            md.error(
                f"Backticked word(s) not in examples: {pprint.pformat(not_in_examples)}", n)
            TickedWords.exclude.error(pprint.pformat(not_in_examples), md)


def title_set():
    result = set()
    for p in config.markdown_dir.glob("*.md"):
        print(p.name)
        result.add(p.read_text().splitlines()[0].strip())
    return result

class CrossLinks(Validator):
    "Check for invalid cross-links"

    explicit_link = re.compile(r"\[[^]]+?\]\([^)]+?\)", flags=re.DOTALL)
    cross_link = re.compile(r"\[.*?\]", flags=re.DOTALL)
    footnote = re.compile(r"\[\^[^]]+?\]", flags=re.DOTALL)
    titles = title_set()

    def validate(self, md: MarkdownFile):
        explicits = [e.replace("\n", " ")
                     for e in CrossLinks.explicit_link.findall(md.prose)]
        explicits = [
            CrossLinks.cross_link.findall(e)[0][1:-1] for e in explicits]
        footnotes = [f.replace("\n", " ")
                     for f in CrossLinks.footnote.findall(md.prose)]
        if footnotes:
            print(f"footnotes: {footnotes}")
        candidates = [c.replace("\n", " ")[1:-1]
                      for c in CrossLinks.cross_link.findall(md.prose)]
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


class MistakenBackquotes(Validator):
    "Discover when backquotes are messed up by paragraph reformatting"
    exclude = Exclusions("mistaken_backquotes.txt")

    def validate(self, md: MarkdownFile):
        lines = md.prose.splitlines()
        for n, line in enumerate(lines):
            if n+1 >= len(lines):
                break
            if line.startswith("`") and lines[n+1].startswith("`"):
                if line in MistakenBackquotes.exclude and lines[n+1] in MistakenBackquotes.exclude:
                    continue
                md.error(
                    f"{config.msgbreak}\nPotential backquote error on line {n}:\n{line}\n{lines[n+1]}\n")
                MistakenBackquotes.exclude.error(md.err_msg, md)


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


class CheckBlankLines(Validator):
    """
    Make sure there isn't more than a single blank line anywhere,
    and that there's a single blank line before/after the end of a code listing.
    """

    def validate(self, md: MarkdownFile):
        for n, line in enumerate(md.lines):
            if line.strip():
                continue
            if n+1 < len(md.lines) and md.lines[n+1].strip():
                continue
            md.error("More than one blank line", n)
        for n, line in enumerate(md.lines):
            if line.startswith("```"):
                if n == 0 or n + 1 >= len(md.lines):
                    continue
                if not (md.lines[n-1].strip() == "" or md.lines[n+1].strip() == ""):
                    md.error("Missing blank line before/after listing", n)


class DuplicateExampleNames(Validator):
    """
    Ensure there are no duplicate example names.
    """
    all_examples = config.data_path / "AllExampleNames.txt"
    all_examples.write_text("")  # Clear file during class construction

    def validate(self, md: MarkdownFile):
        with open(DuplicateExampleNames.all_examples, "a") as aa:
            for example in md.listings:
                if example.proper_slugline:
                    aa.write(f"{example.slug[3:]}\n")

    def post_process(self):
        examples = DuplicateExampleNames.all_examples.read_text().splitlines()
        duplicates = set([x for x in examples if examples.count(x) > 1])
        if duplicates:
            print(
                f"Duplicate example sluglines:\n{pprint.pformat(duplicates)}")
        example_names = [e.split('/')[-1] for e in examples]
        dupnames = set(
            [x for x in example_names if example_names.count(x) > 1])
        if dupnames:
            print(f"Duplicate example names:\n{pprint.pformat(dupnames)}")


class PackageAndDirectoryNames(Validator):
    """
    Ensure that package names are consistent with directory names.
    """
    exclude = Exclusions("package_and_directory_names.txt")

    def validate(self, md: MarkdownFile):
        for lst in md.listings:
            if lst.directory and lst.package and lst.package != lst.directory.lower():
                if lst.package not in PackageAndDirectoryNames.exclude:
                    PackageAndDirectoryNames.exclude.error(lst.package, md)
                    md.error(textwrap.dedent(f"""\
                        Inconsistent package/directory name:
                            {lst.package} != {lst.directory.lower()}"""),  lst.md_starting_line)


class DirectoryNameConsistency(Validator):
    """
    Ensure that directory names in sluglines are consistent with Atom names.
    """
    exclude = Exclusions("directory_name_consistency.txt")
    dirname_exclude = Exclusions("directory_names.txt")

    def validate(self, md: MarkdownFile):
        dirset = ({lst.directory for lst in md.listings if lst.directory}
                  - DirectoryNameConsistency.exclude.set)
        if len(dirset) > 1:
            DirectoryNameConsistency.exclude.error(dirset, md)
            md.error(
                f"Multiple directory names in one atom: {pprint.pformat(dirset)}")
        if dirset - DirectoryNameConsistency.dirname_exclude.set:
            calculated_dir = "".join([w.capitalize()
                                      for w in md.path.name[4:-3].split("_")])
            if calculated_dir not in dirset:
                DirectoryNameConsistency.dirname_exclude.error(
                    f"{calculated_dir} -> {dirset}", md)
                md.error(
                    f"Inconsistent directory name: {calculated_dir} -> {dirset}")
