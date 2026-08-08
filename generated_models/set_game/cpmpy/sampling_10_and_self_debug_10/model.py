
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

num_cards = len(cards_data)
num_features = 4  # number, fill, color, shape

# Model definition
model = cp.Model()

# Decision variables: indices of the three chosen cards (distinct)
winning_cards = cp.intvar(0, num_cards-1, shape=3, name="winning_cards")
model += cp.AllDifferent(winning_cards)

# Extract features as separate lists for easier access
numbers = [card[0] for card in cards_data]
fills = [card[1] for card in cards_data]
colors = [card[2] for card in cards_data]
shapes = [card[3] for card in cards_data]

# For each feature, the three cards must be all the same or all different
def all_same_or_all_diff(x):
    # x is a list of 3 intvars
    return (x[0] == x[1]) & (x[1] == x[2]) | ( (x[0] != x[1]) & (x[1] != x[2]) & (x[0] != x[2]) )

for feature_vals in [numbers, fills, colors, shapes]:
    # create variables for the feature values of the three chosen cards
    fvals = [cp.Element(feature_vals, winning_cards[i]) for i in range(3)]
    model += all_same_or_all_diff(fvals)

# Solve and print
if model.solve():
    solution = {'winning_cards': winning_cards.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
