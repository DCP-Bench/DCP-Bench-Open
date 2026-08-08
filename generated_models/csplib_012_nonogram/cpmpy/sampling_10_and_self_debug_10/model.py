
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
# board[r, c] = 1 if cell (r,c) is shaded, else 0
board = cp.intvar(0, 1, shape=(rows, cols), name="board")

# Helper function to extract blocks from a line of variables (boolean/int 0/1)
# We'll model the blocks positions for each row and column to enforce the run lengths

# For each row, define the starting positions of the blocks
# There are row_rule_len blocks per row (some may be zero length, or zero meaning no block)
# Each block start variable is in [0..cols-1]
row_starts = cp.intvar(0, cols-1, shape=(rows, row_rule_len), name="row_starts")
# block lengths are given by row_rules, constants (but some may be zero)
row_blocklens = row_rules

# For each column, define the starting positions of the blocks
col_starts = cp.intvar(0, rows-1, shape=(cols, col_rule_len), name="col_starts")
col_blocklens = col_rules

# Constraints

# 1) Blocks for rows: For each row and each block, if block length > 0,
# then the block is a consecutive segment of shaded squares of that length,
# starting at row_starts[r,b].

for r in range(rows):
    for b in range(row_rule_len):
        blen = row_blocklens[r][b]
        # If block length is zero, then no block: so start is irrelevant, but let's force start to 0
        if blen == 0:
            model += (row_starts[r, b] == 0)
        else:
            # block start + block length <= cols
            model += (row_starts[r, b] + blen <= cols)
            # The block cells must be shaded
            for i in range(blen):
                model += (board[r, row_starts[r, b] + i] == 1)

# Blocks do not overlap and are strictly increasing start positions
# For each row, block starts must be strictly increasing and separated by at least 1 cell
# between the end of previous block and start of next block
for r in range(rows):
    for b in range(row_rule_len - 1):
        blen_curr = row_blocklens[r][b]
        blen_next = row_blocklens[r][b+1]
        if blen_curr == 0 and blen_next == 0:
            # both zero blocks, starts are zero, no constraint needed
            continue
        elif blen_curr == 0:
            # current block zero length, so starts[r,b] == 0
            # next block start >= 0, no special constraint needed, but enforce strictly increasing
            model += (row_starts[r, b+1] >= 0)
        elif blen_next == 0:
            # next block zero length, starts[r,b+1] == 0
            # current block start plus length <= cols
            # no further constraint needed
            pass
        else:
            # start of next block must be at least after current block end + 1
            model += (row_starts[r, b] + blen_curr < row_starts[r, b+1])

# Any cells outside the blocks in each row must be zero (unshaded)
# For each cell in row r, it must be covered by exactly one block or be zero
for r in range(rows):
    for c in range(cols):
        # create boolvar whether cell (r,c) is in any block in row r
        in_block_vars = []
        for b in range(row_rule_len):
            blen = row_blocklens[r][b]
            if blen == 0:
                # no block
                continue
            # cell c is in block b if c in [row_starts[r,b], row_starts[r,b]+blen-1]
            # model as boolean indicator variables
            in_block = cp.boolvar()
            model += (in_block == ((c >= row_starts[r, b]) & (c < row_starts[r, b] + blen)))
            in_block_vars.append(in_block)
        # If the cell is shaded then it must be inside one of the blocks:
        # board[r,c] == 1 => sum(in_block_vars) == 1
        # Also, if sum(in_block_vars) == 1 then board[r,c] == 1
        # So board[r,c] == sum(in_block_vars)
        if len(in_block_vars) > 0:
            model += (board[r, c] == cp.sum(in_block_vars))
        else:
            # no blocks in this row, so all cells must be zero
            model += (board[r, c] == 0)

# Similar constraints for columns

# For each column, blocks given by col_rules, starting at col_starts[c,b]

for c in range(cols):
    for b in range(col_rule_len):
        blen = col_blocklens[c][b]
        if blen == 0:
            model += (col_starts[c, b] == 0)
        else:
            model += (col_starts[c, b] + blen <= rows)
            for i in range(blen):
                model += (board[col_starts[c, b] + i, c] == 1)

# Blocks do not overlap and start strictly increasing for columns
for c in range(cols):
    for b in range(col_rule_len - 1):
        blen_curr = col_blocklens[c][b]
        blen_next = col_blocklens[c][b+1]
        if blen_curr == 0 and blen_next == 0:
            continue
        elif blen_curr == 0:
            model += (col_starts[c, b+1] >= 0)
        elif blen_next == 0:
            pass
        else:
            model += (col_starts[c, b] + blen_curr < col_starts[c, b+1])

# Cells outside column blocks must be zero (unshaded)
for c in range(cols):
    for r in range(rows):
        in_block_vars = []
        for b in range(col_rule_len):
            blen = col_blocklens[c][b]
            if blen == 0:
                continue
            in_block = cp.boolvar()
            model += (in_block == ((r >= col_starts[c, b]) & (r < col_starts[c, b] + blen)))
            in_block_vars.append(in_block)
        if len(in_block_vars) > 0:
            # board[r,c] == sum of in_block_vars (should be 0 or 1)
            model += (board[r, c] == cp.sum(in_block_vars))
        else:
            model += (board[r, c] == 0)

# Solve and print
if model.solve():
    solution = {'board': board.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
