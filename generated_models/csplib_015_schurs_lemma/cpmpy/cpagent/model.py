import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Schur's Lemma with n=13 balls and c=3 boxes
# 
# Constraints:
# 1. Each ball must be in exactly one box
# 2. For any triple (x, y, z) where x + y = z, not all three can be in the same box

n = 13  # Number of balls
c = 3   # Number of boxes

# Find all triples (x, y, z) where x + y = z
triples = []
for x in range(1, n + 1):
    for y in range(x, n + 1):  # y >= x to avoid duplicates
        z = x + y
        if z <= n:
            triples.append((x, y, z))

# Step 2: Model with CPMpy
# Decision variables: M[i,j] = 1 if ball i is in box j
# Using 0-based indexing internally, will convert to 1-based for output
M = cp.boolvar(shape=(n, c), name="M")

model = cp.Model()

# Constraint 1: Each ball must be in exactly one box
for i in range(n):
    model += cp.sum(M[i, :]) == 1

# Constraint 2: For each triple (x, y, z) where x + y = z,
# not all three can be in the same box
# This means: M[x,j] + M[y,j] + M[z,j] <= 2 for each box j
for x, y, z in triples:
    # Convert to 0-based indexing
    x_idx, y_idx, z_idx = x - 1, y - 1, z - 1
    for j in range(c):
        model += M[x_idx, j] + M[y_idx, j] + M[z_idx, j] <= 2

# Step 3: Solve & Verify
if model.solve():
    # Extract the solution - convert to 1-based box numbering
    assignment = []
    for i in range(n):
        for j in range(c):
            if M[i, j].value() == 1:
                assignment.append(j + 1)  # Convert to 1-based
                break
    
    # Create solution in required format
    solution = {"balls": assignment}
    
    # Verification - independent check
    def verify_solution(sol):
        balls = sol["balls"]
        
        # 1. Structural verification
        if len(balls) != n:
            return False, f"Wrong number of balls: {len(balls)}, expected {n}"
        
        if not all(1 <= b <= c for b in balls):
            return False, f"Invalid box numbers: {balls}, must be 1-{c}"
        
        # 2. Logical verification - check Schur constraint
        for x, y, z in triples:
            box_x = balls[x - 1]  # Convert to 0-based indexing
            box_y = balls[y - 1]
            box_z = balls[z - 1]
            
            if box_x == box_y == box_z:
                return False, f"Schur constraint violated: balls {x}, {y}, {z} all in box {box_x}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))