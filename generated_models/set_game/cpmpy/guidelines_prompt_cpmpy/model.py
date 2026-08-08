
import cpmpy as cp
import json
import numpy as np

# Input data
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

cards_data = [
    [ONE, EMPTY, GREEN, DIAMOND],
    [TWO, STRIPED, RED, RECT],
    [THREE, STRIPED, GREEN, DIAMOND],
    [THREE, FULL, RED, DIAMOND],
    [ONE, STRIPED, GREEN, DIAMOND],
    [ONE, EMPTY, RED, DIAMOND],
    [TWO, FULL, PURPLE, DIAMOND],
    [THREE, FULL, PURPLE, ELLIPSE],
    [THREE, FULL, GREEN, RECT],
    [ONE, FULL, PURPLE, DIAMOND],
    [ONE, STRIPED, PURPLE, DIAMOND],
    [ONE, FULL, GREEN, RECT]
]
card_features = np.array(cards_data)

# Model definition
model = cp.Model()

n = card_features.shape[0]
# Decision variables: indices of the three cards
i = cp.IntVar(0, n-1, name="i")
j = cp.IntVar(0, n-1, name="j")
k = cp.IntVar(0, n-1, name="k")

# Enforce distinct and ordered indices to avoid symmetry
model += [i < j, j < k]

# For each feature (number, shading, color, shape), enforce the "set" condition:
# sum of the three values mod 3 == 0  <=> either all same or all different
for f in range(4):
    col = card_features[:, f]
    v_i = cp.element(col, i)
    v_j = cp.element(col, j)
    v_k = cp.element(col, k)
    model += (v_i + v_j + v_k) % 3 == 0

# Solve and print
if model.solve():
    solution = {
        'winning_cards': [int(i.value()), int(j.value()), int(k.value())]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
