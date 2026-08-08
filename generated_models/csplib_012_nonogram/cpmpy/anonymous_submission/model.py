# Import libraries
from cpmpy import *
import json

# Parameters
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

# Decision Variables
board = boolvar(shape=(rows, cols), name="board")  # Solution board (True = shaded)

# Model
model = Model()

# Helper function to implement nonogram constraints for a sequence
def nonogram_sequence(sequence, rules):
    # Filter out zeros from rules
    blocks = [r for r in rules if r > 0]
    if not blocks:
        # If no blocks, all cells must be unshaded
        return [sequence[i] == False for i in range(len(sequence))]
    
    # Calculate minimum required length
    min_len = sum(blocks) + len(blocks) - 1
    if min_len > len(sequence):
        return []  # Impossible to satisfy
    
    # Create constraints for the sequence pattern
    constraints = []
    n = len(sequence)
    m = len(blocks)
    
    # Variables for block starts and ends
    starts = intvar(0, n-1, shape=m, name="starts")
    ends = intvar(0, n-1, shape=m, name="ends")
    
    # Block lengths
    for i in range(m):
        constraints += (ends[i] - starts[i] + 1 == blocks[i])
    
    # Blocks are ordered
    for i in range(m-1):
        constraints += (ends[i] + 1 < starts[i+1])
    
    # All cells before first block are unshaded
    constraints += [sequence[i] == False for i in range(starts[0])]
    
    # All cells after last block are unshaded
    constraints += [sequence[i] == False for i in range(ends[-1]+1, n)]
    
    # All cells between blocks are unshaded
    for i in range(m-1):
        constraints += [sequence[j] == False for j in range(ends[i]+1, starts[i+1])]
    
    # All cells in blocks are shaded
    for i in range(m):
        constraints += [sequence[j] == True for j in range(starts[i], ends[i]+1)]
    
    return constraints

# Apply row constraints
for r in range(rows):
    model += nonogram_sequence(board[r], row_rules[r])

# Apply column constraints
for c in range(cols):
    model += nonogram_sequence(board[:, c], col_rules[c])

# Solve
model.solve()

# Print solution
solution = {"board": board.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script