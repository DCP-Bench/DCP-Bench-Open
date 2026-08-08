import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Kidney exchange to maximize transplants
# Constraints:
# 1. Compatibility: can only donate to compatible people
# 2. No self-donation
# 3. Each person donates at most one kidney
# 4. Each person receives at most one kidney
# 5. Anyone who gives a kidney must receive one

# Input data
num_people = 8
compatible = [  # 1-based indexing, compatible[i] is the list of people to which i can donate
    [2, 3],     # Person 1 can donate to persons 2, 3
    [1, 6],     # Person 2 can donate to persons 1, 6
    [1, 4, 7],  # Person 3 can donate to persons 1, 4, 7
    [2],        # Person 4 can donate to person 2
    [2],        # Person 5 can donate to person 2
    [5],        # Person 6 can donate to person 5
    [8],        # Person 7 can donate to person 8
    [3]         # Person 8 can donate to person 3
]

# Convert to 0-based indexing for easier processing
compatible_0based = []
for person_targets in compatible:
    compatible_0based.append([t-1 for t in person_targets])

# Step 2: Model with CPMpy
# Decision variables: transplants[i][j] = 1 if person i donates to person j
transplants = cp.boolvar(shape=(num_people, num_people), name="transplants")

model = cp.Model()

# Constraint 1: Compatibility - can only donate to compatible people
for i in range(num_people):
    for j in range(num_people):
        if j not in compatible_0based[i]:
            model += transplants[i, j] == 0

# Constraint 2: No self-donation
for i in range(num_people):
    model += transplants[i, i] == 0

# Constraint 3: Each person donates at most one kidney
for i in range(num_people):
    model += cp.sum(transplants[i, :]) <= 1

# Constraint 4: Each person receives at most one kidney
for j in range(num_people):
    model += cp.sum(transplants[:, j]) <= 1

# Constraint 5: Anyone who gives a kidney must receive one
for i in range(num_people):
    gives = cp.sum(transplants[i, :])  # Number of kidneys person i gives
    receives = cp.sum(transplants[:, i])  # Number of kidneys person i receives
    model += gives == receives  # If gives 1, must receive 1; if gives 0, receives 0

# Objective: Maximize number of people who receive a kidney
total_transplants = cp.sum(transplants)
model.maximize(total_transplants)

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    transplant_matrix = transplants.value()
    
    # Convert boolean matrix to integer matrix (0/1) for output format
    transplant_matrix_int = transplant_matrix.astype(int)
    
    solution = {
        "transplants": transplant_matrix_int.tolist()
    }
    
    # Verification
    def verify_solution(sol):
        """Independent verification of the solution"""
        transplant_matrix = np.array(sol["transplants"])
        
        # Structural verification
        if transplant_matrix.shape != (num_people, num_people):
            return False, f"Wrong shape: {transplant_matrix.shape}"
        
        # Logical verification
        # Check compatibility constraints
        for i in range(num_people):
            for j in range(num_people):
                if transplant_matrix[i, j] == 1:
                    if j not in compatible_0based[i]:
                        return False, f"Incompatible donation: Person {i+1} to Person {j+1}"
        
        # Check no self-donation
        for i in range(num_people):
            if transplant_matrix[i, i] == 1:
                return False, f"Self-donation detected for Person {i+1}"
        
        # Check each person donates at most one kidney
        for i in range(num_people):
            donations = np.sum(transplant_matrix[i, :])
            if donations > 1:
                return False, f"Person {i+1} donates {donations} kidneys"
        
        # Check each person receives at most one kidney
        for j in range(num_people):
            received = np.sum(transplant_matrix[:, j])
            if received > 1:
                return False, f"Person {j+1} receives {received} kidneys"
        
        # Check constraint: anyone who gives must receive
        for i in range(num_people):
            gives = np.sum(transplant_matrix[i, :])
            receives = np.sum(transplant_matrix[:, i])
            if gives != receives:
                return False, f"Person {i+1} gives {gives} but receives {receives}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))