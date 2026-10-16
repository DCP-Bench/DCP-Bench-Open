"""Maximise: integer production of two products under two resource limits."""
from exact import Exact

solver = Exact()
solver.addVariable("chairs", 0, 100)
solver.addVariable("tables", 0, 100)
# labour hours: 6 per chair, 4 per table, at most 24
solver.addConstraint([(6, "chairs"), (4, "tables")], False, 0, True, 24)
# wood: 1 per chair, 2 per table, at most 6
solver.addConstraint([(1, "chairs"), (2, "tables")], False, 0, True, 6)

profit = [(5, "chairs"), (4, "tables")]
solver.setObjective(profit, minimize=False)

state, value = solver.toOptimum()
if state == "SAT":
    chairs, tables = solver.getLastSolutionFor(["chairs", "tables"])
    print("status:", state)
    print("Optimal profit:", -value)  # maximisation comes back negated
    print(f"chairs={chairs} tables={tables}")
else:
    print("status:", state)
