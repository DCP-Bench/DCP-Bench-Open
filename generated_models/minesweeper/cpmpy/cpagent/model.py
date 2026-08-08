import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Minesweeper constraint satisfaction problem:
# - Given a board with numbers and unknown cells (X)
# - Numbers indicate count of mines in adjacent cells (8-connected)
# - Determine which X cells contain mines

X = -1
game_data = [  # 0-8: number of mines around, -1: not opened
    [2, 3, X, 2, 2, X, 2, 1],
    [X, X, 4, X, X, 4, X, 2],
    [X, X, X, X, X, X, 4, X],
    [X, 5, X, 6, X, X, X, 2],
    [2, X, X, X, 5, 5, X, 2],
    [1, 3, 4, X, X, X, 4, X],
    [0, 1, X, 4, X, X, X, 3],
    [0, 1, 2, X, 2, 3, X, 2]
]

rows = len(game_data)
cols = len(game_data[0])

# Find all unknown cells (X) and known cells (numbers)
unknown_cells = []
known_cells = []

for i in range(rows):
    for j in range(cols):
        if game_data[i][j] == X:
            unknown_cells.append((i, j))
        else:
            known_cells.append((i, j, game_data[i][j]))

def get_neighbors(r, c):
    """Get all 8-connected neighbors of cell (r,c)"""
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbors.append((nr, nc))
    return neighbors

# Analyze constraints: for each known cell, identify its unknown neighbors
constraints_info = []
for i, j, value in known_cells:
    neighbors = get_neighbors(i, j)
    unknown_neighbors = [(r, c) for r, c in neighbors if game_data[r][c] == X]
    
    if unknown_neighbors:  # Only create constraint if there are unknown neighbors
        constraints_info.append({
            'cell': (i, j),
            'value': value,
            'unknown_neighbors': unknown_neighbors
        })

# Step 2: Model with CPMpy
# Create mapping from unknown cell position to variable index
unknown_to_idx = {cell: idx for idx, cell in enumerate(unknown_cells)}
n_unknowns = len(unknown_cells)

# Decision variables: mines[i] = 1 if unknown cell i contains a mine, 0 otherwise
mines = cp.boolvar(shape=n_unknowns, name="mines")

model = cp.Model()

# Add constraints: for each numbered cell, sum of mines in unknown neighbors = cell value
for constraint in constraints_info:
    required_mines = constraint['value']
    unknown_neighbors = constraint['unknown_neighbors']
    
    # Get variable indices for unknown neighbors
    neighbor_vars = [mines[unknown_to_idx[neighbor]] for neighbor in unknown_neighbors]
    # Sum of mines in unknown neighbors must equal the cell's number
    model += cp.sum(neighbor_vars) == required_mines

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    mine_values = mines.value()
    
    # Create the full board solution (0 = safe, 1 = mine)
    solution_board = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Fill in mine positions for unknown cells
    for idx, (r, c) in enumerate(unknown_cells):
        solution_board[r][c] = int(mine_values[idx])
    
    # Known cells (numbers) are safe (not mines)
    for i, j, value in known_cells:
        solution_board[i][j] = 0
    
    # Verification: check that all numbered cells have correct mine count in neighbors
    def verify_solution(board):
        for i, j, expected_count in known_cells:
            neighbors = get_neighbors(i, j)
            actual_mine_count = sum(1 for nr, nc in neighbors if board[nr][nc] == 1)
            if actual_mine_count != expected_count:
                return False
        return True
    
    assert verify_solution(solution_board), "Solution verification failed!"
    
    # Step 4: Output in required JSON format
    solution = {"mines": solution_board}
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))