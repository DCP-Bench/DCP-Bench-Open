#!/usr/bin/env python3
"""Judge one model's output on one toy-problem instance. Standard library only.

Usage: check_solution.py PROBLEM_DIR INSTANCE_JSON OUTPUT_TXT

PROBLEM_DIR is a directory under assets/toy-problems/. OUTPUT_TXT is what the
model printed on stdout. The answer key is PROBLEM_DIR/expected/<instance name>.json.
Prints PASS or FAIL with a reason; the exit code is 0 on PASS and 1 on FAIL.
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the skill folder free of __pycache__


def read_output(text):
    """Split stdout into solutions and status lines; lines not starting with '{' are logs."""
    solutions, statuses = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError(f"line starting with '{{' is not valid JSON: {line[:80]}")
        if not isinstance(obj, dict):
            raise ValueError(f"line is not a JSON object: {line[:80]}")
        (statuses if set(obj) == {"status"} else solutions).append(obj)
    return solutions, statuses


def load_checker(problem_dir):
    spec = importlib.util.spec_from_file_location("toy_check", problem_dir / "check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_count(solutions, count):
    """Return (False, reason) on duplicates or a wrong count, else None."""
    distinct = {json.dumps(s, sort_keys=True) for s in solutions}
    if len(distinct) != len(solutions):
        return False, f"{len(solutions) - len(distinct)} duplicate solution(s)"
    if len(solutions) != count:
        return False, f"found {len(solutions)} solutions, expected {count}"
    return None


def judge(problem_dir, instance_path, output_text):
    """Return (passed, reason)."""
    problem_dir, instance_path = Path(problem_dir), Path(instance_path)
    instance = json.loads(instance_path.read_text())
    expected = json.loads((problem_dir / "expected" / instance_path.name).read_text())
    checker = load_checker(problem_dir)
    try:
        solutions, statuses = read_output(output_text)
    except ValueError as error:
        return False, str(error)
    kind = expected["kind"]

    if kind == "unsat":
        if solutions:
            return False, f"instance is infeasible but {len(solutions)} solution(s) were printed"
        if statuses != [{"status": "unsatisfiable"}]:
            return False, 'expected exactly one line {"status": "unsatisfiable"}'
        return True, "infeasibility reported"

    if statuses:
        return False, f"instance has solutions but a status was printed: {statuses[0]}"
    if not solutions:
        return False, "no solution printed"
    for i, solution in enumerate(solutions):
        errors = checker.feasible(instance, solution)
        if errors:
            return False, f"solution {i + 1} is infeasible: " + "; ".join(errors[:3])

    if kind == "satisfy":
        if len(solutions) != 1:
            return False, f"asked for one solution, got {len(solutions)}"
        return True, "feasible solution"
    if kind == "all":
        return check_count(solutions, expected["count"]) or (True, f"all {expected['count']} solutions")
    if kind == "all-optimal":
        for i, solution in enumerate(solutions):
            value = checker.objective(instance, solution)
            if value != expected["objective"]:
                return False, f"solution {i + 1} is not optimal: objective {value} ({expected['sense']} = {expected['objective']})"
        return check_count(solutions, expected["count"]) or (True, f"all {expected['count']} optimal solutions")
    if kind == "optimize":
        if len(solutions) != 1:
            return False, f"asked for one optimal solution, got {len(solutions)}"
        value = checker.objective(instance, solutions[0])
        if value != expected["objective"]:
            return False, f"objective {value} is not optimal ({expected['sense']} = {expected['objective']})"
        return True, f"optimal ({value})"
    raise ValueError(f"unknown kind {kind!r} in answer key")


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    passed, reason = judge(sys.argv[1], sys.argv[2], Path(sys.argv[3]).read_text())
    print(("PASS" if passed else "FAIL") + ": " + reason)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
