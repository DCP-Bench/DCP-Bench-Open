"""Scheduling: three jobs on one machine with release times, minimise the makespan."""
import gurobipy as gp
from gurobipy import GRB

JOBS = {"drill": (3, 0), "cut": (2, 1), "paint": (4, 2)}   # name: (duration, release)
HORIZON = 100

model = gp.Model("one_machine")
model.Params.OutputFlag = 0
start = {j: model.addVar(lb=0, ub=HORIZON, vtype=GRB.INTEGER, name=f"s_{j}") for j in JOBS}
end = model.addVar(lb=0, ub=HORIZON, vtype=GRB.INTEGER, name="makespan")

for j, (dur, release) in JOBS.items():
    model.addConstr(start[j] >= release, name=f"release_{j}")
    model.addConstr(end >= start[j] + dur, name=f"end_{j}")

# No two jobs overlap: for each pair, one of them finishes before the other starts.
names = list(JOBS)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        a_first = model.addVar(vtype=GRB.BINARY, name=f"{a}_before_{b}")
        model.addConstr((a_first == 1) >> (start[a] + JOBS[a][0] <= start[b]))
        model.addConstr((a_first == 0) >> (start[b] + JOBS[b][0] <= start[a]))

model.setObjective(end, GRB.MINIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Makespan:", round(model.ObjVal))
    for j in sorted(JOBS, key=lambda j: start[j].X):
        print(f"  {j}: start {round(start[j].X)}")
else:
    print("Status:", model.Status)
