#!/usr/bin/env python3
"""Send More Money – CP-SAT model using Google OR-Tools.
Solves the classic cryptarithmetic addition puzzle
   SEND
 + MORE
 -------
  MONEY
and prints the unique solution as a JSON object whose keys are exactly
['y', 'e', 's', 'r', 'o', 'd', 'm', 'n'].
"""

import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# 1. Input parsing (none required for this puzzle, placeholder kept for spec)
# ---------------------------------------------------------------------------
# The <input_data> section is empty, so there is nothing to parse. We keep the
# placeholder to adhere strictly to the instruction of parsing the given input
# exactly as provided.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 2. Model construction
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: one IntVar per distinct letter
letters = 's e n d m o r y'.split()
vars_ = {l: model.NewIntVar(0, 9, l.upper()) for l in letters}

s, e, n, d, m, o, r, y = (vars_[l] for l in letters)

# All-different constraint
model.AddAllDifferent(list(vars_.values()))

# Leading letters cannot be zero (S and M)
model.Add(s != 0)
model.Add(m != 0)

# Arithmetic correctness constraint
# 1000*S + 100*E + 10*N + D
# + 1000*M + 100*O + 10*R + E
# = 10000*M + 1000*O + 100*N + 10*E + Y
lhs = (
    1000 * s + 100 * e + 10 * n + d +
    1000 * m + 100 * o + 10 * r + e
)
rhs = 10000 * m + 1000 * o + 100 * n + 10 * e + y
model.Add(lhs == rhs)

# No objective – feasibility problem

# ---------------------------------------------------------------------------
# 3. Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ---------------------------------------------------------------------------
# 4. Output
# ---------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        'y': solver.Value(y),
        'e': solver.Value(e),
        's': solver.Value(s),
        'r': solver.Value(r),
        'o': solver.Value(o),
        'd': solver.Value(d),
        'm': solver.Value(m),
        'n': solver.Value(n),
    }
    print(json.dumps(result))
else:
    # If for some reason no solution exists (should not happen), print empty JSON
    print(json.dumps({k: None for k in ['y','e','s','r','o','d','m','n']}))
