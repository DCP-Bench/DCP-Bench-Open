# Resource-constrained scheduling: tasks with durations and worker demands share a crew
# of 3 workers; task 3 starts after task 0 ends. Minimise the makespan.
from pyscipopt import Model

durations = [3, 2, 4, 2, 3]
demands = [2, 1, 2, 2, 1]
capacity = 3
precedences = [(0, 3)]          # (before, after)
horizon = sum(durations)

m = Model("rcpsp")
m.hideOutput()
start = [m.addVar(vtype="I", lb=0, ub=horizon - d, name=f"s{i}") for i, d in enumerate(durations)]
# at no time do the running tasks need more than the capacity
m.addConsCumulative(start, durations, demands, capacity)
for a, b in precedences:
    m.addCons(start[a] + durations[a] <= start[b])
makespan = m.addVar(vtype="I", lb=0, ub=horizon, name="makespan")
for s, d in zip(start, durations):
    m.addCons(makespan >= s + d)
m.setObjective(makespan, "minimize")

m.optimize()
status = m.getStatus()
print("Status:", status)
if status == "optimal":
    print("Makespan:", round(m.getVal(makespan)))
    for i, s in enumerate(start):
        t = round(m.getVal(s))
        print(f"task {i}: {t}-{t + durations[i]}")
