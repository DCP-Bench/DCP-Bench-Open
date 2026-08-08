
import cpmpy as cp
import json

# Data
n_slots = 9  # The amount of slots on a template
n_templates = 2  # The amount of templates
n_var = 7  # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Number of printed sheets for each template
sum_demand = sum(demand)
production = cp.intvar(0, sum_demand, shape=n_templates, name="production")

# layout[t,v] = number of copies of variation v on template t (per sheet)
layout = cp.intvar(0, n_slots, shape=(n_templates, n_var), name="layout")

# Constraints
# Each template has exactly n_slots items printed per sheet
for t in range(n_templates):
    model += (cp.sum(layout[t, :]) == n_slots)

# Meet (or exceed) demand for each variation across all templates
for v in range(n_var):
    # sum_t layout[t,v] * production[t] >= demand[v]
    model += (cp.sum([layout[t, v] * production[t] for t in range(n_templates)]) >= demand[v])

# Objective: minimize total number of printed sheets
model.minimize(cp.sum(production))

# Solve and print
if model.solve():
    solution = {
        'production': production.value().tolist(),
        'layout': layout.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
