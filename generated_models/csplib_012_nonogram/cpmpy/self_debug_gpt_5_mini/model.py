
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
]  # Rules for rows
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
]  # Rules for columns
# End of data

# Parse rules: remove zeros that are placeholders
row_blocks = [[l for l in rule if l > 0] for rule in row_rules]
col_blocks = [[l for l in rule if l > 0] for rule in col_rules]

# Model definition
model = cp.Model()

# Decision Variables
# Board: rows x cols binary (0/1)
board = cp.intvar(0, 1, shape=(rows, cols), name="board")

# Row block start variables and helper booleans
row_starts = []  # list of lists of start vars per row
for i in range(rows):
    lengths = row_blocks[i]
    starts_i = []
    for j, lj in enumerate(lengths):
        # start must be in 0..cols-lj
        s = cp.intvar(0, cols - lj, name=f"r{i}_s{j}")
        starts_i.append(s)
    row_starts.append(starts_i)
    # ordering between blocks in the same row
    for j in range(len(starts_i) - 1):
        model += (starts_i[j+1] >= starts_i[j] + lengths[j] + 1)

# Column block start variables and helper booleans
col_starts = []
for j in range(cols):
    lengths = col_blocks[j]
    starts_j = []
    for k, lk in enumerate(lengths):
        s = cp.intvar(0, rows - lk, name=f"c{j}_s{k}")
        starts_j.append(s)
    col_starts.append(starts_j)
    for k in range(len(starts_j) - 1):
        model += (starts_j[k+1] >= starts_j[k] + lengths[k] + 1)

# Link board with row blocks
for i in range(rows):
    lengths = row_blocks[i]
    starts_i = row_starts[i]
    if len(lengths) == 0:
        # no blocks in this row -> all zeros
        for c in range(cols):
            model += (board[i, c] == 0)
    else:
        # For each block j and column c create boolean indicating whether cell is covered by that block
        for c in range(cols):
            cover_bools = []
            for j, lj in enumerate(lengths):
                y = cp.boolvar(name=f"r{i}_b{j}_c{c}")
                # y iff starts_i[j] <= c <= starts_i[j] + lj - 1
                model += (y == ((starts_i[j] <= c) & (c <= starts_i[j] + lj - 1)))
                cover_bools.append(y)
            # sum of covers (0 or 1) equals board cell
            model += (cp.sum(cover_bools) == board[i, c])

# Link board with column blocks
for j in range(cols):
    lengths = col_blocks[j]
    starts_j = col_starts[j]
    if len(lengths) == 0:
        # no blocks in this column -> all zeros
        for r in range(rows):
            model += (board[r, j] == 0)
    else:
        for r in range(rows):
            cover_bools = []
            for k, lk in enumerate(lengths):
                z = cp.boolvar(name=f"c{j}_b{k}_r{r}")
                # z iff starts_j[k] <= r <= starts_j[k] + lk - 1
                model += (z == ((starts_j[k] <= r) & (r <= starts_j[k] + lk - 1)))
                cover_bools.append(z)
            # sum of covers equals board cell (ensures consistency with rows)
            model += (cp.sum(cover_bools) == board[r, j])

# Solve and print
if model.solve():
    solution = {'board': board.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
