# Import libraries
from cpmpy import *
import json

# Parameters
n_slots = 9  # The amount of slots on a template
n_templates = 2  # The amount of templates
n_var = 7  # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation

# Decision Variables
production = intvar(0, max(demand), shape=n_templates, name="production")  # Number of printed sheets per template
layout = intvar(0, n_var-1, shape=(n_templates, n_slots), name="layout")  # Layout of templates

# Auxiliary variables to count occurrences of each variation in each template
counts = intvar(0, n_slots, shape=(n_templates, n_var), name="counts")

# Model
model = Model()

# Each slot in each template must be assigned a valid variation
for t in range(n_templates):
    for s in range(n_slots):
        model += (layout[t,s] >= 0) & (layout[t,s] < n_var)

# Count the number of occurrences of each variation in each template
for t in range(n_templates):
    for v in range(n_var):
        model += (counts[t,v] == sum(layout[t,:] == v))

# The production must be sufficient to meet the demand for each variation
for v in range(n_var):
    model += (sum(counts[:,v] * production) >= demand[v])

# Solve the model
model.minimize(sum(production))
model.solve()

# Print the solution
solution = {
    "production": production.value().tolist(),
    "layout": layout.value().tolist()
}
print(json.dumps(solution))