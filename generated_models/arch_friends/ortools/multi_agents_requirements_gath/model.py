#!/usr/bin/env python3
"""
Google OR-Tools CP-SAT model for the Harriet shoe-shopping logic puzzle.
All four shoes and all four stores are assigned to the shopping positions 1-4
subject to the narrative clues.  The program prints a JSON object that maps
 every decision-variable name to the integer position that satisfies all
 constraints.
"""

import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# 1. Model
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Domain of shopping positions
POSITIONS = range(1, 5)  # {1,2,3,4}

# ---------------------------------------------------------------------------
# 2. Decision variables  (integer position of every shoe / store)
# ---------------------------------------------------------------------------
# Shoes
ecruespadrilles  = model.NewIntVar(1, 4, 'ecruespadrilles')
fuchsiaflats     = model.NewIntVar(1, 4, 'fuchsiaflats')
purplepumps      = model.NewIntVar(1, 4, 'purplepumps')
suedesandals     = model.NewIntVar(1, 4, 'suedesandals')

# Stores
footfarm         = model.NewIntVar(1, 4, 'footfarm')
heelsinahandcart = model.NewIntVar(1, 4, 'heelsinahandcart')
theshoepalace    = model.NewIntVar(1, 4, 'theshoepalace')
tootsies         = model.NewIntVar(1, 4, 'tootsies')

# Convenience collections
shoe_vars  = [ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]
store_vars = [footfarm, heelsinahandcart, theshoepalace, tootsies]

# ---------------------------------------------------------------------------
# 3. Constraints
# ---------------------------------------------------------------------------
# 3.1 All-different constraints for uniqueness within each category
model.AddAllDifferent(shoe_vars)
model.AddAllDifferent(store_vars)

# 3.2 Narrative clues translated into algebraic constraints
# 1) Fuchsia flats were bought at Heels in a Handcart
model.Add(fuchsiaflats == heelsinahandcart)

# 2) Immediately after buying purple pumps Harriet visits a store that is not Tootsies
model.Add(purplepumps <= 3)                 # ensures a "next" stop exists
model.Add(tootsies != purplepumps + 1)      # that next stop is NOT Tootsies

# 3) Foot Farm was Harriet's second stop
model.Add(footfarm == 2)

# 4) Two stops after leaving The Shoe Palace she bought the suede sandals
model.Add(theshoepalace <= 2)               # so that +2 remains in domain 1..4
model.Add(suedesandals == theshoepalace + 2)

# ---------------------------------------------------------------------------
# 4. Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError('No solution found for the puzzle.')

# ---------------------------------------------------------------------------
# 5. Output  (exact key order required by the instructions)
# ---------------------------------------------------------------------------
result = {
    'ecruespadrilles':  solver.Value(ecruespadrilles),
    'purplepumps':      solver.Value(purplepumps),
    'theshoepalace':    solver.Value(theshoepalace),
    'suedesandals':     solver.Value(suedesandals),
    'footfarm':         solver.Value(footfarm),
    'fuchsiaflats':     solver.Value(fuchsiaflats),
    'tootsies':         solver.Value(tootsies),
    'heelsinahandcart': solver.Value(heelsinahandcart),
}

print(json.dumps(result))
