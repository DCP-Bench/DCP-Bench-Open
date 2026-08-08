import cpmpy as cp
import numpy as np
import json

# Step 1: Problem Analysis
# We have 6 time slots of 4 hours each (24 hours total)
# Each bus works 8 consecutive hours = 2 consecutive time slots
# Need to minimize total buses while meeting demand in each slot

demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
n_slots = len(demands)

# Step 2: Model with CPMpy
# Decision variables: x[i] = number of buses starting their shift at time slot i
x = cp.intvar(0, 20, shape=n_slots, name="x")

model = cp.Model()

# Constraints: For each time slot, available buses must meet demand
# A bus starting at slot i works in slots i and (i+1) % n_slots
for slot in range(n_slots):
    # Buses available in this slot come from:
    # 1. Buses that started in this slot (first 4 hours of their 8-hour shift)
    # 2. Buses that started in the previous slot (second 4 hours of their 8-hour shift)
    prev_slot = (slot - 1) % n_slots
    available_buses = x[slot] + x[prev_slot]
    model += available_buses >= demands[slot]

# Objective: minimize total number of buses
total_buses = cp.sum(x)
model.minimize(total_buses)

# Step 3: Solve & Verify
if model.solve():
    solution_x = x.value()
    
    # Create solution in required format
    solution = {
        "x": solution_x.tolist() if hasattr(solution_x, 'tolist') else list(solution_x)
    }
    
    # Verification
    def verify_solution(sol):
        x_vals = sol["x"]
        n = len(x_vals)
        
        # Check all demand constraints
        for slot in range(n):
            prev_slot = (slot - 1) % n
            available = x_vals[slot] + x_vals[prev_slot]
            required = demands[slot]
            
            if available < required:
                return False, f"Slot {slot}: available={available} < required={required}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))