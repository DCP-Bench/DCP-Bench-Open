from hermax.model import Model
import json

model = Model()

# Decision variables: number of men, women, and children
men = model.int("men", 0, 100)
women = model.int("women", 0, 100)
children = model.int("children", 0, 100)

# 100 people in total
model &= (men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
model &= (6 * men + 4 * women + children == 200)
# Five times as many women as men
model &= (women == 5 * men)

result = model.solve()
if not result.ok:
    raise SystemExit("No solution found.")
assignment = result.assignment
print(json.dumps({
    "men": int(assignment[men]),
    "women": int(assignment[women]),
    "children": int(assignment[children]),
}))
