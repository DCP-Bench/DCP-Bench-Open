from mip import Model, INTEGER, OptimizationStatus
import json

model = Model(solver_name="CBC")
model.verbose = 0

# Decision variables: number of men, women, and children
men = model.add_var(var_type=INTEGER, lb=0, ub=100, name="men")
women = model.add_var(var_type=INTEGER, lb=0, ub=100, name="women")
children = model.add_var(var_type=INTEGER, lb=0, ub=100, name="children")

# 100 people in total
model += men + women + children == 100
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
model += 6 * men + 4 * women + children == 200
# Five times as many women as men
model += women == 5 * men

status = model.optimize()
if status not in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
    raise SystemExit(f"No solution found ({status}).")

print(json.dumps({
    "men": int(round(men.x)),
    "women": int(round(women.x)),
    "children": int(round(children.x)),
}))
