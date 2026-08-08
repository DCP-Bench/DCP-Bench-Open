import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Boy gives apple to girl, passes through 5 gates
# At each gate: gives half his apples + 1 to guard
# Constraint: Must have even number of apples before each gate
# Final state: 0 apples after giving apple to girl
# Output: 6 numbers - apples before each gate + apples after last gate

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: apples[i] for i=0,1,2,3,4,5
# apples[0-4] = apples before gates 1-5
# apples[5] = apples after gate 5 (before giving to girl)
apples = cp.intvar(0, 1000, shape=6, name="apples")

# Constraint 1: All apples before gates must be even numbers
for i in range(5):  # Before gates 1-5
    model += apples[i] % 2 == 0

# Constraint 2: Transition through each gate
# At gate i: give apples[i-1]/2 + 1, keep apples[i-1] - (apples[i-1]/2 + 1) = apples[i-1]/2 - 1
for i in range(1, 6):
    model += apples[i] == apples[i-1] // 2 - 1

# Constraint 3: After giving apple to girl, he has 0 apples left
# So apples[5] = 1 (he gives 1 apple to girl)
model += apples[5] == 1

# Step 3: Solve and verify
if model.solve():
    solution_values = apples.value().tolist()
    
    # Verification
    def verify_solution(apples_list):
        """Independent verification of the solution"""
        # Check structure: should have 6 numbers
        if len(apples_list) != 6:
            return False
        
        # Check that first 5 are even (before gates)
        for i in range(5):
            if apples_list[i] % 2 != 0:
                return False
        
        # Simulate the process
        current_apples = apples_list[0]
        
        for gate in range(1, 6):
            # Check if current matches expected
            if current_apples != apples_list[gate-1]:
                return False
            
            # Give half + 1 to guard
            given = current_apples // 2 + 1
            current_apples = current_apples - given
            
            # Check if this matches next expected value (except for last gate)
            if gate < 5 and current_apples != apples_list[gate]:
                return False
        
        # Check final state
        if current_apples != apples_list[5] or current_apples != 1:
            return False
        
        # Give apple to girl - should result in 0
        return (current_apples - 1) == 0
    
    assert verify_solution(solution_values), "Solution verification failed!"
    
    # Step 4: Output in required JSON format
    solution = {
        "apples": solution_values
    }
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))