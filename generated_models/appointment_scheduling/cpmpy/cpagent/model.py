import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Schedule 4 people into 4 interview slots based on their free-busy schedules
# 
# Constraints:
# 1. Each person must be assigned to exactly one slot
# 2. Each slot must have exactly one person assigned
# 3. A person can only be assigned to a slot if they are available (m[person][slot] == 1)

# Problem dimensions
n_people = 4
n_slots = 4

# Availability matrix
m = [
    [1, 1, 1, 1],  # Person 0: available for all slots
    [0, 1, 1, 0],  # Person 1: available for slots 1, 2
    [1, 0, 0, 1],  # Person 2: available for slots 0, 3
    [1, 0, 0, 1]   # Person 3: available for slots 0, 3
]

# Step 2: Model with CPMpy
# Decision variables: x[i][j] = 1 if person i is assigned to slot j
x = cp.boolvar(shape=(n_people, n_slots), name="x")

model = cp.Model()

# Constraint 1: Each person must be assigned to exactly one slot
for person in range(n_people):
    model += cp.sum(x[person, :]) == 1

# Constraint 2: Each slot must have exactly one person assigned
for slot in range(n_slots):
    model += cp.sum(x[:, slot]) == 1

# Constraint 3: A person can only be assigned to a slot if they are available
for person in range(n_people):
    for slot in range(n_slots):
        if m[person][slot] == 0:  # Person not available for this slot
            model += x[person, slot] == 0

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    x_solution = x.value()
    
    # Create solution in required format with integer values
    solution = {
        "x": [[int(val) for val in row] for row in x_solution.tolist()]
    }
    
    # Verification (independent of CPMpy)
    def verify_solution(sol, availability_matrix):
        """Verify the solution satisfies all constraints"""
        x_matrix = np.array(sol["x"])
        n_people, n_slots = x_matrix.shape
        
        # 1. Structural Verification
        if x_matrix.shape != (4, 4):
            return False, f"Structural failure: Shape is {x_matrix.shape}, expected (4, 4)"
        
        # 2. Logical Verification
        
        # Check constraint 1: Each person assigned to exactly one slot
        for person in range(n_people):
            person_assignments = np.sum(x_matrix[person, :])
            if person_assignments != 1:
                return False, f"Logical failure: Person {person} assigned to {person_assignments} slots, expected 1"
        
        # Check constraint 2: Each slot has exactly one person
        for slot in range(n_slots):
            slot_assignments = np.sum(x_matrix[:, slot])
            if slot_assignments != 1:
                return False, f"Logical failure: Slot {slot} has {slot_assignments} people, expected 1"
        
        # Check constraint 3: Assignments respect availability
        for person in range(n_people):
            for slot in range(n_slots):
                if x_matrix[person, slot] == 1 and availability_matrix[person][slot] == 0:
                    return False, f"Logical failure: Person {person} assigned to slot {slot} but not available"
        
        return True, "All constraints satisfied"
    
    # Verify the solution
    valid, msg = verify_solution(solution, m)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))