from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Constants
num_dice = 5
faces_per_die = 6
max_face_value = 30  # Arbitrary upper bound for face values to allow spacing

# Dice indices for readability
ROCK = 0
PAPER = 1
SCISSORS = 2
LIZARD = 3
SPOCK = 4

# Beats relationships as pairs (winner, loser)
beats = [
    (ROCK, SCISSORS),
    (ROCK, LIZARD),
    (PAPER, ROCK),
    (PAPER, SPOCK),
    (SCISSORS, PAPER),
    (SCISSORS, LIZARD),
    (LIZARD, PAPER),
    (LIZARD, SPOCK),
    (SPOCK, ROCK),
    (SPOCK, SCISSORS),
]

# Decision variables: dice[i][j] is the j-th face of the i-th die
dice = []
for i in range(num_dice):
    die = [model.NewIntVar(1, max_face_value, f'dice_{i}_face_{j}') for j in range(faces_per_die)]
    dice.append(die)

# Constraint: Faces within each die are all different (to avoid trivial ties)
for die in dice:
    model.AddAllDifferent(die)

# To model the dominance relationships, we consider the probability that one die beats another.
# For dice A and B, the probability that A beats B is:
# (number of pairs (a,b) with a > b) / 36 (since 6 faces each)
# We want for each (winner, loser) pair that winner beats loser with probability > 0.5

# Auxiliary variables: for each pair of dice and each pair of faces, a boolean indicating if face_i > face_j
# We'll create these for each beats pair only to reduce variables

# We will create variables for each beats pair:
# count_winner_beats_loser = sum over faces of winner and loser of indicator(winner_face > loser_face)
# Constraint: count_winner_beats_loser > 18 (since 36 pairs, > 0.5 means > 18)

for (winner, loser) in beats:
    # Create boolean variables for each face pair comparison
    bool_vars = []
    for i in range(faces_per_die):
        for j in range(faces_per_die):
            b = model.NewBoolVar(f'w{winner}_f{i}_gt_l{loser}_f{j}')
            # b == 1 if dice[winner][i] > dice[loser][j]
            model.Add(dice[winner][i] > dice[loser][j]).OnlyEnforceIf(b)
            model.Add(dice[winner][i] <= dice[loser][j]).OnlyEnforceIf(b.Not())
            bool_vars.append(b)
    # Sum of bool_vars > 18 to ensure winner beats loser with probability > 0.5
    model.Add(sum(bool_vars) > 18)

# Optional: To reduce symmetry, order faces within each die ascending
for die in dice:
    for i in range(faces_per_die - 1):
        model.Add(die[i] < die[i + 1])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'dice': [[solver.Value(face) for face in die] for die in dice]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")