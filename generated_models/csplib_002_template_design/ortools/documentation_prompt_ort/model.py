from ortools.sat.python import cp_model
import json

# Input data
n_slots = 9  # The amount of slots on a template
n_templates = 2  # The amount of templates
n_var = 7  # The amount of different variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # The demand per variation

# Model definition
model = cp_model.CpModel()

# Decision Variables
# layout[t][v]: number of copies of variation v on template t (0..n_slots)
layout = []
for t in range(n_templates):
    row = []
    for v in range(n_var):
        row.append(model.NewIntVar(0, n_slots, f'layout_{t}_{v}'))
    layout.append(row)

# production[t]: number of printed sheets for template t
# Upper bound can be max demand because we cannot produce more than max demand per template
max_demand = max(demand)
production = [model.NewIntVar(0, max_demand, f'production_{t}') for t in range(n_templates)]

# Constraints

# 1) Each template can have at most n_slots items printed on it
for t in range(n_templates):
    model.Add(sum(layout[t][v] for v in range(n_var)) <= n_slots)

# 2) The total production for each variation must meet the demand exactly
# sum over templates of (layout[t][v] * production[t]) == demand[v]
for v in range(n_var):
    model.Add(
        sum(layout[t][v] * production[t] for t in range(n_templates)) == demand[v]
    )

# Objective: minimize total production (sum of printed sheets)
model.Minimize(sum(production))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    production_val = [solver.Value(production[t]) for t in range(n_templates)]
    layout_val = []
    for t in range(n_templates):
        layout_val.append([solver.Value(layout[t][v]) for v in range(n_var)])
    solution = {
        'production': production_val,
        'layout': layout_val
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")