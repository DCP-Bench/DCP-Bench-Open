
from ortools.sat.python import cp_model
import json

# Input data
ONE, TWO, THREE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3

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

# Model definition
model = cp_model.CpModel()
num_cards = len(cards_data)

# Decision variables: indices of the three winning cards
win0 = model.NewIntVar(0, num_cards - 1, 'win0')
win1 = model.NewIntVar(0, num_cards - 1, 'win1')
win2 = model.NewIntVar(0, num_cards - 1, 'win2')

# Enforce an ordering to avoid symmetric solutions
model.Add(win0 < win1)
model.Add(win1 < win2)

# For each feature (0:number, 1:shading, 2:color, 3:shape),
# extract the feature values and impose the SET constraints
for f in range(4):
    # Build a list of that feature's values across all cards
    feature_list = [cards_data[i][f] for i in range(num_cards)]
    
    # Variables for the feature values of the chosen cards
    v0 = model.NewIntVar(1, 3, f'v0_{f}')
    v1 = model.NewIntVar(1, 3, f'v1_{f}')
    v2 = model.NewIntVar(1, 3, f'v2_{f}')
    
    # Link card indices to their feature values via element constraints
    model.AddElement(win0, feature_list, v0)
    model.AddElement(win1, feature_list, v1)
    model.AddElement(win2, feature_list, v2)
    
    # Boolean indicators: either all the same or all different
    all_same = model.NewBoolVar(f'all_same_{f}')
    all_diff = model.NewBoolVar(f'all_diff_{f}')
    
    # Exactly one of the two conditions must hold
    model.Add(all_same + all_diff == 1)
    
    # If all_same, enforce pairwise equalities
    model.Add(v0 == v1).OnlyEnforceIf(all_same)
    model.Add(v1 == v2).OnlyEnforceIf(all_same)
    
    # If all_diff, enforce pairwise inequalities
    model.Add(v0 != v1).OnlyEnforceIf(all_diff)
    model.Add(v0 != v2).OnlyEnforceIf(all_diff)
    model.Add(v1 != v2).OnlyEnforceIf(all_diff)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the result
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'winning_cards': [
            solver.Value(win0),
            solver.Value(win1),
            solver.Value(win2)
        ]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
