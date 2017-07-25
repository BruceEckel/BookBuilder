# Book Builder

- Supporting tools for computer programming books written in Pandoc-Flavored
  Markdown.

- Requires Python 3.6+<sup>[1](#footnote1)</sup>

- All functionality is collected under the single `bb` command which will be
  installed automatically.

## Creating `settings.config`

To use BookBuilder you must place a `settings.config` file in the
base directory of your book's repository. For example, the `settings.config` for
*Atomic Kotlin* contains:

```
base_name = "AtomicKotlin"
language_name = "kotlin"
```

For *Thinking in Python*, it is:

```
base_name = "ThinkingInPython"
language_name = "python"
```

Once you've invoked the virtual environment for BookBuilder, you can then run
the `bb` command from within any directory in your book's repo.

## To Install
- Download and unzip this package (or `git clone` it)
- Move to the base directory where you unzipped or cloned it

## To Set Up the Virtual Environment (Mac/Linux)
- You must set up the virtual environment before you can use `bb`.
- You only need to do this the first time, after installation


#### The following will ideally be eliminated:

1. At the end of your `.bashrc` file, set the `ATOMIC_KOTLIN_BUILDER` environment variable to the base
directory of your installation. For example:

```
export set ATOMIC_KOTLIN_BUILDER=/mnt/c/Users/bruce/Documents/Git/AtomicKotlinBuilder
```

Start a new bash shell or move to your home directory and `source .bashrc`.

2. Move to the base directory. Run `python3 -m venv virtualenv` at the bash prompt.
   (You might have to first execute `sudo apt-get install python3.4-venv` to get this to work).

3. Then run `source ./virtualenv/bin/activate` at the bash prompt.

4. Run `pip install .` at the bash prompt. You might need to install `pip` first.


## To Enter the Virtual Environment (Mac/Linux)
- You must enter the virtual environment before you can use `bb`.
- Run `source ./virtualenv/bin/activate` at the bash prompt.
- You'll know that you're inside the virtual environment because of the
`(virtualenv)` at the beginning of your command prompt.


## To Enter the Virtual Environment (Windows)
- You must enter the virtual environment before you can use `bb`.
- Run `venv.bat`. The first time, this will set up the virtual environment and enter it.
- From now on, running `venv` from the base directory will enter the virtual environment.
- You'll know that you're inside the virtual environment because of the
`(virtualenv)` at the beginning of your command prompt.


## Running `bb`
- Run `bb`. This will indicate the basic commands
- To find out more about a command, run `bb` *the_command* `--help`


## To Quit the Virtual Environment

### Windows: type `venv`

### Mac/Linux: type `deactivate`

In either case, the `(virtualenv)` will disappear from your command prompt.


<a name="footnote1">1</a>: If you are using Ubuntu Bash on Windows 10 or the
Ubuntu Windows 10 App, do the following to get Python 3.6:

1. `sudo add-apt-repository ppa:fkrull/deadsnakes`

2. `sudo apt-get update`

3. `sudo apt-get install python3.6`

Running `python3.6` should now produce the desired version.
