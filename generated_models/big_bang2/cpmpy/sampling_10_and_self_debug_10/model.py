
import cpmpy as cp
import json

# The 5 dice represent Rock(1), Paper(2), Scissors(3), Lizard(4), Spock(5)
# Each die has 6 faces, values between 1 and 99 (arbitrary large to avoid trivial ties)
# We want to assign values to dice so that the dice dominance matches the RPSSL rules.

# Beats relationships:
# 1 (Rock) beats 3 (Scissors) and 4 (Lizard)
# 2 (Paper) beats 1 (Rock) and 5 (Spock)
# 3 (Scissors) beats 2 (Paper) and 4 (Lizard)
# 4 (Lizard) beats 2 (Paper) and 5 (Spock)
# 5 (Spock) beats 1 (Rock) and 3 (Scissors)

# Model:
# For each pair (i,j) where i beats j:
#   count of (dice_i_face > dice_j_face) > count of (dice_i_face < dice_j_face)
#   ties do not count
# To break ties we want strict majority wins.

# Approach:
# We create dice as intvar arrays dice[i][face]
# Constraint: faces between 1 and 99
# Optional: faces sorted per die to reduce symmetries (non-decreasing order)
# Constraint: All dice faces are integers from 1 to 99

# Define dice
num_dice = 5
faces = 6

model = cp.Model()

# Dice values: dice[i][f] for i in 0..4, f in 0..5
dice = cp.intvar(1, 99, shape=(num_dice, faces), name="dice")

# Sort faces per die to reduce symmetry
for i in range(num_dice):
    model += cp.Increasing(dice[i])

# List of "beats" pairs: (winner, loser)
beats = [
    (0, 2),  # Rock(0) beats Scissors(2)
    (0, 3),  # Rock(0) beats Lizard(3)
    (1, 0),  # Paper(1) beats Rock(0)
    (1, 4),  # Paper(1) beats Spock(4)
    (2, 1),  # Scissors(2) beats Paper(1)
    (2, 3),  # Scissors(2) beats Lizard(3)
    (3, 1),  # Lizard(3) beats Paper(1)
    (3, 4),  # Lizard(3) beats Spock(4)
    (4, 0),  # Spock(4) beats Rock(0)
    (4, 2),  # Spock(4) beats Scissors(2)
]

# For each beat pair, count how many faces in winner die are greater than faces in loser die
# For each face pair (f1,f2), create boolvar win_face = dice[winner][f1] > dice[loser][f2]
# Then sum all win_face and sum all lose_face (reversed)
# Constraint: sum_win > sum_lose

for (w, l) in beats:
    win_count = []
    lose_count = []
    for f1 in range(faces):
        for f2 in range(faces):
            win_face = cp.boolvar()
            lose_face = cp.boolvar()
            # win_face = 1 if dice[w][f1] > dice[l][f2]
            model += (win_face == (dice[w, f1] > dice[l, f2]))
            # lose_face = 1 if dice[w][f1] < dice[l][f2]
            model += (lose_face == (dice[w, f1] < dice[l, f2]))
            win_count.append(win_face)
            lose_count.append(lose_face)
    model += cp.sum(win_count) > cp.sum(lose_count)

# Symmetry breaking: For example, sum faces of dice 0 < sum dice 1 < sum dice 2 < sum dice 3 < sum dice 4
sums = [cp.sum(dice[i]) for i in range(num_dice)]
for i in range(num_dice - 1):
    model += sums[i] < sums[i + 1]

# Solve and print dice
if model.solve():
    solution = {'dice': [dice[i].value().tolist() for i in range(num_dice)]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
