from exact import Exact
import json

solver = Exact()

# Decision variables: number of men, women, and children
solver.addVariable("men", 0, 100)
solver.addVariable("women", 0, 100)
solver.addVariable("children", 0, 100)

# 100 people in total
solver.addConstraint([(1, "men"), (1, "women"), (1, "children")], True, 100, True, 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
solver.addConstraint([(6, "men"), (4, "women"), (1, "children")], True, 200, True, 200)
# Five times as many women as men
solver.addConstraint([(5, "men"), (-1, "women")], True, 0, True, 0)

status = solver.runFull(optimize=False)
if status != "SAT" or not solver.hasSolution():
    raise SystemExit(f"No solution found ({status}).")
men, women, children = solver.getLastSolutionFor(["men", "women", "children"])
print(json.dumps({
    "men": int(men),
    "women": int(women),
    "children": int(children),
}))
