import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Vessel Loading - pack containers on deck without overlapping
# Constraints:
# - Containers must fit within deck boundaries
# - No overlapping containers
# - Separation constraints between classes (all same class here, so no separation needed)

# Input data
deck_width = 5  # Width of the deck 
deck_length = 5  # Length of the deck 
n_containers = 3  # Number of containers 
width = [5, 2, 3]  # Widths of containers 
length = [1, 4, 4]  # Lengths of containers 
classes = [1, 1, 1]  # Classes of containers 
separation = [  # Separation constraints between classes
    [0, 0],
    [0, 0] 
]

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: position of each container
# left[i] = left edge x-coordinate of container i
# bottom[i] = bottom edge y-coordinate of container i
left = cp.intvar(0, deck_width, shape=n_containers, name="left")
bottom = cp.intvar(0, deck_length, shape=n_containers, name="bottom")

# Derived variables for convenience
right = [left[i] + width[i] for i in range(n_containers)]
top = [bottom[i] + length[i] for i in range(n_containers)]

# Constraints:
# 1. Containers must fit within deck boundaries
for i in range(n_containers):
    model += right[i] <= deck_width
    model += top[i] <= deck_length

# 2. No overlapping containers
# Two rectangles don't overlap if one is completely to the left, right, above, or below the other
for i in range(n_containers):
    for j in range(i+1, n_containers):
        # Container i is to the left of j OR j is to the left of i OR
        # Container i is below j OR j is below i
        model += (right[i] <= left[j]) | (right[j] <= left[i]) | \
                 (top[i] <= bottom[j]) | (top[j] <= bottom[i])

# 3. Separation constraints
# Since all containers are class 1 and separation[0][0] = 0, no additional separation needed

# 4. Symmetry breaking (performance improvement)
# Fix container 0 to be leftmost to break symmetry
model += left[0] <= left[1]
model += left[0] <= left[2]

# Step 3: Solve & Verify
if model.solve():
    # Extract solution values
    left_vals = left.value()
    bottom_vals = bottom.value()
    right_vals = [left_vals[i] + width[i] for i in range(n_containers)]
    top_vals = [bottom_vals[i] + length[i] for i in range(n_containers)]
    
    # Create solution in required format
    solution = {
        "left": [int(x) for x in left_vals],
        "right": [int(x) for x in right_vals],
        "top": [int(x) for x in top_vals],
        "bottom": [int(x) for x in bottom_vals]
    }
    
    # Verification
    def verify_solution(sol):
        """Independent verification of the solution"""
        
        # 1. Structural Verification
        if len(sol["left"]) != n_containers:
            return False, f"Wrong number of left positions"
        if len(sol["right"]) != n_containers:
            return False, f"Wrong number of right positions"
        if len(sol["top"]) != n_containers:
            return False, f"Wrong number of top positions"
        if len(sol["bottom"]) != n_containers:
            return False, f"Wrong number of bottom positions"
        
        # 2. Logical Verification
        left_pos = sol["left"]
        right_pos = sol["right"]
        top_pos = sol["top"]
        bottom_pos = sol["bottom"]
        
        # Check container dimensions are correct
        for i in range(n_containers):
            if right_pos[i] - left_pos[i] != width[i]:
                return False, f"Container {i} width mismatch"
            if top_pos[i] - bottom_pos[i] != length[i]:
                return False, f"Container {i} length mismatch"
        
        # Check containers fit within deck
        for i in range(n_containers):
            if left_pos[i] < 0 or right_pos[i] > deck_width:
                return False, f"Container {i} exceeds deck width"
            if bottom_pos[i] < 0 or top_pos[i] > deck_length:
                return False, f"Container {i} exceeds deck length"
        
        # Check no overlapping
        for i in range(n_containers):
            for j in range(i+1, n_containers):
                # Check if rectangles overlap
                x_overlap = not (right_pos[i] <= left_pos[j] or right_pos[j] <= left_pos[i])
                y_overlap = not (top_pos[i] <= bottom_pos[j] or top_pos[j] <= bottom_pos[i])
                
                if x_overlap and y_overlap:
                    return False, f"Containers {i} and {j} overlap"
        
        return True, "All constraints satisfied"
    
    # Verify the solution
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))