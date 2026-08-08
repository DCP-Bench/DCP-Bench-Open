import json
from ortools.sat.python import cp_model

# -----------------------------
# Constant Data (problem sets)
# -----------------------------
HOUSES = range(1, 6)  # 1 .. 5 (left -> right)

COLORS_ORDER = ["yellow", "green", "red", "white", "blue"]
NATIONS_ORDER = ["italy", "spain", "japan", "england", "norway"]
JOBS_ORDER    = ["painter", "sculptor", "diplomat", "pianist", "doctor"]
PETS_ORDER    = ["cat", "zebra", "bear", "snails", "horse"]
DRINKS_ORDER  = ["milk", "water", "tea", "coffee", "juice"]

# -----------------------------
# Helper for reified equality
# -----------------------------

def add_reified_equality(model: cp_model.CpModel, var1, var2, name):
    """Create boolean representing (var1 == var2)"""
    b = model.NewBoolVar(name)
    model.Add(var1 == var2).OnlyEnforceIf(b)
    model.Add(var1 != var2).OnlyEnforceIf(b.Not())
    return b

# -----------------------------
# Model Building
# -----------------------------
model = cp_model.CpModel()

# Decision variables: one IntVar per attribute value, domain 1..5 (house index)
colors  = {c: model.NewIntVar(1, 5, f"pos_color_{c}")   for c in COLORS_ORDER}
nations = {n: model.NewIntVar(1, 5, f"pos_nation_{n}")  for n in NATIONS_ORDER}
jobs    = {j: model.NewIntVar(1, 5, f"pos_job_{j}")     for j in JOBS_ORDER}
pets    = {p: model.NewIntVar(1, 5, f"pos_pet_{p}")     for p in PETS_ORDER}
drinks  = {d: model.NewIntVar(1, 5, f"pos_drink_{d}")   for d in DRINKS_ORDER}

# Permutation (all-different) constraints for each category
model.AddAllDifferent(colors.values())
model.AddAllDifferent(nations.values())
model.AddAllDifferent(jobs.values())
model.AddAllDifferent(pets.values())
model.AddAllDifferent(drinks.values())

# -----------------------------
# Clue Constraints
# -----------------------------
# Direct equalities
model.Add(jobs["painter"]   == pets["horse"])    # painter owns horse
model.Add(jobs["diplomat"] == drinks["coffee"])  # diplomat drinks coffee
model.Add(drinks["milk"]   == colors["white"])  # milk in white house
model.Add(nations["spain"] == jobs["painter"])  # Spaniard is painter
model.Add(nations["england"] == colors["red"])  # Englishman in red house
model.Add(pets["snails"]  == jobs["sculptor"]) # snails owned by sculptor
model.Add(jobs["doctor"]   == drinks["milk"])  # doctor drinks milk
model.Add(jobs["diplomat"] == nations["japan"]) # diplomat is Japanese
model.Add(nations["norway"] == pets["zebra"])  # Norwegian owns zebra

# Positional relations
model.Add(colors["green"] < colors["red"])      # green left of red
model.Add(nations["norway"] > colors["blue"])  # Norwegian right of blue

# Green next to White (|diff| == 1)
diff_gw = model.NewIntVar(-4, 4, "diff_gw")
abs_diff_gw = model.NewIntVar(1, 4, "abs_diff_gw")
model.Add(diff_gw == colors["green"] - colors["white"])
model.AddAbsEquality(abs_diff_gw, diff_gw)
model.Add(abs_diff_gw == 1)

# Horse next to Diplomat
horse_diplom_diff = model.NewIntVar(-4, 4, "diff_hd")
abs_diff_hd = model.NewIntVar(1, 4, "abs_diff_hd")
model.Add(horse_diplom_diff == pets["horse"] - jobs["diplomat"])
model.AddAbsEquality(abs_diff_hd, horse_diplom_diff)
model.Add(abs_diff_hd == 1)

# Italian lives in red OR white OR green house
b1 = add_reified_equality(model, nations["italy"], colors["red"],   "italy_red")
b2 = add_reified_equality(model, nations["italy"], colors["white"], "italy_white")
b3 = add_reified_equality(model, nations["italy"], colors["green"], "italy_green")
model.AddBoolOr([b1, b2, b3])

# -----------------------------
# Solve
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # safety limit
status = solver.Solve(model)

if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    raise RuntimeError("No solution found for the Zebra puzzle variant.")

# -----------------------------
# Extract Solution in requested order
# -----------------------------
solution = {
    "colors":  [solver.Value(colors[c])  for c in COLORS_ORDER],
    "jobs":    [solver.Value(jobs[j])    for j in JOBS_ORDER],
    "nations": [solver.Value(nations[n]) for n in NATIONS_ORDER],
    "pets":    [solver.Value(pets[p])    for p in PETS_ORDER],
    "drinks":  [solver.Value(drinks[d])  for d in DRINKS_ORDER],
}

print(json.dumps(solution))