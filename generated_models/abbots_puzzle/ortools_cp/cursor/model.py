from ortools.constraint_solver import pywrapcp
import json

solver = pywrapcp.Solver("abbots_puzzle")

# Decision variables: number of men, women, and children
men = solver.IntVar(0, 100, "men")
women = solver.IntVar(0, 100, "women")
children = solver.IntVar(0, 100, "children")

# 100 people in total
solver.Add(men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
solver.Add(6 * men + 4 * women + children == 200)
# Five times as many women as men
solver.Add(women == 5 * men)

db = solver.Phase(
    [men, women, children],
    solver.CHOOSE_FIRST_UNBOUND,
    solver.ASSIGN_MIN_VALUE,
)
solver.NewSearch(db)
if not solver.NextSolution():
    solver.EndSearch()
    raise SystemExit("No solution found.")
print(json.dumps({
    "men": men.Value(),
    "women": women.Value(),
    "children": children.Value(),
}))
solver.EndSearch()
