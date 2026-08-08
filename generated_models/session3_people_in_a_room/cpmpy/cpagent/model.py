import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Problem: 13 people (4 males, 9 females) enter a room one at a time
# Constraint: At any time, ratio F/M <= 7/3
# Output: Sequence where 0=male, 1=female

total_people = 13
males = 4
females = 9

# Step 2: Model with CPMpy
# Decision variables: sequence[i] represents the gender of the i-th person to enter
# 0 = male, 1 = female
sequence = cp.intvar(0, 1, shape=13, name="sequence")

model = cp.Model()

# Constraint 1: Exactly 4 males and 9 females
model += cp.Count(sequence, 0) == 4  # 4 males
model += cp.Count(sequence, 1) == 9  # 9 females

# Constraint 2: At any time t, the ratio F/M <= 7/3
# This means: 3*F <= 7*M at all times, with special handling for M=0
for t in range(1, 14):  # For each time step (1-indexed)
    # Count males and females up to time t
    males_so_far = cp.sum([1 - sequence[i] for i in range(t)])  # Count of 0s
    females_so_far = cp.sum([sequence[i] for i in range(t)])    # Count of 1s
    
    # If no males have entered yet, no females can enter either
    # If males have entered, then 3*F <= 7*M
    model += (males_so_far == 0).implies(females_so_far == 0)
    model += (males_so_far > 0).implies(3 * females_so_far <= 7 * males_so_far)

# Step 3: Solve and verify
if model.solve():
    solution_sequence = sequence.value().tolist()
    
    # Verification
    def verify_solution(seq):
        # Check counts
        if seq.count(0) != 4 or seq.count(1) != 9 or len(seq) != 13:
            return False
        
        # Check ratio constraint at each step
        males_count = 0
        females_count = 0
        for gender in seq:
            if gender == 0:
                males_count += 1
            else:
                females_count += 1
            
            if males_count == 0 and females_count > 0:
                return False
            if males_count > 0 and females_count / males_count > 7/3 + 1e-9:
                return False
        
        return True
    
    assert verify_solution(solution_sequence), "Solution verification failed!"
    
    # Step 4: Output
    solution = {"sequence": solution_sequence}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))