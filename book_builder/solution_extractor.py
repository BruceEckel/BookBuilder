from collections import deque
from pathlib import Path
from pprint import pprint

import book_builder.config as config

exercises_repo = Path("C:/Git/AtomicKotlinExercises")
exercise_header = "## Exercises"
exercise_start = "##### Exercise "
solution_start = "> Solution "


def extract_description(lines: deque) -> (str, str):
    exercise_number = lines.popleft().split(exercise_start)[1]
    description = ""
    while lines and solution_start not in lines[0]:
        description += lines.popleft() + "\n"
    return exercise_number, description.strip()


def extract_solution(lines: deque) -> (str, str):
    solution_number = lines.popleft().split(solution_start)[1]
    solution = ""
    while lines and exercise_start not in lines[0]:
        line = lines.popleft()
        if line.startswith("```"):
            continue
        solution += line + "\n"
    return solution_number, solution.strip()


class ExercisesAndSolutions:
    def __init__(self, md: Path):
        self.contains_exercises_and_solutions = False
        self.atom = md.read_text()
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
                number, description = extract_description(lines)
                self.exercise_descriptions[number] = description
            elif solution_start in lines[0]:
                number, solution = extract_solution(lines)
                self.exercise_solutions[number] = solution
            else:
                lines.popleft()

    def __str__(self):
        result = ""
        if self.contains_exercises_and_solutions:
            for n, ex in self.exercise_descriptions.items():
                result += f"\n{'-'*20}\nExercise {n}: \n{ex}"
            for n, ex in self.exercise_solutions.items():
                result += f"{n}: \n{ex}"
        return result


def display_unconverted_solutions():
    for md in config.markdown_dir.glob("*.md"):
        solutions = ExercisesAndSolutions(md)
        if solutions.contains_exercises_and_solutions:
            print(md.name.center(78, '='))
            print(solutions)

# def extract_unconverted_solutions():
#     for md in config.markdown_dir.glob("*.md"):
#         solutions = ExercisesAndSolutions(md)
#         if solutions.contains_exercises:
#             print(md.name.center(78, '='))
#             print(solutions.exercises)
