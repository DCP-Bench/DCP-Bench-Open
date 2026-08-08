import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Input data (exactly as provided by the exercise)
# --------------------------------------------------
num_people = 8  # number of people
compatible = [                 # 1-based indexing in the raw list
    [2, 3],                    # patient 1 can donate to 2, 3
    [1, 6],                    # patient 2 → 1, 6
    [1, 4, 7],                 # patient 3 → 1, 4, 7
    [2],                      
    [2],
    [5],
    [8],
    [3]
]

# --------------------------------------------------
# Pre-processing: convert every ID from 1-based → 0-based
# --------------------------------------------------
compatible_0 = []
for donor, recipients in enumerate(compatible):
    # shift indices and remove any accidental self-loop
    new_list = [r - 1 for r in recipients if (r - 1) != donor]
    compatible_0.append(new_list)

# --------------------------------------------------
# Create CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# Decision variables: x[(i,j)] is 1 if patient i donates to patient j
x = {}
for i in range(num_people):
    for j in compatible_0[i]:
        x[(i, j)] = model.NewBoolVar(f"x_{i}_{j}")

# 1. Each donor donates at most one kidney
for i in range(num_people):
    out_vars = [x[(i, j)] for j in compatible_0[i]]
    if out_vars:                       # skip if patient cannot donate to anyone
        model.Add(sum(out_vars) <= 1)

# 2. Each recipient receives at most one kidney
for j in range(num_people):
    in_vars = [x[(i, j)] for i in range(num_people) if (i, j) in x]
    if in_vars:                        # skip if no one can donate to j
        model.Add(sum(in_vars) <= 1)

# 3. Donate  ⇔  Receive  (balance incoming and outgoing)
for k in range(num_people):
    out_vars = [x[(k, j)] for j in compatible_0[k]]
    in_vars  = [x[(i, k)] for i in range(num_people) if (i, k) in x]
    # Only post when the equality is not trivially 0 == 0 to avoid bool constant
    if out_vars or in_vars:
        model.Add(sum(out_vars) == sum(in_vars))

# Objective: maximise total number of actual transplants
model.Maximize(sum(x.values()))

# --------------------------------------------------
# Solve the model
# --------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety time-out
status = solver.Solve(model)

# --------------------------------------------------
# Extract solution into full num_people × num_people matrix
# --------------------------------------------------
transplants = [[0 for _ in range(num_people)] for _ in range(num_people)]

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    for (i, j), var in x.items():
        transplants[i][j] = int(solver.Value(var))
else:
    # If no solution was found (should not occur for the given data),
    # an all-zero matrix is still a valid JSON according to spec.
    pass

# --------------------------------------------------
# Output: JSON with the required key
# --------------------------------------------------
print(json.dumps({"transplants": transplants}))
