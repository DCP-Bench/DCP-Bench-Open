import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# SET game rules: For each of the 4 features (number, fill, color, shape),
# the three selected cards must have either ALL SAME or ALL DIFFERENT values
# Cannot have exactly 2 cards with one value and 1 card with another value

# Constants
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

# Card deck - each card has [number, fill, color, shape]
cards_data = [
    [ONE, EMPTY, GREEN, DIAMOND],     # 0
    [TWO, STRIPED, RED, RECT],        # 1
    [THREE, STRIPED, GREEN, DIAMOND], # 2
    [THREE, FULL, RED, DIAMOND],      # 3
    [ONE, STRIPED, GREEN, DIAMOND],   # 4
    [ONE, EMPTY, RED, DIAMOND],       # 5
    [TWO, FULL, PURPLE, DIAMOND],     # 6
    [THREE, FULL, PURPLE, ELLIPSE],   # 7
    [THREE, FULL, GREEN, RECT],       # 8
    [ONE, FULL, PURPLE, DIAMOND],     # 9
    [ONE, STRIPED, PURPLE, DIAMOND],  # 10
    [ONE, FULL, GREEN, RECT]          # 11
]

n_cards = len(cards_data)
n_features = 4

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: select exactly 3 cards
selected = cp.boolvar(shape=n_cards, name="selected")

# Constraint: exactly 3 cards selected
model += cp.sum(selected) == 3

# For each feature, enforce SET rules
for feature_idx in range(n_features):
    # Get the feature values for all cards
    feature_values = [cards_data[i][feature_idx] for i in range(n_cards)]
    
    # Get all possible values for this feature
    possible_values = sorted(set(feature_values))  # [1, 2, 3] for most features
    
    # Binary variables: value_used[v] = 1 if value v appears in selected cards
    value_used = cp.boolvar(shape=len(possible_values), name=f"value_used_feature_{feature_idx}")
    
    # Link value_used to selected cards
    for v_idx, value in enumerate(possible_values):
        # value_used[v_idx] = 1 iff at least one selected card has this value for this feature
        cards_with_value = [i for i in range(n_cards) if feature_values[i] == value]
        model += value_used[v_idx] == (cp.sum([selected[i] for i in cards_with_value]) >= 1)
    
    # Count how many different values are used
    num_different_values = cp.sum(value_used)
    
    # SET rule: Must be either 1 (all same) or 3 (all different), cannot be 2
    model += (num_different_values == 1) | (num_different_values == 3)

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    selected_indices = [i for i in range(n_cards) if selected.value()[i] == 1]
    
    solution = {
        "winning_cards": selected_indices
    }
    
    # Verification - independent check of SET rules
    def verify_solution(sol):
        """Verify the solution independently"""
        winning_cards = sol["winning_cards"]
        
        # Structural verification
        if len(winning_cards) != 3:
            return False, f"Must select exactly 3 cards, got {len(winning_cards)}"
        
        if not all(0 <= idx < n_cards for idx in winning_cards):
            return False, f"Invalid card indices: {winning_cards}"
        
        # Logical verification - check SET rules
        cards = [cards_data[idx] for idx in winning_cards]
        
        for feature_idx in range(n_features):
            values = [cards[i][feature_idx] for i in range(3)]
            unique_values = set(values)
            
            # Must be either all same (1 unique) or all different (3 unique)
            if len(unique_values) == 2:
                return False, f"Feature {feature_idx} violates SET rules: {values}"
        
        return True, "Valid SET found"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))