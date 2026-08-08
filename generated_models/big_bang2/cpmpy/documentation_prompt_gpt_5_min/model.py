
import cpmpy as cp
import json

# Data
rock = 0
paper = 1
scissors = 2
lizard = 3
spock = 4

m = 5  # number of dice
n = 6  # faces per die
f = 2 * n  # max face value

edge = [
    [rock, scissors],  # 1: Rock crushes Scissors
    [rock, lizard],  # etc.
    [paper, rock],
    [paper, spock],
    [scissors, paper],
    [scissors, lizard],
    [lizard, paper],
    [lizard, spock],
    [spock, rock],
    [spock, scissors]
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: dice values between 1 and f inclusive
dice = cp.intvar(1, f, shape=(m, n), name="dice")

# Constraints
# 1) For readability / symmetry-breaking: faces of each die in non-decreasing order
for i in range(m):
    model += cp.Increasing(dice[i, :])

# 2) For each directed 'beats' edge (a beats b) require:
#    number of ordered face pairs (i,j) with dice[a,i] > dice[b,j] is strictly greater
#    than the number with dice[a,i] < dice[b,j] (i.e., wins >= losses + 1).
for (a, b) in edge:
    wins = cp.sum([dice[a, i] > dice[b, j] for i in range(n) for j in range(n)])
    losses = cp.sum([dice[a, i] < dice[b, j] for i in range(n) for j in range(n)])
    model += wins >= losses + 1

# No objective, just find a feasible set of dice
if model.solve():
    solution = {'dice': dice.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
