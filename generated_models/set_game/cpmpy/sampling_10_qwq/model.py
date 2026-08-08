
import cpmpy as cp
import json

# Data (optional)
numbers = ONE, TWO, THREE = 1, 2, 3
colors = RED, PURPLE, GREEN = 1, 2, 3
shapes = DIAMOND, RECT, ELLIPSE = 1, 2, 3
fills = FULL, EMPTY, STRIPED = 1, 2, 3

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

# Model definition
model = cp.Model()

# Decision Variables
n_cards = len(cards_data)
card_indices = cp.intvar(0, n_cards -1, shape=3, name="card_indices")

# Ensure all indices are different
model += cp.AllDifferent(card_indices)

# Precompute feature arrays for each of the four features (number, fill, color, shape)
feature_arrays = []
for f in range(4):
    feature_values = [card[f] for card in cards_data]
    feature_arrays.append(feature_values)

# Constraints for each feature
for f in range(4):
    arr = feature_arrays[f]
    v0 = cp.Element(arr, card_indices[0])
    v1 = cp.Element(arr, card_indices[1])
    v2 = cp.Element(arr, card_indices[2])

    all_same = (v0 == v1) & (v1 == v2)
    all_diff = (v0 != v1) & (v0 != v2) & (v1 != v2)
    model += (all_same | all_diff)

# Solve and print
if model.solve():
    solution = {'winning_cards': card_indices.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
