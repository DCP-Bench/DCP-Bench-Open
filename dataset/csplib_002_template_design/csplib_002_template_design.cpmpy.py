#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob002_template_design.py
# Source description: https://www.csplib.org/Problems/prob002/
# Problem instances: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob002_template_design.json

# Data
n_slots = 9  # The amount of slots on a template
n_templates = 2  # The amount of templates
n_var = 7  # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
ub = max(demand)  # The upper bound for the production

# create model
model = Model()

# decision variables
production = intvar(1, ub, shape=n_templates, name="production")
layout = intvar(0, n_slots, shape=(n_templates, n_var), name="layout")

# all slots are populated in a template
model += all(sum(layout[i]) == n_slots for i in range(n_templates))

# meet demand
for var in range(n_var):
    model += sum(production * layout[:, var]) >= demand[var]

# <SYMMETRY_BREAKING_CONSTRAINT_START>
# break symmetry
# equal demand
# for i in range(n_var - 1):
#     if demand[i] == demand[i + 1]:
#         model += layout[0, i] <= layout[0, i + 1]
#         for j in range(n_templates - 1):
#             model += (layout[j, i] == layout[j, i + 1]).implies(layout[j + 1, i] <= layout[j + 1, i + 1])

# distinguish templates
# for i in range(n_templates - 1):
#     model += production[i] <= production[i + 1]

# static symmetry
# for i in range(n_var - 1):
#     if demand[i] < demand[i + 1]:
#         model += sum(production * layout[:, i]) <= sum(production * layout[:, i + 1])
# <SYMMETRY_BREAKING_CONSTRAINT_END>

# implied: every template fills all its slots, so the sheets cover the total demand
model += n_slots * sum(production) >= sum(demand)

# minimize number of printed sheets
model.minimize(sum(production))

# Solve
model.solve()

# Print
solution = {"production": production.value().tolist(), "layout": layout.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
