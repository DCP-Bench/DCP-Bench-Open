"""Infeasible: two orders must total at least 5 units, but each is capped at 2.

The solver reports UNSAT; check the status instead of expecting an exception.
"""
from exact import Exact

solver = Exact()
solver.addVariable("order_a", 0, 2)
solver.addVariable("order_b", 0, 2)
solver.addConstraint([(1, "order_a"), (1, "order_b")], True, 5, False, 0)

status = solver.runFull(optimize=False)
print("status:", status)
if status == "UNSAT":
    print("no feasible plan")
