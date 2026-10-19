# Assignment: give each worker a different job at minimum total cost.
# The job of each worker is an integer linked to one-hot binaries; all-different is then
# "each job used at most once", far stronger than pairwise != constraints.
from pyscipopt import Model, quicksum

cost = [[9, 2, 7, 8],
        [6, 4, 3, 7],
        [5, 8, 1, 8],
        [7, 6, 9, 4]]
n = len(cost)

m = Model("assignment")
m.hideOutput()
b = {(w, j): m.addVar(vtype="B", name=f"b_{w}_{j}") for w in range(n) for j in range(n)}
job = [m.addVar(vtype="I", lb=0, ub=n - 1, name=f"job_{w}") for w in range(n)]
for w in range(n):
    m.addCons(quicksum(b[w, j] for j in range(n)) == 1)          # one job per worker
    m.addCons(job[w] == quicksum(j * b[w, j] for j in range(n)))  # integer view of the choice
for j in range(n):
    m.addCons(quicksum(b[w, j] for w in range(n)) <= 1)           # all-different
# hold the objective in a bounded integer variable
total = m.addVar(vtype="I", lb=0, ub=sum(max(row) for row in cost), name="total")
m.addCons(total == quicksum(cost[w][j] * b[w, j] for w in range(n) for j in range(n)))
m.setObjective(total, "minimize")

m.optimize()
status = m.getStatus()
print("Status:", status)
if status == "optimal":
    print("Total cost:", round(m.getVal(total)))
    print("Jobs:", [round(m.getVal(v)) for v in job])
