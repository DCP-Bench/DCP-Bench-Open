import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Find 4 item prices such that:
# 1. Sum of prices = $7.11 (711 cents)
# 2. Product of prices = $7.11 (when prices are in dollars)
# 
# Key insight: If prices are p1, p2, p3, p4 in cents, then:
# - Sum constraint: p1 + p2 + p3 + p4 = 711
# - Product constraint: (p1/100) * (p2/100) * (p3/100) * (p4/100) = 7.11
#   Which means: p1 * p2 * p3 * p4 = 7.11 * 100^4 = 711000000

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: prices in cents (must be positive integers)
prices = cp.intvar(1, 711, shape=4, name="prices")

# Step 3: Add constraints
# Constraint 1: Sum of prices in cents equals 711
model += cp.sum(prices) == 711

# Constraint 2: Product constraint (accounting for dollar conversion)
model += prices[0] * prices[1] * prices[2] * prices[3] == 711000000

# Performance constraint: symmetry breaking (order prices)
model += prices[0] <= prices[1]
model += prices[1] <= prices[2] 
model += prices[2] <= prices[3]

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    solution_prices = prices.value().tolist()
    
    # Step 4: Verification (independent check)
    def verify_solution(price_list):
        # Structural verification
        if len(price_list) != 4 or any(p <= 0 for p in price_list):
            return False
        
        # Logical verification
        total_sum_cents = sum(price_list)
        if total_sum_cents != 711:
            return False
        
        # Product verification: convert to dollars and check
        prices_dollars = [p / 100.0 for p in price_list]
        product_dollars = prices_dollars[0] * prices_dollars[1] * prices_dollars[2] * prices_dollars[3]
        
        return abs(product_dollars - 7.11) < 1e-10
    
    # Verify the solution
    assert verify_solution(solution_prices), "Solution verification failed!"
    
    # Step 4: Output in required JSON format
    solution = {"prices": solution_prices}
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))