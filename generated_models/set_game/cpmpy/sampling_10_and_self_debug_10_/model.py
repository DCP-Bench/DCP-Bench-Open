
import cpmpy as cp
import json

# Data (from the problem)
numbers = ONE, TWO, THREE = 1, 2, 3
colors = RED, PURPLE, GREEN = 1, 2, 3
shapes = DIAMOND, RECT, ELLIPSE = 1, 2, 3
fills = FULL, EMPTY, STRIPED = 1, 2, 3

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

# Model definition
model = cp.Model()

# Decision Variables: three indices into the cards (0-based)
winning_cards = cp.intvar(0, len(cards_data)-1, shape=3, name="winning_cards")

# Enforce strictly increasing indices to avoid symmetries and ensure distinct cards
model += cp.IncreasingStrict(winning_cards)

# Prepare feature arrays for element access: order is [number, fill, color, shape]
feature_lists = [
    [card[0] for card in cards_data],  # number
    [card[1] for card in cards_data],  # fill
    [card[2] for card in cards_data],  # color
    [card[3] for card in cards_data],  # shape
]

# For each feature, the three selected cards must be all the same OR all different
for feat in feature_lists:
    v0 = cp.Element(feat, winning_cards[0])
    v1 = cp.Element(feat, winning_cards[1])
    v2 = cp.Element(feat, winning_cards[2])
    all_same = (v0 == v1) & (v1 == v2)
    all_diff = (v0 != v1) & (v0 != v2) & (v1 != v2)
    model += (all_same | all_diff)

# No objective; just find any valid set

# Solve and print
if model.solve():
    solution = {'winning_cards': winning_cards.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
