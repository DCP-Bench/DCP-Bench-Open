""" 
Feasibility model for constructing a set S of n=8 DNA words that satisfy
 all distance / GC–content requirements stated in the problem description.

The model uses Google OR-Tools CP-SAT.  Each character is represented by an
 IntVar in domain {0:A, 1:C, 2:G, 3:T}.  Auxiliary variables implement
 complement, GC-indicator, and pairwise distance reification.
The solver is asked for the first feasible solution and prints it as JSON.
"""

from ortools.sat.python import cp_model
import json

# ---------------------------------------------------------------------------
# Input data (immutable as required)
# ---------------------------------------------------------------------------
n = 8  # Number of words to find (|S|)
L = 8  # Length of each word
ALPHABET = ['A', 'C', 'G', 'T']  # index -> letter

# ---------------------------------------------------------------------------
# CP-SAT model
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# 1. Decision variables : word characters ------------------------------------------------
char = [[model.NewIntVar(0, 3, f"w{j}_p{k}") for k in range(L)]
        for j in range(n)]  # 0:A, 1:C, 2:G, 3:T

# 2. Watson–Crick complement variables ---------------------------------------------------
comp = [[model.NewIntVar(0, 3, f"c{j}_p{k}") for k in range(L)]
        for j in range(n)]
allowed_comp = [(0, 3),  # A -> T
                (1, 2),  # C -> G
                (2, 1),  # G -> C
                (3, 0)]  # T -> A
for j in range(n):
    for k in range(L):
        model.AddAllowedAssignments([char[j][k], comp[j][k]], allowed_comp)

# 3. GC-content (exactly 4 of the 8 positions must be C or G) -----------------------------
allowed_cg = [(0, 0),  # A  -> not CG
              (1, 1),  # C  -> CG
              (2, 1),  # G  -> CG
              (3, 0)]  # T  -> not CG
for j in range(n):
    cg_flags = []
    for k in range(L):
        cg = model.NewBoolVar(f"isCG_{j}_{k}")
        model.AddAllowedAssignments([char[j][k], cg], allowed_cg)
        cg_flags.append(cg)
    model.Add(sum(cg_flags) == 4)

# 4. Pairwise Hamming distance between distinct words >= 4 -------------------------------
for i in range(n):
    for j2 in range(i + 1, n):
        diffs = []
        for k in range(L):
            d = model.NewBoolVar(f"diff_{i}_{j2}_{k}")
            model.Add(char[i][k] == char[j2][k]).OnlyEnforceIf(d.Not())
            model.Add(char[i][k] != char[j2][k]).OnlyEnforceIf(d)
            diffs.append(d)
        model.Add(sum(diffs) >= 4)

# 5. Distance between reverse of any word and complement of any (inc. itself) >= 4 -------
for i in range(n):
    for j2 in range(n):  # note: j2 may equal i
        rc_diffs = []
        for k in range(L):
            # k-th symbol of reverse(word_i)
            rev_char = char[i][L - 1 - k]
            comp_char = comp[j2][k]
            d = model.NewBoolVar(f"rcdiff_{i}_{j2}_{k}")
            model.Add(rev_char == comp_char).OnlyEnforceIf(d.Not())
            model.Add(rev_char != comp_char).OnlyEnforceIf(d)
            rc_diffs.append(d)
        model.Add(sum(rc_diffs) >= 4)

# 6. Mild symmetry breaking (lexicographic order of words) -------------------------------
weights = [4 ** (L - 1 - k) for k in range(L)]  # high-order weight first char
codes = []
for j in range(n):
    code = model.NewIntVar(0, 4 ** L - 1, f"code_{j}")
    model.Add(code == sum(char[j][k] * weights[k] for k in range(L)))
    codes.append(code)
for j in range(n - 1):
    model.Add(codes[j] < codes[j + 1])

# Also fix first letter of first word to 'A' to break some symmetry
model.Add(char[0][0] == 0)

# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # safety (can be removed)
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No solution found.")

# ---------------------------------------------------------------------------
# Extract solution
# ---------------------------------------------------------------------------
words = []
for j in range(n):
    word = ''.join(ALPHABET[solver.Value(char[j][k])] for k in range(L))
    words.append(word)

# ---------------------------------------------------------------------------
# Output as JSON -------------------------------------------------------------------------
print(json.dumps({"words": words}))