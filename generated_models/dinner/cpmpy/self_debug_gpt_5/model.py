
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
grandparents = cp.intvar(1, 6, name="grandparents")
parents = cp.intvar(1, 10, name="parents")
children = cp.intvar(1, 40, name="children")

# Constraints
# Total people
model += (grandparents + parents + children == 20)

# Cost constraints (scale by 2 to avoid fractions: $3->6, $2->4, $0.5->1, $20->40)
model += (6*grandparents + 4*parents + children == 40)

# Solve and print
if model.solve():
    solution = {
        'grandparents': int(grandparents.value()),
        'parents': int(parents.value()),
        'children': int(children.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
