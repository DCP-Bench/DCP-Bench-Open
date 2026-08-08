
import cpmpy as cp
import json

# Data (optional)
deck_width = 5  # Width of the deck
deck_length = 5  # Length of the deck
n_containers = 3  # Number of containers
width = [5, 2, 3]  # Widths of containers
length = [1, 4, 4]  # Lengths of containers
classes = [1, 1, 1]  # Classes of containers (1-based)
separation = [  # Separation constraints between classes (min clearance along x or y)
    [0, 0],
    [0, 0]
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
left = cp.intvar(0, deck_width, shape=n_containers, name="left")
right = cp.intvar(0, deck_width, shape=n_containers, name="right")
bottom = cp.intvar(0, deck_length, shape=n_containers, name="bottom")
top = cp.intvar(0, deck_length, shape=n_containers, name="top")

# Constraints

# Fit on deck and define right/top from left/bottom plus dimensions
for i in range(n_containers):
    model += (right[i] == left[i] + width[i])
    model += (top[i] == bottom[i] + length[i])
    model += (right[i] <= deck_width)
    model += (top[i] <= deck_length)

# Non-overlap constraints between all pairs
for i in range(n_containers):
    for j in range(i+1, n_containers):
        model += (
            (left[i] >= right[j]) |
            (left[j] >= right[i]) |
            (bottom[i] >= top[j]) |
            (bottom[j] >= top[i])
        )

# Class-based separation constraints (minimum clearance along x or y)
# separation[c1][c2] is the minimum clearance required between class c1 and c2
# Enforced as: intervals are separated by at least sep along x or along y
for i in range(n_containers):
    for j in range(i+1, n_containers):
        c_i = classes[i] - 1  # convert to 0-based
        c_j = classes[j] - 1  # convert to 0-based
        # Ensure indices are valid
        if 0 <= c_i < len(separation) and 0 <= c_j < len(separation[0]):
            sep = separation[c_i][c_j]
            if sep > 0:
                model += (
                    (left[i] >= right[j] + sep) |
                    (left[j] >= right[i] + sep) |
                    (bottom[i] >= top[j] + sep) |
                    (bottom[j] >= top[i] + sep)
                )

# Solve and print
if model.solve():
    solution = {
        'left': left.value().tolist(),
        'right': right.value().tolist(),
        'top': top.value().tolist(),
        'bottom': bottom.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
