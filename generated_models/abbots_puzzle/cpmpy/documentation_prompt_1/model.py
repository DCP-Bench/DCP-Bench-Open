
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# men, women, children are non-negative integers
men = cp.intvar(0, 100, name="men")
women = cp.intvar(0, 100, name="women")
children = cp.intvar(0, 100, name="children")

# Constraints
# Total people = 100
model += (men + women + children == 100)

# Total bushels = 100
# men get 3 bushels each, women 2 each, children 0.5 each
model += (3*men + 2*women + children//2 == 100)

# There are five times as many women as men
model += (women == 5*men)

# Solve and print
if model.solve():
    solution = {'men': int(men.value()), 'women': int(women.value()), 'children': int(children.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
