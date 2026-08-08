
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

model = cp.Model()

# Decision variables: positions of containers on the deck
# left[i], bottom[i] are coordinates of the bottom-left corner of container i
left = cp.intvar(0, deck_width, shape=n_containers, name="left")
bottom = cp.intvar(0, deck_length, shape=n_containers, name="bottom")

# right[i], top[i] can be derived from left[i], bottom[i] and container dimensions
right = [left[i] + width[i] for i in range(n_containers)]
top = [bottom[i] + length[i] for i in range(n_containers)]

# Constraints list
constraints = []

# 1) Containers must be inside the deck boundaries
for i in range(n_containers):
    constraints += [right[i] <= deck_width]
    constraints += [top[i] <= deck_length]

# 2) No overlapping between containers
for i in range(n_containers):
    for j in range(i+1, n_containers):
        # Containers i and j do not overlap if one is completely to the left, right, above or below the other
        no_overlap = (
            (right[i] <= left[j]) |
            (right[j] <= left[i]) |
            (top[i] <= bottom[j]) |
            (top[j] <= bottom[i])
        )
        constraints += [no_overlap]

# 3) Separation constraints between classes
# Since separation matrix is 2x2 but classes are 1-based and only class 1 is used,
# and separation is zero, no constraints needed here.
# But we implement general form for completeness.
for i in range(n_containers):
    for j in range(i+1, n_containers):
        c1 = classes[i] - 1
        c2 = classes[j] - 1
        sep = separation[c1][c2]
        if sep > 0:
            # Enforce minimum separation horizontally or vertically
            # This means containers must be at least sep apart horizontally or vertically
            constraints += [
                (right[i] + sep <= left[j]) |
                (right[j] + sep <= left[i]) |
                (top[i] + sep <= bottom[j]) |
                (top[j] + sep <= bottom[i])
            ]

# 4) Loading sequence constraints:
# Each successive container must touch part of another container or a deck wall both to the north and to the west.
# "North" means touching something above (top side), "west" means touching something to the left side.
# The first container is positioned from the southeast corner, so it must touch deck walls on north and west.
# But since deck walls are at left=0 (west wall) and bottom=0 (south wall), and containers are placed from bottom-left,
# the first container must touch deck walls to north and west means:
# Actually, the problem states "Each successive container in the loading sequence must be positioned so that it touches part of another container or a deck wall both to the north and to the west."
# So for container 0 (first), it must touch deck walls north and west.
# For others, must touch either deck wall or another container on north and west sides.

# Define helper functions to check touching on north and west sides
def touches_north(i):
    # Container i touches deck wall north if top[i] == deck_length
    # Or touches another container j if bottom[j] == top[i] and horizontal intervals overlap
    touch_deck = (top[i] == deck_length)
    touch_container = []
    for j in range(n_containers):
        if j == i:
            continue
        # Check if bottom[j] == top[i] and horizontal overlap
        horizontal_overlap = (left[i] < right[j]) & (right[i] > left[j])
        touch_container.append((bottom[j] == top[i]) & horizontal_overlap)
    if touch_container:
        return touch_deck | cp.any(touch_container)
    else:
        return touch_deck

def touches_west(i):
    # Container i touches deck wall west if left[i] == 0
    # Or touches another container j if right[j] == left[i] and vertical intervals overlap
    touch_deck = (left[i] == 0)
    touch_container = []
    for j in range(n_containers):
        if j == i:
            continue
        # Check if right[j] == left[i] and vertical overlap
        vertical_overlap = (bottom[i] < top[j]) & (top[i] > bottom[j])
        touch_container.append((right[j] == left[i]) & vertical_overlap)
    if touch_container:
        return touch_deck | cp.any(touch_container)
    else:
        return touch_deck

# Add loading sequence constraints for containers 1..n-1
for i in range(n_containers):
    model += touches_north(i)
    model += touches_west(i)

# Add all constraints to model
model += constraints

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
