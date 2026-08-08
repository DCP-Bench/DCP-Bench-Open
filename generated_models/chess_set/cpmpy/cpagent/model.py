import cpmpy as cp
import json

# Chess Set Production Optimization Problem
# Maximize profit from producing small and large chess sets
# Subject to lathe hours and boxwood material constraints

# Decision variables
small_set = cp.intvar(0, 200, name="small_set")  # Number of small chess sets
large_set = cp.intvar(0, 80, name="large_set")   # Number of large chess sets

# Create model
model = cp.Model()

# Constraints
# Lathe hours: 3 hours for small set, 2 hours for large set, 160 total hours
model += 3 * small_set + 2 * large_set <= 160

# Boxwood material: 1 kg for small set, 3 kg for large set, 200 kg total
model += 1 * small_set + 3 * large_set <= 200

# Objective: Maximize profit ($5 for small set, $20 for large set)
profit = 5 * small_set + 20 * large_set
model.maximize(profit)

# Solve the model
if model.solve():
    # Extract solution
    solution = {
        "small_set": int(small_set.value()),
        "large_set": int(large_set.value()),
        "max_profit": int(profit.value())
    }
    
    # Verification
    def verify_solution(sol):
        small = sol["small_set"]
        large = sol["large_set"]
        profit_val = sol["max_profit"]
        
        # Check constraints
        lathe_hours = 3 * small + 2 * large
        boxwood = 1 * small + 3 * large
        calculated_profit = 5 * small + 20 * large
        
        if lathe_hours > 160:
            return False, f"Lathe hours violated: {lathe_hours} > 160"
        if boxwood > 200:
            return False, f"Boxwood violated: {boxwood} > 200"
        if calculated_profit != profit_val:
            return False, f"Profit mismatch: {calculated_profit} != {profit_val}"
        
        return True, "Solution verified"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))