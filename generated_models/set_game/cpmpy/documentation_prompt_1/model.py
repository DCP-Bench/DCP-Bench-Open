
import cpmpy as cp
import json

# Constants
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

# Make the card deck
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

n_cards = len(cards_data)

# Model definition
model = cp.Model()

# Decision variables: indices of the three cards forming the set
winning_cards = cp.intvar(0, n_cards-1, shape=3, name="winning_cards")

# Cards must be distinct
model += cp.AllDifferent(winning_cards)

# Extract features for the chosen cards
# cards_data is list of [number, fill, color, shape]
# We want to check the set condition for each feature across the 3 chosen cards

# For each feature index (0:number, 1:fill, 2:color, 3:shape)
# We create arrays of the feature values for the chosen cards
features = list(zip(*cards_data))  # 4 lists, each length n_cards

# For each feature, get the values of the chosen cards
chosen_features = []
for f in range(4):
    # Create an array of feature values for the chosen cards
    # Use Element constraint: chosen_features[f][i] = feature value of winning_cards[i]
    chosen_features.append(cp.intvar(1,3, shape=3, name=f"feat{f}"))
    for i in range(3):
        model += (chosen_features[f][i] == features[f][winning_cards[i]])

# For each feature, the three values must be all same or all different
for f in range(4):
    vals = chosen_features[f]
    # all same: vals[0] == vals[1] == vals[2]
    all_same = (vals[0] == vals[1]) & (vals[1] == vals[2])
    # all different: all distinct
    all_diff = cp.AllDifferent(vals)
    model += (all_same | all_diff)

# Solve and print
if model.solve():
    solution = {'winning_cards': winning_cards.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
