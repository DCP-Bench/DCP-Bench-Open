import cpmpy as cp
import numpy as np
import json

# Problem data
target_amount = 199
coin_values = [1, 2, 5, 10, 25, 50]
coin_available = [20, 10, 15, 8, 4, 2]
n_coin_types = len(coin_values)

# Decision variables: number of coins of each type to use
coin_counts = cp.intvar(0, max(coin_available), shape=n_coin_types, name="coin_counts")

model = cp.Model()

# Constraint 1: Cannot use more coins than available
for i in range(n_coin_types):
    model += coin_counts[i] <= coin_available[i]

# Constraint 2: Total value must equal target amount
total_value = cp.sum([coin_counts[i] * coin_values[i] for i in range(n_coin_types)])
model += total_value == target_amount

# Objective: Minimize total number of coins used
total_coins = cp.sum(coin_counts)
model.minimize(total_coins)

# Solve the model
if model.solve():
    # Extract solution
    solution_counts = coin_counts.value()
    
    # Create solution in required format
    solution = {
        "coin_counts": solution_counts.tolist()
    }
    
    # Verification
    def verify_solution(sol):
        counts = sol["coin_counts"]
        
        # Check availability constraints
        for i in range(n_coin_types):
            if counts[i] > coin_available[i] or counts[i] < 0:
                return False
        
        # Check value constraint
        total_value_check = sum(counts[i] * coin_values[i] for i in range(n_coin_types))
        if total_value_check != target_amount:
            return False
        
        return True
    
    assert verify_solution(solution), "Solution verification failed!"
    
    # Output the solution
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))