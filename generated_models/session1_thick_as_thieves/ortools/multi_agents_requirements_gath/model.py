#!/usr/bin/env python3
"""Sparkles the Jeweller’s robbery logic puzzle – CP-SAT model.

The program decides which of the six suspects are guilty under the
assumptions given by Inspector Korner (≤2 people in the getaway car and
perfect truth-telling by the innocent, lying by the guilty).

The result is printed as a JSON object with the mandatory key order:
['dodgy', 'fingers', 'edgy', 'bill', 'artie', 'crackitt']
"""

import sys
import json
from ortools.sat.python import cp_model

# -------------------------------------------------------------
# 1. Model & variables
# -------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: 1 = guilty, 0 = innocent
artie    = model.NewBoolVar('artie')
bill     = model.NewBoolVar('bill')
crackitt = model.NewBoolVar('crackitt')
dodgy    = model.NewBoolVar('dodgy')
edgy     = model.NewBoolVar('edgy')
fingers  = model.NewBoolVar('fingers')

suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

# Total number of guilty people (1 or 2)
g = model.NewIntVar(1, 2, 'guilty_count')
model.Add(g == sum(suspects))

# -------------------------------------------------------------
# 2. Constraints derived from the statements
# -------------------------------------------------------------
# 2.1 Bill: "Crackitt was in it up to his neck."
#      -> crackitt = 1 - bill
model.Add(bill + crackitt == 1)

# 2.2 Dodgy: "If Crackitt did it, Bill did it with him."  (¬C ∨ B)
#      Truth value variable for Dodgy's statement
s_dodgy = model.NewBoolVar('stmt_dodgy')
# allowed table for (crackitt, bill, statement truth)
model.AddAllowedAssignments([crackitt, bill, s_dodgy],
                            [
                                [0, 0, 1],  # implication true (antecedent false)
                                [0, 1, 1],  # implication true
                                [1, 0, 0],  # implication false
                                [1, 1, 1],  # implication true
                            ])
# Innocent tell truth, guilty lie => statement truth + speaker guilt = 1
model.Add(s_dodgy + dodgy == 1)

# 2.3 Edgy: "Nobody did it alone."  -> g = 2 when statement true
#      Relation g + edgy == 2 captures both truth/lie requirements
model.Add(g + edgy == 2)

# 2.4 Fingers: "That’s right: it was Artie and Dodgy together."
#      Statement is true  <=>  (artie=1 ∧ dodgy=1 ∧ g=2)
# Boolean helper: g_is_two  (g == 2)
g_is_two = model.NewBoolVar('g_is_two')
# g is 1 or 2, so g == 1 + g_is_two
model.Add(g == 1 + g_is_two)

# Boolean helper: artie ∧ dodgy
artie_and_dodgy = model.NewBoolVar('artie_and_dodgy')
model.Add(artie_and_dodgy <= artie)
model.Add(artie_and_dodgy <= dodgy)
model.Add(artie_and_dodgy >= artie + dodgy - 1)

# Statement truth for Fingers
s_fingers = model.NewBoolVar('stmt_fingers')
# s_fingers = artie_and_dodgy ∧ g_is_two
model.Add(s_fingers <= artie_and_dodgy)
model.Add(s_fingers <= g_is_two)
model.Add(s_fingers >= artie_and_dodgy + g_is_two - 1)
# Innocent tell truth, guilty lie
model.Add(s_fingers + fingers == 1)

# -------------------------------------------------------------
# 3. Solve
# -------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(json.dumps({
        'dodgy': None,
        'fingers': None,
        'edgy': None,
        'bill': None,
        'artie': None,
        'crackitt': None
    }))
    sys.exit(0)

# -------------------------------------------------------------
# 4. Output JSON in the requested key order
# -------------------------------------------------------------
result = {
    'dodgy':    solver.Value(dodgy),
    'fingers':  solver.Value(fingers),
    'edgy':     solver.Value(edgy),
    'bill':     solver.Value(bill),
    'artie':    solver.Value(artie),
    'crackitt': solver.Value(crackitt)
}

print(json.dumps(result))
