
import cpmpy as cp
import json

# Data
n_slots = 9  # The amount of slots on a template
n_templates = 2  # The amount of templates
n_var = 7  # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation

# Model definition
model = cp.Model()

# Decision Variables
# layout[t, v]: number of copies of variation v on template t (0..n_slots)
layout = cp.intvar(0, n_slots, shape=(n_templates, n_var), name="layout")

# production[t]: number of printed sheets of template t
# Upper bound: max demand divided by minimum number of copies of any variation on that template (at least 1)
# To be safe, upper bound can be max demand (1100)
production = cp.intvar(0, max(demand), shape=n_templates, name="production")

# Constraints

# 1) Each template can have at most n_slots copies in total
for t in range(n_templates):
    model += (cp.sum(layout[t, :]) <= n_slots)

# 2) Demand satisfaction: sum over templates of (copies per template * production) >= demand for each variation
for v in range(n_var):
    model += (cp.sum([layout[t, v] * production[t] for t in range(n_templates)]) >= demand[v])

# 3) If a variation is not on a template, layout[t,v] = 0
# (Already ensured by domain 0..n_slots)

# Objective: minimize total production (sum of printed sheets)
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
