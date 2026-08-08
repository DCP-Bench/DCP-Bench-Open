
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

# Total cost:
# To avoid non-integer costs (children = $0.50), scale all costs by 2:
# grandparents: $3 -> 6, parents: $2 -> 4, children: $0.5 -> 1
# Total scaled cost = $20 * 2 = 40
model += (6 * grandparents + 4 * parents + 1 * children == 40)

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
