
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
men = cp.intvar(0, 100, name="men")
women = cp.intvar(0, 100, name="women")
children = cp.intvar(0, 100, name="children")

# Constraints
model += (men + women + children == 100)          # total people
model += (women == 5 * men)                        # five times as many women as men
# Scale bushels by 2 to avoid fractions: men=6, women=4, children=1, total=200
model += (6 * men + 4 * women + children == 200)   # total bushels (scaled)

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
