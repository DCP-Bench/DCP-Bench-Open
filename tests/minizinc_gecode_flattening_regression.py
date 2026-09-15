"""Regression for the minizinc-gecode skill's warning about one-sided bounds.

MiniZinc 2.9.3 can flatten a model in which an auxiliary variable is bounded
from one side so that the variable doing the bounding drops out of another
constraint entirely, and then reports solutions that violate it. This check
reproduces that through the container evaluator on `cell_tower`, whose reference
has exactly that shape: the literal translation is rejected as
`invalid_solution`, and the same model with the bound stated as an equivalence
is accepted.

It also requires the bundle to warn about it, so a bundle without the guidance
fails. Evidence:
`generation/runs/breadth2-20260915/attempts/cell_tower/minizinc_gecode/attempt-002/lessons.md`.
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation import evaluate  # noqa: E402

PROBLEM = "cell_tower"
HEADER = '''include "globals.mzn";

array[int, int] of int: delta;
array[int] of int: cost;
array[int] of int: population;
int: budget;

set of int: Sites = index_set(cost);
set of int: Regions = index_set(population);
array[Sites] of var bool: build_tower;
array[Regions] of var bool: covered;

'''
TAIL = '''constraint sum(i in Sites) (cost[i] * bool2int(build_tower[i])) <= budget;

var int: objective = sum(j in Regions) (population[j] * bool2int(covered[j]));
solve maximize objective;

output ["{\\"build_tower\\": [", join(", ", [show(build_tower[i]) | i in Sites]),
        "], \\"total_population_covered\\": ", show(objective), "}"];
'''
# The reference's own one-sided bound, translated literally.
ONE_SIDED = HEADER + '''constraint forall(j in Regions) (
    bool2int(covered[j]) <= sum(i in Sites) (delta[i, j] * bool2int(build_tower[i])));

''' + TAIL
# The same relationship as an equivalence.
EQUIVALENCE = HEADER + '''constraint forall(j in Regions) (
    covered[j] <-> exists(i in Sites) (delta[i, j] = 1 /\\ build_tower[i]));

''' + TAIL


def outcome(directory, name, source):
    path = Path(directory) / f"{name}.mzn"
    path.write_text(source, encoding="utf-8")
    result = evaluate(path, PROBLEM, "minizinc_gecode", solution_limit=2, execution_timeout=30)
    return result["accepted"], result["reason"]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: minizinc_gecode_flattening_regression.py SKILL_BUNDLE")
    bundle = Path(sys.argv[1])
    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")

    failures = []
    with tempfile.TemporaryDirectory(prefix="dcp_skill_regression_") as directory:
        accepted, reason = outcome(directory, "one_sided", ONE_SIDED)
        if accepted or reason != "invalid_solution":
            failures.append(f"the one-sided bound did not misbehave: accepted={accepted} reason={reason}")
        accepted, reason = outcome(directory, "equivalence", EQUIVALENCE)
        if not accepted:
            failures.append(f"the equivalence form was rejected: {reason}")

    guidance = [line for line in skill.splitlines()
                if "equivalence" in line.lower() or "one-sided" in line.lower()]
    if not guidance:
        failures.append(f"{bundle} does not warn about one-sided bounds")

    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)
    print(f"ok {bundle}: the one-sided bound is rejected, the equivalence accepted, and the "
          "skill says so")


if __name__ == "__main__":
    main()
