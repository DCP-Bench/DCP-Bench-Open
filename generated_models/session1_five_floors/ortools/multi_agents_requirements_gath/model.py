import json
from ortools.sat.python import cp_model

# -------------------------------------------------------------
# 1. Parse input data (empty in this particular task)
# -------------------------------------------------------------
# The problem statement provides no dynamic input; all parameters
# are hard-coded according to the specification.

# -------------------------------------------------------------
# 2. Build the CP-SAT model
# -------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: floor (1..5) for each resident
B = model.NewIntVar(1, 5, 'B')  # Baker
C = model.NewIntVar(1, 5, 'C')  # Cooper
F = model.NewIntVar(1, 5, 'F')  # Fletcher
M = model.NewIntVar(1, 5, 'M')  # Miller
S = model.NewIntVar(1, 5, 'S')  # Smith

# All residents live on different floors
model.AddAllDifferent([B, C, F, M, S])

# -------------------------------------------------------------
# 3. Add constraints from the specification
# -------------------------------------------------------------
# 3.1 Specific floor exclusions
model.Add(B != 5)        # Baker not on 5th
model.Add(C != 1)        # Cooper not on 1st
model.Add(F != 1)        # Fletcher not on 1st
model.Add(F != 5)        # Fletcher not on 5th

# 3.2 Relative floor constraints
model.Add(M > C)         # Miller on a higher floor than Cooper

# 3.3 Non-adjacency constraints using absolute differences
# Create auxiliary variables for absolute differences
sf_diff = model.NewIntVar(0, 4, 'sf_diff')  # |S − F|
fc_diff = model.NewIntVar(0, 4, 'fc_diff')  # |F − C|

# Link auxiliary vars with absolute value constraints
model.AddAbsEquality(sf_diff, S - F)
model.AddAbsEquality(fc_diff, F - C)

# Enforce non-adjacency (difference cannot be 1)
model.Add(sf_diff != 1)
model.Add(fc_diff != 1)

# -------------------------------------------------------------
# 4. Solve the model (pure feasibility, no objective)
# -------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# -------------------------------------------------------------
# 5. Extract and print results as JSON
# -------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        'M': solver.Value(M),
        'C': solver.Value(C),
        'F': solver.Value(F),
        'B': solver.Value(B),
        'S': solver.Value(S)
    }
    print(json.dumps(result))
else:
    # If no solution exists, output an empty JSON object (contractually JSON output only)
    print(json.dumps({}))
