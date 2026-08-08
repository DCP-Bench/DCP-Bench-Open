
from ortools.sat.python import cp_model
import json

# Input data
rows = 8  # Number of rows
row_rule_len = 2  # Maximum length of row rules
row_rules = [
    [0, 1],
    [0, 2],
    [4, 4],
    [0, 12],
    [0, 8],
    [0, 9],
    [3, 4],
    [2, 2]
]
cols = 13  # Number of columns
col_rule_len = 2  # Maximum length of column rules
col_rules = [
    [0, 2],
    [2, 1],
    [3, 2],
    [0, 6],
    [1, 4],
    [0, 3],
    [0, 4],
    [0, 4],
    [0, 4],
    [0, 5],
    [0, 4],
    [1, 3],
    [0, 2]
]

# Helper to generate all binary patterns of length n satisfying given blocks
def generate_patterns(n, blocks):
    patterns = []
    def helper(prefix, rem_blocks):
        if not rem_blocks:
            # fill remaining with zeros
            suffix = [0] * (n - len(prefix))
            patterns.append(prefix + suffix)
            return
        L = rem_blocks[0]
        # minimal length needed for all remaining blocks including gaps
        min_rest = sum(rem_blocks) + len(rem_blocks) - 1
        # how many zeros we can still put before this block
        max_zeros = n - len(prefix) - min_rest
        for z in range(max_zeros + 1):
            new_pref = prefix + [0] * z + [1] * L
            # if more blocks follow, add one zero as separator
            if len(rem_blocks) > 1:
                new_pref = new_pref + [0]
            helper(new_pref, rem_blocks[1:])
    helper([], blocks)
    # filter exactly length n
    return [p for p in patterns if len(p) == n]

# Precompute row and column patterns
row_patterns = []
for r in range(rows):
    blks = [x for x in row_rules[r] if x > 0]
    row_patterns.append(generate_patterns(cols, blks))

col_patterns = []
for c in range(cols):
    blks = [x for x in col_rules[c] if x > 0]
    col_patterns.append(generate_patterns(rows, blks))

# Model definition
model = cp_model.CpModel()

# Decision variables
# board[i][j] = 1 if cell (i,j) is filled
board = [
    [model.NewBoolVar(f"b_{i}_{j}") for j in range(cols)]
    for i in range(rows)
]

# For each row, choose exactly one pattern
row_choice = []
for i in range(rows):
    pcs = []
    for p in range(len(row_patterns[i])):
        pcs.append(model.NewBoolVar(f"r_{i}_{p}"))
    model.Add(sum(pcs) == 1)
    row_choice.append(pcs)

# For each column, choose exactly one pattern
col_choice = []
for j in range(cols):
    pcs = []
    for p in range(len(col_patterns[j])):
        pcs.append(model.NewBoolVar(f"c_{j}_{p}"))
    model.Add(sum(pcs) == 1)
    col_choice.append(pcs)

# Link row patterns to board
for i in range(rows):
    for j in range(cols):
        # sum of chosen row patterns that have a 1 at position j equals board[i][j]
        model.Add(
            sum(row_patterns[i][p][j] * row_choice[i][p] for p in range(len(row_patterns[i])))
            == board[i][j]
        )

# Link column patterns to board
for j in range(cols):
    for i in range(rows):
        model.Add(
            sum(col_patterns[j][p][i] * col_choice[j][p] for p in range(len(col_patterns[j])))
            == board[i][j]
        )

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'board': [
            [int(solver.Value(board[i][j])) for j in range(cols)]
            for i in range(rows)
        ]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
