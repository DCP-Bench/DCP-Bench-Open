import json
from ortools.sat.python import cp_model
from math import isqrt

# ---------------------------------------------------------------------------
# 1.  Grid description -------------------------------------------------------
# ---------------------------------------------------------------------------
R = C = 9  # dimensions
# blocked cells (1-based coordinates) as given in the requirements document
blocked = {
    (1, 5),
    (2, 3), (2, 7),
    (3, 2), (3, 5), (3, 8),
    (4, 5),
    (5, 1), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 9),
    (6, 5),
    (7, 2), (7, 5), (7, 8),
    (8, 3), (8, 7),
    (9, 5),
}

# ---------------------------------------------------------------------------
# 2.  Enumerate Across and Down entries (length > 1) -------------------------
# ---------------------------------------------------------------------------

def enumerate_entries():
    """Return two dicts: across[number] = list[(r,c)],  down[number] = list[(r,c)]"""
    across, down = {}, {}
    number = 1

    # convenience lambdas ----------------------------------------------------
    def is_open(rc):
        return rc not in blocked

    def horiz_len(r, c):
        length = 0
        while c + length <= C and is_open((r, c + length)):
            length += 1
        return length

    def vert_len(r, c):
        length = 0
        while r + length <= R and is_open((r + length, c)):
            length += 1
        return length

    for r in range(1, R + 1):
        for c in range(1, C + 1):
            if not is_open((r, c)):
                continue

            starts_across = (
                (c == 1 or (r, c - 1) in blocked) and horiz_len(r, c) > 1
            )
            starts_down = (
                (r == 1 or (r - 1, c) in blocked) and vert_len(r, c) > 1
            )
            if not (starts_across or starts_down):
                continue

            # assign this clue number to every entry that starts here
            if starts_across:
                across[number] = [(r, cc) for cc in range(c, c + horiz_len(r, c))]
            if starts_down:
                down[number] = [(rr, c) for rr in range(r, r + vert_len(r, c))]

            number += 1
    return across, down

across_cells, down_cells = enumerate_entries()

# ---------------------------------------------------------------------------
# 3.  Helper sets for special domains ---------------------------------------
# ---------------------------------------------------------------------------
# 2-digit primes -------------------------------------------------------------
prime_2d = []
for n in range(11, 100):
    if all(n % p for p in range(2, isqrt(n) + 1)):
        prime_2d.append(n)

# 2- and 4-digit perfect squares -------------------------------------------
square_2d = [n * n for n in range(4, 10)]          # 16 … 81
square_4d = [n * n for n in range(32, 100)]         # 1024 … 9801

# ---------------------------------------------------------------------------
# 4.  Build CP-SAT model -----------------------------------------------------
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Digit variables ------------------------------------------------------------
M = [[None for _ in range(C)] for _ in range(R)]  # placeholders for open cells
cell_var = {}  # (r,c) -> IntVar
for r in range(1, R + 1):
    for c in range(1, C + 1):
        if (r, c) in blocked:
            continue
        v = model.NewIntVar(0, 9, f"d_{r}_{c}")
        cell_var[(r, c)] = v
        M[r - 1][c - 1] = v
    # blocked cells represented by None for now (will fill with -1 later)

# Entry variables -----------------------------------------------------------
A, D = {}, {}

# constants for across and down entries -------------------------------------
across_constants = {10: 72, 28: 48, 29: 1008}
down_constants  = {2: 60, 5: 84, 10: 76, 18: 56}

# helper to create IntVar with optional domain list --------------------------

def new_var(name, length, special_domain=None):
    if special_domain is not None:
        return model.NewIntVarFromDomain(cp_model.Domain.FromValues(special_domain), name)
    lo = 10 ** (length - 1)
    hi = 10 ** length - 1
    return model.NewIntVar(lo, hi, name)

# Across variables and digit linkage ----------------------------------------
for num, cells in across_cells.items():
    L = len(cells)
    if num in across_constants:
        var = model.NewIntVar(across_constants[num], across_constants[num], f"A{num}")
    elif num == 20:
        var = new_var(f"A{num}", L, square_4d)
    elif num == 23:
        var = new_var(f"A{num}", L, prime_2d)
    elif num == 24:
        var = new_var(f"A{num}", L, square_2d)
    else:
        var = new_var(f"A{num}", L)
    A[num] = var

    # digits to number linkage
    coeffs = []
    for idx, (r, c) in enumerate(cells):
        coeff = 10 ** (L - idx - 1)
        coeffs.append(coeff)
        model.Add(var == sum(10 ** (L - k - 1) * cell_var[cells[k]] for k in range(L)))

    # leading digit not zero if length > 1
    if L > 1:
        model.Add(cell_var[cells[0]] >= 1)

# Down variables and digit linkage ------------------------------------------
for num, cells in down_cells.items():
    L = len(cells)
    if num in down_constants:
        var = model.NewIntVar(down_constants[num], down_constants[num], f"D{num}")
    else:
        var = new_var(f"D{num}", L)
    D[num] = var

    model.Add(var == sum(10 ** (L - k - 1) * cell_var[cells[k]] for k in range(L)))
    if L > 1:
        model.Add(cell_var[cells[0]] >= 1)

# ---------------------------------------------------------------------------
# 5.  Arithmetic clue constraints -------------------------------------------
# ---------------------------------------------------------------------------
# Across constraints ---------------------------------------------------------
model.Add(A[1]   == A[27] * 2)
model.Add(A[4]   == D[4] + 71)
model.Add(A[7]   == D[18] + 4)
model.AddMultiplicationEquality(D[6], [A[23], model.NewConstant(48)])  # D6 = 48*A23
model.AddMultiplicationEquality(A[8], [model.NewConstant(1), A[8]])  # placeholder to ensure var exists
# Translate “A8 = D6 / 16”  → D6 = A8 * 16
model.AddMultiplicationEquality(D[6], [A[8], model.NewConstant(16)])
model.Add(A[9]  == D[2] - 18)
# A10 fixed = 72 already encoded
model.Add(A[11] == D[5] - 70)
# A13 = D26 * A23  (multiplication)
model.AddMultiplicationEquality(A[13], [D[26], A[23]])
# A15 = D6 - 350
model.Add(A[15] == D[6] - 350)
# A17 = A25 * A23
model.AddMultiplicationEquality(A[17], [A[25], A[23]])
# A20 perfect square domain handled
# A23 prime domain handled
# A24 perfect square domain handled
# A25 = A20 / 17  ->  A20 = 17 * A25
model.AddMultiplicationEquality(A[20], [A[25], model.NewConstant(17)])
# A27 = D6 / 4   -> D6 = 4 * A27
model.AddMultiplicationEquality(D[6], [A[27], model.NewConstant(4)])
# A28 fixed 48 already encoded
# A29 fixed 1008 already encoded
# A30 = D22 + 450
model.Add(A[30] == D[22] + 450)

# Down constraints -----------------------------------------------------------
model.Add(D[1]  == A[1] + 27)
# D2 fixed 60 already
model.Add(D[3]  == A[30] + 888)
model.Add(D[4]  == A[17] * 2)
# D5 fixed 84 already
model.AddMultiplicationEquality(D[6], [A[28], A[23]])
model.Add(D[10] == A[10] + 4)  # both constants but keep for clarity
model.AddMultiplicationEquality(D[12], [A[24], model.NewConstant(3)])
# D14 = A13 / 16  ->  A13 = 16 * D14
model.AddMultiplicationEquality(A[13], [D[14], model.NewConstant(16)])
model.AddMultiplicationEquality(D[16], [D[28], model.NewConstant(15)])
model.Add(D[17] == A[13] - 399)
# D18 fixed 56 already
model.Add(D[19] == D[22] - 94)
model.Add(D[20] == A[20] - 9)
model.Add(D[21] == A[25] - 52)
# D22 = 6 * D20
model.AddMultiplicationEquality(D[22], [D[20], model.NewConstant(6)])
# D26 = 5 * A24  already enforced via multiplication earlier, but add again for safety
model.AddMultiplicationEquality(D[26], [A[24], model.NewConstant(5)])
# D28 = D21 + 27
model.Add(D[28] == D[21] + 27)

# ---------------------------------------------------------------------------
# 6.  Solve ------------------------------------------------------------------
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError('No solution found')

# ---------------------------------------------------------------------------
# 7.  Extract grid -----------------------------------------------------------
# ---------------------------------------------------------------------------
M_solution = []
for r in range(1, R + 1):
    row = []
    for c in range(1, C + 1):
        if (r, c) in blocked:
            row.append(-1)
        else:
            row.append(solver.Value(cell_var[(r, c)]))
    M_solution.append(row)

print(json.dumps({"M": M_solution}))