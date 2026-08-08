
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
men = cp.IntVar(0, 100, name="men")
women = cp.IntVar(0, 100, name="women")
children = cp.IntVar(0, 100, name="children")

# Constraints
# 1) Total people is 100
# 2) Five times as many women as men
# 3) Multiply the bushel equation by 2 to avoid fractions:
#    6*men + 4*women + children = 200  (since each child is 0.5 bushel)
model += [
    men + women + children == 100,
    women == 5 * men,
    6 * men + 4 * women + children == 200
]

# Solve and print
if model.solve():
    solution = {
        'men': int(men.value()),
        'women': int(women.value()),
        'children': int(children.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
