import json
from ortools.sat.python import cp_model

# -----------------------------
# Data definition
# -----------------------------
# Alphabet without Q and Z, in natural alphabetical order
letters = [ch for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if ch not in ("Q", "Z")]
assert len(letters) == 24  # sanity check
index_of = {ch: idx for idx, ch in enumerate(letters)}

# List of 4-letter words that must be spellable (each letter on a different block)
words = [
    "BAKE", "ONYX", "ECHO", "OVAL",
    "GIRD", "SMUG", "JUMP", "TORN",
    "LUCK", "VINY", "LUSH", "WRAP",
]

# -----------------------------
# Model construction
# -----------------------------
model = cp_model.CpModel()

# Decision variables: dice[l] is the block index (0..3) carrying letter l
num_blocks = 4
faces_per_block = 6

dice = [model.NewIntVar(0, num_blocks - 1, f"dice_{l}") for l in letters]

# Helper boolean matrix: is_letter_on_block[(i,b)] is true iff letter i sits on block b
is_letter_on_block = {}
for i, l in enumerate(letters):
    bools = []
    for b in range(num_blocks):
        v = model.NewBoolVar(f"is_{l}_{b}")
        is_letter_on_block[(i, b)] = v
        # Channeling between integer and booleans
        model.Add(dice[i] == b).OnlyEnforceIf(v)
        model.Add(dice[i] != b).OnlyEnforceIf(v.Not())
        bools.append(v)
    # Each letter is placed on exactly one block
    model.AddExactlyOne(bools)

# Cardinality: each block must carry exactly six letters
for b in range(num_blocks):
    model.Add(sum(is_letter_on_block[(i, b)] for i in range(len(letters))) == faces_per_block)

# Word feasibility: letters of each word must reside on distinct blocks
for w in words:
    idxs = [index_of[ch] for ch in w]
    for i in range(4):
        for j in range(i + 1, 4):
            model.Add(dice[idxs[i]] != dice[idxs[j]])

# -----------------------------
# Solve
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # optional time limit
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible assignment found for the given constraints.")

solution = [int(solver.Value(var)) for var in dice]

# -----------------------------
# Output
# -----------------------------
print(json.dumps({"dice": solution}))