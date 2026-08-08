import json
from ortools.sat.python import cp_model

# ---------------------------------
# Constants and input data (fixed)
# ---------------------------------
TOTAL_WEIGHT = 40           # Total weight of the original 40-lb mass
NUM_PIECES   = 4            # The mass broke into exactly four pieces
TARGET_LOADS = range(1, 41) # Integral loads that must be weighable (1..40)

# ----------------------------
# Model construction
# ----------------------------
model = cp_model.CpModel()

# 1. Primary decision variables – the four unknown piece weights
weights = [model.NewIntVar(1, TOTAL_WEIGHT, f"w_{i}") for i in range(NUM_PIECES)]

# Symmetry-breaking – strictly increasing order
for i in range(NUM_PIECES - 1):
    model.Add(weights[i] < weights[i + 1])

# Total weight conservation
model.Add(sum(weights) == TOTAL_WEIGHT)

# 2. Auxiliary variables for each weighing task
#    contribution[t][i]  = actual signed contribution ( −w_i , 0 , or +w_i )
#    We also create three Boolean selector literals for each state (neg, zero, pos)
contribution = {}  # keyed by (t,i) → IntVar

for t in TARGET_LOADS:
    row = []
    for i in range(NUM_PIECES):
        # Three selector Booleans
        b_neg  = model.NewBoolVar(f"b_neg_t{t}_i{i}")
        b_zero = model.NewBoolVar(f"b_zero_t{t}_i{i}")
        b_pos  = model.NewBoolVar(f"b_pos_t{t}_i{i}")

        # Exactly one of the three states is chosen
        model.Add(b_neg + b_zero + b_pos == 1)

        # Contribution variable for (t,i)
        c = model.NewIntVar(-TOTAL_WEIGHT, TOTAL_WEIGHT, f"c_t{t}_i{i}")
        contribution[(t, i)] = c

        # Link contribution to the chosen state using enforcement literals
        model.Add(c == -weights[i]).OnlyEnforceIf(b_neg)
        model.Add(c == 0          ).OnlyEnforceIf(b_zero)
        model.Add(c ==  weights[i]).OnlyEnforceIf(b_pos)

        row.append(c)

    # Weighability constraint for target load t
    model.Add(sum(row) == t)

# ----------------------------
# Solve the model (feasibility)
# ----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # grace limit (optional)
status = solver.Solve(model)

# ----------------------------
# Output handling
# ----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_weights = [int(solver.Value(w)) for w in weights]
    print(json.dumps({"weights": solution_weights}))
else:
    # No solution found (theoretically impossible for this puzzle)
    print(json.dumps({"weights": []}))
