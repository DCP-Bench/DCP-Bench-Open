"""Infeasible: 4 pigeons cannot each have their own hole when there are only 3 holes."""
from ortools.sat.python import cp_model

PIGEONS, HOLES = 4, 3

model = cp_model.CpModel()
in_hole = [[model.new_bool_var(f"p{p}h{h}") for h in range(HOLES)] for p in range(PIGEONS)]
for p in range(PIGEONS):
    model.add_exactly_one(in_hole[p])          # every pigeon sits in one hole
for h in range(HOLES):
    model.add_at_most_one([in_hole[p][h] for p in range(PIGEONS)])  # at most one per hole

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
if status == cp_model.INFEASIBLE:
    print("No assignment exists.")
