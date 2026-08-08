from ortools.sat.python import cp_model
import json

# Constants
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

# Card deck data: [number, fill, color, shape]
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

# Model definition
model = cp_model.CpModel()

# Decision variables: indices of the three cards forming the set
card_indices = [model.NewIntVar(0, num_cards - 1, f'card_{i}') for i in range(3)]

# All three cards must be different
model.AddAllDifferent(card_indices)

# Helper function to get feature values for a card index variable
def feature_values(feature_idx):
    # feature_idx: 0=number,1=fill,2=color,3=shape
    return [cards_data[i][feature_idx] for i in range(num_cards)]

# For each feature, the three cards must be all same or all different
for feature_idx in range(4):
    # Extract feature values for all cards
    feature_vals = feature_values(feature_idx)
    # Create variables for the feature values of the chosen cards
    f_vars = [model.NewIntVar(1, 3, f'feature_{feature_idx}_card_{i}') for i in range(3)]
    for i in range(3):
        # Link card index to feature value using Element constraint
        model.AddElement(card_indices[i], feature_vals, f_vars[i])
    # Constraint: either all same or all different
    # all same: f_vars[0] == f_vars[1] == f_vars[2]
    all_same = model.NewBoolVar(f'all_same_feature_{feature_idx}')
    model.Add(f_vars[0] == f_vars[1]).OnlyEnforceIf(all_same)
    model.Add(f_vars[1] == f_vars[2]).OnlyEnforceIf(all_same)
    model.AddBoolAnd([f_vars[0] == f_vars[1], f_vars[1] == f_vars[2]]).OnlyEnforceIf(all_same)
    model.AddBoolOr([f_vars[0] != f_vars[1], f_vars[1] != f_vars[2], f_vars[0] != f_vars[2]]).OnlyEnforceIf(all_same.Not())

    # all different: all three different
    all_diff = model.NewBoolVar(f'all_diff_feature_{feature_idx}')
    model.AddAllDifferent(f_vars).OnlyEnforceIf(all_diff)
    model.AddBoolOr([f_vars[0] == f_vars[1], f_vars[1] == f_vars[2], f_vars[0] == f_vars[2]]).OnlyEnforceIf(all_diff.Not())

    # Exactly one of all_same or all_diff must be true
    model.AddBoolXOr([all_same, all_diff])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    winning_cards = [solver.Value(card_indices[i]) for i in range(3)]
    solution = {'winning_cards': winning_cards}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")