import cpmpy as cp
import numpy as np
import json

# Step 1: Input data and problem analysis
warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"]
fixed_costs = [400, 500, 300, 150]  # Weekly fixed costs per warehouse
max_shipping = 100  # Max units per week per warehouse
demands = [80, 70, 40]  # Weekly demands for regions 1 to 3
shipping_costs = [
    [20, 40, 50],  # New York to regions 1, 2, 3
    [48, 15, 26],  # Los Angeles to regions 1, 2, 3
    [26, 35, 18],  # Chicago to regions 1, 2, 3
    [24, 50, 35]   # Atlanta to regions 1, 2, 3
]

n_warehouses = len(warehouse_s)
n_regions = len(demands)

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables
# Binary variables for whether each warehouse is open
open_warehouse = cp.boolvar(shape=n_warehouses, name="open_warehouse")

# Integer variables for shipments from each warehouse to each region
ships = cp.intvar(0, max_shipping, shape=(n_warehouses, n_regions), name="ships")

# Constraints
# 1. If New York (0) is opened, then Los Angeles (1) must be opened
model += open_warehouse[0].implies(open_warehouse[1])

# 2. No more than 3 warehouses can be operational
model += cp.sum(open_warehouse) <= 3

# 3. Either Atlanta (3) or Los Angeles (1) must be opened
model += open_warehouse[3] | open_warehouse[1]

# 4. All regional demands must be satisfied
for r in range(n_regions):
    model += cp.sum(ships[w, r] for w in range(n_warehouses)) == demands[r]

# 5. Each warehouse cannot ship more than max_shipping units total
for w in range(n_warehouses):
    model += cp.sum(ships[w, r] for r in range(n_regions)) <= max_shipping

# 6. Can only ship from open warehouses
for w in range(n_warehouses):
    for r in range(n_regions):
        model += ships[w, r] <= max_shipping * open_warehouse[w]

# Objective: Minimize total cost
fixed_cost_total = cp.sum(fixed_costs[w] * open_warehouse[w] for w in range(n_warehouses))
shipping_cost_total = cp.sum(shipping_costs[w][r] * ships[w, r] 
                           for w in range(n_warehouses) 
                           for r in range(n_regions))
total_cost = fixed_cost_total + shipping_cost_total

model.minimize(total_cost)

# Step 3: Solve and verify
if model.solve():
    # Extract solution values
    open_vals = open_warehouse.value()
    ships_vals = ships.value()
    total_cost_val = total_cost.value()
    
    # Create solution dictionary
    solution = {
        "total_cost": int(total_cost_val),
        "open_warehouse": [int(x) for x in open_vals],
        "ships": [[int(ships_vals[w][r]) for r in range(n_regions)] for w in range(n_warehouses)]
    }
    
    # Verification
    def verify_solution(sol):
        open_wh = sol["open_warehouse"]
        ships_matrix = sol["ships"]
        
        # Check all constraints
        # 1. NY -> LA implication
        if open_wh[0] == 1 and open_wh[1] != 1:
            return False
        
        # 2. Max 3 warehouses
        if sum(open_wh) > 3:
            return False
        
        # 3. Atlanta OR Los Angeles
        if open_wh[3] == 0 and open_wh[1] == 0:
            return False
        
        # 4. Demand satisfaction
        for r in range(n_regions):
            if sum(ships_matrix[w][r] for w in range(n_warehouses)) != demands[r]:
                return False
        
        # 5. Shipping limits
        for w in range(n_warehouses):
            if sum(ships_matrix[w][r] for r in range(n_regions)) > max_shipping:
                return False
        
        # 6. Only open warehouses ship
        for w in range(n_warehouses):
            if open_wh[w] == 0 and sum(ships_matrix[w][r] for r in range(n_regions)) > 0:
                return False
        
        return True
    
    assert verify_solution(solution), "Solution verification failed!"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))