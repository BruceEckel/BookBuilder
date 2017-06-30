# py -3
# -*- coding: utf8 -*-
"""
Fix exercise example code
"""
from pathlib import Path
from pprint import pprint
import os, sys, re, shutil, time
from itertools import chain
from sortedcontainers import SortedSet
from collections import OrderedDict
from betools import CmdLine, visitDir, ruler, head
import webbrowser
import textwrap
import config


class FixExercises:
    """
    Uses recursive descent
    """

    def __init__(self, source):
        self.input = list(source)
        self.output = []
        self.index = 0
        self.has_exercises = self.find_exercises()
        if self.has_exercises:
            while self.fix_one_exercise():
                pass
            self.output.append("")
        self.input_length = len(self.input)
        self.output_length = len(self.output)


    def current_line(self):
        if self.index < len(self.input):
            return self.input[self.index]
        return ""

    def append_line(self):
        if self.index < len(self.input):
            self.output.append(self.input[self.index])
            self.index += 1

    def find_exercises(self):
        while self.index < len(self.input):
            if self.input[self.index] == "Exercises" and self.input[self.index + 1].startswith("---------"):
                self.append_line()
                self.append_line()
                return self.index
            self.append_line()
        else:
            return None # End of file, no Exercises

    def fix_one_exercise(self):
        while not re.match("\d+\.\s\s", self.current_line()) and self.index < len(self.input):
            self.append_line()
        try:
            print(self.current_line())
        except:
            print(self.current_line().encode("utf8"))
        # We are now sitting on the first line of the exercise.
        # Hunt for the first backslash, indicating a code block,
        # or a space, indicating the end of the exercise
        while self.current_line() != "":
            if self.current_line().endswith("\\"):
                return self.fix_backslashes()
            self.append_line()
        return self.index < len(self.input)

    def fix_backslashes(self):
        # We're on the first backslash, so start the listing:
        self.output.append(self.current_line()[:-1])
        self.output.append("    ```scala")
        self.index += 1
        return self.fix_remainder()

    def fix_remainder(self):
        while self.current_line() != "" and self.index < len(self.input):
            if self.current_line().endswith("\\"):
                self.output.append(self.current_line()[:-1])
                if self.index < len(self.input):
                    self.index += 1
            else:
                self.append_line()
        self.output.append("    ```")
        return self.index < len(self.input)


@CmdLine('f')
def fix_exercises():
    """
    Fix embedded exercise listings
    """
    OFFSET = 20
    for uf in undone_files:
        md = config.markdown_dir / uf
        print(md.name)
        fixed = FixExercises(md.read_text(encoding="utf8").splitlines())
        if fixed.has_exercises:
            md.write_text("\n".join(fixed.output), encoding="utf8")
            os.system("subl {}:{}".format(md, fixed.input_length - OFFSET))

    # OFFSET = 20
    # md = config.markdown_dir / undone_files[0]
    # print(md.name)
    # fixed = FixExercises(md.read_text(encoding="utf8").splitlines())
    # if fixed.has_exercises:
    #     md.with_name("AAATEST.md").write_text("\n".join(fixed.output), encoding="utf8")
    #     os.system("subl {}:{}".format(md, fixed.input_length - OFFSET))
    #     os.system("subl {}:{}".format(md.with_name("AAATEST.md"), fixed.output_length - OFFSET))


@CmdLine('u')
def update_fixes():
    """
    Copy fixes into destination
    """
    md = config.markdown_dir / undone_files[0]
    src = md.with_name("AAATEST.md")
    dest_check = md.read_text(encoding="utf8").splitlines()
    src_check = src.read_text(encoding="utf8").splitlines()
    assert dest_check[:10] == src_check[:10]
    print(str(src))
    print(str(md))
    shutil.copy(str(src), str(md))



undone_files = """
37_Case_Classes.md
38_String_Interpolation.md
39_Parameterized_Types.md
40_Functions_as_Objects.md
41_map_and_reduce.md
42_Comprehensions.md
43_Pattern_Matching_with_Types.md
44_Pattern_Matching_with_Case_Classes.md
45_Brevity.md
46_A_Bit_of_Style.md
47_Idiomatic_Scala.md
48_Defining_Operators.md
49_Automatic_String_Conversion.md
50_Tuples.md
51_Companion_Objects.md
52_Inheritance.md
53_Base_Class_Initialization.md
54_Overriding_Methods.md
55_Enumerations.md
56_Abstract_Classes.md
57_Traits.md
58_Uniform_Access_and_Setters.md
59_Reaching_into_Java.md
60_Applications.md
61_A_Little_Reflection.md
62_Polymorphism.md
63_Composition.md
64_Using_Traits.md
65_Tagging_Traits_and_Case_Objects.md
66_Type_Parameter_Constraints.md
67_Building_Systems_with_Traits.md
68_Sequences.md
69_Lists_and_Recursion.md
70_Combining_Sequences_with_zip.md
71_Sets.md
72_Maps.md
73_References_and_Mutability.md
74_Pattern_Matching_with_Tuples.md
75_Error_Handling_with_Exceptions.md
76_Constructors_and_Exceptions.md
77_Error_Reporting_with_Either.md
78_Handling_Non_Values_with_Option.md
79_Converting_Exceptions_with_Try.md
80_Custom_Error_Reporting.md
81_Design_by_Contract.md
82_Logging.md
83_Extension_Methods.md
84_Extensible_Systems_with_Type_Classes.md
""".strip().splitlines()


if __name__ == '__main__':
    CmdLine.run()
