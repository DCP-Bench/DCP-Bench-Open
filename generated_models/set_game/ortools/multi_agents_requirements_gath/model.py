import json
from ortools.sat.python import cp_model

# -----------------------------
# 1. Parse the EXACT input data
# -----------------------------
# Constants (the numerical encodings themselves are irrelevant as long as they
# are consistent throughout the model).
ONE, TWO, THREE = 1, 2, 3
RED, PURPLE, GREEN = 1, 2, 3
DIAMOND, RECT, ELLIPSE = 1, 2, 3
FULL, EMPTY, STRIPED = 1, 2, 3

# Card attributes: [number, fill, colour, shape]
cards_data = [
    [ONE,   EMPTY,   GREEN,   DIAMOND],
    [TWO,   STRIPED, RED,     RECT],
    [THREE, STRIPED, GREEN,   DIAMOND],
    [THREE, FULL,    RED,     DIAMOND],
    [ONE,   STRIPED, GREEN,   DIAMOND],
    [ONE,   EMPTY,   RED,     DIAMOND],
    [TWO,   FULL,    PURPLE,  DIAMOND],
    [THREE, FULL,    PURPLE,  ELLIPSE],
    [THREE, FULL,    GREEN,   RECT],
    [ONE,   FULL,    PURPLE,  DIAMOND],
    [ONE,   STRIPED, PURPLE,  DIAMOND],
    [ONE,   FULL,    GREEN,   RECT],
]

n_cards = len(cards_data)                # 12
n_features = 4                           # number, fill, colour, shape
feature_values = [1, 2, 3]               # every feature can take 1..3

# -----------------------------
# 2. Build the CP-SAT model
# -----------------------------
model = cp_model.CpModel()

# Decision variables – 1 iff card i is chosen
x = [model.NewBoolVar(f"x_{i}") for i in range(n_cards)]

# (C1) Exactly three cards form the set
model.Add(sum(x) == 3)

# For every feature f and value v create a counting variable
for f in range(n_features):
    for v in feature_values:
        y_f_v = model.NewIntVar(0, 3, f"y_{f}_{v}")

        # y_f_v = Σ selected cards whose feature-value equals v
        matching = [x[i] for i in range(n_cards) if cards_data[i][f] == v]
        if matching:                          # at least one candidate card
            model.Add(y_f_v == sum(matching))
        else:                                 # no card on the table shows this value
            model.Add(y_f_v == 0)

        # (C2) For a legal SET a feature may never appear exactly twice
        #      among the three selected cards.
        model.Add(y_f_v != 2)

# No objective – pure feasibility

# -----------------------------
# 3. Invoke the solver
# -----------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# -----------------------------
# 4. Extract and print solution
# -----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    winning_cards = [i for i in range(n_cards) if solver.Value(x[i]) == 1]
else:
    winning_cards = []

print(json.dumps({"winning_cards": winning_cards}))
