
import cpmpy as cp
import json

# Data
n = 10  # total people (Hilary(0) and Jocelyn(1) plus 4 other couples)
hil_index = 0
jocelyn_index = 1
couples = [(0,1),(2,3),(4,5),(6,7),(8,9)]

# Model definition
model = cp.Model()

# Decision Variables
# Handshake matrix: H[i,j] = 1 if i shook j's hand, else 0
H = cp.boolvar(shape=(n, n), name="H")

# Number of hands each person shook: 0..8 (can't shake self or spouse)
hands = cp.intvar(0, 8, shape=n, name="hands")

# Constraints
# No one shakes their own hand
for i in range(n):
    model += (H[i, i] == 0)

# Symmetry: if i shakes j then j shakes i
for i in range(n):
    for j in range(i + 1, n):
        model += (H[i, j] == H[j, i])

# No one shakes their spouse's hand
for (a, b) in couples:
    model += (H[a, b] == 0)
    model += (H[b, a] == 0)

# Define hands as the row sums of H
for i in range(n):
    model += (hands[i] == cp.sum(H[i, :]))

# Jocelyn asks everyone else (not herself) and gets all different answers.
# So the counts of the other 9 people are all different (hence 0..8).
others = [i for i in range(n) if i != jocelyn_index]
model += cp.AllDifferent([hands[i] for i in others])

# Solve and print
if model.solve():
    solution = {'hil': int(hands[hil_index].value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
