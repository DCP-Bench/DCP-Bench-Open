"""Regression for the minizinc-gecode skill's guidance on implied constraints.

Takes a skill bundle path and checks both halves of the claim: that implied
constraints decide whether Gecode finishes `csplib_049_number_partitioning`
n = 20 at all, by running the two models through the container evaluator, and
that the bundle says so. A bundle without the guidance fails, which is what
makes this a check of the instructions rather than of the integration alone.

Evidence behind it:
`generation/runs/models-20260914-vamos/attempts/csplib_049_number_partitioning/minizinc_gecode/`,
where attempt 001 reached `execution_timeout` on n = 16 and n = 20 and attempt
002 was accepted on all four instances.
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation import evaluate  # noqa: E402

PROBLEM = "csplib_049_number_partitioning"
HARDEST = "json:3"
BUDGET = 25

DIRECT = '''include "globals.mzn";

int: n;
int: half = n div 2;

array[1..half] of var 1..n: x;
array[1..half] of var 1..n: y;

constraint all_different(x ++ y);
constraint sum(x) = sum(y);
constraint sum(i in 1..half) (x[i] * x[i]) = sum(i in 1..half) (y[i] * y[i]);

solve satisfy;

output ["{\\"A\\": [", join(", ", [show(x[i]) | i in 1..half]),
        "], \\"B\\": [", join(", ", [show(y[i]) | i in 1..half]), "]}"];
'''
IMPLIED = DIRECT.replace("solve satisfy;", '''% Implied: x and y partition 1..n, so each half carries half of the totals.
constraint 4 * sum(x) = n * (n + 1);
constraint 12 * sum(i in 1..half) (x[i] * x[i]) = n * (n + 1) * (2 * n + 1);

solve satisfy;''')


def outcome(directory, name, source):
    path = Path(directory) / f"{name}.mzn"
    path.write_text(source, encoding="utf-8")
    result = evaluate(path, PROBLEM, "minizinc_gecode", instance_ids=[HARDEST],
                      execution_timeout=BUDGET)
    return result["accepted"], result["reason"]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: minizinc_gecode_skill_regression.py SKILL_BUNDLE")
    bundle = Path(sys.argv[1])
    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")

    failures = []
    with tempfile.TemporaryDirectory(prefix="dcp_skill_regression_") as directory:
        accepted, reason = outcome(directory, "direct", DIRECT)
        if accepted or reason != "execution_timeout":
            failures.append(f"the direct model did not time out: accepted={accepted} reason={reason}")
        accepted, reason = outcome(directory, "implied", IMPLIED)
        if not accepted:
            failures.append(f"the implied constraints did not rescue the instance: {reason}")

    if not [line for line in skill.splitlines() if "implied" in line.lower()]:
        failures.append(f"{bundle} has no line about implied constraints")

    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)
    print(f"ok {bundle}: implied constraints decide the instance, and the skill says so")


if __name__ == "__main__":
    main()
