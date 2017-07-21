# Book Builder

- Requires Python 3.4+
- All functionality is collected under the single `bb` command which will be installed automatically

## Upcoming change:

- To support multiple targets, will be adding [Confetti](https://github.com/aviaviavi/confetti)

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
