# 0/1 knapsack: choose items of maximum total value within the capacity.
from pyscipopt import Model, quicksum

weights = [3, 4, 2, 5]
values = [40, 50, 30, 60]
capacity = 7

m = Model("knapsack")
m.hideOutput()
take = [m.addVar(vtype="B", name=f"take_{i}") for i in range(len(weights))]
m.addCons(quicksum(w * t for w, t in zip(weights, take)) <= capacity)
m.setObjective(quicksum(v * t for v, t in zip(values, take)), "maximize")

m.optimize()
status = m.getStatus()
print("Status:", status)
if status == "optimal":  # the default gap is 0, so this optimum is proven
    print("Objective:", round(m.getObjVal()))
    print("Items:", [i for i, t in enumerate(take) if m.getVal(t) > 0.5])
