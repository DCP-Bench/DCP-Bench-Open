"""Regression for the swipl-clpfd skill's guidance on labelling auxiliary variables.

Takes a skill bundle path and checks two things about one trap:

1. that the trap is real, by running the broken and the repaired model through
   the container evaluator and requiring the reported outcomes to differ in the
   documented way, and
2. that the bundle warns about it.

The trap: a model introduces auxiliary channelling variables, posts the
problem's real constraints on them, and then returns only the declared decision
variables in `Vars`. The auxiliaries are never labelled. Given `sum(Row) #= 1`
and `scalar_product([0,1,2,...], Row) #= Value`, fixing `Value` does not narrow
`Row` by bounds reasoning - neither constraint prunes on its own, and CLP(FD)
propagates them separately - so the constraints posted on the rows stay merely
consistent instead of satisfied, and the evaluator finds a counterexample among
the values that do get reported.

The two models below are the ones that actually hit this, unedited, from the
run that produced this script: attempt-002 was rejected as `invalid_solution`
and attempt-005 was accepted, under
`generation/runs/20260915T153604-c7f2/attempts/session3_farmer_and_cows/swipl_clpfd/`.
They differ in which variables reach `Vars` and in nothing else that matters.

A bundle that does not carry the guidance fails, which is what makes this a
check of the instructions rather than of the integration alone.
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation import evaluate  # noqa: E402

PROBLEM = "session3_farmer_and_cows"

COMMON = '''
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

build(Instance, Assignments, Matrix) :-
    NumCows = Instance.num_cows,
    NumSons = Instance.num_sons,
    CowsPerSon = Instance.cows_per_son,
    length(Assignments, NumCows),
    Top is NumSons - 1,
    Assignments ins 0..Top,
    numlist(1, NumCows, MilkPerCow),
    sum_list(MilkPerCow, TotalMilk),
    Share is TotalMilk // NumSons,
    numlist(0, Top, SonIndices),
    length(Matrix, NumCows),
    maplist({NumSons}/[Row]>>(length(Row, NumSons), Row ins 0..1), Matrix),
    maplist({SonIndices}/[Row, Cow]>>channel(Row, SonIndices, Cow),
            Matrix, Assignments),
    transpose(Matrix, BySon),
    maplist({MilkPerCow, Share}/[Column, HeadCount]>>
                fair_share(Column, MilkPerCow, Share, HeadCount),
            BySon, CowsPerSon).

channel(Row, SonIndices, Cow) :-
    sum(Row, #=, 1),
    scalar_product(SonIndices, Row, #=, Cow).

fair_share(Column, MilkPerCow, Share, HeadCount) :-
    sum(Column, #=, HeadCount),
    scalar_product(MilkPerCow, Column, #=, Share).
'''

# Broken: only the declared assignments are labelled, so the matrix carrying
# the head-count and milk constraints is left free.
UNLABELLED = COMMON + '''
model(Instance, Assignments, [cow_assignments-Assignments]) :-
    build(Instance, Assignments, _Matrix).
'''

# Repaired: the matrix is labelled, heaviest cow first.
LABELLED = COMMON + '''
model(Instance, Vars, [cow_assignments-Assignments]) :-
    build(Instance, Assignments, Matrix),
    reverse(Matrix, Heaviest),
    append(Heaviest, HeaviestVars),
    append(HeaviestVars, Assignments, Vars).

labeling_options([leftmost]).
'''

GUIDANCE = ("label", "auxiliar")


def outcome(directory, name, source):
    path = Path(directory) / f"{name}.pl"
    path.write_text(source, encoding="utf-8")
    result = evaluate(path, PROBLEM, "swipl_clpfd", execution_timeout=120)
    return result["accepted"], result["reason"]


def documented(text, words):
    return any(all(word in line.lower() for word in words) for line in text.splitlines())


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: swipl_clpfd_labelling_regression.py SKILL_BUNDLE")
    bundle = Path(sys.argv[1])
    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")

    failures = []
    with tempfile.TemporaryDirectory(prefix="dcp_labelling_regression_") as directory:
        accepted, reason = outcome(directory, "unlabelled", UNLABELLED)
        if accepted or reason != "invalid_solution":
            failures.append("the unlabelled-auxiliary trap did not reproduce: "
                            f"accepted={accepted} reason={reason}")
        accepted, reason = outcome(directory, "labelled", LABELLED)
        if not accepted:
            failures.append(f"the repair was rejected: {reason}")

    if not documented(skill, GUIDANCE):
        failures.append(f"{bundle} has no line mentioning {' and '.join(GUIDANCE)}")

    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)
    print(f"ok {bundle}: the trap reproduces through the evaluator and is documented")


if __name__ == "__main__":
    main()
