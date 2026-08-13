from pyscipopt import Model
import json

model = Model()
model.hideOutput()

# Decision variables: number of men, women, and children
men = model.addVar(vtype="I", lb=0, ub=100, name="men")
women = model.addVar(vtype="I", lb=0, ub=100, name="women")
children = model.addVar(vtype="I", lb=0, ub=100, name="children")

# 100 people in total
model.addCons(men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
model.addCons(6 * men + 4 * women + children == 200)
# Five times as many women as men
model.addCons(women == 5 * men)

model.optimize()
if model.getStatus() not in ("optimal", "feasible"):
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": int(round(model.getVal(men))),
    "women": int(round(model.getVal(women))),
    "children": int(round(model.getVal(children))),
}))
