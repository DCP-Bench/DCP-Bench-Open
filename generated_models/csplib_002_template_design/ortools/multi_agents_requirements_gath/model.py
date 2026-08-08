import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Immutable input parameters (do NOT modify)
# --------------------------------------------------
n_slots = 9                # number of slots on every template
n_templates = 2            # maximum number of templates that can be fabricated
n_var = 7                  # number of distinct carton variations
demand = [250, 255, 260, 500, 500, 800, 1100]  # demand per variation

# --------------------------------------------------
# CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# Some safe upper bounds -----------------------------------------------------
sum_demand = sum(demand)           # 3665 – printing 1 carton per sheet is enough
production_ub = sum_demand         # upper bound for sheets printed per template
prints_ub = production_ub * n_slots          # bound for production * slots
produced_ub = n_templates * prints_ub        # bound for total produced of a var

# Decision variables ---------------------------------------------------------
# layout[j][v] – how many of the 9 slots on template j are assigned to variation v
layout = [
    [model.NewIntVar(0, n_slots, f"layout_{j}_{v}") for v in range(n_var)]
    for j in range(n_templates)
]

# production[j] – number of mother sheets printed with template j
production = [
    model.NewIntVar(0, production_ub, f"production_{j}")
    for j in range(n_templates)
]

# prints[j][v] = production[j] * layout[j][v] -------------------------------
prints = []
for j in range(n_templates):
    row = []
    for v in range(n_var):
        pv = model.NewIntVar(0, prints_ub, f"prints_{j}_{v}")
        model.AddMultiplicationEquality(pv, [production[j], layout[j][v]])
        row.append(pv)
    prints.append(row)

# ---------------------------------------------------------------------------
# Hard constraints
# ---------------------------------------------------------------------------
# (C1) every template uses exactly n_slots slots
for j in range(n_templates):
    model.Add(sum(layout[j]) == n_slots)

# (C2) demand satisfaction
for v in range(n_var):
    model.Add(sum(prints[j][v] for j in range(n_templates)) >= demand[v])

# ---------------------------------------------------------------------------
# 1st optimisation stage – minimise total number of sheets
# ---------------------------------------------------------------------------
objective_1 = sum(production)
model.Minimize(objective_1)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
status = solver.Solve(model)
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible solution found in stage 1.")

best_total_sheets = solver.Value(objective_1)

# ---------------------------------------------------------------------------
# 2nd optimisation stage – minimise over-production given optimal sheets
# ---------------------------------------------------------------------------
# Fix primary objective value
model.Add(objective_1 == best_total_sheets)

# Produced quantity and over-production per variation
produced = []
overprod = []
for v in range(n_var):
    prod_v = model.NewIntVar(0, produced_ub, f"produced_{v}")
    model.Add(prod_v == sum(prints[j][v] for j in range(n_templates)))
    produced.append(prod_v)

    over_v = model.NewIntVar(0, produced_ub, f"over_{v}")
    model.Add(prod_v == demand[v] + over_v)
    overprod.append(over_v)

objective_2 = sum(overprod)
model.Minimize(objective_2)

solver2 = cp_model.CpSolver()
solver2.parameters.max_time_in_seconds = 30
status = solver2.Solve(model)
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible solution found in stage 2.")

# ---------------------------------------------------------------------------
# Extract and print solution
# ---------------------------------------------------------------------------
solution_layout = [[solver2.Value(layout[j][v]) for v in range(n_var)]
                   for j in range(n_templates)]
solution_production = [solver2.Value(p) for p in production]

print(json.dumps({
    "production": solution_production,
    "layout": solution_layout,
}))
