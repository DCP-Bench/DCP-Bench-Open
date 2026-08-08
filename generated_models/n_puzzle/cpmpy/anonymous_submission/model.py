# Import libraries
from cpmpy import *
import json
import numpy as np

# Parameters
N = 20  # Number of steps to the solution
puzzle_start = [  # Start state of the puzzle, 0 represents the empty tile
    [0, 3, 6],
    [2, 4, 8],
    [1, 7, 5]
]
puzzle_end = [  # End state of the puzzle
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# Decision Variables
# Represent each step as a 3x3 matrix of integers (0-8)
steps = intvar(0, 8, shape=(N+1, 3, 3), name="steps")

# Model
model = Model()

# Initial state constraint
for i in range(3):
    for j in range(3):
        model += steps[0][i][j] == puzzle_start[i][j]

# Final state constraint
for i in range(3):
    for j in range(3):
        model += steps[N][i][j] == puzzle_end[i][j]

# Transition constraints between steps
for step in range(N):
    # Exactly one empty tile in each step
    model += sum(steps[step] == 0) == 1
    model += sum(steps[step+1] == 0) == 1
    
    # Find possible moves (adjacent swaps)
    for i in range(3):
        for j in range(3):
            # If current position is empty in next step, it must have swapped with an adjacent tile
            model += (steps[step+1][i][j] == 0).implies(
                sum([(steps[step][k][l] == 0) & 
                     ((abs(i-k) + abs(j-l)) == 1) for k in range(3) for l in range(3)]) == 1)
            
            # The tile that moved must come from adjacent position
            for k in range(3):
                for l in range(3):
                    if (abs(i-k) + abs(j-l)) == 1:  # adjacent positions
                        # If tile moved from (k,l) to (i,j)
                        model += ((steps[step][k][l] == 0) & (steps[step+1][i][j] == 0)).implies(
                            steps[step+1][k][l] == steps[step][i][j])
    
    # All non-moving tiles must stay the same
    for i in range(3):
        for j in range(3):
            model += ((steps[step][i][j] != 0) & (steps[step+1][i][j] != 0)).implies(
                steps[step][i][j] == steps[step+1][i][j])

# Solve
model.solve()

# Print solution
solution = {"steps": np.array(steps.value()).tolist()}
print(json.dumps(solution))
# End of CPMPy script