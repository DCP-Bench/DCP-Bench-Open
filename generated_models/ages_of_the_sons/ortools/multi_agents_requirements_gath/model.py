#!/usr/bin/env python3
"""Solve the “ages of three sons” riddle with Google OR-Tools (CP-SAT).

The script follows the formal requirements supplied with the task and
prints **only** a JSON object that contains the decision-variable values
with the exact keys `['A3', 'A1', 'A2']` – in that order.
"""

import json
from collections import defaultdict
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# 1. Enumerate every unordered triple (A1 ≥ A2 ≥ A3 ≥ 1) whose product is 36.
# ---------------------------------------------------------------------------
PRODUCT = 36
triples = []
for a in range(1, PRODUCT + 1):
    if PRODUCT % a:
        continue
    for b in range(1, a + 1):                           # enforce a ≥ b
        if (PRODUCT // a) % b:
            continue
        c = PRODUCT // (a * b)
        if c > b or c < 1:                              # need b ≥ c ≥ 1
            continue
        triples.append((a, b, c))

# ---------------------------------------------------------------------------
# 2. Pre-analyse the triples so the verbal clues can be expressed via a
#    single AllowedAssignments table inside the CP model.
# ---------------------------------------------------------------------------
unique_oldest = {t: int(t[0] > t[1]) for t in triples}   # 1 ⇔ A1 > A2
sum_to_triples = defaultdict(list)
for t in triples:
    sum_to_triples[sum(t)].append(t)

valid_triples = []  # triples satisfying *all* clues from the story
for t in triples:
    a, b, _ = t

    # Clue: there is a unique oldest son
    if not (a > b):
        continue

    # Clue: the sum of the ages was ambiguous
    same_sum = sum_to_triples[sum(t)]
    if len(same_sum) < 2:
        continue

    # Clue: after hearing “the oldest has blue eyes” the mathematician knew
    #       the ages ⇒ within this sum exactly one triple has a unique oldest
    if sum(unique_oldest[s] for s in same_sum) != 1:
        continue

    valid_triples.append(t)

# The classical riddle leaves exactly one triple (9,2,2).
if not valid_triples:
    raise RuntimeError("No triple satisfies all verbal clues – check logic.")

allowed_rows = [list(t) for t in valid_triples]  # convert tuples → lists

# ---------------------------------------------------------------------------
# 3. Build the CP-SAT model.
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables (ages)
A1 = model.NewIntVar(1, PRODUCT, 'A1')  # oldest
A2 = model.NewIntVar(1, PRODUCT, 'A2')  # middle
A3 = model.NewIntVar(1, PRODUCT, 'A3')  # youngest

# Core constraints taken verbatim from the requirements
model.Add(A1 >= A2)                 # ordering (oldest ≥ middle)
model.Add(A2 >= A3)                 # ordering (middle ≥ youngest)
model.Add(A1 > A2)                  # unique-oldest condition
model.AddMultiplicationEquality(PRODUCT, [A1, A2, A3])  # product = 36

# Verbal-clue logic encoded via a table of pre-validated triples
model.AddAllowedAssignments([A1, A2, A3], allowed_rows)

# No objective – we only need a feasible assignment
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    raise RuntimeError('Solver reported the model as infeasible.')

# ---------------------------------------------------------------------------
# 4. Output – strictly the JSON object with keys ['A3', 'A1', 'A2'].
# ---------------------------------------------------------------------------
result = {
    'A3': solver.Value(A3),  # youngest
    'A1': solver.Value(A1),  # oldest
    'A2': solver.Value(A2)   # middle
}
print(json.dumps(result))
