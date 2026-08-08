
import cpmpy as cp
import json

# Data
n_slots = 9  # The amount of slots on a template
n_templates = 2  # The amount of templates
n_var = 7  # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation
# End of data

# Upper bounds
sum_demand = sum(demand)  # global upper bound for productions / intermediate vars

# Model definition
model = cp.Model()

# Decision Variables
# Number of printed sheets for each template
# Upper bound can be sum_demand (safe)
production = cp.intvar(0, sum_demand, shape=n_templates, name="production")

# layout[t,v] = number of copies of variation v on template t (per sheet)
layout = cp.intvar(0, n_slots, shape=(n_templates, n_var), name="layout")

# To linearize the product production[t] * layout[t,v], we decompose layout into booleans:
# y[t,v,k] == 1 iff layout[t,v] == k, for k in 0..n_slots
y = cp.boolvar(shape=(n_templates, n_var, n_slots + 1), name="y")

# z[t,v,k] will represent production[t] * y[t,v,k]  (product of intvar and bool)
# Upper bound for production is sum_demand, so z in [0, sum_demand]
z = cp.intvar(0, sum_demand, shape=(n_templates, n_var, n_slots + 1), name="z")

# Constraints

# Link y and layout: for each (t,v), exactly one k is chosen and layout equals that k
for t in range(n_templates):
    for v in range(n_var):
        # Exactly one k chosen
        model += (cp.sum(y[t, v, :]) == 1)
        # layout[t,v] == sum_k k * y[t,v,k]
        model += (cp.sum([k * y[t, v, k] for k in range(n_slots + 1)]) == layout[t, v])

# Each template has exactly n_slots items printed per sheet
for t in range(n_templates):
    model += (cp.sum(layout[t, :]) == n_slots)

# Linearize z[t,v,k] = production[t] * y[t,v,k] using Big-M (sum_demand as M)
M = sum_demand
for t in range(n_templates):
    for v in range(n_var):
        for k in range(n_slots + 1):
            # z <= production
            model += (z[t, v, k] <= production[t])
            # z <= M * y
            model += (z[t, v, k] <= M * y[t, v, k])
            # z >= production - M * (1 - y)
            model += (z[t, v, k] >= production[t] - M * (1 - y[t, v, k]))
            # z >= 0  (already domain, but we keep it conceptually)
            model += (z[t, v, k] >= 0)

# Demand constraints:
# total printed of variation v is sum_t sum_k k * z[t,v,k]  (since z is production * y_k)
for v in range(n_var):
    model += (cp.sum([k * z[t, v, k] for t in range(n_templates) for k in range(n_slots + 1)]) >= demand[v])

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
