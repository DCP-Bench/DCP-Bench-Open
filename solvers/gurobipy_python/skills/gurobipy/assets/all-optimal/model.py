"""All optimal solutions: the minimum vertex covers of a 4-cycle, plus an isolated vertex."""
import gurobipy as gp
from gurobipy import GRB

EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]
V = 5

model = gp.Model("covers")
model.Params.OutputFlag = 0
pick = model.addVars(V, vtype=GRB.BINARY, name="in_cover")
for a, b in EDGES:
    model.addConstr(pick[a] + pick[b] >= 1, name=f"edge_{a}_{b}")
model.setObjective(pick.sum(), GRB.MINIMIZE)
model.Params.MIPGap = 0  # the default gap 1e-4 may stop at a non-optimal solution

# Keep the objective and collect every solution within PoolGap = 0 of the best.
model.Params.PoolSearchMode = 2
model.Params.PoolSolutions = 1000
model.Params.PoolGap = 0
model.optimize()

print("Status:", model.Status)
print("Minimum cover size:", round(model.ObjVal))
covers = set()
for k in range(model.SolCount):
    model.Params.SolutionNumber = k
    covers.add(tuple(i for i in range(V) if round(pick[i].Xn) == 1))
print("Optimal covers:", len(covers))
for c in sorted(covers):
    print("  ", list(c))
