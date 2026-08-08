
import cpmpy as cp
import json

# Constants
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

# Card data
cards_data = [
    [ONE, EMPTY, GREEN, DIAMOND],    # 0
    [TWO, STRIPED, RED, RECT],       # 1
    [THREE, STRIPED, GREEN, DIAMOND],# 2
    [THREE, FULL, RED, DIAMOND],     # 3
    [ONE, STRIPED, GREEN, DIAMOND],  # 4
    [ONE, EMPTY, RED, DIAMOND],      # 5
    [TWO, FULL, PURPLE, DIAMOND],    # 6
    [THREE, FULL, PURPLE, ELLIPSE],  # 7
    [THREE, FULL, GREEN, RECT],      # 8
    [ONE, FULL, PURPLE, DIAMOND],    # 9
    [ONE, STRIPED, PURPLE, DIAMOND], #10
    [ONE, FULL, GREEN, RECT]         #11
]

# Convert features to Python lists (not numpy arrays)
number_features = [card[0] for card in cards_data]
fill_features = [card[1] for card in cards_data]
color_features = [card[2] for card in cards_data]
shape_features = [card[3] for card in cards_data]

# Decision variables: indices of three distinct cards (i < j < k)
i = cp.intvar(0, len(cards_data)-1, name="i")
j = cp.intvar(0, len(cards_data)-1, name="j")
k = cp.intvar(0, len(cards_data)-1, name="k")

model = cp.Model()

# Constraints for indices
model += [i < j, j < k]

# Function to add feature constraints
def add_feature_constraints(feature_list):
    a = feature_list[i]  # Valid list indexing creates Element constraint
    b = feature_list[j]
    c = feature_list[k]
    # Must be all same (NValue=1) or all different (NValue=3)
    model += (cp.NValue([a, b, c]) == 1) | (cp.NValue([a, b, c]) == 3)

# Apply constraints to all features
add_feature_constraints(number_features)
add_feature_constraints(fill_features)
add_feature_constraints(color_features)
add_feature_constraints(shape_features)

# Solve and print
if model.solve():
    solution = {'winning_cards': [int(i.value()), int(j.value()), int(k.value())]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
