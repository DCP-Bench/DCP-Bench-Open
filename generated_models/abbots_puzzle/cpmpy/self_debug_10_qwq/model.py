
import cpmpy as cp
import json

model = cp.Model()

# Decision Variables
men = cp.intvar(0, 16, name="men")
women = cp.intvar(0, 80, name="women")
children = cp.intvar(0, 100, name="children")

# Constraints
model += (men + women + children == 100)
model += (6 * men + 4 * women + children == 200)
model += (women == 5 * men)

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
