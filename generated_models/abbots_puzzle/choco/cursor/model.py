from pychoco.model import Model
import json

model = Model("abbots_puzzle")

# Decision variables: number of men, women, and children
men = model.intvar(0, 100, "men")
women = model.intvar(0, 100, "women")
children = model.intvar(0, 100, "children")

# 100 people in total
model.sum([men, women, children], "=", 100).post()
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
model.scalar([men, women, children], [6, 4, 1], "=", 200).post()
# Five times as many women as men
model.arithm(women, "=", men, "*", 5).post()

if not model.get_solver().solve():
    raise SystemExit("No solution found.")

print(json.dumps({
    "men": men.get_value(),
    "women": women.get_value(),
    "children": children.get_value(),
}))
