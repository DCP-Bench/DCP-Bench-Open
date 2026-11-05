#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/abbots_puzzle.py

# Import libraries
from cpmpy import *
import json

# Decision variables
men = intvar(0, 100, name="men")
women = intvar(0, 100, name="women")
children = intvar(0, 100, name="children")

# Model
model = Model([
    men + women + children == 100,  # Total number of people
    men * 6 + women * 4 + children == 200,  # Total bushels of corn
    men * 5 == women  # Five times as many women as men
])

# Solve the model
model.solve()

# Print the solution
solution = {
    "men": men.value(),
    "women": women.value(),
    "children": children.value()
}
print(json.dumps(solution))
# End of CPMPy script
