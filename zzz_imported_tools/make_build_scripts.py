from pathlib import Path
from collections import OrderedDict
import config


# Files to be compiled rather than run as scripts, along with their file dependency.
# Currently only existence of the dependency is checked; it would probably be an easy change
# to compare timestamps.
compileFiles = OrderedDict([
  ('AtomicTest.kt', 'com/atomicscala/AtomicTest.class'),
  ('PythagoreanTheorem.kt', 'pythagorean/RightTriangle.class'),
  ('ALibrary.kt', 'com/yoururl/libraryname/x.class'),
  ('SodaFountain.kt', 'sodafountain/IceCream.class'),
  ('Name.kt', 'com/atomicscala/Name.class'),
  ('Compiled.kt', 'WhenAmI.class'),
  ('CompiledWithArgs.kt', 'EchoArgs.class'),
  ('CompiledWithMain.kt', 'EchoArgs2.class'),
  ('PaintColors.kt', 'paintcolors/Color.class'),
  ('ColorBlend.kt', 'colorblend/package.class'),
  ('Errors.kt', 'errors/Except1.class'),
  ('CodeListing.kt', 'codelisting/CodeListing.class'),
  ('CodeListingTester.kt', 'codelistingtester/CodeListingTester.class'),
  ('CodeListingEither.kt', 'codelistingeither/CodeListingEither.class'),
  ('Fail.kt', 'com/atomicscala/reporterr/FailMsg.class'),
  ('CodeListingCustom.kt', 'codelistingcustom/CodeListingCustom.class'),
  ('CodeVector.kt', 'codevector/CodeVector.class'),
  ('ElidingDBC.kt', 'ElidingDBC.class'),
  ('Logging.kt', 'com/atomicscala/Logging.class'),
  ('Quoting2.kt', 'Quoting2/package.class'),
  ('Eratosthenes.kt', 'primesieve/Eratosthenes.class'),
])


####################### For Windows PowerShell File #####################

powershellcontents = '''\
cls
if (Test-Path "_testoutput.txt") { rm "_testoutput.txt" }
if (Test-Path "_AtomicTestErrors.txt") { rm "_AtomicTestErrors.txt" }

$compiled = @(
    %s
)

fsc -reset

foreach($dependency in $compiled) {
    $source, $target = $dependency
    if(-Not(Test-Path $target)) {
        Write-Host fsc $source
        Write-Output "> fsc $source" | Out-File ./_testoutput.txt -append
        fsc $source 2>&1 | tee -Variable testout
        out-file ./_testoutput.txt -InputObject $testout -append
    } else {
        Write-Host $target already exists
        Write-Output "$target already exists" | Out-File ./_testoutput.txt -append
    }
}

$scripts = (
    %s
)

foreach($script in $scripts) {
    Write-Host scala $script
    Write-Output "> scala $script" | Out-File ./_testoutput.txt -append
    scala -nocompdaemon $script 2>&1 | tee -Variable testout
    out-file ./_testoutput.txt -InputObject $testout -append
    Write-Output "--------------------" | Out-File ./_testoutput.txt -append
}

'''


####################### For Windows Batch File #####################
batchcontents = '''\
echo off
cls

%s

if exist _testerrors.txt (del _testerrors.txt)
if exist _AtomicTestErrors.txt (del _AtomicTestErrors.txt)

FOR %%%%I IN (
%s
) DO (
echo scala %%%%I
CALL scala -nocompdaemon %%%%I 2>> _testerrors.txt
)
'''

batchCompile = '''\
if not exist %s (
    echo scalac %s
    call scalac %s
) else (
    echo %s already exists
)

'''


####################### For Linux/Mac Bash File #####################
bashcontents = '''\
#!/bin/bash

trap 'exit' INT TERM # exit when interrupted or terminated
clear

conditionalCompile() {
  if [ ! -e "$1" ]
  then
    echo scalac "$2"
    scalac "$2"
  else
    echo "$1" already exists
  fi
}

%s

rm -fv _testerrors.txt _testoutput.txt _AtomicTestErrors.txt

scripts=(
%s
)

for script in "${scripts[@]}"; do
    echo scala "${script}"
    scala -nocompdaemon "${script}" > >(tee -a _testoutput.txt) \\
        2> >(tee -a _testerrors.txt >&2)
done
'''


#################################################################


def powershellfile(examples):
    dependencies = ['@("%s", "%s")' % (k, compileFiles[k]) for k in compileFiles]
    dependency = ['"%s" = "%s"' % (k, compileFiles[k]) for k in compileFiles]
    sourceFiles = ['"%s"' % k for k in compileFiles]
    scripts = ['"' + ex.name + '"' for ex in examples if ex.name not in compileFiles]
    with (config.examples_dir / "testall.ps1").open("w") as build:
        build.write(powershellcontents % (",\n    ".join(dependencies), ",\n    ".join(scripts)))
        build.write("\njavac FindPrimes.java\n")
        build.write("java FindPrimes\n")


def batchfile(examples):
    cf = compileFiles
    compiles = [batchCompile % (cf[ex], ex, ex, cf[ex]) for ex in cf]
    scripts = [ex.name for ex in examples if ex.name not in compileFiles]
    with (config.examples_dir / "testall.bat").open("w") as build:
        build.write(batchcontents % ("".join(compiles), "\n".join(scripts)))
        build.write("\njavac FindPrimes.java\n")
        build.write("java FindPrimes\n")


def bashfile(examples):
    cf = compileFiles
    compiles = ["conditionalCompile %s %s" % (cf[ex], ex) for ex in cf]
    scripts = [ex.name for ex in examples if ex.name not in compileFiles]
    print("\n".join(scripts))
    with (config.examples_dir / "testall.sh").open("w", newline="\n") as build:
        build.write(bashcontents % ("\n".join(compiles), "\n".join(scripts)))
        build.write("\njavac FindPrimes.java\n")
        build.write("java FindPrimes\n")

    # os.chmod(code("testall.sh"), 0777) Not necessary in Python 3 w/ newline="\n"

