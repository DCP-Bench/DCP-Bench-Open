from optlang import Constraint, Model, Variable
import json

# Decision variables: number of men, women, and children
men = Variable("men", lb=0, ub=100, type="integer")
women = Variable("women", lb=0, ub=100, type="integer")
children = Variable("children", lb=0, ub=100, type="integer")

model = Model(name="abbots_puzzle")
model.add([
    # 100 people in total
    Constraint(men + women + children, lb=100, ub=100),
    # 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
    Constraint(6 * men + 4 * women + children, lb=200, ub=200),
    # Five times as many women as men
    Constraint(women - 5 * men, lb=0, ub=0),
])
status = model.optimize()
if men.primal is None:
    raise SystemExit(f"No solution found ({status}).")

print(json.dumps({
    "men": int(round(men.primal)),
    "women": int(round(women.primal)),
    "children": int(round(children.primal)),
}))
