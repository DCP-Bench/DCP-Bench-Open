
import cpmpy as cp
import numpy as np
import json

# Data (optional)
# Constants
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

# Each card is [number, fill, color, shape]
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
cards_np = np.array(cards_data, dtype=int)
n_cards = cards_np.shape[0]
n_features = cards_np.shape[1]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
winning_cards = cp.intvar(0, n_cards-1, shape=3, name="winning_cards")  # 0-based indices
# Feature values of the selected cards: shape (3 cards, 4 features)
sel_feat = cp.intvar(1, 3, shape=(3, n_features), name="sel_feat")

# Constraints
# Distinct cards and symmetry breaking to avoid permutations
model += cp.AllDifferent(winning_cards)
model += cp.IncreasingStrict(winning_cards)

# Link selected indices to their feature values via Element constraints
for k in range(3):
    for d in range(n_features):
        col = cards_np[:, d]
        model += (sel_feat[k, d] == cp.Element(col, winning_cards[k]))

# For each feature, values across the three cards must be all equal or all different
for d in range(n_features):
    same = cp.AllEqual(list(sel_feat[:, d]))
    alldiff = cp.AllDifferent(sel_feat[:, d])
    model += (same | alldiff)

# Solve and print
if model.solve():
    solution = {'winning_cards': winning_cards.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
