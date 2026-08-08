import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: 4x4 Magic Square
# Constraints:
# 1. Each cell contains a different integer from 1 to 16
# 2. Sum of each row = 34
# 3. Sum of each column = 34  
# 4. Sum of each diagonal = 34
# 5. All numbers 1-16 used exactly once

n = 4
magic_sum = n * (n**2 + 1) // 2  # = 4 * (16 + 1) / 2 = 34

# Step 2: Model with CPMpy
# Decision variables: 4x4 grid with values 1-16
square = cp.intvar(1, n**2, shape=(n, n), name="square")

model = cp.Model()

# Constraint 1: All different values (each number 1-16 used exactly once)
model += cp.AllDifferent(square.flat)

# Constraint 2: Row sums equal magic_sum
for i in range(n):
    model += cp.sum(square[i, :]) == magic_sum

# Constraint 3: Column sums equal magic_sum  
for j in range(n):
    model += cp.sum(square[:, j]) == magic_sum

# Constraint 4: Diagonal sums equal magic_sum
# Main diagonal (top-left to bottom-right)
model += cp.sum([square[i, i] for i in range(n)]) == magic_sum

# Anti-diagonal (top-right to bottom-left)
model += cp.sum([square[i, n-1-i] for i in range(n)]) == magic_sum

# Performance improvements: Symmetry breaking
# Fix the top-left corner to reduce search space
model += square[0, 0] == 1

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    solution_matrix = square.value()
    
    # Create JSON output
    solution = {
        "square": solution_matrix.tolist()
    }
    
    # Verification (independent of CPMpy)
    def verify_magic_square(square_data):
        """Verify that the solution is a valid 4x4 magic square"""
        square_matrix = np.array(square_data["square"])
        n = 4
        expected_magic_sum = 34
        
        # 1. Structural Verification
        if square_matrix.shape != (n, n):
            return False, f"Wrong shape: {square_matrix.shape}, expected {(n, n)}"
        
        # 2. Logical Verification
        
        # Check all values are in range 1-16
        flat_values = square_matrix.flatten()
        if not all(1 <= val <= 16 for val in flat_values):
            return False, "Values outside range 1-16"
        
        # Check all values are different (no duplicates)
        if len(set(flat_values)) != 16:
            return False, "Duplicate values found"
        
        # Check all values 1-16 are present
        if set(flat_values) != set(range(1, 17)):
            return False, "Not all values 1-16 are present"
        
        # Check row sums
        for i in range(n):
            row_sum = sum(square_matrix[i, :])
            if row_sum != expected_magic_sum:
                return False, f"Row {i} sum is {row_sum}, expected {expected_magic_sum}"
        
        # Check column sums
        for j in range(n):
            col_sum = sum(square_matrix[:, j])
            if col_sum != expected_magic_sum:
                return False, f"Column {j} sum is {col_sum}, expected {expected_magic_sum}"
        
        # Check main diagonal sum
        main_diag_sum = sum(square_matrix[i, i] for i in range(n))
        if main_diag_sum != expected_magic_sum:
            return False, f"Main diagonal sum is {main_diag_sum}, expected {expected_magic_sum}"
        
        # Check anti-diagonal sum
        anti_diag_sum = sum(square_matrix[i, n-1-i] for i in range(n))
        if anti_diag_sum != expected_magic_sum:
            return False, f"Anti-diagonal sum is {anti_diag_sum}, expected {expected_magic_sum}"
        
        return True, "All constraints satisfied - valid magic square"
    
    # Verify the solution
    valid, message = verify_magic_square(solution)
    assert valid, f"Verification failed: {message}"
    
    # Step 4: Output
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))