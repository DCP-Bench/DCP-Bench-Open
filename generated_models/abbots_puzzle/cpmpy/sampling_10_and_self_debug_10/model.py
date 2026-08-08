
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
men = cp.intvar(0, 100, name="men")
women = cp.intvar(0, 100, name="women")
children = cp.intvar(0, 100, name="children")

# Constraints
model += (men + women + children == 100)
model += (women == 5 * men)

# Multiply bushels by 2 to avoid fractions:
# men: 3 bushels -> 6 half-bushels
# women: 2 bushels -> 4 half-bushels
# children: 0.5 bushels -> 1 half-bushel
model += (6 * men + 4 * women + children == 200)

# Solve and print
if model.solve():
    solution = {'men': int(men.value()), 'women': int(women.value()), 'children': int(children.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
