
import cpmpy as cp
import json

# Data
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
# End of data

# Utility to generate all 0/1 patterns of length N matching run-lengths 'lens'
def generate_patterns(N, lens):
    patterns = []
    k = len(lens)
    # minimal required length from block i onward = sum of lens[i:] + (remaining blocks -1) for mandatory gaps
    min_req_suffix = [0]* (k+1)
    for i in range(k-1, -1, -1):
        # lens[i] plus one gap after if not last block
        min_req_suffix[i] = min_req_suffix[i+1] + lens[i] + (1 if i < k-1 else 0)
    def helper(curr, block_idx):
        if block_idx == k:
            # fill remaining zeros
            if len(curr) < N:
                curr = curr + [0]*(N - len(curr))
            patterns.append(curr)
            return
        # next block of length lens[block_idx]
        start_min = len(curr)
        start_max = N - min_req_suffix[block_idx]
        for s in range(start_min, start_max+1):
            # place zeros to reach s
            new_curr = curr + [0]*(s - len(curr))
            # place block of ones
            new_curr = new_curr + [1]*lens[block_idx]
            # if not the last block, place a zero gap
            if block_idx < k-1:
                new_curr = new_curr + [0]
            helper(new_curr, block_idx+1)
    # Special case: no blocks
    if k == 0:
        patterns.append([0]*N)
    else:
        helper([], 0)
    return patterns

# Prepare row and column patterns
row_patterns = []
for i in range(rows):
    lens = [x for x in row_rules[i] if x > 0]
    row_patterns.append(generate_patterns(cols, lens))

col_patterns = []
for j in range(cols):
    lens = [x for x in col_rules[j] if x > 0]
    col_patterns.append(generate_patterns(rows, lens))

# Model definition
model = cp.Model()

# Decision variables
# Board: 1=shaded, 0=empty
B = cp.intvar(0, 1, shape=(rows, cols), name="B")

# Row selection variables
sel_row = []
for i in range(rows):
    n_pat = len(row_patterns[i])
    sel = cp.boolvar(shape=n_pat, name=f"sr{i}")
    sel_row.append(sel)
    # exactly one pattern per row
    model += cp.sum(sel) == 1

# Column selection variables
sel_col = []
for j in range(cols):
    n_pat = len(col_patterns[j])
    sel = cp.boolvar(shape=n_pat, name=f"sc{j}")
    sel_col.append(sel)
    # exactly one pattern per column
    model += cp.sum(sel) == 1

# Link board with row patterns
for i in range(rows):
    for j in range(cols):
        # sum over row patterns choosing 1 if pattern has a 1 at position j
        row_expr = cp.sum([sel_row[i][p] * row_patterns[i][p][j]
                           for p in range(len(row_patterns[i]))])
        model += (B[i, j] == row_expr)

# Link board with column patterns
for i in range(rows):
    for j in range(cols):
        col_expr = cp.sum([sel_col[j][q] * col_patterns[j][q][i]
                           for q in range(len(col_patterns[j]))])
        model += (B[i, j] == col_expr)

# Solve and print
if model.solve():
    board = B.value().tolist()
    solution = {'board': board}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
