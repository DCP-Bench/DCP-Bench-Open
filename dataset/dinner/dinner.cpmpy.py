#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/dinner.py

# Import libraries
from cpmpy import *
import json


# variables
# "We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children"
grandparents = intvar(1, 6, name="grandparents")
parents = intvar(1, 10, name="parents")
children = intvar(1, 40, name="children")

model = Model([
    # "Grandparents cost $3 for dinner, parents $2 and children $0.50"
    # "There must be 20 total people at dinner ...
    grandparents * 6 + parents * 4 + children * 1 == 20 * 2,  # multiplied by 2 to not have decimals
    # ... and it must cost $20"
    grandparents + parents + children == 20
])

# Solve and print the solution
model.solve()

solution = {
    "grandparents": grandparents.value(),
    "parents": parents.value(),
    "children": children.value()
}
print(json.dumps(solution, indent=4))
# End of CPMPy script
