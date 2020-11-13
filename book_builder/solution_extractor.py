from collections import deque
from pathlib import Path

import book_builder.config as config
import book_builder.util as util

exercises_repo = Path("C:/Git/AtomicKotlinExercises")
exercise_start = "##### Exercise "
solution_start = "> Solution "


def extract(lines: deque, start: str) -> (str, str):
    exercise_number = lines.popleft().split(start)[1]
    content = ""
    while lines and solution_start not in lines[0] and exercise_start not in lines[0]:
        line = lines.popleft()
        if line.startswith("```"):
            continue
        content += line + "\n"
    return exercise_number, content.strip()


class ExercisesAndSolutions:
    def __init__(self, md: Path):
        self.md = md
        self.atom = md.read_text()
        self.atom_lines = self.atom.splitlines()
        self.directory_name = md.stem
        self.directory = exercises_repo / self.directory_name
        self.contains_exercises = config.exercise_header in self.atom_lines
        if not self.contains_exercises:
            return
        self.exercises = self.atom.split(config.exercise_header)[1]
        self.exercise_lines = self.exercises.splitlines()
        self.exercise_descriptions = {}
        self.exercise_solutions = {}
        lines = deque(self.exercise_lines)
        while lines:
            if exercise_start in lines[0]:
                number, description = extract(lines, exercise_start)
                self.exercise_descriptions[number] = description
            elif solution_start in lines[0]:
                number, solution = extract(lines, solution_start)
                self.exercise_solutions[number] = solution
            else:
                lines.popleft()

    def __str__(self):
        result = ""

        def display(n, ex, name):
            nonlocal result
            result += "\n\n" + f"{name} {n}".center(78, '-') + "\n"
            result += f"\n{ex}"

        if self.contains_exercises:
            [display(n, ex, "Exercise") for n, ex in self.exercise_descriptions.items()]
        # if self.contains_solutions:
        if self.exercise_solutions:
            [display(n, ex, "Solution") for n, ex in self.exercise_solutions.items()]
        return result

    def write_no_exercises(self):
        recreate_directory(self.directory)
        note_file = self.directory / "No_Exercises_Here.txt"
        note_file.touch()
        return f"{self.md.name}: No Exercises"

    def write_exercises(self):
        recreate_directory(self.directory)
        exercise_file = self.directory / "Exercises.txt"
        with exercise_file.open(mode='w') as efile:
            [write_exercise(efile, n, ex) for n, ex in self.exercise_descriptions.items()]

    def write_solutions(self):
        assert self.directory and self.directory.is_dir()
        for n, solution in self.exercise_solutions.items():
            solution_file = self.directory / solution.splitlines()[0].split('/')[-1]
            solution_file.write_text(solution + "\n")


def display_unconverted_solutions():
    for md in config.markdown_dir.glob("*.md"):
        e_and_s = ExercisesAndSolutions(md)
        # if e_and_s.contains_exercises and e_and_s.contains_solutions:
        if e_and_s.contains_exercises and e_and_s.exercise_solutions:
            print(md.name.center(78, '='))
            print(e_and_s)


def recreate_directory(directory: Path):
    if directory.exists():
        assert directory.is_dir()
        util.erase(directory)
    directory.mkdir()


def write_exercise(efile, number, description):
    efile.write(f"Exercise {number}".center(78, '-'))
    efile.write("\n\n" + description + "\n\n")


def extract_unconverted_solutions():
    for md in config.markdown_dir.glob("*.md"):
        e_and_s = ExercisesAndSolutions(md)
        # if e_and_s.contains_exercises and e_and_s.contains_solutions:
        if e_and_s.contains_exercises and e_and_s.exercise_solutions:
            e_and_s.write_exercises()
            e_and_s.write_solutions()


def extract_all_exercises():
    print("Test")
    print(f"{config.markdown_dir}")
    for md in config.markdown_dir.glob("*.md"):
        print(f"{md.name}")
        e_and_s = ExercisesAndSolutions(md)
        if not e_and_s.contains_exercises:
            e_and_s.write_no_exercises()
            continue
        if e_and_s.contains_exercises:
            e_and_s.write_exercises()
        if e_and_s.exercise_solutions:
            e_and_s.write_solutions()
