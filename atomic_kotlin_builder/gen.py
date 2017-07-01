#! py -3
# For running from gen.bat (placed in each atom directory)
# Compiles and runs each example, attaches output to new version
# of that example, placed in the 'generated' subdirectory
import os
import subprocess
import sys
from pathlib import Path
import click

def generate_example(source_file):
    "Compile and capture results, create new source file with output appended"
    gen = Path.cwd() / "generated"
    if not gen.exists():
        gen.mkdir()
    def execute(cmd, topic):
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = result.stdout.decode('utf-8')
        err = result.stderr.decode('utf-8')
        if len(err):
            print("{} failed: {}\n{}".format(topic, source_file.name, err))
        return out, err

    compiler_out, compiler_err = execute(["kotlinc", "{}".format(source_file.name)], "compile")
    run_out, run_err = execute(["kotlin", "{}.{}".format(source_file.parent.stem, source_file.stem + "Kt")], "run")

    if len(compiler_err) or len(run_err):
        return None

    def chop_output(source_path):
        lines = source_path.read_text().strip().splitlines()
        for n, line in enumerate(lines):
            if line.startswith("/* Output:"):
                return "\n".join(lines[:n])
        return "\n".join(lines)

    run_out = ("\n".join([ln.rstrip() for ln in run_out.splitlines()])).strip()
    source_code = chop_output(source_file)
    if len(run_out):
        source_code += "\n/* Output:\n{}\n*/".format(run_out.strip())
    generated_example = gen / source_file.name
    generated_example.write_text(source_code)
    print("wrote {}".format(generated_example.relative_to(Path.cwd())))
    return generated_example


def process_file(source_file):
    generated_file = generate_example(source_file)
    if generated_file:
        os.system("subl {}".format(generated_file))


@click.command()
@click.option('--reinsert', is_flag=True, help='Insert result back into md file.')
def generate(reinsert):
    if reinsert:
        print("Reinserting result into md file")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not len(args): # No arguments
        for source_file in Path.cwd().glob("*.kt"):
            process_file(source_file)
    else:
        for arg in args:
            source_file = Path.cwd() / arg
            process_file(source_file)


if __name__ == '__main__':
    generate()
