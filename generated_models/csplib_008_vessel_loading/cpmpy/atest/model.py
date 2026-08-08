# Import libraries
from cpmpy import *
import json

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

# Decision variables
# For each container, define its left, right, top, and bottom coordinates
left = intvar(0, deck_width, shape=n_containers, name="left")
right = intvar(0, deck_width + 1, shape=n_containers, name="right")
bottom = intvar(0, deck_length, shape=n_containers, name="bottom")
top = intvar(0, deck_length + 1, shape=n_containers, name="top")

# Model
model = Model()

# Ensure that for each container, right = left + width and top = bottom + length
for i in range(n_containers):
    model += [right[i] == left[i] + width[i]]
    model += [top[i] == bottom[i] + length[i]]

# Ensure that containers do not overlap
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        # No overlap in x-axis
        model += [(right[i] <= left[j]) | (right[j] <= left[i])]
        # No overlap in y-axis
        model += [(top[i] <= bottom[j]) | (top[j] <= bottom[i])]

# Ensure that containers are within the deck boundaries
for i in range(n_containers):
    model += [left[i] >= 0]
    model += [right[i] <= deck_width]
    model += [bottom[i] >= 0]
    model += [top[i] <= deck_length]

# Solve the model
model.solve()

# Output the solution
solution = {
    "right": right.value().tolist(),
    "top": top.value().tolist(),
    "left": left.value().tolist(),
    "bottom": bottom.value().tolist()
}
print(json.dumps(solution))