import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Interval scheduling maximization
# Objective: Maximize number of non-overlapping movie intervals
# Constraints: 
# 1. Each movie can be selected (1) or not selected (0)
# 2. No two selected movies can have overlapping time intervals
# 3. Two intervals [a,b] and [c,d] overlap if max(a,c) <= min(b,d)

# Input data
movies = [
    ["Tarjan of the Jungle", 4, 13],
    ["The Four Volume Problem", 17, 27],
    ["The President's Algorist", 1, 10],
    ["Steiner's Tree", 12, 18],
    ["Process Terminated", 23, 30],
    ["Halting State", 9, 16],
    ["Programming Challenges", 19, 25],
    ["Discrete Mathematics", 2, 7],
    ["Calculated Bets", 26, 31]
]

n = len(movies)

# Extract start and end times
starts = [movie[1] for movie in movies]
ends = [movie[2] for movie in movies]

# Pre-compute which pairs of movies overlap
# Two intervals [a,b] and [c,d] overlap if max(a,c) <= min(b,d)
overlapping_pairs = []
for i in range(n):
    for j in range(i+1, n):
        start_i, end_i = starts[i], ends[i]
        start_j, end_j = starts[j], ends[j]
        
        # Check if intervals overlap
        if max(start_i, start_j) <= min(end_i, end_j):
            overlapping_pairs.append((i, j))

# Step 2: Model with CPMpy
# Decision variables: select[i] = 1 if movie i is selected, 0 otherwise
select = cp.boolvar(shape=n, name="select")

# Create the model
model = cp.Model()

# Constraint: No two overlapping movies can both be selected
for i, j in overlapping_pairs:
    model += select[i] + select[j] <= 1

# Objective: Maximize the number of selected movies
num_selected = cp.sum(select)
model.maximize(num_selected)

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    selected_movies = select.value().tolist()
    num_selected_movies = int(num_selected.value())
    
    # Verification (independent of CPMpy)
    def verify_solution(sol):
        """Verify the solution satisfies all constraints"""
        selected = sol["selected_movies"]
        num_selected = sol["num_selected_movies"]
        
        # Structural verification
        if len(selected) != n:
            return False, f"Wrong length: {len(selected)} vs {n}"
        
        # Convert to boolean for consistency
        selected_bool = [bool(x) for x in selected]
        
        # Check count matches
        actual_count = sum(selected_bool)
        if actual_count != num_selected:
            return False, f"Count mismatch: {actual_count} vs {num_selected}"
        
        # Check no overlapping movies are both selected
        selected_indices = [i for i, sel in enumerate(selected_bool) if sel]
        
        for i in selected_indices:
            for j in selected_indices:
                if i < j:  # Check each pair once
                    start_i, end_i = starts[i], ends[i]
                    start_j, end_j = starts[j], ends[j]
                    
                    # Check if intervals overlap
                    if max(start_i, start_j) <= min(end_i, end_j):
                        return False, f"Movies {i} and {j} overlap"
        
        return True, "All constraints satisfied"
    
    # Convert to required format (integers instead of booleans)
    solution = {
        "num_selected_movies": num_selected_movies,
        "selected_movies": [1 if x else 0 for x in selected_movies]
    }
    
    # Verify solution
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))