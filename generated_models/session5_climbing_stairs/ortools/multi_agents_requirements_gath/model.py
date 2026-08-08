# Complete, runnable Python code that solves the stated constraint programming problem
# using Google OR-Tools CP-SAT.

import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# 1. Problem constants (immutable)
# ---------------------------------------------------------------------------
N = 20                 # length of the list and total height of the staircase
ALLOWED_STEPS = [0, 3, 4, 5]  # domain for each move (0 allowed after completion)

# ---------------------------------------------------------------------------
# 2. Build CP-SAT model
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: steps[i] for i = 0..19
steps = [model.NewIntVarFromDomain(cp_model.Domain.FromValues(ALLOWED_STEPS),
                                   f'steps_{i}') for i in range(N)]

# Helper Boolean variables indicating whether a given move is zero
is_zero = [model.NewBoolVar(f'is_zero_{i}') for i in range(N)]

# Link helper booleans with step variables
for i in range(N):
    # steps[i] == 0  <=>  is_zero[i] is true
    model.Add(steps[i] == 0).OnlyEnforceIf(is_zero[i])
    model.Add(steps[i] != 0).OnlyEnforceIf(is_zero[i].Not())

# ---------------------------------------------------------------------------
# 3. Constraints
# ---------------------------------------------------------------------------
# 3.1 Total climb equals N
model.Add(sum(steps) == N)

# 3.2 No prefix may exceed N (no overshoot)
for k in range(N):
    model.Add(sum(steps[:k + 1]) <= N)

# 3.3 Zeros can appear only after the first zero (monotone zeros)
for i in range(N - 1):
    # is_zero[i] => is_zero[i+1]
    model.AddImplication(is_zero[i], is_zero[i + 1])

# ---------------------------------------------------------------------------
# 4. Solve (pure feasibility, no objective)
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError('No feasible solution found.')

# ---------------------------------------------------------------------------
# 5. Extract and print solution as JSON
# ---------------------------------------------------------------------------
solution_steps = [int(solver.Value(var)) for var in steps]
print(json.dumps({"steps": solution_steps}))
