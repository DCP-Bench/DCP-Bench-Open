from z3 import Int, Solver, sat
import json

# Decision variables: number of men, women, and children
men = Int("men")
women = Int("women")
children = Int("children")

solver = Solver()
solver.add(men >= 0, men <= 100)
solver.add(women >= 0, women <= 100)
solver.add(children >= 0, children <= 100)

# 100 people in total
solver.add(men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
solver.add(6 * men + 4 * women + children == 200)
# Five times as many women as men
solver.add(women == 5 * men)

if solver.check() != sat:
    raise SystemExit("No solution found.")
model = solver.model()
print(json.dumps({
    "men": model[men].as_long(),
    "women": model[women].as_long(),
    "children": model[children].as_long(),
}))
