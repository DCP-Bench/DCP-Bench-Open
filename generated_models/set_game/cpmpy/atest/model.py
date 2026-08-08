from cpmpy import *
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

# Parameters
n_cards = len(cards_data)

# Decision variables
winning_cards = boolvar(shape=n_cards, name="winning_cards")

# Model
model = Model()

# Exactly three cards must be selected
model += [sum(winning_cards) == 3]

# For each feature (number, color, shape, fill), the three selected cards must be either all the same or all different
for feature_index in range(4):  # 4 features: number, color, shape, fill
    # Extract the feature values for all cards
    feature_values = [cards_data[i][feature_index] for i in range(n_cards)]
    
    # Create a variable for the feature value of the selected cards
    selected_values = intvar(1, 3, shape=n_cards)
    
    # Assign the feature values to the selected_values variable
    for i in range(n_cards):
        model += [selected_values[i] == feature_values[i]]
    
    # If a card is not selected, its feature value is irrelevant
    for i in range(n_cards):
        model += [(selected_values[i] == 0) | (winning_cards[i] == 0)]
    
    # All selected cards must have the same feature value or all different feature values
    # All same
    for i in range(n_cards):
        for j in range(i + 1, n_cards):
            model += [(selected_values[i] == selected_values[j]) | (winning_cards[i] == 0) | (winning_cards[j] == 0)]
    
    # All different
    for i in range(n_cards):
        for j in range(i + 1, n_cards):
            for k in range(j + 1, n_cards):
                model += [(selected_values[i] != selected_values[j]) | (winning_cards[i] == 0) | (winning_cards[j] == 0)]
                model += [(selected_values[i] != selected_values[k]) | (winning_cards[i] == 0) | (winning_cards[k] == 0)]
                model += [(selected_values[j] != selected_values[k]) | (winning_cards[j] == 0) | (winning_cards[k] == 0)]

# Solve the model
model.solve()

# Print the solution
solution = {"winning_cards": winning_cards.value().tolist()}
print(json.dumps(solution))