import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# No external input to parse – the instance is fully specified in the
# problem description.
# --------------------------------------------------

# Create the CP-SAT model
model = cp_model.CpModel()

# --------------------------------------------------
# Decision variables
# Every variable stores the index {0: Debra, 1: Janet, 2: Hugh, 3: Rick}
# --------------------------------------------------
var_names = [
    'malone',  # surname Malone
    'baxter',  # surname Baxter
    'nuts',    # allergy nuts
    'ragweed', # allergy ragweed
    'mold',    # allergy mold
    'fleet',   # surname Fleet
    'lemon',   # surname Lemon
    'eggs'     # allergy eggs
]

# Helper dictionary name -> IntVar
vars_dict = {
    name: model.NewIntVar(0, 3, name) for name in var_names
}

# Shorthand access
malone  = vars_dict['malone']
baxter  = vars_dict['baxter']
nuts    = vars_dict['nuts']
ragweed = vars_dict['ragweed']
mold    = vars_dict['mold']
fleet   = vars_dict['fleet']
lemon   = vars_dict['lemon']
eggs    = vars_dict['eggs']

# --------------------------------------------------
# Constraints
# --------------------------------------------------
# C1: All surnames different
model.AddAllDifferent([baxter, lemon, malone, fleet])

# C2: All allergies different
model.AddAllDifferent([eggs, mold, nuts, ragweed])

# C3: Rick (index 3) is not allergic to mold
model.Add(mold != 3)

# C4: Baxter is allergic to eggs (same friend index)
model.Add(baxter == eggs)

# C5: Hugh (index 2) is neither Lemon nor Fleet
model.Add(lemon != 2)
model.Add(fleet != 2)

# C6: Debra (index 0) is allergic to ragweed
model.Add(ragweed == 0)

# C7: Janet (index 1) constraints
model.Add(lemon != 1)
model.Add(eggs != 1)
model.Add(mold != 1)

# --------------------------------------------------
# Solve
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError('No solution found')

# --------------------------------------------------
# Output in required JSON format
# --------------------------------------------------
result = {name: solver.Value(vars_dict[name]) for name in var_names}
print(json.dumps(result))
