
import cpmpy as cp
import json

# Data (from problem)
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

cards_data = [  # Each card is represented as a list of [number, fill, color, shape]
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
# End of data

n = len(cards_data)

# Build separate lists for each feature (index order in card: number, fill, color, shape)
numbers = [c[0] for c in cards_data]
fills   = [c[1] for c in cards_data]
colors  = [c[2] for c in cards_data]
shapes  = [c[3] for c in cards_data]
features = [numbers, fills, colors, shapes]

# Model definition
model = cp.Model()

# Decision Variables: three 0-based indices of the winning set (enforce increasing to avoid symmetry)
winning_cards = cp.intvar(0, n-1, shape=3, name="winning_cards")

# Distinct and ordered indices
model += winning_cards[0] < winning_cards[1]
model += winning_cards[1] < winning_cards[2]

# For each feature, forbid the pattern "exactly two equal and the third different".
# This enforces for each feature that the three values are either all equal or all different.
for feat in features:
    v0 = cp.Element(feat, winning_cards[0])
    v1 = cp.Element(feat, winning_cards[1])
    v2 = cp.Element(feat, winning_cards[2])
    # forbid (v0==v1 and v2 different) or (v0==v2 and v1 different) or (v1==v2 and v0 different)
    two_equal_one_diff = ((v0 == v1) & (v1 != v2)) | ((v0 == v2) & (v2 != v1)) | ((v1 == v2) & (v2 != v0))
    model += ~two_equal_one_diff

# No objective
# Solve and print
if model.solve():
    solution = {'winning_cards': winning_cards.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
