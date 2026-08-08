import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Perfect Square Placement - pack squares into a larger square without overlap
# Constraints:
# 1. All squares must fit within the large square boundaries
# 2. No two squares can overlap
# 3. All squares must be placed (perfect packing)

# Input data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n = len(sides)

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: bottom-left coordinates of each square
x_coords = cp.intvar(0, base-1, shape=n, name="x_coords")
y_coords = cp.intvar(0, base-1, shape=n, name="y_coords")

# Constraint 1: Boundary constraints - squares must fit within the large square
for i in range(n):
    model += x_coords[i] + sides[i] <= base  # Right edge within bounds
    model += y_coords[i] + sides[i] <= base  # Top edge within bounds

# Constraint 2: Non-overlap constraints
from itertools import combinations
for i, j in combinations(range(n), 2):
    # Two squares don't overlap if one of these conditions is true:
    model += (
        (x_coords[i] + sides[i] <= x_coords[j]) |  # i left of j
        (x_coords[j] + sides[j] <= x_coords[i]) |  # j left of i
        (y_coords[i] + sides[i] <= y_coords[j]) |  # i below j
        (y_coords[j] + sides[j] <= y_coords[i])    # j below i
    )

# Performance constraints: Symmetry breaking for identical squares
# Order the three size-3 squares by x-coordinate
model += x_coords[0] <= x_coords[1]
model += x_coords[1] <= x_coords[2]

# Order the five size-1 squares by x-coordinate (indices 4-8)
for i in range(4, 8):
    model += x_coords[i] <= x_coords[i+1]

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    x_solution = x_coords.value().tolist()
    y_solution = y_coords.value().tolist()
    
    # Verification (independent of CPMpy)
    def verify_solution(x_coords, y_coords, sides, base):
        n = len(sides)
        
        # Check boundaries
        for i in range(n):
            if x_coords[i] < 0 or y_coords[i] < 0:
                return False
            if x_coords[i] + sides[i] > base or y_coords[i] + sides[i] > base:
                return False
        
        # Check non-overlap
        for i in range(n):
            for j in range(i+1, n):
                left_of = x_coords[i] + sides[i] <= x_coords[j]
                right_of = x_coords[j] + sides[j] <= x_coords[i]
                below = y_coords[i] + sides[i] <= y_coords[j]
                above = y_coords[j] + sides[j] <= y_coords[i]
                
                if not (left_of or right_of or below or above):
                    return False
        
        # Check perfect packing
        grid = [[False for _ in range(base)] for _ in range(base)]
        for i in range(n):
            for dx in range(sides[i]):
                for dy in range(sides[i]):
                    x, y = x_coords[i] + dx, y_coords[i] + dy
                    if grid[y][x]:
                        return False
                    grid[y][x] = True
        
        return True
    
    assert verify_solution(x_solution, y_solution, sides, base), "Solution verification failed!"
    
    # Step 4: Output in required JSON format
    solution = {
        "x_coords": x_solution,
        "y_coords": y_solution
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))