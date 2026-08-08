
import cpmpy as cp
import json

# Data (optional)
num_moves = 3  # Number of moves to make all coins face either all heads or all tails
init = [1, 0, 1]  # Initial configuration of the coins, 1 means tails and 0 means heads
# End of data

n_coins = len(init)

# Model definition
model = cp.Model()

# Decision Variables
# steps[t][i] is the state (0=heads, 1=tails) of coin i after t moves
steps = cp.boolvar(shape=(num_moves + 1, n_coins), name="steps")

# Constraints

# Initial configuration
for i in range(n_coins):
    model += (steps[0, i] == init[i])

# Each move flips exactly one coin (Hamming distance between consecutive steps is 1)
for t in range(1, num_moves + 1):
    model += (cp.sum(steps[t, :] != steps[t - 1, :]) == 1)

# Final configuration should be all heads or all tails (all equal)
model += cp.AllEqual(steps[num_moves, :])

# Objective (optional)
# No objective, just find any feasible sequence

# Solve and print
if model.solve():
    # Convert booleans to integers (0/1) for JSON serialization
    steps_val_bool = steps.value().tolist()
    steps_val_int = [[int(b) for b in row] for row in steps_val_bool]
    solution = {'steps': steps_val_int}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
