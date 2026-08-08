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
total_demand = sum(demand)  # Total number of cartons to be printed

# Decision Variables
# production: number of printed sheets (each sheet uses one template)
production = intvar(0, 10000, shape=n_templates, name="production")

# layout: how many of each variation are included in each template
layout = intvar(0, n_slots, shape=(n_templates, n_var), name="layout")

# Model
model = Model()

# Each template must have exactly n_slots variations in total
for t in range(n_templates):
    model += [sum(layout[t, :]) == n_slots]

# The total number of each variation printed must meet the demand
for v in range(n_var):
    model += [sum(layout[t, v] * production[t] for t in range(n_templates)) == demand[v]]

# Additional constraint to reduce search space: production must be at least 1
model += [production >= 1]

# Solve
model.solve()

# Print
solution = {
    "production": production.value().tolist(),
    "layout": layout.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script