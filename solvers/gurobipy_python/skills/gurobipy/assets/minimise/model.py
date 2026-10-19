"""Minimise: assign each worker to one job, one job per worker, at least cost."""
import gurobipy as gp
from gurobipy import GRB

cost = [[9, 2, 7],
        [6, 4, 3],
        [5, 8, 1]]
n = len(cost)

model = gp.Model("assign")
model.Params.OutputFlag = 0
x = model.addVars(n, n, vtype=GRB.BINARY, name="x")
model.addConstrs((x.sum(w, "*") == 1 for w in range(n)), name="worker")
model.addConstrs((x.sum("*", j) == 1 for j in range(n)), name="job")
model.setObjective(gp.quicksum(cost[w][j] * x[w, j] for w in range(n) for j in range(n)), GRB.MINIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Total cost:", round(model.ObjVal))
    for w in range(n):
        job = next(j for j in range(n) if round(x[w, j].X) == 1)
        print(f"  worker {w} -> job {job} (cost {cost[w][job]})")
else:
    print("Status:", model.Status)
