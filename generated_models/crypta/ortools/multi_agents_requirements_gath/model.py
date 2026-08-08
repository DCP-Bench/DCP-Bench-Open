import json
from ortools.sat.python import cp_model

# -------------------------------------------------------------
# Cryptarithmetic puzzle
#     B A I J J A J I I A H F C F E B B J E A
#   + D H F G A B C D I D B I F F A G F E J E
#   ------------------------------------------
#     G J E G A C D D H F A F J B F I H E E F
# -------------------------------------------------------------
# We must assign each of the ten letters A..J a distinct decimal
# digit so that the long addition is correct (with the usual base–10
# carries).  Leading letters (B, D, G) may not be zero.
# -------------------------------------------------------------

# Create CP-SAT model
model = cp_model.CpModel()

# 1. Decision variables for the ten letters
letters = list("ABCDEFGHIJ")
letter_vars = {l: model.NewIntVar(0, 9, l) for l in letters}

# 2. Carries: c_k is the carry INTO column k (k = 1..20);
#    c_0 and c_21 are fixed to 0.  We index carries[0..20]
#    so carries[k] is the carry into column k+1 in zero-based Python.
#    Only c_1..c_19 are true variables (boolean 0/1).
carriers = [model.NewConstant(0)]  # c_0 = 0
for k in range(1, 20):  # c_1 .. c_19
    carriers.append(model.NewBoolVar(f"c{k}"))
carriers.append(model.NewConstant(0))  # c_20 = 0 (no overflow)

# 3. AllDifferent constraint for the letters
model.AddAllDifferent(list(letter_vars.values()))

# 4. Leading letters must not be zero
for l in ("B", "D", "G"):
    model.Add(letter_vars[l] != 0)

# 5. Column-wise addition constraints (units column = index 0)
addend1 = [
    "A", "E", "J", "B", "B", "E", "F", "C", "F", "H",
    "A", "I", "I", "J", "A", "J", "J", "I", "A", "B",
]
addend2 = [
    "E", "J", "E", "F", "G", "A", "F", "F", "I", "B",
    "D", "I", "D", "C", "B", "A", "G", "F", "H", "D",
]
sumcol = [
    "F", "E", "E", "H", "I", "F", "B", "J", "F", "A",
    "F", "H", "D", "D", "C", "A", "G", "E", "J", "G",
]

# Sanity check: length should be 20
assert len(addend1) == len(addend2) == len(sumcol) == 20

for k in range(20):
    # a1 + a2 + carry_in = sum + 10*carry_out
    a1 = letter_vars[addend1[k]]
    a2 = letter_vars[addend2[k]]
    s  = letter_vars[sumcol[k]]
    cin = carriers[k]        # carry into this column
    cout = carriers[k + 1]   # carry out of this column
    # The equation is linear and directly supported by CP-SAT
    model.Add(a1 + a2 + cin == s + cout * 10)

# 6. Solve the model (pure feasibility)
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety limit
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    keys = ["H", "D", "J", "G", "E", "C", "I", "F", "A", "B"]
    result = {k: solver.Value(letter_vars[k]) for k in keys}
    print(json.dumps(result))
else:
    print(json.dumps({}))