# Import libraries
from cpmpy import *
import json

# Parameters
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

# Decision Variables
left = intvar(0, deck_width, shape=n_containers, name="left")
right = intvar(0, deck_width, shape=n_containers, name="right")
bottom = intvar(0, deck_length, shape=n_containers, name="bottom")
top = intvar(0, deck_length, shape=n_containers, name="top")

# Model
model = Model()

# Container dimensions
for i in range(n_containers):
    model += right[i] == left[i] + width[i]
    model += top[i] == bottom[i] + length[i]

# Containers must be within deck boundaries
for i in range(n_containers):
    model += right[i] <= deck_width
    model += top[i] <= deck_length

# No overlapping containers
for i in range(n_containers):
    for j in range(i+1, n_containers):
        model += (right[i] <= left[j]) | (right[j] <= left[i]) | (top[i] <= bottom[j]) | (top[j] <= bottom[i])

# First container must be in southeast corner
model += left[0] == 0
model += bottom[0] == deck_length - length[0]

# Loading sequence constraints (each subsequent container must touch north and west)
for i in range(1, n_containers):
    # Must touch west (either left edge of deck or right edge of another container)
    west_touch = [left[i] == 0]  # Touches west wall
    for j in range(i):
        west_touch.append(left[i] <= right[j])  # Touches or overlaps with another container's right
        west_touch.append(right[j] <= left[i])  # Exact touching condition
    model += any(west_touch)
    
    # Must touch north (either top edge of deck or bottom edge of another container)
    north_touch = [top[i] == deck_length]  # Touches north wall
    for j in range(i):
        north_touch.append(bottom[i] <= top[j])  # Touches or overlaps with another container's top
        north_touch.append(top[j] <= bottom[i])  # Exact touching condition
    model += any(north_touch)

# Solve
model.solve()

# Print solution
solution = {
    "right": right.value().tolist(),
    "top": top.value().tolist(),
    "left": left.value().tolist(),
    "bottom": bottom.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script