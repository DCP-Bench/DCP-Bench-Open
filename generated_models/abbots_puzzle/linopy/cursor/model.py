import linopy
import json

m = linopy.Model()
# Decision variables: number of men, women, and children
men = m.add_variables(lower=0, upper=100, integer=True, name="men")
women = m.add_variables(lower=0, upper=100, integer=True, name="women")
children = m.add_variables(lower=0, upper=100, integer=True, name="children")

# 100 people in total
m.add_constraints(men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
m.add_constraints(6 * men + 4 * women + children == 200)
# Five times as many women as men
m.add_constraints(women == 5 * men)
m.add_objective(0 * men)

status, _ = m.solve(solver_name="highs", display=False)
if men.solution is None:
    raise SystemExit(f"No solution found ({status}).")

print(json.dumps({
    "men": int(round(float(men.solution))),
    "women": int(round(float(women.solution))),
    "children": int(round(float(children.solution))),
}))
