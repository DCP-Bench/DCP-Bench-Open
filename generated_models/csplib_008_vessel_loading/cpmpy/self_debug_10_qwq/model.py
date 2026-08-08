
import cpmpy as cp
import json

# Data
deck_width = 5
deck_length = 5
n_containers = 3
width = [5, 2, 3]
length = [1, 4, 4]
classes = [1, 1, 1]
separation = [[0, 0], [0, 0]]

model = cp.Model()

# Decision Variables
left = [cp.intvar(0, deck_width, name=f"left_{i}") for i in range(n_containers)]
bottom = [cp.intvar(0, deck_length, name=f"bottom_{i}") for i in range(n_containers)]

# Constraints

# Non-overlapping between all pairs of containers
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        # Non-overlap in x-axis OR y-axis
        x_overlap = (left[i] + width[i] <= left[j]) | (left[j] + width[j] <= left[i])
        y_overlap = (bottom[i] + length[i] <= bottom[j]) | (bottom[j] + length[j] <= bottom[i])
        model += (x_overlap | y_overlap)  # Corrected to OR

# Containers must fit within the deck boundaries
for i in range(n_containers):
    model += left[i] >= 0
    model += (left[i] + width[i]) <= deck_width
    model += bottom[i] >= 0
    model += (bottom[i] + length[i]) <= deck_length

# Loading sequence constraints
for k in range(1, n_containers):
    # West condition: left edge touches deck wall or a previous container's right edge
    west_ok = (left[k] == 0) | cp.any([(left[m] + width[m] == left[k]) for m in range(k)])
    
    # North condition: top edge touches deck wall or a previous container's bottom edge
    top_k = bottom[k] + length[k]
    north_ok = (top_k == deck_length) | cp.any([(bottom[n] == top_k) for n in range(k)])
    
    model += (west_ok & north_ok)

# Solve and print solution
if model.solve():
    left_values = [int(l.value()) for l in left]
    right_values = [l + w for l, w in zip(left_values, width)]
    bottom_values = [int(b.value()) for b in bottom]
    top_values = [b + l for b, l in zip(bottom_values, length)]
    
    solution = {
        'left': left_values,
        'right': right_values,
        'bottom': bottom_values,
        'top': top_values
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
