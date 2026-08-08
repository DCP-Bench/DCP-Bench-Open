from cpmpy import *
import json

# Decision variables
men = intvar(0, 100, name="men")
women = intvar(0, 100, name="women")
children = intvar(0, 100, name="children")

# Model
model = Model()

# Total number of people is 100
model += [men + women + children == 100]

# Total bushels distributed is 100 (scaled by 2 to avoid fractions)
model += [6 * men + 4 * women + children == 200]

# There are five times as many women as men
model += [women == 5 * men]

# Solve the model
model.solve()

# Print the solution
solution = {"men": men.value(), "women": women.value(), "children": children.value()}
print(json.dumps(solution))