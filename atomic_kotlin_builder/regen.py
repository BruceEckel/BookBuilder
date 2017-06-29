#! py -3
# For running from regen.bat (placed in each atom directory)
# Compiles and runs each example, attaches output to new version
# of that example, placed in the 'regenerated' subdirectory
import subprocess
from pathlib import Path

def regenerate_example(source_file):
    "Compile and capture results, create new source file with output appended"
    regen = Path.cwd() / "regenerated"
    if not regen.exists():
        regen.mkdir()
    def execute(cmd, topic):
        # print(cmd)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = result.stdout.decode('utf-8')
        err = result.stderr.decode('utf-8')
        if len(err):
            print("{} failed: {}\n{}".format(topic, source_file.name, err))
        # else:
        #     print("{} succeeded: {}".format(topic, source_file.name))
        return out, err

    compiler_out, compiler_err = execute(["kotlinc", "{}".format(source_file.name)], "compile")
    run_out, run_err = execute(["kotlin", "{}.{}".format(source_file.parent.stem, source_file.stem + "Kt")], "run")

    def chop_output(source_path):
        lines = source_path.read_text().strip().splitlines()
        for n, line in enumerate(lines):
            if line.startswith("/* Output:"):
                return "\n".join(lines[:n])
        return "\n".join(lines)

    if(len(compiler_err) == 0 and len(run_err) == 0):
        run_out = ("\n".join([ln.rstrip() for ln in run_out.splitlines()])).strip()
        source_code = chop_output(source_file)
        if len(run_out):
            source_code += "\n/* Output:\n{}\n*/".format(run_out.strip())
        regenerated_example = regen / source_file.name
        regenerated_example.write_text(source_code)
        print("wrote {}".format(regenerated_example.relative_to(Path.cwd())))


if __name__ == '__main__':
    for source_file in Path.cwd().glob("*.kt"):
        regenerate_example(source_file)
