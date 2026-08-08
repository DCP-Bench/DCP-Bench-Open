
import cpmpy as cp
import json

# Data
rows = 8
row_rule_len = 2
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
cols = 13
col_rule_len = 2
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

# Model definition
model = cp.Model()

# Decision Variables
# board[r,c] = 1 if cell is shaded, 0 otherwise
board = cp.intvar(0, 1, shape=(rows, cols), name="board")

# Helper function to get the runs of shaded cells in a line (row or column)
# We model the start positions of each block in the line.
# For each line, we have row_rule_len blocks (some may be zero length).
# We create variables for the start positions of each block.
# Constraints:
# - Blocks must be placed in order, non-overlapping, with at least one gap between blocks.
# - Blocks of length 0 mean no block, so start position is irrelevant but we fix it to 0.
# - The sum of block lengths + minimum gaps must fit in the line length.
# - The board cells must match the blocks.

# We will create start position variables for each block in each row and column.
# For zero-length blocks, start position is fixed to 0.

# Row block start positions
row_starts = cp.intvar(0, cols - 1, shape=(rows, row_rule_len), name="row_starts")
# Column block start positions
col_starts = cp.intvar(0, rows - 1, shape=(cols, col_rule_len), name="col_starts")

# Constraints for rows
for r in range(rows):
    blocks = row_rules[r]
    # For zero-length blocks, fix start to 0
    for b in range(row_rule_len):
        if blocks[b] == 0:
            model += (row_starts[r, b] == 0)
        else:
            # start must be in range so that block fits in row
            model += (row_starts[r, b] >= 0)
            model += (row_starts[r, b] + blocks[b] <= cols)
    # Blocks must be in ascending order with at least one gap between non-zero blocks
    for b in range(row_rule_len - 1):
        if blocks[b] == 0 or blocks[b+1] == 0:
            # If either block is zero length, no ordering needed
            # But to avoid overlap, we can just allow any order
            # Actually, zero length blocks do not occupy space, so no constraint needed
            pass
        else:
            # start of next block > end of current block
            model += (row_starts[r, b] + blocks[b] < row_starts[r, b+1])
    # Now enforce the board cells for this row to match the blocks
    # For each cell in the row, it is shaded if it belongs to any block
    for c in range(cols):
        # cell_shaded = OR over blocks of (start <= c < start+length)
        # We create boolean variables for each block indicating if cell c is in that block
        in_block_bools = []
        for b in range(row_rule_len):
            if blocks[b] == 0:
                # no block, so cell cannot be in it
                in_block_bools.append(cp.intvar(0,0))
            else:
                # boolean variable: 1 if c in block b, else 0
                in_block = cp.boolvar()
                model += (in_block == ((row_starts[r, b] <= c) & (c < row_starts[r, b] + blocks[b])))
                in_block_bools.append(in_block)
        # cell shaded if any in_block_bools is true
        model += (board[r, c] == cp.max(in_block_bools))

# Constraints for columns
for c in range(cols):
    blocks = col_rules[c]
    # For zero-length blocks, fix start to 0
    for b in range(col_rule_len):
        if blocks[b] == 0:
            model += (col_starts[c, b] == 0)
        else:
            model += (col_starts[c, b] >= 0)
            model += (col_starts[c, b] + blocks[b] <= rows)
    # Blocks must be in ascending order with at least one gap between non-zero blocks
    for b in range(col_rule_len - 1):
        if blocks[b] == 0 or blocks[b+1] == 0:
            pass
        else:
            model += (col_starts[c, b] + blocks[b] < col_starts[c, b+1])
    # Enforce board cells for this column to match the blocks
    for r in range(rows):
        in_block_bools = []
        for b in range(col_rule_len):
            if blocks[b] == 0:
                in_block_bools.append(cp.intvar(0,0))
            else:
                in_block = cp.boolvar()
                model += (in_block == ((col_starts[c, b] <= r) & (r < col_starts[c, b] + blocks[b])))
                in_block_bools.append(in_block)
        model += (board[r, c] == cp.max(in_block_bools))

# Solve and print
if model.solve():
    solution = {'board': board.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
