#!/usr/bin/env python3
"""Solve the corn–distribution puzzle with Google OR-Tools (CP-SAT).

Requirements recap
------------------
men   + women + children                = 100  (total people)
3*men + 2*women + 0.5*children          = 100  (total bushels)
women = 5*men                                  (gender ratio)
All variables are non-negative integers.
The program prints the unique solution as JSON with the keys
["men", "women", "children"].
"""
import json
from ortools.sat.python import cp_model

# ----------------------------
# 1. Model
# ----------------------------
model = cp_model.CpModel()

# Decision variables: bounds 0..100 (more than enough for this puzzle)
men = model.NewIntVar(0, 100, 'men')
women = model.NewIntVar(0, 100, 'women')
children = model.NewIntVar(0, 100, 'children')

# ----------------------------
# 2. Constraints
# ----------------------------
# C1: Total number of people
model.Add(men + women + children == 100)

# C2: Total corn allocation (multiply by 2 to keep coefficients integral)
model.Add(6 * men + 4 * women + children == 200)

# C3: Five times as many women as men
model.Add(women == 5 * men)

# No objective – just find any feasible solution

# ----------------------------
# 3. Solve
# ----------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ----------------------------
# 4. Output
# ----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        'men': solver.Value(men),
        'women': solver.Value(women),
        'children': solver.Value(children),
    }
    print(json.dumps(result))
else:
    # For completeness; problem guarantees feasibility.
    print(json.dumps({'men': None, 'women': None, 'children': None}))
