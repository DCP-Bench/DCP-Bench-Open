"""Regression for the swipl-clpfd skill's copying and scoping guidance.

Takes a skill bundle path and checks two things about the same two traps:

1. that each trap is real, by running the broken and the repaired model through
   the container evaluator and requiring the reported outcomes to differ in the
   documented way, and
2. that the bundle warns about it.

A bundle that does not carry the guidance fails, which is what makes this a
check of the instructions rather than of the integration alone. Both traps cost
a model attempt during the run that produced this script:
`generation/runs/prolog-20260914-clpfd/attempts/sudoku/swipl_clpfd/attempt-002`
and `.../session1_magic_square/swipl_clpfd/attempt-002`.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation import evaluate  # noqa: E402

REFERENCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''

HEADER = (":- use_module(library(clpfd)).\n"
          ":- use_module(library(apply)).\n"
          ":- use_module(library(lists)).\n"
          ":- use_module(library(yall)).\n\n")

# Trap one: the sum is posted over what findall/3 returned, which are copies of
# X and Y, so the model itself is left unconstrained.
COPIED = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                   "    N = Instance.n,\n"
                   "    [X, Y] ins 0..N,\n"
                   "    findall(V, member(V, [X, Y]), Cells),\n"
                   "    sum(Cells, #=, N).\n")
MAPPED = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                   "    N = Instance.n,\n"
                   "    [X, Y] ins 0..N,\n"
                   "    sum([X, Y], #=, N).\n")

# Trap two: N is not in the lambda's {...} set, so the copy inside it is a fresh
# unbound variable and the domain goal has nothing to work with.
UNSHARED = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                     "    N = Instance.n,\n"
                     "    maplist([V]>>(V in 0..N), [X, Y]),\n"
                     "    sum([X, Y], #=, N).\n")
SHARED = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                   "    N = Instance.n,\n"
                   "    maplist({N}/[V]>>(V in 0..N), [X, Y]),\n"
                   "    sum([X, Y], #=, N).\n")

GUIDANCE = (("findall", "copies"), ("{...}", "lambda"))


def outcome(directory, name, source):
    path = Path(directory) / f"{name}.pl"
    path.write_text(source, encoding="utf-8")
    result = evaluate(path, "skill_regression", "swipl_clpfd", reference_source=REFERENCE,
                      execution_timeout=20)
    return result["accepted"], result["reason"]


def documented(text, words):
    sentences = [line for line in text.splitlines() if all(word in line for word in words)]
    return bool(sentences)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: swipl_clpfd_skill_regression.py SKILL_BUNDLE")
    bundle = Path(sys.argv[1])
    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")

    import tempfile
    failures = []
    with tempfile.TemporaryDirectory(prefix="dcp_skill_regression_") as directory:
        for name, broken, repaired, expected in (
                ("findall", COPIED, MAPPED, "invalid_solution"),
                ("lambda", UNSHARED, SHARED, "execution_error")):
            accepted, reason = outcome(directory, f"{name}_broken", broken)
            if accepted or reason != expected:
                failures.append(f"the {name} trap did not reproduce: accepted={accepted} reason={reason}")
            accepted, reason = outcome(directory, f"{name}_repaired", repaired)
            if not accepted:
                failures.append(f"the {name} repair was rejected: {reason}")

    for words in GUIDANCE:
        if not documented(skill, words):
            failures.append(f"{bundle} has no line mentioning {' and '.join(words)}")

    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)
    print(f"ok {bundle}: both traps reproduce through the evaluator and are documented")


if __name__ == "__main__":
    main()
