"""Infeasible: 4 pigeons into 3 holes, one pigeon per hole.

Shows: reading unsat from check() (no exception, no model), and what the
solver's answer means when no solution exists.
"""
from cvc5.pythonic import *

PIGEONS, HOLES = 4, 3

hole = [Int(f"pigeon_{p}") for p in range(PIGEONS)]

s = SolverFor("QF_LIA")
s.add(*[And(h >= 0, h < HOLES) for h in hole])
s.add(Distinct(hole))

result = s.check()
if result == sat:
    print("assignment:", [s.model().eval(h, model_completion=True).as_long() for h in hole])
elif result == unsat:
    print("unsatisfiable")
else:
    print(f"undecided: {s.reason_unknown()}")
