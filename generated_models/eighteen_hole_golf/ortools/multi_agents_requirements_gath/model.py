import json
import random
from ortools.sat.python import cp_model

# ---------------------------
# Problem constants
# ---------------------------
N_HOLES = 18              # total number of golf holes
ALLOWED_PARS = [3, 4, 5]  # admissible par values for each hole
TOTAL_PAR = 72            # required total par of the course

# ---------------------------
# CP-SAT model
# ---------------------------
model = cp_model.CpModel()

# Decision variables: one integer variable per hole restricted to {3,4,5}
holes = [
    model.NewIntVarFromDomain(cp_model.Domain.FromValues(ALLOWED_PARS), f"hole_{i}")
    for i in range(N_HOLES)
]

# Constraint: total par of the course must equal 72
model.Add(sum(holes) == TOTAL_PAR)

# No optimisation objective is required; we just need a feasible solution.
# Adding a dummy objective (minimise 0) keeps the model purely feasible.
model.Minimize(0)

# ---------------------------
# Solve the model
# ---------------------------
solver = cp_model.CpSolver()

# Optional: add some randomness so we don't always get the same layout
solver.parameters.random_seed = random.randint(1, 1_000_000)

status = solver.Solve(model)

# ---------------------------
# Output the solution in the required JSON format
# ---------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [int(solver.Value(var)) for var in holes]
    print(json.dumps({"holes": solution}))
else:
    # If no solution is found, output an empty list to adhere to the expected JSON schema
    print(json.dumps({"holes": []}))
