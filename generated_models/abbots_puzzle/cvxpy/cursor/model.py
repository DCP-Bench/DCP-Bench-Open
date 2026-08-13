import cvxpy as cp
import json

# Decision variables: number of men, women, and children
men = cp.Variable(integer=True, name="men")
women = cp.Variable(integer=True, name="women")
children = cp.Variable(integer=True, name="children")

constraints = [
    men >= 0, men <= 100,
    women >= 0, women <= 100,
    children >= 0, children <= 100,
    # 100 people in total
    men + women + children == 100,
    # 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
    6 * men + 4 * women + children == 200,
    # Five times as many women as men
    women == 5 * men,
]
prob = cp.Problem(cp.Minimize(0), constraints)
prob.solve(solver=cp.HIGHS, verbose=False)
if men.value is None:
    raise SystemExit(f"No solution found ({prob.status}).")

print(json.dumps({
    "men": int(round(float(men.value))),
    "women": int(round(float(women.value))),
    "children": int(round(float(children.value))),
}))
