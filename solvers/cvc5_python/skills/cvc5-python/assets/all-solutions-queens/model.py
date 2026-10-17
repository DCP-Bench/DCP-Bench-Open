"""Enumerate: every solution of the 6-queens problem.

Shows: enumeration with a no-good on the decision variables only,
Distinct over derived expressions (diagonals), a loop until unsat.
"""
from cvc5.pythonic import *

N = 6

q = [Int(f"q{i}") for i in range(N)]  # q[i] = row of the queen in column i

s = SolverFor("QF_LIA")
s.add(*[And(v >= 0, v < N) for v in q])
s.add(Distinct(q))
s.add(Distinct([q[i] + i for i in range(N)]))
s.add(Distinct([q[i] - i for i in range(N)]))

solutions = []
while True:
    result = s.check()
    if result != sat:
        break
    m = s.model()
    values = [m.eval(v, model_completion=True).as_long() for v in q]
    solutions.append(values)
    # block this assignment of the decision variables only
    s.add(Or([v != x for v, x in zip(q, values)]))

if result == unknown:
    print(f"undecided after {len(solutions)} solutions: {s.reason_unknown()}")
else:
    for values in solutions:
        print(values)
    print(f"{len(solutions)} solutions")
