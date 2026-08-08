import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# This is a classic Sudoku problem with the following constraints:
# 1. Each row must contain digits 1-9 exactly once
# 2. Each column must contain digits 1-9 exactly once  
# 3. Each 3x3 box must contain digits 1-9 exactly once
# 4. Pre-filled cells must retain their values

# Input data
input_grid = [
    [0, 0, 0,  2, 0, 5,  0, 0, 0],
    [0, 9, 0,  0, 0, 0,  7, 3, 0],
    [0, 0, 2,  0, 0, 9,  0, 6, 0],
    
    [2, 0, 0,  0, 0, 0,  4, 0, 9],
    [0, 0, 0,  0, 7, 0,  0, 0, 0],
    [6, 0, 9,  0, 0, 0,  0, 0, 1],
    
    [0, 8, 0,  4, 0, 0,  1, 0, 0],
    [0, 6, 3,  0, 0, 0,  0, 8, 0],
    [0, 0, 0,  6, 0, 8,  0, 0, 0]
]

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: 9x9 grid with values 1-9
grid = cp.intvar(1, 9, shape=(9, 9), name="grid")

# Constraint 1: Each row contains all digits 1-9 (AllDifferent)
for i in range(9):
    model += cp.AllDifferent(grid[i, :])

# Constraint 2: Each column contains all digits 1-9 (AllDifferent)
for j in range(9):
    model += cp.AllDifferent(grid[:, j])

# Constraint 3: Each 3x3 box contains all digits 1-9 (AllDifferent)
for box_row in range(3):
    for box_col in range(3):
        # Extract the 3x3 box
        box = []
        for i in range(3):
            for j in range(3):
                row = box_row * 3 + i
                col = box_col * 3 + j
                box.append(grid[row, col])
        model += cp.AllDifferent(box)

# Constraint 4: Pre-filled cells must retain their values
for i in range(9):
    for j in range(9):
        if input_grid[i][j] != 0:
            model += grid[i, j] == input_grid[i][j]

# Step 3: Solve & Verify
# This is a satisfaction problem (any valid solution is acceptable)
if model.solve():
    # Extract the solution
    solution_grid = grid.value().tolist()
    
    # Verification - Independent verification of the solution
    def verify_sudoku_solution(sol_grid):
        """Verify that the solution satisfies all Sudoku constraints"""
        
        # 1. Structural Verification
        if len(sol_grid) != 9:
            return False, f"Grid has {len(sol_grid)} rows, expected 9"
        for i, row in enumerate(sol_grid):
            if len(row) != 9:
                return False, f"Row {i} has {len(row)} columns, expected 9"
            for j, val in enumerate(row):
                if not (1 <= val <= 9):
                    return False, f"Cell ({i},{j}) has value {val}, expected 1-9"
        
        # 2. Logical Verification
        # Check rows
        for i, row in enumerate(sol_grid):
            if len(set(row)) != 9 or set(row) != set(range(1, 10)):
                return False, f"Row {i} doesn't contain all digits 1-9: {row}"
        
        # Check columns
        for j in range(9):
            col = [sol_grid[i][j] for i in range(9)]
            if len(set(col)) != 9 or set(col) != set(range(1, 10)):
                return False, f"Column {j} doesn't contain all digits 1-9: {col}"
        
        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        box.append(sol_grid[row][col])
                if len(set(box)) != 9 or set(box) != set(range(1, 10)):
                    return False, f"Box ({box_row},{box_col}) doesn't contain all digits 1-9: {box}"
        
        # Check pre-filled cells are preserved
        for i in range(9):
            for j in range(9):
                if input_grid[i][j] != 0:
                    if sol_grid[i][j] != input_grid[i][j]:
                        return False, f"Pre-filled cell ({i},{j}) changed from {input_grid[i][j]} to {sol_grid[i][j]}"
        
        return True, "All constraints satisfied"
    
    # Verify the solution
    valid, msg = verify_sudoku_solution(solution_grid)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output in required JSON format
    solution = {"grid": solution_grid}
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))