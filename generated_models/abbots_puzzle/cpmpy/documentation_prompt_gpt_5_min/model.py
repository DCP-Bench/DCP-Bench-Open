
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
men = cp.intvar(0, 16, name="men")        # m <= floor(100/6) = 16
women = cp.intvar(0, 100, name="women")
children = cp.intvar(0, 100, name="children")

# Constraints
model += (men + women + children == 100)   # total people
model += (women == 5 * men)                # five times as many women as men
# Scale bushels by 2 to avoid fractions: man=6, woman=4, child=1, total=200
model += (6 * men + 4 * women + 1 * children == 200)

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
