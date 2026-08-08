# -*- coding: utf-8 -*-
"""
Google OR-Tools CP-SAT solution for the candy distribution (rating) problem.
The program:
  • sets up decision variables for the number of candies per child and the
    total candies (z),
  • imposes all problem constraints, and
  • minimises the total number of candies.
Finally, it prints the optimal value of z as a JSON object – exactly
matching the required output specification.
"""

import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# Input data (immutable – do not modify)
# ---------------------------------------------------------------------------
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
n = len(ratings)

# ---------------------------------------------------------------------------
# Model creation
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables ---------------------------------------------------------
# candies[i] – candies given to child i (at least 1, at most n – see analysis)
candies = [model.NewIntVar(1, n, f"candies_{i}") for i in range(n)]

# z – total candies; upper-bounded by n*(n+1)//2 (worst-case 1..n assignment)
max_total_candies = n * (n + 1) // 2
z = model.NewIntVar(0, max_total_candies, "z")

# Constraints ----------------------------------------------------------------
# Neighbour jealousy constraints
for i in range(n - 1):
    if ratings[i] > ratings[i + 1]:
        # Child i has a higher rating -> must receive strictly more candies
        model.Add(candies[i] >= candies[i + 1] + 1)
    elif ratings[i] < ratings[i + 1]:
        # Child i+1 has a higher rating -> must receive strictly more candies
        model.Add(candies[i + 1] >= candies[i] + 1)
    # If ratings are equal, no extra constraint is necessary.

# Definition of total candies
model.Add(z == sum(candies))

# Objective ------------------------------------------------------------------
model.Minimize(z)

# ---------------------------------------------------------------------------
# Solve the model
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ---------------------------------------------------------------------------
# Output the result as required (JSON with key 'z')
# ---------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {"z": solver.Value(z)}
else:
    result = {"z": None}  # Infeasible/unknown (should not occur for this task)

print(json.dumps(result))
