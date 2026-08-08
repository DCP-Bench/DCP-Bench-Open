import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Problem: 25 cows (numbered 1-25, cow i gives i kg milk per day)
# 5 sons getting 7, 6, 5, 4, 3 cows respectively
# Each son must get the same total amount of milk

# Problem parameters
n_cows = 25
n_sons = 5
cows_per_son = [7, 6, 5, 4, 3]
milk_per_cow = list(range(1, 26))  # cow i gives i kg milk
total_milk = sum(milk_per_cow)  # 325 kg
target_milk_per_son = total_milk // n_sons  # 65 kg per son

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: cow_assignment[i] = j means cow i is assigned to son j
# Using 0-based indexing for sons (0, 1, 2, 3, 4)
cow_assignment = cp.intvar(0, n_sons-1, shape=n_cows, name="cow_assignment")

# Constraint 1: Each son gets the correct number of cows
for son in range(n_sons):
    count_cows_for_son = cp.Count(cow_assignment, son)
    model += count_cows_for_son == cows_per_son[son]

# Constraint 2: Each son gets exactly the same amount of milk (65 kg)
for son in range(n_sons):
    # Calculate total milk for this son
    milk_for_son = cp.sum([
        (cow_assignment[cow] == son) * milk_per_cow[cow] 
        for cow in range(n_cows)
    ])
    model += milk_for_son == target_milk_per_son

# Step 3: Solve and verify
if model.solve():
    # Extract the solution
    assignment = cow_assignment.value()
    
    # Verification (independent of CPMpy)
    def verify_solution(assign):
        # Check cow counts per son
        for son in range(n_sons):
            count = sum(1 for a in assign if a == son)
            if count != cows_per_son[son]:
                return False, f"Son {son} has {count} cows, expected {cows_per_son[son]}"
        
        # Check milk distribution per son
        for son in range(n_sons):
            total_milk = sum(milk_per_cow[cow] for cow in range(n_cows) if assign[cow] == son)
            if total_milk != target_milk_per_son:
                return False, f"Son {son} has {total_milk} kg milk, expected {target_milk_per_son}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(assignment)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output in required format
    solution = {
        "cow_assignments": assignment.tolist()
    }
    
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))