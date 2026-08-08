import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: 31x31 grid, place coins such that:
# 1. Each row has exactly 14 coins
# 2. Each column has exactly 14 coins  
# 3. At most 1 coin per cell (implicit with boolvar)
# 4. Minimize sum of quadratic horizontal distance from main diagonal
# Quadratic horizontal distance for cell (i,j) = (j-i)^2

# Step 2: Model with CPMpy
n = 31
coins_per_row = 14
coins_per_col = 14

# Decision variables: x[i][j] = 1 if coin is placed at position (i,j)
x = cp.boolvar(shape=(n, n), name="x")

model = cp.Model()

# Constraint 1: Each row has exactly 14 coins
for i in range(n):
    model += cp.sum(x[i, :]) == coins_per_row

# Constraint 2: Each column has exactly 14 coins  
for j in range(n):
    model += cp.sum(x[:, j]) == coins_per_col

# Objective: minimize sum of quadratic horizontal distances from main diagonal
total_distance = 0
for i in range(n):
    for j in range(n):
        distance_squared = (j - i) ** 2
        total_distance += x[i, j] * distance_squared

# Step 3: Solve & Verify
model.minimize(total_distance)

if model.solve():
    # Extract solution
    x_solution = x.value()
    z_value = total_distance.value()
    
    # Convert to proper format (0/1 integers)
    x_list = [[int(x_solution[i, j]) for j in range(n)] for i in range(n)]
    
    # Verification
    def verify_solution(x_sol, z_val):
        """Independent verification of the solution"""
        n = len(x_sol)
        
        # Structural verification
        if n != 31 or len(x_sol[0]) != 31:
            return False, f"Wrong dimensions: {n}x{len(x_sol[0])}, expected 31x31"
        
        # Logical verification - row constraints
        for i in range(n):
            row_sum = sum(x_sol[i])
            if row_sum != 14:
                return False, f"Row {i} has {row_sum} coins, expected 14"
        
        # Logical verification - column constraints
        for j in range(n):
            col_sum = sum(x_sol[i][j] for i in range(n))
            if col_sum != 14:
                return False, f"Column {j} has {col_sum} coins, expected 14"
        
        # Verify objective calculation
        calculated_z = 0
        for i in range(n):
            for j in range(n):
                if x_sol[i][j] == 1:
                    calculated_z += (j - i) ** 2
        
        if calculated_z != z_val:
            return False, f"Objective mismatch: calculated {calculated_z}, reported {z_val}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(x_list, int(z_value))
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    solution = {
        "x": x_list,
        "z": int(z_value)
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))