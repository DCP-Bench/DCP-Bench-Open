
import cpmpy as cp
import json

# Data (optional)
n_slots = 9       # The amount of slots on a template
n_templates = 2   # The amount of templates
n_var = 7         # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation
# End of data

# Helper computations
total_demand = sum(demand)
lb_total_sheets = (total_demand + n_slots - 1) // n_slots  # ceil(total_demand / n_slots)
# A safe upper bound per template: one template could print everything alone
ub_production = lb_total_sheets

# Model definition
model = cp.Model()

# Decision Variables
# Number of printed sheets per template
production = cp.intvar(0, ub_production, shape=n_templates, name="production")

# Layout counts: number of each variation on each template (per sheet)
layout = cp.intvar(0, n_slots, shape=(n_templates, n_var), name="layout")

# One-hot encoding of layout counts: y[t,v,k] = 1 iff layout[t,v] = k
# k ranges from 0..n_slots
y = cp.boolvar(shape=(n_templates, n_var, n_slots + 1), name="y")

# Constraints

# 1) Each template uses exactly n_slots per sheet
for t in range(n_templates):
    model += (cp.sum([layout[t, v] for v in range(n_var)]) == n_slots)

# 2) One-hot for layout counts via y
for t in range(n_templates):
    for v in range(n_var):
        # exactly one k chosen
        model += (cp.sum([y[t, v, k] for k in range(n_slots + 1)]) == 1)
        # layout equals the chosen k
        model += (layout[t, v] == cp.sum([k * y[t, v, k] for k in range(n_slots + 1)]))

# 3) Demand satisfaction:
# For each variation v, total produced across templates must be >= demand[v]
# total produced for v = sum_t production[t] * layout[t,v]
# Linearize using y: layout[t,v] = sum_k k*y[t,v,k]
# so produced for v = sum_{t,k} (k*production[t]) * y[t,v,k]
for v in range(n_var):
    model += (
        cp.sum([(k * production[t]) * y[t, v, k]
                for t in range(n_templates)
                for k in range(n_slots + 1)]) >= demand[v]
    )

# 4) Strengthening: total sheets must be at least the global lower bound
model += (cp.sum(production) >= lb_total_sheets)

# 5) Symmetry breaking between templates
model += (production[0] >= production[1])
model += cp.LexLessEq(layout[0, :].tolist(), layout[1, :].tolist())

# Objective: minimize total number of printed sheets
model.minimize(cp.sum(production))

# Solve and print
if model.solve():
    solution = {
        'production': [int(p) for p in production.value().tolist()],
        'layout': [[int(x) for x in layout[t, :].value().tolist()] for t in range(n_templates)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
