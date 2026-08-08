
import cpmpy as cp
import json

# Data
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
# End of data

# Model definition
model = cp.Model()

# Decision Variables
left = cp.intvar(0, deck_width, shape=n_containers, name="left")
right = cp.intvar(0, deck_width, shape=n_containers, name="right")
bottom = cp.intvar(0, deck_length, shape=n_containers, name="bottom")
top = cp.intvar(0, deck_length, shape=n_containers, name="top")

# Size constraints: link left/right and bottom/top with widths and lengths
for i in range(n_containers):
    model += [
        left[i] + width[i] == right[i],
        bottom[i] + length[i] == top[i]
    ]

# Separation (and non-overlap) constraints between all pairs
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        ci = classes[i] - 1
        cj = classes[j] - 1
        sep = separation[ci][cj]
        # Enforce separation along x or y
        model += (
            (right[i] + sep <= left[j]) |
            (right[j] + sep <= left[i]) |
            (top[i] + sep <= bottom[j]) |
            (top[j] + sep <= bottom[i])
        )

# Loading sequence constraints
# Container 0 must touch west wall (left=0) and north wall (top=deck_length)
model += [left[0] == 0, top[0] == deck_length]

# For each subsequent container j, enforce a contact to the north and to the west
for j in range(1, n_containers):
    # North contact: either touch deck north wall or touch bottom of some earlier container
    north_terms = [top[j] == deck_length]
    for k in range(j):
        # top[j] == bottom[k] AND x-intervals overlap
        north_terms.append(
            (top[j] == bottom[k]) &
            (left[j] < right[k]) &
            (left[k] < right[j])
        )
    model += cp.any(north_terms)

    # West contact: either touch west wall or touch right side of some earlier container
    west_terms = [left[j] == 0]
    for k in range(j):
        # left[j] == right[k] AND y-intervals overlap
        west_terms.append(
            (left[j] == right[k]) &
            (bottom[j] < top[k]) &
            (bottom[k] < top[j])
        )
    model += cp.any(west_terms)

# Solve and print
if model.solve():
    solution = {
        "left": left.value().tolist(),
        "right": right.value().tolist(),
        "top": top.value().tolist(),
        "bottom": bottom.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
