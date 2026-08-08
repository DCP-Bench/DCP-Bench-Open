#!/usr/bin/env python3
"""Langford L(k,n) sequencing – CP-SAT implementation with Google OR-Tools

Usage (no interactive input):
    python langford.py               # solves default instance k=4, n=7
    python langford.py 11            # solves k=4, n=11

The script NEVER calls input() nor reads external files; n may be passed as
an optional command-line argument.  It prints exactly one JSON object with the
mandatory keys
    ["position", "solution"].

Both structures are reported 1-based as required by the specification.
"""

import sys
import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# Fixed / input parameters
# ---------------------------------------------------------------------------
K = 4  # number of identical copies of every integer (given, immutable)

# Largest value n can be supplied on the command line; default to 7 because
# L(4,7) is the smallest non-trivial solvable instance for k=4.
if len(sys.argv) > 1:
    try:
        N = int(sys.argv[1])
        if N <= 0:
            raise ValueError
    except ValueError:
        print("Command-line argument must be a positive integer.")
        sys.exit(1)
else:
    N = 7

# Derived sequence length
P = K * N  # total number of positions in the sequence

# ---------------------------------------------------------------------------
# Model construction
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables ---------------------------------------------------------
# position[m][c] : absolute 0-based index of copy c (0..K-1) of value m (1..N)
position = {
    m: [model.NewIntVar(0, P - 1, f"pos_{m}_{c}") for c in range(K)]
    for m in range(1, N + 1)
}

# solution[j] : value located at 0-based position j in the final sequence
solution = [model.NewIntVar(1, N, f"sol_{j}") for j in range(P)]

# ---------------------------------------------------------------------------
# Hard constraints
# ---------------------------------------------------------------------------

# C2 & C3 – Langford spacing and ordering
for m in range(1, N + 1):
    for c in range(K - 1):
        # spacing equality implicitly enforces order as well
        model.Add(position[m][c + 1] == position[m][c] + m + 1)
        model.Add(position[m][c + 1] > position[m][c])  # explicit C2

# Optional pruning: first copy must leave room for the remaining K-1 copies
for m in range(1, N + 1):
    latest_start = P - 1 - (K - 1) * (m + 1)
    if latest_start >= 0:
        model.Add(position[m][0] <= latest_start)

# C4 – all positions are pair-wise different (implies C6 exhaustiveness)
model.AddAllDifferent([position[m][c] for m in range(1, N + 1) for c in range(K)])

# C5 – coherence between position[][] and solution[] via Element constraint
for m in range(1, N + 1):
    for c in range(K):
        model.AddElement(position[m][c], solution, m)

# C7 – each value appears exactly K times in the sequence
#   We create indicator Booleans b_{j,m}:  b == 1  ⇔  solution[j] == m
indicators = {}
for j in range(P):
    row_bools = []
    for m in range(1, N + 1):
        b = model.NewBoolVar(f"is_{m}_at_{j}")
        indicators[(j, m)] = b
        model.Add(solution[j] == m).OnlyEnforceIf(b)
        model.Add(solution[j] != m).OnlyEnforceIf(b.Not())
        row_bools.append(b)
    # Every position is assigned exactly one value
    model.Add(sum(row_bools) == 1)

for m in range(1, N + 1):
    model.Add(sum(indicators[(j, m)] for j in range(P)) == K)

# Simple symmetry breaking: first occurrence of value 1 before first of value N
model.Add(position[1][0] < position[N][0])

# ---------------------------------------------------------------------------
# Solve the model
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
# Use all available CPU cores for faster search
solver.parameters.num_search_workers = 8
status = solver.Solve(model)

# ---------------------------------------------------------------------------
# Produce the required JSON output
# ---------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    # Convert positions to 1-based for user friendliness
    pos_out = [[solver.Value(position[m][c]) + 1 for c in range(K)]
               for m in range(1, N + 1)]
    sol_out = [solver.Value(solution[j]) for j in range(P)]
else:
    pos_out = []
    sol_out = []

print(json.dumps({"position": pos_out, "solution": sol_out}))
