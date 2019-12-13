# Book Builder

- Supporting tools for computer programming books written in Pandoc-Flavored
  Markdown.

- Requires Python 3.6+<sup>[1](#footnote1)</sup>

- All functionality is collected under the single `bb` command which will be
  installed automatically.

## Usage

Once installed (see below), type `bb` at the command prompt and you will see the various options, which will look something like this:

```
  Book Builder

  Provides all book building and testing utilities under a single central
  command.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  code      Code extraction and testing.
  docx      Create docx file for print version
  edit      Edit BookBuilder files using VS Code
  epub      Creates epub
  html      Create html ebook
  markdown  Markdown file manipulation
  mobi      Creates mobi files for kindle
  notes     Show all {{ Notes }} and atoms under construction except...
  release   Create full release from scratch
  validate  Validation tests
  z         Subtools for special needs
```

## Creating `configuration.py`

To use BookBuilder you must place a `configuration.py` file in the base
directory of your book's repository.

You must also set the environment variable `BOOK_PROJECT_HOME` to point to
the base directory of your book's repository.

For example, the `configuration.py` for *Atomic Kotlin* contains:

```
from pathlib import Path
import os

title = "Atomic Kotlin"
base_name = "AtomicKotlin"
language_name = "kotlin"
code_ext = "kt"
code_width = 47
start_comment = "//"
extracted_examples = Path(os.environ['BOOK_PROJECT_HOME']).parent / "AtomicKotlinExamples"
sample_size = 35 # Number of atoms in free sample
```

Once you've invoked the virtual environment for BookBuilder, you can then run
the `bb` command from within any directory in your book's repo.

## To Install
- Download and unzip this package (or `git clone` it)
- Move to the base directory where you unzipped or cloned it

## To Set Up the Virtual Environment (Mac/Linux)
- You must set up the virtual environment before you can use `bb`.
- You only need to do this the first time, after installation.

1. Move to the base directory. Run `python3 -m venv virtualenv` at the bash prompt.
   (You might have to first execute `sudo apt-get install python3.6-venv` to get this to work).

2. Then run `source ./virtualenv/bin/activate` at the bash prompt.

3. Run `pip install .` at the bash prompt. You might need to install `pip` first.


## To Enter the Virtual Environment (Mac/Linux)
- You must enter the virtual environment before you can use `bb`.
- Run `source ./virtualenv/bin/activate` at the bash prompt.
- You'll know that you're inside the virtual environment because of the
`(virtualenv)` at the beginning of your command prompt.


## To Enter the Virtual Environment (Windows)
- You must enter the virtual environment before you can use `bb`.
- Run `venv.bat` in the BookBuilder base directory. The first time,
  this will set up the virtual environment and enter it.
- From now on, running `venv` from the base directory will enter the virtual environment.
- You'll know that you're inside the virtual environment because of the
  `(virtualenv)` at the beginning of your command prompt.


## Running `bb`
- Run `bb`. This will indicate the basic commands.
- To find out more about a command, run `bb` *the_command* `--help`


## To Quit the Virtual Environment

The easiest thing to do is just kill the shell. If you want to keep the shell:

### Windows: type `venv`

### Mac/Linux: type `deactivate`

In either case, the `(virtualenv)` will disappear from your command prompt.

<hr style="height:10px">

<a name="footnote1">1</a>: If you are using Ubuntu Bash on Windows 10 or the
Ubuntu Windows 10 App, do the following to get Python 3.6:

1. `sudo add-apt-repository ppa:fkrull/deadsnakes` (You might need to follow [these instructions](http://lifeonubuntu.com/ubuntu-missing-add-apt-repository-command/)).

2. `sudo apt-get update`

3. `sudo apt-get install python3.6`

Running `python3.6` should now produce the desired version.
