from cpmpy import *
import json

# Parameters
n_dice = 5  # Number of dice
faces = 8  # Number of faces on each die

# Decision variables
dice = intvar(1, 100, shape=(n_dice, faces), name="dice")  # Each die has 8 faces with values from 1 to 100

# Model
model = Model()

# Each die must have 8 distinct values (no constraint on duplicates)
# No constraint on the values being from 1 to 5

# Define the beats relationships
beats = [
    (1, 3),  # Rock(1) beats Scissors(3)
    (1, 4),  # Rock(1) beats Lizard(4)
    (2, 1),  # Paper(2) beats Rock(1)
    (2, 5),  # Paper(2) beats Spock(5)
    (3, 2),  # Scissors(3) beats Paper(2)
    (3, 4),  # Scissors(3) beats Lizard(4)
    (4, 2),  # Lizard(4) beats Paper(2)
    (4, 5),  # Lizard(4) beats Spock(5)
    (5, 1),  # Spock(5) beats Rock(1)
    (5, 3)   # Spock(5) beats Scissors(3)
]

# For each (a, b) in beats, die a must beat die b
for a, b in beats:
    # Count how many times die a beats die b
    model += [sum((dice[a - 1, :] > dice[b - 1, :])) > sum((dice[b - 1, :] > dice[a - 1, :]))]

# Solve the model
model.solve()

# Print the solution
solution = {"dice": dice.value().tolist()}
print(json.dumps(solution))