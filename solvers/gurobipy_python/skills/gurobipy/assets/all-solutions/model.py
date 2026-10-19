"""All solutions: every set of 3 numbers from 1..6 that sums to 10."""
import gurobipy as gp
from gurobipy import GRB

N, PICK, TARGET = 6, 3, 10

model = gp.Model("subsets")
model.Params.OutputFlag = 0
pick = model.addVars(N, vtype=GRB.BINARY, name="pick")
model.addConstr(pick.sum() == PICK, name="size")
model.addConstr(gp.quicksum((i + 1) * pick[i] for i in range(N)) == TARGET, name="sum")
model.setObjective(0)  # satisfaction: enumerate feasible solutions

# The solution pool returns every feasible solution when PoolSolutions exceeds their number.
model.Params.PoolSearchMode = 2
model.Params.PoolSolutions = 2_000_000_000
model.optimize()

solutions = set()
for k in range(model.SolCount):
    model.Params.SolutionNumber = k
    solutions.add(tuple(round(pick[i].Xn) for i in range(N)))  # dedupe on the outputs

print("Status:", model.Status)
print("Solutions:", len(solutions))
for s in sorted(solutions):
    print("  {", ", ".join(str(i + 1) for i in range(N) if s[i]), "}")
