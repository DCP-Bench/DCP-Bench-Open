
import cpmpy as cp
import json

# Data
rock = 0
paper = 1
scissors = 2
lizard = 3
spock = 4

m = 5  # number of dice
n = 6  # number of faces of each die
f = 2 * n  # max face value of dice
edge = [
    [rock, scissors],  # 1: Rock crushes Scissors
    [rock, lizard],    # 2: Rock crushes Lizard
    [paper, rock],     # 3: Paper covers Rock
    [paper, spock],    # 4: Paper disproves Spock
    [scissors, paper], # 5: Scissors cuts Paper
    [scissors, lizard],# 6: Scissors decapitate Lizard
    [lizard, paper],   # 7: Lizard eats Paper
    [lizard, spock],   # 8: Lizard poisons Spock
    [spock, rock],     # 9: Spock vaporizes Rock
    [spock, scissors]  # 10: Spock smashes Scissors
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# dice[d][i] is the i-th face of die d
dice = cp.intvar(1, f, shape=(m, n), name="dice")

# wins[a][b] is the number of (i,j) pairs where die a's face > die b's face
wins = cp.intvar(0, n*n, shape=(m, m), name="wins")

# Constraints

# Symmetry breaking within each die: sort faces non-decreasing
for d in range(m):
    model += cp.Increasing(dice[d])

# Define wins counts for all ordered pairs (a,b)
for a in range(m):
    for b in range(m):
        if a == b:
            model += (wins[a, b] == 0)
        else:
            gt_pairs = [dice[a, i] > dice[b, j] for i in range(n) for j in range(n)]
            model += (wins[a, b] == cp.sum(gt_pairs))

# Enforce the "beats" relationships:
# For each directed edge (a beats b), require strictly more than half of the pairings
# i.e., wins[a][b] >= 19 when n=6 (since 6*6=36, strictly more than 18)
half_plus_one = (n * n) // 2 + 1  # 19 for n=6
for (a, b) in edge:
    model += (wins[a, b] >= half_plus_one)

# Objective (none, satisfiability problem)

# Solve and print
if model.solve():
    solution = {'dice': dice.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
