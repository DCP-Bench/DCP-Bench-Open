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

# Import libraries
from cpmpy import *
import json

# Parameters
n_rows = rows
n_cols = cols

# Decision Variables
board = boolvar(shape=(n_rows, n_cols), name="board")

# Helper function to convert rules to actual block lengths
def get_blocks(rule):
    blocks = []
    if rule[0] != 0:
        blocks.append(rule[0])
    if rule[1] != 0:
        blocks.append(rule[1])
    return blocks

# Model
model = Model()

# Apply row constraints
for r in range(n_rows):
    blocks = get_blocks(row_rules[r])
    if len(blocks) > 0:
        model += [GlobalCardinality(board[r, :], [1] * sum(blocks) + [0] * (n_cols - sum(blocks)), counts=[sum(blocks), n_cols - sum(blocks)])]
        model += [ConsecutiveOnes(board[r, :], blocks)]

# Apply column constraints
for c in range(n_cols):
    blocks = get_blocks(col_rules[c])
    if len(blocks) > 0:
        model += [GlobalCardinality(board[:, c], [1] * sum(blocks) + [0] * (n_rows - sum(blocks)), counts=[sum(blocks), n_rows - sum(blocks)])]
        model += [ConsecutiveOnes(board[:, c], blocks)]

# Solve
model.solve()

# Print
solution = {"board": board.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script