
import cpmpy as cp
import json

# Data (optional)
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

# Model definition
model = cp.Model()

# Decision Variables
board = cp.boolvar(shape=(rows, cols), name="board")

# Helper to parse rules: filter out zeros (placeholders)
def parse_rule(rule):
    return [r for r in rule if r > 0]

# Row constraints
for i in range(rows):
    lengths = parse_rule(row_rules[i])
    k = len(lengths)
    if k == 0:
        # No blocks: all zeros in the row
        model += (cp.sum(board[i, :]) == 0)
    else:
        # Start variables for each block in the row
        # Each start s_j is in [0, cols - lengths[j]]
        s = [cp.intvar(0, cols - L) for L in lengths]

        # Order and separation: next block starts at least 1 after previous ends
        for j in range(k - 1):
            model += (s[j + 1] >= s[j] + lengths[j] + 1)

        # Bounds (redundant due to domains, but explicit for clarity)
        for j in range(k):
            model += (s[j] >= 0)
            model += (s[j] + lengths[j] <= cols)

        # Occupancy: board[i,c] is 1 iff c is covered by one of the blocks
        for c in range(cols):
            covers = [(s[j] <= c) & (c < s[j] + lengths[j]) for j in range(k)]
            model += (board[i, c] == cp.any(covers))

        # Redundant but helpful: total number of shaded cells equals sum of lengths
        model += (cp.sum(board[i, :]) == sum(lengths))

# Column constraints
for j in range(cols):
    lengths = parse_rule(col_rules[j])
    k = len(lengths)
    if k == 0:
        # No blocks: all zeros in the column
        model += (cp.sum(board[:, j]) == 0)
    else:
        # Start variables for each block in the column
        # Each start t_j is in [0, rows - lengths[j]]
        t = [cp.intvar(0, rows - L) for L in lengths]

        # Order and separation: next block starts at least 1 after previous ends
        for r in range(k - 1):
            model += (t[r + 1] >= t[r] + lengths[r] + 1)

        # Bounds (explicit)
        for r in range(k):
            model += (t[r] >= 0)
            model += (t[r] + lengths[r] <= rows)

        # Occupancy: board[r,j] is 1 iff r is covered by one of the blocks
        for r in range(rows):
            covers = [(t[m] <= r) & (r < t[m] + lengths[m]) for m in range(k)]
            model += (board[r, j] == cp.any(covers))

        # Redundant but helpful: total number of shaded cells equals sum of lengths
        model += (cp.sum(board[:, j]) == sum(lengths))

# Objective (optional)
# Nonograms are feasibility problems; no objective required.

# Solve and print
if model.solve():
    # Convert boolean matrix to list of lists of ints (0/1)
    board_list = [[int(v) for v in row] for row in board.value().tolist()]
    solution = {'board': board_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
