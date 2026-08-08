
import cpmpy as cp
import json

# Data
deck_width = 5  # Width of the deck
deck_length = 5  # Length of the deck
n_containers = 3  # Number of containers
width = [5, 2, 3]  # Widths of containers
length = [1, 4, 4]  # Lengths of containers
classes = [1, 1, 1]  # Classes of containers (1-based)
separation = [  # Separation constraints between classes (separation[a][b] is min separation for class a+1 vs b+1)
    [0, 0],
    [0, 0]
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# We'll allow left/top to range over whole deck and enforce right/bottom and bounds via constraints
left = cp.intvar(0, deck_width, shape=n_containers, name="left")
top = cp.intvar(0, deck_length, shape=n_containers, name="top")
right = cp.intvar(0, deck_width, shape=n_containers, name="right")
bottom = cp.intvar(0, deck_length, shape=n_containers, name="bottom")

# Constraints
for i in range(n_containers):
    # size constraints: right = left + width[i], bottom = top + length[i]
    model += (right[i] == left[i] + width[i])
    model += (bottom[i] == top[i] + length[i])
    # must fit on deck
    model += (right[i] <= deck_width)
    model += (bottom[i] <= deck_length)

# Non-overlap and separation constraints:
# For each pair i<j enforce that they are separated by at least separation[ci][cj] in either x or y direction
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        ci = classes[i] - 1  # convert to 0-based index for separation lookup
        cj = classes[j] - 1
        # separation required for this pair (as given). Interpretation: must be separated by at least s
        # along either x (width) or y (length) direction.
        s = int(separation[ci][cj])

        # Four possible disjuncts (i to left of j, j to left of i, i above j, j above i) with separation s
        b1 = cp.boolvar()  # right[i] + s <= left[j]
        b2 = cp.boolvar()  # right[j] + s <= left[i]
        b3 = cp.boolvar()  # bottom[i] + s <= top[j]
        b4 = cp.boolvar()  # bottom[j] + s <= top[i]

        model += b1.implies(right[i] + s <= left[j])
        model += b2.implies(right[j] + s <= left[i])
        model += b3.implies(bottom[i] + s <= top[j])
        model += b4.implies(bottom[j] + s <= top[i])

        # at least one separation direction must hold
        model += (cp.sum([b1, b2, b3, b4]) >= 1)

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
