import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# Immutable data that fully specifies the crossword fill problem
# ---------------------------------------------------------------------------

# Catalogue of 15 words already sorted (longest first, then alphabetically)
CATALOGUE = [
    "HOSES",  # 0 – length 5
    "LASER",  # 1 – length 5
    "SAILS",  # 2 – length 5
    "SHEET",  # 3 – length 5
    "STEER",  # 4 – length 5
    "HEEL",   # 5 – length 4
    "HIKE",   # 6 – length 4
    "KEEL",   # 7 – length 4
    "KNOT",   # 8 – length 4
    "LINE",   # 9 – length 4
    "AFT",    # 10 – length 3
    "ALE",    # 11 – length 3
    "EEL",    # 12 – length 3
    "LEE",    # 13 – length 3
    "TIE",    # 14 – length 3
]

NUM_WORDS = len(CATALOGUE)          # 15
MAX_WORD_LEN = max(len(w) for w in CATALOGUE)  # 5

# The eight numbered locations in the crossword (1–8)
LENGTH_PER_LOCATION = [5, 5, 5, 4, 4, 3, 3, 5]  # L_1 … L_8
NUM_LOCATIONS = len(LENGTH_PER_LOCATION)         # 8

# Crossing equality constraints P   (all indices made 0-based in this list)
# Format: (location_i, pos_i, location_j, pos_j) where pos indices are 0-based
CROSSINGS = [
    (0, 2, 1, 0),   # (1,3, 2,1)
    (0, 4, 2, 0),   # (1,5, 3,1)
    (1, 2, 3, 1),   # (2,3, 4,2)
    (1, 3, 6, 0),   # (2,4, 7,1)
    (1, 4, 7, 2),   # (2,5, 8,3)
    (2, 2, 3, 3),   # (3,3, 4,4)
    (2, 3, 6, 2),   # (3,4, 7,3)
    (2, 4, 7, 4),   # (3,5, 8,5)
    (3, 2, 4, 0),   # (4,3, 5,1)
    (4, 1, 6, 1),   # (5,2, 7,2)
    (4, 2, 7, 3),   # (5,3, 8,4)
    (5, 1, 7, 0),   # (6,2, 8,1)
]

# ---------------------------------------------------------------------------
# Helper data structures
# ---------------------------------------------------------------------------

# Pre-compute letter code tables for quick element constraints
# letter_codes[pos][word_index] = ord(letter) if that position exists else 0
letter_codes = []  # will become a list of lists, outer index = position (0..4)
for p in range(MAX_WORD_LEN):
    codes_for_p = []
    for w in CATALOGUE:
        if p < len(w):
            codes_for_p.append(ord(w[p]))
        else:
            codes_for_p.append(0)  # dummy value, never used thanks to length filter
    letter_codes.append(codes_for_p)

# Map length -> list of catalogue indices having exactly that length
length_to_indices = {}
for idx, w in enumerate(CATALOGUE):
    length_to_indices.setdefault(len(w), []).append(idx)

# ---------------------------------------------------------------------------
# Build CP-SAT model
# ---------------------------------------------------------------------------

model = cp_model.CpModel()

# Decision variables ---------------------------------------------------------
E = []  # catalogue index chosen for each location (0-based)
for n, required_len in enumerate(LENGTH_PER_LOCATION):
    domain_vals = length_to_indices[required_len]
    var = model.NewIntVarFromDomain(cp_model.Domain.FromValues(domain_vals), f"E_{n+1}")
    E.append(var)

# All-different constraint ---------------------------------------------------
model.AddAllDifferent(E)

# Character variables and element constraints --------------------------------
# char_vars[n][k] = integer code of k-th character of the word placed at loc n
char_vars = []
for n, required_len in enumerate(LENGTH_PER_LOCATION):
    loc_chars = []
    for k in range(required_len):
        cvar = model.NewIntVar(0, 127, f"C_{n+1}_{k+1}")
        # Element constraint: character value determined by selected word
        model.AddElement(E[n], letter_codes[k], cvar)
        loc_chars.append(cvar)
    char_vars.append(loc_chars)

# Crossing equality constraints ---------------------------------------------
for (loc1, pos1, loc2, pos2) in CROSSINGS:
    model.Add(char_vars[loc1][pos1] == char_vars[loc2][pos2])

# No objective (pure feasibility) -------------------------------------------

# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10.0  # a polite time limit
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_E = [int(solver.Value(v)) for v in E]
    print(json.dumps({"E": solution_E}))
else:
    # No solution found (should not happen for this puzzle)
    print(json.dumps({"E": []}))
