"""Reification: x must be at most 3 or at least 8, and at least 5. Minimise x.

Each disjunct is a reified condition; the head variables are the switches.
"""
from exact import Exact

solver = Exact()
solver.addVariable("x", 0, 10)
solver.addVariable("low", 0, 1)   # low == 1 exactly when x <= 3
solver.addVariable("high", 0, 1)  # high == 1 exactly when x >= 8

solver.addReification("low", True, [(-1, "x")], -3)     # low <-> -x >= -3
solver.addReification("high", True, [(1, "x")], 8)      # high <-> x >= 8
solver.addConstraint([(1, "low"), (1, "high")], True, 1)  # one of them holds
solver.addConstraint([(1, "x")], True, 5)               # x >= 5

solver.setObjective([(1, "x")], minimize=True)
state, value = solver.toOptimum()
print("status:", state)
if state == "SAT":
    print("x =", solver.getLastSolutionFor(["x"])[0], "minimum:", value)
