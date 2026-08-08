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

# Model definition
model = cp_model.CpModel()

# Decision Variables
# board[r][c] = 1 if cell (r,c) is shaded, 0 otherwise
board = []
for r in range(rows):
    row_vars = [model.NewBoolVar(f'board_{r}_{c}') for c in range(cols)]
    board.append(row_vars)

# Helper function to enforce block constraints on a line (row or column)
def add_line_constraints(line_vars, rules):
    """
    line_vars: list of BoolVar for the line (row or column)
    rules: list of block lengths (integers)
    """
    length = len(line_vars)
    # Filter out zero-length blocks (0 means no block)
    blocks = [b for b in rules if b > 0]
    num_blocks = len(blocks)

    # If no blocks, all cells must be 0
    if num_blocks == 0:
        for v in line_vars:
            model.Add(v == 0)
        return

    # We create start position variables for each block
    # start[i] is the start index of block i in the line
    # start[i] in [0, length - blocks[i]]
    starts = []
    for i, b in enumerate(blocks):
        start_var = model.NewIntVar(0, length - b, f'start_{i}')
        starts.append(start_var)

    # Blocks must be in order and non-overlapping with at least one gap between blocks
    for i in range(num_blocks - 1):
        model.Add(starts[i] + blocks[i] < starts[i + 1])

    # For each cell, determine if it is covered by any block
    # We create auxiliary variables for each cell and block to indicate coverage
    coverage = []
    for i in range(num_blocks):
        b = blocks[i]
        cov = []
        for pos in range(length):
            # cell_covered = 1 if pos in [start[i], start[i]+b-1], else 0
            in_block = model.NewBoolVar(f'cov_b{i}_pos{pos}')
            # in_block <=> (starts[i] <= pos <= starts[i] + b - 1)
            model.Add(starts[i] <= pos).OnlyEnforceIf(in_block)
            model.Add(starts[i] > pos).OnlyEnforceIf(in_block.Not())
            model.Add(starts[i] + b - 1 >= pos).OnlyEnforceIf(in_block)
            model.Add(starts[i] + b - 1 < pos).OnlyEnforceIf(in_block.Not())
            cov.append(in_block)
        coverage.append(cov)

    # For each cell, sum coverage over blocks <= 1 (no overlapping blocks)
    for pos in range(length):
        model.Add(sum(coverage[i][pos] for i in range(num_blocks)) <= 1)

    # For each cell, board cell must be 1 if covered by any block, else 0
    for pos in range(length):
        # sum coverage[i][pos] over i is 1 if cell is shaded, else 0
        # line_vars[pos] == OR over coverage[i][pos]
        # We enforce line_vars[pos] == max coverage[i][pos]
        # Since coverage[i][pos] are bools, sum is 0 or 1
        model.Add(line_vars[pos] == sum(coverage[i][pos] for i in range(num_blocks)))

# Add constraints for rows
for r in range(rows):
    add_line_constraints(board[r], row_rules[r])

# Add constraints for columns
for c in range(cols):
    col_vars = [board[r][c] for r in range(rows)]
    add_line_constraints(col_vars, col_rules[c])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution_board = []
    for r in range(rows):
        solution_board.append([solver.Value(board[r][c]) for c in range(cols)])
    solution = {'board': solution_board}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")