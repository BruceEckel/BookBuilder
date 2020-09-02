from collections import deque
from pathlib import Path
import book_builder.util as util
from pprint import pprint

import book_builder.config as config

exercises_repo = Path("C:/Git/AtomicKotlinExercises")
exercise_header = "## Exercises"
exercise_start = "##### Exercise "
solution_start = "> Solution "


def extract(lines: deque, start: str, end: str) -> (str, str):
    exercise_number = lines.popleft().split(start)[1]
    content = ""
    while lines and end not in lines[0]:
        line = lines.popleft()
        if line.startswith("```"):
            continue
        content += line + "\n"
    return exercise_number, content.strip()


class ExercisesAndSolutions:
    def __init__(self, md: Path):
        self.contains_exercises_and_solutions = False
        self.atom = md.read_text()
        self.directory_name = self.atom.splitlines()[0][2:].split("{#")[0].replace(' ', '').replace('`', '')
        self.contains_exercises = exercise_header in self.atom
        if not self.contains_exercises:
            return
        self.exercises = self.atom.split(exercise_header)[1]
        self.contains_solutions = solution_start in self.exercises
        if not self.contains_solutions:
            return
        self.contains_exercises_and_solutions = True
        self.lines = self.exercises.splitlines()
        self.exercise_descriptions = {}
        self.exercise_solutions = {}
        lines = deque(self.lines)
        while lines:
            if exercise_start in lines[0]:
                number, description = extract(lines, exercise_start, solution_start)
                self.exercise_descriptions[number] = description
            elif solution_start in lines[0]:
                number, solution = extract(lines, solution_start, exercise_start)
                self.exercise_solutions[number] = solution
            else:
                lines.popleft()

    def __str__(self):
        result = ""

        def display(n, ex, name):
            nonlocal result
            result += "\n\n" + f"{name} {n}".center(78, '-') + "\n"
            result += f"\n{ex}"

        if self.contains_exercises_and_solutions:
            [display(n, ex, "Exercise") for n, ex in self.exercise_descriptions.items()]
            [display(n, ex, "Solution") for n, ex in self.exercise_solutions.items()]
        return result


def display_unconverted_solutions():
    for md in config.markdown_dir.glob("*.md"):
        e_and_s = ExercisesAndSolutions(md)
        if e_and_s.contains_exercises_and_solutions:
            print(md.name.center(78, '='))
            print(e_and_s)

def extract_unconverted_solutions():
    def write_exercise(efile, number, description):
        efile.write(f"Exercise {number}".center(78, '-'))
        efile.write("\n\n" + description + "\n\n")
    for md in config.markdown_dir.glob("*.md"):
        e_and_s = ExercisesAndSolutions(md)
        if e_and_s.contains_exercises_and_solutions:
            directory = exercises_repo / e_and_s.directory_name
            if directory.exists():
                util.clean(directory)
            directory.mkdir()
            exercise_file = directory / "Exercises.txt"
            with exercise_file.open(mode='w') as efile:
                [write_exercise(efile, n, ex) for n, ex in e_and_s.exercise_descriptions.items()]


