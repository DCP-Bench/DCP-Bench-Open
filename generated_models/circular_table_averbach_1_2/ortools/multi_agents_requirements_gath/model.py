# Complete, runnable Python program that solves the Hearts nationality logic puzzle
# and prints the answer as JSON with the required keys.

from ortools.sat.python import cp_model
import json

# ------------------------------
# Model creation
# ------------------------------
model = cp_model.CpModel()

# Index mapping (used for readability)
# Players: 0 -> X, 1 -> Y, 2 -> Z
# Nationalities: 0 -> American, 1 -> English, 2 -> French

# Decision variables -------------------------------------------------
# Nationality of each player
x = model.NewIntVar(0, 2, 'x')        # nationality index of player X
y = model.NewIntVar(0, 2, 'y')        # nationality index of player Y
z = model.NewIntVar(0, 2, 'z')        # nationality index of player Z

# Player who has a given nationality
american = model.NewIntVar(0, 2, 'american')
english  = model.NewIntVar(0, 2, 'english')
french   = model.NewIntVar(0, 2, 'french')

# Convenience lists to channel later
nat_of_player = [x, y, z]                  # index by player -> nationality
player_of_nat = [american, english, french] # index by nationality -> player

# ------------------------------
# Constraints
# ------------------------------
# 1) All different nationalities for players
model.AddAllDifferent(nat_of_player)

# 2) All different players for each nationality
model.AddAllDifferent(player_of_nat)

# 3) Mutual inverse consistency using element constraints
for p in range(3):
    # player p's nationality tells which entry of player_of_nat must equal p
    # player_of_nat[ nat_of_player[p] ] == p
    model.AddElement(nat_of_player[p], player_of_nat, model.NewConstant(p))

# 4) Clue #1: Y passed three hearts to the American -> X is the American
model.Add(x == 0)  # player X has nationality American

# 5) Clue #2: X passed to the person who passed to the Frenchwoman -> Y is French
model.Add(y == 2)  # player Y has nationality French

# No optimisation objective – feasibility problem only.

# ------------------------------
# Solve
# ------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise ValueError("No solution found for the given puzzle constraints.")

# ------------------------------
# Extract and print solution in required JSON order
# Required order: ['y', 'english', 'american', 'french', 'x', 'z']
# ---------------------------------------------------------------
result = {
    'y':        solver.Value(y),
    'english':  solver.Value(english),
    'american': solver.Value(american),
    'french':   solver.Value(french),
    'x':        solver.Value(x),
    'z':        solver.Value(z)
}

print(json.dumps(result))
