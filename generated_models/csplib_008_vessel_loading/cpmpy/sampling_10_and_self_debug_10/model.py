
import cpmpy as cp
import json

# Data
deck_width = 5  # Width of the deck
deck_length = 5  # Length of the deck
n_containers = 3  # Number of containers
width = [5, 2, 3]  # Widths of containers
length = [1, 4, 4]  # Lengths of containers
classes = [1, 1, 1]  # Classes of containers
separation = [  # Separation constraints between classes (0-based indexing for classes)
    [0, 0],
    [0, 0]
]
# End of data

model = cp.Model()

# Decision variables for container positions on the deck:
# left and bottom coordinates of each container (top and right can be derived)
left = cp.intvar(0, deck_width, shape=n_containers, name="left")
bottom = cp.intvar(0, deck_length, shape=n_containers, name="bottom")

# Derived variables
right = [left[i] + width[i] for i in range(n_containers)]
top = [bottom[i] + length[i] for i in range(n_containers)]

# Constraints
# 1. Containers must be fully on the deck
for i in range(n_containers):
    model += (right[i] <= deck_width)
    model += (top[i] <= deck_length)

# 2. No overlapping of containers
for i in range(n_containers):
    for j in range(i+1, n_containers):
        # Non-overlapping means one container is left, right, above or below the other
        model += (
            (right[i] <= left[j]) | (right[j] <= left[i]) |
            (top[i] <= bottom[j]) | (top[j] <= bottom[i])
        )

# 3. Separation constraints between classes (here all zero, but let's still implement for completeness)
# For each pair of containers i,j with classes c_i, c_j, if c_i != c_j then enforce min separation in width or length
for i in range(n_containers):
    for j in range(i+1, n_containers):
        ci = classes[i] - 1
        cj = classes[j] - 1
        sep = separation[ci][cj]
        if sep > 0:
            # The minimum horizontal or vertical gap between containers of these classes must be >= sep
            # This means containers must be separated by at least sep in either horizontal or vertical dimension
            model += (
                (right[i] + sep <= left[j]) | (right[j] + sep <= left[i]) |
                (top[i] + sep <= bottom[j]) | (top[j] + sep <= bottom[i])
            )

# 4. Physical loading sequence constraints:
# Each successive container must touch another container or a wall to the north and west.
# That means for containers 1..n-1 (index 1..n-1), left[i] touches either left wall (x=0) or right[j] of some container j,
# and bottom[i] touches either bottom wall (y=0) or top[j] of some container j.
for i in range(1, n_containers):
    # Touch to west (left side): either left[i] == 0 or exists j < i: right[j] == left[i]
    west_touch = (left[i] == 0) | cp.any([right[j] == left[i] for j in range(i)])
    # Touch to north (bottom side): either bottom[i] == 0 or exists j < i: top[j] == bottom[i]
    north_touch = (bottom[i] == 0) | cp.any([top[j] == bottom[i] for j in range(i)])
    model += west_touch
    model += north_touch

# Solve and print
if model.solve():
    solution = {
        'left': left.value().tolist(),
        'right': [int(r.value()) for r in right],
        'top': [int(t.value()) for t in top],
        'bottom': bottom.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
