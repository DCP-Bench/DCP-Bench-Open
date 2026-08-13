import picos
import json

P = picos.Problem()
# Decision variables: number of men, women, and children
men = picos.IntegerVariable("men")
women = picos.IntegerVariable("women")
children = picos.IntegerVariable("children")
P.add_constraint(0 <= men)
P.add_constraint(men <= 100)
P.add_constraint(0 <= women)
P.add_constraint(women <= 100)
P.add_constraint(0 <= children)
P.add_constraint(children <= 100)
# 100 people in total
P.add_constraint(men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
P.add_constraint(6 * men + 4 * women + children == 200)
# Five times as many women as men
P.add_constraint(women == 5 * men)
P.set_objective("min", 0 * men)

sol = P.solve(solver="scip", verbosity=0)
if men.value is None:
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": int(round(float(men))),
    "women": int(round(float(women))),
    "children": int(round(float(children))),
}))
