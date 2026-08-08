from cpmpy import *
import json

# Constants
numbers = [1, 2, 3]  # ONE, TWO, THREE
colors = [1, 2, 3]    # RED, PURPLE, GREEN
shapes = [1, 2, 3]    # DIAMOND, RECT, ELLIPSE
fills = [1, 2, 3]     # FULL, EMPTY, STRIPED

# Card deck
cards_data = [
    [1, 2, 3, 1],  # ONE, EMPTY, GREEN, DIAMOND
    [2, 3, 1, 2],  # TWO, STRIPED, RED, RECT
    [3, 3, 3, 1],  # THREE, STRIPED, GREEN, DIAMOND
    [3, 1, 1, 1],  # THREE, FULL, RED, DIAMOND
    [1, 3, 3, 1],  # ONE, STRIPED, GREEN, DIAMOND
    [1, 2, 1, 1],  # ONE, EMPTY, RED, DIAMOND
    [2, 1, 2, 1],  # TWO, FULL, PURPLE, DIAMOND
    [3, 1, 2, 3],  # THREE, FULL, PURPLE, ELLIPSE
    [3, 1, 3, 2],  # THREE, FULL, GREEN, RECT
    [1, 1, 2, 1],  # ONE, FULL, PURPLE, DIAMOND
    [1, 3, 2, 1],  # ONE, STRIPED, PURPLE, DIAMOND
    [1, 1, 3, 2]   # ONE, FULL, GREEN, RECT
]

# Decision Variables
winning_cards = intvar(0, len(cards_data)-1, shape=3, name="winning_cards")

# Model
model = Model()

# Constraint: All cards must be distinct
model += AllDifferent(winning_cards)

# For each feature, check if all same or all different
for feature_idx in range(4):  # 4 features: number, color, shape, fill
    # Get the feature values for the three cards
    f0 = intvar(1,3)
    f1 = intvar(1,3)
    f2 = intvar(1,3)
    
    # Link feature variables to actual card data
    model += (f0 == cards_data[winning_cards[0]][feature_idx])
    model += (f1 == cards_data[winning_cards[1]][feature_idx])
    model += (f2 == cards_data[winning_cards[2]][feature_idx])
    
    # Either all same or all different
    model += (
        ((f0 == f1) & (f1 == f2)) |
        (AllDifferent([f0, f1, f2]))
    )

# Solve
model.solve()

# Print solution
solution = {
    "winning_cards": winning_cards.value().tolist()
}
print(json.dumps(solution))